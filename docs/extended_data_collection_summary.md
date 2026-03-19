# 扩展数据采集功能总结

## 概述

本次在 `feature/extended-data-collection` 分支上新增了以下数据采集能力：

## 新增数据采集功能

### 1. 交易日历采集 (4-交易日历采集.py)
- **数据源**: 从已有日线数据生成 (QMT API需要付费版本)
- **目标表**: `trade_calendar`
- **采集结果**: 807天记录 (532个交易日, 275个非交易日)
- **日期范围**: 2024-01-02 ~ 2026-03-18

### 2. 港股通数据采集 (5-港股通数据采集.py)
- **数据源**: MiniQMT (xtquant)
- **目标表**: `trade_hk_daily`
- **采集范围**: 香港联交所股票
- **采集结果**: 3181只股票, 4,072,041条记录
- **日期范围**: 2020-01-02 ~ 2026-03-19
- **并发**: 4线程 (港股数据较慢)

- **字段**: stock_code, trade_date, open_price, high_price, low_price, close_price, volume, amount, turnover_rate

- **命令**: `python 5-港股通数据采集.py`

### 3. ETF基金数据采集 (6-基金ETF数据采集.py)
- **数据源**: MiniQMT (xtquant)
- **目标表**: `trade_etf_daily`, `trade_etf_info`
- **采集范围**: 沪市ETF + 深市ETF
- **采集结果**: 1449只ETF, 1,267,391条日线记录
- **日期范围**: 2015-01-05 ~ 2026-03-18
- **并发**: 8线程

- **日线字段**: fund_code, trade_date, open_price, high_price, low_price, close_price, volume, amount
- **信息字段**: fund_code, fund_name, fund_type, underlying_index, list_date, total_shares
- **命令**: `python 6-基金ETF数据采集.py`

### 4. 分钟线数据采集 (3-分钟线数据采集.py)
- **数据源**: MiniQMT (xtquant)
- **目标表**: `trade_stock_min1`, `trade_stock_min5`, `trade_stock_min15`, `trade_stock_min30`, `trade_stock_min60`
- **支持周期**: 1分钟/5分钟/15分钟/30分钟/60分钟
- **命令**:
  ```bash
  python 3-分钟线数据采集.py              # 默认1分钟
  python 3-分钟线数据采集.py --period 5m   # 5分钟
  python 3-分钟线数据采集.py --period 15m  # 15分钟
  python 3-分钟线数据采集.py --period 30m  # 30分钟
  python 3-分钟线数据采集.py --period 60m  # 60分钟
  ```

- **注意**: 分钟线数据量大，默认只保留近期数据 (从2024-01-01开始)

## 数据库表设计

### 交易日历表 (trade_calendar)
```sql
CREATE TABLE trade_calendar (
    trade_date DATE NOT NULL COMMENT '交易日期',
    is_trading TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否交易日 1=是 0=否',
    market VARCHAR(20) NOT NULL DEFAULT 'A股' COMMENT '市场',
    PRIMARY KEY (trade_date, market)
);
```

### 港股日线表 (trade_hk_daily)
```sql
CREATE TABLE trade_hk_daily (
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
);
```
### ETF日线表 (trade_etf_daily)
```sql
CREATE TABLE trade_etf_daily (
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
);
```
### ETF信息表 (trade_etf_info)
```sql
CREATE TABLE trade_etf_info (
    fund_code VARCHAR(20) NOT NULL COMMENT '基金代码',
    fund_name VARCHAR(100) COMMENT '基金名称',
    fund_type VARCHAR(50) COMMENT '基金类型',
    underlying_index VARCHAR(50) COMMENT '跟踪指数',
    list_date DATE COMMENT '上市日期',
    total_shares DECIMAL(20,2) COMMENT '总份额(万份)',
    update_time DATETIME COMMENT '更新时间',
    PRIMARY KEY (fund_code)
);
```
### 分钟线表 (trade_stock_min1/5/15/30/60)
```sql
CREATE TABLE trade_stock_min1 (
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
);
```

## 当前数据概况 (2026-03-19)

| 表名 | 数量 | 记录数 | 日期范围 |
|------|------|--------|----------|
| trade_stock_daily | 5191只A股 | - | 2024-01-02 ~ 2026-03-18 |
| trade_stock_financial | ~5000只A股 | - | 2015-01至今 |
| trade_calendar | 807天 | 807条 | 2024-01-02 ~ 2026-03-18 |
| trade_hk_daily | 3181只港股 | 4,072,041条 | 2020-01-02 ~ 2026-03-19 |
| trade_etf_daily | 1449只ETF | 1,267,391条 | 2015-01-05 ~ 2026-03-18 |

## Bug修复

1. **db_config.py .env路径问题**
   - 償还从 `parent / '.env'` 改为 `parent.parent / '.env'`
   - 确保.example/CASE-数据采集 2/db_config.py能正确读取.quant/.env

2. **db_config.py密码读取问题**
   - `dotenv_values()` 不会读取系统环境变量
   - 添加 `os.environ.get()` 优先检查系统环境变量
   - 确保 WUCAI_SQL_PASSWORD 环境变量能被正确读取

3. **交易日历采集QMT API问题**
   - `download_holiday_data()` 和 `get_trading_calendar()` 需要付费版QMT
   - 改为从已有 trade_stock_daily 表提取交易日
   - 顫充非交易日(周末等)以生成完整日历

## 更新日志

### 2026-03-19
- 新增分钟线数据采集 (支持1m/5m/15m/30m/60m)
- 新增交易日历采集 (基于已有日线数据生成, 532个交易日)
- 新增港股通数据采集 (香港联交所3181只股票, 407万条记录)
- 新增ETF基金数据采集 (沪深两市1449只ETF, 126万条记录)
- 修复db_config.py的.env路径问题
- 修复db_config.py密码读取问题 (支持系统环境变量)
