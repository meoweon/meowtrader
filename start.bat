@echo off
chcp 65001 >nul
REM MeowTrader 启动脚本

cd /d "%~dp0"

REM 检查虚拟环境是否存在
if not exist ".venv\Scripts\python.exe" (
    echo ========================================
    echo 错误: 虚拟环境不存在
    echo 请先运行: uv sync
    echo ========================================
    pause
    exit /b 1
)

REM 启动应用
echo ========================================
echo 启动 MeowTrader...
echo ========================================
.venv\Scripts\python.exe app\desktop\main.py

REM 如果程序退出，显示退出码
if errorlevel 1 (
    echo.
    echo ========================================
    echo 程序异常退出，退出码: %errorlevel%
    echo ========================================
    pause
)
