# 数据补充计划

## 概述

根据 `multi_strategy.md` 方案分析，多因子选股框架需要补充以下数据表。

---

## 现有数据评估

### 已有数据统计

| 数据表 | 记录数 | 股票数 | 日期范围 | 数据源 | 状态 |
|-------|--------|-------|---------|-------|------|
| `trade_stock_daily` | 2,713,899 | 5,191 | 2024-01-02 ~ 2026-03-18 | QMT | ✅ 完整 |
| `trade_stock_financial` | 166,397 | 5,154 | 2015-03-31 ~ 2025-12-31 | QMT | ⚠️ 部分字段空 |
| `trade_stock_industry` | 0 | - | - | - | ❌ 空 |
| `trade_stock_daily_basic` | 0 | - | - | - | ❌ 空 |
| `trade_stock_moneyflow` | 0 | - | - | - | ❌ 空 |
| `trade_north_holding` | 0 | - | - | - | ❌ 空 |
| `trade_margin_trade` | 0 | - | - | - | ❌ 空 |

### 财务数据字段填充情况

| 字段 | 填充数量 | 填充率 | 说明 |
|-----|---------|-------|------|
| eps | 165,460 | 99.4% | ✅ 完整 |
| roe | 165,724 | 99.6% | ✅ 完整 |
| gross_margin | 162,988 | 98.0% | ✅ 完整 |
| revenue | 1 | 0.0% | ❌ 需补充 |
| net_profit | 1 | 0.0% | ❌ 需补充 |
| roa | 1 | 0.0% | ❌ 需补充 |
| net_margin | 1 | 0.0% | ❌ 需补充 |
| debt_ratio | 1 | 0.0% | ❌ 需补充 |
| current_ratio | 1 | 0.0% | ❌ 需补充 |
| operating_cashflow | 1 | 0.0% | ❌ 需补充 |

**结论**：QMT 财务数据只采集了 EPS、ROE、毛利率，营收、净利润、现金流等关键字段几乎为空，需要从 Tushare/AKShare 补充。

### 数据重叠分析

| 数据类型 | QMT已有 | 需要补充 | 补充来源 |
|---------|--------|---------|---------|
| 日K线 | ✅ 2024-2026 完整 | 无 | - |
| 财务数据 | ⚠️ 部分字段 | revenue, net_profit, cashflow | Tushare |
| 行业分类 | ❌ 无 | 全量 | Tushare/AKShare |
| 市值/PE/PB | ❌ 无 | 全量 | Tushare |
| 资金流向 | ❌ 无 | 全量 | Tushare/AKShare |
| 北向持股 | ❌ 无 | 全量 | Tushare/AKShare |
| 融资融券 | ❌ 无 | 全量 | Tushare/AKShare |

---

## 数据缺失评估

### 已有数据 ✅

| 数据类型 | 表名 | 用途 | 状态 |
|---------|------|------|------|
| 日K线数据 | `trade_stock_daily` | 价格动量、技术因子 | ✅ 已有 |
| 财务数据 | `trade_stock_financial` | EP/BP/ROE等基本面因子 | ✅ 已有 |
| 新闻事件 | `trade_stock_news` | 情绪/事件驱动 | ✅ 表已有 |
| 研报评级 | `trade_report_consensus` | 一致预期因子 | ✅ 表已有 |
| 宏观指标 | `trade_macro_indicator` | 市场环境判断 | ✅ 表已有 |
| 利率汇率 | `trade_rate_daily` | 无风险利率参考 | ✅ 表已有 |
| 财经日历 | `trade_calendar_event` | 事件驱动 | ✅ 表已有 |

### 缺失数据 ⚠️

| 数据类型 | 用途 | 重要性 | 数据源 |
|---------|------|--------|--------|
| **行业分类** | 行业中性化处理（必须） | ⭐⭐⭐ 关键 | Tushare/AKShare |
| **市值数据** | 市值中性化 + 规模因子 | ⭐⭐⭐ 关键 | Tushare |
| **资金流数据** | 大单净流入、情绪因子 | ⭐⭐ 重要 | Tushare |
| **北向持股** | 北向资金变化、情绪因子 | ⭐⭐ 重要 | Tushare |
| **融资融券** | 融资余额变化率 | ⭐ 可选 | Tushare |

---

## 需要新增的数据表

### 1. 行业分类表 `trade_stock_industry`

```sql
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
```

**字段说明：**
- `stock_code`: 股票代码，如 600519.SH
- `industry_code`: 行业代码，如 8501
- `industry_name`: 行业名称，如 食品饮料
- `industry_level`: 申万一级行业(L1)、二级行业(L2)、三级行业(L3)
- `classify_type`: sw=申万行业分类, zx=中信行业分类

**数据源：**
- Tushare Pro: `index_classify` 接口
- AKShare: `stock_board_industry_name_em` 接口

---

### 2. 每日市值表 `trade_stock_daily_basic`

```sql
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
```

**字段说明：**
- `total_mv`: 总市值（万元）
- `circ_mv`: 流通市值（万元）
- `pe_ttm`: 滚动市盈率，用于计算 EP = 1/PE
- `pb`: 市净率，用于计算 BP = 1/PB
- `turnover_rate`: 换手率

**数据源：**
- Tushare Pro: `daily_basic` 接口

---

### 3. 资金流向表 `trade_stock_moneyflow`

```sql
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
```

**字段说明：**
- `buy_elg_vol`: 特大单买入量
- `net_mf_vol`: 净流入量 = 买入量 - 卖出量
- `net_mf_amount`: 净流入金额

**数据源：**
- Tushare Pro: `moneyflow` 接口

---

### 4. 北向持股表 `trade_north_holding`

```sql
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
```

**字段说明：**
- `hold_amount`: 北向持股数量
- `hold_change`: 持股变化，正数增持，负数减持
- `hold_ratio`: 占流通股比例

**数据源：**
- Tushare Pro: `hsgt_top10` 接口（沪深港股通十大成交股）

---

### 5. 融资融券表 `trade_margin_trade`

```sql
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
```

**字段说明：**
- `rzye`: 融资余额
- `rzmre`: 融资买入额
- `rzche`: 融资偿还额
- 融资余额变化率 = (rzye_t - rzye_t-1) / rzye_t-1

**数据源：**
- Tushare Pro: `margin` 接口

---

## 数据采集优先级

### 第一优先级（必须，用于中性化）

| 序号 | 表名 | 采集脚本 | 预计耗时 |
|-----|------|---------|---------|
| 1 | `trade_stock_industry` | `collect_industry.py` | 5分钟 |
| 2 | `trade_stock_daily_basic` | `collect_daily_basic.py` | 每日约30分钟 |

### 第二优先级（重要，用于情绪因子）

| 序号 | 表名 | 采集脚本 | 预计耗时 |
|-----|------|---------|---------|
| 3 | `trade_stock_moneyflow` | `collect_moneyflow.py` | 每日约20分钟 |
| 4 | `trade_north_holding` | `collect_north_holding.py` | 每日约10分钟 |

### 第三优先级（可选）

| 序号 | 表名 | 采集脚本 | 预计耗时 |
|-----|------|---------|---------|
| 5 | `trade_margin_trade` | `collect_margin.py` | 每日约15分钟 |

---

## 因子计算依赖关系

```
行业中性化:
  trade_stock_daily (价格)
  + trade_stock_industry (行业)
  + trade_stock_daily_basic (市值)
  → 行业市值中性化后的因子

EP/BP因子:
  trade_stock_daily_basic (pe_ttm, pb)
  → EP = 1/pe_ttm, BP = 1/pb

资金流因子:
  trade_stock_moneyflow
  → 大单净流入占比 = net_mf_vol / volume

北向资金因子:
  trade_north_holding
  → 北向持股变化率 = hold_change / hold_amount

融资情绪因子:
  trade_margin_trade
  → 融资余额变化率 = (rzye_t - rzye_t-1) / rzye_t-1
```

---

## 下一步行动

1. ~~创建上述5张数据表~~ ✅ 已完成
2. 编写数据采集脚本（放置在 `my/data_hub/` 目录）
3. 填充历史数据
4. 更新因子计算逻辑，使用新数据

---

## 数据源对比

| 特性 | QMT | Tushare | AKShare |
|-----|-----|---------|---------|
| **运行环境** | Windows + QMT客户端 | 任意（API调用） | 任意（API调用） |
| **数据质量** | 高（券商级） | 高 | 中（东方财富） |
| **更新频率** | 实时 | T+1 | T+1 |
| **权限要求** | QMT账号 | 积分制（2000分+可访问资金流） | 免费 |
| **数据类型** | 行情+财务 | 全品种 | 全品种 |
| **适用场景** | 实时交易 | 研究+回测 | 研究+回测 |

### Tushare 积分要求

| 接口 | 功能 | 最低积分 |
|-----|------|---------|
| `daily_basic` | 每日指标(市值/PE/PB) | 120分 ✅ |
| `index_classify` | 行业分类 | 120分 ✅ |
| `moneyflow` | 资金流向 | 2000分 ⚠️ |
| `hsgt_top10` | 北向持股 | 2000分 ⚠️ |
| `margin` | 融资融券 | 2000分 ⚠️ |

> 如果积分不足，资金流/北向/融资融券可使用 AKShare 作为替代数据源（免费无限制）
