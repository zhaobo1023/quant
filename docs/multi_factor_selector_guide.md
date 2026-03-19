# 多因子选股器使用指南

## 概述

多因子选股器是一个基于 Streamlit 的可视化工具，支持自定义因子权重、策略模板、因子存储和增量更新。

## 快速开始

### 启动选股器

```bash
cd /Users/wenwen/data0/person/quant
streamlit run my/multi_factor_selector.py
```

访问地址: http://localhost:8501

### 重新计算因子（每周一次）

```bash
python my/quick_save_factors.py
```

---

## 功能模块

### 1. 因子配置

支持8个技术因子，可自定义权重：

| 因子 | 说明 | 方向 | 默认权重 |
|------|------|------|----------|
| momentum_20d | 20日动量 ROC(20) | 正向 | 20% |
| momentum_60d | 60日动量 ROC(60) | 正向 | 15% |
| volatility | 波动率 ATR/Close | 反向 | 15% |
| rsi_14 | RSI(14) | 反向 | 10% |
| adx_14 | ADX(14) 趋势强度 | 正向 | 10% |
| turnover_ratio | 换手率 | 正向 | 10% |
| price_position | 价格位置 (60日区间) | 反向 | 10% |
| macd_signal | MACD柱状图 | 正向 | 10% |

### 2. 预设策略模板

| 模板 | 说明 | 特点 |
|------|------|------|
| 均衡策略 | 各因子均衡配置 | 稳健投资 |
| 动量优先 | 侧重价格趋势 | 追涨杀跌 |
| 价值挖掘 | 寻找超卖反弹 | 逆向投资 |
| 趋势跟踪 | ADX权重高 | 强趋势股票 |
| 低波动 | 波动率权重高 | 风险控制 |

### 3. 因子数据管理

- 从数据库加载已有因子
- 保存计算结果到数据库
- 支持增量更新

---

## 数据库设计

### 因子表结构 (trade_stock_factor)

```sql
CREATE TABLE trade_stock_factor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',
    calc_date DATE NOT NULL COMMENT '计算日期(数据截止日期)',

    -- 技术因子
    momentum_20d DOUBLE COMMENT '20日动量 ROC(20)',
    momentum_60d DOUBLE COMMENT '60日动量 ROC(60)',
    volatility DOUBLE COMMENT '波动率 ATR(14)/Close',
    rsi_14 DOUBLE COMMENT 'RSI(14)',
    adx_14 DOUBLE COMMENT 'ADX(14) 趋势强度',
    turnover_ratio DOUBLE COMMENT '换手率 当日量/20日均量',
    price_position DOUBLE COMMENT '价格位置 60日区间内位置',
    macd_signal DOUBLE COMMENT 'MACD柱状图',

    -- 辅助字段
    close DOUBLE COMMENT '收盘价',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uk_code_date (calc_date, stock_code),
    KEY idx_calc_date (calc_date),
    KEY idx_stock_code (stock_code)
);
```

### 数据更新策略

- **增量更新**: 每天每只股票一条记录
- **唯一约束**: (calc_date, stock_code)
- **更新频率**: 建议每周重新计算一次

---

## 使用流程

### 首次使用

```
1. 计算因子 → 保存到数据库
2. 调整权重 → 重新打分（秒级）
3. 查看结果 → 导出数据
```

### 日常使用

```
1. 从数据库加载已有因子
2. 调整权重 → 重新打分
3. 每周一次：重新计算因子并保存
```

---

## 文件结构

```
quant/
├── my/
│   ├── multi_factor_selector.py   # Streamlit选股器
│   ├── factor_storage.py          # 因子存储模块
│   ├── test_factor_storage.py     # 单元测试
│   ├── save_factors_to_db.py      # 因子入库脚本
│   └── quick_save_factors.py      # 简化版入库
├── db_config.py                   # 数据库配置
├── data_loader.py                 # 数据加载模块
└── docs/
    └── multi_factor_selector_guide.md
```

---

## API 参考

### factor_storage.py

```python
# 创建因子表
create_factor_table()

# 保存因子
save_factors(factor_df, calc_date)
batch_save_factors(factor_df, calc_date, batch_size=500)

# 加载因子
load_factors(calc_date, stock_codes=None)
load_factors_range(start_date, end_date, stock_code=None)

# 元数据查询
get_latest_factor_date()
get_factor_dates()
delete_factors_by_date(calc_date)
```

### data_loader.py

```python
# 加载股票数据
load_stock_data(stock_code, start_date, end_date)

# 运行回测
run_and_report(strategy_class, stock_code, ...)

# 计算买入持有收益
calc_buy_and_hold(stock_code, start_date, end_date)
```

---

## 测试

### 运行单元测试

```bash
python my/test_factor_storage.py
```

### 测试覆盖

- 保存/加载因子
- 更新因子 (同一日期重复保存)
- 批量保存
- 数据完整性验证
- 删除因子
- 因子计算逻辑
- 打分逻辑

---

## 性能

| 操作 | 耗时 | 说明 |
|------|------|------|
| 计算因子 | 30秒-2分钟 | 加载数据 + TA-Lib计算 |
| 重新打分 | <1秒 | 仅重新加权排名 |
| 从数据库加载 | <1秒 | 直接读取已计算因子 |

---

## 注意事项

1. **权重总和必须为1.0** - 否则打分结果不准确
2. **因子数据定期更新** - 建议每周重新计算
3. **数据库连接** - 确保 .env 配置正确
4. **缓存机制** - Streamlit 自动缓存因子数据

---

## 更新日志

### v1.0.0 (2026-03-19)

- 初始版本发布
- 8个技术因子支持
- 5种预设策略模板
- 因子存储与增量更新
- Streamlit 可视化界面
- 完整单元测试覆盖
