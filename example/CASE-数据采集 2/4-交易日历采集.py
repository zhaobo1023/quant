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
    """下载并保存交易日历"""
    print("=" * 60)
    print("交易日历采集 (MiniQMT -> MySQL)")
    print("=" * 60)

    print("\n连接QMT数据服务...")
    xtdata.connect()
    print("  连接成功")

    # 下载节假日数据
    print("\n下载节假日数据...")
    xtdata.download_holiday_data()

    # 获取交易日历
    print("获取交易日历...")
    trading_dates = xtdata.get_trading_calendar('SH')  # 上交所
    trading_dates_sz = xtdata.get_trading_calendar('SZ')  # 深交所

    # 获取节假日
    print("获取节假日...")
    holidays = xtdata.get_holidays()

    print(f"  上交所交易日: {len(trading_dates)} 天")
    print(f"  深交所交易日: {len(trading_dates_sz)} 天")
    print(f"  节假日: {len(holidays)} 天")

    # 写入数据库
    ensure_table_exists()
    conn = get_connection()
    cursor = conn.cursor()

    # 清空旧数据
    cursor.execute("DELETE FROM trade_calendar")
    conn.commit()

    # 写入交易日数据
    insert_sql = """
        INSERT INTO trade_calendar (trade_date, is_trading, market)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE is_trading=VALUES(is_trading)
    """

    rows = 0
    for dt in trading_dates:
        dt_str = str(dt)
        if len(dt_str) == 8:
            trade_date = f"{dt_str[:4]}-{dt_str[4:6]}-{dt_str[6:8]}"
            cursor.execute(insert_sql, (trade_date, 1, 'SH'))
            rows += 1

    for dt in trading_dates_sz:
        dt_str = str(dt)
        if len(dt_str) == 8:
            trade_date = f"{dt_str[:4]}-{dt_str[4:6]}-{dt_str[6:8]}"
            cursor.execute(insert_sql, (trade_date, 1, 'SZ'))
            rows += 1

    # 写入节假日数据
    for dt in holidays:
        dt_str = str(dt)
        if len(dt_str) == 8:
            holiday_date = f"{dt_str[:4]}-{dt_str[4:6]}-{dt_str[6:8]}"
            cursor.execute(insert_sql, (holiday_date, 0, 'ALL'))
            rows += 1

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n写入 {rows} 条记录")

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
