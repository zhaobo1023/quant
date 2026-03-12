# 个人持仓管理系统设计文档

**日期**: 2026-03-12
**方案**: Web应用 + 定时任务 (方案B)
**预计开发周期**: 3周

---

## 一、项目背景

### 现有基础
- 日线数据(含成交量)已通过QMT采集到MySQL
- 财务数据已采集
- Backtrader回测框架已集成
- MySQL数据库(7张核心表)
- FastAPI后端 + React前端(未完善)

### 核心需求
1. **持仓管理** - 支持券商APP截图OCR识别 + 手动输入/修改
2. **数据补充** - 技术指标数据、新闻舆情、研报评级等另类数据
3. **技术分析** - 自动检测放量、均线突破/跌破、趋势反转等信号
4. **简报推送** - 每日20:00通过飞书Webhook推送持仓分析简报
5. **选股功能** - 根据技术面/基本面条件筛选股票

---

## 二、系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      用户交互层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Web前端      │  │  飞书推送     │  │  命令行工具   │      │
│  │  (React)     │  │  (Webhook)   │  │  (CLI可选)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      应用服务层                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FastAPI 后端 (web/api/main.py)                      │  │
│  │  - 持仓管理 API                                       │  │
│  │  - 技术分析 API                                       │  │
│  │  - 选股 API                                          │  │
│  │  - 文件上传 API (OCR截图)                            │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  定时任务服务 (APScheduler)                          │  │
│  │  - 每日20:00 技术分析扫描                            │  │
│  │  - 每日数据更新 (可选)                               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      业务逻辑层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 持仓管理服务  │  │ 技术分析服务  │  │ 选股服务     │      │
│  │ PositionSvc  │  │ AnalysisSvc  │  │ ScreenerSvc  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ OCR识别服务   │  │ 推送服务      │                        │
│  │ OcrSvc       │  │ NotifySvc    │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      数据访问层                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  MySQL 数据库 (wucai_trade)                          │  │
│  │  - trade_stock_daily (日K线)                         │  │
│  │  - trade_stock_financial (财务数据)                  │  │
│  │  - model_trade_position (持仓管理)                   │  │
│  │  - trade_stock_news (新闻舆情)                       │  │
│  │  - trade_technical_indicator (技术指标) ← 新增       │  │
│  │  - trade_analysis_report (分析报告) ← 新增           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      外部服务层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 数据源        │  │ OCR服务       │  │ 推送服务     │      │
│  │ QMT/Tushare  │  │ 百度/腾讯云   │  │ 飞书Webhook  │      │
│  │ AkShare      │  │              │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

**后端:**
- FastAPI (已有)
- APScheduler (定时任务调度)
- 百度OCR API / 腾讯云OCR (截图识别)
- TA-Lib / pandas-ta (技术指标计算)

**前端:**
- React + Ant Design
- 图片上传组件
- ECharts / Recharts (图表可视化)

**数据存储:**
- MySQL 8.0 (主数据库)
- Redis (可选,缓存技术指标)

**推送:**
- 飞书 Webhook (自定义机器人)

---

## 三、数据库设计

### 3.1 新增表结构

#### 1. 技术指标表 (trade_technical_indicator)

```sql
CREATE TABLE IF NOT EXISTS trade_technical_indicator (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',
    trade_date DATE NOT NULL COMMENT '交易日期',

    -- 均线系统
    ma5 DECIMAL(10,2) COMMENT '5日均线',
    ma10 DECIMAL(10,2) COMMENT '10日均线',
    ma20 DECIMAL(10,2) COMMENT '20日均线(月线)',
    ma60 DECIMAL(10,2) COMMENT '60日均线(季线)',
    ma120 DECIMAL(10,2) COMMENT '120日均线(半年线)',
    ma250 DECIMAL(10,2) COMMENT '250日均线(年线)',

    -- MACD指标
    macd_dif DECIMAL(10,4) COMMENT 'MACD DIF',
    macd_dea DECIMAL(10,4) COMMENT 'MACD DEA',
    macd_histogram DECIMAL(10,4) COMMENT 'MACD柱',

    -- RSI指标
    rsi_6 DECIMAL(10,4) COMMENT 'RSI 6日',
    rsi_12 DECIMAL(10,4) COMMENT 'RSI 12日',
    rsi_24 DECIMAL(10,4) COMMENT 'RSI 24日',

    -- 布林带
    boll_upper DECIMAL(10,2) COMMENT '布林上轨',
    boll_middle DECIMAL(10,2) COMMENT '布林中轨',
    boll_lower DECIMAL(10,2) COMMENT '布林下轨',

    -- 成交量相关
    volume_ma5 BIGINT COMMENT '5日均量',
    volume_ma10 BIGINT COMMENT '10日均量',
    volume_ratio DECIMAL(10,4) COMMENT '量比',

    -- KDJ指标
    kdj_k DECIMAL(10,4) COMMENT 'KDJ K值',
    kdj_d DECIMAL(10,4) COMMENT 'KDJ D值',
    kdj_j DECIMAL(10,4) COMMENT 'KDJ J值',

    -- ATR (波动率)
    atr_14 DECIMAL(10,4) COMMENT 'ATR 14日',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_code_date (stock_code, trade_date),
    INDEX idx_trade_date (trade_date),
    INDEX idx_stock_code (stock_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='技术指标数据';
```

#### 2. 分析报告表 (trade_analysis_report)

```sql
CREATE TABLE IF NOT EXISTS trade_analysis_report (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    report_date DATE NOT NULL COMMENT '报告日期',
    report_type VARCHAR(20) NOT NULL COMMENT '报告类型: daily/weekly/manual',
    stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',

    -- 信号类型
    signal_type VARCHAR(50) COMMENT '信号类型: breakout/breakdown/volume_surge/trend_reversal等',
    signal_strength TINYINT COMMENT '信号强度 1-5',

    -- 信号描述
    title VARCHAR(200) NOT NULL COMMENT '信号标题',
    description TEXT COMMENT '详细描述',

    -- 相关指标值
    price DECIMAL(10,2) COMMENT '当时价格',
    volume BIGINT COMMENT '成交量',
    ma_status VARCHAR(100) COMMENT '均线状态 JSON',

    -- 推送状态
    is_pushed TINYINT DEFAULT 0 COMMENT '是否已推送',
    pushed_at TIMESTAMP NULL COMMENT '推送时间',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_report_date (report_date),
    INDEX idx_stock_code (stock_code),
    INDEX idx_signal_type (signal_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='技术分析报告';
```

#### 3. OCR识别记录表 (trade_ocr_record)

```sql
CREATE TABLE IF NOT EXISTS trade_ocr_record (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT COMMENT '用户ID(预留)',
    image_path VARCHAR(500) COMMENT '图片存储路径',
    ocr_result TEXT COMMENT 'OCR识别原始结果 JSON',
    parsed_positions TEXT COMMENT '解析后的持仓列表 JSON',
    status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending/success/failed',
    error_message TEXT COMMENT '错误信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='OCR识别记录';
```

---

## 四、核心模块设计

### 4.1 数据采集模块

#### 技术指标计算服务 (src/services/indicator_service.py)

**职责:**
- 从MySQL读取日K线数据
- 使用TA-Lib计算技术指标
- 批量写入trade_technical_indicator表

**核心指标:**
- 均线系统: MA5/10/20/60/120/250
- MACD: DIF, DEA, MACD柱
- RSI: 6/12/24日
- 布林带: 上轨/中轨/下轨
- KDJ: K/D/J值
- 成交量指标: 均量、量比
- 波动率: ATR

**调度:**
- 每日收盘后自动计算(通过APScheduler)
- 支持手动触发重新计算

#### 新闻舆情采集 (src/services/news_service.py)

**数据源:**
- AkShare: 新闻数据接口
- 东方财富: 新闻API
- Tushare: 新闻接口(如果有)

**字段:**
- 股票代码、标题、内容、来源、发布时间
- 情感分析(可选,后续用大模型)

### 4.2 持仓管理模块

#### OCR识别服务 (src/services/ocr_service.py)

**流程:**
1. 接收上传的券商APP截图
2. 调用百度OCR API进行通用文字识别
3. 解析识别结果,提取股票代码、持仓数量、成本价
4. 返回结构化数据供前端确认/编辑

**支持的券商格式:**
- 优先支持主流券商(华泰、中信、招商等)
- 识别失败时返回原始OCR文本,供用户手动修正

#### 持仓管理API (web/api/positions.py)

**接口:**
- `POST /api/positions/upload` - 上传截图并OCR识别
- `POST /api/positions` - 创建持仓(OCR后确认或手动输入)
- `GET /api/positions` - 获取持仓列表
- `PUT /api/positions/{id}` - 更新持仓
- `DELETE /api/positions/{id}` - 删除持仓

### 4.3 技术分析模块

#### 分析引擎 (src/services/analysis_service.py)

**核心信号检测:**

1. **均线突破信号**
   - 放量站上20日均线(成交量 > 5日均量 × 1.5)
   - 放量站上60日均线
   - 跌破20日均线(需止损)
   - 跌破60日均线(趋势走坏)

2. **趋势反转信号**
   - MACD金叉/死叉
   - RSI超买(>70)/超卖(<30)
   - KDJ金叉/死叉

3. **异常波动信号**
   - 放量大涨(涨幅>5%, 量比>2)
   - 放量下跌(跌幅>5%, 量比>2)
   - 突破布林上轨
   - 跌破布林下轨

4. **持仓相关信号**
   - 价格接近成本价±5%(预警)
   - 价格跌破成本价-10%(止损提醒)

**分析流程:**
```python
def analyze_position(stock_code, position_cost_price):
    # 1. 获取最新K线数据 + 技术指标
    # 2. 检测各类信号
    # 3. 生成信号描述(自然语言)
    # 4. 写入trade_analysis_report表
    # 5. 返回信号列表
```

### 4.4 推送模块

#### 飞书推送服务 (src/services/notify_service.py)

**推送格式:**
```json
{
  "msg_type": "interactive",
  "card": {
    "header": {
      "title": { "tag": "plain_text", "content": "持仓分析简报 - 2026-03-12" },
      "template": "blue"
    },
    "elements": [
      {
        "tag": "div",
        "text": { "tag": "lark_md", "content": "**云天化(600096)**\n当前价: 25.30 | 持仓成本: 22.50 | 盈亏: +12.44%" }
      },
      {
        "tag": "div",
        "text": { "tag": "lark_md", "content": "🔴 **信号**: 放量站上20日均线\n📈 **详情**: 今日放量上涨3.5%,成交量达5日均量的2.1倍,成功站上20日线(24.80)" }
      }
    ]
  }
}
```

**调度:**
- APScheduler定时任务: 每日20:00触发
- 扫描所有持仓股票,生成分析报告
- 推送到飞书群机器人

### 4.5 选股模块

#### 选股服务 (src/services/screener_service.py)

**预设筛选条件:**

1. **技术面突破**
   - 突破20日均线
   - MACD金叉
   - RSI从超卖回升

2. **基本面优质**
   - ROE > 15%
   - 净利润增长率 > 20%
   - 负债率 < 60%

3. **量价配合**
   - 放量上涨
   - 量比 > 1.5
   - 涨幅 3-7%

**API:**
- `POST /api/screener/scan` - 执行选股(可自定义条件)
- `GET /api/screener/presets` - 获取预设筛选模板

---

## 五、前端界面设计

### 5.1 持仓管理页面

**功能:**
- 持仓列表(表格展示: 股票代码、名称、持仓数、成本价、现价、盈亏%)
- 上传截图按钮(拖拽上传)
- OCR识别结果预览(可编辑)
- 手动添加/编辑持仓

**布局:**
```
┌─────────────────────────────────────────────────────────┐
│  持仓管理                                    [上传截图]  │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐   │
│  │  股票代码 | 名称 | 持仓数 | 成本价 | 现价 | 盈亏  │   │
│  │  600096.SH | 云天化 | 1000 | 22.50 | 25.30 | +12.4% │   │
│  │  300274.SZ | 阳光电源 | 500 | 65.00 | 68.20 | +4.9% │   │
│  └─────────────────────────────────────────────────┘   │
│  [OCR识别记录]  [手动添加]                              │
└─────────────────────────────────────────────────────────┘
```

### 5.2 技术分析简报页面

**功能:**
- 日期选择器(查看历史简报)
- 按股票分组的信号列表
- 信号详情(包含相关指标值)
- 手动触发扫描按钮

### 5.3 选股工具页面

**功能:**
- 预设筛选模板选择
- 自定义条件构建器
- 筛选结果列表
- 导出Excel功能

---

## 六、实施计划

### Week 1: 数据层 + 持仓管理

**Day 1-2: 数据库与数据补充**
- 创建新表(trade_technical_indicator, trade_analysis_report, trade_ocr_record)
- 实现技术指标计算服务(indicator_service.py)
- 批量计算历史数据的技术指标

**Day 3-4: 持仓管理后端**
- OCR服务集成(百度API)
- 持仓管理API完善(upload, CRUD)
- 飞书推送服务(notify_service.py)

**Day 5: 持仓管理前端**
- 持仓列表页面
- 图片上传组件
- OCR结果编辑界面

### Week 2: 技术分析 + 定时推送

**Day 1-2: 技术分析引擎**
- 实现信号检测逻辑(analysis_service.py)
- 生成自然语言描述
- 写入分析报告表

**Day 3: 定时任务**
- APScheduler集成
- 每日20:00推送任务
- 手动触发API

**Day 4-5: 前端界面**
- 技术分析简报页面
- 信号可视化展示
- 历史报告查询

### Week 3: 选股功能 + 优化

**Day 1-2: 选股服务**
- 实现筛选逻辑(screener_service.py)
- 预设模板定义
- 选股API

**Day 3-4: 选股前端**
- 选股工具页面
- 条件构建器
- 结果展示

**Day 5: 测试与优化**
- 端到端测试
- 性能优化
- 文档完善

---

## 七、扩展性设计

### 7.1 数据源扩展
- 新增数据源只需实现统一接口(DataProvider)
- 支持插件式接入

### 7.2 技术指标扩展
- 指标计算采用策略模式
- 新增指标只需实现IndicatorCalculator接口

### 7.3 推送渠道扩展
- 推送服务采用工厂模式
- 支持邮件、微信、钉钉等渠道扩展

### 7.4 选股条件扩展
- 选股条件可配置化
- 支持DSL表达式自定义

---

## 八、风险与挑战

### 8.1 OCR识别准确率
- **风险**: 不同券商APP界面差异大,OCR识别可能失败
- **应对**:
  - 优先支持主流券商
  - 识别失败时提供手动编辑
  - 记录OCR结果供后续优化

### 8.2 技术分析误报
- **风险**: 技术指标信号可能产生大量误报
- **应对**:
  - 信号强度分级(1-5级)
  - 多指标交叉验证
  - 用户反馈机制(标记有用/无用信号)

### 8.3 数据更新及时性
- **风险**: 日线数据更新延迟影响分析准确性
- **应对**:
  - 设置合理推送时间(20:00,留出数据更新时间)
  - 数据源健康检查
  - 异常告警机制

---

## 九、成功指标

### 功能完整性
- ✅ 持仓管理: 支持OCR上传、手动编辑
- ✅ 技术分析: 覆盖10+种技术信号
- ✅ 定时推送: 每日20:00准时推送
- ✅ 选股功能: 支持3+预设模板

### 性能指标
- OCR识别准确率 > 80%
- 技术分析扫描时间 < 30秒(100只股票)
- 推送成功率 > 95%

### 用户体验
- 持仓录入时间 < 2分钟(含OCR确认)
- 简报可读性良好(自然语言描述清晰)
- 界面响应速度 < 1秒

---

## 十、后续迭代方向

### Phase 2 (1-2个月后)
- AI增强: 大模型分析新闻情感、生成投资建议
- 策略回测: 集成到Web界面,支持在线回测
- 风险管理: 组合风险分析、VaR计算

### Phase 3 (3-6个月后)
- 实盘交易: 接入券商API,实现自动下单
- 多账户: 支持多个券商账户管理
- 协作功能: 团队共享持仓、讨论区

---

**文档版本**: v1.0
**最后更新**: 2026-03-12
**下一步**: 调用 writing-plans 技能生成详细实施计划
