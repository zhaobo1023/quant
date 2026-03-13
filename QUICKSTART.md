# 快速启动指南

## 🚀 5分钟快速启动

### 第1步：环境准备（2分钟）

```bash
# 1. 进入项目目录
cd /Users/zhaobo/data0/person/quant

# 2. 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt
```

### 第2步：数据库配置（1分钟）

```bash
# 1. 配置环境变量（数据库已配置好）
# 查看 .env 文件确认配置正确

# 2. 初始化数据库
python src/init_db.py

# 输出示例：
# ============================================================
# 数据库初始化
# ============================================================
# ...
# [OK] trade_technical_indicator
# [OK] trade_analysis_report
# [OK] trade_ocr_record
# 初始化完成!
```

### 第3步：启动系统（2分钟）

```bash
# 使用启动脚本
./start_extended.sh

# 选择 3 启动完整系统（后端+前端）

# 系统启动后访问：
# - 前端界面: http://localhost:5173
# - API文档: http://localhost:8000/docs
# - 健康检查: http://localhost:8000/
```

## 📊 功能测试

### 测试1：查看API文档
```bash
# 浏览器打开
open http://localhost:8000/docs

# 测试接口：
# GET /api/positions - 获取持仓列表
# GET /api/reports/daily - 获取每日报告
# POST /api/ocr/upload - 上传OCR图片
```

### 测试2：计算技术指标
```bash
# 如果有K线数据，运行：
python src/technical_indicators.py

# 输出示例：
# 开始计算 100 只股票的技术指标...
# [1/100] 处理 600519.SH...
#   600519.SH: 成功保存 250 条指标数据
```

### 测试3：查看定时任务
```bash
# 运行测试脚本
python tests/test_services.py

# 输出示例：
# ============================================================
# 个人持仓管理系统 - 功能测试
# ============================================================
# 1. 测试数据库连接...
#    ✓ 连接成功
# 2. 测试数据库表...
#    ✓ model_trade_position
#    ✓ trade_technical_indicator
#    ...
```

## 🎯 核心功能

### 1. 持仓管理
- ✅ 增删改查持仓
- ✅ 多账户支持
- ✅ 融资标记
- ✅ 状态跟踪

### 2. 技术分析
- ✅ MA5/10/20/60/120/250
- ✅ MACD/DIF/DEA
- ✅ RSI/KDJ/布林带
- ✅ ATR波动率

### 3. OCR识别
- ✅ 上传持仓截图
- ✅ 自动识别股票代码
- ✅ 解析持仓信息

### 4. 定时任务
- ✅ 每日20:00推送报告
- ✅ 每日15:30更新指标
- ✅ 每5分钟更新价格

### 5. 消息推送
- ✅ 飞书Webhook
- ✅ 持仓报告推送
- ✅ 分析报告推送

## 🔧 常见问题

### Q1: 数据库连接失败？
```bash
# 检查MySQL服务
mysql.server status  # 或 service mysql status

# 检查配置
cat .env | grep DB_

# 测试连接
python -c "from src.db import test_connection; print(test_connection())"
```

### Q2: 前端无法访问后端？
```bash
# 检查后端是否启动
curl http://localhost:8000/

# 检查CORS配置
# 已在 web/api/main.py 中配置 allow_origins=["*"]
```

### Q3: 技术指标计算失败？
```bash
# 检查是否有K线数据
python -c "from src.db import execute_query; print(len(execute_query('SELECT * FROM trade_stock_daily LIMIT 5')))"

# 如果没有数据，先下载K线数据
python CASE-1/1-tushare_download_data.py
```

### Q4: 定时任务不执行？
```bash
# 检查调度器状态
curl http://localhost:8000/api/scheduler/jobs

# 手动触发任务
curl -X POST http://localhost:8000/api/scheduler/run/daily_report_push
```

## 📁 重要文件位置

```
quant/
├── src/
│   ├── models.py                  # 数据库表定义
│   ├── technical_indicators.py    # 技术指标计算
│   ├── ocr_service.py             # OCR识别服务
│   ├── scheduler_service.py       # 定时任务调度
│   ├── push_service.py            # 飞书推送服务
│   └── report_service.py          # 报告生成服务
│
├── web/api/main.py                # FastAPI后端
├── web/frontend/                  # React前端
│
├── .env                           # 环境变量
├── requirements.txt               # Python依赖
├── start_extended.sh              # 启动脚本
└── README_EXTENDED.md             # 完整文档
```

## 🎓 下一步

1. **添加持仓数据**
   - 通过前端界面添加
   - 或使用OCR上传识别

2. **下载历史数据**
   - 运行K线数据下载脚本
   - 计算技术指标

3. **配置推送服务**
   - 配置飞书Webhook
   - 测试消息推送

4. **自定义分析**
   - 修改报告服务
   - 添加新的技术指标

## 💡 提示

- 首次使用建议先运行 `tests/test_services.py` 验证环境
- 生产环境建议配置HTTPS和数据库备份
- 定期检查日志文件排查问题
- 关注定时任务执行状态

## 📞 获取帮助

- 查看完整文档：`README_EXTENDED.md`
- 查看项目总结：`PROJECT_SUMMARY.md`
- 查看API文档：http://localhost:8000/docs

---

**祝你使用愉快！** 🎉
