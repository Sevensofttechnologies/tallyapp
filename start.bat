@echo off
title TallyBots - Starting Services
color 0A

echo ============================================
echo        TallyBots - Service Launcher
echo ============================================
echo.
echo Ports:
echo   TallyInsight: http://localhost:8401
echo   TallyBridge:  http://localhost:8451
echo.
echo ============================================
echo.

:: Use full python path from miniconda
set PYTHON=C:\ProgramData\miniconda3\python.exe

:: Start TallyInsight in new window
echo Starting TallyInsight (Port 8401)...
start "TallyInsight - Port 8401" cmd /k "cd /d D:\Microservice\TallyBots\TallyInsight && %PYTHON% run.py --port 8401"

:: Wait 3 seconds for TallyInsight to start
ping 127.0.0.1 -n 4 > nul

:: Start TallyBridge in new window
echo Starting TallyBridge (Port 8451)...
start "TallyBridge - Port 8451" cmd /k "cd /d D:\Microservice\TallyBots\TallyBridge && %PYTHON% -m uvicorn app.main:app --host 0.0.0.0 --port 8451 --reload"

echo.
echo ============================================
echo   Both services started!
echo.
echo   TallyInsight: http://localhost:8401
echo   TallyBridge:  http://localhost:8451
echo   API Docs:     http://localhost:8451/docs
echo ============================================
echo.
echo Press any key to open TallyBridge in browser...
pause > nul

start http://localhost:8451
