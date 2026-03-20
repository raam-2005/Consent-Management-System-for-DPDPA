"""
URL Configuration for the application app.

All API endpoints are prefixed with /api/ (configured in project urls.py).
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'purposes', views.PurposeViewSet, basename='purpose')
router.register(r'consent-requests', views.ConsentRequestViewSet, basename='consent-request')
router.register(r'consents', views.ConsentViewSet, basename='consent')
router.register(r'grievances', views.GrievanceViewSet, basename='grievance')
router.register(r'audit-logs', views.AuditLogViewSet, basename='audit-log')
router.register(r'rights-requests', views.DataPrincipalRightsRequestViewSet, basename='rights-request')
router.register(r'notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    # Router URLs (CRUD for all models)
    path('', include(router.urls)),
    
    # ============================================
    # AUTHENTICATION ENDPOINTS
    # ============================================
    path('auth/login/', views.CustomTokenObtainPairView.as_view(), name='token-obtain'),
    path('auth/verify-principal-otp/', views.VerifyPrincipalOtpView.as_view(), name='verify-principal-otp'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/me/', views.CurrentUserView.as_view(), name='current-user'),
    path('auth/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    
    # Dashboard stats
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
    
    # Compliance dashboard (DPDPA)
    path('compliance/dashboard/', views.compliance_dashboard, name='compliance-dashboard'),
    
    # Health check
    path('health/', views.health_check, name='health-check'),
]

"""
API Endpoints Summary:
======================

Health Check:
  GET  /api/health/                                    - API health check

Dashboard:
  GET  /api/dashboard/stats/                           - Get dashboard statistics
       Query params: ?user_id=xxx&role=principal

Compliance Dashboard (DPDPA):
  GET  /api/compliance/dashboard/                      - Get compliance statistics (DPO/Processor only)

Users:
  GET  /api/users/                                     - List all users (paginated)
  POST /api/users/                                     - Create new user
  GET  /api/users/{id}/                                - Get user by ID
  PUT  /api/users/{id}/                                - Update user
  PATCH /api/users/{id}/                               - Partial update user
  DELETE /api/users/{id}/                              - Delete user
  GET  /api/users/role/{role}/                         - Get users by role
  GET  /api/users/principals/                          - Get all data principals
  GET  /api/users/fiduciaries/                         - Get all data fiduciaries

Purposes:
  GET  /api/purposes/                                  - List all purposes (paginated)
  POST /api/purposes/                                  - Create new purpose
  GET  /api/purposes/{id}/                             - Get purpose by ID
  PUT  /api/purposes/{id}/                             - Update purpose
  PATCH /api/purposes/{id}/                            - Partial update purpose
  DELETE /api/purposes/{id}/                           - Delete purpose
  GET  /api/purposes/fiduciary/{id}/                   - Get purposes by fiduciary

Consent Requests:
  GET  /api/consent-requests/                          - List all consent requests
  POST /api/consent-requests/                          - Create new consent request
  GET  /api/consent-requests/{id}/                     - Get consent request by ID
  PATCH /api/consent-requests/{id}/                    - Update consent request
  GET  /api/consent-requests/principal/{id}/           - Get by principal
  GET  /api/consent-requests/fiduciary/{id}/           - Get by fiduciary
  GET  /api/consent-requests/pending_cms/              - Get pending CMS review
  GET  /api/consent-requests/pending_principal/        - Get pending principal response
  POST /api/consent-requests/{id}/cms_approve/         - CMS approves request
  POST /api/consent-requests/{id}/cms_deny/            - CMS denies request
  POST /api/consent-requests/{id}/accept/              - Principal accepts
  POST /api/consent-requests/{id}/reject/              - Principal rejects

Consents:
  GET  /api/consents/                                  - List all consents
  GET  /api/consents/{id}/                             - Get consent by ID
  GET  /api/consents/principal/{id}/                   - Get by principal
  GET  /api/consents/fiduciary/{id}/                   - Get by fiduciary
  GET  /api/consents/active/                           - Get active consents
  POST /api/consents/{id}/revoke/                      - Revoke a consent

Grievances (Enhanced Workflow):
  GET  /api/grievances/                                - List all grievances
  POST /api/grievances/                                - Create new grievance
  GET  /api/grievances/{id}/                           - Get grievance by ID
  PATCH /api/grievances/{id}/                          - Update grievance
  GET  /api/grievances/complainant/{id}/               - Get by complainant
  GET  /api/grievances/dpo/{id}/                       - Get by assigned DPO
  GET  /api/grievances/open/                           - Get open grievances
  GET  /api/grievances/unassigned/                     - Get unassigned grievances (DPO/Processor)
  GET  /api/grievances/sla_breached/                   - Get SLA breached grievances (DPO/Processor)
  GET  /api/grievances/by_status/?status=xxx           - Filter by status
  GET  /api/grievances/by_priority/?priority=xxx       - Filter by priority
  POST /api/grievances/{id}/assign_dpo/                - Assign DPO
  POST /api/grievances/{id}/resolve/                   - Resolve grievance
  POST /api/grievances/{id}/escalate/                  - Escalate grievance (DPO only)
  POST /api/grievances/{id}/close/                     - Close resolved grievance

Data Principal Rights (DPDPA):
  GET  /api/rights-requests/                           - List rights requests
  POST /api/rights-requests/                           - Submit new rights request
  GET  /api/rights-requests/{id}/                      - Get request details
  GET  /api/rights-requests/pending/                   - Get pending requests (DPO/Processor)
  GET  /api/rights-requests/overdue/                   - Get overdue requests (DPO/Processor)
  GET  /api/rights-requests/my-data/                   - Export personal data (Principal)
  POST /api/rights-requests/withdraw-all/              - Withdraw all consents (Principal)
  POST /api/rights-requests/request-erasure/           - Request data erasure (Principal)
  POST /api/rights-requests/{id}/process/              - Start processing (DPO/Processor)
  POST /api/rights-requests/{id}/complete/             - Complete request (DPO/Processor)
  POST /api/rights-requests/{id}/reject/               - Reject request (DPO/Processor)

Audit Logs:
  GET  /api/audit-logs/                                - List all audit logs
  POST /api/audit-logs/                                - Create new audit log
  GET  /api/audit-logs/{id}/                           - Get audit log by ID
  GET  /api/audit-logs/user/{id}/                      - Get by user
  GET  /api/audit-logs/entity/{type}/{id}/             - Get by entity
"""
