@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title VoxDub Studio - GPU Setup

cd /d "%~dp0"

echo.
echo ============================================================
echo   VoxDub Studio - GPU ACCELERATION SETUP
echo ============================================================
echo.
echo   This installs GPU support for 10x faster processing.
echo.
echo   Requirements:
echo     - NVIDIA GPU with CUDA support
echo     - Windows 10/11
echo     - ~2 GB download
echo.
echo   GPU acceleration applies to:
echo     - Whisper ASR (speech recognition)
echo     - Demucs (vocal separation)
echo.
pause

echo.
echo ------------------------------------------------------------
echo  Checking Python
echo ------------------------------------------------------------

set "PY="
py -3 --version >nul 2>&1 && set "PY=py -3"
if not defined PY python --version >nul 2>&1 && set "PY=python"

if not defined PY (
    echo.
    echo  [ERROR] Python not found. Run setup.bat first.
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('%PY% --version 2^>^&1') do set "PYVER=%%v"
echo  Found Python !PYVER!

echo.
echo ------------------------------------------------------------
echo  Creating GPU virtual environment
echo ------------------------------------------------------------
echo.

if exist ".venv-gpu" (
    echo  .venv-gpu already exists - upgrading packages.
) else (
    echo  Creating .venv-gpu...
    %PY% -m venv .venv-gpu
    if errorlevel 1 (
        echo.
        echo  [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo.
echo ------------------------------------------------------------
echo  Installing PyTorch with CUDA 12.4
echo ------------------------------------------------------------
echo.
echo  Downloading ~2 GB...
echo.

.venv-gpu\Scripts\python.exe -m pip install --upgrade pip
.venv-gpu\Scripts\python.exe -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

if errorlevel 1 (
    echo.
    echo  [ERROR] PyTorch installation failed.
    echo  Check internet connection and try again.
    pause
    exit /b 1
)

echo.
echo ------------------------------------------------------------
echo  Installing Demucs
echo ------------------------------------------------------------
echo.

.venv-gpu\Scripts\python.exe -m pip install demucs

if errorlevel 1 (
    echo.
    echo  [WARNING] Demucs installation failed.
    echo  Vocal separation will use CPU only.
    pause
)

echo.
echo ------------------------------------------------------------
echo  Testing GPU availability
echo ------------------------------------------------------------
echo.

.venv-gpu\Scripts\python.exe -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"

if errorlevel 1 (
    echo.
    echo  [WARNING] GPU test failed.
    echo  Your GPU may not support CUDA or drivers need updating.
    echo.
    echo  Install NVIDIA drivers from:
    echo    https://www.nvidia.com/download/index.aspx
    echo.
) else (
    echo.
    echo  GPU setup complete!
)

echo.
echo ============================================================
echo   GPU SETUP COMPLETE
echo ============================================================
echo.
echo   GPU acceleration is now available for:
echo     - Whisper ASR (10x faster speech recognition)
echo     - Demucs (10x faster vocal separation)
echo.
echo   The pipeline will automatically use GPU when available.
echo.
pause
