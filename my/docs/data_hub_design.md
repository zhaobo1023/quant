# 统一数据采集中控台设计方案

## 一、现状评估

### 1.1 已有数据情况

| 数据表 | 记录数 | 股票数 | 日期范围 | 数据源 | 状态 |
|-------|--------|-------|---------|-------|------|
| `trade_stock_daily` | 2,713,899 | 5,191 | 2024-01-02 ~ 2026-03-18 | QMT | ✅ 完整 |
| `trade_stock_financial` | 166,397 | 5,154 | 2015-03-31 ~ 2025-12-31 | QMT | ⚠️ 部分字段空 |
| `trade_stock_industry` | 0 | - | - | - | ❌ 空 |
| `trade_stock_daily_basic` | 0 | - | - | - | ❌ 空 |
| `trade_stock_moneyflow` | 0 | - | - | - | ❌ 空 |
| `trade_north_holding` | 0 | - | - | - | ❌ 空 |
| `trade_margin_trade` | 0 | - | - | - | ❌ 空 |

### 1.2 数据重叠分析

**日K线数据 (trade_stock_daily)**
- 来源：QMT（已入库）
- 日期范围：2024-01-02 ~ 2026-03-18（约2.5年）
- 股票覆盖：5,191只
- **结论**：日K线数据完整，无需补充

**财务数据 (trade_stock_financial)**
- 来源：QMT（已入库）
- 字段填充情况：
  - ✅ `eps`: 99.4%
  - ✅ `roe`: 99.6%
  - ✅ `gross_margin`: 98.0%
  - ❌ `revenue`: 0.0%（几乎为空）
  - ❌ `net_profit`: 0.0%（几乎为空）
  - ❌ `debt_ratio`: 0.0%（几乎为空）
  - ❌ `operating_cashflow`: 0.0%（几乎为空）
- **结论**：部分字段缺失，需要从 Tushare/AKShare 补充

### 1.3 数据源特性对比

| 特性 | QMT | Tushare | AKShare |
|-----|-----|---------|---------|
| **运行环境** | Windows + QMT客户端 | 任意（API调用） | 任意（API调用） |
| **数据质量** | 高（券商级） | 高 | 中（东方财富） |
| **更新频率** | 实时 | T+1 | T+1 |
| **权限要求** | QMT账号 | 积分制 | 免费 |
| **数据类型** | 行情+财务 | 全品种 | 全品种 |
| **适用场景** | 实时交易 | 研究+回测 | 研究+回测 |

---

## 二、架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     数据采集中控台 (DataHub)                      │
│                     运行环境: Mac / Linux Server                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  任务调度器  │  │  配置管理器  │  │  状态监控器  │             │
│  │  Scheduler  │  │   Config    │  │   Monitor   │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                     │
│         └────────────────┼────────────────┘                     │
│                          ▼                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    任务队列 (TaskQueue)                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          │                                      │
│         ┌────────────────┼────────────────┐                     │
│         ▼                ▼                ▼                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                │
│  │  Tushare   │  │  AKShare   │  │  QMT Bridge │                │
│  │  Collector │  │  Collector │  │  (远程调用)  │                │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘                │
│        │               │               │                        │
└────────┼───────────────┼───────────────┼────────────────────────┘
         │               │               │
         ▼               ▼               ▼
    ┌─────────────────────────────────────────────┐
    │              MySQL 数据库                    │
    │         (云端 RDS / 本地 MySQL)              │
    └─────────────────────────────────────────────┘
         ▲
         │ (远程调用)
         │
    ┌────┴────┐
    │ Windows │
    │  + QMT  │
    │  Agent  │
    └─────────┘
```

### 2.2 组件说明

| 组件 | 运行环境 | 功能 |
|-----|---------|------|
| **数据中控台** | Mac/Linux | 统一调度、配置管理、状态监控 |
| **Tushare采集器** | Mac/Linux | 通过API采集数据（市值、行业、资金流等） |
| **AKShare采集器** | Mac/Linux | 通过API采集数据（免费替代方案） |
| **QMT Agent** | Windows | 连接QMT采集行情/财务数据，接受中控台调度 |

### 2.3 通信方式

**方案A：HTTP API（推荐）**
- Windows Agent 提供 REST API
- 中控台通过 HTTP 触发采集任务
- 简单可靠，易于调试

**方案B：消息队列**
- 使用 Redis 或 RabbitMQ
- 适合大规模分布式场景
- 配置相对复杂

**方案C：数据库状态表**
- 任务状态写入数据库
- Agent 轮询数据库获取任务
- 最简单，但有延迟

**本项目采用方案A + 方案C组合**：
- HTTP API 用于实时触发
- 数据库状态表用于任务持久化和重试

---

## 三、数据采集任务规划

### 3.1 任务分类

| 优先级 | 任务名 | 数据源 | 运行环境 | 频率 | 依赖 |
|-------|-------|-------|---------|------|-----|
| P0 | 行业分类 | Tushare/AKShare | Mac/Linux | 一次性 | - |
| P0 | 每日指标(市值/PE) | Tushare | Mac/Linux | 每日 | - |
| P1 | 日K线增量 | QMT | Windows | 每日 | - |
| P1 | 财务数据补充 | Tushare | Mac/Linux | 季度 | - |
| P2 | 资金流向 | Tushare/AKShare | Mac/Linux | 每日 | - |
| P2 | 北向持股 | Tushare/AKShare | Mac/Linux | 每日 | - |
| P3 | 融资融券 | Tushare/AKShare | Mac/Linux | 每日 | - |
| P3 | 宏观指标 | AKShare | Mac/Linux | 月度 | - |

### 3.2 任务依赖图

```
                    ┌─────────────┐
                    │  行业分类    │ (一次性)
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
  ┌────────────┐   ┌────────────┐   ┌────────────┐
  │ 每日指标    │   │  日K线     │   │ 财务补充   │
  │ (市值/PE)  │   │  (QMT)    │   │ (Tushare) │
  └─────┬──────┘   └─────┬──────┘   └─────┬──────┘
        │                │                │
        └────────────────┼────────────────┘
                         ▼
                  ┌────────────┐
                  │  多因子计算 │
                  └────────────┘
```

---

## 四、目录结构设计

```
/Users/wenwen/data0/person/quant/
├── .env                          # 环境变量配置
├── db_config.py                  # 数据库配置
├── src/
│   └── models.py                 # 表结构定义
│
├── my/
│   ├── docs/                     # 文档
│   │   ├── data_supplement_plan.md
│   │   ├── environment_setup.md
│   │   └── data_hub_design.md    # 本文档
│   │
│   ├── data_hub/                 # 数据采集中控台
│   │   ├── __init__.py
│   │   ├── config.py             # 采集配置
│   │   ├── scheduler.py          # 任务调度器
│   │   ├── monitor.py            # 状态监控
│   │   ├── api.py                # HTTP API (Flask)
│   │   │
│   │   ├── collectors/           # 数据采集器
│   │   │   ├── __init__.py
│   │   │   ├── base.py           # 基类
│   │   │   ├── tushare_collector.py
│   │   │   ├── akshare_collector.py
│   │   │   └── qmt_bridge.py     # QMT远程调用桥
│   │   │
│   │   ├── tasks/                # 具体采集任务
│   │   │   ├── __init__.py
│   │   │   ├── task_industry.py      # 行业分类
│   │   │   ├── task_daily_basic.py   # 每日指标
│   │   │   ├── task_moneyflow.py     # 资金流向
│   │   │   ├── task_north_holding.py # 北向持股
│   │   │   └── task_margin.py        # 融资融券
│   │   │
│   │   └── agent/                # Windows QMT Agent
│   │       ├── qmt_agent.py      # Agent主程序
│   │       ├── qmt_tasks.py      # QMT采集任务
│   │       └── run_agent.bat     # 启动脚本
│   │
│   └── run_data_hub.py           # 中控台启动入口
│
└── outputs/                      # 输出文件
```

---

## 五、核心模块设计

### 5.1 采集配置 (config.py)

```python
# 数据采集任务配置
TASK_CONFIG = {
    'industry': {
        'name': '行业分类',
        'source': 'tushare',
        'schedule': None,  # 一次性任务
        'priority': 0,
        'table': 'trade_stock_industry',
    },
    'daily_basic': {
        'name': '每日指标',
        'source': 'tushare',
        'schedule': '0 18 * * *',  # 每天18:00
        'priority': 1,
        'table': 'trade_stock_daily_basic',
    },
    'daily_kline': {
        'name': '日K线',
        'source': 'qmt',
        'schedule': '0 17 * * *',  # 每天17:00
        'priority': 1,
        'table': 'trade_stock_daily',
        'agent': 'windows-qmt',  # 需要Windows Agent
    },
    # ...
}

# 数据源配置
SOURCE_CONFIG = {
    'tushare': {
        'token_env': 'TUSHARE_TOKEN',
        'rate_limit': 200,  # 每分钟请求限制
    },
    'akshare': {
        'rate_limit': 100,
    },
    'qmt': {
        'agent_url': 'http://windows-host:8080',
    }
}
```

### 5.2 采集器基类 (base.py)

```python
class BaseCollector:
    """数据采集器基类"""

    def __init__(self, config):
        self.config = config
        self.db = get_db_connection()

    def collect(self, **params):
        """执行采集，子类实现"""
        raise NotImplementedError

    def save_to_db(self, df, table, conflict='update'):
        """保存数据到数据库"""
        pass

    def get_last_date(self, table, stock_code=None):
        """获取最后更新日期"""
        pass
```

### 5.3 QMT Agent (agent/qmt_agent.py)

```python
"""
运行在 Windows 机器上的 QMT Agent
提供 HTTP API 接收采集任务
"""
from flask import Flask, request, jsonify
from xtquant import xtdata

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/collect/daily', methods=['POST'])
def collect_daily():
    """采集日K线数据"""
    data = request.json
    stock_codes = data.get('stocks', [])
    start_date = data.get('start_date')

    # 下载并获取数据
    results = []
    for code in stock_codes:
        xtdata.download_history_data(code, '1d', start_date)
        # ... 处理数据

    return jsonify({'success': True, 'count': len(results)})

@app.route('/collect/financial', methods=['POST'])
def collect_financial():
    """采集财务数据"""
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### 5.4 中控台调度器 (scheduler.py)

```python
class DataScheduler:
    """数据采集调度器"""

    def __init__(self):
        self.tasks = {}  # 任务注册表
        self.running = False

    def register_task(self, name, task_class, config):
        """注册采集任务"""
        self.tasks[name] = {
            'class': task_class,
            'config': config,
            'last_run': None,
            'status': 'idle'
        }

    def run_task(self, name, **params):
        """执行单个任务"""
        task_info = self.tasks[name]
        task = task_info['class'](task_info['config'])
        return task.run(**params)

    def run_scheduled(self):
        """运行定时任务"""
        for name, info in self.tasks.items():
            if self._should_run(info):
                self.run_task(name)

    def run_all(self):
        """手动运行所有任务"""
        for name in self.tasks:
            self.run_task(name)
```

---

## 六、实施计划

### 第一阶段：基础框架（1-2天）

1. 创建目录结构
2. 实现配置管理模块
3. 实现采集器基类
4. 实现 Tushare/AKShare 采集器

### 第二阶段：核心任务（2-3天）

1. 实现行业分类采集任务
2. 实现每日指标采集任务
3. 填充历史数据
4. 验证数据质量

### 第三阶段：QMT集成（1-2天）

1. 开发 Windows QMT Agent
2. 实现中控台与Agent通信
3. 配置增量更新任务

### 第四阶段：监控优化（1天）

1. 添加任务状态监控
2. 添加错误告警
3. 优化采集性能

---

## 七、使用示例

### 7.1 手动触发采集

```bash
# 采集行业分类
python my/run_data_hub.py --task industry

# 采集每日指标（最近30天）
python my/run_data_hub.py --task daily_basic --days 30

# 采集全部数据
python my/run_data_hub.py --all
```

### 7.2 启动定时调度

```bash
# 启动中控台服务
python my/run_data_hub.py --daemon

# 启动API服务
python my/run_data_hub.py --api --port 5000
```

### 7.3 Windows Agent

```batch
:: 在 Windows 机器上运行
cd my\data_hub\agent
python qmt_agent.py --port 8080
```

---

## 八、注意事项

### 8.1 数据源权限

- Tushare 资金流数据需要 2000+ 积分
- 积分不足时可使用 AKShare 替代
- QMT 需要有效的 QMT 账号

### 8.2 网络配置

- Windows Agent 需要能访问 MySQL 数据库
- 如使用云数据库，需配置安全组白名单
- 中控台需要能访问 Windows Agent 的 HTTP 端口

### 8.3 数据一致性

- 采集任务使用 `UPSERT` 策略（存在则更新，不存在则插入）
- 每个表都有 `(stock_code, date)` 唯一索引
- 支持增量更新和全量覆盖

---

## 九、扩展性

### 9.1 添加新数据源

1. 在 `collectors/` 下创建新的采集器类
2. 继承 `BaseCollector`
3. 在 `config.py` 中添加配置

### 9.2 添加新任务

1. 在 `tasks/` 下创建任务文件
2. 实现采集逻辑
3. 在调度器中注册任务

### 9.3 多机器部署

- 中控台可部署在 Linux 服务器
- 多个 Agent 可分布式部署
- 通过数据库实现任务协调
