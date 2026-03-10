"""
Notification Utilities for DPDPA Consent Management System

This module provides helper functions to create in-app notifications.
Notifications are created for various events in the system.

Usage:
    from application.notification_utils import notify_consent_request
    notify_consent_request(consent_request)
"""

import logging
from datetime import timedelta
from django.utils import timezone
from .models import (
    Notification, NotificationTypeChoices, GrievancePriorityChoices
)

logger = logging.getLogger(__name__)


# ============================================
# CONSENT NOTIFICATIONS
# ============================================

def notify_consent_request(consent_request):
    """
    Notify principal of a new consent request.
    
    Called after CMS approves the request.
    """
    try:
        Notification.create_notification(
            user=consent_request.principal,
            notification_type=NotificationTypeChoices.CONSENT_REQUEST,
            title="New Consent Request",
            message=f"You have a new consent request from {consent_request.fiduciary.organization_name or consent_request.fiduciary.email} for {consent_request.purpose.name}.",
            entity_type="consent_request",
            entity_id=consent_request.id,
            action_url="/consent-requests",
            priority=GrievancePriorityChoices.MEDIUM
        )
        logger.info(f"Notification created for consent request {consent_request.request_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to create consent request notification: {e}")
        return False


def notify_consent_approved(consent):
    """
    Notify fiduciary that consent was approved by principal.
    """
    try:
        Notification.create_notification(
            user=consent.fiduciary,
            notification_type=NotificationTypeChoices.CONSENT_APPROVED,
            title="Consent Approved",
            message=f"Your consent request to {consent.principal.full_name or consent.principal.email} has been approved.",
            entity_type="consent",
            entity_id=consent.id,
            action_url="/consents",
            priority=GrievancePriorityChoices.LOW
        )
        return True
    except Exception as e:
        logger.error(f"Failed to create consent approved notification: {e}")
        return False


def notify_consent_rejected(consent_request):
    """
    Notify fiduciary that consent was rejected by principal.
    """
    try:
        Notification.create_notification(
            user=consent_request.fiduciary,
            notification_type=NotificationTypeChoices.CONSENT_REJECTED,
            title="Consent Rejected",
            message=f"Your consent request to {consent_request.principal.full_name or consent_request.principal.email} was rejected.",
            entity_type="consent_request",
            entity_id=consent_request.id,
            action_url="/consent-requests",
            priority=GrievancePriorityChoices.MEDIUM
        )
        return True
    except Exception as e:
        logger.error(f"Failed to create consent rejected notification: {e}")
        return False


def notify_consent_expiring(consent, days_remaining):
    """
    Notify principal that consent is expiring soon.
    """
    try:
        Notification.create_notification(
            user=consent.principal,
            notification_type=NotificationTypeChoices.CONSENT_EXPIRING,
            title="Consent Expiring Soon",
            message=f"Your consent for {consent.purpose.name} with {consent.fiduciary.organization_name or consent.fiduciary.email} will expire in {days_remaining} days.",
            entity_type="consent",
            entity_id=consent.id,
            action_url="/manage-consents",
            priority=GrievancePriorityChoices.MEDIUM
        )
        return True
    except Exception as e:
        logger.error(f"Failed to create consent expiring notification: {e}")
        return False


def notify_consent_expired(consent):
    """
    Notify both principal and fiduciary that consent has expired.
    """
    try:
        # Notify principal
        Notification.create_notification(
            user=consent.principal,
            notification_type=NotificationTypeChoices.CONSENT_EXPIRED,
            title="Consent Expired",
            message=f"Your consent for {consent.purpose.name} with {consent.fiduciary.organization_name or consent.fiduciary.email} has expired.",
            entity_type="consent",
            entity_id=consent.id,
            action_url="/consent-history",
            priority=GrievancePriorityChoices.LOW
        )
        
        # Notify fiduciary
        Notification.create_notification(
            user=consent.fiduciary,
            notification_type=NotificationTypeChoices.CONSENT_EXPIRED,
            title="Consent Expired",
            message=f"Consent from {consent.principal.full_name or consent.principal.email} for {consent.purpose.name} has expired.",
            entity_type="consent",
            entity_id=consent.id,
            action_url="/consents",
            priority=GrievancePriorityChoices.MEDIUM
        )
        return True
    except Exception as e:
        logger.error(f"Failed to create consent expired notification: {e}")
        return False


def notify_consent_withdrawn(consent, withdrawn_by):
    """
    Notify fiduciary when principal withdraws consent.
    """
    try:
        Notification.create_notification(
            user=consent.fiduciary,
            notification_type=NotificationTypeChoices.CONSENT_WITHDRAWN,
            title="Consent Withdrawn",
            message=f"{consent.principal.full_name or consent.principal.email} has withdrawn their consent for {consent.purpose.name}.",
            entity_type="consent",
            entity_id=consent.id,
            action_url="/consents",
            priority=GrievancePriorityChoices.HIGH
        )
        return True
    except Exception as e:
        logger.error(f"Failed to create consent withdrawn notification: {e}")
        return False


# ============================================
# GRIEVANCE NOTIFICATIONS
# ============================================

def notify_grievance_filed(grievance):
    """
    Notify complainant that grievance was filed.
    Also notify DPOs about new grievance.
    """
    from .models import User, RoleChoices
    
    try:
        # Notify complainant
        Notification.create_notification(
            user=grievance.complainant,
            notification_type=NotificationTypeChoices.GRIEVANCE_FILED,
            title="Grievance Submitted",
            message=f"Your grievance '{grievance.subject}' has been submitted. Grievance ID: {grievance.grievance_id}",
            entity_type="grievance",
            entity_id=grievance.id,
            action_url="/grievances",
            priority=GrievancePriorityChoices.MEDIUM
        )
        
        # Notify all DPOs
        dpos = User.objects.filter(role=RoleChoices.DPO, is_active=True)
        for dpo in dpos:
            Notification.create_notification(
                user=dpo,
                notification_type=NotificationTypeChoices.GRIEVANCE_FILED,
                title="New Grievance Filed",
                message=f"A new grievance '{grievance.subject}' has been filed. Priority: {grievance.get_priority_display()}",
                entity_type="grievance",
                entity_id=grievance.id,
                action_url="/dpo/grievances",
                priority=grievance.priority
            )
        
        return True
    except Exception as e:
        logger.error(f"Failed to create grievance filed notification: {e}")
        return False


def notify_grievance_assigned(grievance, assigned_dpo=None):
    """
    Notify DPO that grievance was assigned to them.
    
    Args:
        grievance: The Grievance object
        assigned_dpo: Optional User object (overrides grievance.assigned_dpo)
    """
    dpo = assigned_dpo or grievance.assigned_dpo
    if not dpo:
        return False
    
    try:
        # Check for duplicate notification to avoid spam
        existing = Notification.objects.filter(
            user=dpo,
            notification_type=NotificationTypeChoices.GRIEVANCE_ASSIGNED,
            entity_id=grievance.id,
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).exists()
        
        if existing:
            logger.info(f"Skipping duplicate grievance assigned notification for {grievance.grievance_id}")
            return True
        
        Notification.create_notification(
            user=dpo,
            notification_type=NotificationTypeChoices.GRIEVANCE_ASSIGNED,
            title="Grievance Assigned",
            message=f"Grievance '{grievance.subject}' ({grievance.grievance_id}) has been assigned to you. Priority: {grievance.get_priority_display()}",
            entity_type="grievance",
            entity_id=grievance.id,
            action_url="/dpo/grievances",
            priority=grievance.priority
        )
        return True
    except Exception as e:
        logger.error(f"Failed to create grievance assigned notification: {e}")
        return False


def notify_grievance_resolved(grievance):
    """
    Notify complainant that grievance was resolved.
    """
    try:
        Notification.create_notification(
            user=grievance.complainant,
            notification_type=NotificationTypeChoices.GRIEVANCE_RESOLVED,
            title="Grievance Resolved",
            message=f"Your grievance '{grievance.subject}' ({grievance.grievance_id}) has been resolved.",
            entity_type="grievance",
            entity_id=grievance.id,
            action_url="/grievances",
            priority=GrievancePriorityChoices.LOW
        )
        return True
    except Exception as e:
        logger.error(f"Failed to create grievance resolved notification: {e}")
        return False


def notify_grievance_update(grievance, update_message):
    """
    Notify complainant about grievance status update.
    """
    try:
        Notification.create_notification(
            user=grievance.complainant,
            notification_type=NotificationTypeChoices.GRIEVANCE_UPDATED,
            title="Grievance Update",
            message=f"Update on grievance '{grievance.subject}': {update_message}",
            entity_type="grievance",
            entity_id=grievance.id,
            action_url="/grievances",
            priority=GrievancePriorityChoices.MEDIUM
        )
        return True
    except Exception as e:
        logger.error(f"Failed to create grievance update notification: {e}")
        return False


# ============================================
# SLA BREACH NOTIFICATIONS
# ============================================

def notify_sla_breach(grievance):
    """
    Notify DPO and complainant about SLA breach.
    """
    try:
        # Notify assigned DPO
        if grievance.assigned_dpo:
            Notification.create_notification(
                user=grievance.assigned_dpo,
                notification_type=NotificationTypeChoices.SLA_BREACH,
                title="⚠️ SLA Breach Alert",
                message=f"Grievance '{grievance.subject}' ({grievance.grievance_id}) has exceeded SLA deadline! Immediate action required.",
                entity_type="grievance",
                entity_id=grievance.id,
                action_url="/dpo/grievances",
                priority=GrievancePriorityChoices.CRITICAL
            )
        
        # Notify complainant
        Notification.create_notification(
            user=grievance.complainant,
            notification_type=NotificationTypeChoices.SLA_BREACH,
            title="Grievance Delay Notice",
            message=f"We apologize for the delay in resolving your grievance '{grievance.subject}'. We are working on it urgently.",
            entity_type="grievance",
            entity_id=grievance.id,
            action_url="/grievances",
            priority=GrievancePriorityChoices.HIGH
        )
        
        return True
    except Exception as e:
        logger.error(f"Failed to create SLA breach notification: {e}")
        return False


# ============================================
# DATA RIGHTS REQUEST NOTIFICATIONS
# ============================================

def notify_rights_request_submitted(rights_request):
    """
    Notify principal that their rights request was submitted.
    Also notify processors/DPOs.
    """
    from .models import User, RoleChoices
    
    try:
        # Notify principal
        Notification.create_notification(
            user=rights_request.principal,
            notification_type=NotificationTypeChoices.RIGHTS_REQUEST,
            title="Rights Request Submitted",
            message=f"Your {rights_request.get_request_type_display()} request has been submitted. Request ID: {rights_request.request_id}",
            entity_type="rights_request",
            entity_id=rights_request.id,
            action_url="/data-access",
            priority=GrievancePriorityChoices.MEDIUM
        )
        
        # Notify processors
        processors = User.objects.filter(
            role__in=[RoleChoices.PROCESSOR, RoleChoices.DPO],
            is_active=True
        )
        for processor in processors:
            Notification.create_notification(
                user=processor,
                notification_type=NotificationTypeChoices.RIGHTS_REQUEST,
                title="New Data Rights Request",
                message=f"A new {rights_request.get_request_type_display()} request has been submitted.",
                entity_type="rights_request",
                entity_id=rights_request.id,
                action_url="/admin/rights-requests",
                priority=GrievancePriorityChoices.MEDIUM
            )
        
        return True
    except Exception as e:
        logger.error(f"Failed to create rights request notification: {e}")
        return False


def notify_rights_request_completed(rights_request):
    """
    Notify principal that their rights request was completed.
    """
    try:
        Notification.create_notification(
            user=rights_request.principal,
            notification_type=NotificationTypeChoices.RIGHTS_REQUEST,
            title="Rights Request Completed",
            message=f"Your {rights_request.get_request_type_display()} request ({rights_request.request_id}) has been completed.",
            entity_type="rights_request",
            entity_id=rights_request.id,
            action_url="/data-access",
            priority=GrievancePriorityChoices.LOW
        )
        return True
    except Exception as e:
        logger.error(f"Failed to create rights request completed notification: {e}")
        return False


# ============================================
# SYSTEM NOTIFICATIONS
# ============================================

def notify_system_alert(user, title, message, priority=GrievancePriorityChoices.MEDIUM, action_url=None):
    """
    Create a generic system notification.
    """
    try:
        Notification.create_notification(
            user=user,
            notification_type=NotificationTypeChoices.SYSTEM_ALERT,
            title=title,
            message=message,
            action_url=action_url,
            priority=priority
        )
        return True
    except Exception as e:
        logger.error(f"Failed to create system notification: {e}")
        return False


def notify_all_users(title, message, role=None, priority=GrievancePriorityChoices.MEDIUM):
    """
    Send notification to all users (optionally filtered by role).
    """
    from .models import User, RoleChoices
    
    try:
        users = User.objects.filter(is_active=True)
        if role:
            users = users.filter(role=role)
        
        for user in users:
            notify_system_alert(user, title, message, priority)
        
        logger.info(f"System notification sent to {users.count()} users")
        return users.count()
    except Exception as e:
        logger.error(f"Failed to send bulk notification: {e}")
        return 0


# ============================================
# PROFILE NOTIFICATIONS
# ============================================

def notify_profile_updated(user, updated_by=None):
    """
    Notify user that their profile was updated.
    
    Args:
        user: The User whose profile was updated
        updated_by: The User who made the update (optional)
    """
    try:
        # Don't notify if user updated their own profile
        if updated_by and updated_by.id == user.id:
            return True
        
        # Check for duplicate notification
        existing = Notification.objects.filter(
            user=user,
            notification_type=NotificationTypeChoices.SYSTEM_ALERT,
            title="Profile Updated",
            created_at__gte=timezone.now() - timedelta(minutes=5)
        ).exists()
        
        if existing:
            logger.info(f"Skipping duplicate profile update notification for {user.email}")
            return True
        
        message = "Your profile information has been updated."
        if updated_by:
            message = f"Your profile was updated by {updated_by.full_name or updated_by.email}."
        
        Notification.create_notification(
            user=user,
            notification_type=NotificationTypeChoices.SYSTEM_ALERT,
            title="Profile Updated",
            message=message,
            entity_type="user",
            entity_id=user.id,
            action_url="/profile",
            priority=GrievancePriorityChoices.LOW
        )
        return True
    except Exception as e:
        logger.error(f"Failed to create profile update notification: {e}")
        return False
