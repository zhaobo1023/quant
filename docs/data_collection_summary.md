# QMT数据采集系统总结

## 概述

本文档总结了基于MiniQMT(xtquant)的数据采集系统，涵盖A股、港股、ETF等多种市场的数据采集能力。

## 数据采集脚本列表

### 1. A股日线数据采集 (1-行情数据采集.py)
- **数据源**: MiniQMT (xtquant)
- **目标表**: `trade_stock_daily`
- **采集范围**: 沪深A股 (约5000只)
- **字段**: stock_code, trade_date, open_price, high_price, low_price, close_price, volume, amount, turnover_rate
- **更新策略**: 增量更新 (从DB最新日期开始下载)
- **并发**: 8线程并行

### 2. A股财务数据采集 (2-财务数据采集.py)
- **数据源**: MiniQMT (xtquant)
- **目标表**: `trade_stock_financial`
- **采集范围**: 沪深A股
- **字段**: revenue, net_profit, eps, roe, roa, gross_margin, net_margin, debt_ratio, current_ratio, operating_cashflow, total_assets, total_equity
- **更新策略**: 批量下载 (每批50只)
- **并发**: 批量处理

### 3. A股分钟线数据采集 (3-分钟线数据采集.py)
- **数据源**: MiniQMT (xtquant)
- **目标表**: `trade_stock_min1`, `trade_stock_min5`, `trade_stock_min15`, `trade_stock_min30`, `trade_stock_min60`
- **采集范围**: 沪深A股
- **字段**: stock_code, trade_time, open_price, high_price, low_price, close_price, volume, amount
- **支持周期**: 1分钟/5分钟/15分钟/30分钟/60分钟
- **命令行参数**: `--period 1m/5m/15m/30m/60m`
- **数据起始**: 2024-01-01 (分钟线数据量大，只保留近期)

### 4. 交易日历采集 (4-交易日历采集.py)
- **数据源**: 从已有日线数据生成 (无需QMT API)
- **目标表**: `trade_calendar`
- **字段**: trade_date, is_trading, market
- **说明**: 原计划使用QMT API的`download_holiday_data()`需要付费版本, 因此改为从trade_stock_daily表提取交易日

### 5. 港股通数据采集 (5-港股通数据采集.py)
- **数据源**: MiniQMT (xtquant)
- **目标表**: `trade_hk_daily`
- **采集范围**: 香港联交所股票 (约3197只)
- **字段**: stock_code, trade_date, open_price, high_price, low_price, close_price, volume, amount, turnover_rate
- **并发**: 4线程 (港股数据较慢)

### 6. ETF基金数据采集 (6-基金ETF数据采集.py)
- **数据源**: MiniQMT (xtquant)
- **目标表**: `trade_etf_daily`, `trade_etf_info`
- **采集范围**: 沪市ETF + 深市ETF
- **日线字段**: fund_code, trade_date, open_price, high_price, low_price, close_price, volume, amount
- **信息字段**: fund_code, fund_name, fund_type, underlying_index, list_date, total_shares
- **并发**: 8线程

## 数据库表设计规范

### 命名规范
- 日线数据表: `trade_<market>_daily`
- 分钟线数据表: `trade_stock_min<period>`
- 信息表: `trade_<market>_info`
- 日历表: `trade_calendar`
- 财务表: `trade_stock_financial`

### 主键设计
- 日线/分钟线: (stock_code/fund_code, trade_date/trade_time)
- 信息表: (stock_code/fund_code)
- 日历表: (trade_date, market)

### 更新策略
所有表使用 `ON DUPLICATE KEY UPDATE` 实现幂等更新, 支持重复运行.

## 配置说明

### 环境变量 (.env)
```
WUCAI_SQL_HOST=数据库地址
WUCAI_SQL_USERNAME=用户名
WUCAI_SQL_PASSWORD=密码
WUCAI_SQL_DB=数据库名
WUCAI_SQL_PORT=端口
```

### 测试模式
所有脚本支持 `TEST_MODE` 开关:
- `TEST_MODE = True`: 只采集1只股票用于验证流程
- `TEST_MODE = False`: 采集全量数据

## 运行命令

```bash
# A股日线
python 1-行情数据采集.py

# A股财务
python 2-财务数据采集.py

# 分钟线 (默认1分钟)
python 3-分钟线数据采集.py
python 3-分钟线数据采集.py --period 5m

# 交易日历
python 4-交易日历采集.py

# 港股通
python 5-港股通数据采集.py

# ETF基金
python 6-基金ETF数据采集.py
```

## 依赖安装

```bash
pip install pymysql python-dotenv pandas
# 需安装QMT并配置好xtquant
```

## 当前数据概况 (2026-03-19)

| 表名 | 数量 | 记录数 | 日期范围 |
|------|------|--------|----------|
| trade_stock_daily | ~5000只A股 | 大量 | 2023-01至今 |
| trade_stock_financial | ~5000只A股 | 大量 | 2015-01至今 |
| trade_calendar | 807天 | 807条 | 2024-01-02 ~ 2026-03-18 |
| trade_hk_daily | 3181只港股 | 4,072,041条 | 2020-01-02 ~ 2026-03-19 |
| trade_etf_daily | 1449只ETF | 1,267,391条 | 2015-01-05 ~ 2026-03-18 |

## 更新日志

### 2026-03-19
- 新增分钟线数据采集 (支持1m/5m/15m/30m/60m)
- 新增交易日历采集 (基于已有日线数据生成, 532个交易日)
- 新增港股通数据采集 (香港联交所3181只股票, 407万条记录)
- 新增ETF基金数据采集 (沪深两市1449只ETF, 126万条记录)
- 修复db_config.py的.env路径问题
- 修复db_config.py密码读取问题 (支持系统环境变量)
