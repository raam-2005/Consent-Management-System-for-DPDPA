"""
Gunicorn Configuration File for DPDPA CMS

Usage:
    gunicorn consent_backend.wsgi:application -c gunicorn.conf.py

For more options, see:
    https://docs.gunicorn.org/en/stable/settings.html
"""

import multiprocessing
import os

# Get environment
is_development = os.getenv('DEBUG', 'True').lower() == 'true'

# ============================================
# SERVER SOCKET
# ============================================
# Bind to all interfaces (use 127.0.0.1 if behind nginx)
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')

# ============================================
# WORKER PROCESSES
# ============================================
# Recommended: 2-4 x $(NUM_CORES)
# For a small app, 2-4 workers is usually enough
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))

# Worker class (sync is default, use 'gevent' or 'eventlet' for async)
worker_class = os.getenv('GUNICORN_WORKER_CLASS', 'sync')

# Threads per worker (for sync workers)
threads = int(os.getenv('GUNICORN_THREADS', 4))

# ============================================
# WORKER TIMEOUT
# ============================================
# Timeout for worker to complete request
timeout = int(os.getenv('GUNICORN_TIMEOUT', 120))

# Graceful timeout for worker shutdown
graceful_timeout = int(os.getenv('GUNICORN_GRACEFUL_TIMEOUT', 30))

# Keep-alive connections timeout
keepalive = int(os.getenv('GUNICORN_KEEPALIVE', 5))

# ============================================
# WORKER RECYCLING
# ============================================
# Restart workers after this many requests (helps with memory leaks)
max_requests = int(os.getenv('GUNICORN_MAX_REQUESTS', 1000))

# Add randomness to max_requests to avoid all workers restarting at once
max_requests_jitter = int(os.getenv('GUNICORN_MAX_REQUESTS_JITTER', 50))

# ============================================
# LOGGING
# ============================================
# Access log - "-" for stdout
accesslog = os.getenv('GUNICORN_ACCESS_LOG', 'logs/gunicorn_access.log')

# Error log - "-" for stderr
errorlog = os.getenv('GUNICORN_ERROR_LOG', 'logs/gunicorn_error.log')

# Log level (debug, info, warning, error, critical)
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')

# Access log format
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)s'

# ============================================
# PROCESS NAMING
# ============================================
proc_name = 'dpdpa-cms'

# ============================================
# SERVER MECHANICS
# ============================================
# Daemonize the Gunicorn process (set False if using systemd)
daemon = False

# PID file location
pidfile = os.getenv('GUNICORN_PID_FILE', None)

# User and group to run workers as (for production)
# user = 'www-data'
# group = 'www-data'

# ============================================
# SSL (if not using nginx for SSL termination)
# ============================================
# keyfile = '/path/to/key.pem'
# certfile = '/path/to/cert.pem'

# ============================================
# DEVELOPMENT MODE OVERRIDES
# ============================================
if is_development:
    # Fewer workers for development
    workers = 1
    threads = 1
    
    # Enable auto-reload in development
    reload = True
    reload_engine = 'auto'
    
    # Log to stdout/stderr
    accesslog = '-'
    errorlog = '-'
    loglevel = 'debug'

# ============================================
# HOOKS (Optional callbacks)
# ============================================
def on_starting(server):
    """Called before master process is initialized."""
    pass

def on_reload(server):
    """Called when SIGHUP is received."""
    pass

def worker_abort(worker):
    """Called when a worker is killed due to timeout."""
    pass

def pre_fork(server, worker):
    """Called just before worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after worker is forked."""
    pass
