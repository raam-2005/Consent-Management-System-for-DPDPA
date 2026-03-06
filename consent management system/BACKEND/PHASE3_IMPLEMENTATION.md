# DPDPA 2023 Consent Management System - Phase 3 Implementation Guide

## Overview

This document provides step-by-step instructions for the Phase 3 implementation of the DPDPA 2023 Consent Management System. All Phase 3 features have been implemented in the Django backend.

---

## What's New in Phase 3

### 1. Audit Logging System ✅

**Location:** `application/audit_utils.py`

A comprehensive audit logging system that tracks:
- User login/logout events
- Consent granted/revoked/expired
- Data access events
- Profile updates
- Grievance actions
- Data rights requests

**Usage Example:**
```python
from application.audit_utils import create_audit_log, log_consent_granted

# Generic logging
create_audit_log(
    request=request,
    action=AuditActionChoices.DATA_ACCESSED,
    entity_type='consent',
    entity_id='uuid-here',
    details={'purpose': 'Marketing'}
)

# Convenience functions
log_consent_granted(request, consent)
log_consent_revoked(request, consent, reason='User requested')
```

---

### 2. Consent Lifecycle Management ✅

**Location:** `application/models.py` (Consent model updated)

New lifecycle states:
```
Requested → Pending CMS → CMS Approved → Active → Withdrawn/Expired
```

**New Fields:**
- `lifecycle_state`: Current state in lifecycle
- `expiry_notified`: Whether user was notified about expiry

**New Methods:**
```python
consent.is_expired        # Check if expired
consent.days_until_expiry # Days remaining
consent.revoke(reason)    # Withdraw consent
consent.expire()          # Mark as expired
Consent.expire_all_overdue()  # Batch expire
```

**Auto-Expiry Management Command:**
```bash
python manage.py expire_consents
python manage.py expire_consents --dry-run  # Preview only
```

---

### 3. Data Principal Rights APIs ✅

**Location:** `application/views.py` (DataPrincipalRightsRequestViewSet)

**Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/rights-requests/` | List rights requests |
| POST | `/api/rights-requests/` | Submit new request |
| GET | `/api/rights-requests/{id}/` | Get request details |
| GET | `/api/rights-requests/my-data/` | Export personal data (Principal) |
| POST | `/api/rights-requests/withdraw-all/` | Withdraw all consents (Principal) |
| POST | `/api/rights-requests/request-erasure/` | Request data erasure (Principal) |
| POST | `/api/rights-requests/{id}/process/` | Start processing (DPO/Processor) |
| POST | `/api/rights-requests/{id}/complete/` | Complete request (DPO/Processor) |
| POST | `/api/rights-requests/{id}/reject/` | Reject request (DPO/Processor) |
| GET | `/api/rights-requests/pending/` | Get pending requests (DPO/Processor) |
| GET | `/api/rights-requests/overdue/` | Get overdue requests (DPO/Processor) |

**Request Types:**
- `access` - Access personal data
- `correction` - Correction of data
- `erasure` - Right to be forgotten
- `portability` - Data portability
- `withdraw_all` - Withdraw all consents

**Example - Export Personal Data:**
```javascript
// Frontend call
const response = await api.get('/rights-requests/my-data/');
// Returns structured JSON with all user data
```

**Example - Withdraw All Consents:**
```javascript
const response = await api.post('/rights-requests/withdraw-all/', {
  reason: 'No longer need the service'
});
```

---

### 4. Grievance Redressal Workflow ✅

**Location:** `application/views.py` (GrievanceViewSet enhanced)

**New Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/grievances/{id}/escalate/` | Escalate grievance (DPO only) |
| POST | `/api/grievances/{id}/close/` | Close resolved grievance |
| GET | `/api/grievances/sla_breached/` | Get SLA breached grievances |
| GET | `/api/grievances/unassigned/` | Get unassigned grievances |
| GET | `/api/grievances/by_status/?status=xxx` | Filter by status |
| GET | `/api/grievances/by_priority/?priority=xxx` | Filter by priority |

**Workflow States:**
```
Open → In Progress → Resolved → Closed
          ↓
       Escalated
```

**New Model Fields:**
- `escalation_reason`: Reason for escalation
- `escalated_at`: Escalation timestamp
- `closed_at`: Closure timestamp
- `sla_breached`: Boolean flag for SLA breach

**SLA Tracking:**
- 30-day deadline as per DPDPA
- `is_overdue` property
- `days_until_sla` property
- Auto-breach marking via `expire_consents` command

---

### 5. Role-Based API Permissions ✅

**Location:** `application/views.py`

**Permission Classes:**
```python
IsPrincipal     # Data Principal only
IsFiduciary     # Data Fiduciary only
IsProcessor     # CMS Processor only
IsDPO           # Data Protection Officer only
IsDPOOrProcessor # DPO or Processor
IsAdminRole     # Admin roles (DPO/Processor)
IsOwnerOrAdmin  # Owner or admin
```

**Access Control by Role:**

| Resource | Principal | Fiduciary | Processor | DPO |
|----------|-----------|-----------|-----------|-----|
| Consents | Own | Own | All | All |
| Consent Requests | Own | Own | All | All |
| Grievances | Own | Own | All | All |
| Rights Requests | Own | Against them | All | All |
| Audit Logs | Own | Own | All | All |
| Compliance Dashboard | ❌ | ❌ | ✅ | ✅ |

---

### 6. Compliance Dashboard & Reports ✅

**Location:** `application/views.py` (compliance_dashboard view)

**Endpoint:** `GET /api/compliance/dashboard/`

**Returns:**
```json
{
  "total_consents": 150,
  "active_consents": 120,
  "revoked_consents": 20,
  "expired_consents": 10,
  "expiring_soon": 15,
  
  "total_grievances": 50,
  "open_grievances": 10,
  "resolved_grievances": 35,
  "escalated_grievances": 3,
  "sla_breached_grievances": 2,
  
  "total_rights_requests": 30,
  "pending_rights_requests": 5,
  "completed_rights_requests": 22,
  "overdue_rights_requests": 3,
  
  "compliance_score": 85,
  "compliance_factors": {
    "grievance_sla": 28.5,
    "rights_processing": 22.0,
    "consent_management": 20.0,
    "grievance_resolution": 14.5
  }
}
```

**Compliance Score Calculation:**
- Grievance SLA compliance (30 points)
- Rights request processing (25 points)
- Consent management (25 points)
- Grievance resolution (20 points)

---

### 7. Security Improvements ✅

**Locations:**
- `application/validators.py` - Input validation
- `consent_backend/settings.py` - Security settings

**Input Validation:**
```python
from application.validators import (
    validate_email_address,
    validate_password_strength,
    validate_phone_number,
    sanitize_text,
    sanitize_html
)

# Example usage
email = validate_email_address(user_input)
password = validate_password_strength(new_password)
```

**Security Features:**
- Strong password validation
- Email validation
- Phone number validation
- JSON depth limiting
- XSS prevention
- SQL injection prevention
- Rate limiting

**Production Security Settings:**
- HTTPS redirect
- HSTS headers
- Secure cookies
- Content security headers
- Rate limiting (100/hour anonymous, 1000/hour authenticated)

---

## Setup Instructions

### Step 1: Run Migrations

```bash
cd BACKEND
python manage.py makemigrations
python manage.py migrate
```

### Step 2: Create Superuser (if needed)

```bash
python manage.py createsuperuser
```

### Step 3: Run Server

```bash
python manage.py runserver
```

### Step 4: Test APIs

Visit `http://localhost:8000/api/` to see all available endpoints.

---

## Scheduled Tasks Setup

### For Consent Expiry and SLA Checks

**Option 1: Manual Run**
```bash
python manage.py expire_consents
```

**Option 2: Windows Task Scheduler**

Create a scheduled task to run daily:
```
Program: python
Arguments: manage.py expire_consents
Start in: C:\path\to\BACKEND
Schedule: Daily at midnight
```

**Option 3: Using Cron (Linux)**
```cron
0 0 * * * cd /path/to/BACKEND && python manage.py expire_consents
```

---

## API Testing Examples

### Test Data Export (Principal)
```bash
curl -X GET http://localhost:8000/api/rights-requests/my-data/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Withdraw All Consents (Principal)
```bash
curl -X POST http://localhost:8000/api/rights-requests/withdraw-all/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "No longer using the service"}'
```

### Get Compliance Dashboard (DPO/Processor)
```bash
curl -X GET http://localhost:8000/api/compliance/dashboard/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Submit Erasure Request (Principal)
```bash
curl -X POST http://localhost:8000/api/rights-requests/request-erasure/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "I want my data deleted"}'
```

### Escalate Grievance (DPO)
```bash
curl -X POST http://localhost:8000/api/grievances/{id}/escalate/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Requires management attention"}'
```

---

## Frontend Integration Guide

### 1. Data Export Page (Principal Dashboard)

```typescript
// services/api.ts
export const exportMyData = async () => {
  const response = await api.get('/rights-requests/my-data/');
  return response.data;
};

// Page component
const handleExport = async () => {
  const data = await exportMyData();
  // Trigger download
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'my-data-export.json';
  a.click();
};
```

### 2. Compliance Dashboard (DPO/Processor Dashboard)

```typescript
// services/api.ts
export const getComplianceDashboard = async () => {
  const response = await api.get('/compliance/dashboard/');
  return response.data;
};

// Use in component
const [stats, setStats] = useState(null);
useEffect(() => {
  getComplianceDashboard().then(setStats);
}, []);
```

### 3. Rights Requests Management

```typescript
// services/api.ts
export const submitRightsRequest = async (type: string, data: any) => {
  return api.post('/rights-requests/', { request_type: type, ...data });
};

export const processRightsRequest = async (id: string) => {
  return api.post(`/rights-requests/${id}/process/`);
};

export const completeRightsRequest = async (id: string, notes: string) => {
  return api.post(`/rights-requests/${id}/complete/`, { response_notes: notes });
};
```

---

## Database Schema Changes

### New Model: DataPrincipalRightsRequest

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| request_id | String | Human-readable ID (DPR-YYYYMMDD-XXXX) |
| principal | FK(User) | User making the request |
| fiduciary | FK(User) | Optional - against which organization |
| request_type | Choice | access/correction/erasure/portability/withdraw_all |
| description | Text | Request details |
| data_to_correct | JSON | For correction requests |
| status | Choice | pending/in_progress/completed/rejected/partially_completed |
| processed_by | FK(User) | DPO/Processor handling the request |
| processed_at | DateTime | When processing started |
| response_notes | Text | Response/resolution notes |
| exported_data_url | URL | For portability - download link |
| sla_deadline | DateTime | 30 days from submission |
| submitted_at | DateTime | Submission timestamp |
| completed_at | DateTime | Completion timestamp |

### Updated Model: Consent

New fields:
- `lifecycle_state`: ConsentLifecycleChoices
- `expiry_notified`: Boolean

### Updated Model: Grievance

New fields:
- `escalation_reason`: Text
- `escalated_at`: DateTime
- `closed_at`: DateTime
- `sla_breached`: Boolean

---

## Files Modified/Created

### New Files:
1. `application/audit_utils.py` - Audit logging utilities
2. `application/validators.py` - Input validation
3. `application/management/commands/expire_consents.py` - Auto-expiry command

### Modified Files:
1. `application/models.py` - New DataPrincipalRightsRequest model, enhanced Consent and Grievance
2. `application/serializers.py` - New serializers for rights requests, updated existing
3. `application/views.py` - New DataPrincipalRightsRequestViewSet, compliance_dashboard, enhanced GrievanceViewSet
4. `application/urls.py` - New routes for rights requests and compliance dashboard
5. `application/admin.py` - Admin for DataPrincipalRightsRequest
6. `consent_backend/settings.py` - Security settings, logging, rate limiting

---

## Testing Checklist

- [ ] Run migrations successfully
- [ ] Create test users (Principal, Fiduciary, DPO, Processor)
- [ ] Test consent lifecycle (grant → active → expire)
- [ ] Test data export endpoint
- [ ] Test withdraw all consents
- [ ] Test erasure request workflow
- [ ] Test grievance escalation
- [ ] Test compliance dashboard access control
- [ ] Test rate limiting
- [ ] Run expire_consents command
- [ ] Verify audit logs are created

---

## Next Steps (Recommended)

1. **Frontend Pages to Add:**
   - Data Rights Request page for Principals
   - Compliance Dashboard page for DPO/Processor
   - Enhanced Grievance management with escalation

2. **Email Notifications (Future):**
   - Consent expiry reminders
   - Rights request status updates
   - SLA breach alerts

3. **Reports Export (Future):**
   - PDF compliance reports
   - CSV data exports

---

## Support

For issues or questions about this implementation:
1. Check the API documentation at `/api/`
2. Review the audit logs for debugging
3. Use the Django admin at `/admin/` for data management
