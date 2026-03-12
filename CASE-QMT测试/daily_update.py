# -*- coding: utf-8 -*-
"""
A股日线数据每日增量更新脚本

功能：
1. 从QMT拉取最新一天的日线数据
2. 增量写入MySQL数据库

定时任务：每天晚上7点执行
"""
import os
import sys
import time
import logging
from datetime import datetime, timedelta
from xtquant import xtdata
import pymysql

# ============================================================
# 配置
# ============================================================

DB_CONFIG = {
    'host': '123.56.3.1',
    'user': 'root',
    'password': os.environ.get('WUCAI_SQL_PASSWORD', 'Hao1023@zb'),
    'port': 3306,
    'database': 'trade',
    'charset': 'utf8mb4'
}

BATCH_SIZE = 200  # 每批处理股票数

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'daily_update.log'), encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def get_trade_date():
    """获取今天的日期（格式：YYYYMMDD）"""
    return datetime.now().strftime('%Y%m%d')


def get_yesterday():
    """获取昨天的日期"""
    return (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')


def connect_qmt():
    """连接QMT"""
    logger.info("Connecting to QMT...")
    result = xtdata.connect()
    logger.info(f"QMT connected: {result}")
    return result


def get_stock_list():
    """获取A股股票列表"""
    stock_list = xtdata.get_stock_list_in_sector('沪深A股')
    valid_stocks = [s for s in stock_list if s.endswith('.SH') or s.endswith('.SZ')]
    logger.info(f"Total stocks: {len(valid_stocks)}")
    return valid_stocks


def download_and_save_data(stock_list, start_date):
    """下载并保存数据"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    total_records = 0
    failed_count = 0

    for i in range(0, len(stock_list), BATCH_SIZE):
        batch = stock_list[i:i+BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(stock_list) + BATCH_SIZE - 1) // BATCH_SIZE

        logger.info(f"Processing batch {batch_num}/{total_batches}...")

        # 批量下载
        for stock_code in batch:
            try:
                xtdata.download_history_data(
                    stock_code=stock_code,
                    period='1d',
                    start_time=start_date,
                    end_time=''
                )
            except:
                pass

        time.sleep(1)

        # 获取并保存数据
        for stock_code in batch:
            try:
                import pandas as pd

                res = xtdata.get_market_data(
                    stock_list=[stock_code],
                    period='1d',
                    start_time=start_date,
                    end_time='',
                    count=-1,
                    dividend_type='front',
                    fill_data=True
                )

                if not res or 'close' not in res or stock_code not in res['close'].index:
                    continue

                close_df = res['close']
                open_df = res.get('open')
                high_df = res.get('high')
                low_df = res.get('low')
                volume_df = res.get('volume')
                amount_df = res.get('amount')

                dates = close_df.columns.tolist()
                records = []

                for j, date_str in enumerate(dates):
                    record = {
                        'stock_code': stock_code,
                        'trade_date': date_str,
                        'close_price': None,
                        'open_price': None,
                        'high_price': None,
                        'low_price': None,
                        'volume': None,
                        'amount': None,
                    }

                    try:
                        val = close_df.loc[stock_code].values[j]
                        if pd.notna(val):
                            record['close_price'] = float(val)
                    except:
                        pass

                    try:
                        if open_df is not None and stock_code in open_df.index:
                            val = open_df.loc[stock_code].values[j]
                            if pd.notna(val):
                                record['open_price'] = float(val)
                    except:
                        pass

                    try:
                        if high_df is not None and stock_code in high_df.index:
                            val = high_df.loc[stock_code].values[j]
                            if pd.notna(val):
                                record['high_price'] = float(val)
                    except:
                        pass

                    try:
                        if low_df is not None and stock_code in low_df.index:
                            val = low_df.loc[stock_code].values[j]
                            if pd.notna(val):
                                record['low_price'] = float(val)
                    except:
                        pass

                    try:
                        if volume_df is not None and stock_code in volume_df.index:
                            val = volume_df.loc[stock_code].values[j]
                            if pd.notna(val):
                                record['volume'] = int(val)
                    except:
                        pass

                    try:
                        if amount_df is not None and stock_code in amount_df.index:
                            val = amount_df.loc[stock_code].values[j]
                            if pd.notna(val):
                                record['amount'] = float(val)
                    except:
                        pass

                    if record['close_price'] is not None:
                        records.append(record)

                if records:
                    sql = '''
                    INSERT INTO trade_stock_daily
                        (stock_code, trade_date, open_price, high_price, low_price, close_price, volume, amount)
                    VALUES
                        (%(stock_code)s, %(trade_date)s, %(open_price)s, %(high_price)s, %(low_price)s, %(close_price)s, %(volume)s, %(amount)s)
                    ON DUPLICATE KEY UPDATE
                        open_price = VALUES(open_price),
                        high_price = VALUES(high_price),
                        low_price = VALUES(low_price),
                        close_price = VALUES(close_price),
                        volume = VALUES(volume),
                        amount = VALUES(amount)
                    '''
                    cursor.executemany(sql, records)
                    total_records += len(records)

            except Exception as e:
                failed_count += 1

        conn.commit()

    cursor.close()
    conn.close()

    return total_records, failed_count


def verify_data():
    """验证数据"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM trade_stock_daily')
    total = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(DISTINCT stock_code) FROM trade_stock_daily')
    stocks = cursor.fetchone()[0]

    cursor.execute('SELECT MAX(trade_date) FROM trade_stock_daily')
    last_date = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return total, stocks, last_date


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("Daily Update Started")
    logger.info("=" * 60)

    start_time = datetime.now()

    # 获取日期
    today = get_trade_date()
    yesterday = get_yesterday()

    # 使用昨天作为起始日期（增量更新最近2天的数据，确保不遗漏）
    start_date = yesterday
    logger.info(f"Start date: {start_date}")

    # 连接QMT
    connect_qmt()

    # 获取股票列表
    stock_list = get_stock_list()

    # 下载并保存数据
    total_records, failed_count = download_and_save_data(stock_list, start_date)

    # 验证
    total, stocks, last_date = verify_data()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    logger.info("=" * 60)
    logger.info("Summary")
    logger.info("=" * 60)
    logger.info(f"Duration: {duration:.1f} seconds")
    logger.info(f"Records updated: {total_records}")
    logger.info(f"Failed stocks: {failed_count}")
    logger.info(f"Database total: {stocks} stocks, {total} records")
    logger.info(f"Last trade date: {last_date}")
    logger.info("[Done]")


if __name__ == "__main__":
    main()
