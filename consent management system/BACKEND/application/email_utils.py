"""
Email Notification Utilities for DPDPA Consent Management System

This module provides email notification functions for:
- Consent expiry reminders
- Grievance SLA breach alerts
- Consent withdrawal confirmations
- Data rights request updates

Usage:
    from application.email_utils import send_consent_expiry_reminder
    send_consent_expiry_reminder(consent)

Email configuration is in settings.py
"""

import logging
from django.conf import settings
from django.core.mail import send_mail, send_mass_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


# ============================================
# EMAIL HELPER FUNCTIONS
# ============================================

def send_email_safe(subject, message, recipient_list, html_message=None):
    """
    Send email with error handling.
    Returns True if successful, False otherwise.
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Email sent successfully to: {recipient_list}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_list}: {str(e)}")
        return False


# ============================================
# CONSENT NOTIFICATIONS
# ============================================

def send_consent_expiry_reminder(consent):
    """
    Send reminder email when consent is about to expire.
    
    Called by: expire_consents management command (when expiry_notified is False)
    
    Args:
        consent: Consent object
    """
    if not consent.principal.email:
        logger.warning(f"No email for principal of consent {consent.consent_id}")
        return False
    
    days_left = (consent.expires_at - timezone.now()).days if consent.expires_at else 0
    
    subject = f"[DPDPA] Your consent is expiring in {days_left} days"
    
    message = f"""
Dear {consent.principal.full_name or consent.principal.username},

This is a reminder that your consent for the following data processing will expire soon:

Consent ID: {consent.consent_id}
Organization: {consent.fiduciary.organization_name or consent.fiduciary.email}
Purpose: {consent.purpose.name}
Data Categories: {', '.join(consent.purpose.data_categories)}
Expires On: {consent.expires_at.strftime('%Y-%m-%d %H:%M') if consent.expires_at else 'N/A'}
Days Remaining: {days_left}

What happens after expiry:
- The organization will no longer be able to process your data under this consent
- You may receive a new consent request if the organization wishes to continue

If you wish to renew your consent, please log in to the Consent Management Portal.

This is an automated message from the DPDPA Consent Management System.
Please do not reply to this email.

Best regards,
DPDPA Consent Management System
    """.strip()
    
    return send_email_safe(
        subject=subject,
        message=message,
        recipient_list=[consent.principal.email]
    )


def send_consent_withdrawal_confirmation(consent, reason=None):
    """
    Send confirmation email when consent is withdrawn/revoked.
    
    Called by: Consent.revoke() method or revoke API endpoint
    
    Args:
        consent: Consent object (after revocation)
        reason: Optional revocation reason
    """
    if not consent.principal.email:
        logger.warning(f"No email for principal of consent {consent.consent_id}")
        return False
    
    subject = f"[DPDPA] Your consent has been successfully withdrawn"
    
    message = f"""
Dear {consent.principal.full_name or consent.principal.username},

This email confirms that your consent has been successfully withdrawn.

Consent Details:
- Consent ID: {consent.consent_id}
- Organization: {consent.fiduciary.organization_name or consent.fiduciary.email}
- Purpose: {consent.purpose.name}
- Withdrawn On: {timezone.now().strftime('%Y-%m-%d %H:%M')}
{f'- Reason: {reason}' if reason else ''}

What this means:
- The organization must immediately stop processing your data under this consent
- Previously processed data may be retained as per their data retention policy
- You may file a grievance if you believe your data is being mishandled

You can view your consent history in the Consent Management Portal.

This is an automated message from the DPDPA Consent Management System.

Best regards,
DPDPA Consent Management System
    """.strip()
    
    # Also notify the fiduciary
    fiduciary_subject = f"[DPDPA] Consent Withdrawn - {consent.consent_id}"
    fiduciary_message = f"""
Dear {consent.fiduciary.organization_name or consent.fiduciary.full_name},

A data principal has withdrawn their consent:

Consent ID: {consent.consent_id}
Principal: {consent.principal.email}
Purpose: {consent.purpose.name}
Withdrawn On: {timezone.now().strftime('%Y-%m-%d %H:%M')}

Required Actions:
1. Stop processing data under this consent immediately
2. Review your data retention obligations
3. Update your records accordingly

Please ensure compliance with DPDPA 2023 requirements.

DPDPA Consent Management System
    """.strip()
    
    # Send to principal
    principal_sent = send_email_safe(
        subject=subject,
        message=message,
        recipient_list=[consent.principal.email]
    )
    
    # Send to fiduciary
    if consent.fiduciary.email:
        send_email_safe(
            subject=fiduciary_subject,
            message=fiduciary_message,
            recipient_list=[consent.fiduciary.email]
        )
    
    return principal_sent


def send_new_consent_request_notification(consent_request):
    """
    Notify principal of a new consent request (after CMS approval).
    
    Called by: ConsentRequest CMS approval
    """
    if not consent_request.principal.email:
        return False
    
    subject = f"[DPDPA] New Consent Request - Action Required"
    
    message = f"""
Dear {consent_request.principal.full_name or consent_request.principal.username},

You have received a new consent request:

Request ID: {consent_request.request_id}
From: {consent_request.fiduciary.organization_name or consent_request.fiduciary.email}
Purpose: {consent_request.purpose.name}
Description: {consent_request.purpose.description}
Data Requested: {', '.join(consent_request.data_requested)}

Please log in to the Consent Management Portal to review and respond to this request.

You have the right to:
- Accept or reject this request
- Request more information
- File a grievance if needed

This is an automated notification from the DPDPA Consent Management System.

Best regards,
DPDPA Consent Management System
    """.strip()
    
    return send_email_safe(
        subject=subject,
        message=message,
        recipient_list=[consent_request.principal.email]
    )


# ============================================
# GRIEVANCE NOTIFICATIONS
# ============================================

def send_grievance_sla_breach_alert(grievance):
    """
    Send alert when grievance SLA is breached.
    
    Called by: expire_consents management command
    """
    # Alert DPO
    if grievance.assigned_dpo and grievance.assigned_dpo.email:
        dpo_subject = f"[URGENT] Grievance SLA Breached - {grievance.grievance_id}"
        dpo_message = f"""
URGENT: GRIEVANCE SLA BREACH

Grievance ID: {grievance.grievance_id}
Subject: {grievance.subject}
Filed By: {grievance.complainant.email}
Filed On: {grievance.filed_at.strftime('%Y-%m-%d %H:%M')}
SLA Deadline: {grievance.sla_deadline.strftime('%Y-%m-%d %H:%M') if grievance.sla_deadline else 'N/A'}
Status: {grievance.get_status_display()}
Priority: {grievance.get_priority_display()}

This grievance has exceeded its SLA deadline. Immediate action is required.

Please resolve this grievance as soon as possible to maintain compliance.

DPDPA Consent Management System
        """.strip()
        
        send_email_safe(
            subject=dpo_subject,
            message=dpo_message,
            recipient_list=[grievance.assigned_dpo.email]
        )
    
    # Alert complainant
    if grievance.complainant.email:
        complainant_subject = f"[DPDPA] Update on your grievance - {grievance.grievance_id}"
        complainant_message = f"""
Dear {grievance.complainant.full_name or grievance.complainant.username},

We apologize for the delay in resolving your grievance:

Grievance ID: {grievance.grievance_id}
Subject: {grievance.subject}
Status: {grievance.get_status_display()}

We are working to resolve your complaint as quickly as possible.

If you need immediate assistance, please contact us directly.

Best regards,
DPDPA Consent Management System
        """.strip()
        
        return send_email_safe(
            subject=complainant_subject,
            message=complainant_message,
            recipient_list=[grievance.complainant.email]
        )
    
    return True


def send_grievance_resolution_notification(grievance):
    """
    Send notification when grievance is resolved.
    
    Called by: Grievance.resolve() method
    """
    if not grievance.complainant.email:
        return False
    
    subject = f"[DPDPA] Your grievance has been resolved - {grievance.grievance_id}"
    
    message = f"""
Dear {grievance.complainant.full_name or grievance.complainant.username},

Good news! Your grievance has been resolved.

Grievance Details:
- Grievance ID: {grievance.grievance_id}
- Subject: {grievance.subject}
- Status: Resolved
- Resolved On: {timezone.now().strftime('%Y-%m-%d %H:%M')}

Resolution:
{grievance.resolution or 'Please log in to the portal to view the full resolution.'}

If you are not satisfied with this resolution, you have the right to:
- Escalate this grievance
- File a new grievance
- Contact the Data Protection Board

Thank you for using the DPDPA Consent Management System.

Best regards,
DPDPA Consent Management System
    """.strip()
    
    return send_email_safe(
        subject=subject,
        message=message,
        recipient_list=[grievance.complainant.email]
    )


def send_grievance_assigned_notification(grievance):
    """
    Notify DPO when grievance is assigned.
    
    Called by: GrievanceViewSet.assign_dpo action
    """
    if not grievance.assigned_dpo or not grievance.assigned_dpo.email:
        return False
    
    subject = f"[DPDPA] New Grievance Assigned - {grievance.grievance_id}"
    
    message = f"""
Dear {grievance.assigned_dpo.full_name or grievance.assigned_dpo.username},

A new grievance has been assigned to you:

Grievance ID: {grievance.grievance_id}
Subject: {grievance.subject}
Priority: {grievance.get_priority_display()}
Filed By: {grievance.complainant.email}
Filed On: {grievance.filed_at.strftime('%Y-%m-%d %H:%M')}
SLA Deadline: {grievance.sla_deadline.strftime('%Y-%m-%d %H:%M') if grievance.sla_deadline else 'Not set'}

Description:
{grievance.description[:500]}...

Please log in to the portal to review and respond to this grievance.

DPDPA Consent Management System
    """.strip()
    
    return send_email_safe(
        subject=subject,
        message=message,
        recipient_list=[grievance.assigned_dpo.email]
    )


# ============================================
# DATA RIGHTS REQUEST NOTIFICATIONS
# ============================================

def send_rights_request_confirmation(rights_request):
    """
    Send confirmation when data rights request is submitted.
    
    Called by: DataPrincipalRightsRequestViewSet.create
    """
    if not rights_request.principal.email:
        return False
    
    subject = f"[DPDPA] Data Rights Request Received - {rights_request.request_id}"
    
    message = f"""
Dear {rights_request.principal.full_name or rights_request.principal.username},

Your data rights request has been received:

Request ID: {rights_request.request_id}
Request Type: {rights_request.get_request_type_display()}
Submitted On: {timezone.now().strftime('%Y-%m-%d %H:%M')}
Status: Pending

What to expect:
- Your request will be processed within the DPDPA timeline
- You will be notified when your request is complete
- You can track the status in the Consent Management Portal

Thank you for exercising your data rights under DPDPA 2023.

Best regards,
DPDPA Consent Management System
    """.strip()
    
    return send_email_safe(
        subject=subject,
        message=message,
        recipient_list=[rights_request.principal.email]
    )


def send_rights_request_completed_notification(rights_request):
    """
    Send notification when data rights request is completed.
    
    Called by: DataPrincipalRightsRequestViewSet.complete action
    """
    if not rights_request.principal.email:
        return False
    
    subject = f"[DPDPA] Your Data Rights Request is Complete - {rights_request.request_id}"
    
    message = f"""
Dear {rights_request.principal.full_name or rights_request.principal.username},

Your data rights request has been processed:

Request ID: {rights_request.request_id}
Request Type: {rights_request.get_request_type_display()}
Status: {rights_request.get_status_display()}
Completed On: {timezone.now().strftime('%Y-%m-%d %H:%M')}

Please log in to the Consent Management Portal to view the results.

If you have questions about the results, you may file a grievance.

Thank you for using the DPDPA Consent Management System.

Best regards,
DPDPA Consent Management System
    """.strip()
    
    return send_email_safe(
        subject=subject,
        message=message,
        recipient_list=[rights_request.principal.email]
    )


# ============================================
# BULK EMAIL FUNCTIONS
# ============================================

def send_expiry_reminders_bulk(consents):
    """
    Send expiry reminders to multiple consents efficiently.
    
    Args:
        consents: QuerySet of Consent objects
    
    Returns:
        int: Number of emails sent successfully
    """
    sent_count = 0
    
    for consent in consents:
        if consent.principal.email and not consent.expiry_notified:
            if send_consent_expiry_reminder(consent):
                # Mark as notified
                consent.expiry_notified = True
                consent.save(update_fields=['expiry_notified'])
                sent_count += 1
    
    logger.info(f"Sent {sent_count} consent expiry reminders")
    return sent_count


def send_sla_breach_alerts_bulk(grievances):
    """
    Send SLA breach alerts for multiple grievances.
    
    Args:
        grievances: QuerySet of Grievance objects with SLA breach
    
    Returns:
        int: Number of alerts sent
    """
    sent_count = 0
    
    for grievance in grievances:
        if send_grievance_sla_breach_alert(grievance):
            sent_count += 1
    
    logger.info(f"Sent {sent_count} SLA breach alerts")
    return sent_count
