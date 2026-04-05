# Enhanced Consent Request Flow with Data Collection

## Overview
This document describes the enhanced consent request workflow where data principals receive consent requests with specific purposes and data categories, fill in the required information, and decide whether to accept or reject before forwarding to the data fiduciary.

## Workflow Steps

### 1. Data Fiduciary Creates Consent Request
The data fiduciary (company) creates a consent request specifying:
- **Purpose**: Why they need the data (e.g., "Account Creation", "Marketing Communications")
- **Data Categories**: What data fields they need (e.g., ["name", "email", "phone", "address"])
- **Expiry Date**: How long the consent is valid
- **Notes**: Additional context about the request

**API Endpoint**: `POST /api/consent-requests/`

**Request Body**:
```json
{
  "principal": "uuid-of-data-principal",
  "purpose": "uuid-of-purpose",
  "data_requested": ["name", "email", "phone", "address", "date_of_birth"],
  "notes": "We need this information to create your account and provide personalized services",
  "expires_at": "2027-04-05T00:00:00Z"
}
```

### 2. CMS Processor Reviews Request
The consent management system processor reviews the request for compliance:
- Validates the purpose is legitimate
- Ensures data requested is appropriate for the purpose
- Checks compliance with DPDPA regulations

**API Endpoint**: `POST /api/consent-requests/{id}/cms_approve/`

### 3. Data Principal Receives Request
Once CMS approved, the data principal receives a notification and can view:
- The requesting organization (fiduciary)
- The purpose of data collection
- List of data fields being requested
- Retention period
- Expiry date

**API Endpoint**: `GET /api/consent-requests/pending_principal/`

**Response**:
```json
{
  "id": "uuid",
  "request_id": "CR-20260405-0001",
  "fiduciary_details": {
    "organization_name": "ABC Corporation",
    "email": "contact@abc.com"
  },
  "purpose_details": {
    "name": "Account Creation",
    "description": "To create and manage your user account",
    "data_categories": ["name", "email", "phone", "address"],
    "retention_period_days": 365
  },
  "data_requested": ["name", "email", "phone", "address", "date_of_birth"],
  "notes": "We need this information to create your account",
  "cms_status": "cms_approved",
  "status": "pending",
  "expires_at": "2027-04-05T00:00:00Z"
}
```

### 4. Data Principal Fills Required Data
The principal reviews the request and fills in the actual data for each requested field:

**Frontend Form Example**:
```
Consent Request from: ABC Corporation
Purpose: Account Creation

Please provide the following information:
- Name: [John Doe]
- Email: [john.doe@example.com]
- Phone: [+1-555-0123]
- Address: [123 Main St, City, State 12345]
- Date of Birth: [1990-01-15]

[Accept] [Reject]
```

### 5. Data Principal Accepts or Rejects

#### Option A: Accept with Data
**API Endpoint**: `POST /api/consent-requests/{id}/accept/`

**Request Body**:
```json
{
  "response_data": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-0123",
    "address": "123 Main St, City, State 12345",
    "date_of_birth": "1990-01-15"
  }
}
```

**Validation**:
- All requested data fields must be provided
- Data format validation (email format, phone format, etc.)
- Returns error if any required field is missing

**Response**:
```json
{
  "message": "Consent request accepted successfully",
  "consent_request": { /* updated consent request */ },
  "consent_id": "uuid-of-created-consent"
}
```

**What Happens**:
1. Consent request status updated to "active"
2. Principal's response data stored in `principal_response_data` field
3. New Consent record created with:
   - Status: "active"
   - Provided data stored in `provided_data` field
   - Link to original consent request
4. Audit log created
5. Notification sent to fiduciary
6. Data is now accessible to the fiduciary

#### Option B: Reject
**API Endpoint**: `POST /api/consent-requests/{id}/reject/`

**Request Body**:
```json
{
  "reason": "I don't feel comfortable sharing this information"
}
```

**What Happens**:
1. Consent request status updated to "rejected"
2. Rejection reason stored in audit log
3. Notification sent to fiduciary
4. No consent record created
5. No data shared with fiduciary

### 6. Data Fiduciary Accesses Consented Data
Once accepted, the fiduciary can access the provided data through the consent record:

**API Endpoint**: `GET /api/consents/{id}/`

**Response**:
```json
{
  "id": "uuid",
  "consent_id": "CON-20260405-0001",
  "principal_details": {
    "email": "john.doe@example.com",
    "full_name": "John Doe"
  },
  "purpose_details": {
    "name": "Account Creation"
  },
  "provided_data": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-0123",
    "address": "123 Main St, City, State 12345",
    "date_of_birth": "1990-01-15"
  },
  "status": "active",
  "granted_at": "2026-04-05T10:30:00Z",
  "expires_at": "2027-04-05T00:00:00Z"
}
```

## Data Security Considerations

### Current Implementation
- Data is stored in JSON fields in the database
- Access controlled through role-based permissions
- Audit logs track all data access

### Recommended Enhancements for Production
1. **Encryption at Rest**: Encrypt `provided_data` and `principal_response_data` fields
2. **Encryption in Transit**: Use HTTPS/TLS for all API communications
3. **Data Masking**: Mask sensitive data in logs and non-essential views
4. **Access Logging**: Log every access to consented data
5. **Data Minimization**: Only store what's necessary
6. **Secure Deletion**: Implement secure data deletion when consent expires/revoked

## API Endpoints Summary

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/api/consent-requests/` | POST | Fiduciary | Create consent request |
| `/api/consent-requests/{id}/cms_approve/` | POST | Processor/DPO | Approve request |
| `/api/consent-requests/{id}/cms_deny/` | POST | Processor/DPO | Deny request |
| `/api/consent-requests/pending_principal/` | GET | Principal | View pending requests |
| `/api/consent-requests/{id}/accept/` | POST | Principal | Accept with data |
| `/api/consent-requests/{id}/reject/` | POST | Principal | Reject request |
| `/api/consents/` | GET | All | List consents (filtered by role) |
| `/api/consents/{id}/` | GET | Fiduciary/Principal | View consent details |
| `/api/consents/{id}/revoke/` | POST | Principal | Revoke consent |

## Example Frontend Flow

### Step 1: Principal Views Pending Requests
```javascript
// Fetch pending consent requests
const response = await fetch('/api/consent-requests/pending_principal/', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const requests = await response.json();
```

### Step 2: Display Request Details
```javascript
// Show request details to user
const request = requests[0];
console.log(`Request from: ${request.fiduciary_details.organization_name}`);
console.log(`Purpose: ${request.purpose_details.name}`);
console.log(`Data needed: ${request.data_requested.join(', ')}`);
```

### Step 3: Collect Data from User
```javascript
// Create form dynamically based on data_requested
const form = {};
request.data_requested.forEach(field => {
  form[field] = getUserInput(field); // Get input from user
});
```

### Step 4: Submit Response
```javascript
// Accept with data
const acceptResponse = await fetch(`/api/consent-requests/${request.id}/accept/`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    response_data: form
  })
});

// Or reject
const rejectResponse = await fetch(`/api/consent-requests/${request.id}/reject/`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    reason: 'User provided reason'
  })
});
```

## Database Schema Changes

### ConsentRequest Model
```python
class ConsentRequest(models.Model):
    # ... existing fields ...
    data_requested = models.JSONField()  # List of field names
    principal_response_data = models.JSONField()  # NEW: Data provided by principal
```

### Consent Model
```python
class Consent(models.Model):
    # ... existing fields ...
    data_categories = models.JSONField()  # List of categories
    provided_data = models.JSONField()  # NEW: Actual data from principal
```

## Migration

Run the migration to add new fields:
```bash
python manage.py migrate
```

## Testing

### Test Case 1: Accept with Complete Data
```bash
curl -X POST http://localhost:8000/api/consent-requests/{id}/accept/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "response_data": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1-555-0123"
    }
  }'
```

### Test Case 2: Accept with Missing Data (Should Fail)
```bash
curl -X POST http://localhost:8000/api/consent-requests/{id}/accept/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "response_data": {
      "name": "John Doe"
    }
  }'
```
Expected: Error response indicating missing fields

### Test Case 3: Reject with Reason
```bash
curl -X POST http://localhost:8000/api/consent-requests/{id}/reject/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "I do not wish to share this information"
  }'
```

## Compliance Notes

This implementation supports DPDPA 2023 requirements:
- ✅ Clear purpose specification
- ✅ Explicit consent collection
- ✅ Data minimization (only requested fields)
- ✅ Audit trail of all actions
- ✅ Right to withdraw consent
- ✅ Transparency in data usage
- ✅ Time-bound consent (expiry dates)

## Next Steps

1. Run migration: `python manage.py migrate`
2. Test the enhanced flow with sample data
3. Update frontend to collect and submit response data
4. Implement data encryption for sensitive fields
5. Add data validation rules for specific field types
6. Implement data masking in audit logs
