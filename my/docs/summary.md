# 多因子选股数据体系总结

## 一、项目背景

根据 `multi_strategy.md` 方案，多因子选股框架需要进行以下改进：

1. **因子体系重构**：引入动量、价值、质量、流动性、情绪类因子
2. **行业/市值中性化**：必须做中性化处理，否则选股结果本质是行业轮动
3. **动态权重优化**：从手动权重升级为 IC 加权、风险平价
4. **补充数据源**：行业分类、市值数据、资金流数据等

---

## 二、数据现状评估

### 2.1 已有数据

| 数据表 | 记录数 | 股票数 | 日期范围 | 数据源 | 状态 |
|-------|--------|-------|---------|-------|------|
| `trade_stock_daily` | 2,713,899 | 5,191 | 2024-01-02 ~ 2026-03-18 | QMT | ✅ 完整 |
| `trade_stock_financial` | 166,397 | 5,154 | 2015-03-31 ~ 2025-12-31 | QMT | ⚠️ 部分字段空 |

### 2.2 缺失数据

| 数据表 | 用途 | 重要性 | 数据源 |
|-------|------|--------|--------|
| `trade_stock_industry` | 行业中性化（必须） | ⭐⭐⭐ 关键 | Tushare/AKShare |
| `trade_stock_daily_basic` | 市值中性化 + EP/BP因子 | ⭐⭐⭐ 关键 | Tushare |
| `trade_stock_moneyflow` | 大单净流入、情绪因子 | ⭐⭐ 重要 | Tushare/AKShare |
| `trade_north_holding` | 北向资金变化 | ⭐⭐ 重要 | Tushare/AKShare |
| `trade_margin_trade` | 融资余额变化率 | ⭐ 可选 | Tushare/AKShare |

### 2.3 财务数据字段缺失

QMT 采集的财务数据只填充了部分字段：

| 字段 | 填充率 | 状态 |
|-----|-------|------|
| eps | 99.4% | ✅ |
| roe | 99.6% | ✅ |
| gross_margin | 98.0% | ✅ |
| revenue | 0.0% | ❌ 需补充 |
| net_profit | 0.0% | ❌ 需补充 |
| debt_ratio | 0.0% | ❌ 需补充 |
| operating_cashflow | 0.0% | ❌ 需补充 |

---

## 三、数据采集中控台方案

### 3.1 架构设计

```
┌────────────────────┐     HTTP API      ┌─────────────────┐
│  数据中控台         │◄──────────────────│  Windows QMT    │
│  (Mac/Linux)       │                    │  Agent          │
│  - Tushare采集     │                    │  - 日K线采集    │
│  - AKShare采集     │                    │  - 财务数据采集 │
│  - 任务调度        │                    │                 │
└────────┬───────────┘                    └────────┬────────┘
         │                                         │
         └────────────────┬────────────────────────┘
                          ▼
                  ┌───────────────┐
                  │ MySQL 数据库   │
                  │ (云端RDS)      │
                  └───────────────┘
```

### 3.2 任务分配

| 环境 | 数据源 | 采集内容 |
|-----|-------|---------|
| Mac/Linux | Tushare | 行业分类、每日指标(市值/PE/PB)、财务补充 |
| Mac/Linux | AKShare | 资金流向、北向持股、融资融券（Tushare积分不足时） |
| Windows | QMT | 日K线增量、分钟数据、实时行情 |

### 3.3 采集优先级

| 优先级 | 任务 | 数据源 | 频率 | 说明 |
|-------|-----|-------|------|------|
| P0 | 行业分类 | Tushare | 一次性 | 中性化必需 |
| P0 | 每日指标(市值/PE) | Tushare | 每日 | 中性化必需 |
| P1 | 财务数据补充 | Tushare | 季度 | 补充营收、净利润等 |
| P2 | 资金流向 | AKShare | 每日 | 情绪因子 |
| P2 | 北向持股 | AKShare | 每日 | 情绪因子 |
| P3 | 融资融券 | AKShare | 每日 | 情绪因子 |

---

## 四、数据库表结构

### 4.1 已有表（8张）

1. `trade_stock_daily` - 股票日线行情
2. `trade_stock_financial` - 股票财务指标
3. `trade_stock_news` - 股票新闻事件
4. `trade_report_consensus` - 研报评级/一致预期
5. `trade_macro_indicator` - 宏观经济指标
6. `trade_rate_daily` - 利率汇率日频
7. `trade_calendar_event` - 财经日历事件
8. `model_trade_position` - 持仓管理

### 4.2 新增表（5张）✅ 已创建

1. `trade_stock_industry` - 股票行业分类
2. `trade_stock_daily_basic` - 每日指标(市值/估值)
3. `trade_stock_moneyflow` - 个股资金流向
4. `trade_north_holding` - 北向资金持股
5. `trade_margin_trade` - 融资融券交易

---

## 五、环境配置

### 5.1 环境变量 (.env)

```bash
# 数据库配置
WUCAI_SQL_HOST=123.56.3.1
WUCAI_SQL_USERNAME=root
WUCAI_SQL_PASSWORD=***
WUCAI_SQL_PORT=3306
WUCAI_SQL_DB=trade

# Tushare API
TUSHARE_TOKEN=7c9f8381...

# 回测参数
BACKTEST_INITIAL_CASH=1000000
BACKTEST_COMMISSION=0.0002
BACKTEST_POSITION_PCT=95
```

### 5.2 数据源权限

- **Tushare Token**：✅ 已配置，基础接口可用
- **积分情况**：120分（基础权限），资金流接口需要2000分+
- **替代方案**：AKShare 免费，可作为资金流/北向/融资融券的数据源

---

## 六、因子计算依赖

```
┌─────────────────────────────────────────────────────────────┐
│                      因子计算依赖图                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  技术因子 (已有)                                             │
│  ├── trade_stock_daily → 动量(ROC)、波动率(ATR)、RSI、ADX   │
│  └── talib 计算                                             │
│                                                             │
│  基本面因子 (需补充)                                          │
│  ├── trade_stock_daily_basic                                │
│  │   ├── total_mv → 市值因子                                │
│  │   ├── pe_ttm → EP = 1/PE                                │
│  │   └── pb → BP = 1/PB                                    │
│  └── trade_stock_financial                                  │
│      ├── roe → 质量因子                                     │
│      └── gross_margin → 盈利能力                            │
│                                                             │
│  中性化处理 (需补充)                                          │
│  ├── trade_stock_industry → 行业哑变量                      │
│  └── trade_stock_daily_basic.total_mv → 市值中性化          │
│                                                             │
│  情绪因子 (需补充)                                           │
│  ├── trade_stock_moneyflow → 大单净流入                     │
│  ├── trade_north_holding → 北向持股变化                     │
│  └── trade_margin_trade → 融资余额变化率                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 七、相关文档

| 文档 | 路径 | 说明 |
|-----|------|------|
| 多因子策略方案 | `my/docs/multi_strategy.md` | 因子体系、权重优化、改进路线图 |
| 数据补充计划 | `my/docs/data_supplement_plan.md` | 5张新表设计、字段说明、采集优先级 |
| 环境配置说明 | `my/docs/environment_setup.md` | 环境变量、Tushare配置 |
| 数据中控台设计 | `my/docs/data_hub_design.md` | 架构设计、目录结构、实施计划 |
| 数据体系总结 | `my/docs/summary.md` | 本文档 |

---

## 八、下一步工作

1. **实现数据采集中控台**
   - 创建 `my/data_hub/` 目录结构
   - 实现 Tushare/AKShare 采集器
   - 实现任务调度器

2. **填充历史数据**
   - 行业分类（一次性）
   - 每日指标（回溯1年）
   - 资金流数据（回溯6个月）

3. **更新因子计算**
   - 在 `multi_factor_selector.py` 中集成新数据
   - 实现行业/市值中性化
   - 添加 EP/BP 因子

4. **QMT Agent（可选）**
   - Windows 端 Agent 开发
   - 增量更新日K线数据
