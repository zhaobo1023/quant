# Backtrader 回测系统

基于 Backtrader 框架的量化策略回测系统，支持从 MySQL 加载数据、多策略回测、绩效分析和可视化。

## 目录结构

```
CASE-Backtrader回测/
├── db_config.py           # 数据库配置与回测参数
├── data_loader.py         # 数据加载、策略包装、绩效计算、可视化
├── 1-双均线策略.py         # 趋势跟踪入门
├── 2-MACD策略.py          # 趋势跟踪
├── 3-RSI策略.py           # 超买超卖
├── 4-布林带策略.py         # 波动率
├── 5-乖离率策略.py         # 均值回归
├── 6-动量策略.py           # 动量因子
├── 7-自定义策略.py         # 插件机制演示
├── strategies/            # 自定义策略目录
│   └── macd_divergence.py # MACD底背离策略示例
├── outputs/               # 回测图表输出
│   ├── MACD策略.png
│   ├── RSI策略.png
│   └── ...
└── .env                   # 配置文件（需创建）
```

## 环境配置

### 依赖安装

```bash
pip install backtrader pandas numpy pymysql python-dotenv matplotlib
```

### .env 配置文件

```ini
# 数据库配置
WUCAI_SQL_HOST=localhost
WUCAI_SQL_PORT=3306
WUCAI_SQL_USERNAME=root
WUCAI_SQL_PASSWORD=123456
WUCAI_SQL_DB=quant_trade

# 回测参数
BACKTEST_INITIAL_CASH=1000000
BACKTEST_COMMISSION=0.0002
BACKTEST_POSITION_PCT=95
```

### 数据要求

需要 MySQL 中存在 `trade_stock_daily` 表，包含以下字段：
- `stock_code` - 股票代码
- `trade_date` - 交易日期
- `open_price`, `high_price`, `low_price`, `close_price` - OHLC
- `volume` - 成交量

## 策略列表

| 编号 | 策略名称 | 类别 | 核心逻辑 |
|-----|---------|------|---------|
| 1 | 双均线 | 趋势跟踪 | 快线(10日)上穿慢线(30日)买入，下穿卖出 |
| 2 | MACD | 趋势跟踪 | DIF上穿DEA(金叉)买入，下穿(死叉)卖出 |
| 3 | RSI | 超买超卖 | RSI < 30(超卖)买入，RSI > 70(超买)卖出 |
| 4 | 布林带 | 波动率 | 价格触及下轨买入，触及上轨卖出 |
| 5 | 乖离率 | 均值回归 | 乖离率 < -6%买入，> 6%卖出 |
| 6 | 动量 | 动量因子 | 20日涨幅 > 5%买入，跌幅 > 5%卖出 |
| 7 | 自定义 | 插件 | 动态加载 strategies/ 目录下的策略 |

## 快速开始

### 运行单个策略

```bash
cd example/CASE-Backtrader回测
python 2-MACD策略.py
```

### 输出示例

```
MACD策略 | 600519.SH | 2025-01-02 ~ 2025-12-31 | 242个交易日
  总收益: +15.32% | 年化: +15.32% | 最大回撤: 8.45% | 夏普: 1.23 | 卡玛: 1.81
  交易: 12次 | 胜率: 58.3% | 盈亏比: 2.15 | 利润因子: 2.89 | 最大连亏: 2次
  图表已保存: outputs/MACD策略.png
```

## 核心模块说明

### db_config.py

- `DB_CONFIG`: 数据库连接配置
- `INITIAL_CASH`: 初始资金（默认100万）
- `COMMISSION`: 手续费率（默认万分之二）
- `POSITION_PCT`: 仓位比例（默认95%）
- `get_connection()`: 获取数据库连接
- `execute_query()`: 执行SQL查询

### data_loader.py

#### 数据加载
```python
from data_loader import load_stock_data

df = load_stock_data('600519.SH', '2025-01-01', '2025-12-31')
# 返回 DataFrame，索引为日期，列为 open/high/low/close/volume
```

#### 一键回测
```python
from data_loader import run_and_report

result = run_and_report(
    MACDStrategy,           # 策略类
    '600519.SH',            # 股票代码
    '2025-01-01',           # 开始日期
    '2025-12-31',           # 结束日期
    label='MACD策略',        # 显示名称
    plot=True               # 是否生成图表
)
```

#### 绩效指标

| 指标 | 说明 |
|-----|------|
| `total_return` | 总收益率 |
| `annual_return` | 年化收益率 |
| `max_drawdown` | 最大回撤 |
| `sharpe_ratio` | 夏普比率 |
| `calmar_ratio` | 卡玛比率（年化收益/最大回撤） |
| `win_rate` | 胜率 |
| `profit_loss_ratio` | 盈亏比（平均盈利/平均亏损） |
| `profit_factor` | 利润因子（总盈利/总亏损） |
| `max_consecutive_losses` | 最大连续亏损次数 |

#### 可视化图表

`plot_backtest()` 生成三合一图表：
1. **上图**: K线（收盘价）+ 买卖点标记
2. **中图**: 策略净值 vs 买入持有基准
3. **下图**: 回撤曲线

## 自定义策略开发

### 方式一：直接编写策略文件

参考 `1-双均线策略.py` 的结构：

```python
import backtrader as bt
from data_loader import run_and_report

class MyStrategy(bt.Strategy):
    params = (('period', 20),)  # 策略参数

    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=self.p.period)

    def next(self):
        if not self.position:
            if self.data.close[0] > self.sma[0]:
                self.buy()
        else:
            if self.data.close[0] < self.sma[0]:
                self.close()

if __name__ == '__main__':
    run_and_report(MyStrategy, '600519.SH', '2025-01-01', '2025-12-31',
                  label='我的策略', plot=True)
```

### 方式二：插件机制（推荐）

在 `strategies/` 目录下创建策略文件：

```python
# strategies/my_strategy.py
import backtrader as bt

# 必须定义：策略元信息
STRATEGY_META = {
    'name': '策略中文名',
    'category': 'custom',
    'desc': '策略描述',
    'params': {'period': 20},
    'logic': '买入条件 -> 买入; 卖出条件 -> 卖出',
}

# 必须定义：Strategy 类
class Strategy(bt.Strategy):
    params = (('period', 20),)

    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=self.p.period)

    def next(self):
        if not self.position:
            if self.data.close[0] > self.sma[0]:
                self.buy()
        else:
            if self.data.close[0] < self.sma[0]:
                self.close()
```

运行 `python 7-自定义策略.py` 会自动加载并回测所有策略。

## Backtrader 核心概念

### Cerebro 引擎

```python
cerebro = bt.Cerebro()           # 创建引擎
cerebro.addstrategy(MyStrategy)  # 添加策略
cerebro.adddata(data)            # 添加数据
cerebro.broker.setcash(1000000)  # 设置初始资金
cerebro.run()                    # 运行回测
```

### 常用指标

```python
# 均线
sma = bt.indicators.SMA(self.data.close, period=20)
ema = bt.indicators.EMA(self.data.close, period=20)

# MACD
macd = bt.indicators.MACD(self.data.close, period_me1=12, period_me2=26, period_signal=9)

# RSI
rsi = bt.indicators.RSI(self.data.close, period=14)

# 布林带
boll = bt.indicators.BollingerBands(self.data.close, period=20, devfactor=2.0)

# 交叉信号
crossover = bt.indicators.CrossOver(fast_line, slow_line)
# > 0 表示上穿，< 0 表示下穿
```

### 交易方法

```python
self.buy()      # 开多仓
self.sell()     # 开空仓
self.close()    # 平仓
self.order_target_percent(target=0.95)  # 调仓到目标比例
```

## 注意事项

1. **数据准备**: 运行前确保 MySQL 中已有对应的股票日线数据
2. **中文字体**: 图表显示中文需要系统安装 SimHei 字体
3. **仓位管理**: 默认使用95%仓位，留5%应对手续费滑点
4. **手续费**: 默认万分之二，可在 .env 中调整

## 扩展阅读

- [Backtrader 官方文档](https://www.backtrader.com/docu/)
- [Backtrader 中文教程](https://www.backtrader.com.cn/)
