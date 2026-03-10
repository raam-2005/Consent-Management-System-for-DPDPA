# DPDPA CMS - Automation Setup Guide

This guide explains how to set up automated tasks for the DPDPA Consent Management System.

## Overview

The system requires these scheduled tasks:

| Task | Frequency | Purpose |
|------|-----------|---------|
| `expire_consents` | Daily | Expire old consents, check SLA deadlines |
| `generate_compliance_report` | Weekly | Generate compliance report |

---

## Windows Task Scheduler Setup

### Prerequisites
- Python virtual environment set up in `BACKEND/venv`
- All dependencies installed

### Daily Tasks (Midnight)

1. **Open Task Scheduler**
   - Press `Win + R`, type `taskschd.msc`, press Enter

2. **Create New Task**
   - Click "Create Basic Task..."
   - Name: `DPDPA Daily Tasks`
   - Description: `Run daily consent expiry and SLA checks`

3. **Trigger**
   - Select "Daily"
   - Start time: `12:00:00 AM` (midnight)

4. **Action**
   - Select "Start a program"
   - Program/script: Browse to `BACKEND\scripts\daily_tasks.bat`
   - Start in: `C:\path\to\BACKEND` (your actual path)

5. **Finish**
   - Check "Open Properties dialog"
   - In Properties > Settings:
     - ✅ "Run task as soon as possible after scheduled start missed"
     - ✅ "Stop the task if it runs longer than: 1 hour"

### Weekly Tasks (Sunday 8 AM)

1. **Create New Task**
   - Name: `DPDPA Weekly Report`
   - Description: `Generate weekly compliance report`

2. **Trigger**
   - Select "Weekly"
   - Start time: `8:00:00 AM`
   - ✅ Sunday only

3. **Action**
   - Program/script: Browse to `BACKEND\scripts\weekly_tasks.bat`
   - Start in: `C:\path\to\BACKEND`

### Manual Commands (PowerShell)

```powershell
# Run daily tasks manually
cd "C:\path\to\BACKEND"
.\venv\Scripts\activate
python manage.py expire_consents

# Run weekly report manually
python manage.py generate_compliance_report

# With email notification
python manage.py generate_compliance_report --email admin@example.com
```

---

## Linux Cron Setup

### Prerequisites
- Python virtual environment set up in `BACKEND/venv`
- Scripts marked as executable

### Make Scripts Executable

```bash
cd /path/to/BACKEND/scripts
chmod +x daily_tasks.sh
chmod +x weekly_tasks.sh
```

### Edit Crontab

```bash
crontab -e
```

### Add Cron Jobs

```cron
# DPDPA CMS Scheduled Tasks
# -------------------------

# Daily tasks at midnight
0 0 * * * /path/to/BACKEND/scripts/daily_tasks.sh >> /path/to/BACKEND/logs/cron_daily.log 2>&1

# Weekly report on Sunday at 8 AM
0 8 * * 0 /path/to/BACKEND/scripts/weekly_tasks.sh >> /path/to/BACKEND/logs/cron_weekly.log 2>&1
```

### Verify Cron Jobs

```bash
# List current cron jobs
crontab -l

# Check cron service status
sudo systemctl status cron
```

### Manual Commands (Bash)

```bash
# Activate virtual environment
cd /path/to/BACKEND
source venv/bin/activate

# Run daily tasks
python manage.py expire_consents

# Run weekly report
python manage.py generate_compliance_report

# With specific output file
python manage.py generate_compliance_report --output my_report.json

# With email
python manage.py generate_compliance_report --email admin@example.com
```

---

## Command Reference

### expire_consents

```bash
# Basic usage
python manage.py expire_consents

# Dry run (preview without changes)
python manage.py expire_consents --dry-run
```

**What it does:**
- Expires consents past their expiry date
- Marks grievances as SLA breached if past deadline
- Checks rights request SLA deadlines
- Creates audit logs for all actions

### generate_compliance_report

```bash
# Basic usage (default: last 7 days)
python manage.py generate_compliance_report

# Custom date range
python manage.py generate_compliance_report --days 30

# Custom output file
python manage.py generate_compliance_report --output monthly_report.json

# With email notification
python manage.py generate_compliance_report --email admin@example.com
```

**What it does:**
- Generates comprehensive compliance statistics
- Calculates compliance score (0-100)
- Identifies issues (SLA breaches, expiring consents, etc.)
- Provides recommendations
- Saves report as JSON file
- Optionally sends email summary

---

## Logs and Reports

### Log Files
- `logs/dpdpa_cms.log` - Application logs
- `logs/cron_daily.log` - Daily task logs (Linux)
- `logs/cron_weekly.log` - Weekly task logs (Linux)

### Report Files
- `reports/compliance_report.json` - Latest report
- `reports/weekly_report_YYYYMMDD.json` - Weekly reports

---

## Troubleshooting

### Task Not Running

**Windows:**
1. Check Task Scheduler History
2. Verify paths in batch file
3. Run batch file manually to test

**Linux:**
1. Check cron logs: `grep CRON /var/log/syslog`
2. Verify script permissions
3. Test script manually

### Permission Issues

**Windows:**
- Run Task Scheduler as Administrator
- Check file permissions on scripts folder

**Linux:**
```bash
# Fix permissions
chmod +x scripts/*.sh
chmod 755 scripts/
```

### Python/Virtual Environment Issues

1. Verify virtual environment exists
2. Check Python path in scripts
3. Ensure all dependencies are installed

```bash
# Reinstall dependencies
pip install -r requirements.txt
```

---

## Production Recommendations

1. **Monitoring**: Set up alerts for failed tasks
2. **Backup**: Include reports folder in backups
3. **Retention**: Clean old reports periodically
4. **Email**: Configure proper SMTP for email notifications
5. **Logging**: Rotate logs to prevent disk space issues

```bash
# Example: Clean reports older than 90 days (Linux)
find /path/to/BACKEND/reports -name "*.json" -mtime +90 -delete
```
