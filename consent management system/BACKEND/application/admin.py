"""
Django Admin Configuration for DPDPA Consent Management System

Registers all models with the Django admin interface.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Purpose, ConsentRequest, Consent, Grievance, AuditLog,
    DataPrincipalRightsRequest, Notification
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin"""
    list_display = ['email', 'username', 'full_name', 'role', 'organization_name', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['email', 'username', 'full_name', 'organization_name']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('DPDPA Info', {
            'fields': ('role', 'full_name', 'phone', 'address', 'organization_name', 'organization_id', 'avatar_url')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('DPDPA Info', {
            'fields': ('role', 'full_name', 'phone', 'organization_name', 'organization_id')
        }),
    )


@admin.register(Purpose)
class PurposeAdmin(admin.ModelAdmin):
    """Purpose Admin"""
    list_display = ['name', 'fiduciary', 'lawful_basis', 'retention_period_days', 'is_active', 'created_at']
    list_filter = ['is_active', 'lawful_basis']
    search_fields = ['name', 'description', 'fiduciary__organization_name']
    ordering = ['-created_at']


@admin.register(ConsentRequest)
class ConsentRequestAdmin(admin.ModelAdmin):
    """Consent Request Admin"""
    list_display = ['request_id', 'fiduciary', 'principal', 'purpose', 'cms_status', 'status', 'requested_at']
    list_filter = ['cms_status', 'status']
    search_fields = ['request_id', 'fiduciary__organization_name', 'principal__full_name', 'purpose__name']
    ordering = ['-requested_at']
    readonly_fields = ['request_id', 'requested_at']


@admin.register(Consent)
class ConsentAdmin(admin.ModelAdmin):
    """Consent Admin"""
    list_display = ['consent_id', 'principal', 'fiduciary', 'purpose', 'status', 'granted_at', 'expires_at']
    list_filter = ['status']
    search_fields = ['consent_id', 'principal__full_name', 'fiduciary__organization_name']
    ordering = ['-granted_at']
    readonly_fields = ['consent_id', 'granted_at']


@admin.register(Grievance)
class GrievanceAdmin(admin.ModelAdmin):
    """Grievance Admin"""
    list_display = ['grievance_id', 'complainant', 'subject', 'priority', 'status', 'assigned_dpo', 'filed_at']
    list_filter = ['status', 'priority']
    search_fields = ['grievance_id', 'subject', 'complainant__full_name']
    ordering = ['-filed_at']
    readonly_fields = ['grievance_id', 'filed_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Audit Log Admin"""
    list_display = ['log_id', 'user', 'action', 'entity_type', 'entity_id', 'performed_at']
    list_filter = ['action', 'entity_type']
    search_fields = ['log_id', 'user__email', 'entity_id']
    ordering = ['-performed_at']
    readonly_fields = ['log_id', 'performed_at', 'created_at']
    
    def has_change_permission(self, request, obj=None):
        # Audit logs should not be editable
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Audit logs should not be deletable
        return False


@admin.register(DataPrincipalRightsRequest)
class DataPrincipalRightsRequestAdmin(admin.ModelAdmin):
    """Data Principal Rights Request Admin"""
    list_display = [
        'request_id', 'principal', 'request_type', 'status',
        'processed_by', 'sla_deadline', 'submitted_at'
    ]
    list_filter = ['request_type', 'status']
    search_fields = ['request_id', 'principal__full_name', 'principal__email', 'description']
    ordering = ['-submitted_at']
    readonly_fields = ['request_id', 'submitted_at', 'sla_deadline']
    
    fieldsets = (
        ('Request Info', {
            'fields': ('request_id', 'principal', 'fiduciary', 'request_type', 'description')
        }),
        ('Status', {
            'fields': ('status', 'processed_by', 'processed_at', 'response_notes', 'completed_at')
        }),
        ('Data Correction', {
            'fields': ('data_to_correct',),
            'classes': ('collapse',)
        }),
        ('SLA', {
            'fields': ('sla_deadline', 'submitted_at')
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Notification Admin"""
    list_display = [
        'title', 'user', 'notification_type', 'priority',
        'is_read', 'created_at'
    ]
    list_filter = ['notification_type', 'priority', 'is_read']
    search_fields = ['title', 'message', 'user__email', 'user__full_name']
    ordering = ['-created_at']
    readonly_fields = ['read_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Notification Info', {
            'fields': ('user', 'notification_type', 'title', 'message', 'priority')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Related Entity', {
            'fields': ('entity_type', 'entity_id', 'action_url'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
