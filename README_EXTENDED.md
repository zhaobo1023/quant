# 个人持仓管理系统

## 项目概述

这是一个基于FastAPI和React的个人持仓管理系统，支持技术分析、OCR识别、定时推送、选股等功能。

## 技术栈

- **后端**: Python 3.9+, FastAPI, SQLAlchemy, APScheduler
- **前端**: React, TypeScript, Ant Design, Tailwind CSS
- **数据库**: MySQL 8.0
- **第三方服务**: 百度OCR API, 飞书Webhook, Tushare

## 功能特性

### 1. 持仓管理
- 持仓信息的增删改查
- 多账户支持
- 融资标记
- 持仓状态跟踪

### 2. 技术指标计算
- **均线系统**: MA5/10/20/60/120/250
- **MACD**: DIF, DEA, 柱状图
- **RSI**: 6/12/24周期
- **KDJ**: K, D, J值
- **布林带**: 上轨、中轨、下轨
- **ATR**: 波动率指标
- **量比**: 成交量比率

### 3. OCR识别
- 上传持仓截图自动识别
- 百度OCR API集成
- 自动解析持仓信息

### 4. 定时任务
- 每日20:00推送持仓报告到飞书
- 每日15:30更新技术指标
- 每5分钟更新实时价格

### 5. 分析报告
- 单只股票深度分析
- 每日持仓汇总报告
- 信号强度分析
- 风险等级评估

## 数据库表结构

### 核心表
1. `model_trade_position` - 持仓管理
2. `trade_stock_daily` - 日K线数据
3. `trade_technical_indicator` - 技术指标
4. `trade_analysis_report` - 分析报告
5. `trade_ocr_record` - OCR识别记录
6. `trade_stock_financial` - 财务数据
7. `trade_stock_news` - 新闻数据

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd quant

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填写必要配置
# - MySQL数据库配置（必需）
# - Tushare Token（必需）
# - 百度OCR API密钥（可选）
# - 飞书Webhook URL（可选）
```

### 3. 初始化数据库

```bash
# 创建数据库和表
python src/init_db.py
```

### 4. 下载K线数据

```bash
# 使用QMT数据源
python CASE-1/1-qmt_download_data.py

# 或使用Tushare数据源
python CASE-1/1-tushare_download_data.py
```

### 5. 计算技术指标

```bash
# 为所有股票计算技术指标
python src/technical_indicators.py
```

### 6. 启动后端服务

```bash
# 启动FastAPI服务
cd web/api
uvicorn main:app --reload --port 8000

# 或直接运行
python web/api/main.py
```

### 7. 启动前端服务

```bash
# 进入前端目录
cd web/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 8. 访问应用

- 前端界面: http://localhost:5173
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/

## API接口文档

### 持仓管理
- `GET /api/positions` - 获取持仓列表
- `POST /api/positions` - 创建持仓
- `PUT /api/positions/{id}` - 更新持仓
- `DELETE /api/positions/{id}` - 删除持仓
- `GET /api/accounts` - 获取账户列表

### 技术指标
- `GET /api/indicators/{stock_code}` - 获取技术指标
- `POST /api/sync/indicators` - 同步技术指标

### 分析报告
- `GET /api/reports/daily` - 获取每日报告
- `GET /api/reports/stock/{stock_code}` - 获取股票报告

### OCR识别
- `POST /api/ocr/upload` - 上传OCR图片

### 定时任务
- `GET /api/scheduler/jobs` - 获取定时任务列表
- `POST /api/scheduler/run/{job_id}` - 手动执行任务

## 目录结构

```
quant/
├── src/                          # 后端核心代码
│   ├── db.py                     # 数据库连接
│   ├── models.py                 # 数据库表定义
│   ├── init_db.py                # 数据库初始化
│   ├── technical_indicators.py   # 技术指标计算
│   ├── ocr_service.py            # OCR识别服务
│   ├── scheduler_service.py      # 定时任务调度
│   ├── push_service.py           # 飞书推送服务
│   └── report_service.py         # 报告生成服务
│
├── web/
│   ├── api/                      # FastAPI后端
│   │   └── main.py               # API路由定义
│   └── frontend/                 # React前端
│       ├── src/
│       │   ├── App.tsx           # 主应用组件
│       │   ├── main.tsx          # 入口文件
│       │   └── index.css         # 样式文件
│       └── package.json
│
├── CASE-1/                       # 基础策略回测
├── CASE-数据采集/                 # 数据采集脚本
├── CASE-数据采集 2/               # MySQL数据采集
├── CASE-多因子选股/               # 多因子选股
└── CASE-QMT测试/                 # QMT测试脚本
│
├── .env                          # 环境变量配置
├── .env.example                  # 环境变量模板
├── requirements.txt              # Python依赖
└── README.md                     # 项目说明
```

## 定时任务说明

系统启动后会自动运行以下定时任务：

1. **每日报告推送** (20:00)
   - 生成持仓报告
   - 推送到飞书

2. **技术指标更新** (15:30)
   - 计算最新技术指标
   - 更新数据库

3. **实时价格更新** (每5分钟)
   - 更新股票实时价格
   - 计算盈亏

## 开发计划

- [x] 数据库表结构设计
- [x] 技术指标计算服务
- [x] OCR识别服务
- [x] 定时任务调度
- [x] 飞书推送服务
- [x] FastAPI接口扩展
- [ ] React前端界面完善
- [ ] 新闻数据采集
- [ ] 端到端测试
- [ ] 性能优化

## 注意事项

1. **数据库配置**: 确保MySQL服务已启动，且.env中的配置正确
2. **TA-Lib安装**: 技术指标计算依赖TA-Lib库，如未安装会降级使用pandas实现
3. **OCR服务**: 需要配置百度OCR API密钥才能使用真实OCR功能
4. **飞书推送**: 需要配置飞书Webhook URL才能推送消息
5. **数据源**: 建议使用Tushare或QMT获取高质量的历史数据

## 常见问题

### 1. 数据库连接失败
- 检查MySQL服务是否启动
- 确认.env中的数据库配置正确
- 检查数据库用户权限

### 2. 技术指标计算失败
- 确保已下载K线数据
- 检查数据完整性
- 查看日志排查具体错误

### 3. 前端无法访问后端API
- 确认后端服务已启动
- 检查CORS配置
- 查看浏览器控制台错误

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

MIT License
