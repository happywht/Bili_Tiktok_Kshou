@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
cd /d "%~dp0"

set PYTHONIOENCODING=utf-8
set PYTHONPATH=%~dp0
if "%PYTHONPATH:~-1%"=="\" set PYTHONPATH=%PYTHONPATH:~0,-1%

echo ========================================
echo   VideoHub - Start Service
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo [1/3] Checking dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo [2/3] Checking yt-dlp...
python -c "import yt_dlp" >nul 2>&1
if errorlevel 1 (
    echo Installing yt-dlp...
    pip install yt-dlp
)

echo [3/3] Checking .env...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul 2>&1
        echo Created .env file. Configure LLM_API_KEY if needed.
    )
)

echo.
echo ========================================
echo   Starting Backend...
echo ========================================
echo   Backend: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo ========================================
echo.

start "VideoHub Backend" cmd /k "cd /d "%~dp0" && set PYTHONIOENCODING=utf-8 && set PYTHONPATH=%~dp0 && python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   Backend started!
echo ========================================
echo.
echo Access the app at: http://localhost:5173 (if frontend is running)
echo Or API docs at: http://localhost:8000/docs
echo.
echo Press any key to exit...
pause >nul
