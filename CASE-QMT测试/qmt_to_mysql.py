# -*- coding: utf-8 -*-
"""
从QMT拉取股票日线数据并写入MySQL

功能：
1. 连接QMT下载日线数据
2. 写入MySQL数据库 trade.trade_stock_daily

运行：python qmt_to_mysql.py
环境：需启动miniQMT客户端
"""
import os
import sys
import time
import pandas as pd
from datetime import datetime
from xtquant import xtdata
import pymysql
from dotenv import dotenv_values


# ============================================================
# 配置
# ============================================================

# 股票列表
STOCK_LIST = [
    {'code': '600096.SH', 'name': '云天化'},
    {'code': '300274.SZ', 'name': '阳光电源'},
    {'code': '601872.SH', 'name': '招商轮船'},
]

# 数据日期范围
DATA_START = '20240101'
DATA_END = ''  # 空表示到最新

# 数据库配置
_env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
_env = dotenv_values(_env_path) if os.path.exists(_env_path) else {}

DB_CONFIG = {
    'host': _env.get('WUCAI_SQL_HOST', '123.56.3.1'),
    'user': _env.get('WUCAI_SQL_USERNAME', 'root'),
    'password': os.environ.get('WUCAI_SQL_PASSWORD', ''),
    'port': int(_env.get('WUCAI_SQL_PORT', '3306')),
    'database': 'trade',
    'charset': 'utf8mb4'
}


def connect_qmt():
    """连接QMT数据服务"""
    print("Connecting to QMT...")
    result = xtdata.connect()
    print(f"[OK] QMT connected: {result}")
    return result


def download_stock_data(stock_code, stock_name):
    """下载单只股票的日线数据"""
    print(f"\nDownloading {stock_name} ({stock_code})...")

    # 下载历史数据到本地缓存
    try:
        xtdata.download_history_data(
            stock_code=stock_code,
            period='1d',
            start_time=DATA_START,
            end_time=DATA_END
        )
        time.sleep(1)
    except Exception as e:
        print(f"  [WARN] Download warning: {e}")

    # 获取市场数据
    res = xtdata.get_market_data(
        stock_list=[stock_code],
        period='1d',
        start_time=DATA_START,
        end_time=DATA_END,
        count=-1,
        dividend_type='front',  # 前复权
        fill_data=True
    )

    if not res or 'close' not in res or stock_code not in res['close'].index:
        print(f"  [FAIL] No data for {stock_code}")
        return None

    # 提取数据
    close_df = res['close']
    open_df = res.get('open')
    high_df = res.get('high')
    low_df = res.get('low')
    volume_df = res.get('volume')
    amount_df = res.get('amount')

    dates = close_df.columns.tolist()

    # 构建DataFrame
    records = []
    for i, date_str in enumerate(dates):
        record = {
            'stock_code': stock_code,
            'trade_date': date_str,
            'close_price': float(close_df.loc[stock_code].values[i]) if pd.notna(close_df.loc[stock_code].values[i]) else None,
        }

        if open_df is not None and stock_code in open_df.index:
            record['open_price'] = float(open_df.loc[stock_code].values[i]) if pd.notna(open_df.loc[stock_code].values[i]) else None
        if high_df is not None and stock_code in high_df.index:
            record['high_price'] = float(high_df.loc[stock_code].values[i]) if pd.notna(high_df.loc[stock_code].values[i]) else None
        if low_df is not None and stock_code in low_df.index:
            record['low_price'] = float(low_df.loc[stock_code].values[i]) if pd.notna(low_df.loc[stock_code].values[i]) else None
        if volume_df is not None and stock_code in volume_df.index:
            record['volume'] = int(volume_df.loc[stock_code].values[i]) if pd.notna(volume_df.loc[stock_code].values[i]) else None
        if amount_df is not None and stock_code in amount_df.index:
            record['amount'] = float(amount_df.loc[stock_code].values[i]) if pd.notna(amount_df.loc[stock_code].values[i]) else None

        # 过滤无效数据
        if record['close_price'] is not None:
            records.append(record)

    print(f"  [OK] Downloaded {len(records)} records")
    return records


def save_to_mysql(records, stock_code, stock_name):
    """保存数据到MySQL"""
    if not records:
        return 0

    print(f"  Saving to MySQL...")

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 使用 INSERT ... ON DUPLICATE KEY UPDATE 实现去重
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

    # 批量插入
    cursor.executemany(sql, records)
    affected = cursor.rowcount
    conn.commit()

    cursor.close()
    conn.close()

    print(f"  [OK] Saved {affected} records to MySQL")
    return affected


def verify_data(stock_code):
    """验证数据库中的数据"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            COUNT(*) as total,
            MIN(trade_date) as first_date,
            MAX(trade_date) as last_date
        FROM trade_stock_daily
        WHERE stock_code = %s
    ''', (stock_code,))

    result = cursor.fetchone()
    cursor.close()
    conn.close()

    return result


def main():
    """主函数"""
    print("=" * 60)
    print("QMT -> MySQL Data Sync")
    print("=" * 60)
    print(f"Date range: {DATA_START} ~ now")
    print(f"Database: {DB_CONFIG['database']}")
    print(f"Table: trade_stock_daily")
    print(f"Stocks: {len(STOCK_LIST)}")
    print()

    # 连接QMT
    connect_qmt()

    # 处理每只股票
    total_records = 0
    for stock in STOCK_LIST:
        print(f"\n{'='*40}")
        print(f"Processing: {stock['name']} ({stock['code']})")
        print(f"{'='*40}")

        # 下载数据
        records = download_stock_data(stock['code'], stock['name'])

        # 保存到MySQL
        if records:
            saved = save_to_mysql(records, stock['code'], stock['name'])
            total_records += saved

            # 验证
            result = verify_data(stock['code'])
            if result:
                print(f"  [Verify] Total: {result[0]}, Range: {result[1]} ~ {result[2]}")

    # 汇总
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Stocks processed: {len(STOCK_LIST)}")
    print(f"Total records saved: {total_records}")

    # 显示数据库统计
    print("\nDatabase Statistics:")
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    for stock in STOCK_LIST:
        cursor.execute('''
            SELECT stock_code, COUNT(*), MIN(trade_date), MAX(trade_date)
            FROM trade_stock_daily
            WHERE stock_code = %s
            GROUP BY stock_code
        ''', (stock['code'],))
        row = cursor.fetchone()
        if row:
            print(f"  {stock['name']:8s} ({row[0]}): {row[1]:4d} records, {row[2]} ~ {row[3]}")

    cursor.close()
    conn.close()

    print("\n[Done] All data synced successfully!")


if __name__ == "__main__":
    main()
