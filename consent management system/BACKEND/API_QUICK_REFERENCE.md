# Consent Request API - Quick Reference

## Accept Consent Request with Data

### Endpoint
```
POST /api/consent-requests/{id}/accept/
```

### Authentication
Required: Bearer Token (Data Principal only)

### Request Body
```json
{
  "response_data": {
    "field1": "value1",
    "field2": "value2",
    ...
  }
}
```

### Example
```bash
curl -X POST http://localhost:8000/api/consent-requests/abc-123-def/accept/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "response_data": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1-555-0123",
      "address": "123 Main St",
      "date_of_birth": "1990-01-15"
    }
  }'
```

### Success Response (200 OK)
```json
{
  "message": "Consent request accepted successfully",
  "consent_request": {
    "id": "abc-123-def",
    "request_id": "CR-20260405-0001",
    "status": "active",
    "principal_response_data": {
      "name": "John Doe",
      "email": "john@example.com",
      ...
    }
  },
  "consent_id": "xyz-789-ghi"
}
```

### Error Responses

#### Missing Response Data (400)
```json
{
  "error": "response_data is required when accepting a consent request",
  "code": "MISSING_RESPONSE_DATA"
}
```

#### Incomplete Data (400)
```json
{
  "error": "Missing required data fields: phone, address",
  "code": "INCOMPLETE_RESPONSE_DATA"
}
```

#### Not Authorized (403)
```json
{
  "error": "Only the data principal can accept this request"
}
```

#### Already Responded (400)
```json
{
  "error": "Request has already been responded to"
}
```

---

## Reject Consent Request

### Endpoint
```
POST /api/consent-requests/{id}/reject/
```

### Authentication
Required: Bearer Token (Data Principal only)

### Request Body
```json
{
  "reason": "Optional reason for rejection"
}
```

### Example
```bash
curl -X POST http://localhost:8000/api/consent-requests/abc-123-def/reject/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "I do not wish to share this information"
  }'
```

### Success Response (200 OK)
```json
{
  "id": "abc-123-def",
  "request_id": "CR-20260405-0001",
  "status": "rejected",
  "responded_at": "2026-04-05T10:30:00Z"
}
```

---

## View Pending Consent Requests

### Endpoint
```
GET /api/consent-requests/pending_principal/
```

### Authentication
Required: Bearer Token (Data Principal)

### Example
```bash
curl -X GET http://localhost:8000/api/consent-requests/pending_principal/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Success Response (200 OK)
```json
[
  {
    "id": "abc-123-def",
    "request_id": "CR-20260405-0001",
    "fiduciary_details": {
      "id": "fid-123",
      "organization_name": "ABC Corporation",
      "email": "contact@abc.com"
    },
    "purpose_details": {
      "name": "Account Creation",
      "description": "To create and manage your user account",
      "data_categories": ["name", "email", "phone"],
      "retention_period_days": 365
    },
    "data_requested": ["name", "email", "phone", "address", "date_of_birth"],
    "notes": "We need this information to create your account",
    "cms_status": "cms_approved",
    "status": "pending",
    "requested_at": "2026-04-05T09:00:00Z",
    "expires_at": "2027-04-05T00:00:00Z"
  }
]
```

---

## View Consent Details (Fiduciary)

### Endpoint
```
GET /api/consents/{id}/
```

### Authentication
Required: Bearer Token (Data Fiduciary)

### Example
```bash
curl -X GET http://localhost:8000/api/consents/xyz-789-ghi/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Success Response (200 OK)
```json
{
  "id": "xyz-789-ghi",
  "consent_id": "CON-20260405-0001",
  "principal_details": {
    "email": "john@example.com",
    "full_name": "John Doe"
  },
  "fiduciary_details": {
    "organization_name": "ABC Corporation"
  },
  "purpose_details": {
    "name": "Account Creation",
    "description": "To create and manage your user account"
  },
  "provided_data": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-555-0123",
    "address": "123 Main St",
    "date_of_birth": "1990-01-15"
  },
  "status": "active",
  "lifecycle_state": "active",
  "granted_at": "2026-04-05T10:30:00Z",
  "expires_at": "2027-04-05T00:00:00Z",
  "is_expired": false,
  "days_until_expiry": 365
}
```

---

## Data Field Validation

### Common Data Fields

| Field | Type | Format | Example |
|-------|------|--------|---------|
| name | string | Full name | "John Doe" |
| email | string | Email format | "john@example.com" |
| phone | string | Phone number | "+1-555-0123" |
| address | string | Full address | "123 Main St, City, State 12345" |
| date_of_birth | string | YYYY-MM-DD | "1990-01-15" |
| postal_code | string | Zip/Postal code | "12345" |
| country | string | Country name | "United States" |
| city | string | City name | "New York" |
| state | string | State/Province | "NY" |

### Custom Validation
You can add custom validation in the frontend before submitting:

```javascript
function validateResponseData(data, requiredFields) {
  const errors = {};
  
  requiredFields.forEach(field => {
    if (!data[field]) {
      errors[field] = 'This field is required';
    }
    
    // Email validation
    if (field === 'email' && data[field]) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(data[field])) {
        errors[field] = 'Invalid email format';
      }
    }
    
    // Phone validation
    if (field === 'phone' && data[field]) {
      const phoneRegex = /^\+?[\d\s\-()]+$/;
      if (!phoneRegex.test(data[field])) {
        errors[field] = 'Invalid phone format';
      }
    }
    
    // Date validation
    if (field === 'date_of_birth' && data[field]) {
      const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
      if (!dateRegex.test(data[field])) {
        errors[field] = 'Date must be in YYYY-MM-DD format';
      }
    }
  });
  
  return errors;
}
```

---

## Frontend Integration Example (React)

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

function ConsentRequestForm({ requestId }) {
  const [request, setRequest] = useState(null);
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch consent request details
    axios.get(`/api/consent-requests/${requestId}/`)
      .then(response => {
        setRequest(response.data);
        // Initialize form data
        const initialData = {};
        response.data.data_requested.forEach(field => {
          initialData[field] = '';
        });
        setFormData(initialData);
      })
      .catch(err => setError(err.message));
  }, [requestId]);

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleAccept = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(
        `/api/consent-requests/${requestId}/accept/`,
        { response_data: formData }
      );
      
      alert('Consent accepted successfully!');
      // Redirect or update UI
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to accept consent');
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async () => {
    const reason = prompt('Reason for rejection (optional):');
    setLoading(true);
    
    try {
      await axios.post(
        `/api/consent-requests/${requestId}/reject/`,
        { reason }
      );
      
      alert('Consent rejected');
      // Redirect or update UI
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to reject consent');
    } finally {
      setLoading(false);
    }
  };

  if (!request) return <div>Loading...</div>;

  return (
    <div className="consent-request-form">
      <h2>Consent Request</h2>
      
      <div className="request-info">
        <p><strong>From:</strong> {request.fiduciary_details.organization_name}</p>
        <p><strong>Purpose:</strong> {request.purpose_details.name}</p>
        <p><strong>Description:</strong> {request.purpose_details.description}</p>
        <p><strong>Notes:</strong> {request.notes}</p>
      </div>

      <h3>Please provide the following information:</h3>
      
      {request.data_requested.map(field => (
        <div key={field} className="form-field">
          <label>{field.replace('_', ' ').toUpperCase()}</label>
          <input
            type={field.includes('email') ? 'email' : 
                  field.includes('date') ? 'date' : 'text'}
            value={formData[field]}
            onChange={(e) => handleChange(field, e.target.value)}
            required
          />
        </div>
      ))}

      {error && <div className="error">{error}</div>}

      <div className="actions">
        <button 
          onClick={handleAccept} 
          disabled={loading}
          className="btn-accept"
        >
          Accept & Share Data
        </button>
        <button 
          onClick={handleReject} 
          disabled={loading}
          className="btn-reject"
        >
          Reject
        </button>
      </div>
    </div>
  );
}

export default ConsentRequestForm;
```

---

## Testing with cURL

### Complete Flow Test

```bash
# 1. Login as Principal
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"principal@example.com","password":"password123"}' \
  | jq -r '.access')

# 2. View pending requests
curl -X GET http://localhost:8000/api/consent-requests/pending_principal/ \
  -H "Authorization: Bearer $TOKEN"

# 3. Accept with data
curl -X POST http://localhost:8000/api/consent-requests/REQUEST_ID/accept/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "response_data": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1-555-0123"
    }
  }'

# 4. View your consents
curl -X GET http://localhost:8000/api/consents/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## Error Codes Reference

| Code | Description | HTTP Status |
|------|-------------|-------------|
| MISSING_RESPONSE_DATA | No response_data provided | 400 |
| INCOMPLETE_RESPONSE_DATA | Missing required fields | 400 |
| ALREADY_REVIEWED | Request already processed | 400 |
| NOT_AUTHORIZED | User not authorized | 403 |
| NOT_FOUND | Resource not found | 404 |
| SERVER_ERROR | Internal server error | 500 |

---

## Security Best Practices

1. **Always use HTTPS** in production
2. **Validate JWT tokens** on every request
3. **Sanitize input data** before storing
4. **Encrypt sensitive data** at rest
5. **Log all data access** for audit trails
6. **Implement rate limiting** to prevent abuse
7. **Use CORS properly** to restrict origins
8. **Validate data formats** on both frontend and backend
