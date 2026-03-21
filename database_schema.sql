-- ============================================================
-- 五彩交易系统 数据库 Schema
-- 数据库: wucai_trade
-- 生成时间: 2026-03-21
-- 表数量: 26
-- ============================================================

-- 设置字符集
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- ============================================================
-- 1. 股票日线行情表
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_stock_daily (
    id BIGINT NOT NULL AUTO_INCREMENT,
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
    PRIMARY KEY (id),
    UNIQUE KEY uk_code_date (stock_code, trade_date),
    INDEX idx_trade_date (trade_date),
    INDEX idx_stock_code (stock_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='股票日线行情表';

-- ============================================================
-- 2. 股票财务指标表
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_stock_financial (
    id BIGINT NOT NULL AUTO_INCREMENT,
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
    data_source VARCHAR(20) COMMENT '数据来源',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_code_report (stock_code, report_date),
    INDEX idx_report_date (report_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='股票财务指标表';

-- ============================================================
-- 3. 股票新闻事件表
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_stock_news (
    id BIGINT NOT NULL AUTO_INCREMENT,
    stock_code VARCHAR(20) COMMENT '股票代码',
    news_type VARCHAR(20) COMMENT '新闻类型',
    title VARCHAR(500) NOT NULL COMMENT '新闻标题',
    content TEXT COMMENT '新闻内容',
    source VARCHAR(50) COMMENT '来源',
    source_url VARCHAR(500) COMMENT '原文链接',
    sentiment VARCHAR(20) COMMENT '情感:positive/negative/neutral',
    is_important TINYINT DEFAULT 0 COMMENT '是否重要',
    published_at VARCHAR(50) COMMENT '发布时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_title (title),
    INDEX idx_stock_code (stock_code),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='股票新闻事件表';

-- ============================================================
-- 4. 研报评级/一致预期表
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_report_consensus (
    id BIGINT NOT NULL AUTO_INCREMENT,
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
    PRIMARY KEY (id),
    INDEX idx_stock_code (stock_code),
    INDEX idx_report_date (report_date),
    INDEX idx_broker (broker)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='研报评级/一致预期表';

-- ============================================================
-- 5. 宏观经济指标表(月频)
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_macro_indicator (
    id BIGINT NOT NULL AUTO_INCREMENT,
    indicator_date DATE NOT NULL COMMENT '指标日期(月度)',
    cpi_yoy DECIMAL(10,4) COMMENT 'CPI同比(%)',
    ppi_yoy DECIMAL(10,4) COMMENT 'PPI同比(%)',
    pmi DECIMAL(10,4) COMMENT 'PMI',
    m2_yoy DECIMAL(10,4) COMMENT 'M2同比(%)',
    shrzgm DECIMAL(14,2) COMMENT '社融规模增量(亿)',
    lpr_1y DECIMAL(10,4) COMMENT 'LPR 1年期(%)',
    lpr_5y DECIMAL(10,4) COMMENT 'LPR 5年期(%)',
    data_source VARCHAR(20) COMMENT '数据来源',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_indicator_date (indicator_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='宏观经济指标表(月频)';

-- ============================================================
-- 6. 利率汇率日频表
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_rate_daily (
    id BIGINT NOT NULL AUTO_INCREMENT,
    rate_date DATE NOT NULL COMMENT '日期',
    cn_bond_10y DECIMAL(10,4) COMMENT '中国10年期国债收益率(%)',
    us_bond_10y DECIMAL(10,4) COMMENT '美国10年期国债收益率(%)',
    data_source VARCHAR(20) COMMENT '数据来源',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_rate_date (rate_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='利率汇率日频表';

-- ============================================================
-- 7. 财经日历事件表
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_calendar_event (
    id BIGINT NOT NULL AUTO_INCREMENT,
    event_date DATE NOT NULL COMMENT '事件日期',
    event_time VARCHAR(20) COMMENT '事件时间',
    title VARCHAR(500) NOT NULL COMMENT '事件标题',
    country VARCHAR(50) COMMENT '国家',
    category VARCHAR(50) COMMENT '类别',
    importance TINYINT COMMENT '重要性 1-3',
    forecast_value VARCHAR(50) COMMENT '预期值',
    actual_value VARCHAR(50) COMMENT '实际值',
    previous_value VARCHAR(50) COMMENT '前值',
    source VARCHAR(50) COMMENT '来源',
    ai_prompt TEXT COMMENT 'AI提问prompt',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_event_date (event_date),
    INDEX idx_country (country),
    INDEX idx_importance (importance)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='财经日历事件表';

-- ============================================================
-- 8. 持仓管理表
-- ============================================================
CREATE TABLE IF NOT EXISTS model_trade_position (
    id BIGINT NOT NULL AUTO_INCREMENT,
    stock_code VARCHAR(20) NOT NULL COMMENT '股票代码 如600519.SH',
    stock_name VARCHAR(50) COMMENT '股票名称',
    shares INT COMMENT '持仓数量(股)',
    cost_price DECIMAL(12,4) COMMENT '成本价',
    is_margin TINYINT DEFAULT 0 COMMENT '是否融资 0-否 1-是',
    account_tag VARCHAR(50) COMMENT '账户标签',
    notes VARCHAR(500) COMMENT '备注',
    status TINYINT DEFAULT 1 COMMENT '状态 1-持有 0-已清仓',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_code_account (stock_code, account_tag),
    INDEX idx_account_tag (account_tag),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='持仓管理表';

-- ============================================================
-- 9. 股票行业分类表
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_stock_industry (
    id BIGINT NOT NULL AUTO_INCREMENT,
    stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',
    stock_name VARCHAR(50) COMMENT '股票名称',
    industry_code VARCHAR(20) COMMENT '行业代码',
    industry_name VARCHAR(50) COMMENT '行业名称',
    industry_level VARCHAR(10) COMMENT '行业级别 L1/L2/L3',
    classify_type VARCHAR(20) COMMENT '分类标准 sw(申万)/zx(中信)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_code_type_level (stock_code, classify_type, industry_level),
    INDEX idx_industry_code (industry_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='股票行业分类表';

-- ============================================================
-- 10. 每日指标表(市值/估值)
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_stock_daily_basic (
    id BIGINT NOT NULL AUTO_INCREMENT,
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
    PRIMARY KEY (id),
    UNIQUE KEY uk_code_date (stock_code, trade_date),
    INDEX idx_trade_date (trade_date),
    INDEX idx_total_mv (total_mv)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='每日指标表(市值/估值)';

-- ============================================================
-- 11. 个股资金流向表
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_stock_moneyflow (
    id BIGINT NOT NULL AUTO_INCREMENT,
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
    PRIMARY KEY (id),
    UNIQUE KEY uk_code_date (stock_code, trade_date),
    INDEX idx_trade_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='个股资金流向表';

-- ============================================================
-- 12. 北向资金持股表
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_north_holding (
    id BIGINT NOT NULL AUTO_INCREMENT,
    stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',
    hold_date DATE NOT NULL COMMENT '持股日期',
    hold_amount DECIMAL(18,4) COMMENT '持股数量(万股)',
    hold_ratio DECIMAL(10,4) COMMENT '持股占比(%)',
    hold_change DECIMAL(18,4) COMMENT '持股变化(万股)',
    hold_value DECIMAL(18,2) COMMENT '持股市值(万元)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_code_date (stock_code, hold_date),
    INDEX idx_hold_date (hold_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='北向资金持股表';

-- ============================================================
-- 13. 融资融券交易表
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_margin_trade (
    id BIGINT NOT NULL AUTO_INCREMENT,
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
    PRIMARY KEY (id),
    UNIQUE KEY uk_code_date (stock_code, trade_date),
    INDEX idx_trade_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='融资融券交易表';

-- ============================================================
-- 14. 技术指标表
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_technical_indicator (
    id BIGINT NOT NULL AUTO_INCREMENT,
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
    PRIMARY KEY (id),
    UNIQUE KEY uk_code_date (stock_code, trade_date),
    INDEX idx_trade_date (trade_date),
    INDEX idx_stock_code (stock_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='技术指标表';

-- ============================================================
-- 15. 分析报告表
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_analysis_report (
    id BIGINT NOT NULL AUTO_INCREMENT,
    stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',
    report_date DATE NOT NULL COMMENT '报告日期',
    report_type VARCHAR(20) COMMENT '报告类型',
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
    PRIMARY KEY (id),
    INDEX idx_stock_code (stock_code),
    INDEX idx_report_date (report_date),
    INDEX idx_signal_type (signal_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='分析报告表';

-- ============================================================
-- 16. OCR识别记录表
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_ocr_record (
    id BIGINT NOT NULL AUTO_INCREMENT,
    user_id INT COMMENT '用户ID',
    image_path VARCHAR(500) COMMENT '图片路径',
    ocr_type VARCHAR(20) COMMENT 'OCR类型',
    ocr_result TEXT COMMENT 'OCR识别结果',
    parsed_data JSON COMMENT '解析后的结构化数据',
    confidence DECIMAL(10,4) COMMENT '识别置信度',
    status TINYINT DEFAULT 0 COMMENT '状态 0-待处理 1-已处理 2-处理失败',
    error_message VARCHAR(500) COMMENT '错误信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='OCR识别记录表';

-- ============================================================
-- 17. 股票技术因子表
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_stock_factor (
    id INT NOT NULL AUTO_INCREMENT,
    stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',
    calc_date DATE NOT NULL COMMENT '计算日期(数据截止日期)',
    momentum_20d DOUBLE COMMENT '20日动量 ROC(20)',
    momentum_60d DOUBLE COMMENT '60日动量 ROC(60)',
    volatility DOUBLE COMMENT '波动率 ATR(14)/Close',
    rsi_14 DOUBLE COMMENT 'RSI(14)',
    adx_14 DOUBLE COMMENT 'ADX(14) 趋势强度',
    turnover_ratio DOUBLE COMMENT '换手率 当日量/20日均量',
    price_position DOUBLE COMMENT '价格位置 60日区间内位置',
    macd_signal DOUBLE COMMENT 'MACD柱状图',
    close DOUBLE COMMENT '收盘价',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_date_code (calc_date, stock_code),
    INDEX idx_calc_date (calc_date),
    INDEX idx_stock_code (stock_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='股票技术因子表';

-- ============================================================
-- 18. 1分钟K线数据表
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_stock_min1 (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='1分钟K线数据表';

-- ============================================================
-- 19. 5分钟K线数据表
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_stock_min5 (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='5分钟K线数据表';

-- ============================================================
-- 20. 15分钟K线数据表
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_stock_min15 (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='15分钟K线数据表';

-- ============================================================
-- 21. 30分钟K线数据表
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_stock_min30 (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='30分钟K线数据表';

-- ============================================================
-- 22. 60分钟K线数据表
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_stock_min60 (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='60分钟K线数据表';

-- ============================================================
-- 23. 交易日历表
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_calendar (
    trade_date DATE NOT NULL COMMENT '交易日期',
    is_trading TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否交易日 1=是 0=否',
    market VARCHAR(20) NOT NULL DEFAULT 'A股' COMMENT '市场',
    PRIMARY KEY (trade_date, market),
    INDEX idx_trade_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='交易日历表';

-- ============================================================
-- 24. 港股通日线数据表
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_hk_daily (
    stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',
    trade_date DATE NOT NULL COMMENT '交易日期',
    open_price DECIMAL(12,4) COMMENT '开盘价(港币)',
    high_price DECIMAL(12,4) COMMENT '最高价(港币)',
    low_price DECIMAL(12,4) COMMENT '最低价(港币)',
    close_price DECIMAL(12,4) COMMENT '收盘价(港币)',
    volume BIGINT COMMENT '成交量(股)',
    amount DECIMAL(20,4) COMMENT '成交额(港币)',
    turnover_rate DECIMAL(10,4) COMMENT '换手率(%)',
    PRIMARY KEY (stock_code, trade_date),
    INDEX idx_trade_date (trade_date),
    INDEX idx_stock_code (stock_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='港股通日线数据表';

-- ============================================================
-- 25. ETF基金日线数据表
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_etf_daily (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='ETF基金日线数据表';

-- ============================================================
-- 26. ETF基金基本信息表
-- ============================================================
CREATE TABLE IF NOT EXISTS trade_etf_info (
    fund_code VARCHAR(20) NOT NULL COMMENT '基金代码',
    fund_name VARCHAR(100) COMMENT '基金名称',
    fund_type VARCHAR(50) COMMENT '基金类型',
    underlying_index VARCHAR(50) COMMENT '跟踪指数',
    list_date DATE COMMENT '上市日期',
    total_shares DECIMAL(20,2) COMMENT '总份额(万份)',
    update_time DATETIME COMMENT '更新时间',
    PRIMARY KEY (fund_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='ETF基金基本信息表';
