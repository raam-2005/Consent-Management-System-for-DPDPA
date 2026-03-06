"""
Audit Logging Utility for DPDPA Consent Management System

This module provides helper functions to create audit logs consistently
across the application. It's used to track all important actions for
DPDPA compliance.

Usage:
    from application.audit_utils import create_audit_log
    
    create_audit_log(
        request=request,
        action='consent_granted',
        entity_type='consent',
        entity_id=str(consent.id),
        details={'purpose': purpose_name}
    )
"""

from .models import AuditLog, AuditActionChoices


def get_client_ip(request):
    """
    Get client IP address from request.
    Handles both direct connections and proxy forwarded requests.
    
    Args:
        request: Django request object
        
    Returns:
        str: Client IP address or None
    """
    if not request:
        return None
    
    # Check for forwarded IP (when behind proxy/load balancer)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """
    Get user agent string from request.
    
    Args:
        request: Django request object
        
    Returns:
        str: User agent string or None
    """
    if not request:
        return None
    return request.META.get('HTTP_USER_AGENT', '')


def create_audit_log(
    request=None,
    user=None,
    action=None,
    entity_type=None,
    entity_id=None,
    details=None
):
    """
    Create an audit log entry.
    
    This is the main function to use for creating audit logs.
    It automatically captures IP address and user agent from the request.
    
    Args:
        request: Django request object (optional, used to get IP and user agent)
        user: User who performed the action (defaults to request.user)
        action: Action type from AuditActionChoices
        entity_type: Type of entity affected (e.g., 'consent', 'grievance')
        entity_id: ID of the affected entity
        details: Dict with additional details about the action
        
    Returns:
        AuditLog: The created audit log entry
        
    Example:
        create_audit_log(
            request=request,
            action=AuditActionChoices.CONSENT_GRANTED,
            entity_type='consent',
            entity_id='uuid-here',
            details={'fiduciary': 'Company XYZ'}
        )
    """
    # Get user from request if not provided
    if user is None and request and hasattr(request, 'user') and request.user.is_authenticated:
        user = request.user
    
    # Prepare log entry
    log = AuditLog.objects.create(
        user=user,
        action=action,
        entity_type=entity_type or '',
        entity_id=str(entity_id) if entity_id else '',
        details=details or {},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return log


# ============================================
# CONVENIENCE FUNCTIONS FOR COMMON ACTIONS
# ============================================

def log_login(request, user):
    """Log user login event"""
    return create_audit_log(
        request=request,
        user=user,
        action=AuditActionChoices.LOGIN,
        entity_type='user',
        entity_id=user.id,
        details={'email': user.email, 'role': user.role}
    )


def log_logout(request, user):
    """Log user logout event"""
    return create_audit_log(
        request=request,
        user=user,
        action=AuditActionChoices.LOGOUT,
        entity_type='user',
        entity_id=user.id,
        details={'email': user.email}
    )


def log_consent_granted(request, consent):
    """Log consent granted event"""
    return create_audit_log(
        request=request,
        user=consent.principal,
        action=AuditActionChoices.CONSENT_GRANTED,
        entity_type='consent',
        entity_id=consent.id,
        details={
            'consent_id': consent.consent_id,
            'fiduciary': str(consent.fiduciary.organization_name or consent.fiduciary.email),
            'purpose': consent.purpose.name,
            'data_categories': consent.data_categories
        }
    )


def log_consent_revoked(request, consent, reason=''):
    """Log consent revoked event"""
    return create_audit_log(
        request=request,
        user=consent.principal,
        action=AuditActionChoices.CONSENT_REVOKED,
        entity_type='consent',
        entity_id=consent.id,
        details={
            'consent_id': consent.consent_id,
            'fiduciary': str(consent.fiduciary.organization_name or consent.fiduciary.email),
            'reason': reason
        }
    )


def log_consent_rejected(request, consent_request, reason=''):
    """Log consent request rejected event"""
    return create_audit_log(
        request=request,
        user=consent_request.principal,
        action=AuditActionChoices.CONSENT_REJECTED,
        entity_type='consent_request',
        entity_id=consent_request.id,
        details={
            'request_id': consent_request.request_id,
            'fiduciary': str(consent_request.fiduciary.organization_name or consent_request.fiduciary.email),
            'reason': reason
        }
    )


def log_data_accessed(request, user, data_type, entity_id=None, details=None):
    """Log data access event"""
    return create_audit_log(
        request=request,
        user=user,
        action=AuditActionChoices.DATA_ACCESSED,
        entity_type=data_type,
        entity_id=entity_id,
        details=details or {}
    )


def log_data_corrected(request, user, entity_type, entity_id, changes):
    """Log data correction event"""
    return create_audit_log(
        request=request,
        user=user,
        action=AuditActionChoices.DATA_CORRECTED,
        entity_type=entity_type,
        entity_id=entity_id,
        details={'changes': changes}
    )


def log_data_deleted(request, user, entity_type, entity_id, details=None):
    """Log data deletion event"""
    return create_audit_log(
        request=request,
        user=user,
        action=AuditActionChoices.DATA_DELETED,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details or {}
    )


def log_grievance_raised(request, grievance):
    """Log grievance filed event"""
    return create_audit_log(
        request=request,
        user=grievance.complainant,
        action=AuditActionChoices.GRIEVANCE_RAISED,
        entity_type='grievance',
        entity_id=grievance.id,
        details={
            'grievance_id': grievance.grievance_id,
            'subject': grievance.subject,
            'category': grievance.category
        }
    )


def log_grievance_resolved(request, grievance):
    """Log grievance resolved event"""
    return create_audit_log(
        request=request,
        user=grievance.assigned_dpo,
        action=AuditActionChoices.GRIEVANCE_RESOLVED,
        entity_type='grievance',
        entity_id=grievance.id,
        details={
            'grievance_id': grievance.grievance_id,
            'resolution': grievance.resolution
        }
    )


def log_profile_updated(request, user, changes):
    """Log profile update event"""
    return create_audit_log(
        request=request,
        user=user,
        action=AuditActionChoices.PROFILE_UPDATED,
        entity_type='user',
        entity_id=user.id,
        details={'changes': changes}
    )
