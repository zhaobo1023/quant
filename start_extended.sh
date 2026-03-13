#!/bin/bash

# 个人持仓管理系统启动脚本

echo "================================"
echo "个人持仓管理系统"
echo "================================"
echo ""

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo "错误: 未找到Python，请先安装Python 3.9+"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "检查并安装依赖..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "警告: .env文件不存在，正在从模板创建..."
    cp .env.example .env
    echo "请编辑.env文件并填写必要配置"
    exit 1
fi

# 初始化数据库
echo "检查数据库..."
python src/init_db.py

echo ""
echo "启动选项:"
echo "1. 启动后端API服务"
echo "2. 启动前端开发服务器"
echo "3. 启动完整系统（后端+前端）"
echo "4. 运行技术指标计算"
echo "5. 测试定时任务"
echo ""

read -p "请选择 (1-5): " choice

case $choice in
    1)
        echo "启动后端API服务..."
        cd web/api
        uvicorn main:app --reload --port 8000
        ;;
    2)
        echo "启动前端开发服务器..."
        cd web/frontend
        if [ ! -d "node_modules" ]; then
            echo "安装前端依赖..."
            npm install
        fi
        npm run dev
        ;;
    3)
        echo "启动完整系统..."
        # 启动后端
        cd web/api
        uvicorn main:app --reload --port 8000 &
        BACKEND_PID=$!
        cd ../..

        # 等待后端启动
        sleep 3

        # 启动前端
        cd web/frontend
        if [ ! -d "node_modules" ]; then
            echo "安装前端依赖..."
            npm install
        fi
        npm run dev &
        FRONTEND_PID=$!

        echo ""
        echo "系统已启动:"
        echo "  - 后端API: http://localhost:8000"
        echo "  - API文档: http://localhost:8000/docs"
        echo "  - 前端界面: http://localhost:5173"
        echo ""
        echo "按Ctrl+C停止所有服务"

        # 等待中断信号
        trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
        wait
        ;;
    4)
        echo "运行技术指标计算..."
        python src/technical_indicators.py
        ;;
    5)
        echo "测试定时任务..."
        python src/scheduler_service.py
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac
