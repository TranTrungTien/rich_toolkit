@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title VoxDub Studio - First Run Wizard

cd /d "%~dp0"

echo.
echo ============================================================
echo   VoxDub Studio - FIRST RUN SETUP WIZARD
echo ============================================================
echo.
echo   Welcome! This wizard will help you configure VoxDub.
echo.
pause

echo.
echo ------------------------------------------------------------
echo  Step 1: Choose Translation Provider
echo ------------------------------------------------------------
echo.
echo   VoxDub supports three translation providers:
echo.
echo   1. VoxDub Cloud (Recommended)
echo      - Centralized backend with optimized prompts
echo      - Automatic credit management
echo      - Context analysis and review passes
echo      - Requires: VOXDUB_API_URL configuration
echo.
echo   2. Gemini Direct
echo      - Direct Google Gemini API integration
echo      - Free tier: 15 requests/minute
echo      - Requires: GEMINI_API_KEY
echo      - Get key at: https://aistudio.google.com/apikey
echo.
echo   3. OpenRouter
echo      - Access to multiple AI models
echo      - Flexible pricing and rate limits
echo      - Requires: OPENROUTER_API_KEY
echo      - Get key at: https://openrouter.ai/keys
echo.
set /p PROVIDER="  Choose provider (1/2/3) [1]: "
if "!PROVIDER!"=="" set PROVIDER=1
if "!PROVIDER!"=="2" set PROVIDER_NAME=gemini
if "!PROVIDER!"=="3" set PROVIDER_NAME=openrouter
if "!PROVIDER!"=="1" set PROVIDER_NAME=voxdub

echo.
echo   Selected: !PROVIDER_NAME!

if "!PROVIDER_NAME!"=="gemini" (
    echo.
    echo ------------------------------------------------------------
    echo  Gemini API Configuration
    echo ------------------------------------------------------------
    echo.
    echo   Get your free API key at:
    echo     https://aistudio.google.com/apikey
    echo.
    set /p GEMINI_KEY="  Enter your Gemini API key: "
    echo.
    set /p GEMINI_MODEL="  Gemini model [gemini-2.0-flash-exp]: "
    if "!GEMINI_MODEL!"=="" set GEMINI_MODEL=gemini-2.0-flash-exp
)

if "!PROVIDER_NAME!"=="openrouter" (
    echo.
    echo ------------------------------------------------------------
    echo  OpenRouter API Configuration
    echo ------------------------------------------------------------
    echo.
    echo   Get your API key at:
    echo     https://openrouter.ai/keys
    echo.
    set /p OR_KEY="  Enter your OpenRouter API key: "
    echo.
    set /p OR_MODEL="  OpenRouter model [google/gemini-2.0-flash-exp:free]: "
    if "!OR_MODEL!"=="" set OR_MODEL=google/gemini-2.0-flash-exp:free
)

if "!PROVIDER_NAME!"=="voxdub" (
    echo.
    echo ------------------------------------------------------------
    echo  VoxDub Cloud Configuration
    echo ------------------------------------------------------------
    echo.
    echo   VoxDub Cloud requires backend URL configuration.
    echo   Contact support for backend setup or deployment.
    echo.
    set /p VOXDUB_URL="  Enter VoxDub API URL (or leave empty): "
)

echo.
echo ------------------------------------------------------------
echo  Step 2: ASR Engine Selection
echo ------------------------------------------------------------
echo.
echo   Choose speech recognition engine:
echo.
echo   1. Whisper (Recommended)
echo      - Supports all languages
echo      - GPU acceleration available
echo      - Models: tiny/base/small/medium/large-v3
echo.
echo   2. Paraformer
echo      - Chinese only, higher accuracy
echo      - CPU only (ONNX)
echo      - Requires: cai_them_paraformer.bat
echo.
set /p ASR="  Choose ASR engine (1/2) [1]: "
if "!ASR!"=="2" (
    set ASR_ENGINE=paraformer
    echo   Selected: Paraformer
) else (
    set ASR_ENGINE=whisper
    echo   Selected: Whisper
)

if "!ASR_ENGINE!"=="whisper" (
    echo.
    set /p WHISPER_MODEL="  Whisper model (auto/medium/large-v3) [auto]: "
    if "!WHISPER_MODEL!"=="" set WHISPER_MODEL=auto
)

echo.
echo ------------------------------------------------------------
echo  Step 3: Quality Preset
echo ------------------------------------------------------------
echo.
echo   1. Fast      - Faster processing, lower quality
echo   2. Balanced  - Good balance (Recommended)
echo   3. Quality   - Best quality, slower processing
echo.
set /p QUALITY="  Choose preset (1/2/3) [2]: "
if "!QUALITY!"=="1" set QUALITY_NAME=fast
if "!QUALITY!"=="3" set QUALITY_NAME=quality
if "!QUALITY!"=="" set QUALITY_NAME=balanced
if "!QUALITY!"=="2" set QUALITY_NAME=balanced

echo   Selected: !QUALITY_NAME!

echo.
echo ------------------------------------------------------------
echo  Writing configuration to .env
echo ------------------------------------------------------------
echo.

if not exist ".env" (
    copy ".env.example" ".env" >nul
)

:: Update .env file
powershell -Command "(Get-Content .env) -replace '^TRANSLATE_PROVIDER=.*', 'TRANSLATE_PROVIDER=!PROVIDER_NAME!' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace '^ASR_ENGINE=.*', 'ASR_ENGINE=!ASR_ENGINE!' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace '^QUALITY_PRESET=.*', 'QUALITY_PRESET=!QUALITY_NAME!' | Set-Content .env"

if defined WHISPER_MODEL (
    powershell -Command "(Get-Content .env) -replace '^WHISPER_MODEL=.*', 'WHISPER_MODEL=!WHISPER_MODEL!' | Set-Content .env"
)

if defined GEMINI_KEY (
    powershell -Command "(Get-Content .env) -replace '^GEMINI_API_KEY=.*', 'GEMINI_API_KEY=!GEMINI_KEY!' | Set-Content .env"
)

if defined GEMINI_MODEL (
    powershell -Command "(Get-Content .env) -replace '^GEMINI_MODEL=.*', 'GEMINI_MODEL=!GEMINI_MODEL!' | Set-Content .env"
)

if defined OR_KEY (
    powershell -Command "(Get-Content .env) -replace '^OPENROUTER_API_KEY=.*', 'OPENROUTER_API_KEY=!OR_KEY!' | Set-Content .env"
)

if defined OR_MODEL (
    powershell -Command "(Get-Content .env) -replace '^OPENROUTER_MODEL=.*', 'OPENROUTER_MODEL=!OR_MODEL!' | Set-Content .env"
)

if defined VOXDUB_URL (
    powershell -Command "(Get-Content .env) -replace '^VOXDUB_API_URL=.*', 'VOXDUB_API_URL=!VOXDUB_URL!' | Set-Content .env"
)

echo   Configuration saved to .env

echo.
echo ============================================================
echo   CONFIGURATION COMPLETE
echo ============================================================
echo.
echo   Your settings:
echo     Provider: !PROVIDER_NAME!
echo     ASR Engine: !ASR_ENGINE!
echo     Quality: !QUALITY_NAME!
echo.
echo   You can edit .env file anytime to change these settings.
echo.
echo   Ready to start! Run: chay_app.bat
echo.
pause
