@echo off
cd /d "%~dp0"
git pull --ff-only
if errorlevel 1 (echo Update failed. See message above.& pause & exit /b 1)
call setup.bat
