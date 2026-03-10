"""
Security Logging Utilities for DPDPA Consent Management System

This module provides security-related logging functions for:
- Failed login attempts
- Suspicious activity detection
- Rate limiting violations
- Security events tracking

Usage:
    from application.security_logging import log_failed_login, log_suspicious_activity
    log_failed_login(request, email="user@example.com", reason="Invalid password")
"""

import logging
from django.utils import timezone
from django.conf import settings

# Create security logger
security_logger = logging.getLogger('application.security')
auth_logger = logging.getLogger('application.auth')


def get_client_ip(request):
    """
    Get the client IP address from request.
    Handles X-Forwarded-For header for reverse proxies.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    return ip


def get_user_agent(request):
    """Get the user agent from request."""
    return request.META.get('HTTP_USER_AGENT', 'unknown')


# ============================================
# AUTHENTICATION LOGGING
# ============================================

def log_successful_login(request, user):
    """
    Log successful login attempt.
    
    Args:
        request: Django request object
        user: User who logged in
    """
    ip = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    auth_logger.info(
        f"LOGIN_SUCCESS: User {user.email} (role: {user.role}) logged in "
        f"from IP {ip} using {user_agent[:50]}",
        extra={'ip': ip, 'user': user.email}
    )


def log_failed_login(request, email=None, reason="Invalid credentials"):
    """
    Log failed login attempt.
    
    This is important for detecting brute force attacks.
    
    Args:
        request: Django request object
        email: Email that was attempted
        reason: Reason for failure
    """
    ip = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    security_logger.warning(
        f"LOGIN_FAILED: Failed login attempt for '{email or 'unknown'}' "
        f"from IP {ip}. Reason: {reason}. User-Agent: {user_agent[:50]}",
        extra={'ip': ip, 'user': email or 'unknown'}
    )


def log_logout(request, user):
    """Log user logout."""
    ip = get_client_ip(request)
    
    auth_logger.info(
        f"LOGOUT: User {user.email} logged out from IP {ip}",
        extra={'ip': ip, 'user': user.email}
    )


def log_password_change(request, user, success=True):
    """Log password change attempt."""
    ip = get_client_ip(request)
    
    if success:
        auth_logger.info(
            f"PASSWORD_CHANGED: User {user.email} changed their password from IP {ip}",
            extra={'ip': ip, 'user': user.email}
        )
    else:
        security_logger.warning(
            f"PASSWORD_CHANGE_FAILED: Failed password change for {user.email} from IP {ip}",
            extra={'ip': ip, 'user': user.email}
        )


# ============================================
# SUSPICIOUS ACTIVITY LOGGING
# ============================================

def log_suspicious_activity(request, activity_type, description, user=None):
    """
    Log suspicious activity.
    
    Args:
        request: Django request object
        activity_type: Type of suspicious activity
        description: Description of the activity
        user: User involved (if any)
    """
    ip = get_client_ip(request)
    user_agent = get_user_agent(request)
    user_email = user.email if user else "anonymous"
    
    security_logger.warning(
        f"SUSPICIOUS_ACTIVITY: Type={activity_type} | User={user_email} | "
        f"IP={ip} | Description: {description} | UA: {user_agent[:50]}",
        extra={'ip': ip, 'user': user_email}
    )


def log_rate_limit_exceeded(request, limit_type="api", user=None):
    """
    Log when rate limit is exceeded.
    
    Args:
        request: Django request object
        limit_type: Type of rate limit (api, login, etc.)
        user: User who exceeded limit (if authenticated)
    """
    ip = get_client_ip(request)
    user_email = user.email if user else "anonymous"
    
    security_logger.warning(
        f"RATE_LIMIT_EXCEEDED: Type={limit_type} | User={user_email} | IP={ip}",
        extra={'ip': ip, 'user': user_email}
    )


def log_unauthorized_access(request, resource, user=None):
    """
    Log unauthorized access attempt.
    
    Args:
        request: Django request object
        resource: Resource that was attempted to access
        user: User who attempted access (if any)
    """
    ip = get_client_ip(request)
    user_email = user.email if user else "anonymous"
    
    security_logger.warning(
        f"UNAUTHORIZED_ACCESS: Resource={resource} | User={user_email} | IP={ip} | "
        f"Method={request.method} | Path={request.path}",
        extra={'ip': ip, 'user': user_email}
    )


# ============================================
# DATA ACCESS LOGGING
# ============================================

def log_sensitive_data_access(request, user, data_type, entity_id=None):
    """
    Log access to sensitive data (for DPDPA compliance).
    
    Args:
        request: Django request object
        user: User accessing the data
        data_type: Type of data accessed
        entity_id: ID of the entity accessed
    """
    ip = get_client_ip(request)
    
    auth_logger.info(
        f"DATA_ACCESS: User {user.email} accessed {data_type} "
        f"(ID: {entity_id or 'N/A'}) from IP {ip}",
        extra={'ip': ip, 'user': user.email}
    )


def log_data_export(request, user, export_type, record_count):
    """
    Log data export events (DPDPA requirement).
    
    Args:
        request: Django request object
        user: User exporting data
        export_type: Type of export
        record_count: Number of records exported
    """
    ip = get_client_ip(request)
    
    auth_logger.info(
        f"DATA_EXPORT: User {user.email} exported {record_count} {export_type} records "
        f"from IP {ip}",
        extra={'ip': ip, 'user': user.email}
    )


def log_data_deletion(request, user, data_type, entity_id):
    """
    Log data deletion events (DPDPA requirement).
    
    Args:
        request: Django request object
        user: User deleting data
        data_type: Type of data deleted
        entity_id: ID of deleted entity
    """
    ip = get_client_ip(request)
    
    security_logger.info(
        f"DATA_DELETION: User {user.email} deleted {data_type} (ID: {entity_id}) "
        f"from IP {ip}",
        extra={'ip': ip, 'user': user.email}
    )


# ============================================
# CONSENT OPERATION LOGGING
# ============================================

def log_consent_operation(request, user, operation, consent_id, details=None):
    """
    Log consent-related operations (DPDPA requirement).
    
    Args:
        request: Django request object
        user: User performing operation
        operation: Type of operation (granted, revoked, etc.)
        consent_id: ID of the consent
        details: Additional details
    """
    ip = get_client_ip(request)
    
    auth_logger.info(
        f"CONSENT_{operation.upper()}: User {user.email} | Consent: {consent_id} | "
        f"IP: {ip} | Details: {details or 'N/A'}",
        extra={'ip': ip, 'user': user.email}
    )


# ============================================
# ADMIN OPERATION LOGGING
# ============================================

def log_admin_operation(request, admin_user, operation, target, details=None):
    """
    Log administrative operations.
    
    Args:
        request: Django request object
        admin_user: Admin performing operation
        operation: Type of operation
        target: Target of operation
        details: Additional details
    """
    ip = get_client_ip(request)
    
    security_logger.info(
        f"ADMIN_OPERATION: Admin {admin_user.email} performed {operation} on {target} "
        f"from IP {ip}. Details: {details or 'N/A'}",
        extra={'ip': ip, 'user': admin_user.email}
    )
