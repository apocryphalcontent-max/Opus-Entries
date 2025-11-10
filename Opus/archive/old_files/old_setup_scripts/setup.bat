@echo off
REM OPUS MAXIMUS ULTIMATE: SETUP LAUNCHER
REM ======================================
REM
REM Quick setup for Windows users
REM Just double-click this file to run setup

echo.
echo ========================================================================
echo OPUS MAXIMUS ULTIMATE EDITION v3.0 - SETUP
echo ========================================================================
echo.
echo Starting setup process...
echo.

python setup.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================================
    echo SETUP SUCCESSFUL!
    echo ========================================================================
    echo.
    echo Next step: Run golden_pattern_extractor.py
    echo.
) else (
    echo.
    echo ========================================================================
    echo SETUP FAILED - Please check errors above
    echo ========================================================================
    echo.
)

pause
