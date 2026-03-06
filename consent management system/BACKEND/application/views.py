"""
Django REST Framework Views for DPDPA Consent Management System

Provides CRUD APIs for all models:
- Users (with role-based filtering)
- Purposes
- Consent Requests (with CMS workflow)
- Consents
- Grievances
- Audit Logs
- Dashboard Statistics
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes as perm_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta

from .models import (
    User, Purpose, ConsentRequest, Consent, Grievance, AuditLog,
    RoleChoices, ConsentStatusChoices, CMSStatusChoices,
    GrievanceStatusChoices, AuditActionChoices,
    DataRightsRequestTypeChoices, DataRightsRequestStatusChoices,
    ConsentLifecycleChoices
)
from .models import DataPrincipalRightsRequest
from .serializers import (
    UserSerializer, UserCreateSerializer, UserMinimalSerializer,
    PurposeSerializer,
    ConsentRequestSerializer, ConsentRequestCreateSerializer,
    ConsentSerializer,
    GrievanceSerializer, GrievanceCreateSerializer,
    AuditLogSerializer, AuditLogCreateSerializer,
    DataPrincipalRightsRequestSerializer, DataPrincipalRightsRequestCreateSerializer,
    DataExportSerializer,
    DashboardStatsSerializer, ComplianceDashboardSerializer
)
from .audit_utils import (
    create_audit_log, log_consent_granted, log_consent_revoked,
    log_data_accessed, log_data_corrected, log_data_deleted,
    log_grievance_raised, log_grievance_resolved, log_profile_updated
)


# ============================================
# ROLE-BASED PERMISSION CLASSES
# ============================================
class IsPrincipal(BasePermission):
    """Only allows access to Data Principals"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == RoleChoices.PRINCIPAL


class IsFiduciary(BasePermission):
    """Only allows access to Data Fiduciaries"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == RoleChoices.FIDUCIARY


class IsProcessor(BasePermission):
    """Only allows access to Consent Managers/Processors"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == RoleChoices.PROCESSOR


class IsDPO(BasePermission):
    """Only allows access to Data Protection Officers"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == RoleChoices.DPO


class IsDPOOrProcessor(BasePermission):
    """Allows access to DPO or Consent Manager"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            RoleChoices.DPO, RoleChoices.PROCESSOR
        ]


class IsAdminRole(BasePermission):
    """Allows access to admin roles (DPO or Processor)"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in [RoleChoices.DPO, RoleChoices.PROCESSOR]


class IsOwnerOrAdmin(BasePermission):
    """Allows access to resource owner or admin roles"""
    def has_object_permission(self, request, view, obj):
        if request.user.role in [RoleChoices.DPO, RoleChoices.PROCESSOR]:
            return True
        if hasattr(obj, 'principal') and obj.principal == request.user:
            return True
        if hasattr(obj, 'fiduciary') and obj.fiduciary == request.user:
            return True
        if hasattr(obj, 'complainant') and obj.complainant == request.user:
            return True
        return False


# ============================================
# USER VIEWSET
# ============================================
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Users.
    
    GET /api/users/ - List all users (Admin only)
    POST /api/users/ - Create new user (Public for registration)
    GET /api/users/{id}/ - Get user by ID
    PATCH /api/users/{id}/ - Update user
    DELETE /api/users/{id}/ - Delete user (Admin only)
    
    Custom actions:
    GET /api/users/role/{role}/ - Get users by role
    GET /api/users/principals/ - Get all principals
    GET /api/users/fiduciaries/ - Get all fiduciaries
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """Allow registration without auth, protect other actions"""
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_queryset(self):
        """Filter users based on role"""
        user = self.request.user
        if not user.is_authenticated:
            return User.objects.none()
        # Admins see all users
        if user.role in [RoleChoices.DPO, RoleChoices.PROCESSOR]:
            return User.objects.all()
        # Others see only themselves
        return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get'], url_path='role/(?P<role>[^/.]+)')
    def by_role(self, request, role=None):
        """Get users by role"""
        users = User.objects.filter(role=role)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def principals(self, request):
        """Get all data principals"""
        users = User.objects.filter(role=RoleChoices.PRINCIPAL)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def fiduciaries(self, request):
        """Get all data fiduciaries"""
        users = User.objects.filter(role=RoleChoices.FIDUCIARY)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


# ============================================
# PURPOSE VIEWSET
# ============================================
class PurposeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Purposes.
    
    GET /api/purposes/ - List all purposes
    POST /api/purposes/ - Create new purpose (Fiduciary only)
    GET /api/purposes/{id}/ - Get purpose by ID
    PATCH /api/purposes/{id}/ - Update purpose (Owner or Admin)
    DELETE /api/purposes/{id}/ - Delete purpose (Admin only)
    
    Custom actions:
    GET /api/purposes/fiduciary/{id}/ - Get purposes by fiduciary
    """
    queryset = Purpose.objects.all()
    serializer_class = PurposeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter purposes based on user role"""
        user = self.request.user
        if not user.is_authenticated:
            return Purpose.objects.none()
        # Admins see all
        if user.role in [RoleChoices.DPO, RoleChoices.PROCESSOR]:
            return Purpose.objects.all()
        # Fiduciaries see their own purposes
        if user.role == RoleChoices.FIDUCIARY:
            return Purpose.objects.filter(fiduciary=user)
        # Principals see all active purposes
        return Purpose.objects.filter(is_active=True)
    
    def perform_create(self, serializer):
        """Auto-assign fiduciary to current user if fiduciary role"""
        if self.request.user.role == RoleChoices.FIDUCIARY:
            serializer.save(fiduciary=self.request.user)
        else:
            serializer.save()
    
    @action(detail=False, methods=['get'], url_path='fiduciary/(?P<fiduciary_id>[^/.]+)')
    def by_fiduciary(self, request, fiduciary_id=None):
        """Get purposes by fiduciary"""
        purposes = Purpose.objects.filter(fiduciary_id=fiduciary_id)
        serializer = PurposeSerializer(purposes, many=True)
        return Response(serializer.data)


# ============================================
# CONSENT REQUEST VIEWSET
# ============================================
class ConsentRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Consent Requests.
    
    Role-based access:
    - Principal: See only their consent requests
    - Fiduciary: See requests they created
    - Processor: See all for CMS review
    - DPO: Full access
    
    Workflow Actions:
    POST /api/consent-requests/{id}/cms_approve/ - CMS approves (Processor/DPO)
    POST /api/consent-requests/{id}/cms_deny/ - CMS denies (Processor/DPO)
    POST /api/consent-requests/{id}/accept/ - Principal accepts
    POST /api/consent-requests/{id}/reject/ - Principal rejects
    """
    queryset = ConsentRequest.objects.all()
    serializer_class = ConsentRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ConsentRequestCreateSerializer
        return ConsentRequestSerializer
    
    def get_queryset(self):
        """Filter based on user role"""
        user = self.request.user
        if not user.is_authenticated:
            return ConsentRequest.objects.none()
        # Admins see all
        if user.role in [RoleChoices.DPO, RoleChoices.PROCESSOR]:
            return ConsentRequest.objects.all()
        # Fiduciaries see their requests
        if user.role == RoleChoices.FIDUCIARY:
            return ConsentRequest.objects.filter(fiduciary=user)
        # Principals see requests to them
        return ConsentRequest.objects.filter(principal=user)
    
    @action(detail=False, methods=['get'], url_path='principal/(?P<principal_id>[^/.]+)')
    def by_principal(self, request, principal_id=None):
        """Get consent requests by principal"""
        requests = ConsentRequest.objects.filter(principal_id=principal_id)
        serializer = ConsentRequestSerializer(requests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='fiduciary/(?P<fiduciary_id>[^/.]+)')
    def by_fiduciary(self, request, fiduciary_id=None):
        """Get consent requests by fiduciary"""
        requests = ConsentRequest.objects.filter(fiduciary_id=fiduciary_id)
        serializer = ConsentRequestSerializer(requests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending_cms(self, request):
        """Get consent requests pending CMS review (Processor/DPO only)"""
        if request.user.role not in [RoleChoices.PROCESSOR, RoleChoices.DPO]:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        requests = ConsentRequest.objects.filter(cms_status=CMSStatusChoices.PENDING_CMS)
        serializer = ConsentRequestSerializer(requests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending_principal(self, request):
        """Get consent requests pending principal response (CMS approved)"""
        requests = ConsentRequest.objects.filter(
            cms_status=CMSStatusChoices.CMS_APPROVED,
            status=ConsentStatusChoices.PENDING
        )
        # Filter by principal if they're a principal
        if request.user.role == RoleChoices.PRINCIPAL:
            requests = requests.filter(principal=request.user)
        serializer = ConsentRequestSerializer(requests, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cms_approve(self, request, pk=None):
        """CMS approves a consent request (Processor/DPO only)"""
        if request.user.role not in [RoleChoices.PROCESSOR, RoleChoices.DPO]:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        consent_request = self.get_object()
        
        if consent_request.cms_status != CMSStatusChoices.PENDING_CMS:
            return Response(
                {'error': 'Request has already been reviewed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        consent_request.cms_status = CMSStatusChoices.CMS_APPROVED
        consent_request.cms_reviewed_at = timezone.now()
        consent_request.cms_reviewed_by_id = request.data.get('reviewer_id')
        consent_request.cms_notes = request.data.get('notes', '')
        consent_request.save()
        
        # Create audit log
        AuditLog.objects.create(
            user_id=request.data.get('reviewer_id'),
            action='consent_granted',
            entity_type='consent_request',
            entity_id=str(consent_request.id),
            details={'action': 'cms_approved', 'notes': consent_request.cms_notes}
        )
        
        serializer = ConsentRequestSerializer(consent_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cms_deny(self, request, pk=None):
        """CMS denies a consent request"""
        consent_request = self.get_object()
        
        if consent_request.cms_status != CMSStatusChoices.PENDING_CMS:
            return Response(
                {'error': 'Request has already been reviewed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        consent_request.cms_status = CMSStatusChoices.CMS_DENIED
        consent_request.status = ConsentStatusChoices.REJECTED
        consent_request.cms_reviewed_at = timezone.now()
        consent_request.cms_reviewed_by_id = request.data.get('reviewer_id')
        consent_request.cms_notes = request.data.get('notes', '')
        consent_request.responded_at = timezone.now()
        consent_request.save()
        
        # Create audit log
        AuditLog.objects.create(
            user_id=request.data.get('reviewer_id'),
            action='consent_rejected',
            entity_type='consent_request',
            entity_id=str(consent_request.id),
            details={'action': 'cms_denied', 'notes': consent_request.cms_notes}
        )
        
        serializer = ConsentRequestSerializer(consent_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Principal accepts a consent request"""
        consent_request = self.get_object()
        
        if consent_request.cms_status != CMSStatusChoices.CMS_APPROVED:
            return Response(
                {'error': 'Request not yet approved by CMS'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if consent_request.status != ConsentStatusChoices.PENDING:
            return Response(
                {'error': 'Request has already been responded to'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update consent request
        consent_request.status = ConsentStatusChoices.ACTIVE
        consent_request.responded_at = timezone.now()
        consent_request.save()
        
        # Create Consent record
        consent = Consent.objects.create(
            consent_request=consent_request,
            principal=consent_request.principal,
            fiduciary=consent_request.fiduciary,
            purpose=consent_request.purpose,
            data_categories=consent_request.data_requested,
            status=ConsentStatusChoices.ACTIVE,
            expires_at=consent_request.expires_at
        )
        
        # Create audit log
        AuditLog.objects.create(
            user=consent_request.principal,
            action=AuditActionChoices.CONSENT_GRANTED,
            entity_type='consent',
            entity_id=str(consent.id),
            details={'consent_request_id': str(consent_request.id)}
        )
        
        serializer = ConsentRequestSerializer(consent_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Principal rejects a consent request"""
        consent_request = self.get_object()
        
        if consent_request.cms_status != CMSStatusChoices.CMS_APPROVED:
            return Response(
                {'error': 'Request not yet approved by CMS'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if consent_request.status != ConsentStatusChoices.PENDING:
            return Response(
                {'error': 'Request has already been responded to'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        consent_request.status = ConsentStatusChoices.REJECTED
        consent_request.responded_at = timezone.now()
        consent_request.save()
        
        # Create audit log
        AuditLog.objects.create(
            user=consent_request.principal,
            action=AuditActionChoices.CONSENT_REJECTED,
            entity_type='consent_request',
            entity_id=str(consent_request.id),
            details={'reason': 'Principal rejected'}
        )
        
        serializer = ConsentRequestSerializer(consent_request)
        return Response(serializer.data)


# ============================================
# CONSENT VIEWSET
# ============================================
class ConsentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Consents.
    
    Role-based access:
    - Principal: See only their consents, can revoke
    - Fiduciary: See consents they hold
    - Processor/DPO: Full access
    
    Custom actions:
    GET /api/consents/active/ - Get active consents
    POST /api/consents/{id}/revoke/ - Revoke a consent (Principal only)
    """
    queryset = Consent.objects.all()
    serializer_class = ConsentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']  # No PUT/PATCH/DELETE
    
    def get_queryset(self):
        """Filter based on user role"""
        user = self.request.user
        if not user.is_authenticated:
            return Consent.objects.none()
        # Admins see all
        if user.role in [RoleChoices.DPO, RoleChoices.PROCESSOR]:
            return Consent.objects.all()
        # Fiduciaries see their consents
        if user.role == RoleChoices.FIDUCIARY:
            return Consent.objects.filter(fiduciary=user)
        # Principals see their consents
        return Consent.objects.filter(principal=user)
    
    @action(detail=False, methods=['get'], url_path='principal/(?P<principal_id>[^/.]+)')
    def by_principal(self, request, principal_id=None):
        """Get consents by principal"""
        consents = self.queryset.filter(principal_id=principal_id)
        serializer = ConsentSerializer(consents, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='fiduciary/(?P<fiduciary_id>[^/.]+)')
    def by_fiduciary(self, request, fiduciary_id=None):
        """Get consents by fiduciary"""
        consents = self.queryset.filter(fiduciary_id=fiduciary_id)
        serializer = ConsentSerializer(consents, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active consents"""
        consents = self.queryset.filter(status=ConsentStatusChoices.ACTIVE)
        serializer = ConsentSerializer(consents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke a consent"""
        consent = self.get_object()
        
        if consent.status != ConsentStatusChoices.ACTIVE:
            return Response(
                {'error': 'Consent is not active'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', '')
        consent.revoke(reason=reason)
        
        # Update consent request status
        consent.consent_request.status = ConsentStatusChoices.REVOKED
        consent.consent_request.save()
        
        # Create audit log
        AuditLog.objects.create(
            user=consent.principal,
            action=AuditActionChoices.CONSENT_REVOKED,
            entity_type='consent',
            entity_id=str(consent.id),
            details={'reason': reason}
        )
        
        serializer = ConsentSerializer(consent)
        return Response(serializer.data)


# ============================================
# GRIEVANCE VIEWSET
# ============================================
class GrievanceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Grievances.
    
    Role-based access:
    - Principal/Fiduciary: See only their grievances
    - DPO: Manage all grievances, assign, resolve
    - Processor: View all grievances
    
    Actions:
    POST /api/grievances/{id}/assign_dpo/ - Assign DPO (DPO only)
    POST /api/grievances/{id}/resolve/ - Resolve grievance (DPO only)
    """
    queryset = Grievance.objects.all()
    serializer_class = GrievanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return GrievanceCreateSerializer
        return GrievanceSerializer
    
    def get_queryset(self):
        """Filter based on user role"""
        user = self.request.user
        if not user.is_authenticated:
            return Grievance.objects.none()
        # DPO sees all
        if user.role == RoleChoices.DPO:
            return Grievance.objects.all()
        # Processor sees all
        if user.role == RoleChoices.PROCESSOR:
            return Grievance.objects.all()
        # Others see only their grievances
        return Grievance.objects.filter(complainant=user)
    
    def perform_create(self, serializer):
        # Auto-assign complainant to current user
        grievance = serializer.save(complainant=self.request.user)
        # Create audit log
        AuditLog.objects.create(
            user=grievance.complainant,
            action=AuditActionChoices.GRIEVANCE_RAISED,
            entity_type='grievance',
            entity_id=str(grievance.id),
            details={'subject': grievance.subject}
        )
    
    @action(detail=False, methods=['get'], url_path='complainant/(?P<complainant_id>[^/.]+)')
    def by_complainant(self, request, complainant_id=None):
        """Get grievances by complainant"""
        grievances = Grievance.objects.filter(complainant_id=complainant_id)
        serializer = GrievanceSerializer(grievances, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='dpo/(?P<dpo_id>[^/.]+)')
    def by_dpo(self, request, dpo_id=None):
        """Get grievances assigned to a DPO"""
        grievances = self.queryset.filter(assigned_dpo_id=dpo_id)
        serializer = GrievanceSerializer(grievances, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def open(self, request):
        """Get all open grievances"""
        grievances = self.queryset.filter(
            status__in=[
                GrievanceStatusChoices.OPEN,
                GrievanceStatusChoices.IN_PROGRESS,
                GrievanceStatusChoices.ESCALATED
            ]
        )
        serializer = GrievanceSerializer(grievances, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign_dpo(self, request, pk=None):
        """Assign a DPO to a grievance"""
        grievance = self.get_object()
        dpo_id = request.data.get('dpo_id')
        
        if not dpo_id:
            return Response(
                {'error': 'dpo_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        grievance.assigned_dpo_id = dpo_id
        grievance.status = GrievanceStatusChoices.IN_PROGRESS
        grievance.acknowledged_at = timezone.now()
        grievance.save()
        
        serializer = GrievanceSerializer(grievance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve a grievance"""
        grievance = self.get_object()
        resolution = request.data.get('resolution', '')
        
        if not resolution:
            return Response(
                {'error': 'resolution is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        grievance.resolve(resolution)
        
        # Create audit log
        log_grievance_resolved(request, grievance)
        
        serializer = GrievanceSerializer(grievance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def escalate(self, request, pk=None):
        """Escalate a grievance (DPO only)"""
        if request.user.role != RoleChoices.DPO:
            return Response({'error': 'Only DPO can escalate grievances'}, status=status.HTTP_403_FORBIDDEN)
        
        grievance = self.get_object()
        reason = request.data.get('reason', '')
        
        if not reason:
            return Response(
                {'error': 'escalation reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        grievance.escalate(reason)
        
        # Create audit log
        create_audit_log(
            request=request,
            action=AuditActionChoices.GRIEVANCE_ESCALATED,
            entity_type='grievance',
            entity_id=str(grievance.id),
            details={'reason': reason}
        )
        
        serializer = GrievanceSerializer(grievance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close a resolved grievance"""
        grievance = self.get_object()
        
        if grievance.status != GrievanceStatusChoices.RESOLVED:
            return Response(
                {'error': 'Only resolved grievances can be closed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        grievance.close()
        
        serializer = GrievanceSerializer(grievance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def sla_breached(self, request):
        """Get all grievances with SLA breach"""
        if request.user.role not in [RoleChoices.DPO, RoleChoices.PROCESSOR]:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        grievances = Grievance.objects.filter(sla_breached=True)
        serializer = GrievanceSerializer(grievances, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unassigned(self, request):
        """Get all unassigned grievances"""
        if request.user.role not in [RoleChoices.DPO, RoleChoices.PROCESSOR]:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        grievances = Grievance.objects.filter(
            assigned_dpo__isnull=True,
            status=GrievanceStatusChoices.OPEN
        )
        serializer = GrievanceSerializer(grievances, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Get grievances filtered by status"""
        status_filter = request.query_params.get('status', '')
        if not status_filter:
            return Response(
                {'error': 'status query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        grievances = self.get_queryset().filter(status=status_filter)
        serializer = GrievanceSerializer(grievances, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_priority(self, request):
        """Get grievances filtered by priority"""
        priority = request.query_params.get('priority', '')
        if not priority:
            return Response(
                {'error': 'priority query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        grievances = self.get_queryset().filter(priority=priority)
        serializer = GrievanceSerializer(grievances, many=True)
        return Response(serializer.data)


# ============================================
# AUDIT LOG VIEWSET
# ============================================
class AuditLogViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Audit Logs.
    
    Role-based access:
    - DPO/Processor: Full access
    - Others: See only their logs
    
    Custom actions:
    GET /api/audit-logs/user/{id}/ - Get by user
    GET /api/audit-logs/entity/{type}/{id}/ - Get by entity
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']  # No UPDATE/DELETE for audit logs
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AuditLogCreateSerializer
        return AuditLogSerializer
    
    def get_queryset(self):
        """Filter based on user role"""
        user = self.request.user
        if not user.is_authenticated:
            return AuditLog.objects.none()
        # Admins see all
        if user.role in [RoleChoices.DPO, RoleChoices.PROCESSOR]:
            return AuditLog.objects.all()
        # Others see only their logs
        return AuditLog.objects.filter(user=user)
    
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        """Get audit logs by user"""
        logs = AuditLog.objects.filter(user_id=user_id)
        serializer = AuditLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='entity/(?P<entity_type>[^/.]+)/(?P<entity_id>[^/.]+)')
    def by_entity(self, request, entity_type=None, entity_id=None):
        """Get audit logs by entity"""
        logs = AuditLog.objects.filter(entity_type=entity_type, entity_id=entity_id)
        serializer = AuditLogSerializer(logs, many=True)
        return Response(serializer.data)


# ============================================
# DATA PRINCIPAL RIGHTS REQUEST VIEWSET
# ============================================
class DataPrincipalRightsRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Data Principal Rights Requests (DPDPA 2023).
    
    Rights supported:
    - Access: Request access to personal data
    - Correction: Request correction of personal data
    - Erasure: Right to be forgotten
    - Portability: Export personal data
    - Withdraw All: Withdraw all consents
    
    Role-based access:
    - Principal: Create and view their requests
    - DPO/Processor: Process requests
    
    Endpoints:
    GET /api/rights-requests/ - List requests (filtered by role)
    POST /api/rights-requests/ - Submit new request (Principal)
    GET /api/rights-requests/{id}/ - Get request details
    POST /api/rights-requests/{id}/process/ - Process request (DPO/Processor)
    POST /api/rights-requests/{id}/complete/ - Complete request (DPO/Processor)
    POST /api/rights-requests/{id}/reject/ - Reject request (DPO/Processor)
    GET /api/rights-requests/my-data/ - Export personal data (Principal)
    POST /api/rights-requests/withdraw-all/ - Withdraw all consents (Principal)
    POST /api/rights-requests/request-erasure/ - Request data erasure (Principal)
    """
    queryset = DataPrincipalRightsRequest.objects.all()
    serializer_class = DataPrincipalRightsRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DataPrincipalRightsRequestCreateSerializer
        return DataPrincipalRightsRequestSerializer
    
    def get_queryset(self):
        """Filter based on user role"""
        user = self.request.user
        if not user.is_authenticated:
            return DataPrincipalRightsRequest.objects.none()
        # Admins see all
        if user.role in [RoleChoices.DPO, RoleChoices.PROCESSOR]:
            return DataPrincipalRightsRequest.objects.all()
        # Fiduciaries see requests against them
        if user.role == RoleChoices.FIDUCIARY:
            return DataPrincipalRightsRequest.objects.filter(fiduciary=user)
        # Principals see their own requests
        return DataPrincipalRightsRequest.objects.filter(principal=user)
    
    def perform_create(self, serializer):
        """Create rights request and log it"""
        request_obj = serializer.save(principal=self.request.user)
        create_audit_log(
            request=self.request,
            action=AuditActionChoices.RIGHTS_REQUEST_SUBMITTED,
            entity_type='rights_request',
            entity_id=str(request_obj.id),
            details={
                'request_type': request_obj.request_type,
                'request_id': request_obj.request_id
            }
        )
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Mark request as in-progress (DPO/Processor)"""
        if request.user.role not in [RoleChoices.DPO, RoleChoices.PROCESSOR]:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        rights_request = self.get_object()
        
        if rights_request.status != DataRightsRequestStatusChoices.PENDING:
            return Response(
                {'error': 'Request is not in pending status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rights_request.status = DataRightsRequestStatusChoices.IN_PROGRESS
        rights_request.processed_by = request.user
        rights_request.processed_at = timezone.now()
        rights_request.save()
        
        serializer = DataPrincipalRightsRequestSerializer(rights_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a rights request (DPO/Processor)"""
        if request.user.role not in [RoleChoices.DPO, RoleChoices.PROCESSOR]:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        rights_request = self.get_object()
        response_notes = request.data.get('response_notes', '')
        
        rights_request.status = DataRightsRequestStatusChoices.COMPLETED
        rights_request.response_notes = response_notes
        rights_request.completed_at = timezone.now()
        if not rights_request.processed_by:
            rights_request.processed_by = request.user
            rights_request.processed_at = timezone.now()
        rights_request.save()
        
        # Create audit log
        create_audit_log(
            request=request,
            action=AuditActionChoices.RIGHTS_REQUEST_COMPLETED,
            entity_type='rights_request',
            entity_id=str(rights_request.id),
            details={
                'request_type': rights_request.request_type,
                'request_id': rights_request.request_id,
                'response_notes': response_notes
            }
        )
        
        serializer = DataPrincipalRightsRequestSerializer(rights_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a rights request (DPO/Processor)"""
        if request.user.role not in [RoleChoices.DPO, RoleChoices.PROCESSOR]:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        rights_request = self.get_object()
        reason = request.data.get('reason', '')
        
        if not reason:
            return Response(
                {'error': 'Rejection reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rights_request.status = DataRightsRequestStatusChoices.REJECTED
        rights_request.response_notes = reason
        rights_request.completed_at = timezone.now()
        if not rights_request.processed_by:
            rights_request.processed_by = request.user
            rights_request.processed_at = timezone.now()
        rights_request.save()
        
        serializer = DataPrincipalRightsRequestSerializer(rights_request)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_data(self, request):
        """
        Export personal data for the current user (Data Portability).
        Returns all data associated with the user in a structured format.
        """
        user = request.user
        
        # Collect all user data
        export_data = {
            'user_profile': {
                'id': str(user.id),
                'email': user.email,
                'username': user.username,
                'full_name': user.full_name,
                'phone': user.phone,
                'address': user.address,
                'role': user.role,
                'organization_name': user.organization_name,
                'organization_id': user.organization_id,
                'created_at': user.created_at.isoformat() if user.created_at else None,
            },
            'consents': [],
            'consent_requests': [],
            'grievances': [],
            'audit_logs': [],
            'exported_at': timezone.now().isoformat(),
            'export_format': 'json'
        }
        
        # Get consents (Principal)
        if user.role == RoleChoices.PRINCIPAL:
            consents = Consent.objects.filter(principal=user)
            for consent in consents:
                export_data['consents'].append({
                    'consent_id': consent.consent_id,
                    'fiduciary': consent.fiduciary.organization_name or consent.fiduciary.email,
                    'purpose': consent.purpose.name,
                    'data_categories': consent.data_categories,
                    'status': consent.status,
                    'granted_at': consent.granted_at.isoformat() if consent.granted_at else None,
                    'expires_at': consent.expires_at.isoformat() if consent.expires_at else None,
                    'revoked_at': consent.revoked_at.isoformat() if consent.revoked_at else None,
                })
            
            # Get consent requests
            consent_requests = ConsentRequest.objects.filter(principal=user)
            for req in consent_requests:
                export_data['consent_requests'].append({
                    'request_id': req.request_id,
                    'fiduciary': req.fiduciary.organization_name or req.fiduciary.email,
                    'purpose': req.purpose.name,
                    'status': req.status,
                    'cms_status': req.cms_status,
                    'requested_at': req.requested_at.isoformat() if req.requested_at else None,
                    'responded_at': req.responded_at.isoformat() if req.responded_at else None,
                })
            
            # Get grievances
            grievances = Grievance.objects.filter(complainant=user)
            for grvnc in grievances:
                export_data['grievances'].append({
                    'grievance_id': grvnc.grievance_id,
                    'subject': grvnc.subject,
                    'description': grvnc.description,
                    'status': grvnc.status,
                    'filed_at': grvnc.filed_at.isoformat() if grvnc.filed_at else None,
                    'resolved_at': grvnc.resolved_at.isoformat() if grvnc.resolved_at else None,
                })
        
        # Get audit logs for user
        audit_logs = AuditLog.objects.filter(user=user).order_by('-performed_at')[:100]
        for log in audit_logs:
            export_data['audit_logs'].append({
                'log_id': log.log_id,
                'action': log.action,
                'entity_type': log.entity_type,
                'performed_at': log.performed_at.isoformat() if log.performed_at else None,
            })
        
        # Create audit log for data access
        log_data_accessed(
            request=request,
            user=user,
            data_type='personal_data_export',
            entity_id=str(user.id),
            details={'export_type': 'full_data_export'}
        )
        
        return Response(export_data)
    
    @action(detail=False, methods=['post'])
    def withdraw_all(self, request):
        """
        Withdraw all active consents for the current user.
        Creates a rights request and revokes all consents.
        """
        if request.user.role != RoleChoices.PRINCIPAL:
            return Response(
                {'error': 'Only principals can withdraw consents'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = request.user
        reason = request.data.get('reason', 'User requested withdrawal of all consents')
        
        # Get all active consents
        active_consents = Consent.objects.filter(
            principal=user,
            status=ConsentStatusChoices.ACTIVE
        )
        
        count = active_consents.count()
        
        if count == 0:
            return Response({
                'message': 'No active consents to withdraw',
                'revoked_count': 0
            })
        
        # Revoke all consents
        for consent in active_consents:
            consent.revoke(reason=reason)
            log_consent_revoked(request, consent, reason)
        
        # Create rights request record
        rights_request = DataPrincipalRightsRequest.objects.create(
            principal=user,
            request_type=DataRightsRequestTypeChoices.WITHDRAW_ALL,
            description=reason,
            status=DataRightsRequestStatusChoices.COMPLETED,
            completed_at=timezone.now(),
            response_notes=f'Successfully withdrew {count} consent(s)'
        )
        
        return Response({
            'message': f'Successfully withdrew {count} consent(s)',
            'revoked_count': count,
            'request_id': rights_request.request_id
        })
    
    @action(detail=False, methods=['post'])
    def request_erasure(self, request):
        """
        Request erasure of personal data (Right to be forgotten).
        Creates a rights request that must be processed by DPO.
        """
        if request.user.role != RoleChoices.PRINCIPAL:
            return Response(
                {'error': 'Only principals can request erasure'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = request.user
        fiduciary_id = request.data.get('fiduciary_id')
        reason = request.data.get('reason', '')
        
        # Create erasure request
        rights_request = DataPrincipalRightsRequest.objects.create(
            principal=user,
            fiduciary_id=fiduciary_id if fiduciary_id else None,
            request_type=DataRightsRequestTypeChoices.ERASURE,
            description=reason,
            status=DataRightsRequestStatusChoices.PENDING
        )
        
        create_audit_log(
            request=request,
            action=AuditActionChoices.RIGHTS_REQUEST_SUBMITTED,
            entity_type='rights_request',
            entity_id=str(rights_request.id),
            details={
                'request_type': 'erasure',
                'request_id': rights_request.request_id
            }
        )
        
        serializer = DataPrincipalRightsRequestSerializer(rights_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending rights requests (DPO/Processor only)"""
        if request.user.role not in [RoleChoices.DPO, RoleChoices.PROCESSOR]:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        requests = DataPrincipalRightsRequest.objects.filter(
            status=DataRightsRequestStatusChoices.PENDING
        )
        serializer = DataPrincipalRightsRequestSerializer(requests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue rights requests (past SLA deadline)"""
        if request.user.role not in [RoleChoices.DPO, RoleChoices.PROCESSOR]:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        now = timezone.now()
        requests = DataPrincipalRightsRequest.objects.filter(
            sla_deadline__lt=now
        ).exclude(
            status__in=[
                DataRightsRequestStatusChoices.COMPLETED,
                DataRightsRequestStatusChoices.REJECTED
            ]
        )
        serializer = DataPrincipalRightsRequestSerializer(requests, many=True)
        return Response(serializer.data)


# ============================================
# COMPLIANCE DASHBOARD VIEW
# ============================================
@api_view(['GET'])
@perm_classes([IsAuthenticated])
def compliance_dashboard(request):
    """
    Get comprehensive compliance dashboard statistics.
    
    GET /api/compliance/dashboard/
    
    Returns statistics for DPDPA compliance monitoring:
    - Consent statistics (active, revoked, expired)
    - Grievance statistics (open, resolved, SLA breached)
    - Data rights request statistics
    - Compliance score
    
    Only accessible by DPO and Processor roles.
    """
    user = request.user
    
    # Only DPO and Processor can access compliance dashboard
    if user.role not in [RoleChoices.DPO, RoleChoices.PROCESSOR]:
        return Response(
            {'error': 'Access denied. Only DPO and Processors can view compliance dashboard.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    now = timezone.now()
    today = now.date()
    thirty_days_from_now = now + timedelta(days=30)
    
    # Consent Statistics
    total_consents = Consent.objects.count()
    active_consents = Consent.objects.filter(status=ConsentStatusChoices.ACTIVE).count()
    revoked_consents = Consent.objects.filter(status=ConsentStatusChoices.REVOKED).count()
    expired_consents = Consent.objects.filter(status=ConsentStatusChoices.EXPIRED).count()
    expiring_soon = Consent.objects.filter(
        status=ConsentStatusChoices.ACTIVE,
        expires_at__lte=thirty_days_from_now,
        expires_at__gt=now
    ).count()
    
    # Consent Request Statistics
    total_requests = ConsentRequest.objects.count()
    pending_requests = ConsentRequest.objects.filter(status=ConsentStatusChoices.PENDING).count()
    approved_requests = ConsentRequest.objects.filter(status=ConsentStatusChoices.ACTIVE).count()
    rejected_requests = ConsentRequest.objects.filter(status=ConsentStatusChoices.REJECTED).count()
    
    # Grievance Statistics
    total_grievances = Grievance.objects.count()
    open_grievances = Grievance.objects.filter(
        status__in=[GrievanceStatusChoices.OPEN, GrievanceStatusChoices.IN_PROGRESS]
    ).count()
    resolved_grievances = Grievance.objects.filter(status=GrievanceStatusChoices.RESOLVED).count()
    escalated_grievances = Grievance.objects.filter(status=GrievanceStatusChoices.ESCALATED).count()
    sla_breached_grievances = Grievance.objects.filter(sla_breached=True).count()
    
    # Data Rights Request Statistics
    total_rights_requests = DataPrincipalRightsRequest.objects.count()
    pending_rights_requests = DataPrincipalRightsRequest.objects.filter(
        status=DataRightsRequestStatusChoices.PENDING
    ).count()
    completed_rights_requests = DataPrincipalRightsRequest.objects.filter(
        status=DataRightsRequestStatusChoices.COMPLETED
    ).count()
    overdue_rights_requests = DataPrincipalRightsRequest.objects.filter(
        sla_deadline__lt=now
    ).exclude(
        status__in=[
            DataRightsRequestStatusChoices.COMPLETED,
            DataRightsRequestStatusChoices.REJECTED
        ]
    ).count()
    
    # By Request Type
    access_requests = DataPrincipalRightsRequest.objects.filter(
        request_type=DataRightsRequestTypeChoices.ACCESS
    ).count()
    correction_requests = DataPrincipalRightsRequest.objects.filter(
        request_type=DataRightsRequestTypeChoices.CORRECTION
    ).count()
    erasure_requests = DataPrincipalRightsRequest.objects.filter(
        request_type=DataRightsRequestTypeChoices.ERASURE
    ).count()
    portability_requests = DataPrincipalRightsRequest.objects.filter(
        request_type=DataRightsRequestTypeChoices.PORTABILITY
    ).count()
    
    # User Statistics
    total_principals = User.objects.filter(role=RoleChoices.PRINCIPAL).count()
    total_fiduciaries = User.objects.filter(role=RoleChoices.FIDUCIARY).count()
    
    # Time-based Statistics
    consents_granted_today = Consent.objects.filter(granted_at__date=today).count()
    consents_revoked_today = Consent.objects.filter(revoked_at__date=today).count()
    grievances_filed_today = Grievance.objects.filter(filed_at__date=today).count()
    grievances_resolved_today = Grievance.objects.filter(resolved_at__date=today).count()
    
    # Calculate Compliance Score (0-100)
    compliance_factors = {}
    
    # Factor 1: SLA compliance for grievances (weight: 30)
    if total_grievances > 0:
        grievance_sla_compliance = ((total_grievances - sla_breached_grievances) / total_grievances) * 30
    else:
        grievance_sla_compliance = 30
    compliance_factors['grievance_sla'] = round(grievance_sla_compliance, 1)
    
    # Factor 2: Rights request processing (weight: 25)
    if total_rights_requests > 0:
        rights_completion_rate = (completed_rights_requests / total_rights_requests) * 25
        if overdue_rights_requests > 0:
            rights_completion_rate -= (overdue_rights_requests / total_rights_requests) * 10
    else:
        rights_completion_rate = 25
    compliance_factors['rights_processing'] = max(0, round(rights_completion_rate, 1))
    
    # Factor 3: Consent management (weight: 25)
    if total_consents > 0:
        active_ratio = (active_consents / total_consents) * 15
        expired_penalty = (expired_consents / total_consents) * 5  # Penalty for expired
    else:
        active_ratio = 15
        expired_penalty = 0
    consent_score = 25 - expired_penalty + (active_ratio / 15 * 10)
    compliance_factors['consent_management'] = max(0, round(min(25, consent_score), 1))
    
    # Factor 4: Grievance resolution (weight: 20)
    if total_grievances > 0:
        resolution_rate = (resolved_grievances / total_grievances) * 20
        escalation_penalty = (escalated_grievances / total_grievances) * 5
    else:
        resolution_rate = 20
        escalation_penalty = 0
    grievance_score = resolution_rate - escalation_penalty
    compliance_factors['grievance_resolution'] = max(0, round(grievance_score, 1))
    
    compliance_score = sum(compliance_factors.values())
    
    stats = {
        'total_consents': total_consents,
        'active_consents': active_consents,
        'revoked_consents': revoked_consents,
        'expired_consents': expired_consents,
        'expiring_soon': expiring_soon,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
        'total_grievances': total_grievances,
        'open_grievances': open_grievances,
        'resolved_grievances': resolved_grievances,
        'escalated_grievances': escalated_grievances,
        'sla_breached_grievances': sla_breached_grievances,
        'total_rights_requests': total_rights_requests,
        'pending_rights_requests': pending_rights_requests,
        'completed_rights_requests': completed_rights_requests,
        'overdue_rights_requests': overdue_rights_requests,
        'access_requests': access_requests,
        'correction_requests': correction_requests,
        'erasure_requests': erasure_requests,
        'portability_requests': portability_requests,
        'total_principals': total_principals,
        'total_fiduciaries': total_fiduciaries,
        'consents_granted_today': consents_granted_today,
        'consents_revoked_today': consents_revoked_today,
        'grievances_filed_today': grievances_filed_today,
        'grievances_resolved_today': grievances_resolved_today,
        'compliance_score': round(compliance_score),
        'compliance_factors': compliance_factors,
    }
    
    serializer = ComplianceDashboardSerializer(stats)
    return Response(serializer.data)


# ============================================
# DASHBOARD STATS VIEW
# ============================================
@api_view(['GET'])
@perm_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Get dashboard statistics based on authenticated user's role.
    
    GET /api/dashboard/stats/
    Query params:
    - user_id: Filter stats for specific user (optional, defaults to current user)
    - role: Filter stats by role (optional, defaults to current user's role)
    """
    # Use current user if not specified
    user = request.user
    user_id = request.query_params.get('user_id', str(user.id))
    role = request.query_params.get('role', user.role)
    
    # Base stats
    stats = {
        'total_consents': Consent.objects.count(),
        'active_consents': Consent.objects.filter(status=ConsentStatusChoices.ACTIVE).count(),
        'pending_requests': ConsentRequest.objects.filter(status=ConsentStatusChoices.PENDING).count(),
        'revoked_consents': Consent.objects.filter(status=ConsentStatusChoices.REVOKED).count(),
        'open_grievances': Grievance.objects.filter(
            status__in=[
                GrievanceStatusChoices.OPEN,
                GrievanceStatusChoices.IN_PROGRESS,
                GrievanceStatusChoices.ESCALATED
            ]
        ).count(),
    }
    
    # Role-specific stats
    if user_id:
        if role == 'principal':
            stats['my_active_consents'] = Consent.objects.filter(
                principal_id=user_id, status=ConsentStatusChoices.ACTIVE
            ).count()
            stats['my_pending_requests'] = ConsentRequest.objects.filter(
                principal_id=user_id,
                cms_status=CMSStatusChoices.CMS_APPROVED,
                status=ConsentStatusChoices.PENDING
            ).count()
            stats['my_grievances'] = Grievance.objects.filter(complainant_id=user_id).count()
        
        elif role == 'fiduciary':
            stats['my_consent_requests'] = ConsentRequest.objects.filter(fiduciary_id=user_id).count()
            stats['my_active_consents'] = Consent.objects.filter(
                fiduciary_id=user_id, status=ConsentStatusChoices.ACTIVE
            ).count()
        
        elif role == 'processor':
            stats['pending_cms_review'] = ConsentRequest.objects.filter(
                cms_status=CMSStatusChoices.PENDING_CMS
            ).count()
            stats['pending_cms_reviews'] = stats['pending_cms_review']
            today = timezone.now().date()
            stats['approved_today'] = ConsentRequest.objects.filter(
                cms_status=CMSStatusChoices.CMS_APPROVED,
                cms_reviewed_at__date=today
            ).count()
        
        elif role == 'dpo':
            stats['assigned_grievances'] = Grievance.objects.filter(assigned_dpo_id=user_id).count()
            stats['unassigned_grievances'] = Grievance.objects.filter(assigned_dpo__isnull=True).count()
            stats['total_principals'] = User.objects.filter(role=RoleChoices.PRINCIPAL).count()
            stats['total_fiduciaries'] = User.objects.filter(role=RoleChoices.FIDUCIARY).count()
    
    serializer = DashboardStatsSerializer(stats)
    return Response(serializer.data)


# ============================================
# HEALTH CHECK VIEW
# ============================================
@api_view(['GET'])
def health_check(request):
    """
    API Health Check endpoint.
    
    GET /api/health/
    """
    return Response({
        'status': 'healthy',
        'message': 'DPDPA Consent Management API is running',
        'timestamp': timezone.now().isoformat()
    })


# ============================================
# AUTHENTICATION VIEWS
# ============================================
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from .serializers import (
    CustomTokenObtainPairSerializer, RegisterSerializer, ChangePasswordSerializer
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom login view that returns JWT tokens + user data.
    
    POST /api/auth/login/
    Body: { "email": "user@example.com", "password": "password" }
    Response: { "access": "...", "refresh": "...", "user": {...} }
    """
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(APIView):
    """
    User registration endpoint.
    
    POST /api/auth/register/
    Body: { "email": "...", "username": "...", "password": "...", "password_confirm": "...", "role": "..." }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User registered successfully',
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'username': user.username,
                    'role': user.role,
                    'full_name': user.full_name,
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserView(APIView):
    """
    Get current authenticated user's profile.
    
    GET /api/auth/me/
    Requires: Bearer token
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    def patch(self, request):
        """Update current user's profile"""
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """
    Change password for authenticated user.
    
    POST /api/auth/change-password/
    Body: { "old_password": "...", "new_password": "..." }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({'message': 'Password changed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
