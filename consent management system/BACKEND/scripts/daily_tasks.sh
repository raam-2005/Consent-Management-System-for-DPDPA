#!/bin/bash
# ============================================
# DPDPA CMS - Daily Tasks Shell Script
# ============================================
#
# This script runs daily maintenance tasks:
# 1. expire_consents - Expire old consents
# 2. check_grievance_sla - Check SLA deadlines
#
# SETUP (Linux Cron):
# 1. Make script executable: chmod +x daily_tasks.sh
# 2. Edit crontab: crontab -e
# 3. Add: 0 0 * * * /path/to/BACKEND/scripts/daily_tasks.sh
#    (Runs at midnight every day)
#
# ============================================

echo "============================================"
echo "DPDPA CMS - Daily Tasks"
echo "Date: $(date)"
echo "============================================"

# Change to BACKEND directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# Activate virtual environment
source venv/bin/activate

# Run expire_consents command
echo ""
echo "[1/2] Running expire_consents..."
python manage.py expire_consents
if [ $? -ne 0 ]; then
    echo "ERROR: expire_consents failed!"
else
    echo "SUCCESS: expire_consents completed."
fi

echo ""
echo "============================================"
echo "Daily tasks completed at $(date)"
echo "============================================"

# Deactivate virtual environment
deactivate
