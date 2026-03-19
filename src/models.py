# -*- coding: utf-8 -*-
"""
数据库表结构定义

核心数据表:
1. trade_stock_daily       - 股票日线行情
2. trade_stock_financial   - 股票财务指标
3. trade_stock_industry    - 股票行业分类
4. trade_stock_daily_basic - 每日指标(市值/PE/PB)

资金流数据表:
5. trade_stock_moneyflow   - 个股资金流向
6. trade_north_holding     - 北向资金持股
7. trade_margin_trade      - 融资融券交易

资讯数据表:
8. trade_stock_news        - 股票新闻事件
9. trade_report_consensus  - 研报评级/一致预期

宏观数据表:
10. trade_macro_indicator  - 宏观经济指标
11. trade_rate_daily       - 利率汇率日频
12. trade_calendar_event   - 财经日历事件

持仓管理:
13. model_trade_position   - 持仓管理

技术分析:
14. trade_technical_indicator - 技术指标(MACD/RSI/KDJ等)
15. trade_analysis_report     - 分析报告

系统功能:
16. trade_ocr_record          - OCR识别记录
"""

# 表结构定义: (表名, 建表SQL)
TABLES = [
    # 1. 股票日线行情表
    ("""
    CREATE TABLE IF NOT EXISTS trade_stock_daily (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        stock_code VARCHAR(20) NOT NULL COMMENT '股票代码 如600519.SH',
        trade_date DATE NOT NULL COMMENT '交易日期',
        open_price DECIMAL(12,4) COMMENT '开盘价',
        high_price DECIMAL(12,4) COMMENT '最高价',
        low_price DECIMAL(12,4) COMMENT '最低价',
        close_price DECIMAL(12,4) COMMENT '收盘价',
        volume BIGINT COMMENT '成交量(手)',
        amount DECIMAL(18,2) COMMENT '成交额(元)',
        turnover_rate DECIMAL(8,4) COMMENT '换手率(%)',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY uk_code_date (stock_code, trade_date),
        INDEX idx_trade_date (trade_date),
        INDEX idx_stock_code (stock_code)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票日线行情';
    """, "trade_stock_daily"),

    # 2. 股票财务指标表
    ("""
    CREATE TABLE IF NOT EXISTS trade_stock_financial (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',
        report_date DATE NOT NULL COMMENT '报告期',
        revenue DECIMAL(18,2) COMMENT '营业收入',
        net_profit DECIMAL(18,2) COMMENT '净利润',
        eps DECIMAL(10,4) COMMENT '每股收益',
        roe DECIMAL(10,4) COMMENT 'ROE(%)',
        roa DECIMAL(10,4) COMMENT 'ROA(%)',
        gross_margin DECIMAL(10,4) COMMENT '毛利率(%)',
        net_margin DECIMAL(10,4) COMMENT '净利率(%)',
        debt_ratio DECIMAL(10,4) COMMENT '资产负债率(%)',
        current_ratio DECIMAL(10,4) COMMENT '流动比率',
        operating_cashflow DECIMAL(18,2) COMMENT '经营现金流',
        total_assets DECIMAL(18,2) COMMENT '总资产',
        total_equity DECIMAL(18,2) COMMENT '股东权益',
        data_source VARCHAR(20) DEFAULT 'qmt' COMMENT '数据来源',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY uk_code_report (stock_code, report_date),
        INDEX idx_report_date (report_date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票财务指标';
    """, "trade_stock_financial"),

    # 3. 股票新闻事件表
    ("""
    CREATE TABLE IF NOT EXISTS trade_stock_news (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',
        news_type VARCHAR(20) DEFAULT 'news' COMMENT '新闻类型',
        title VARCHAR(500) NOT NULL COMMENT '新闻标题',
        content TEXT COMMENT '新闻内容',
        source VARCHAR(50) COMMENT '来源',
        source_url VARCHAR(500) COMMENT '原文链接',
        sentiment VARCHAR(20) DEFAULT 'neutral' COMMENT '情感:positive/negative/neutral',
        is_important TINYINT DEFAULT 0 COMMENT '是否重要',
        published_at VARCHAR(50) COMMENT '发布时间',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uk_title (title(191)),
        INDEX idx_stock_code (stock_code),
        INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票新闻事件';
    """, "trade_stock_news"),

    # 4. 研报评级/一致预期表
    ("""
    CREATE TABLE IF NOT EXISTS trade_report_consensus (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',
        broker VARCHAR(100) COMMENT '券商/机构',
        report_date DATE COMMENT '报告日期',
        rating VARCHAR(50) COMMENT '评级',
        target_price DECIMAL(12,4) COMMENT '目标价',
        eps_forecast_current DECIMAL(10,4) COMMENT '当年EPS预测',
        eps_forecast_next DECIMAL(10,4) COMMENT '次年EPS预测',
        revenue_forecast DECIMAL(18,2) COMMENT '营收预测',
        source_file VARCHAR(50) COMMENT '来源文件',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_stock_code (stock_code),
        INDEX idx_report_date (report_date),
        INDEX idx_broker (broker)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='研报评级/一致预期';
    """, "trade_report_consensus"),

    # 5. 宏观经济指标表(月频)
    ("""
    CREATE TABLE IF NOT EXISTS trade_macro_indicator (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        indicator_date DATE NOT NULL COMMENT '指标日期(月度)',
        cpi_yoy DECIMAL(10,4) COMMENT 'CPI同比(%)',
        ppi_yoy DECIMAL(10,4) COMMENT 'PPI同比(%)',
        pmi DECIMAL(10,4) COMMENT 'PMI',
        m2_yoy DECIMAL(10,4) COMMENT 'M2同比(%)',
        shrzgm DECIMAL(14,2) COMMENT '社融规模增量(亿)',
        lpr_1y DECIMAL(10,4) COMMENT 'LPR 1年期(%)',
        lpr_5y DECIMAL(10,4) COMMENT 'LPR 5年期(%)',
        data_source VARCHAR(20) DEFAULT 'akshare' COMMENT '数据来源',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY uk_indicator_date (indicator_date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='宏观经济指标';
    """, "trade_macro_indicator"),

    # 6. 利率汇率日频表
    ("""
    CREATE TABLE IF NOT EXISTS trade_rate_daily (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        rate_date DATE NOT NULL COMMENT '日期',
        cn_bond_10y DECIMAL(10,4) COMMENT '中国10年期国债收益率(%)',
        us_bond_10y DECIMAL(10,4) COMMENT '美国10年期国债收益率(%)',
        data_source VARCHAR(20) DEFAULT 'akshare' COMMENT '数据来源',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY uk_rate_date (rate_date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='利率汇率日频';
    """, "trade_rate_daily"),

    # 7. 财经日历事件表
    ("""
    CREATE TABLE IF NOT EXISTS trade_calendar_event (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        event_date DATE NOT NULL COMMENT '事件日期',
        event_time VARCHAR(20) COMMENT '事件时间',
        title VARCHAR(500) NOT NULL COMMENT '事件标题',
        country VARCHAR(50) DEFAULT '中国' COMMENT '国家',
        category VARCHAR(50) DEFAULT 'other' COMMENT '类别',
        importance TINYINT DEFAULT 1 COMMENT '重要性 1-3',
        forecast_value VARCHAR(50) COMMENT '预期值',
        actual_value VARCHAR(50) COMMENT '实际值',
        previous_value VARCHAR(50) COMMENT '前值',
        source VARCHAR(50) DEFAULT 'baidu_economic' COMMENT '来源',
        ai_prompt TEXT COMMENT 'AI提问prompt',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_event_date (event_date),
        INDEX idx_country (country),
        INDEX idx_importance (importance)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='财经日历事件';
    """, "trade_calendar_event"),

    # 8. 持仓管理表
    ("""
    CREATE TABLE IF NOT EXISTS model_trade_position (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        stock_code VARCHAR(20) NOT NULL COMMENT '股票代码 如600519.SH',
        stock_name VARCHAR(50) COMMENT '股票名称',
        shares INT NOT NULL DEFAULT 0 COMMENT '持仓数量(股)',
        cost_price DECIMAL(12,4) NOT NULL COMMENT '成本价',
        is_margin TINYINT DEFAULT 0 COMMENT '是否融资 0-否 1-是',
        account_tag VARCHAR(50) DEFAULT 'default' COMMENT '账户标签',
        notes VARCHAR(500) COMMENT '备注',
        status TINYINT DEFAULT 1 COMMENT '状态 1-持有 0-已清仓',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY uk_code_account (stock_code, account_tag),
        INDEX idx_account_tag (account_tag),
        INDEX idx_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='持仓管理';
    """, "model_trade_position"),

    # 9. 股票行业分类表
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

    # 10. 每日指标表(市值/估值)
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

    # 11. 个股资金流向表
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

    # 12. 北向资金持股表
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

    # 13. 融资融券交易表
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

    # 14. 技术指标表
    ("""
    CREATE TABLE IF NOT EXISTS trade_technical_indicator (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',
        trade_date DATE NOT NULL COMMENT '交易日期',
        ma5 DECIMAL(12,4) COMMENT '5日均线',
        ma10 DECIMAL(12,4) COMMENT '10日均线',
        ma20 DECIMAL(12,4) COMMENT '20日均线',
        ma60 DECIMAL(12,4) COMMENT '60日均线',
        ma120 DECIMAL(12,4) COMMENT '120日均线',
        ma250 DECIMAL(12,4) COMMENT '250日均线',
        macd_dif DECIMAL(12,4) COMMENT 'MACD-DIF',
        macd_dea DECIMAL(12,4) COMMENT 'MACD-DEA',
        macd_histogram DECIMAL(12,4) COMMENT 'MACD柱状图',
        rsi_6 DECIMAL(12,4) COMMENT 'RSI(6)',
        rsi_12 DECIMAL(12,4) COMMENT 'RSI(12)',
        rsi_24 DECIMAL(12,4) COMMENT 'RSI(24)',
        kdj_k DECIMAL(12,4) COMMENT 'KDJ-K值',
        kdj_d DECIMAL(12,4) COMMENT 'KDJ-D值',
        kdj_j DECIMAL(12,4) COMMENT 'KDJ-J值',
        bollinger_upper DECIMAL(12,4) COMMENT '布林带上轨',
        bollinger_middle DECIMAL(12,4) COMMENT '布林带中轨',
        bollinger_lower DECIMAL(12,4) COMMENT '布林带下轨',
        atr DECIMAL(12,4) COMMENT 'ATR波动率',
        volume_ratio DECIMAL(12,4) COMMENT '量比',
        turnover_rate DECIMAL(12,4) COMMENT '换手率(%)',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY uk_code_date (stock_code, trade_date),
        INDEX idx_trade_date (trade_date),
        INDEX idx_stock_code (stock_code)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='技术指标';
    """, "trade_technical_indicator"),

    # 15. 分析报告表
    ("""
    CREATE TABLE IF NOT EXISTS trade_analysis_report (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',
        report_date DATE NOT NULL COMMENT '报告日期',
        report_type VARCHAR(20) DEFAULT 'daily' COMMENT '报告类型',
        signal_type VARCHAR(20) COMMENT '信号类型',
        signal_strength DECIMAL(10,4) COMMENT '信号强度',
        current_price DECIMAL(12,4) COMMENT '当前价格',
        support_price DECIMAL(12,4) COMMENT '支撑位',
        resistance_price DECIMAL(12,4) COMMENT '阻力位',
        trend_direction VARCHAR(20) COMMENT '趋势方向',
        trend_strength DECIMAL(10,4) COMMENT '趋势强度',
        risk_level VARCHAR(20) COMMENT '风险等级',
        recommendation VARCHAR(500) COMMENT '操作建议',
        analysis_data JSON COMMENT '详细分析数据',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_stock_code (stock_code),
        INDEX idx_report_date (report_date),
        INDEX idx_signal_type (signal_type)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分析报告';
    """, "trade_analysis_report"),

    # 16. OCR识别记录表
    ("""
    CREATE TABLE IF NOT EXISTS trade_ocr_record (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        user_id INT DEFAULT 1 COMMENT '用户ID',
        image_path VARCHAR(500) COMMENT '图片路径',
        ocr_type VARCHAR(20) DEFAULT 'position' COMMENT 'OCR类型',
        ocr_result TEXT COMMENT 'OCR识别结果',
        parsed_data JSON COMMENT '解析后的结构化数据',
        confidence DECIMAL(10,4) COMMENT '识别置信度',
        status TINYINT DEFAULT 0 COMMENT '状态 0-待处理 1-已处理 2-处理失败',
        error_message VARCHAR(500) COMMENT '错误信息',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_user_id (user_id),
        INDEX idx_status (status),
        INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='OCR识别记录';
    """, "trade_ocr_record"),
]


def get_create_sql_list():
    """返回建表SQL列表"""
    return [(sql.strip(), name) for sql, name in TABLES]
