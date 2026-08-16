@echo off
cd /d "%~dp0"
echo This removes only generated virtual environments and caches. Your output is preserved.
set /p OK="Type YES to continue: "
if /i not "%OK%"=="YES" exit /b 0
for %%D in (.venv-gpu .venv-whisper .venv-vieneu .venv-asr) do if exist "%%D" rmdir /s /q "%%D"
echo Uninstalled optional runtimes.
pause
