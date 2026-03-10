@echo off
REM ============================================
REM DPDPA CMS - Weekly Tasks Batch Script
REM ============================================
REM 
REM This script runs weekly maintenance tasks:
REM 1. generate_compliance_report - Weekly compliance report
REM
REM SETUP (Windows Task Scheduler):
REM 1. Open Task Scheduler (taskschd.msc)
REM 2. Create Basic Task > Name: "DPDPA Weekly Report"
REM 3. Trigger: Weekly, every Sunday at 08:00
REM 4. Action: Start a program
REM 5. Program: Path to this batch file
REM 6. Start in: Path to BACKEND folder
REM
REM ============================================

echo ============================================
echo DPDPA CMS - Weekly Tasks
echo Date: %date% Time: %time%
echo ============================================

REM Change to the BACKEND directory
cd /d "%~dp0\.."

REM Activate virtual environment
call venv\Scripts\activate

REM Run weekly compliance report
echo.
echo [1/1] Generating compliance report...
python manage.py generate_compliance_report --output weekly_report_%date:~-4,4%%date:~-7,2%%date:~-10,2%.json
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: generate_compliance_report failed!
) else (
    echo SUCCESS: Compliance report generated.
)

echo.
echo ============================================
echo Weekly tasks completed at %time%
echo ============================================

REM Deactivate virtual environment
deactivate
