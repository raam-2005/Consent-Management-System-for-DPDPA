"""
Django REST Framework Serializers for DPDPA Consent Management System

Serializers convert Django model instances to JSON and vice versa.
They also handle validation of incoming data.
"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import (
    User, Purpose, ConsentRequest, Consent, Grievance, AuditLog,
    DataPrincipalRightsRequest, Notification,
    RoleChoices, ConsentStatusChoices, CMSStatusChoices,
    GrievanceStatusChoices, GrievancePriorityChoices,
    DataRightsRequestTypeChoices, DataRightsRequestStatusChoices,
    ConsentLifecycleChoices, NotificationTypeChoices
)


# ============================================
# USER SERIALIZERS
# ============================================
class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal user info for nested relationships"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'organization_name', 'role']


class UserSerializer(serializers.ModelSerializer):
    """Full user serializer"""
    role_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'role', 'role_display',
            'full_name', 'aadhaar_number', 'phone', 'address',
            'organization_name', 'organization_id',
            'avatar_url', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'role_display', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users"""
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'password', 'role',
            'full_name', 'aadhaar_number', 'phone', 'address',
            'organization_name', 'organization_id', 'avatar_url'
        ]
        read_only_fields = ['id']

    def validate_aadhaar_number(self, value):
        if not value:
            return value
        aadhaar = value.strip()
        if not aadhaar.isdigit() or len(aadhaar) != 12:
            raise serializers.ValidationError('Aadhaar number must be exactly 12 digits.')
        return aadhaar
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# ============================================
# PURPOSE SERIALIZER
# ============================================
class PurposeSerializer(serializers.ModelSerializer):
    """Serializer for Purpose model"""
    fiduciary_name = serializers.CharField(read_only=True)
    fiduciary_details = UserMinimalSerializer(source='fiduciary', read_only=True)
    
    class Meta:
        model = Purpose
        fields = [
            'id', 'name', 'description',
            'fiduciary', 'fiduciary_name', 'fiduciary_details',
            'data_categories', 'lawful_basis', 'retention_period_days',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'fiduciary_name', 'created_at', 'updated_at']
        extra_kwargs = {
            # Fiduciary is auto-assigned in PurposeViewSet.perform_create for fiduciary users.
            'fiduciary': {'required': False}
        }


# ============================================
# CONSENT REQUEST SERIALIZERS
# ============================================
class ConsentRequestSerializer(serializers.ModelSerializer):
    """Full serializer for ConsentRequest"""
    fiduciary_details = UserMinimalSerializer(source='fiduciary', read_only=True)
    principal_details = UserMinimalSerializer(source='principal', read_only=True)
    purpose_details = PurposeSerializer(source='purpose', read_only=True)
    cms_reviewer_details = UserMinimalSerializer(source='cms_reviewed_by', read_only=True)
    status_display = serializers.CharField(read_only=True)
    cms_status_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = ConsentRequest
        fields = [
            'id', 'request_id',
            'fiduciary', 'fiduciary_details',
            'principal', 'principal_details',
            'purpose', 'purpose_details',
            'data_requested', 'notes',
            'cms_status', 'cms_status_display',
            'cms_reviewed_by', 'cms_reviewer_details',
            'cms_reviewed_at', 'cms_notes',
            'status', 'status_display',
            'requested_at', 'responded_at', 'expires_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'request_id', 'status_display', 'cms_status_display',
            'cms_reviewed_at', 'requested_at', 'responded_at',
            'created_at', 'updated_at'
        ]


class ConsentRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating consent requests"""
    
    class Meta:
        model = ConsentRequest
        fields = [
            'fiduciary', 'principal', 'purpose',
            'data_requested', 'notes', 'expires_at'
        ]
        extra_kwargs = {
            # Fiduciary is auto-assigned in ConsentRequestViewSet.perform_create for fiduciary users.
            'fiduciary': {'required': False}
        }


# ============================================
# CONSENT SERIALIZERS
# ============================================
class ConsentSerializer(serializers.ModelSerializer):
    """Full serializer for Consent"""
    principal_details = UserMinimalSerializer(source='principal', read_only=True)
    fiduciary_details = UserMinimalSerializer(source='fiduciary', read_only=True)
    purpose_details = PurposeSerializer(source='purpose', read_only=True)
    status_display = serializers.CharField(read_only=True)
    lifecycle_state_display = serializers.CharField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    days_until_expiry = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Consent
        fields = [
            'id', 'consent_id', 'consent_request',
            'principal', 'principal_details',
            'fiduciary', 'fiduciary_details',
            'purpose', 'purpose_details',
            'data_categories', 'status', 'status_display',
            'lifecycle_state', 'lifecycle_state_display',
            'granted_at', 'expires_at',
            'revoked_at', 'revocation_reason',
            'is_expired', 'days_until_expiry',
            'expiry_notified',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'consent_id', 'status_display', 'lifecycle_state_display',
            'granted_at', 'revoked_at', 'is_expired', 'days_until_expiry',
            'created_at', 'updated_at'
        ]


# ============================================
# GRIEVANCE SERIALIZERS
# ============================================
class GrievanceSerializer(serializers.ModelSerializer):
    """Full serializer for Grievance"""
    complainant_details = UserMinimalSerializer(source='complainant', read_only=True)
    against_entity_details = UserMinimalSerializer(source='against_entity', read_only=True)
    assigned_dpo_details = UserMinimalSerializer(source='assigned_dpo', read_only=True)
    status_display = serializers.CharField(read_only=True)
    priority_display = serializers.CharField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_until_sla = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Grievance
        fields = [
            'id', 'grievance_id',
            'complainant', 'complainant_details',
            'against_entity', 'against_entity_details',
            'assigned_dpo', 'assigned_dpo_details',
            'subject', 'description', 'category',
            'priority', 'priority_display',
            'status', 'status_display',
            'resolution',
            'escalation_reason', 'escalated_at',
            'filed_at', 'acknowledged_at', 'resolved_at', 'closed_at',
            'sla_deadline', 'sla_breached',
            'is_overdue', 'days_until_sla',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'grievance_id', 'status_display', 'priority_display',
            'filed_at', 'acknowledged_at', 'resolved_at', 'closed_at',
            'escalated_at', 'sla_deadline', 'sla_breached',
            'is_overdue', 'days_until_sla',
            'created_at', 'updated_at'
        ]


class GrievanceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating grievances (complainant is auto-assigned)"""
    
    class Meta:
        model = Grievance
        fields = [
            'against_entity',
            'subject', 'description', 'category', 'priority'
        ]


# ============================================
# DATA PRINCIPAL RIGHTS REQUEST SERIALIZERS
# ============================================
class DataPrincipalRightsRequestSerializer(serializers.ModelSerializer):
    """Full serializer for Data Principal Rights Request"""
    principal_details = UserMinimalSerializer(source='principal', read_only=True)
    fiduciary_details = UserMinimalSerializer(source='fiduciary', read_only=True)
    processed_by_details = UserMinimalSerializer(source='processed_by', read_only=True)
    request_type_display = serializers.CharField(read_only=True)
    status_display = serializers.CharField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = DataPrincipalRightsRequest
        fields = [
            'id', 'request_id',
            'principal', 'principal_details',
            'fiduciary', 'fiduciary_details',
            'request_type', 'request_type_display',
            'description', 'data_to_correct',
            'status', 'status_display',
            'processed_by', 'processed_by_details',
            'processed_at',
            'response_notes', 'exported_data_url',
            'sla_deadline', 'is_overdue',
            'submitted_at', 'completed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'request_id', 'request_type_display', 'status_display',
            'processed_at', 'sla_deadline', 'is_overdue',
            'submitted_at', 'completed_at',
            'created_at', 'updated_at'
        ]


class DataPrincipalRightsRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Data Principal Rights requests"""
    
    class Meta:
        model = DataPrincipalRightsRequest
        fields = [
            'principal', 'fiduciary', 'request_type',
            'description', 'data_to_correct'
        ]
    
    def validate(self, attrs):
        # Validate that correction requests have data_to_correct
        if attrs.get('request_type') == DataRightsRequestTypeChoices.CORRECTION:
            if not attrs.get('data_to_correct'):
                raise serializers.ValidationError({
                    'data_to_correct': 'This field is required for correction requests'
                })
        return attrs


class DataExportSerializer(serializers.Serializer):
    """Serializer for data export (portability) response"""
    user_profile = serializers.DictField()
    consents = serializers.ListField(child=serializers.DictField())
    consent_requests = serializers.ListField(child=serializers.DictField())
    grievances = serializers.ListField(child=serializers.DictField())
    audit_logs = serializers.ListField(child=serializers.DictField())
    exported_at = serializers.DateTimeField()
    export_format = serializers.CharField()


# ============================================
# AUDIT LOG SERIALIZERS
# ============================================
class AuditLogSerializer(serializers.ModelSerializer):
    """Full serializer for AuditLog"""
    user_details = UserMinimalSerializer(source='user', read_only=True)
    action_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'log_id',
            'user', 'user_details',
            'action', 'action_display',
            'entity_type', 'entity_id',
            'details',
            'ip_address', 'user_agent',
            'performed_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'log_id', 'action_display',
            'performed_at', 'created_at'
        ]


class AuditLogCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating audit logs"""
    
    class Meta:
        model = AuditLog
        fields = [
            'user', 'action', 'entity_type', 'entity_id',
            'details', 'ip_address', 'user_agent'
        ]


# ============================================
# DASHBOARD STATS SERIALIZER
# ============================================
class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    total_consents = serializers.IntegerField()
    active_consents = serializers.IntegerField()
    pending_requests = serializers.IntegerField()
    revoked_consents = serializers.IntegerField()
    open_grievances = serializers.IntegerField()
    
    # Role-specific stats (optional)
    my_active_consents = serializers.IntegerField(required=False)
    my_pending_requests = serializers.IntegerField(required=False)
    my_grievances = serializers.IntegerField(required=False)
    my_consent_requests = serializers.IntegerField(required=False)
    pending_cms_review = serializers.IntegerField(required=False)
    pending_cms_reviews = serializers.IntegerField(required=False)
    approved_today = serializers.IntegerField(required=False)
    assigned_grievances = serializers.IntegerField(required=False)
    unassigned_grievances = serializers.IntegerField(required=False)
    total_principals = serializers.IntegerField(required=False)
    total_fiduciaries = serializers.IntegerField(required=False)


class ComplianceDashboardSerializer(serializers.Serializer):
    """Serializer for DPDPA compliance dashboard statistics"""
    # Consent Statistics
    total_consents = serializers.IntegerField()
    active_consents = serializers.IntegerField()
    revoked_consents = serializers.IntegerField()
    expired_consents = serializers.IntegerField()
    expiring_soon = serializers.IntegerField(help_text="Consents expiring within 30 days")
    
    # Consent Request Statistics
    total_requests = serializers.IntegerField()
    pending_requests = serializers.IntegerField()
    approved_requests = serializers.IntegerField()
    rejected_requests = serializers.IntegerField()
    
    # Grievance Statistics
    total_grievances = serializers.IntegerField()
    open_grievances = serializers.IntegerField()
    resolved_grievances = serializers.IntegerField()
    escalated_grievances = serializers.IntegerField()
    sla_breached_grievances = serializers.IntegerField()
    
    # Data Rights Request Statistics
    total_rights_requests = serializers.IntegerField()
    pending_rights_requests = serializers.IntegerField()
    completed_rights_requests = serializers.IntegerField()
    overdue_rights_requests = serializers.IntegerField()
    
    # By Request Type
    access_requests = serializers.IntegerField()
    correction_requests = serializers.IntegerField()
    erasure_requests = serializers.IntegerField()
    portability_requests = serializers.IntegerField()
    
    # User Statistics
    total_principals = serializers.IntegerField()
    total_fiduciaries = serializers.IntegerField()
    
    # Time-based Statistics
    consents_granted_today = serializers.IntegerField()
    consents_revoked_today = serializers.IntegerField()
    grievances_filed_today = serializers.IntegerField()
    grievances_resolved_today = serializers.IntegerField()
    
    # Compliance Score (0-100)
    compliance_score = serializers.IntegerField()
    compliance_factors = serializers.DictField()


# ============================================
# JWT AUTHENTICATION SERIALIZERS
# ============================================
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer that includes user info in response"""
    aadhaar_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims to token
        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = user.full_name or ''
        return token
    
    def validate(self, attrs):
        aadhaar_number = (attrs.pop('aadhaar_number', '') or '').strip()
        data = super().validate(attrs)

        if self.user.role == RoleChoices.PRINCIPAL:
            if not aadhaar_number:
                raise serializers.ValidationError({
                    'aadhaar_number': 'Aadhaar number is required for Data Principal login.'
                })

            if not aadhaar_number.isdigit() or len(aadhaar_number) != 12:
                raise serializers.ValidationError({
                    'aadhaar_number': 'Aadhaar number must be exactly 12 digits.'
                })

            saved_aadhaar = (self.user.aadhaar_number or '').strip()
            if not saved_aadhaar:
                # Backward compatibility for existing principal accounts: bind Aadhaar on first login.
                self.user.aadhaar_number = aadhaar_number
                self.user.save(update_fields=['aadhaar_number'])
                saved_aadhaar = aadhaar_number

            if aadhaar_number != saved_aadhaar:
                raise serializers.ValidationError({
                    'aadhaar_number': 'Aadhaar verification failed.'
                })

        # Add user data to response
        data['user'] = {
            'id': str(self.user.id),
            'email': self.user.email,
            'username': self.user.username,
            'role': self.user.role,
            'role_display': self.user.role_display,
            'full_name': self.user.full_name,
            'organization_name': self.user.organization_name,
            'avatar_url': self.user.avatar_url,
        }
        return data


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration with strong password validation"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    aadhaar_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password_confirm',
            'role', 'full_name', 'aadhaar_number', 'phone', 'organization_name', 'organization_id'
        ]
    
    def validate_password(self, value):
        """Validate password strength using Django's validators"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate_email(self, value):
        """Validate email format and uniqueness"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()
    
    def validate_username(self, value):
        """Validate username"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        # Only allow alphanumeric and underscore
        import re
        if not re.match(r'^[\w]+$', value):
            raise serializers.ValidationError(
                "Username can only contain letters, numbers, and underscores."
            )
        return value

    def validate_aadhaar_number(self, value):
        if not value:
            return value
        aadhaar = value.strip()
        if not aadhaar.isdigit() or len(aadhaar) != 12:
            raise serializers.ValidationError('Aadhaar number must be exactly 12 digits.')
        return aadhaar
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match"})

        if attrs.get('role') == RoleChoices.PRINCIPAL and not attrs.get('aadhaar_number'):
            raise serializers.ValidationError({
                'aadhaar_number': 'Aadhaar number is required for Data Principal registration.'
            })
        
        # Additional validation for fiduciaries
        if attrs.get('role') == RoleChoices.FIDUCIARY:
            if not attrs.get('organization_name'):
                raise serializers.ValidationError({
                    "organization_name": "Organization name is required for fiduciaries"
                })
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change with strong validation"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect")
        return value
    
    def validate_new_password(self, value):
        """Validate new password strength"""
        try:
            validate_password(value, self.context['request'].user)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, attrs):
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError({
                "new_password": "New password must be different from old password"
            })
        return attrs


# ============================================
# NOTIFICATION SERIALIZERS
# ============================================
class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    notification_type_display = serializers.CharField(
        source='get_notification_type_display',
        read_only=True
    )
    priority_display = serializers.CharField(
        source='get_priority_display',
        read_only=True
    )
    user_details = UserMinimalSerializer(source='user', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_details',
            'notification_type', 'notification_type_display',
            'title', 'message',
            'entity_type', 'entity_id',
            'is_read', 'read_at',
            'action_url', 'priority', 'priority_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'notification_type_display', 'priority_display',
            'read_at', 'created_at', 'updated_at'
        ]


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications"""
    
    class Meta:
        model = Notification
        fields = [
            'user', 'notification_type', 'title', 'message',
            'entity_type', 'entity_id', 'action_url', 'priority'
        ]
    
    def validate_user(self, value):
        """Validate user exists"""
        if not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("User does not exist")
        return value
