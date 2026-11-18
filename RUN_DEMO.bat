@echo off
title IrrigaTrace Automated Demo Runner
cd /d "%~dp0"
echo ========================================================
echo   Launching IrrigaTrace Automated Evaluator Demo...
echo ========================================================
echo.
python run_demo.py %*
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Demo exited with error code %ERRORLEVEL%.
    pause
)
