@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   VideoHub - B站视频搜索平台
echo ========================================
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

:: 检查Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Node.js，请先安装Node.js 18+
    pause
    exit /b 1
)

echo [1/4] 检查后端依赖...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo 正在安装后端依赖...
    pip install -r requirements.txt
)

echo.
echo [2/4] 检查前端依赖...
if not exist "web\node_modules" (
    echo 正在安装前端依赖...
    cd web
    call npm install
    cd ..
)

echo.
echo [3/4] 检查环境配置...
if not exist ".env" (
    echo [警告] 未找到.env文件，请确保已配置BILIBILI_SESSDATA
    if exist ".env.example" (
        copy .env.example .env >nul 2>&1
        echo 已创建.env文件，请编辑填入你的SESSDATA
    ) else (
        echo 请手动创建.env文件并配置BILIBILI_SESSDATA
    )
)

echo.
echo [4/4] 启动服务...
echo.
echo ========================================
echo   后端服务: http://localhost:8000
echo   前端界面: http://localhost:5173
echo   API文档:  http://localhost:8000/docs
echo ========================================
echo.

:: 设置PYTHONPATH为当前目录
set PYTHONPATH=%~dp0

echo 正在启动后端服务...
start "VideoHub API" cmd /k "cd /d "%~dp0" && set PYTHONPATH=%~dp0 && python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo 正在启动前端服务...
start "VideoHub Web" cmd /k "cd /d "%~dp0web" && npm run dev"

echo.
echo 服务已启动！
echo - 前端界面: http://localhost:5173
echo - 后端API:  http://localhost:8000
echo - API文档:  http://localhost:8000/docs
echo.
echo 按任意键退出此窗口（服务会继续运行）...
pause >nul
