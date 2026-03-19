# -*- coding: utf-8 -*-
"""
基金ETF数据采集 - 使用MiniQMT(xtquant)下载ETF/LOF基金行情数据存入MySQL

功能：
  1. 沪深两市ETF基金列表
  2. 日K线数据
  3. 基金基本信息

模式：
  - TEST_MODE = True  -> 只采集沪深300ETF，用于验证流程
  - TEST_MODE = False -> 采集全量ETF基金

运行：python 6-基金ETF数据采集.py
环境：需安装QMT并配置好xtquant, pip install pymysql python-dotenv
"""
import sys
import os
import time
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
TEST_MODE = False
TEST_STOCK = '510300.SH'  # 沪深300ETF

SECTORS = ['沪市ETF', '深市ETF']  # 同时采集沪深两市ETF
NUM_WORKERS = 8
DATA_START = '20150101'
TABLE_DAILY = 'trade_etf_daily'
TABLE_INFO = 'trade_etf_info'


# ============================================================
# 数据库辅助
# ============================================================

def ensure_tables_exist():
    """确保ETF相关表存在"""
    conn = get_connection()
    cursor = conn.cursor()

    # ETF日线数据表
    create_daily_sql = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_DAILY} (
        fund_code VARCHAR(20) NOT NULL COMMENT '基金代码',
        trade_date DATE NOT NULL COMMENT '交易日期',
        open_price DECIMAL(10,4) COMMENT '开盘价',
        high_price DECIMAL(10,4) COMMENT '最高价',
        low_price DECIMAL(10,4) COMMENT '最低价',
        close_price DECIMAL(10,4) COMMENT '收盘价',
        volume BIGINT COMMENT '成交量(手)',
        amount DECIMAL(18,4) COMMENT '成交额',
        PRIMARY KEY (fund_code, trade_date),
        INDEX idx_trade_date (trade_date),
        INDEX idx_fund_code (fund_code)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='ETF基金日线数据'
    """
    cursor.execute(create_daily_sql)

    # ETF基本信息表
    create_info_sql = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_INFO} (
        fund_code VARCHAR(20) NOT NULL COMMENT '基金代码',
        fund_name VARCHAR(100) COMMENT '基金名称',
        fund_type VARCHAR(50) COMMENT '基金类型',
        underlying_index VARCHAR(50) COMMENT '跟踪指数',
        list_date DATE COMMENT '上市日期',
        total_shares DECIMAL(20,2) COMMENT '总份额(万份)',
        update_time DATETIME COMMENT '更新时间',
        PRIMARY KEY (fund_code)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='ETF基金基本信息'
    """
    cursor.execute(create_info_sql)

    conn.commit()
    cursor.close()
    conn.close()


def get_existing_latest_dates():
    """查询所有ETF在DB中的最新交易日"""
    rows = execute_query(
        f"SELECT fund_code, MAX(trade_date) AS max_date FROM {TABLE_DAILY} GROUP BY fund_code"
    )
    result = {}
    for r in rows:
        if r['max_date']:
            result[r['fund_code']] = r['max_date'].strftime('%Y%m%d')
    return result


# ============================================================
# 核心逻辑
# ============================================================

INSERT_DAILY_SQL = f"""
    INSERT INTO {TABLE_DAILY}
    (fund_code, trade_date, open_price, high_price, low_price, close_price, volume, amount)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    open_price=VALUES(open_price), high_price=VALUES(high_price),
    low_price=VALUES(low_price), close_price=VALUES(close_price),
    volume=VALUES(volume), amount=VALUES(amount)
"""

INSERT_INFO_SQL = f"""
    INSERT INTO {TABLE_INFO}
    (fund_code, fund_name, fund_type, underlying_index, list_date, total_shares, update_time)
    VALUES (%s, %s, %s, %s, %s, %s, NOW())
    ON DUPLICATE KEY UPDATE
    fund_name=VALUES(fund_name), fund_type=VALUES(fund_type),
    underlying_index=VALUES(underlying_index), list_date=VALUES(list_date),
    total_shares=VALUES(total_shares), update_time=NOW()
"""


def download_etf_info(fund_code):
    """下载并保存ETF基本信息"""
    try:
        xtdata.download_etf_info()
        info = xtdata.get_etf_info(fund_code)
        if info:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(INSERT_INFO_SQL, (
                fund_code,
                info.get('fund_name', ''),
                info.get('fund_type', 'ETF'),
                info.get('underlying_index', ''),
                info.get('list_date', None),
                info.get('total_shares', 0),
            ))
            conn.commit()
            cursor.close()
            conn.close()
    except Exception:
        pass


def download_and_save(fund_code, start_date):
    """增量下载单只ETF的日线数据并写入MySQL"""
    xtdata.download_history_data(fund_code, '1d', start_time=start_date)

    data = xtdata.get_market_data_ex(
        field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[fund_code],
        period='1d',
        start_time=start_date,
        dividend_type='front',
    )

    if not data or fund_code not in data:
        return fund_code, 0

    df = data[fund_code]
    if df is None or len(df) == 0:
        return fund_code, 0

    rows = []
    for idx, row in df.iterrows():
        idx_str = str(idx)
        if len(idx_str) >= 8:
            trade_date = f"{idx_str[:4]}-{idx_str[4:6]}-{idx_str[6:8]}"
            rows.append((
                fund_code, trade_date,
                float(row['open']), float(row['high']),
                float(row['low']), float(row['close']),
                int(row['volume']), float(row['amount']),
            ))

    if rows:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.executemany(INSERT_DAILY_SQL, rows)
        conn.commit()
        cursor.close()
        conn.close()

    return fund_code, len(rows)


# ============================================================
# 主流程
# ============================================================

def main():
    print("=" * 60)
    print("基金ETF数据采集 (MiniQMT -> MySQL)")
    if TEST_MODE:
        print("[测试模式] 只采集沪深300ETF")
    else:
        print(f"[全量模式] 采集沪深两市ETF, {NUM_WORKERS}线程并行")
    print(f"目标表: {TABLE_DAILY}, {TABLE_INFO}")
    print("=" * 60)

    print("\n确保数据库表存在...")
    ensure_tables_exist()
    print("  表已就绪")

    print("\n连接QMT数据服务...")
    xtdata.connect()
    print("  连接成功")

    # 获取ETF列表
    if TEST_MODE:
        all_codes = [TEST_STOCK]
        print(f"\n[测试模式] 只采集 {TEST_STOCK}")
    else:
        print(f"\n获取ETF基金列表...")
        all_codes = []
        for sector in SECTORS:
            codes = xtdata.get_stock_list_in_sector(sector)
            codes = [c for c in codes if '.' in str(c)]
            all_codes.extend(codes)
            print(f"  {sector}: {len(codes)} 只")
        all_codes = list(set(all_codes))  # 去重
        print(f"  共 {len(all_codes)} 只ETF")

    # 批量查询DB中已有的最新日期
    print("查询数据库已有数据...")
    existing = get_existing_latest_dates()
    recent_cutoff = date.today().strftime('%Y%m%d')

    tasks = []
    skip_count = 0
    for code in all_codes:
        latest = existing.get(code)
        if latest and latest >= recent_cutoff:
            skip_count += 1
            continue
        start = latest if latest else DATA_START
        tasks.append((code, start))

    print(f"  需更新: {len(tasks)} 只, 跳过(今日已有数据): {skip_count} 只")

    if not tasks:
        print("\n全部已是最新，无需更新")
        _print_summary()
        return

    # 下载ETF基本信息
    print("\n下载ETF基本信息...")
    try:
        xtdata.download_etf_info()
    except Exception as e:
        print(f"  下载ETF信息失败: {e}")

    total = len(tasks)
    total_rows = 0
    success_count = 0
    fail_list = []
    start_time = time.time()

    print(f"\n并行下载（{NUM_WORKERS} 线程）...")

    def _worker(args):
        code, start = args
        try:
            download_etf_info(code)
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
    print(f"  成功: {success_count}/{total} 只ETF")
    print(f"  总写入: {total_rows:,} 条记录")

    if fail_list:
        print(f"  失败 {len(fail_list)} 只: {fail_list[:20]}{'...' if len(fail_list) > 20 else ''}")

    _print_summary()


def _print_summary():
    summary = execute_query(f"""
        SELECT COUNT(DISTINCT fund_code) as fund_cnt,
               COUNT(*) as row_cnt,
               MIN(trade_date) as min_date, MAX(trade_date) as max_date
        FROM {TABLE_DAILY}
    """)
    if summary:
        row = summary[0]
        print(f"\n数据库 {TABLE_DAILY} 概况:")
        print(f"  {row['fund_cnt']} 只ETF, {row['row_cnt']:,} 条记录")
        print(f"  日期范围: {row['min_date']} ~ {row['max_date']}")

    info_cnt = execute_query(f"SELECT COUNT(*) as cnt FROM {TABLE_INFO}")
    if info_cnt:
        print(f"  ETF基本信息: {info_cnt[0]['cnt']} 条")

    print("=" * 60)


if __name__ == "__main__":
    main()
