# 五彩交易系统 数据库 Schema 文档

**数据库名称:** `wucai_trade`
**字符集:** `utf8mb4`
**排序规则:** `utf8mb4_unicode_ci`
**表数量:** 26
**生成时间:** 2026-03-21

---

## 连接信息

| 项目 | 值 |
|------|-----|
| Host | `192.168.1.233` |
| Port | `3306` |
| Database | `wucai_trade` |
| User | `quant_user` |
| Password | `Quant@2024User` |

---

## 表清单总览

| # | 表名 | 说明 | 分类 |
|---|------|------|------|
| 1 | trade_stock_daily | 股票日线行情 | 核心行情 |
| 2 | trade_stock_min1 | 1分钟K线 | 核心行情 |
| 3 | trade_stock_min5 | 5分钟K线 | 核心行情 |
| 4 | trade_stock_min15 | 15分钟K线 | 核心行情 |
| 5 | trade_stock_min30 | 30分钟K线 | 核心行情 |
| 6 | trade_stock_min60 | 60分钟K线 | 核心行情 |
| 7 | trade_hk_daily | 港股通日线 | 核心行情 |
| 8 | trade_etf_daily | ETF日线 | 核心行情 |
| 9 | trade_stock_financial | 股票财务指标 | 财务数据 |
| 10 | trade_stock_news | 股票新闻事件 | 资讯数据 |
| 11 | trade_report_consensus | 研报评级/一致预期 | 资讯数据 |
| 12 | trade_macro_indicator | 宏观经济指标(月频) | 宏观数据 |
| 13 | trade_rate_daily | 利率汇率日频 | 宏观数据 |
| 14 | trade_calendar_event | 财经日历事件 | 宏观数据 |
| 15 | trade_stock_moneyflow | 个股资金流向 | 资金流向 |
| 16 | trade_north_holding | 北向资金持股 | 资金流向 |
| 17 | trade_margin_trade | 融资融券交易 | 资金流向 |
| 18 | trade_technical_indicator | 技术指标 | 技术分析 |
| 19 | trade_stock_factor | 股票技术因子 | 技术分析 |
| 20 | trade_analysis_report | 分析报告 | 技术分析 |
| 21 | model_trade_position | 持仓管理 | 持仓管理 |
| 22 | trade_stock_industry | 股票行业分类 | 辅助数据 |
| 23 | trade_stock_daily_basic | 每日指标(市值/估值) | 辅助数据 |
| 24 | trade_calendar | 交易日历 | 辅助数据 |
| 25 | trade_etf_info | ETF基金基本信息 | 辅助数据 |
| 26 | trade_ocr_record | OCR识别记录 | 系统功能 |

---

## 表结构详情

### 1. trade_stock_daily - 股票日线行情表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BIGINT AUTO_INCREMENT | 主键 |
| stock_code | VARCHAR(20) | 股票代码 如600519.SH |
| trade_date | DATE | 交易日期 |
| open_price | DECIMAL(12,4) | 开盘价 |
| high_price | DECIMAL(12,4) | 最高价 |
| low_price | DECIMAL(12,4) | 最低价 |
| close_price | DECIMAL(12,4) | 收盘价 |
| volume | BIGINT | 成交量(手) |
| amount | DECIMAL(18,2) | 成交额(元) |
| turnover_rate | DECIMAL(8,4) | 换手率(%) |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**索引:**
- PRIMARY KEY (id)
- UNIQUE KEY uk_code_date (stock_code, trade_date)
- INDEX idx_trade_date (trade_date)
- INDEX idx_stock_code (stock_code)

---

### 2. trade_stock_financial - 股票财务指标表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BIGINT AUTO_INCREMENT | 主键 |
| stock_code | VARCHAR(20) | 股票代码 |
| report_date | DATE | 报告期 |
| revenue | DECIMAL(18,2) | 营业收入 |
| net_profit | DECIMAL(18,2) | 净利润 |
| eps | DECIMAL(10,4) | 每股收益 |
| roe | DECIMAL(10,4) | ROE(%) |
| roa | DECIMAL(10,4) | ROA(%) |
| gross_margin | DECIMAL(10,4) | 毛利率(%) |
| net_margin | DECIMAL(10,4) | 净利率(%) |
| debt_ratio | DECIMAL(10,4) | 资产负债率(%) |
| current_ratio | DECIMAL(10,4) | 流动比率 |
| operating_cashflow | DECIMAL(18,2) | 经营现金流 |
| total_assets | DECIMAL(18,2) | 总资产 |
| total_equity | DECIMAL(18,2) | 股东权益 |
| data_source | VARCHAR(20) | 数据来源 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**索引:**
- PRIMARY KEY (id)
- UNIQUE KEY uk_code_report (stock_code, report_date)
- INDEX idx_report_date (report_date)

---

### 3. trade_stock_news - 股票新闻事件表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BIGINT AUTO_INCREMENT | 主键 |
| stock_code | VARCHAR(20) | 股票代码 |
| news_type | VARCHAR(20) | 新闻类型 |
| title | VARCHAR(500) | 新闻标题 |
| content | TEXT | 新闻内容 |
| source | VARCHAR(50) | 来源 |
| source_url | VARCHAR(500) | 原文链接 |
| sentiment | VARCHAR(20) | 情感:positive/negative/neutral |
| is_important | TINYINT | 是否重要 |
| published_at | VARCHAR(50) | 发布时间 |
| created_at | TIMESTAMP | 创建时间 |

**索引:**
- PRIMARY KEY (id)
- UNIQUE KEY uk_title (title)
- INDEX idx_stock_code (stock_code)
- INDEX idx_created_at (created_at)

---

### 4. trade_report_consensus - 研报评级/一致预期表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BIGINT AUTO_INCREMENT | 主键 |
| stock_code | VARCHAR(20) | 股票代码 |
| broker | VARCHAR(100) | 券商/机构 |
| report_date | DATE | 报告日期 |
| rating | VARCHAR(50) | 评级 |
| target_price | DECIMAL(12,4) | 目标价 |
| eps_forecast_current | DECIMAL(10,4) | 当年EPS预测 |
| eps_forecast_next | DECIMAL(10,4) | 次年EPS预测 |
| revenue_forecast | DECIMAL(18,2) | 营收预测 |
| source_file | VARCHAR(50) | 来源文件 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**索引:**
- PRIMARY KEY (id)
- INDEX idx_stock_code (stock_code)
- INDEX idx_report_date (report_date)
- INDEX idx_broker (broker)

---

### 5. trade_macro_indicator - 宏观经济指标表(月频)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BIGINT AUTO_INCREMENT | 主键 |
| indicator_date | DATE | 指标日期(月度) |
| cpi_yoy | DECIMAL(10,4) | CPI同比(%) |
| ppi_yoy | DECIMAL(10,4) | PPI同比(%) |
| pmi | DECIMAL(10,4) | PMI |
| m2_yoy | DECIMAL(10,4) | M2同比(%) |
| shrzgm | DECIMAL(14,2) | 社融规模增量(亿) |
| lpr_1y | DECIMAL(10,4) | LPR 1年期(%) |
| lpr_5y | DECIMAL(10,4) | LPR 5年期(%) |
| data_source | VARCHAR(20) | 数据来源 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**索引:**
- PRIMARY KEY (id)
- UNIQUE KEY uk_indicator_date (indicator_date)

---

### 6. trade_rate_daily - 利率汇率日频表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BIGINT AUTO_INCREMENT | 主键 |
| rate_date | DATE | 日期 |
| cn_bond_10y | DECIMAL(10,4) | 中国10年期国债收益率(%) |
| us_bond_10y | DECIMAL(10,4) | 美国10年期国债收益率(%) |
| data_source | VARCHAR(20) | 数据来源 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**索引:**
- PRIMARY KEY (id)
- UNIQUE KEY uk_rate_date (rate_date)

---

### 7. trade_calendar_event - 财经日历事件表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BIGINT AUTO_INCREMENT | 主键 |
| event_date | DATE | 事件日期 |
| event_time | VARCHAR(20) | 事件时间 |
| title | VARCHAR(500) | 事件标题 |
| country | VARCHAR(50) | 国家 |
| category | VARCHAR(50) | 类别 |
| importance | TINYINT | 重要性 1-3 |
| forecast_value | VARCHAR(50) | 预期值 |
| actual_value | VARCHAR(50) | 实际值 |
| previous_value | VARCHAR(50) | 前值 |
| source | VARCHAR(50) | 来源 |
| ai_prompt | TEXT | AI提问prompt |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**索引:**
- PRIMARY KEY (id)
- INDEX idx_event_date (event_date)
- INDEX idx_country (country)
- INDEX idx_importance (importance)

---

### 8. model_trade_position - 持仓管理表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BIGINT AUTO_INCREMENT | 主键 |
| stock_code | VARCHAR(20) | 股票代码 如600519.SH |
| stock_name | VARCHAR(50) | 股票名称 |
| shares | INT | 持仓数量(股) |
| cost_price | DECIMAL(12,4) | 成本价 |
| is_margin | TINYINT | 是否融资 0-否 1-是 |
| account_tag | VARCHAR(50) | 账户标签 |
| notes | VARCHAR(500) | 备注 |
| status | TINYINT | 状态 1-持有 0-已清仓 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**索引:**
- PRIMARY KEY (id)
- UNIQUE KEY uk_code_account (stock_code, account_tag)
- INDEX idx_account_tag (account_tag)
- INDEX idx_status (status)

---

### 9. trade_stock_industry - 股票行业分类表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BIGINT AUTO_INCREMENT | 主键 |
| stock_code | VARCHAR(20) | 股票代码 |
| stock_name | VARCHAR(50) | 股票名称 |
| industry_code | VARCHAR(20) | 行业代码 |
| industry_name | VARCHAR(50) | 行业名称 |
| industry_level | VARCHAR(10) | 行业级别 L1/L2/L3 |
| classify_type | VARCHAR(20) | 分类标准 sw(申万)/zx(中信) |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**索引:**
- PRIMARY KEY (id)
- UNIQUE KEY uk_code_type_level (stock_code, classify_type, industry_level)
- INDEX idx_industry_code (industry_code)

---

### 10. trade_stock_daily_basic - 每日指标表(市值/估值)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BIGINT AUTO_INCREMENT | 主键 |
| stock_code | VARCHAR(20) | 股票代码 |
| trade_date | DATE | 交易日期 |
| total_mv | DECIMAL(18,4) | 总市值(万元) |
| circ_mv | DECIMAL(18,4) | 流通市值(万元) |
| pe_ttm | DECIMAL(10,4) | 市盈率TTM |
| pb | DECIMAL(10,4) | 市净率 |
| ps_ttm | DECIMAL(10,4) | 市销率TTM |
| total_share | DECIMAL(18,4) | 总股本(万股) |
| circ_share | DECIMAL(18,4) | 流通股本(万股) |
| turnover_rate | DECIMAL(8,4) | 换手率(%) |
| free_share | DECIMAL(18,4) | 自由流通股本(万股) |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**索引:**
- PRIMARY KEY (id)
- UNIQUE KEY uk_code_date (stock_code, trade_date)
- INDEX idx_trade_date (trade_date)
- INDEX idx_total_mv (total_mv)

---

### 11. trade_stock_moneyflow - 个股资金流向表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BIGINT AUTO_INCREMENT | 主键 |
| stock_code | VARCHAR(20) | 股票代码 |
| trade_date | DATE | 交易日期 |
| buy_sm_vol | DECIMAL(18,2) | 小单买入量(手) |
| buy_md_vol | DECIMAL(18,2) | 中单买入量(手) |
| buy_lg_vol | DECIMAL(18,2) | 大单买入量(手) |
| buy_elg_vol | DECIMAL(18,2) | 特大单买入量(手) |
| sell_sm_vol | DECIMAL(18,2) | 小单卖出量(手) |
| sell_md_vol | DECIMAL(18,2) | 中单卖出量(手) |
| sell_lg_vol | DECIMAL(18,2) | 大单卖出量(手) |
| sell_elg_vol | DECIMAL(18,2) | 特大单卖出量(手) |
| net_mf_vol | DECIMAL(18,2) | 净流入量(手) |
| net_mf_amount | DECIMAL(18,2) | 净流入额(万元) |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**索引:**
- PRIMARY KEY (id)
- UNIQUE KEY uk_code_date (stock_code, trade_date)
- INDEX idx_trade_date (trade_date)

---

### 12. trade_north_holding - 北向资金持股表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BIGINT AUTO_INCREMENT | 主键 |
| stock_code | VARCHAR(20) | 股票代码 |
| hold_date | DATE | 持股日期 |
| hold_amount | DECIMAL(18,4) | 持股数量(万股) |
| hold_ratio | DECIMAL(10,4) | 持股占比(%) |
| hold_change | DECIMAL(18,4) | 持股变化(万股) |
| hold_value | DECIMAL(18,2) | 持股市值(万元) |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**索引:**
- PRIMARY KEY (id)
- UNIQUE KEY uk_code_date (stock_code, hold_date)
- INDEX idx_hold_date (hold_date)

---

### 13. trade_margin_trade - 融资融券交易表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BIGINT AUTO_INCREMENT | 主键 |
| stock_code | VARCHAR(20) | 股票代码 |
| trade_date | DATE | 交易日期 |
| rzye | DECIMAL(18,2) | 融资余额(万元) |
| rqye | DECIMAL(18,2) | 融券余额(万元) |
| rzmre | DECIMAL(18,2) | 融资买入额(万元) |
| rzche | DECIMAL(18,2) | 融资偿还额(万元) |
| rqmcl | DECIMAL(18,4) | 融券卖出量(万股) |
| rqchl | DECIMAL(18,4) | 融券偿还量(万股) |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**索引:**
- PRIMARY KEY (id)
- UNIQUE KEY uk_code_date (stock_code, trade_date)
- INDEX idx_trade_date (trade_date)

---

### 14. trade_technical_indicator - 技术指标表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BIGINT AUTO_INCREMENT | 主键 |
| stock_code | VARCHAR(20) | 股票代码 |
| trade_date | DATE | 交易日期 |
| ma5 | DECIMAL(12,4) | 5日均线 |
| ma10 | DECIMAL(12,4) | 10日均线 |
| ma20 | DECIMAL(12,4) | 20日均线 |
| ma60 | DECIMAL(12,4) | 60日均线 |
| ma120 | DECIMAL(12,4) | 120日均线 |
| ma250 | DECIMAL(12,4) | 250日均线 |
| macd_dif | DECIMAL(12,4) | MACD-DIF |
| macd_dea | DECIMAL(12,4) | MACD-DEA |
| macd_histogram | DECIMAL(12,4) | MACD柱状图 |
| rsi_6 | DECIMAL(12,4) | RSI(6) |
| rsi_12 | DECIMAL(12,4) | RSI(12) |
| rsi_24 | DECIMAL(12,4) | RSI(24) |
| kdj_k | DECIMAL(12,4) | KDJ-K值 |
| kdj_d | DECIMAL(12,4) | KDJ-D值 |
| kdj_j | DECIMAL(12,4) | KDJ-J值 |
| bollinger_upper | DECIMAL(12,4) | 布林带上轨 |
| bollinger_middle | DECIMAL(12,4) | 布林带中轨 |
| bollinger_lower | DECIMAL(12,4) | 布林带下轨 |
| atr | DECIMAL(12,4) | ATR波动率 |
| volume_ratio | DECIMAL(12,4) | 量比 |
| turnover_rate | DECIMAL(12,4) | 换手率(%) |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**索引:**
- PRIMARY KEY (id)
- UNIQUE KEY uk_code_date (stock_code, trade_date)
- INDEX idx_trade_date (trade_date)
- INDEX idx_stock_code (stock_code)

---

### 15. trade_analysis_report - 分析报告表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BIGINT AUTO_INCREMENT | 主键 |
| stock_code | VARCHAR(20) | 股票代码 |
| report_date | DATE | 报告日期 |
| report_type | VARCHAR(20) | 报告类型 |
| signal_type | VARCHAR(20) | 信号类型 |
| signal_strength | DECIMAL(10,4) | 信号强度 |
| current_price | DECIMAL(12,4) | 当前价格 |
| support_price | DECIMAL(12,4) | 支撑位 |
| resistance_price | DECIMAL(12,4) | 阻力位 |
| trend_direction | VARCHAR(20) | 趋势方向 |
| trend_strength | DECIMAL(10,4) | 趋势强度 |
| risk_level | VARCHAR(20) | 风险等级 |
| recommendation | VARCHAR(500) | 操作建议 |
| analysis_data | JSON | 详细分析数据 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**索引:**
- PRIMARY KEY (id)
- INDEX idx_stock_code (stock_code)
- INDEX idx_report_date (report_date)
- INDEX idx_signal_type (signal_type)

---

### 16. trade_ocr_record - OCR识别记录表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BIGINT AUTO_INCREMENT | 主键 |
| user_id | INT | 用户ID |
| image_path | VARCHAR(500) | 图片路径 |
| ocr_type | VARCHAR(20) | OCR类型 |
| ocr_result | TEXT | OCR识别结果 |
| parsed_data | JSON | 解析后的结构化数据 |
| confidence | DECIMAL(10,4) | 识别置信度 |
| status | TINYINT | 状态 0-待处理 1-已处理 2-处理失败 |
| error_message | VARCHAR(500) | 错误信息 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**索引:**
- PRIMARY KEY (id)
- INDEX idx_user_id (user_id)
- INDEX idx_status (status)
- INDEX idx_created_at (created_at)

---

### 17. trade_stock_factor - 股票技术因子表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INT AUTO_INCREMENT | 主键 |
| stock_code | VARCHAR(20) | 股票代码 |
| calc_date | DATE | 计算日期(数据截止日期) |
| momentum_20d | DOUBLE | 20日动量 ROC(20) |
| momentum_60d | DOUBLE | 60日动量 ROC(60) |
| volatility | DOUBLE | 波动率 ATR(14)/Close |
| rsi_14 | DOUBLE | RSI(14) |
| adx_14 | DOUBLE | ADX(14) 趋势强度 |
| turnover_ratio | DOUBLE | 换手率 当日量/20日均量 |
| price_position | DOUBLE | 价格位置 60日区间内位置 |
| macd_signal | DOUBLE | MACD柱状图 |
| close | DOUBLE | 收盘价 |
| created_at | TIMESTAMP | 创建时间 |

**索引:**
- PRIMARY KEY (id)
- UNIQUE KEY uk_date_code (calc_date, stock_code)
- INDEX idx_calc_date (calc_date)
- INDEX idx_stock_code (stock_code)

---

### 18-22. 分钟K线数据表 (trade_stock_min1/min5/min15/min30/min60)

统一结构（5张表，周期不同）:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| stock_code | VARCHAR(20) | 股票代码 |
| trade_time | DATETIME | 交易时间 |
| open_price | DECIMAL(10,3) | 开盘价 |
| high_price | DECIMAL(10,3) | 最高价 |
| low_price | DECIMAL(10,3) | 最低价 |
| close_price | DECIMAL(10,3) | 收盘价 |
| volume | BIGINT | 成交量(手) |
| amount | DECIMAL(18,3) | 成交额 |

**索引:**
- PRIMARY KEY (stock_code, trade_time)
- INDEX idx_trade_time (trade_time)
- INDEX idx_stock_code (stock_code)

---

### 23. trade_calendar - 交易日历表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| trade_date | DATE | 交易日期 |
| is_trading | TINYINT(1) | 是否交易日 1=是 0=否 |
| market | VARCHAR(20) | 市场 |

**索引:**
- PRIMARY KEY (trade_date, market)
- INDEX idx_trade_date (trade_date)

---

### 24. trade_hk_daily - 港股通日线数据表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| stock_code | VARCHAR(20) | 股票代码 |
| trade_date | DATE | 交易日期 |
| open_price | DECIMAL(12,4) | 开盘价(港币) |
| high_price | DECIMAL(12,4) | 最高价(港币) |
| low_price | DECIMAL(12,4) | 最低价(港币) |
| close_price | DECIMAL(12,4) | 收盘价(港币) |
| volume | BIGINT | 成交量(股) |
| amount | DECIMAL(20,4) | 成交额(港币) |
| turnover_rate | DECIMAL(10,4) | 换手率(%) |

**索引:**
- PRIMARY KEY (stock_code, trade_date)
- INDEX idx_trade_date (trade_date)
- INDEX idx_stock_code (stock_code)

---

### 25. trade_etf_daily - ETF基金日线数据表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| fund_code | VARCHAR(20) | 基金代码 |
| trade_date | DATE | 交易日期 |
| open_price | DECIMAL(10,4) | 开盘价 |
| high_price | DECIMAL(10,4) | 最高价 |
| low_price | DECIMAL(10,4) | 最低价 |
| close_price | DECIMAL(10,4) | 收盘价 |
| volume | BIGINT | 成交量(手) |
| amount | DECIMAL(18,4) | 成交额 |

**索引:**
- PRIMARY KEY (fund_code, trade_date)
- INDEX idx_trade_date (trade_date)
- INDEX idx_fund_code (fund_code)

---

### 26. trade_etf_info - ETF基金基本信息表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| fund_code | VARCHAR(20) | 基金代码 |
| fund_name | VARCHAR(100) | 基金名称 |
| fund_type | VARCHAR(50) | 基金类型 |
| underlying_index | VARCHAR(50) | 跟踪指数 |
| list_date | DATE | 上市日期 |
| total_shares | DECIMAL(20,2) | 总份额(万份) |
| update_time | DATETIME | 更新时间 |

**索引:**
- PRIMARY KEY (fund_code)

---

## 文件位置

- **SQL Schema 文件:** `/Users/wenwen/data0/person/quant/database_schema.sql`
- **本文档:** `/Users/wenwen/data0/person/quant/DATABASE_SCHEMA.md`
- **数据存储目录:** `/Users/wenwen/data0/person/data/mysql/data/`
