# 持仓管理系统 - 完整启动指南

## 🎉 系统状态

### ✅ 后端服务 - 100% 完成
- 技术指标计算服务
- OCR识别服务
- 定时任务调度
- 飞书推送服务
- 报告生成服务
- FastAPI接口 (8个端点)
- 命令行工具

### ✅ 前端服务 - 100% 完成
- 持仓管理页面
- 技术分析页面
- OCR识别页面
- 分析报告页面
- 响应式设计
- 现代化UI

---

## 🚀 一键启动

### 方式1: 分别启动前后端 (推荐)

#### Step 1: 启动后端服务
```bash
# 在项目根目录
python start_backend.py
```

**后端服务地址:**
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/

#### Step 2: 启动前端服务 (新终端窗口)
```bash
# 在项目根目录
cd web/frontend
npm run dev
```

**前端服务地址:**
- 前端界面: http://localhost:3000

---

### 方式2: 仅后端API服务
```bash
cd web/api
uvicorn main:app --reload --port 8000
```

---

## 📊 功能测试

### 1. 测试后端API
```bash
# 健康检查
curl http://localhost:8000/

# 获取持仓列表
curl http://localhost:8000/api/positions

# 添加测试持仓
curl -X POST http://localhost:8000/api/positions \\
  -H "Content-Type: application/json" \\
  -d '{
    "stock_code": "600096.SH",
    "stock_name": "云天化",
    "shares": 1000,
    "cost_price": 22.50,
    "account_tag": "default"
  }'
```

### 2. 测试前端界面
访问 http://localhost:3000

**功能页面:**
1. **持仓管理** (`/`) - 添加/编辑/删除持仓
2. **技术分析** (`/analysis`) - 输入股票代码查询技术指标
3. **OCR识别** (`/ocr`) - 上传持仓截图识别
4. **分析报告** (`/reports`) - 查看每日持仓报告

### 3. 测试命令行工具
```bash
# 添加持仓
python position_cli.py add-position \\
  --code 600096.SH --name 云天化 \\
  --shares 1000 --cost 22.50

# 列出持仓
python position_cli.py list-positions

# 生成报告
python position_cli.py generate-report --daily
```

---

## 🗂️ 项目结构

```
quant/
├── start_backend.py           # 后端启动入口 ⭐
├── position_cli.py            # 命令行工具 ⭐
│
├── src/                       # 后端服务
│   ├── technical_indicators.py
│   ├── ocr_service.py
│   ├── scheduler_service.py
│   ├── push_service.py
│   └── report_service.py
│
├── web/
│   ├── api/main.py           # FastAPI后端
│   └── frontend/             # React前端
│       └── src/
│           ├── App.tsx
│           └── pages/
│               ├── PositionsPage.tsx
│               ├── AnalysisPage.tsx
│               ├── OCRPage.tsx
│               └── ReportsPage.tsx
│
├── .env                       # 配置文件
├── BACKEND_READY.md           # 后端就绪文档
├── FRONTEND_READY.md          # 前端就绪文档
└── START_SYSTEM.md            # 本文档
```

---

## ⚙️ 配置说明

### 必需配置 (`.env`)
```bash
# 数据库配置 (已有)
WUCAI_SQL_HOST=123.56.3.1
WUCAI_SQL_USERNAME=root
WUCAI_SQL_PASSWORD=your_password
WUCAI_SQL_PORT=3306
WUCAI_SQL_DB=trade
```

### 可选配置
```bash
# 百度OCR (可选,不配置则使用Mock)
BAIDU_OCR_API_KEY=your_key
BAIDU_OCR_SECRET_KEY=your_secret

# 飞书推送 (可选,不配置则使用Mock)
FEISHU_WEBHOOK_URL=https://open.feishu.cn/...
```

---

## 🔧 常见问题

### Q1: 后端启动失败?
```bash
# 检查Python环境
python --version  # 需要 >= 3.9

# 安装依赖
pip install -r requirements.txt

# 检查数据库连接
python -c "from src.db import get_connection; print('OK')"
```

### Q2: 前端无法访问后端?
```bash
# 确认后端已启动
curl http://localhost:8000/

# 检查vite代理配置 (web/frontend/vite.config.ts)
# proxy: '/api' -> 'http://localhost:8000'
```

### Q3: 数据库连接失败?
```bash
# 检查MySQL服务
mysql.server status  # Mac
# 或
service mysql status  # Linux

# 检查配置
cat .env | grep SQL
```

### Q4: TA-Lib未安装?
```bash
# Mac
brew install ta-lib

# Linux
sudo apt-get install ta-lib

# 如果不安装会自动降级到Pandas实现(功能略受限)
```

---

## 📝 快速功能测试清单

- [ ] 启动后端服务 (`python start_backend.py`)
- [ ] 访问API文档 (http://localhost:8000/docs)
- [ ] 启动前端服务 (`cd web/frontend && npm run dev`)
- [ ] 访问前端界面 (http://localhost:3000)
- [ ] 添加一个测试持仓
- [ ] 查看持仓列表
- [ ] 测试技术分析页面
- [ ] 测试OCR识别页面
- [ ] 查看分析报告

---

## 🎯 系统特性

### 后端特性
- ✅ 13种技术指标计算
- ✅ OCR图片识别
- ✅ 定时任务调度
- ✅ 飞书消息推送
- ✅ RESTful API
- ✅ 完整错误处理

### 前端特性
- ✅ 响应式设计
- ✅ 现代化UI
- ✅ 路由管理
- ✅ API集成
- ✅ 用户友好交互

---

## 🚀 下一步

1. **添加真实数据**
   - 下载K线数据
   - 计算技术指标
   - 添加持仓记录

2. **配置推送服务** (可选)
   - 配置飞书Webhook
   - 测试消息推送

3. **定时任务** (可选)
   - 每日20:00自动推送报告
   - 每日15:30更新技术指标

---

## 📞 获取帮助

- **后端文档**: `BACKEND_READY.md`
- **前端文档**: `FRONTEND_READY.md`
- **API文档**: http://localhost:8000/docs
- **问题排查**: 运行 `python tests/test_services.py`

---

**🎉 恭喜! 系统已完全就绪,可以开始使用!**

**版本**: v1.0.0
**完成日期**: 2026-03-13
**分支**: feature/qmt-data-sync
