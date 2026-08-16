@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║  VoxDub Studio - Build và Đóng gói Release              ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Python không tìm thấy. Vui lòng cài Python 3.10+ từ python.org
        pause
        exit /b 1
    )
    set PYTHON_CMD=py
) else (
    set PYTHON_CMD=python
)

echo ✅ Tìm thấy Python
echo.

REM Kiểm tra PyInstaller
%PYTHON_CMD% -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  PyInstaller chưa cài. Đang cài đặt...
    %PYTHON_CMD% -m pip install pyinstaller
    if errorlevel 1 (
        echo ❌ Cài PyInstaller thất bại
        pause
        exit /b 1
    )
    echo ✅ Đã cài PyInstaller
)

echo.
echo 🔨 Bắt đầu build...
echo.

REM Chạy script build
%PYTHON_CMD% build_release.py

if errorlevel 1 (
    echo.
    echo ❌ Build thất bại
    pause
    exit /b 1
)

echo.
echo ✅ Build hoàn tất!
echo.
echo 📦 Package đã sẵn sàng tại: dist\VoxDubStudio-v1.0.0.zip
echo.
pause
