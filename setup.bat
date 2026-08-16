@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title VoxDub Studio - Setup

cd /d "%~dp0"

echo.
echo ============================================================
echo   VoxDub Studio - AUTOMATIC INSTALLATION
echo ============================================================
echo.
echo   This script will:
echo     1. Check Python and ffmpeg
echo     2. Install Python dependencies
echo     3. Create .env configuration file
echo     4. Install Whisper ASR engine      (runs locally, free)
echo     5. Install VieNeu TTS engine       (runs locally, free)
echo     6. Optional: Install GPU support   (10x faster processing)
echo.
echo   First run will download ~1-2 GB and take some time.
echo   Safe to re-run anytime - completed steps will be skipped.
echo.
pause

echo.
echo ------------------------------------------------------------
echo  [1/6] Checking Python
echo ------------------------------------------------------------

set "PY="
py -3 --version >nul 2>&1 && set "PY=py -3"
if not defined PY python --version >nul 2>&1 && set "PY=python"

if not defined PY (
    echo.
    echo  [ERROR] Python not found.
    echo.
    echo  Please download Python 3.10 or higher from:
    echo      https://www.python.org/downloads/
    echo.
    echo  IMPORTANT: Check "Add Python to PATH" during installation.
    echo  After installing, re-run this script.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('%PY% --version 2^>^&1') do set "PYVER=%%v"
echo  Found Python !PYVER!

echo.
echo ------------------------------------------------------------
echo  [2/6] Checking ffmpeg
echo ------------------------------------------------------------

where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [WARNING] ffmpeg not found. Without it you CANNOT export videos.
    echo.
    echo  Installation:
    echo    1. Download "full" build from https://www.gyan.dev/ffmpeg/builds/
    echo       ^(file: ffmpeg-release-full.7z^)
    echo    2. Extract to e.g. C:\ffmpeg
    echo    3. Add C:\ffmpeg\bin to Windows PATH
    echo    4. Re-run this script
    echo.
    echo  You can continue installation now and add ffmpeg later.
    echo.
    pause
) else (
    echo  Found ffmpeg
)

echo.
echo ------------------------------------------------------------
echo  [3/6] Installing Python dependencies
echo ------------------------------------------------------------
echo.

%PY% -m pip install --upgrade pip
%PY% -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo  [ERROR] Failed to install dependencies. Check internet connection.
    pause
    exit /b 1
)
echo.
echo  Dependencies installed successfully.

echo.
echo ------------------------------------------------------------
echo  [4/6] Creating configuration file .env
echo ------------------------------------------------------------

if exist ".env" (
    echo  .env already exists - keeping existing configuration.
) else (
    copy ".env.example" ".env" >nul
    echo  Created .env from .env.example
    echo.
    echo  IMPORTANT: Edit .env to configure:
    echo    - TRANSLATE_PROVIDER: choose voxdub/gemini/openrouter
    echo    - API keys for your chosen provider
    echo    - Other settings as needed
)

echo.
echo ------------------------------------------------------------
echo  [5/6] Installing ASR and TTS engines
echo ------------------------------------------------------------
echo.
echo  The following steps download ~1-2 GB. Both run locally,
echo  completely free, no API keys needed.
echo.

set /p DOASR="  Install Whisper ASR engine now? (y/n) [y]: "
if /i "!DOASR!"=="n" (
    echo  Skipped. Run later with: %PY% scripts\setup_whisper.py
) else (
    %PY% scripts\setup_whisper.py
    if errorlevel 1 echo  [WARNING] Whisper installation failed - run later: %PY% scripts\setup_whisper.py
)

echo.
set /p DOTTS="  Install VieNeu TTS engine now? (y/n) [y]: "
if /i "!DOTTS!"=="n" (
    echo  Skipped. Run later with: %PY% scripts\setup_vieneu.py
) else (
    %PY% scripts\setup_vieneu.py
    if errorlevel 1 echo  [WARNING] VieNeu installation failed - run later: %PY% scripts\setup_vieneu.py
)

echo.
echo ------------------------------------------------------------
echo  [6/6] GPU Support (Optional - 10x faster)
echo ------------------------------------------------------------
echo.
echo  GPU support requires NVIDIA GPU with CUDA.
echo  Provides 10x faster processing for Whisper and Demucs.
echo.
set /p DOGPU="  Install GPU support now? (y/n) [n]: "
if /i "!DOGPU!"=="y" (
    echo.
    echo  Installing GPU support (PyTorch with CUDA)...
    echo  This will download ~2 GB additional data.
    echo.
    if not exist ".venv-gpu" (
        %PY% -m venv .venv-gpu
    )
    .venv-gpu\Scripts\python.exe -m pip install --upgrade pip
    .venv-gpu\Scripts\python.exe -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
    .venv-gpu\Scripts\python.exe -m pip install demucs
    if errorlevel 1 (
        echo  [WARNING] GPU installation failed - you can still use CPU mode.
    ) else (
        echo  GPU support installed successfully.
    )
) else (
    echo  Skipped. Run later with: cai_them_gpu.bat
)

echo.
echo ============================================================
echo   INSTALLATION COMPLETE
echo ============================================================
echo.
echo   To start the application: double-click  chay_app.bat
echo.
echo   Optional installations:
echo     cai_them_douyin.bat      - Download videos from Douyin
echo     cai_them_paraformer.bat  - Better Chinese ASR accuracy
echo     cai_them_gpu.bat         - GPU acceleration (10x faster)
echo     nap_giong_doc.bat        - Load sample voice profiles
echo.
echo   Configuration:
echo     Edit .env file to set your translation provider and API keys
echo.
pause
