# DPDPA CMS - Production Security Guide

This guide provides security recommendations for deploying the DPDPA Consent Management System in production.

## 🔐 Quick Security Checklist

Before deploying to production, ensure:

- [ ] DEBUG=False in settings
- [ ] Strong SECRET_KEY generated
- [ ] HTTPS enabled
- [ ] Database credentials secured
- [ ] Email settings configured
- [ ] CORS restricted to frontend domain
- [ ] Rate limiting enabled
- [ ] Logging configured
- [ ] Backups scheduled

---

## 1. Environment Variables

### Required .env Configuration

```env
# SECURITY - REQUIRED FOR PRODUCTION
DEBUG=False
SECRET_KEY=your-very-long-random-secret-key-min-50-chars
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (for PostgreSQL in production)
DATABASE_URL=postgres://user:password@localhost:5432/dpdpa_cms

# Email
EMAIL_HOST=smtp.yourdomain.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your-secure-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
ADMIN_EMAIL=admin@yourdomain.com

# CORS (restrict to your frontend domain)
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

### Generating a Secure SECRET_KEY

```bash
# Using Python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Using OpenSSL
openssl rand -base64 50
```

---

## 2. HTTPS Setup

### Using Nginx as Reverse Proxy

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL Certificate (Let's Encrypt recommended)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /path/to/static/;
    }
}
```

### Getting SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (should be automatic, but verify)
sudo certbot renew --dry-run
```

---

## 3. Django Security Settings

The following settings are automatically applied when `DEBUG=False`:

```python
# Already in settings.py - enforced when DEBUG=False

# HTTPS
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Content Security
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# CORS
CORS_ALLOW_ALL_ORIGINS = False
```

---

## 4. Database Security

### PostgreSQL (Recommended for Production)

```bash
# Install psycopg2
pip install psycopg2-binary

# Update settings or use DATABASE_URL
```

```python
# settings.py alternative for PostgreSQL
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(default='sqlite:///db.sqlite3')
}
```

### Database Best Practices

1. **Use strong passwords** - At least 16 characters
2. **Restrict access** - Only allow from application server
3. **Regular backups** - Use pg_dump or similar
4. **Encrypt at rest** - Enable database encryption
5. **Audit logging** - Enable PostgreSQL audit logs

---

## 5. Rate Limiting

Already configured in settings.py:

```python
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = [
    'rest_framework.throttling.AnonRateThrottle',
    'rest_framework.throttling.UserRateThrottle'
]
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '100/hour',
    'user': '1000/hour'
}
```

For production, consider using Redis for caching:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

---

## 6. Logging Configuration

Log files are stored in `BACKEND/logs/`:

- `dpdpa_cms.log` - General application logs
- `errors.log` - Error logs only
- `security.log` - Security events (failed logins, unauthorized access)

### Log Rotation

Logs are automatically rotated at 10MB with 5 backups for general logs and 10 backups for security logs.

### Monitoring Recommendations

1. **Set up log monitoring** - Use ELK stack, Graylog, or cloud logging
2. **Alert on security events** - Monitor security.log for anomalies
3. **Track failed logins** - Alert on multiple failures from same IP

---

## 7. Firewall Configuration

### UFW (Ubuntu/Debian)

```bash
# Allow SSH
sudo ufw allow 22

# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### Block Common Attack Patterns

```bash
# Block suspicious IPs (example)
sudo ufw deny from 192.168.1.100
```

---

## 8. Deployment Checklist

### Pre-Deployment

1. [ ] Update all dependencies: `pip install -U -r requirements.txt`
2. [ ] Run security checks: `python manage.py check --deploy`
3. [ ] Collect static files: `python manage.py collectstatic`
4. [ ] Run migrations: `python manage.py migrate`
5. [ ] Test all endpoints
6. [ ] Review CORS settings

### Post-Deployment

1. [ ] Verify HTTPS working
2. [ ] Test authentication flow
3. [ ] Verify email notifications
4. [ ] Check log file creation
5. [ ] Set up monitoring
6. [ ] Configure backups
7. [ ] Set up scheduled tasks (cron)

---

## 9. Running Production Server

### Using Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn consent_backend.wsgi:application --bind 0.0.0.0:8000 --workers 4

# With config file
gunicorn consent_backend.wsgi:application -c gunicorn.conf.py
```

### Gunicorn Configuration (gunicorn.conf.py)

```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"
```

### Using Systemd Service

```ini
# /etc/systemd/system/dpdpa-cms.service
[Unit]
Description=DPDPA CMS Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/BACKEND
ExecStart=/path/to/venv/bin/gunicorn consent_backend.wsgi:application -c gunicorn.conf.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable dpdpa-cms
sudo systemctl start dpdpa-cms
sudo systemctl status dpdpa-cms
```

---

## 10. Backup Strategy

### Database Backup (SQLite)

```bash
# Manual backup
cp db.sqlite3 backups/db.sqlite3.$(date +%Y%m%d)

# Add to cron (daily at 2 AM)
0 2 * * * cp /path/to/db.sqlite3 /path/to/backups/db.sqlite3.$(date +\%Y\%m\%d)
```

### Database Backup (PostgreSQL)

```bash
# Manual backup
pg_dump dpdpa_cms > backups/dpdpa_cms_$(date +%Y%m%d).sql

# Add to cron
0 2 * * * pg_dump dpdpa_cms > /path/to/backups/dpdpa_cms_$(date +\%Y\%m\%d).sql
```

---

## 11. Security Incident Response

### If You Suspect a Breach

1. **Isolate** - Take affected systems offline
2. **Assess** - Review security logs for unauthorized access
3. **Contain** - Reset passwords, revoke tokens
4. **Notify** - Per DPDPA requirements, notify affected users
5. **Document** - Record incident details for compliance

### Log Locations

- Security events: `logs/security.log`
- Application logs: `logs/dpdpa_cms.log`
- Error logs: `logs/errors.log`

---

## 12. Compliance Notes (DPDPA 2023)

### Data Retention

- Consents have configurable expiry
- Use `expire_consents` command to enforce expiry
- Audit logs should be retained as per policy

### Data Subject Rights

- Data export endpoint: `/api/rights-requests/my_data/`
- Data deletion: Via erasure request
- Consent withdrawal: Via revoke endpoint

### Logging Requirements

- All consent operations are logged
- Data access is audited
- Security events are tracked

---

## Quick Commands

```bash
# Check Django deployment settings
python manage.py check --deploy

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run scheduled tasks
python manage.py expire_consents
python manage.py generate_compliance_report
```
