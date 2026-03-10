#!/bin/bash
# ============================================
# DPDPA CMS - Weekly Tasks Shell Script
# ============================================
#
# This script runs weekly maintenance tasks:
# 1. generate_compliance_report - Weekly compliance report
#
# SETUP (Linux Cron):
# 1. Make script executable: chmod +x weekly_tasks.sh
# 2. Edit crontab: crontab -e
# 3. Add: 0 8 * * 0 /path/to/BACKEND/scripts/weekly_tasks.sh
#    (Runs at 8 AM every Sunday)
#
# ============================================

echo "============================================"
echo "DPDPA CMS - Weekly Tasks"
echo "Date: $(date)"
echo "============================================"

# Change to BACKEND directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# Activate virtual environment
source venv/bin/activate

# Generate weekly report
REPORT_DATE=$(date +%Y%m%d)
echo ""
echo "[1/1] Generating compliance report..."
python manage.py generate_compliance_report --output "weekly_report_${REPORT_DATE}.json"
if [ $? -ne 0 ]; then
    echo "ERROR: generate_compliance_report failed!"
else
    echo "SUCCESS: Compliance report generated."
fi

echo ""
echo "============================================"
echo "Weekly tasks completed at $(date)"
echo "============================================"

# Deactivate virtual environment
deactivate
