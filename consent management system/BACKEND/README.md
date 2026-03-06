# DPDPA Consent Management System - Backend

Django REST API backend for the DPDPA 2023 Consent Management System.

## 📁 Project Structure

```
BACKEND/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── db.sqlite3                # SQLite database (created after migration)
│
├── consent_backend/          # Project settings
│   ├── __init__.py
│   ├── settings.py           # Django settings with CORS config
│   ├── urls.py               # Root URL configuration
│   └── wsgi.py               # WSGI entry point
│
└── application/              # Main application
    ├── __init__.py
    ├── admin.py              # Django admin configuration
    ├── apps.py               # App configuration
    ├── models.py             # Database models
    ├── serializers.py        # DRF serializers
    ├── views.py              # API views
    ├── urls.py               # API URL routes
    └── management/
        └── commands/
            └── seed_data.py  # Sample data seeder
```

## 🚀 Quick Start

### Step 1: Create Virtual Environment

```bash
cd BACKEND

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables

```bash
# Copy environment template
copy .env.example .env    # Windows
cp .env.example .env      # Mac/Linux
```

### Step 4: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### Step 6: Seed Sample Data (Optional)

```bash
python manage.py seed_data
```

### Step 7: Run Development Server

```bash
python manage.py runserver
```

The API will be available at: `http://localhost:8000/api/`

## 📚 API Endpoints

### Health Check
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health/` | API health check |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/stats/` | Get dashboard statistics |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/` | List all users |
| POST | `/api/users/` | Create new user |
| GET | `/api/users/{id}/` | Get user by ID |
| PATCH | `/api/users/{id}/` | Update user |
| DELETE | `/api/users/{id}/` | Delete user |
| GET | `/api/users/principals/` | Get all principals |
| GET | `/api/users/fiduciaries/` | Get all fiduciaries |

### Purposes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/purposes/` | List all purposes |
| POST | `/api/purposes/` | Create new purpose |
| GET | `/api/purposes/{id}/` | Get purpose by ID |
| PATCH | `/api/purposes/{id}/` | Update purpose |
| GET | `/api/purposes/fiduciary/{id}/` | Get by fiduciary |

### Consent Requests
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/consent-requests/` | List all requests |
| POST | `/api/consent-requests/` | Create new request |
| GET | `/api/consent-requests/{id}/` | Get request by ID |
| GET | `/api/consent-requests/pending_cms/` | Pending CMS review |
| POST | `/api/consent-requests/{id}/cms_approve/` | CMS approve |
| POST | `/api/consent-requests/{id}/cms_deny/` | CMS deny |
| POST | `/api/consent-requests/{id}/accept/` | Principal accepts |
| POST | `/api/consent-requests/{id}/reject/` | Principal rejects |

### Consents
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/consents/` | List all consents |
| GET | `/api/consents/{id}/` | Get consent by ID |
| GET | `/api/consents/active/` | Get active consents |
| POST | `/api/consents/{id}/revoke/` | Revoke consent |

### Grievances
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/grievances/` | List all grievances |
| POST | `/api/grievances/` | Create grievance |
| GET | `/api/grievances/{id}/` | Get grievance by ID |
| POST | `/api/grievances/{id}/assign_dpo/` | Assign DPO |
| POST | `/api/grievances/{id}/resolve/` | Resolve grievance |

### Audit Logs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/audit-logs/` | List all audit logs |
| POST | `/api/audit-logs/` | Create audit log |
| GET | `/api/audit-logs/user/{id}/` | Get by user |

## 🧪 Testing with Postman

### Example: Create a User (Data Principal)

**POST** `http://localhost:8000/api/users/`

```json
{
  "email": "john@example.com",
  "username": "johndoe",
  "password": "password123",
  "role": "principal",
  "full_name": "John Doe",
  "phone": "+91-9876543210"
}
```

### Example: Create a Consent Request

**POST** `http://localhost:8000/api/consent-requests/`

```json
{
  "fiduciary": "fiduciary-uuid-here",
  "principal": "principal-uuid-here",
  "purpose": "purpose-uuid-here",
  "data_requested": ["name", "email", "phone"],
  "notes": "For marketing communications"
}
```

### Example: Get Dashboard Stats

**GET** `http://localhost:8000/api/dashboard/stats/?user_id=xxx&role=principal`

## 🔒 CORS Configuration

CORS is configured to allow requests from:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Alternative React port)

For production, update `CORS_ALLOWED_ORIGINS` in `settings.py`.

## 📊 Database Models

### User Roles
- **Principal**: Individual whose data is processed
- **Fiduciary**: Organization collecting/processing data
- **Processor**: CMS staff reviewing requests
- **DPO**: Data Protection Officer handling grievances

### Consent Request Workflow
1. Fiduciary creates request → `cms_status = pending_cms`
2. CMS Processor reviews → `cms_approved` or `cms_denied`
3. If approved, Principal responds → `active` or `rejected`
4. Consent record created if accepted

## 🔗 Frontend Integration

The frontend connects to this API using:
```typescript
const API_BASE_URL = 'http://localhost:8000/api';
```

See `src/services/api.ts` in the frontend project for API client implementation.

## 📝 Sample Test Users (after running seed_data)

| Email | Password | Role |
|-------|----------|------|
| john.doe@email.com | password123 | Principal |
| admin@techcorp.com | password123 | Fiduciary |
| cms1@consenthub.com | password123 | Processor |
| dpo@consenthub.com | password123 | DPO |

## 🛠️ Troubleshooting

### CORS Issues
If you see CORS errors:
1. Check that `corsheaders` is installed
2. Verify `corsheaders.middleware.CorsMiddleware` is at the top of MIDDLEWARE
3. Add your frontend URL to `CORS_ALLOWED_ORIGINS`

### Migration Issues
```bash
# Reset migrations
python manage.py migrate application zero
python manage.py makemigrations application
python manage.py migrate
```

### Database Reset
```bash
# Delete database and start fresh
del db.sqlite3           # Windows
rm db.sqlite3            # Mac/Linux
python manage.py migrate
python manage.py seed_data
```
