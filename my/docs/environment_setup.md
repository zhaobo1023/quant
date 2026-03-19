# 环境变量配置说明

本文档说明项目所需的环境变量配置。

---

## 环境变量文件

项目使用 `.env` 文件管理环境变量，放置在项目根目录：

```
/Users/wenwen/data0/person/quant/.env
```

---

## 必需环境变量

### 数据库配置

| 变量名 | 说明 | 示例值 | 必需 |
|-------|------|--------|------|
| `WUCAI_SQL_HOST` | MySQL主机地址 | `localhost` 或 `rm-xxx.mysql.rds.aliyuncs.com` | ✅ |
| `WUCAI_SQL_USERNAME` | 数据库用户名 | `root` | ✅ |
| `WUCAI_SQL_PASSWORD` | 数据库密码 | `your_password` | ✅ |
| `WUCAI_SQL_DB` | 数据库名称 | `trade` | ✅ |
| `WUCAI_SQL_PORT` | 数据库端口 | `3306` | ✅ |

### 数据源API配置

| 变量名 | 说明 | 获取方式 | 必需 |
|-------|------|---------|------|
| `TUSHARE_TOKEN` | Tushare Pro API Token | https://tushare.pro/register | ✅ 强烈推荐 |

**Tushare Token 获取步骤：**
1. 访问 https://tushare.pro/register
2. 注册账号并登录
3. 进入"个人中心" → "接口Token"
4. 复制Token到 `.env` 文件

> Tushare 是本项目主要的数据源，涵盖：
> - 每日指标（市值、PE、PB等）
> - 行业分类
> - 资金流向
> - 北向持股
> - 融资融券
> - 财务数据

---

## 可选环境变量

### 回测参数

| 变量名 | 说明 | 默认值 |
|-------|------|--------|
| `BACKTEST_INITIAL_CASH` | 初始资金 | `1000000` (100万) |
| `BACKTEST_COMMISSION` | 手续费率 | `0.0002` (万分之二) |
| `BACKTEST_POSITION_PCT` | 仓位百分比 | `95` |

### AI API配置（可选）

| 变量名 | 说明 | 用途 |
|-------|------|------|
| `KIMI_API_KEY` | Kimi API密钥 | 新闻分析、研报解读 |
| `DASHSCOPE_API_KEY` | 阿里云通义千问 | AI辅助分析 |

---

## .env 文件模板

在项目根目录创建 `.env` 文件，内容如下：

```bash
# ===========================================
# 数据库配置 (必需)
# ===========================================
WUCAI_SQL_HOST=localhost
WUCAI_SQL_USERNAME=root
WUCAI_SQL_PASSWORD=your_password_here
WUCAI_SQL_DB=trade
WUCAI_SQL_PORT=3306

# ===========================================
# Tushare Pro API (强烈推荐)
# ===========================================
# 获取地址: https://tushare.pro/register
TUSHARE_TOKEN=your_tushare_token_here

# ===========================================
# 回测参数 (可选，有默认值)
# ===========================================
BACKTEST_INITIAL_CASH=1000000
BACKTEST_COMMISSION=0.0002
BACKTEST_POSITION_PCT=95

# ===========================================
# AI API (可选)
# ===========================================
# KIMI_API_KEY=your_kimi_api_key
# DASHSCOPE_API_KEY=your_dashscope_api_key
```

---

## 环境变量使用方式

### Python 读取

```python
from dotenv import dotenv_values

env = dotenv_values('.env')
db_host = env.get('WUCAI_SQL_HOST', 'localhost')
tushare_token = env.get('TUSHARE_TOKEN')
```

### 项目中的配置文件

`db_config.py` 已配置好从 `.env` 读取：

```python
from dotenv import dotenv_values

_env = dotenv_values('.env')

DB_CONFIG = {
    'host': _env.get('WUCAI_SQL_HOST', 'localhost'),
    'user': _env.get('WUCAI_SQL_USERNAME', 'root'),
    'password': _env.get('WUCAI_SQL_PASSWORD', ''),
    'database': _env.get('WUCAI_SQL_DB', 'trade'),
    'port': int(_env.get('WUCAI_SQL_PORT', '3306')),
}
```

---

## Tushare 权限说明

Tushare 采用积分制度，不同积分可访问不同接口：

| 积分等级 | 可用接口 | 获取方式 |
|---------|---------|---------|
| 120分+ | 基础接口（日线、财务） | 注册即送 |
| 2000分+ | 高级接口（分钟线、资金流） | 分享/捐赠 |
| 5000分+ | 全部接口 | 捐赠支持 |

**本项目所需接口及积分要求：**

| 接口 | 功能 | 最低积分 |
|-----|------|---------|
| `daily_basic` | 每日指标(市值/PE/PB) | 120分 ✅ |
| `index_classify` | 行业分类 | 120分 ✅ |
| `moneyflow` | 资金流向 | 2000分 |
| `hsgt_top10` | 北向持股 | 2000分 |
| `margin` | 融资融券 | 2000分 |

> 如果积分不足，可以使用 AKShare 作为替代数据源（免费无限制）

---

## 检查环境配置

运行以下命令检查环境变量是否配置正确：

```bash
cd /Users/wenwen/data0/person/quant
python -c "
from dotenv import dotenv_values
env = dotenv_values('.env')
print('=== 环境变量检查 ===')
print(f'数据库主机: {env.get(\"WUCAI_SQL_HOST\", \"未设置\")}')
print(f'数据库名称: {env.get(\"WUCAI_SQL_DB\", \"未设置\")}')
print(f'Tushare Token: {\"已设置\" if env.get(\"TUSHARE_TOKEN\") else \"未设置\"}')
"
```

---

## 常见问题

### Q: Tushare Token 无效？

检查Token是否正确复制，注意前后不要有空格。

### Q: 数据库连接失败？

1. 确认MySQL服务已启动
2. 检查防火墙是否开放3306端口
3. 确认用户名密码正确

### Q: 积分不足无法访问接口？

1. 使用 AKShare 替代（免费）
2. 在 Tushare 社区分享文章获取积分
3. 考虑捐赠支持

---

## 下一步

1. 复制上述 `.env` 模板到项目根目录
2. 填写实际的数据库密码和 Tushare Token
3. 运行检查命令验证配置
4. 执行数据采集脚本
