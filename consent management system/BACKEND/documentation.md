# DPDPA Consent Management System - Backend Documentation

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture](#architecture)
4. [Database Models](#database-models)
5. [User Roles & Permissions](#user-roles--permissions)
6. [API Endpoints](#api-endpoints)
7. [Authentication System](#authentication-system)
8. [Workflows](#workflows)
9. [Setup & Installation](#setup--installation)
10. [Configuration](#configuration)

---

## Project Overview

The **DPDPA Consent Management System** is a Django-based backend API designed to comply with India's **Digital Personal Data Protection Act, 2023 (DPDPA)**. It provides a complete solution for managing consent between Data Principals (individuals) and Data Fiduciaries (organizations).

### Key Features

- ✅ **Role-Based Access Control (RBAC)** - Four distinct user roles with specific permissions
- ✅ **JWT Authentication** - Secure token-based authentication with refresh tokens
- ✅ **Consent Workflow** - Multi-step consent request and approval process
- ✅ **CMS Review** - Consent Management System review before principal notification
- ✅ **Grievance Management** - DPDPA-compliant grievance handling with 30-day SLA
- ✅ **Audit Logging** - Complete audit trail of all system actions
- ✅ **RESTful API** - Well-structured REST API for frontend integration

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | Django | 4.2.x |
| **API** | Django REST Framework | 3.14+ |
| **Authentication** | SimpleJWT | 5.3+ |
| **Database** | SQLite (Dev) / PostgreSQL (Prod) | - |
| **CORS** | django-cors-headers | 4.3+ |
| **Environment** | python-dotenv | 1.0+ |

### Dependencies (requirements.txt)

```
Django>=4.2,<5.0
djangorestframework>=3.14.0
djangorestframework-simplejwt>=5.3.0
django-cors-headers>=4.3.0
python-dotenv>=1.0.0
```

---

## Architecture

### Project Structure

```
BACKEND/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── db.sqlite3                   # SQLite database (development)
├── .env                         # Environment variables
│
├── consent_backend/             # Django project settings
│   ├── __init__.py
│   ├── settings.py              # Configuration settings
│   ├── urls.py                  # Root URL configuration
│   └── wsgi.py                  # WSGI entry point
│
└── application/                 # Main application
    ├── __init__.py
    ├── admin.py                 # Django admin configuration
    ├── apps.py                  # App configuration
    ├── models.py                # Database models (6 models)
    ├── serializers.py           # DRF serializers (15+ serializers)
    ├── views.py                 # API views & viewsets (6 viewsets + 4 views)
    ├── urls.py                  # API URL routing
    ├── migrations/              # Database migrations
    └── management/
        └── commands/
            └── seed_data.py     # Database seeding command
```

### Request Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│    CORS     │────▶│    JWT      │────▶│   Views     │
│   (React)   │     │  Middleware │     │    Auth     │     │  (ViewSets) │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                    │
                    ┌─────────────┐     ┌─────────────┐     ┌──────▼──────┐
                    │   Response  │◀────│ Serializers │◀────│   Models    │
                    │   (JSON)    │     │             │     │  (Database) │
                    └─────────────┘     └─────────────┘     └─────────────┘
```

---

## Database Models

### Entity Relationship Diagram

```
┌────────────────┐       ┌────────────────┐       ┌────────────────┐
│     User       │       │    Purpose     │       │ ConsentRequest │
├────────────────┤       ├────────────────┤       ├────────────────┤
│ id (UUID)      │       │ id (UUID)      │       │ id (UUID)      │
│ email          │◀──────│ fiduciary (FK) │       │ request_id     │
│ username       │       │ name           │◀──────│ purpose (FK)   │
│ role           │       │ description    │       │ fiduciary (FK) │──▶
│ full_name      │       │ data_categories│       │ principal (FK) │──▶
│ phone          │       │ lawful_basis   │       │ cms_status     │
│ organization   │       │ retention_days │       │ status         │
└────────────────┘       └────────────────┘       └────────────────┘
        │                                                  │
        │                                                  │
        ▼                                                  ▼
┌────────────────┐       ┌────────────────┐       ┌────────────────┐
│    Consent     │       │   Grievance    │       │   AuditLog     │
├────────────────┤       ├────────────────┤       ├────────────────┤
│ id (UUID)      │       │ id (UUID)      │       │ id (UUID)      │
│ consent_id     │       │ grievance_id   │       │ log_id         │
│ consent_request│       │ complainant    │       │ user (FK)      │
│ principal (FK) │◀──────│ against_entity │       │ action         │
│ fiduciary (FK) │       │ assigned_dpo   │       │ entity_type    │
│ purpose (FK)   │       │ subject        │       │ entity_id      │
│ status         │       │ status         │       │ details (JSON) │
│ granted_at     │       │ resolution     │       │ performed_at   │
└────────────────┘       └────────────────┘       └────────────────┘
```

### Model Details

#### 1. User Model

Custom user model extending Django's `AbstractUser` with DPDPA-specific fields.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key (auto-generated) |
| `email` | EmailField | Unique email address (login field) |
| `username` | CharField | Username |
| `role` | CharField | User role (principal/fiduciary/processor/dpo) |
| `full_name` | CharField | Full name |
| `phone` | CharField | Phone number |
| `address` | TextField | Address |
| `organization_name` | CharField | Organization name (for fiduciaries) |
| `organization_id` | CharField | CIN/Registration number |
| `avatar_url` | URLField | Profile picture URL |
| `created_at` | DateTime | Record creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

#### 2. Purpose Model

Defines the purpose for which personal data is collected.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `name` | CharField | Purpose name |
| `description` | TextField | Detailed description |
| `fiduciary` | ForeignKey | Organization that created this purpose |
| `data_categories` | JSONField | List of data types: `['name', 'email', 'phone']` |
| `lawful_basis` | CharField | Legal basis (consent/contract/legal obligation) |
| `retention_period_days` | Integer | Data retention period in days |
| `is_active` | Boolean | Whether purpose is active |

#### 3. ConsentRequest Model

Represents a consent request from a Fiduciary to a Principal.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `request_id` | CharField | Auto-generated: `CR-YYYYMMDD-XXXX` |
| `fiduciary` | ForeignKey | Organization requesting consent |
| `principal` | ForeignKey | Individual being requested |
| `purpose` | ForeignKey | Purpose for data collection |
| `data_requested` | JSONField | List of data fields requested |
| `notes` | TextField | Additional notes |
| `cms_status` | CharField | CMS review status |
| `cms_reviewed_by` | ForeignKey | Processor who reviewed |
| `cms_reviewed_at` | DateTime | Review timestamp |
| `cms_notes` | TextField | CMS reviewer notes |
| `status` | CharField | Principal response status |
| `requested_at` | DateTime | When request was created |
| `responded_at` | DateTime | When principal responded |
| `expires_at` | DateTime | Consent expiry date |

**CMS Status Choices:**
- `pending_cms` - Pending CMS review
- `cms_approved` - Approved by CMS
- `cms_denied` - Denied by CMS

**Consent Status Choices:**
- `pending` - Awaiting principal response
- `active` - Consent granted
- `revoked` - Consent revoked by principal
- `expired` - Consent expired
- `rejected` - Rejected by principal

#### 4. Consent Model

Represents an active consent granted by a Principal.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `consent_id` | CharField | Auto-generated: `CON-YYYYMMDD-XXXX` |
| `consent_request` | OneToOneField | Link to original request |
| `principal` | ForeignKey | Individual who granted consent |
| `fiduciary` | ForeignKey | Organization holding consent |
| `purpose` | ForeignKey | Purpose of consent |
| `data_categories` | JSONField | Consented data categories |
| `status` | CharField | Current status (active/revoked/expired) |
| `granted_at` | DateTime | When consent was granted |
| `expires_at` | DateTime | Expiry date |
| `revoked_at` | DateTime | When revoked (if applicable) |
| `revocation_reason` | TextField | Reason for revocation |

#### 5. Grievance Model

Handles complaints filed by Data Principals.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `grievance_id` | CharField | Auto-generated: `GRV-YYYYMMDD-XXXX` |
| `complainant` | ForeignKey | User filing the complaint |
| `against_entity` | ForeignKey | Fiduciary being complained against |
| `assigned_dpo` | ForeignKey | DPO handling the grievance |
| `subject` | CharField | Grievance subject |
| `description` | TextField | Detailed description |
| `category` | CharField | Category (consent/data_access/data_deletion) |
| `priority` | CharField | Priority level (low/medium/high/critical) |
| `status` | CharField | Current status |
| `resolution` | TextField | Resolution details |
| `filed_at` | DateTime | Filing timestamp |
| `acknowledged_at` | DateTime | When DPO acknowledged |
| `resolved_at` | DateTime | Resolution timestamp |
| `sla_deadline` | DateTime | Auto-set: 30 days from filing (DPDPA requirement) |

**Grievance Status Choices:**
- `open` - Newly filed
- `in_progress` - Being investigated
- `resolved` - Resolution provided
- `escalated` - Escalated to higher authority
- `closed` - Grievance closed

#### 6. AuditLog Model

Complete audit trail of all system actions (DPDPA compliance requirement).

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `log_id` | CharField | Auto-generated: `LOG-YYYYMMDD-XXXXXX` |
| `user` | ForeignKey | User who performed action |
| `action` | CharField | Type of action performed |
| `entity_type` | CharField | Model name (consent/grievance/etc.) |
| `entity_id` | CharField | ID of affected entity |
| `details` | JSONField | Additional context |
| `ip_address` | GenericIPAddress | Request IP |
| `user_agent` | TextField | Browser/client info |
| `performed_at` | DateTime | Action timestamp |

**Auditable Actions:**
- `login` / `logout` - Authentication events
- `consent_granted` / `consent_revoked` / `consent_rejected`
- `data_accessed` / `data_corrected` / `data_deleted`
- `grievance_raised` / `grievance_resolved`
- `profile_updated`

---

## User Roles & Permissions

### Role Hierarchy

```
┌─────────────────────────────────────────────────────────────────────┐
│                     DATA PROTECTION OFFICER (DPO)                   │
│  • Full system access                                               │
│  • Manage all grievances                                            │
│  • View all audit logs                                              │
│  • Compliance oversight                                             │
└─────────────────────────────────────────────────────────────────────┘
                                    │
┌───────────────────────────────────┼───────────────────────────────────┐
│                                   │                                   │
▼                                   ▼                                   ▼
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────────────┐
│    PROCESSOR      │  │    FIDUCIARY      │  │       PRINCIPAL           │
│   (CMS Staff)     │  │  (Organization)   │  │      (Individual)         │
├───────────────────┤  ├───────────────────┤  ├───────────────────────────┤
│ • Review consent  │  │ • Create purposes │  │ • View own consents       │
│   requests        │  │ • Send consent    │  │ • Accept/reject requests  │
│ • Approve/deny    │  │   requests        │  │ • Revoke consents         │
│ • View audit logs │  │ • View own        │  │ • File grievances         │
│ • View all data   │  │   consents        │  │ • View own audit logs     │
└───────────────────┘  └───────────────────┘  └───────────────────────────┘
```

### Permission Classes

```python
# Role-based permission classes in views.py

class IsPrincipal(BasePermission):
    """Only allows access to Data Principals"""

class IsFiduciary(BasePermission):
    """Only allows access to Data Fiduciaries"""

class IsProcessor(BasePermission):
    """Only allows access to CMS Processors"""

class IsDPO(BasePermission):
    """Only allows access to Data Protection Officers"""

class IsDPOOrProcessor(BasePermission):
    """Allows access to DPO or Processor"""

class IsAdminRole(BasePermission):
    """Allows access to admin roles (DPO or Processor)"""

class IsOwnerOrAdmin(BasePermission):
    """Allows access to resource owner or admin roles"""
```

### Data Visibility by Role

| Data | Principal | Fiduciary | Processor | DPO |
|------|:---------:|:---------:|:---------:|:---:|
| Own Profile | ✅ | ✅ | ✅ | ✅ |
| All Users | ❌ | ❌ | ✅ | ✅ |
| Own Consents | ✅ | ✅ | - | - |
| All Consents | ❌ | ❌ | ✅ | ✅ |
| Own Grievances | ✅ | ✅ | - | - |
| All Grievances | ❌ | ❌ | ✅ | ✅ |
| Own Audit Logs | ✅ | ✅ | - | - |
| All Audit Logs | ❌ | ❌ | ✅ | ✅ |
| CMS Review | ❌ | ❌ | ✅ | ✅ |

---

## API Endpoints

### Base URL
```
http://localhost:8000/api/
```

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|:-------------:|
| POST | `/auth/login/` | Login with email/password | ❌ |
| POST | `/auth/refresh/` | Refresh access token | ❌ (needs refresh token) |
| POST | `/auth/register/` | Register new user | ❌ |
| GET | `/auth/me/` | Get current user profile | ✅ |
| PATCH | `/auth/me/` | Update current user profile | ✅ |
| POST | `/auth/change-password/` | Change password | ✅ |

### User Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|:-------------:|
| GET | `/users/` | List all users | ✅ |
| POST | `/users/` | Create new user | ❌ |
| GET | `/users/{id}/` | Get user by ID | ✅ |
| PATCH | `/users/{id}/` | Update user | ✅ |
| DELETE | `/users/{id}/` | Delete user | ✅ (Admin) |
| GET | `/users/role/{role}/` | Get users by role | ✅ |
| GET | `/users/principals/` | Get all principals | ✅ |
| GET | `/users/fiduciaries/` | Get all fiduciaries | ✅ |

### Purpose Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|:-------------:|
| GET | `/purposes/` | List all purposes | ✅ |
| POST | `/purposes/` | Create new purpose | ✅ (Fiduciary) |
| GET | `/purposes/{id}/` | Get purpose by ID | ✅ |
| PATCH | `/purposes/{id}/` | Update purpose | ✅ (Owner/Admin) |
| DELETE | `/purposes/{id}/` | Delete purpose | ✅ (Admin) |
| GET | `/purposes/fiduciary/{id}/` | Get by fiduciary | ✅ |

### Consent Request Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|:-------------:|
| GET | `/consent-requests/` | List consent requests | ✅ |
| POST | `/consent-requests/` | Create new request | ✅ (Fiduciary) |
| GET | `/consent-requests/{id}/` | Get request by ID | ✅ |
| PATCH | `/consent-requests/{id}/` | Update request | ✅ |
| GET | `/consent-requests/principal/{id}/` | Get by principal | ✅ |
| GET | `/consent-requests/fiduciary/{id}/` | Get by fiduciary | ✅ |
| GET | `/consent-requests/pending_cms/` | Get pending CMS review | ✅ (Processor/DPO) |
| GET | `/consent-requests/pending_principal/` | Get pending principal response | ✅ |
| POST | `/consent-requests/{id}/cms_approve/` | CMS approves | ✅ (Processor/DPO) |
| POST | `/consent-requests/{id}/cms_deny/` | CMS denies | ✅ (Processor/DPO) |
| POST | `/consent-requests/{id}/accept/` | Principal accepts | ✅ (Principal) |
| POST | `/consent-requests/{id}/reject/` | Principal rejects | ✅ (Principal) |

### Consent Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|:-------------:|
| GET | `/consents/` | List all consents | ✅ |
| GET | `/consents/{id}/` | Get consent by ID | ✅ |
| GET | `/consents/principal/{id}/` | Get by principal | ✅ |
| GET | `/consents/fiduciary/{id}/` | Get by fiduciary | ✅ |
| GET | `/consents/active/` | Get active consents | ✅ |
| POST | `/consents/{id}/revoke/` | Revoke consent | ✅ (Principal) |

### Grievance Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|:-------------:|
| GET | `/grievances/` | List grievances | ✅ |
| POST | `/grievances/` | Create grievance | ✅ |
| GET | `/grievances/{id}/` | Get grievance by ID | ✅ |
| PATCH | `/grievances/{id}/` | Update grievance | ✅ |
| GET | `/grievances/complainant/{id}/` | Get by complainant | ✅ |
| GET | `/grievances/dpo/{id}/` | Get by assigned DPO | ✅ |
| GET | `/grievances/open/` | Get open grievances | ✅ |
| POST | `/grievances/{id}/assign_dpo/` | Assign DPO | ✅ (DPO) |
| POST | `/grievances/{id}/resolve/` | Resolve grievance | ✅ (DPO) |

### Audit Log Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|:-------------:|
| GET | `/audit-logs/` | List audit logs | ✅ |
| POST | `/audit-logs/` | Create audit log | ✅ |
| GET | `/audit-logs/{id}/` | Get log by ID | ✅ |
| GET | `/audit-logs/user/{id}/` | Get by user | ✅ |
| GET | `/audit-logs/entity/{type}/{id}/` | Get by entity | ✅ |

### Dashboard & Health Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|:-------------:|
| GET | `/dashboard/stats/` | Get dashboard statistics | ✅ |
| GET | `/health/` | API health check | ❌ |

---

## Authentication System

### JWT Token Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                           JWT AUTHENTICATION FLOW                     │
└──────────────────────────────────────────────────────────────────────┘

1. LOGIN
   ┌─────────┐   POST /auth/login/    ┌─────────┐
   │ Frontend│ ────────────────────▶  │ Backend │
   │         │   {email, password}    │         │
   │         │ ◀────────────────────  │         │
   │         │   {access, refresh,    │         │
   │         │    user}               │         │
   └─────────┘                        └─────────┘

2. API REQUEST (with access token)
   ┌─────────┐   GET /api/consents/   ┌─────────┐
   │ Frontend│ ────────────────────▶  │ Backend │
   │         │   Authorization:       │         │
   │         │   Bearer <access>      │         │
   │         │ ◀────────────────────  │         │
   │         │   {data}               │         │
   └─────────┘                        └─────────┘

3. TOKEN REFRESH (when access token expires)
   ┌─────────┐   POST /auth/refresh/  ┌─────────┐
   │ Frontend│ ────────────────────▶  │ Backend │
   │         │   {refresh}            │         │
   │         │ ◀────────────────────  │         │
   │         │   {access, refresh}    │         │
   └─────────┘                        └─────────┘
```

### Token Configuration

```python
# settings.py - SIMPLE_JWT Configuration

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),      # Access token: 1 hour
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),      # Refresh token: 7 days
    'ROTATE_REFRESH_TOKENS': True,                    # New refresh on use
    'BLACKLIST_AFTER_ROTATION': True,                 # Invalidate old tokens
    'UPDATE_LAST_LOGIN': True,                        # Track last login
    'ALGORITHM': 'HS256',                             # Signing algorithm
    'AUTH_HEADER_TYPES': ('Bearer',),                 # Header format
}
```

### Login Request/Response

**Request:**
```json
POST /api/auth/login/
Content-Type: application/json

{
    "email": "principal@example.com",
    "password": "password123"
}
```

**Response:**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": "uuid-here",
        "email": "principal@example.com",
        "username": "principal",
        "role": "principal",
        "role_display": "Data Principal",
        "full_name": "Demo Principal",
        "organization_name": null,
        "avatar_url": null
    }
}
```

### Registration Request/Response

**Request:**
```json
POST /api/auth/register/
Content-Type: application/json

{
    "email": "newuser@example.com",
    "username": "newuser",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "role": "principal",
    "full_name": "New User",
    "phone": "+91-9876543210"
}
```

**Response:**
```json
{
    "message": "User registered successfully",
    "user": {
        "id": "uuid-here",
        "email": "newuser@example.com",
        "username": "newuser",
        "role": "principal",
        "full_name": "New User"
    }
}
```

---

## Workflows

### 1. Consent Request Workflow

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        CONSENT REQUEST WORKFLOW                             │
└────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │   FIDUCIARY     │
                    │ Creates Request │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  cms_status =   │
                    │  pending_cms    │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
    ┌─────────────────┐           ┌─────────────────┐
    │   PROCESSOR     │           │   PROCESSOR     │
    │   Approves      │           │   Denies        │
    │                 │           │                 │
    │ POST /cms_      │           │ POST /cms_deny/ │
    │ approve/        │           │                 │
    └────────┬────────┘           └────────┬────────┘
             │                             │
             ▼                             ▼
    ┌─────────────────┐           ┌─────────────────┐
    │  cms_status =   │           │  cms_status =   │
    │  cms_approved   │           │  cms_denied     │
    │                 │           │  status =       │
    │  status =       │           │  rejected       │
    │  pending        │           │                 │
    └────────┬────────┘           └─────────────────┘
             │                            END
             │
   ┌─────────┴─────────┐
   │                   │
   ▼                   ▼
┌──────────────┐  ┌──────────────┐
│  PRINCIPAL   │  │  PRINCIPAL   │
│  Accepts     │  │  Rejects     │
│              │  │              │
│ POST /accept/│  │ POST /reject/│
└──────┬───────┘  └──────┬───────┘
       │                 │
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│  status =    │  │  status =    │
│  active      │  │  rejected    │
│              │  │              │
│  + Consent   │  │              │
│    Created   │  │              │
└──────────────┘  └──────────────┘
      END               END
```

### 2. Grievance Workflow

```
┌────────────────────────────────────────────────────────────────────────────┐
│                          GRIEVANCE WORKFLOW                                 │
└────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│   PRINCIPAL     │
│ Files Grievance │
│                 │
│ POST /grievances│
└────────┬────────┘
         │
         ▼
┌─────────────────┐      Auto-set:
│  status = open  │◀─────sla_deadline = 30 days
│                 │      (DPDPA requirement)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│      DPO        │
│  Assigns Self   │
│                 │
│ POST /assign_   │
│ dpo/            │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  status =       │
│  in_progress    │
│                 │
│  acknowledged   │
│  _at = now()    │
└────────┬────────┘
         │
    Investigation
         │
         ▼
┌─────────────────┐
│      DPO        │
│  Resolves       │
│                 │
│ POST /resolve/  │
│ {resolution}    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  status =       │
│  resolved       │
│                 │
│  resolved_at =  │
│  now()          │
└─────────────────┘
        END
```

### 3. Consent Revocation Workflow

```
┌────────────────────────────────────────────────────────────────────────────┐
│                       CONSENT REVOCATION WORKFLOW                           │
└────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│   PRINCIPAL     │
│ Revokes Consent │
│                 │
│ POST /consents/ │
│ {id}/revoke/    │
│ {reason}        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Consent:       │
│  status =       │
│  revoked        │
│                 │
│  revoked_at =   │
│  now()          │
│                 │
│  revocation_    │
│  reason = ...   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ConsentRequest: │
│  status =       │
│  revoked        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AuditLog:      │
│  action =       │
│ consent_revoked │
└─────────────────┘
        END
```

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- pip (Python package manager)
- Virtual environment (recommended)

### Step-by-Step Installation

```bash
# 1. Navigate to backend directory
cd BACKEND

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env file (copy from .env.example)
cp .env.example .env

# 6. Run migrations
python manage.py migrate

# 7. Seed demo data (optional but recommended)
python manage.py seed_data

# 8. Start development server
python manage.py runserver 0.0.0.0:8000
```

### Demo Accounts

After running `seed_data`, these accounts are available:

| Role | Email | Password |
|------|-------|----------|
| Principal | principal@example.com | password123 |
| Fiduciary | fiduciary@example.com | password123 |
| Processor | processor@example.com | password123 |
| DPO | dpo@example.com | password123 |

---

## Configuration

### Environment Variables (.env)

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional - defaults to SQLite)
# DATABASE_URL=postgres://user:password@localhost:5432/dpdpa_db
```

### CORS Configuration (settings.py)

```python
# For development - allow all origins
CORS_ALLOW_ALL_ORIGINS = True

# For production - specify allowed origins
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com",
]

CORS_ALLOW_CREDENTIALS = True
```

### JWT Settings (settings.py)

```python
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

---

## API Response Examples

### Dashboard Stats Response

```json
GET /api/dashboard/stats/?role=principal

{
    "total_consents": 15,
    "active_consents": 10,
    "pending_requests": 3,
    "revoked_consents": 2,
    "open_grievances": 1,
    "my_active_consents": 5,
    "my_pending_requests": 2,
    "my_grievances": 1
}
```

### Consent Request Response

```json
GET /api/consent-requests/{id}/

{
    "id": "uuid-here",
    "request_id": "CR-20260204-0001",
    "fiduciary": "uuid",
    "fiduciary_details": {
        "id": "uuid",
        "email": "admin@techcorp.com",
        "full_name": "TechCorp Admin",
        "organization_name": "TechCorp Ltd",
        "role": "fiduciary"
    },
    "principal": "uuid",
    "principal_details": {
        "id": "uuid",
        "email": "john.doe@email.com",
        "full_name": "John Doe",
        "organization_name": null,
        "role": "principal"
    },
    "purpose": "uuid",
    "purpose_details": {
        "id": "uuid",
        "name": "Marketing Analytics",
        "description": "To analyze customer preferences...",
        "data_categories": ["name", "email", "purchase_history"],
        "lawful_basis": "consent",
        "retention_period_days": 365
    },
    "data_requested": ["name", "email"],
    "notes": "For personalized marketing campaigns",
    "cms_status": "cms_approved",
    "cms_status_display": "CMS Approved",
    "status": "pending",
    "status_display": "Pending",
    "requested_at": "2026-02-04T10:30:00Z",
    "expires_at": "2027-02-04T10:30:00Z"
}
```

---

## Error Handling

### Standard Error Response Format

```json
{
    "detail": "Error message here",
    "code": "error_code"
}
```

### Common HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET/PATCH |
| 201 | Created | Successful POST |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Invalid/missing token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Internal error |

---

## Testing

### Using curl

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "principal@example.com", "password": "password123"}'

# Get consents (with token)
curl http://localhost:8000/api/consents/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Using PowerShell

```powershell
# Login
Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login/" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email": "principal@example.com", "password": "password123"}'

# Health check
Invoke-RestMethod -Uri "http://localhost:8000/api/health/" -Method GET
```

---

## DPDPA Compliance Features

| DPDPA Requirement | Implementation |
|-------------------|----------------|
| Informed Consent | Purpose model with detailed description |
| Data Minimization | data_categories field specifies exact data |
| Consent Withdrawal | Consent revocation endpoint |
| Grievance Redressal | 30-day SLA auto-enforcement |
| Audit Trail | Complete AuditLog for all actions |
| Data Retention | retention_period_days field |
| Right to Access | Principals can view all their data |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Feb 2026 | Initial release with full DPDPA compliance |

---

**Documentation generated for DPDPA Consent Management System Backend**

*Last updated: February 4, 2026*
