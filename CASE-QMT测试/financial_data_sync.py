# -*- coding: utf-8 -*-
"""
A股财务数据全量同步脚本

功能：
1. 从QMT拉取全部A股财务数据
2. 写入MySQL数据库 trade.trade_stock_financial

运行：python financial_data_sync.py
"""
import os
import time
import logging
from datetime import datetime
from xtquant import xtdata
import pymysql
import pandas as pd

# ============================================================
# 配置
# ============================================================

DB_CONFIG = {
    'host': '123.56.3.1',
    'user': 'root',
    'password': 'Hao1023@zb',
    'port': 3306,
    'database': 'trade',
    'charset': 'utf8mb4',
    'connect_timeout': 30,
    'read_timeout': 60,
    'write_timeout': 60
}

DATA_START = '20150101'
COMMIT_INTERVAL = 100  # 每100只股票提交一次

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'financial_sync.log'), encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)


def parse_timetag(timetag):
    """解析时间戳"""
    if timetag is None or pd.isna(timetag):
        return None
    try:
        if isinstance(timetag, str):
            if len(timetag) == 8:
                return timetag
            return timetag[:8]
        ts = int(timetag)
        if ts > 1000000000000:
            ts = ts // 1000
        return datetime.fromtimestamp(ts).strftime('%Y%m%d')
    except:
        return None


def safe_float(value):
    """安全转换为float"""
    if value is None or pd.isna(value):
        return None
    try:
        return float(value)
    except:
        return None


def main():
    logger.info("=" * 60)
    logger.info("Financial Data Sync - Full Load")
    logger.info("=" * 60)

    start_time = datetime.now()

    # 连接QMT
    logger.info("Connecting to QMT...")
    xtdata.connect()
    logger.info("QMT connected")

    # 获取股票列表
    logger.info("Getting stock list...")
    stock_list = xtdata.get_stock_list_in_sector('沪深A股')
    valid_stocks = [s for s in stock_list if s.endswith('.SH') or s.endswith('.SZ')]
    logger.info(f"Total stocks: {len(valid_stocks)}")

    # 下载财务数据
    logger.info("Downloading financial data...")
    completed = [0]

    def on_progress(data):
        completed[0] += 1

    xtdata.download_financial_data2(
        stock_list=valid_stocks,
        table_list=['PershareIndex'],
        start_time=DATA_START,
        end_time='',
        callback=on_progress
    )
    logger.info(f"Download completed: {completed[0]}")
    time.sleep(3)

    # 处理数据
    logger.info("Processing stocks...")
    conn = get_db_connection()
    cursor = conn.cursor()

    total_records = 0
    failed = 0
    processed = 0

    for i, stock_code in enumerate(valid_stocks):
        try:
            # 获取财务数据
            data = xtdata.get_financial_data(
                stock_list=[stock_code],
                table_list=['PershareIndex'],
                start_time=DATA_START,
                end_time='',
                report_type='report_time'
            )

            if not data or stock_code not in data:
                continue

            pi = data[stock_code].get('PershareIndex')
            if pi is None or len(pi) == 0:
                continue

            records = []
            for _, row in pi.iterrows():
                report_date = parse_timetag(row.get('m_timetag'))
                if not report_date:
                    continue

                records.append({
                    'stock_code': stock_code,
                    'report_date': report_date,
                    'eps': safe_float(row.get('s_fa_eps_basic')),
                    'bps': safe_float(row.get('s_fa_bps')),
                    'roe': safe_float(row.get('du_return_on_equity')),
                    'gross_margin': safe_float(row.get('sales_gross_profit')),
                    'ocfps': safe_float(row.get('s_fa_ocfps')),
                })

            if records:
                sql = '''
                INSERT INTO trade_stock_financial
                    (stock_code, report_date, eps, roe, gross_margin, data_source)
                VALUES
                    (%(stock_code)s, %(report_date)s, %(eps)s, %(roe)s, %(gross_margin)s, 'qmt')
                ON DUPLICATE KEY UPDATE
                    eps = VALUES(eps),
                    roe = VALUES(roe),
                    gross_margin = VALUES(gross_margin)
                '''
                cursor.executemany(sql, records)
                total_records += len(records)

            processed += 1

            # 定期提交
            if processed % COMMIT_INTERVAL == 0:
                conn.commit()
                logger.info(f"  Progress: {processed}/{len(valid_stocks)}, records: {total_records}")

        except Exception as e:
            failed += 1
            # 重连
            try:
                cursor.close()
                conn.close()
            except:
                pass
            conn = get_db_connection()
            cursor = conn.cursor()

    # 最终提交
    conn.commit()
    cursor.close()
    conn.close()

    # 验证
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*), COUNT(DISTINCT stock_code) FROM trade_stock_financial')
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    logger.info("=" * 60)
    logger.info("Summary")
    logger.info("=" * 60)
    logger.info(f"Duration: {duration:.1f} seconds")
    logger.info(f"Processed: {processed} stocks")
    logger.info(f"Total records: {total_records}")
    logger.info(f"Database: {result[1]} stocks, {result[0]} records")
    logger.info(f"Failed: {failed}")
    logger.info("[Done]")


if __name__ == "__main__":
    main()
