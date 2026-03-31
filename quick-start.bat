@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

set PYTHONIOENCODING=utf-8
set PYTHONPATH=%~dp0
if "%PYTHONPATH:~-1%"=="\" set PYTHONPATH=%PYTHONPATH:~0,-1%

echo Starting backend...
start "Backend" cmd /k "cd /d "%~dp0" && set PYTHONIOENCODING=utf-8 && set PYTHONPATH=%~dp0 && python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"

echo Backend starting...
echo Access: http://localhost:8000/docs
