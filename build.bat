@echo off
chcp 65001 >nul
REM MeowTrader 打包脚本
REM 自动执行清理和打包（全量版）

echo ============================================================
echo MeowTrader Build Script
echo ============================================================
echo.

REM 检查虚拟环境是否存在
if not exist ".venv\Scripts\python.exe" (
    echo 错误: 找不到虚拟环境
    echo 请先运行: uv sync
    exit /b 1
)

REM 切换到项目根目录（确保在正确的目录）
cd /d "%~dp0"

echo [1/2] 清理旧的打包文件...
.venv\Scripts\python.exe packaging\pyinstaller\build.py --clean
if errorlevel 1 (
    echo 清理失败
    exit /b 1
)

echo.
echo [2/2] 开始打包（默认全量版）...
.venv\Scripts\python.exe packaging\pyinstaller\build.py --all
if errorlevel 1 (
    echo 打包失败
    exit /b 1
)

echo.
echo ============================================================
echo 打包完成！
echo ============================================================
pause
