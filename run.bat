@echo off
setlocal
title All-In-One Offline PDF & Media Workstation
cd /d "%~dp0"

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in your PATH.
    echo Please install Python 3.8+ from https://www.python.org/ and check "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

python main.py
if %errorlevel% neq 0 (
    echo.
    echo [NOTE] If you encounter missing package errors, run:
    echo        pip install -r requirements.txt
    echo.
    pause
)
