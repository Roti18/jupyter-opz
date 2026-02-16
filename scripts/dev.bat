@echo off
echo Starting Development Environment...
echo [TIP] If Windows Firewall asks, please select 'Allow Access' for Python.

:: Activate venv
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment ^(venv^) not found. Please run run.bat install first.
    pause
    exit /b 1
)

:: Set MODE and run server
set MODE=DEVELOPMENT
python scripts\dev_server.py
pause
