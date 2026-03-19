# -*- coding: utf-8 -*-
"""
创建补充数据表

运行此脚本创建多因子选股所需的补充数据表：
- trade_stock_industry      行业分类
- trade_stock_daily_basic   每日指标(市值/PE/PB)
- trade_stock_moneyflow     资金流向
- trade_north_holding       北向持股
- trade_margin_trade        融资融券

使用方法:
    python my/create_supplement_tables.py
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from db_config import get_connection


# 新增表结构定义
SUPPLEMENT_TABLES = [
    # 1. 行业分类表
    ("""
    CREATE TABLE IF NOT EXISTS trade_stock_industry (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',
        stock_name VARCHAR(50) COMMENT '股票名称',
        industry_code VARCHAR(20) COMMENT '行业代码',
        industry_name VARCHAR(50) COMMENT '行业名称',
        industry_level VARCHAR(10) DEFAULT 'L1' COMMENT '行业级别 L1/L2/L3',
        classify_type VARCHAR(20) DEFAULT 'sw' COMMENT '分类标准 sw(申万)/zx(中信)',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY uk_code_type_level (stock_code, classify_type, industry_level),
        INDEX idx_industry_code (industry_code)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票行业分类';
    """, "trade_stock_industry"),

    # 2. 每日指标表(市值/估值)
    ("""
    CREATE TABLE IF NOT EXISTS trade_stock_daily_basic (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',
        trade_date DATE NOT NULL COMMENT '交易日期',
        total_mv DECIMAL(18,4) COMMENT '总市值(万元)',
        circ_mv DECIMAL(18,4) COMMENT '流通市值(万元)',
        pe_ttm DECIMAL(10,4) COMMENT '市盈率TTM',
        pb DECIMAL(10,4) COMMENT '市净率',
        ps_ttm DECIMAL(10,4) COMMENT '市销率TTM',
        total_share DECIMAL(18,4) COMMENT '总股本(万股)',
        circ_share DECIMAL(18,4) COMMENT '流通股本(万股)',
        turnover_rate DECIMAL(8,4) COMMENT '换手率(%)',
        free_share DECIMAL(18,4) COMMENT '自由流通股本(万股)',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY uk_code_date (stock_code, trade_date),
        INDEX idx_trade_date (trade_date),
        INDEX idx_total_mv (total_mv)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='每日指标-市值估值';
    """, "trade_stock_daily_basic"),

    # 3. 资金流向表
    ("""
    CREATE TABLE IF NOT EXISTS trade_stock_moneyflow (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',
        trade_date DATE NOT NULL COMMENT '交易日期',
        buy_sm_vol DECIMAL(18,2) COMMENT '小单买入量(手)',
        buy_md_vol DECIMAL(18,2) COMMENT '中单买入量(手)',
        buy_lg_vol DECIMAL(18,2) COMMENT '大单买入量(手)',
        buy_elg_vol DECIMAL(18,2) COMMENT '特大单买入量(手)',
        sell_sm_vol DECIMAL(18,2) COMMENT '小单卖出量(手)',
        sell_md_vol DECIMAL(18,2) COMMENT '中单卖出量(手)',
        sell_lg_vol DECIMAL(18,2) COMMENT '大单卖出量(手)',
        sell_elg_vol DECIMAL(18,2) COMMENT '特大单卖出量(手)',
        net_mf_vol DECIMAL(18,2) COMMENT '净流入量(手)',
        net_mf_amount DECIMAL(18,2) COMMENT '净流入额(万元)',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY uk_code_date (stock_code, trade_date),
        INDEX idx_trade_date (trade_date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='个股资金流向';
    """, "trade_stock_moneyflow"),

    # 4. 北向持股表
    ("""
    CREATE TABLE IF NOT EXISTS trade_north_holding (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',
        hold_date DATE NOT NULL COMMENT '持股日期',
        hold_amount DECIMAL(18,4) COMMENT '持股数量(万股)',
        hold_ratio DECIMAL(10,4) COMMENT '持股占比(%)',
        hold_change DECIMAL(18,4) COMMENT '持股变化(万股)',
        hold_value DECIMAL(18,2) COMMENT '持股市值(万元)',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY uk_code_date (stock_code, hold_date),
        INDEX idx_hold_date (hold_date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='北向资金持股';
    """, "trade_north_holding"),

    # 5. 融资融券表
    ("""
    CREATE TABLE IF NOT EXISTS trade_margin_trade (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',
        trade_date DATE NOT NULL COMMENT '交易日期',
        rzye DECIMAL(18,2) COMMENT '融资余额(万元)',
        rqye DECIMAL(18,2) COMMENT '融券余额(万元)',
        rzmre DECIMAL(18,2) COMMENT '融资买入额(万元)',
        rzche DECIMAL(18,2) COMMENT '融资偿还额(万元)',
        rqmcl DECIMAL(18,4) COMMENT '融券卖出量(万股)',
        rqchl DECIMAL(18,4) COMMENT '融券偿还量(万股)',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY uk_code_date (stock_code, trade_date),
        INDEX idx_trade_date (trade_date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='融资融券交易';
    """, "trade_margin_trade"),
]


def create_tables():
    """创建补充数据表"""
    conn = get_connection()
    cursor = conn.cursor()

    print("=" * 50)
    print("创建补充数据表")
    print("=" * 50)

    for sql, table_name in SUPPLEMENT_TABLES:
        try:
            cursor.execute(sql)
            print(f"✅ {table_name} 创建成功")
        except Exception as e:
            if 'already exists' in str(e).lower():
                print(f"⏭️ {table_name} 已存在，跳过")
            else:
                print(f"❌ {table_name} 创建失败: {e}")

    conn.commit()
    cursor.close()
    conn.close()

    print("=" * 50)
    print("完成！")
    print("=" * 50)


def check_tables():
    """检查表是否存在及记录数"""
    conn = get_connection()
    cursor = conn.cursor()

    print("\n检查数据表状态:")
    print("-" * 50)

    table_names = [name for _, name in SUPPLEMENT_TABLES]

    for table_name in table_names:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  {table_name}: {count} 条记录")
        except Exception as e:
            print(f"  {table_name}: 表不存在")

    cursor.close()
    conn.close()


if __name__ == '__main__':
    create_tables()
    check_tables()
