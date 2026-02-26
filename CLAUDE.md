# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Quantitative trading project for Chinese A-share stocks containing data collection, multi-factor stock screening, and strategy backtesting modules.

## Directory Structure

```
quant/
├── CASE-1/                    # Basic strategy backtests
│   ├── 1-qmt_download_data.py
│   ├── 1-tushare_download_data.py
│   ├── 2-macd_strategy_2025.py
│   └── 3-grid_strategy_2025.py
├── CASE-数据采集/              # Data collection (CSV output)
│   ├── 日线数据-QMT.py / tushare.py / akshare.py
│   ├── 分钟数据-QMT.py / tushare.py / akshare.py
│   └── 财务数据-QMT.py / tushare.py / akshare.py
├── CASE-数据采集 2/            # Data collection (MySQL storage)
│   ├── db_config.py           # DB connection config (reads from .env)
│   ├── 1-行情数据采集.py       # Daily OHLCV → MySQL
│   ├── 2-财务数据采集.py       # Financials → MySQL
│   ├── 3-宏观数据采集.py
│   ├── 4-新闻事件采集.py
│   ├── 5-研报数据采集.py
│   ├── 6-财经日历采集.py
│   └── 7-关键催化剂采集.py
└── CASE-多因子选股/            # Multi-factor stock screening
    ├── 多因子选股-下载数据.py
    ├── 多因子选股-筛选1.py
    └── 多因子选股-筛选2.py
```

## Commands

### Data Collection (CASE-1)
```bash
cd CASE-1
python 1-qmt_download_data.py      # QMT source
python 1-tushare_download_data.py  # Tushare source (needs TUSHARE_TOKEN)
```

### Strategy Backtests (CASE-1)
```bash
cd CASE-1
python 2-macd_strategy_2025.py     # MACD golden/death cross
python 3-grid_strategy_2025.py     # Grid trading with position levels
```

### Multi-factor Screening (CASE-多因子选股)
```bash
cd CASE-多因子选股
python 多因子选股-下载数据.py      # Download financial data
python 多因子选股-筛选1.py         # 5-factor funnel screening
```

### Data Collection to MySQL (CASE-数据采集 2)
```bash
cd "CASE-数据采集 2"
# First create .env with DB credentials (see db_config.py)
python 1-行情数据采集.py           # Set TEST_MODE=True for testing
```

## Data Formats

### CSV Format (CASE-1, CASE-数据采集)
Standard columns: `date`, `close`, `open`, `high`, `low`, `volume`

### MySQL Tables (CASE-数据采集 2)
- `trade_stock_daily`: Daily OHLCV data
- Configuration via environment variables (see `db_config.py`)

## Strategy Details

### MACD Strategy (CASE-1/2-macd_strategy_2025.py)
- Golden cross (DIF > DEA) → full position buy
- Death cross (DIF < DEA) → full position sell
- Outputs: nav CSV, trades CSV, summary TXT, PNG chart

### Grid Strategy (CASE-1/3-grid_strategy_2025.py)
- `GridStrategy` class with position level tracking
- Level-based execution: each buy increments level, each sell decrements
- Grid prices: buy at [1450, 1400, 1350, 1300], sell at [1550, 1600, 1650, 1700]

### Multi-factor Screening (CASE-多因子选股)
5-layer funnel with absolute thresholds:
1. ROE >= 15%
2. Net profit YoY >= 10%
3. Gross margin >= 30%
4. Debt-to-assets <= 60%
5. Operating cash flow / revenue >= 10%

## Environment Variables

- `TUSHARE_TOKEN`: Tushare API token
- MySQL (for CASE-数据采集 2):
  - `WUCAI_SQL_HOST`, `WUCAI_SQL_USERNAME`, `WUCAI_SQL_PASSWORD`
  - `WUCAI_SQL_DB`, `WUCAI_SQL_PORT`
- AI APIs: `KIMI_API_KEY`, `DASHSCOPE_API_KEY`

## Dependencies

- Core: pandas, numpy, matplotlib
- Data sources: tushare, xtquant (QMT), akshare
- Database: pymysql, python-dotenv

## Chinese Font Configuration

All scripts configure matplotlib for Chinese:
```python
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False
```
