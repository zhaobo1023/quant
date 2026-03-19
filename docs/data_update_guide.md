# 数据采集更新频率指南

## 概述

本文档记录了所有数据表的更新频率、对应脚本文件和运行命令。

---

## 数据采集脚本总览

| 序号 | 脚本文件 | 目标表 | 数据源 | 更新频率 | 说明 |
|------|----------|--------|--------|----------|------|
| 1 | `1-行情数据采集.py` | `trade_stock_daily` | QMT | **每日** | A股日线数据 |
| 2 | `2-财务数据采集.py` | `trade_stock_financial` | QMT | **每周/季度** | A股财务数据 |
| 3 | `3-分钟线数据采集.py` | `trade_stock_min1/5/15/30/60` | QMT | **每日** | 分钟K线数据 |
| 4 | `4-交易日历采集.py` | `trade_calendar` | 日线数据 | **一次性/年度** | 交易日历 |
| 5 | `5-港股通数据采集.py` | `trade_hk_daily` | QMT | **每日** | 港股日线数据 |
| 6 | `6-基金ETF数据采集.py` | `trade_etf_daily`, `trade_etf_info` | QMT | **每日** | ETF日线数据 |
| 7 | `3-宏观数据采集.py` | `trade_macro_indicator` | AkShare | **每月** | 宏观经济指标 |
| 8 | `4-新闻事件采集.py` | `trade_stock_news` | AkShare | **每日** | 个股新闻事件 |
| 9 | `5-研报数据采集.py` | `trade_stock_research` | AkShare | **每日** | 券商研报评级 |
| 10 | `6-财经日历采集.py` | `trade_calendar_event` | AkShare | **每日** | 全球财经日历 |
| 11 | `7-关键催化剂采集.py` | `trade_calendar_event` | Qwen AI | **每周** | 重大事件催化剂 |

---

## 详细说明

### 1. A股日线数据 (每日更新)
- **脚本**: `1-行情数据采集.py`
- **目标表**: `trade_stock_daily`
- **数据源**: MiniQMT (xtquant)
- **更新频率**: 每个交易日收盘后
- **运行命令**:
  ```bash
  cd "example/CASE-数据采集 2"
  python 1-行情数据采集.py
  ```
- **字段**: stock_code, trade_date, open_price, high_price, low_price, close_price, volume, amount, turnover_rate

---

### 2. A股财务数据 (每季度更新)
- **脚本**: `2-财务数据采集.py`
- **目标表**: `trade_stock_financial`
- **数据源**: MiniQMT (xtquant)
- **更新频率**: 每季度财报发布后 (1/4/7/10月)，或每周增量更新
- **运行命令**:
  ```bash
  python 2-财务数据采集.py
  ```
- **字段**: revenue, net_profit, eps, roe, roa, gross_margin, net_margin, debt_ratio, current_ratio, operating_cashflow, total_assets, total_equity

---

### 3. 分钟线数据 (每日更新)
- **脚本**: `3-分钟线数据采集.py`
- **目标表**: `trade_stock_min1`, `trade_stock_min5`, `trade_stock_min15`, `trade_stock_min30`, `trade_stock_min60`
- **数据源**: MiniQMT (xtquant)
- **更新频率**: 每个交易日收盘后
- **运行命令**:
  ```bash
  # 默认1分钟
  python 3-分钟线数据采集.py
  # 指定周期
  python 3-分钟线数据采集.py --period 5m
  python 3-分钟线数据采集.py --period 15m
  python 3-分钟线数据采集.py --period 30m
  python 3-分钟线数据采集.py --period 60m
  ```
- **注意**: 分钟线数据量大，默认只保留近期数据 (从2024-01-01开始)

---

### 4. 交易日历 (一次性/年度更新)
- **脚本**: `4-交易日历采集.py`
- **目标表**: `trade_calendar`
- **数据源**: 从已有日线数据生成
- **更新频率**: 首次运行一次，之后每年补充新年份
- **运行命令**:
  ```bash
  python 4-交易日历采集.py
  ```
- **字段**: trade_date, is_trading, market

---

### 5. 港股通数据 (每日更新)
- **脚本**: `5-港股通数据采集.py`
- **目标表**: `trade_hk_daily`
- **数据源**: MiniQMT (xtquant)
- **更新频率**: 每个交易日收盘后
- **运行命令**:
  ```bash
  python 5-港股通数据采集.py
  ```
- **字段**: stock_code, trade_date, open_price, high_price, low_price, close_price, volume, amount, turnover_rate

---

### 6. ETF基金数据 (每日更新)
- **脚本**: `6-基金ETF数据采集.py`
- **目标表**: `trade_etf_daily`, `trade_etf_info`
- **数据源**: MiniQMT (xtquant)
- **更新频率**: 每个交易日收盘后
- **运行命令**:
  ```bash
  python 6-基金ETF数据采集.py
  ```
- **日线字段**: fund_code, trade_date, open_price, high_price, low_price, close_price, volume, amount
- **信息字段**: fund_code, fund_name, fund_type, underlying_index, list_date, total_shares

---

### 7. 宏观经济数据 (每月更新)
- **脚本**: `3-宏观数据采集.py`
- **目标表**: `trade_macro_indicator`
- **数据源**: AkShare
- **更新频率**: 每月 (CPI/PPI/PMI/M2等月度指标发布后)
- **运行命令**:
  ```bash
  python 3-宏观数据采集.py
  ```
- **指标**: CPI同比、PPI同比、PMI、M2同比、社融规模、LPR、国债收益率

---

### 8. 新闻事件数据 (每日更新)
- **脚本**: `4-新闻事件采集.py`
- **目标表**: `trade_stock_news`
- **数据源**: AkShare (东方财富)
- **更新频率**: 每日
- **运行命令**:
  ```bash
  python 4-新闻事件采集.py
  ```
- **字段**: stock_code, news_title, news_content, publish_time, sentiment, is_important

---

### 9. 研报数据 (每日更新)
- **脚本**: `5-研报数据采集.py`
- **目标表**: `trade_stock_research`
- **数据源**: AkShare (东方财富+同花顺)
- **更新频率**: 每日
- **运行命令**:
  ```bash
  python 5-研报数据采集.py
  ```
- **字段**: stock_code, broker_name, rating, target_price, eps_forecast, report_date

---

### 10. 财经日历 (每日更新)
- **脚本**: `6-财经日历采集.py`
- **目标表**: `trade_calendar_event`
- **数据源**: AkShare (百度财经日历)
- **更新频率**: 每日
- **运行命令**:
  ```bash
  python 6-财经日历采集.py
  ```
- **字段**: event_date, event_time, country, event_name, actual_value, forecast_value, previous_value, importance, event_type

---

### 11. 关键催化剂事件 (每周更新)
- **脚本**: `7-关键催化剂采集.py`
- **目标表**: `trade_calendar_event`
- **数据源**: Qwen Max (联网搜索)
- **更新频率**: 每周
- **运行命令**:
  ```bash
  python 7-关键催化剂采集.py
  ```
- **说明**: 使用AI搜索未来6个月重大事件 (两会、FOMC、非农等)

---

## 推荐更新计划

### 每日任务 (交易日收盘后)
```bash
cd "example/CASE-数据采集 2"
python 1-行情数据采集.py      # A股日线
python 5-港股通数据采集.py    # 港股
python 6-基金ETF数据采集.py   # ETF
python 4-新闻事件采集.py      # 新闻
python 5-研报数据采集.py      # 研报
python 6-财经日历采集.py      # 财经日历
```

### 每周任务 (周末)
```bash
python 2-财务数据采集.py      # 财务数据增量
python 7-关键催化剂采集.py    # 催化剂事件
python 3-分钟线数据采集.py    # 分钟线 (如需要)
```

### 每月任务
```bash
python 3-宏观数据采集.py      # 宏观经济指标
```

---

## 当前数据概况 (2026-03-19)

| 表名 | 数量 | 记录数 | 日期范围 |
|------|------|--------|----------|
| trade_stock_daily | 5191只A股 | - | 2024-01-02 ~ 2026-03-18 |
| trade_stock_financial | ~5000只A股 | - | 2015-01至今 |
| trade_calendar | 807天 | 807条 | 2024-01-02 ~ 2026-03-18 |
| trade_hk_daily | 3181只港股 | 4,072,041条 | 2020-01-02 ~ 2026-03-19 |
| trade_etf_daily | 1449只ETF | 1,267,391条 | 2015-01-05 ~ 2026-03-18 |

---

## 环境要求

### QMT数据源脚本
- 安装QMT并配置好xtquant
- `pip install pymysql python-dotenv pandas`

### AkShare数据源脚本
- `pip install akshare pymysql python-dotenv pandas`

### AI数据源脚本
- 配置 DASHSCOPE_API_KEY 环境变量
- `pip install openai pymysql python-dotenv pyyaml`

---

## 更新日志

### 2026-03-19
- 创建数据更新频率指南文档
- 整理所有采集脚本和对应数据表
