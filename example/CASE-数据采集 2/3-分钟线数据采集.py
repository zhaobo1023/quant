# -*- coding: utf-8 -*-
"""
分钟线数据采集 - 使用MiniQMT(xtquant)下载A股分钟K线数据存入MySQL

功能：
  1. 支持1分钟/5分钟/15分钟/30分钟/60分钟K线
  2. 增量下载，跳过已有数据
  3. 多线程并行写入MySQL

模式：
  - TEST_MODE = True  -> 只采集1只股票(贵州茅台)，用于验证流程
  - TEST_MODE = False -> 采集沪深A股全量股票

运行：
  python 3-分钟线数据采集.py          # 默认1分钟
  python 3-分钟线数据采集.py --period 5m  # 5分钟

环境：需安装QMT并配置好xtquant, pip install pymysql python-dotenv
"""
import sys
import os
import time
import argparse
from datetime import date, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from xtquant import xtdata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_config import get_connection, execute_query

if sys.platform == 'win32' and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ============================================================
# 配置
# ============================================================
parser = argparse.ArgumentParser(description='分钟线数据采集')
parser.add_argument('--period', type=str, default='1m',
                    choices=['1m', '5m', '15m', '30m', '60m'],
                    help='K线周期: 1m/5m/15m/30m/60m')
parser.add_argument('--test', action='store_true', help='测试模式，只采集贵州茅台')
args = parser.parse_args()

TEST_MODE = args.test
TEST_STOCK = '600519.SH'
PERIOD = args.period
SECTOR = '沪深A股'
NUM_WORKERS = 8
DATA_START = '20240101'  # 分钟线数据量大，只保留近期数据

# 表名映射
TABLE_MAP = {
    '1m': 'trade_stock_min1',
    '5m': 'trade_stock_min5',
    '15m': 'trade_stock_min15',
    '30m': 'trade_stock_min30',
    '60m': 'trade_stock_min60',
}
TABLE_NAME = TABLE_MAP[PERIOD]


# ============================================================
# 数据库辅助
# ============================================================

def ensure_table_exists():
    """确保分钟线表存在"""
    conn = get_connection()
    cursor = conn.cursor()

    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',
        trade_time DATETIME NOT NULL COMMENT '交易时间',
        open_price DECIMAL(10,3) COMMENT '开盘价',
        high_price DECIMAL(10,3) COMMENT '最高价',
        low_price DECIMAL(10,3) COMMENT '最低价',
        close_price DECIMAL(10,3) COMMENT '收盘价',
        volume BIGINT COMMENT '成交量(手)',
        amount DECIMAL(18,3) COMMENT '成交额',
        PRIMARY KEY (stock_code, trade_time),
        INDEX idx_trade_time (trade_time),
        INDEX idx_stock_code (stock_code)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票{PERIOD}K线数据'
    """
    cursor.execute(create_sql)
    conn.commit()
    cursor.close()
    conn.close()


def get_existing_latest_times():
    """查询所有股票在DB中的最新时间，返回 {stock_code: 'YYYYMMDDHHMM'}"""
    rows = execute_query(
        f"SELECT stock_code, MAX(trade_time) AS max_time FROM {TABLE_NAME} GROUP BY stock_code"
    )
    result = {}
    for r in rows:
        if r['max_time']:
            result[r['stock_code']] = r['max_time'].strftime('%Y%m%d%H%M')
    return result


# ============================================================
# 核心逻辑
# ============================================================

INSERT_SQL = f"""
    INSERT INTO {TABLE_NAME}
    (stock_code, trade_time, open_price, high_price, low_price, close_price, volume, amount)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    open_price=VALUES(open_price), high_price=VALUES(high_price),
    low_price=VALUES(low_price), close_price=VALUES(close_price),
    volume=VALUES(volume), amount=VALUES(amount)
"""


def download_and_save(stock_code, start_date):
    """增量下载单只股票的分钟线数据并写入MySQL"""
    xtdata.download_history_data(stock_code, PERIOD, start_time=start_date)

    data = xtdata.get_market_data_ex(
        field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[stock_code],
        period=PERIOD,
        start_time=start_date,
        dividend_type='front',
    )

    if not data or stock_code not in data:
        return stock_code, 0

    df = data[stock_code]
    if df is None or len(df) == 0:
        return stock_code, 0

    rows = []
    for idx, row in df.iterrows():
        idx_str = str(idx)
        if len(idx_str) >= 12:
            # 分钟线时间格式: YYYYMMDDHHMM 或 YYYYMMDDHHMMSS
            trade_time = f"{idx_str[:4]}-{idx_str[4:6]}-{idx_str[6:8]} {idx_str[8:10]}:{idx_str[10:12]}:00"
            rows.append((
                stock_code, trade_time,
                float(row['open']), float(row['high']),
                float(row['low']), float(row['close']),
                int(row['volume']), float(row['amount']),
            ))

    if rows:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.executemany(INSERT_SQL, rows)
        conn.commit()
        cursor.close()
        conn.close()

    return stock_code, len(rows)


# ============================================================
# 主流程
# ============================================================

def main():
    print("=" * 60)
    print(f"分钟线数据采集 ({PERIOD}) (MiniQMT -> MySQL)")
    if TEST_MODE:
        print("[测试模式] 只采集贵州茅台")
    else:
        print(f"[全量模式] 采集{SECTOR}, {NUM_WORKERS}线程并行")
    print(f"目标表: {TABLE_NAME}")
    print("=" * 60)

    print("\n确保数据库表存在...")
    ensure_table_exists()
    print("  表已就绪")

    print("\n连接QMT数据服务...")
    xtdata.connect()
    print("  连接成功")

    # 获取股票列表
    if TEST_MODE:
        all_codes = [TEST_STOCK]
        print(f"\n[测试模式] 只采集 {TEST_STOCK}")
    else:
        print(f"\n获取 {SECTOR} 股票列表...")
        all_codes = xtdata.get_stock_list_in_sector(SECTOR)
        all_codes = [c for c in all_codes if '.' in str(c)]
        print(f"  共 {len(all_codes)} 只股票")

    # 批量查询DB中已有的最新时间
    print("查询数据库已有数据...")
    existing = get_existing_latest_times()

    # 获取最近交易日作为截止
    recent_cutoff = (date.today() - timedelta(days=1)).strftime('%Y%m%d') + '0930'

    tasks = []
    skip_count = 0
    for code in all_codes:
        latest = existing.get(code)
        if latest and latest >= recent_cutoff:
            skip_count += 1
            continue
        start = latest[:8] if latest else DATA_START
        tasks.append((code, start))

    print(f"  需更新: {len(tasks)} 只, 跳过(已是最新): {skip_count} 只")

    if not tasks:
        print("\n全部已是最新，无需更新")
        _print_summary()
        return

    total = len(tasks)
    total_rows = 0
    success_count = 0
    fail_list = []
    start_time = time.time()

    print(f"\n并行下载（{NUM_WORKERS} 线程）...")

    def _worker(args):
        code, start = args
        try:
            return download_and_save(code, start)
        except Exception:
            return code, -1

    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = {executor.submit(_worker, t): t[0] for t in tasks}
        done = 0
        for future in as_completed(futures):
            code, count = future.result()
            done += 1

            if count >= 0:
                success_count += 1
                total_rows += max(count, 0)
            else:
                fail_list.append(code)

            elapsed = time.time() - start_time
            speed = done / elapsed if elapsed > 0 else 0
            eta = (total - done) / speed if speed > 0 else 0
            sys.stdout.write(
                f"\r  进度 {done}/{total} ({done*100/total:.1f}%) | "
                f"{speed:.1f} 只/秒 | 剩余约 {eta:.0f}秒 | "
                f"写入 {total_rows:,} 条    "
            )
            sys.stdout.flush()

    print()

    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"采集完成! 耗时 {elapsed:.1f} 秒")
    print(f"  成功: {success_count}/{total} 只股票")
    print(f"  总写入: {total_rows:,} 条记录")

    if fail_list:
        print(f"  失败 {len(fail_list)} 只: {fail_list[:20]}{'...' if len(fail_list) > 20 else ''}")

    _print_summary()


def _print_summary():
    summary = execute_query(f"""
        SELECT COUNT(DISTINCT stock_code) as stock_cnt,
               COUNT(*) as row_cnt,
               MIN(trade_time) as min_time, MAX(trade_time) as max_time
        FROM {TABLE_NAME}
    """)
    if summary:
        row = summary[0]
        print(f"\n数据库 {TABLE_NAME} 概况:")
        print(f"  {row['stock_cnt']} 只股票, {row['row_cnt']:,} 条记录")
        print(f"  时间范围: {row['min_time']} ~ {row['max_time']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
