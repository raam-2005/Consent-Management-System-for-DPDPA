"""
URL Configuration for DPDPA Consent Management System Backend

The `urlpatterns` list routes URLs to views.

API endpoints are available at:
  http://localhost:8000/api/

Admin interface:
  http://localhost:8000/admin/
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API endpoints (all under /api/)
    path('api/', include('application.urls')),
    
    # DRF browsable API auth (optional, for development)
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
