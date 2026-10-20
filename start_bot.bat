
@echo off
setlocal
cd /d "%~dp0"

echo Starting Essen ABH Appointment Monitor...
echo.

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found.
    echo Create one with: python -m venv .venv
    pause
    exit /b 1
)

".venv\Scripts\python.exe" abh_monitor.py

echo.
echo Appointment monitor stopped.
pause
