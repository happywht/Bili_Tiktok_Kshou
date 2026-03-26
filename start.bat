@echo off
chcp 65001 >nul
cd /d "%~dp0"

:: 设置 Python 环境变量（解决 Windows 编码问题）
set PYTHONIOENCODING=utf-8
set PYTHONPATH=%~dp0

:: 移除 PYTHONPATH 末尾的反斜杠（避免路径问题）
if "%PYTHONPATH:~-1%"=="\" set PYTHONPATH=%PYTHONPATH:~0,-1%

echo ========================================
echo   VideoHub - 多平台视频搜索
echo ========================================
echo.
echo   支持平台: B站 | 抖音 | 小红书
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

:: 检查Node.js（前端需要）
node --version >nul 2>&1
if errorlevel 1 (
    echo [警告] 未找到Node.js，将跳过前端启动
    echo         如需前端界面，请安装Node.js 18+
    set SKIP_FRONTEND=1
) else (
    set SKIP_FRONTEND=0
)

echo.
echo [1/5] 检查后端依赖...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo 正在安装后端依赖...
    pip install -r requirements.txt
)

echo.
echo [1.5/5] 检查 yt-dlp（AI总结需要）...
python -c "import yt_dlp" >nul 2>&1
if errorlevel 1 (
    echo 正在安装 yt-dlp...
    pip install yt-dlp
)

echo.
echo [2/5] 检查 Playwright 浏览器...
python -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(headless=True); b.close(); p.stop()" >nul 2>&1
if errorlevel 1 (
    echo 正在安装 Playwright Chromium 浏览器...
    playwright install chromium
)

echo.
echo [3/5] 检查环境配置...
if not exist ".env" (
    echo [警告] 未找到.env文件
    if exist ".env.example" (
        copy .env.example .env >nul 2>&1
        echo 已创建.env文件，请配置以下参数:
        echo   - BILIBILI_SESSDATA  (B站Cookie)
        echo   - LLM_API_KEY        (智谱AI Key，用于视频总结)
        echo   - MEDIACRAWLER_HEADLESS=false  (首次使用抖音/小红书需设为false扫码登录)
    )
) else (
    echo .env 文件已存在
)

:: 检查 AI 总结配置
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
key = os.getenv('LLM_API_KEY')
if not key or '填这里' in key:
    print('  [提示] LLM_API_KEY 未配置，AI视频总结功能将不可用')
    print('  请在 .env 文件中配置智谱AI Key')
else:
    print('  AI总结配置已就绪')
" 2>nul

:: 检查 MediaCrawler 是否已克隆
if not exist "tools\MediaCrawler\main.py" (
    echo.
    echo [4/5] 检查 MediaCrawler...
    echo [警告] 未找到 MediaCrawler，正在克隆...
    git clone --depth 1 https://github.com/NanmiCoder/MediaCrawler.git tools\MediaCrawler
    if errorlevel 1 (
        echo [错误] MediaCrawler 克隆失败，抖音和小红书搜索将不可用
        echo 请手动执行: git clone --depth 1 https://github.com/NanmiCoder/MediaCrawler.git tools/MediaCrawler
    )
)

echo.
echo [5/5] 检查抖音/小红书环境...
python tools\mediacrawler_bridge.py --check >nul 2>&1
if errorlevel 1 (
    echo [提示] 抖音/小红书搜索环境未就绪，将在首次使用时自动检查
) else (
    echo 抖音/小红书搜索环境就绪
)

echo.
echo ========================================
echo   启动服务...
echo ========================================
echo   后端服务: http://localhost:8000
echo   前端界面: http://localhost:5173
echo   API文档:  http://localhost:8000/docs
echo ========================================
echo.

:: 启动后端服务（带 UTF-8 编码）
echo 正在启动后端服务...
start "VideoHub API" cmd /k "cd /d "%~dp0" && set PYTHONIOENCODING=utf-8 && set PYTHONPATH=%~dp0 && python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"

:: 等待后端启动
timeout /t 3 /nobreak >nul

:: 启动前端（如果Node.js可用）
if "%SKIP_FRONTEND%"=="0" (
    if exist "web\node_modules" (
        echo 正在启动前端服务...
        start "VideoHub Web" cmd /k "cd /d "%~dp0web" && npm run dev"
    ) else (
        echo [提示] 前端依赖未安装，正在安装...
        cd web
        call npm install
        cd ..
        start "VideoHub Web" cmd /k "cd /d "%~dp0web" && npm run dev"
    )
)

echo.
echo ========================================
echo   服务已启动！
echo ========================================
echo.
echo   使用方式:
echo   1. 浏览器访问 http://localhost:5173
echo   2. 或直接调用API http://localhost:8000/docs
echo.
echo   API示例:
echo   - B站搜索:   /api/v1/search?keyword=Python^&platform=bilibili
echo   - 抖音搜索:  /api/v1/search?keyword=Python^&platform=douyin
echo   - 小红书搜索: /api/v1/search?keyword=Python^&platform=xiaohongshu
echo.
echo   视频总结功能:
echo   - 鼠标悬停视频卡片，点击 ✨ AI总结按钮
echo   - 或在弹窗中手动输入视频URL
echo.
echo 按任意键退出此窗口（服务会继续运行）...
pause >nul
