#!/bin/bash

# 启动脚本 - 同时启动前端和后端

cd "$(dirname "$0")"

# 启动后端
echo "启动后端 API..."
cd web/api
python main.py &
BACKEND_PID=$!
cd ../..

# 等待后端启动
sleep 2

# 启动前端
echo "启动前端..."
cd web/frontend
npm run dev &
FRONTEND_PID=$!
cd ../..

echo ""
echo "=========================================="
echo "投研系统已启动"
echo "=========================================="
echo "前端地址: http://localhost:3000"
echo "后端地址: http://localhost:8000"
echo "API文档:  http://localhost:8000/docs"
echo "=========================================="
echo ""
echo "按 Ctrl+C 停止服务"

# 等待
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
