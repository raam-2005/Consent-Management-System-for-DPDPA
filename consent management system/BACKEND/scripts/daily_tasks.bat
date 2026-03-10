@echo off
REM ============================================
REM DPDPA CMS - Daily Tasks Batch Script
REM ============================================
REM 
REM This script runs daily maintenance tasks:
REM 1. expire_consents - Expire old consents
REM 2. check_grievance_sla - Check SLA deadlines
REM
REM SETUP (Windows Task Scheduler):
REM 1. Open Task Scheduler (taskschd.msc)
REM 2. Create Basic Task > Name: "DPDPA Daily Tasks"
REM 3. Trigger: Daily, at 00:00 (midnight)
REM 4. Action: Start a program
REM 5. Program: Path to this batch file
REM 6. Start in: Path to BACKEND folder
REM
REM ============================================

echo ============================================
echo DPDPA CMS - Daily Tasks
echo Date: %date% Time: %time%
echo ============================================

REM Change to the BACKEND directory (update this path)
cd /d "%~dp0"

REM Activate virtual environment
call venv\Scripts\activate

REM Run expire_consents command
echo.
echo [1/2] Running expire_consents...
python manage.py expire_consents
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: expire_consents failed!
) else (
    echo SUCCESS: expire_consents completed.
)

echo.
echo ============================================
echo Daily tasks completed at %time%
echo ============================================

REM Deactivate virtual environment
deactivate
