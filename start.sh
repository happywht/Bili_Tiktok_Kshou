#!/bin/bash

echo "========================================"
echo "  VideoHub - B站视频搜索平台"
echo "========================================"
echo

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python，请先安装Python 3.8+"
    exit 1
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "[错误] 未找到Node.js，请先安装Node.js 18+"
    exit 1
fi

echo "[1/4] 检查后端依赖..."
if ! pip show fastapi &> /dev/null; then
    echo "正在安装后端依赖..."
    pip install -r requirements.txt
fi

echo
echo "[2/4] 检查前端依赖..."
if [ ! -d "web/node_modules" ]; then
    echo "正在安装前端依赖..."
    cd web && npm install && cd ..
fi

echo
echo "[3/4] 检查环境配置..."
if [ ! -f ".env" ]; then
    echo "[警告] 未找到.env文件，请确保已配置BILIBILI_SESSDATA"
    echo "请复制.env.example为.env并填入你的SESSDATA"
    cp .env.example .env
fi

echo
echo "[4/4] 启动服务..."
echo
echo "========================================"
echo "  后端服务: http://localhost:8000"
echo "  前端界面: http://localhost:3000"
echo "  API文档:  http://localhost:8000/docs"
echo "========================================"
echo

# 启动后端服务
echo "正在启动后端服务..."
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 &
API_PID=$!

sleep 3

# 启动前端服务
echo "正在启动前端服务..."
cd web && npm run dev &
WEB_PID=$!

# 等待用户中断
echo
echo "服务已启动！请访问 http://localhost:3000"
echo "按 Ctrl+C 停止所有服务..."

trap "kill $API_PID $WEB_PID 2>/dev/null; exit 0" INT TERM
wait
