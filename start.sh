#!/bin/bash

echo "========================================"
echo "  VideoHub - B站视频搜索与AI总结"
echo "========================================"
echo
echo "  支持平台: B站"
echo

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python，请先安装Python 3.8+"
    exit 1
fi

# 检查Node.js（可选）
SKIP_FRONTEND=0
if ! command -v node &> /dev/null; then
    echo "[警告] 未找到Node.js，将跳过前端启动"
    echo "        如需前端界面，请安装Node.js 18+"
    SKIP_FRONTEND=1
fi

echo
echo "[1/4] 检查后端依赖..."
if ! pip show fastapi &> /dev/null; then
    echo "正在安装后端依赖..."
    pip install -r requirements.txt
fi

echo
echo "[1.5/4] 检查 yt-dlp（AI总结需要）..."
if ! python3 -c "import yt_dlp" &> /dev/null; then
    echo "正在安装 yt-dlp..."
    pip install yt-dlp
fi

echo
echo "[2/4] 检查环境配置..."
if [ ! -f ".env" ]; then
    echo "[警告] 未找到.env文件"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "已创建.env文件，请配置以下参数:"
        echo "  - BILIBILI_SESSDATA  (B站Cookie，可选)"
        echo "  - LLM_API_KEY        (智谱AI Key，用于视频总结)"
    fi
else
    echo ".env 文件已存在"
fi

# 检查 AI 总结配置
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
key = os.getenv('LLM_API_KEY')
if not key or '填这里' in key:
    print('  [提示] LLM_API_KEY 未配置，AI视频总结功能将不可用')
    print('  请在 .env 文件中配置智谱AI Key')
else:
    print('  AI总结配置已就绪')
" 2>/dev/null

echo
echo "[3/4] 检查B站搜索..."
if python3 -c "import sys; sys.path.insert(0, 'api'); from services.bilibili_service import BilibiliService" 2>/dev/null; then
    echo "B站搜索模块就绪"
else
    echo "[提示] B站搜索模块未就绪"
fi

echo
echo "[4/4] 检查AI总结..."
if python3 -c "import sys; sys.path.insert(0, 'api'); from services.summary_service import SummaryService" 2>/dev/null; then
    echo "AI总结模块就绪"
else
    echo "[提示] AI总结模块未就绪"
fi

echo
echo "========================================"
echo "  启动服务..."
echo "========================================"
echo "  后端服务: http://localhost:8000"
echo "  前端界面: http://localhost:5173"
echo "  API文档:  http://localhost:8000/docs"
echo "========================================"
echo

# 设置PYTHONPATH
export PYTHONPATH=$(pwd)

# 启动后端服务
echo "正在启动后端服务..."
python3 -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 &
API_PID=$!

sleep 3

# 启动前端（如果Node.js可用）
if [ "$SKIP_FRONTEND" -eq 0 ]; then
    if [ -d "web/node_modules" ]; then
        echo "正在启动前端服务..."
        cd web && npm run dev &
        WEB_PID=$!
        cd ..
    else
        echo "[提示] 前端依赖未安装，正在安装..."
        cd web && npm install && cd ..
        echo "正在启动前端服务..."
        cd web && npm run dev &
        WEB_PID=$!
        cd ..
    fi
fi

echo
echo "========================================"
echo "  服务已启动！"
echo "========================================"
echo
echo "  使用方式:"
echo "  1. 浏览器访问 http://localhost:5173"
echo "  2. 或直接调用API http://localhost:8000/docs"
echo
echo "  API示例:"
echo "  - B站搜索:   /api/v1/search?keyword=Python&platform=bilibili"
echo
echo "  视频总结功能:"
echo "  - 鼠标悬停视频卡片，点击 ✨ AI总结按钮"
echo "  - 或访问 /summarize 页面手动输入视频URL"
echo
echo "按 Ctrl+C 停止所有服务..."

# 等待用户中断
trap "kill $API_PID $WEB_PID 2>/dev/null; exit 0" INT TERM
wait
