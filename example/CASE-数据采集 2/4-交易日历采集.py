# -*- coding: utf-8 -*-
"""
交易日历采集 - 使用MiniQMT(xtquant)下载交易日历和节假日数据存入MySQL

功能：
  1. 交易日历数据
  2. 节假日数据
  3. 支持回测框架使用

运行：python 4-交易日历采集.py
环境：需安装QMT并配置好xtquant, pip install pymysql python-dotenv
"""
import sys
import os
from datetime import date

from xtquant import xtdata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_config import get_connection, execute_query

if sys.platform == 'win32' and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def ensure_table_exists():
    """确保交易日历表存在"""
    conn = get_connection()
    cursor = conn.cursor()

    # 交易日历表
    create_sql = """
    CREATE TABLE IF NOT EXISTS trade_calendar (
        trade_date DATE NOT NULL COMMENT '交易日期',
        is_trading TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否交易日 1=是 0=否',
        market VARCHAR(20) NOT NULL DEFAULT 'A股' COMMENT '市场',
        PRIMARY KEY (trade_date, market)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='交易日历'
    """
    cursor.execute(create_sql)
    conn.commit()
    cursor.close()
    conn.close()


def download_trading_calendar():
    """下载并保存交易日历 - 基于已有日线数据生成"""
    print("=" * 60)
    print("交易日历采集 (基于已有日线数据生成)")
    print("=" * 60)

    # 从已有日线数据提取交易日
    print("\n从 trade_stock_daily 表提取交易日...")
    rows = execute_query("""
        SELECT DISTINCT trade_date as trade_date
        FROM trade_stock_daily
        ORDER BY trade_date
    """)

    if not rows:
        print("  错误: trade_stock_daily 表无数据，请先运行日线数据采集")
        return

    trading_dates = [r['trade_date'] for r in rows]
    print(f"  找到 {len(trading_dates)} 个交易日")

    # 生成日期范围(包含非交易日)
    min_date = min(trading_dates)
    max_date = max(trading_dates)
    print(f"  日期范围: {min_date} ~ {max_date}")

    # 写入数据库
    ensure_table_exists()
    conn = get_connection()
    cursor = conn.cursor()

    # 清空旧数据
    cursor.execute("DELETE FROM trade_calendar")
    conn.commit()

    insert_sql = """
        INSERT INTO trade_calendar (trade_date, is_trading, market)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE is_trading=VALUES(is_trading)
    """

    # 写入交易日数据
    rows_written = 0
    for dt in trading_dates:
        cursor.execute(insert_sql, (dt, 1, 'A股'))
        rows_written += 1

    conn.commit()

    # 填充非交易日(周末等)
    from datetime import date, timedelta
    current = min_date
    all_dates = set()
    while current <= max_date:
        all_dates.add(current)
        current += timedelta(days=1)

    non_trading = all_dates - set(trading_dates)
    for dt in non_trading:
        cursor.execute(insert_sql, (dt, 0, 'A股'))
        rows_written += 1

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n写入 {rows_written} 条记录 (交易日: {len(trading_dates)}, 非交易日: {len(non_trading)})")

    # 打印概况
    _print_summary()


def _print_summary():
    summary = execute_query("""
        SELECT
            COUNT(*) as total_cnt,
            SUM(CASE WHEN is_trading = 1 THEN 1 ELSE 0 END) as trading_cnt,
            MIN(trade_date) as min_date, MAX(trade_date) as max_date
        FROM trade_calendar
    """)
    if summary:
        row = summary[0]
        print(f"\n数据库 trade_calendar 概况:")
        print(f"  总记录: {row['total_cnt']} 天")
        print(f"  交易日: {row['trading_cnt']} 天")
        print(f"  日期范围: {row['min_date']} ~ {row['max_date']}")
    print("=" * 60)


if __name__ == "__main__":
    download_trading_calendar()
