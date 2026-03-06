"""
Django Models for DPDPA 2023 Consent Management System

Models:
- User: Custom user model with roles (Principal, Fiduciary, Processor, DPO)
- Purpose: Data processing purposes defined by fiduciaries
- ConsentRequest: Consent requests from fiduciaries to principals
- Consent: Granted consents
- Grievance: Complaints/grievances filed by principals
- AuditLog: Audit trail for all actions
"""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# ============================================
# CHOICES (Enums)
# ============================================
class RoleChoices(models.TextChoices):
    """User roles in the DPDPA system"""
    PRINCIPAL = 'principal', 'Data Principal'  # Individual whose data is processed
    FIDUCIARY = 'fiduciary', 'Data Fiduciary'  # Organization processing data
    PROCESSOR = 'processor', 'CMS Processor'   # CMS staff reviewing requests
    DPO = 'dpo', 'Data Protection Officer'     # Handles grievances


class ConsentStatusChoices(models.TextChoices):
    """Status of a consent"""
    PENDING = 'pending', 'Pending'
    ACTIVE = 'active', 'Active'
    REVOKED = 'revoked', 'Revoked'
    EXPIRED = 'expired', 'Expired'
    REJECTED = 'rejected', 'Rejected'


class CMSStatusChoices(models.TextChoices):
    """CMS review status"""
    PENDING_CMS = 'pending_cms', 'Pending CMS Review'
    CMS_APPROVED = 'cms_approved', 'CMS Approved'
    CMS_DENIED = 'cms_denied', 'CMS Denied'


class GrievanceStatusChoices(models.TextChoices):
    """Status of a grievance"""
    OPEN = 'open', 'Open'
    IN_PROGRESS = 'in_progress', 'In Progress'
    RESOLVED = 'resolved', 'Resolved'
    ESCALATED = 'escalated', 'Escalated'
    CLOSED = 'closed', 'Closed'


class GrievancePriorityChoices(models.TextChoices):
    """Priority levels for grievances"""
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    CRITICAL = 'critical', 'Critical'


class AuditActionChoices(models.TextChoices):
    """Types of auditable actions"""
    LOGIN = 'login', 'User Login'
    LOGOUT = 'logout', 'User Logout'
    CONSENT_GRANTED = 'consent_granted', 'Consent Granted'
    CONSENT_REVOKED = 'consent_revoked', 'Consent Revoked'
    CONSENT_REJECTED = 'consent_rejected', 'Consent Rejected'
    CONSENT_EXPIRED = 'consent_expired', 'Consent Expired'
    DATA_ACCESSED = 'data_accessed', 'Data Accessed'
    DATA_CORRECTED = 'data_corrected', 'Data Corrected'
    DATA_DELETED = 'data_deleted', 'Data Deleted'
    DATA_EXPORTED = 'data_exported', 'Data Exported'
    GRIEVANCE_RAISED = 'grievance_raised', 'Grievance Raised'
    GRIEVANCE_RESOLVED = 'grievance_resolved', 'Grievance Resolved'
    GRIEVANCE_ESCALATED = 'grievance_escalated', 'Grievance Escalated'
    PROFILE_UPDATED = 'profile_updated', 'Profile Updated'
    RIGHTS_REQUEST_SUBMITTED = 'rights_request_submitted', 'Rights Request Submitted'
    RIGHTS_REQUEST_COMPLETED = 'rights_request_completed', 'Rights Request Completed'


class ConsentLifecycleChoices(models.TextChoices):
    """Extended consent lifecycle states for DPDPA compliance"""
    REQUESTED = 'requested', 'Requested'
    PENDING_CMS = 'pending_cms', 'Pending CMS Review'
    CMS_APPROVED = 'cms_approved', 'CMS Approved'
    CMS_DENIED = 'cms_denied', 'CMS Denied'
    APPROVED = 'approved', 'Approved by Principal'
    ACTIVE = 'active', 'Active'
    WITHDRAWN = 'withdrawn', 'Withdrawn'
    EXPIRED = 'expired', 'Expired'
    REJECTED = 'rejected', 'Rejected'


class DataRightsRequestTypeChoices(models.TextChoices):
    """Types of Data Principal Rights requests under DPDPA"""
    ACCESS = 'access', 'Access Personal Data'
    CORRECTION = 'correction', 'Correction of Data'
    ERASURE = 'erasure', 'Erasure (Right to be Forgotten)'
    PORTABILITY = 'portability', 'Data Portability'
    WITHDRAW_ALL = 'withdraw_all', 'Withdraw All Consents'


class DataRightsRequestStatusChoices(models.TextChoices):
    """Status of Data Principal Rights requests"""
    PENDING = 'pending', 'Pending'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    REJECTED = 'rejected', 'Rejected'
    PARTIALLY_COMPLETED = 'partially_completed', 'Partially Completed'


# ============================================
# BASE MODEL (Timestamps)
# ============================================
class TimestampedModel(models.Model):
    """Abstract base model with created_at and updated_at timestamps"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ============================================
# USER MODEL
# ============================================
class User(AbstractUser, TimestampedModel):
    """
    Custom User model with DPDPA roles.
    
    Roles:
    - Principal: Individual whose personal data is being processed
    - Fiduciary: Organization that collects/processes personal data
    - Processor: CMS staff who review consent requests
    - DPO: Data Protection Officer handling grievances
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.PRINCIPAL
    )
    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # For Fiduciaries (Organizations)
    organization_name = models.CharField(max_length=255, blank=True, null=True)
    organization_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Profile
    avatar_url = models.URLField(blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name or self.username} ({self.get_role_display()})"

    @property
    def role_display(self):
        return self.get_role_display()


# ============================================
# PURPOSE MODEL
# ============================================
class Purpose(TimestampedModel):
    """
    Purpose for which data is collected.
    
    Data Fiduciaries define purposes for data collection.
    Each consent request is linked to a specific purpose.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    fiduciary = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purposes',
        limit_choices_to={'role': RoleChoices.FIDUCIARY}
    )
    data_categories = models.JSONField(
        default=list,
        help_text="Categories of personal data: ['name', 'email', 'phone', etc.]"
    )
    lawful_basis = models.CharField(
        max_length=100,
        default='consent',
        help_text="Legal basis for processing (consent, contract, legal obligation, etc.)"
    )
    retention_period_days = models.PositiveIntegerField(
        default=365,
        help_text="How long data will be retained in days"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'purposes'
        verbose_name = 'Purpose'
        verbose_name_plural = 'Purposes'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.fiduciary.organization_name}"

    @property
    def fiduciary_name(self):
        return self.fiduciary.organization_name or self.fiduciary.full_name


# ============================================
# CONSENT REQUEST MODEL
# ============================================
class ConsentRequest(TimestampedModel):
    """
    Consent Request from Data Fiduciary to Data Principal.
    
    Workflow:
    1. Fiduciary creates consent request (cms_status = pending_cms)
    2. CMS Processor reviews and approves/denies
    3. If CMS approved, Principal can accept/reject
    4. If accepted, a Consent record is created
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_id = models.CharField(max_length=50, unique=True, editable=False)
    
    # Parties involved
    fiduciary = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_consent_requests',
        limit_choices_to={'role': RoleChoices.FIDUCIARY}
    )
    principal = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_consent_requests',
        limit_choices_to={'role': RoleChoices.PRINCIPAL}
    )
    purpose = models.ForeignKey(
        Purpose,
        on_delete=models.CASCADE,
        related_name='consent_requests'
    )
    
    # Request details
    data_requested = models.JSONField(
        default=list,
        help_text="List of data fields being requested"
    )
    notes = models.TextField(blank=True, null=True)
    
    # CMS Review (by Processor)
    cms_status = models.CharField(
        max_length=20,
        choices=CMSStatusChoices.choices,
        default=CMSStatusChoices.PENDING_CMS
    )
    cms_reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_requests',
        limit_choices_to={'role__in': [RoleChoices.PROCESSOR, RoleChoices.DPO]}
    )
    cms_reviewed_at = models.DateTimeField(null=True, blank=True)
    cms_notes = models.TextField(blank=True, null=True)
    
    # Principal Response
    status = models.CharField(
        max_length=20,
        choices=ConsentStatusChoices.choices,
        default=ConsentStatusChoices.PENDING
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'consent_requests'
        verbose_name = 'Consent Request'
        verbose_name_plural = 'Consent Requests'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.request_id:
            # Generate unique request ID: CR-YYYYMMDD-XXXX
            today = timezone.now().strftime('%Y%m%d')
            count = ConsentRequest.objects.filter(
                request_id__startswith=f'CR-{today}'
            ).count() + 1
            self.request_id = f'CR-{today}-{count:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.request_id} - {self.fiduciary.organization_name} to {self.principal.full_name}"

    @property
    def status_display(self):
        return self.get_status_display()

    @property
    def cms_status_display(self):
        return self.get_cms_status_display()


# ============================================
# CONSENT MODEL
# ============================================
class Consent(TimestampedModel):
    """
    Active consent granted by a Data Principal.
    
    Created when a ConsentRequest is accepted.
    Can be revoked by the Principal at any time.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consent_id = models.CharField(max_length=50, unique=True, editable=False)
    
    # Link to the original request
    consent_request = models.OneToOneField(
        ConsentRequest,
        on_delete=models.CASCADE,
        related_name='consent'
    )
    
    # Parties (denormalized for easier querying)
    principal = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='given_consents',
        limit_choices_to={'role': RoleChoices.PRINCIPAL}
    )
    fiduciary = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_consents',
        limit_choices_to={'role': RoleChoices.FIDUCIARY}
    )
    purpose = models.ForeignKey(
        Purpose,
        on_delete=models.CASCADE,
        related_name='consents'
    )
    
    # Consent details
    data_categories = models.JSONField(
        default=list,
        help_text="Categories of data consented for"
    )
    status = models.CharField(
        max_length=20,
        choices=ConsentStatusChoices.choices,
        default=ConsentStatusChoices.ACTIVE
    )
    
    # Lifecycle state tracking for DPDPA compliance
    lifecycle_state = models.CharField(
        max_length=30,
        choices=ConsentLifecycleChoices.choices,
        default=ConsentLifecycleChoices.ACTIVE,
        help_text="Current state in the consent lifecycle"
    )
    
    # Timestamps
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revocation_reason = models.TextField(blank=True, null=True)
    
    # Auto-expiry tracking
    expiry_notified = models.BooleanField(
        default=False,
        help_text="Whether the user has been notified about expiry"
    )

    class Meta:
        db_table = 'consents'
        verbose_name = 'Consent'
        verbose_name_plural = 'Consents'
        ordering = ['-granted_at']

    def save(self, *args, **kwargs):
        if not self.consent_id:
            # Generate unique consent ID: CON-YYYYMMDD-XXXX
            today = timezone.now().strftime('%Y%m%d')
            count = Consent.objects.filter(
                consent_id__startswith=f'CON-{today}'
            ).count() + 1
            self.consent_id = f'CON-{today}-{count:04d}'
        
        # Check for expiry and update status
        if self.expires_at and timezone.now() > self.expires_at:
            if self.status == ConsentStatusChoices.ACTIVE:
                self.status = ConsentStatusChoices.EXPIRED
                self.lifecycle_state = ConsentLifecycleChoices.EXPIRED
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.consent_id} - {self.purpose.name}"

    @property
    def status_display(self):
        return self.get_status_display()

    @property
    def lifecycle_state_display(self):
        return self.get_lifecycle_state_display()

    @property
    def is_expired(self):
        """Check if consent has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    @property
    def days_until_expiry(self):
        """Get days until consent expires"""
        if not self.expires_at:
            return None
        delta = self.expires_at - timezone.now()
        return max(0, delta.days)

    def revoke(self, reason=None):
        """Revoke this consent"""
        self.status = ConsentStatusChoices.REVOKED
        self.lifecycle_state = ConsentLifecycleChoices.WITHDRAWN
        self.revoked_at = timezone.now()
        self.revocation_reason = reason
        self.save()

    def expire(self):
        """Mark consent as expired"""
        self.status = ConsentStatusChoices.EXPIRED
        self.lifecycle_state = ConsentLifecycleChoices.EXPIRED
        self.save()

    @classmethod
    def expire_all_overdue(cls):
        """
        Expire all consents that have passed their expiry date.
        Should be run periodically (e.g., via management command or celery task).
        
        Returns:
            int: Number of consents expired
        """
        now = timezone.now()
        expired_consents = cls.objects.filter(
            status=ConsentStatusChoices.ACTIVE,
            expires_at__lt=now
        )
        count = expired_consents.count()
        expired_consents.update(
            status=ConsentStatusChoices.EXPIRED,
            lifecycle_state=ConsentLifecycleChoices.EXPIRED
        )
        return count


# ============================================
# GRIEVANCE MODEL
# ============================================
class Grievance(TimestampedModel):
    """
    Grievance filed by a Data Principal.
    
    Workflow:
    1. Principal files grievance (status = open)
    2. DPO is assigned
    3. DPO investigates (status = in_progress)
    4. Resolution provided (status = resolved/closed)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    grievance_id = models.CharField(max_length=50, unique=True, editable=False)
    
    # Parties
    complainant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='filed_grievances'
    )
    against_entity = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='grievances_against',
        limit_choices_to={'role': RoleChoices.FIDUCIARY}
    )
    assigned_dpo = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_grievances',
        limit_choices_to={'role': RoleChoices.DPO}
    )
    
    # Grievance details
    subject = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(
        max_length=100,
        default='general',
        help_text="Category: consent, data_access, data_deletion, etc."
    )
    priority = models.CharField(
        max_length=20,
        choices=GrievancePriorityChoices.choices,
        default=GrievancePriorityChoices.MEDIUM
    )
    status = models.CharField(
        max_length=20,
        choices=GrievanceStatusChoices.choices,
        default=GrievanceStatusChoices.OPEN
    )
    
    # Resolution
    resolution = models.TextField(blank=True, null=True)
    
    # Escalation details
    escalation_reason = models.TextField(
        blank=True, 
        null=True,
        help_text="Reason for escalation if status is escalated"
    )
    escalated_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    filed_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    sla_deadline = models.DateTimeField(null=True, blank=True)
    
    # SLA tracking
    sla_breached = models.BooleanField(
        default=False,
        help_text="Whether SLA has been breached"
    )

    class Meta:
        db_table = 'grievances'
        verbose_name = 'Grievance'
        verbose_name_plural = 'Grievances'
        ordering = ['-filed_at']

    def save(self, *args, **kwargs):
        if not self.grievance_id:
            # Generate unique grievance ID: GRV-YYYYMMDD-XXXX
            today = timezone.now().strftime('%Y%m%d')
            count = Grievance.objects.filter(
                grievance_id__startswith=f'GRV-{today}'
            ).count() + 1
            self.grievance_id = f'GRV-{today}-{count:04d}'
        
        # Set SLA deadline (30 days from filing as per DPDPA)
        if not self.sla_deadline and not self.pk:
            from datetime import timedelta
            self.sla_deadline = timezone.now() + timedelta(days=30)
        
        # Check for SLA breach
        if self.sla_deadline and timezone.now() > self.sla_deadline:
            if self.status not in [GrievanceStatusChoices.RESOLVED, GrievanceStatusChoices.CLOSED]:
                self.sla_breached = True
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.grievance_id} - {self.subject}"

    @property
    def status_display(self):
        return self.get_status_display()

    @property
    def priority_display(self):
        return self.get_priority_display()

    @property
    def is_overdue(self):
        """Check if grievance is past SLA deadline"""
        if self.status in [GrievanceStatusChoices.RESOLVED, GrievanceStatusChoices.CLOSED]:
            return False
        if self.sla_deadline:
            return timezone.now() > self.sla_deadline
        return False

    @property
    def days_until_sla(self):
        """Get days until SLA deadline"""
        if not self.sla_deadline:
            return None
        delta = self.sla_deadline - timezone.now()
        return max(0, delta.days)

    def escalate(self, reason=''):
        """Escalate the grievance"""
        self.status = GrievanceStatusChoices.ESCALATED
        self.escalation_reason = reason
        self.escalated_at = timezone.now()
        self.save()

    def resolve(self, resolution):
        """Resolve the grievance"""
        self.status = GrievanceStatusChoices.RESOLVED
        self.resolution = resolution
        self.resolved_at = timezone.now()
        self.save()

    def close(self):
        """Close the grievance"""
        self.status = GrievanceStatusChoices.CLOSED
        self.closed_at = timezone.now()
        self.save()


# ============================================
# AUDIT LOG MODEL
# ============================================
class AuditLog(TimestampedModel):
    """
    Audit trail for all significant actions in the system.
    
    Tracks who did what, when, and on what entity.
    Required for DPDPA compliance.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    log_id = models.CharField(max_length=50, unique=True, editable=False)
    
    # Who performed the action
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    
    # What action was performed
    action = models.CharField(
        max_length=50,
        choices=AuditActionChoices.choices
    )
    
    # On what entity
    entity_type = models.CharField(
        max_length=50,
        help_text="Model name: consent, consent_request, grievance, user, etc."
    )
    entity_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="ID of the affected entity"
    )
    
    # Additional details (JSON)
    details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional context about the action"
    )
    
    # Request metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    
    # When
    performed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-performed_at']

    def save(self, *args, **kwargs):
        if not self.log_id:
            # Generate unique log ID: LOG-YYYYMMDD-XXXXXX
            today = timezone.now().strftime('%Y%m%d')
            count = AuditLog.objects.filter(
                log_id__startswith=f'LOG-{today}'
            ).count() + 1
            self.log_id = f'LOG-{today}-{count:06d}'
        super().save(*args, **kwargs)

    def __str__(self):
        user_str = self.user.email if self.user else 'System'
        return f"{self.log_id} - {user_str} - {self.get_action_display()}"

    @property
    def action_display(self):
        return self.get_action_display()


# ============================================
# DATA PRINCIPAL RIGHTS REQUEST MODEL
# ============================================
class DataPrincipalRightsRequest(TimestampedModel):
    """
    Data Principal Rights Request as per DPDPA 2023.
    
    Handles requests for:
    - Access to personal data
    - Correction of data
    - Erasure (Right to be forgotten)
    - Data portability
    - Withdraw all consents
    
    Workflow:
    1. Principal submits request (status = pending)
    2. DPO/Processor reviews and processes (status = in_progress)
    3. Request completed or rejected (status = completed/rejected)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_id = models.CharField(max_length=50, unique=True, editable=False)
    
    # Who is making the request
    principal = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='rights_requests',
        limit_choices_to={'role': RoleChoices.PRINCIPAL}
    )
    
    # Against which fiduciary (optional)
    fiduciary = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rights_requests_against',
        limit_choices_to={'role': RoleChoices.FIDUCIARY}
    )
    
    # Type of request
    request_type = models.CharField(
        max_length=30,
        choices=DataRightsRequestTypeChoices.choices
    )
    
    # Request details
    description = models.TextField(
        blank=True,
        help_text="Additional details about the request"
    )
    
    # For correction requests - what data to correct
    data_to_correct = models.JSONField(
        default=dict,
        blank=True,
        help_text="For correction requests: {field: {old_value, new_value}}"
    )
    
    # Status tracking
    status = models.CharField(
        max_length=30,
        choices=DataRightsRequestStatusChoices.choices,
        default=DataRightsRequestStatusChoices.PENDING
    )
    
    # Processing
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_rights_requests',
        limit_choices_to={'role__in': [RoleChoices.DPO, RoleChoices.PROCESSOR]}
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Response
    response_notes = models.TextField(
        blank=True,
        help_text="Notes about how the request was handled"
    )
    
    # For data export/portability - link to exported data
    exported_data_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL to download exported data (for portability requests)"
    )
    
    # SLA tracking (DPDPA requires response within 30 days)
    sla_deadline = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'data_rights_requests'
        verbose_name = 'Data Principal Rights Request'
        verbose_name_plural = 'Data Principal Rights Requests'
        ordering = ['-submitted_at']

    def save(self, *args, **kwargs):
        if not self.request_id:
            # Generate unique request ID: DPR-YYYYMMDD-XXXX
            today = timezone.now().strftime('%Y%m%d')
            count = DataPrincipalRightsRequest.objects.filter(
                request_id__startswith=f'DPR-{today}'
            ).count() + 1
            self.request_id = f'DPR-{today}-{count:04d}'
        
        # Set SLA deadline (30 days from submission as per DPDPA)
        if not self.sla_deadline and not self.pk:
            from datetime import timedelta
            self.sla_deadline = timezone.now() + timedelta(days=30)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.request_id} - {self.get_request_type_display()} by {self.principal.email}"

    @property
    def request_type_display(self):
        return self.get_request_type_display()

    @property
    def status_display(self):
        return self.get_status_display()

    @property
    def is_overdue(self):
        """Check if the request is past SLA deadline"""
        if self.status in [
            DataRightsRequestStatusChoices.COMPLETED,
            DataRightsRequestStatusChoices.REJECTED
        ]:
            return False
        if self.sla_deadline:
            return timezone.now() > self.sla_deadline
        return False

