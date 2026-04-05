# Troubleshooting Guide - Consent Request Accept/Reject Issues

## Issue: Cannot Accept or Reject Consent Requests

### Problem Description
After creating a consent request:
- CMS portal cannot accept or reject the request
- Data principal portal cannot accept or reject the request

---

## Fixed Issues

### 1. CMS Deny Method Bug ✓ FIXED
**Problem:** The `cms_deny` method was trying to get `reviewer_id` from request data instead of using the authenticated user.

**Error:**
```python
consent_request.cms_reviewed_by_id = request.data.get('reviewer_id')  # Wrong!
```

**Fix:**
```python
consent_request.cms_reviewed_by = request.user  # Correct!
```

**Status:** ✓ Fixed in views.py

---

## Common Issues & Solutions

### Issue 1: Permission Denied (403 Forbidden)

**Symptoms:**
- Error: "Not authorized"
- HTTP 403 status code

**Causes:**
1. User doesn't have the correct role
2. User is not authenticated
3. JWT token is expired or invalid

**Solutions:**

#### For CMS Approve/Deny:
```bash
# Check user role
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# User must have role: "processor" or "dpo"
```

#### For Principal Accept/Reject:
```bash
# Check user role
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# User must have role: "principal"
# User must be the designated principal for the request
```

**Fix:**
- Ensure you're logged in with the correct user role
- Get a fresh JWT token if expired
- Verify the user is the correct principal for the request

---

### Issue 2: Request Already Reviewed (400 Bad Request)

**Symptoms:**
- Error: "Request has already been reviewed"
- HTTP 400 status code

**Cause:**
The consent request has already been processed (approved, denied, accepted, or rejected)

**Check Request Status:**
```bash
curl -X GET http://localhost:8000/api/consent-requests/REQUEST_ID/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Status Flow:**
```
CMS Review:
pending_cms → cms_approved (can proceed to principal)
pending_cms → cms_denied (END - cannot proceed)

Principal Response:
cms_approved + pending → active (accepted)
cms_approved + pending → rejected (rejected)
```

**Solution:**
- Check the `cms_status` and `status` fields
- If already reviewed, create a new consent request

---

### Issue 3: Request Not Yet Approved by CMS

**Symptoms:**
- Error: "Request not yet approved by CMS"
- Principal cannot accept/reject

**Cause:**
The CMS processor hasn't approved the request yet

**Check Status:**
```bash
curl -X GET http://localhost:8000/api/consent-requests/REQUEST_ID/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check: cms_status should be "cms_approved"
```

**Solution:**
1. CMS processor must approve first:
```bash
curl -X POST http://localhost:8000/api/consent-requests/REQUEST_ID/cms_approve/ \
  -H "Authorization: Bearer CMS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Approved for compliance"}'
```

2. Then principal can accept/reject

---

### Issue 4: Missing Response Data (Principal Accept)

**Symptoms:**
- Error: "response_data is required when accepting a consent request"
- HTTP 400 status code

**Cause:**
The new enhanced flow requires principals to provide data when accepting

**Solution:**
Include `response_data` in the request body:

```bash
curl -X POST http://localhost:8000/api/consent-requests/REQUEST_ID/accept/ \
  -H "Authorization: Bearer PRINCIPAL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "response_data": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1-555-0123"
    }
  }'
```

---

### Issue 5: Incomplete Response Data

**Symptoms:**
- Error: "Missing required data fields: field1, field2"
- HTTP 400 status code

**Cause:**
Not all requested fields were provided in `response_data`

**Check Required Fields:**
```bash
curl -X GET http://localhost:8000/api/consent-requests/REQUEST_ID/ \
  -H "Authorization: Bearer TOKEN"

# Look at the "data_requested" field
```

**Solution:**
Provide all fields listed in `data_requested`:

```bash
# If data_requested = ["name", "email", "phone"]
# Then response_data must include all three:

curl -X POST http://localhost:8000/api/consent-requests/REQUEST_ID/accept/ \
  -H "Authorization: Bearer PRINCIPAL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "response_data": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1-555-0123"
    }
  }'
```

---

### Issue 6: Wrong User Trying to Accept/Reject

**Symptoms:**
- Error: "Only the data principal can accept/reject this request"
- HTTP 403 status code

**Cause:**
A different user is trying to accept/reject a request meant for another principal

**Check:**
```bash
# Get request details
curl -X GET http://localhost:8000/api/consent-requests/REQUEST_ID/ \
  -H "Authorization: Bearer TOKEN"

# Compare principal.id with your user.id
```

**Solution:**
- Log in as the correct principal user
- Ensure the request is assigned to your user account

---

## Debugging Steps

### Step 1: Verify User Authentication
```bash
# Get current user info
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected response:
{
  "id": "user-uuid",
  "email": "user@example.com",
  "role": "principal" | "processor" | "dpo" | "fiduciary",
  ...
}
```

### Step 2: Check Consent Request Status
```bash
# Get request details
curl -X GET http://localhost:8000/api/consent-requests/REQUEST_ID/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check these fields:
{
  "cms_status": "pending_cms" | "cms_approved" | "cms_denied",
  "status": "pending" | "active" | "rejected",
  "principal": { "id": "principal-uuid" },
  "data_requested": ["field1", "field2", ...]
}
```

### Step 3: Test CMS Approve (as Processor/DPO)
```bash
curl -X POST http://localhost:8000/api/consent-requests/REQUEST_ID/cms_approve/ \
  -H "Authorization: Bearer CMS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Test approval"}' \
  -v

# Look for:
# - HTTP 200 OK
# - cms_status: "cms_approved"
```

### Step 4: Test Principal Accept
```bash
curl -X POST http://localhost:8000/api/consent-requests/REQUEST_ID/accept/ \
  -H "Authorization: Bearer PRINCIPAL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "response_data": {
      "name": "Test User",
      "email": "test@example.com"
    }
  }' \
  -v

# Look for:
# - HTTP 200 OK
# - status: "active"
# - consent_id in response
```

---

## Testing Script

Save this as `test_consent_flow.sh`:

```bash
#!/bin/bash

# Configuration
BASE_URL="http://localhost:8000/api"
CMS_TOKEN="your-cms-token"
PRINCIPAL_TOKEN="your-principal-token"
REQUEST_ID="your-request-id"

echo "=== Testing Consent Request Flow ==="

# Step 1: Check request status
echo -e "\n1. Checking request status..."
curl -X GET "$BASE_URL/consent-requests/$REQUEST_ID/" \
  -H "Authorization: Bearer $PRINCIPAL_TOKEN" \
  -s | jq '.'

# Step 2: CMS Approve
echo -e "\n2. CMS approving request..."
curl -X POST "$BASE_URL/consent-requests/$REQUEST_ID/cms_approve/" \
  -H "Authorization: Bearer $CMS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Test approval"}' \
  -s | jq '.'

# Step 3: Principal Accept
echo -e "\n3. Principal accepting request..."
curl -X POST "$BASE_URL/consent-requests/$REQUEST_ID/accept/" \
  -H "Authorization: Bearer $PRINCIPAL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "response_data": {
      "name": "Test User",
      "email": "test@example.com",
      "phone": "+1-555-0123"
    }
  }' \
  -s | jq '.'

echo -e "\n=== Test Complete ==="
```

Run with:
```bash
chmod +x test_consent_flow.sh
./test_consent_flow.sh
```

---

## Python Testing Script

Save this as `test_consent_endpoints.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_cms_approve(request_id, cms_token):
    """Test CMS approve endpoint"""
    print("\n=== Testing CMS Approve ===")
    
    url = f"{BASE_URL}/consent-requests/{request_id}/cms_approve/"
    headers = {
        "Authorization": f"Bearer {cms_token}",
        "Content-Type": "application/json"
    }
    data = {"notes": "Test approval"}
    
    response = requests.post(url, headers=headers, json=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✓ CMS Approve successful")
        return True
    else:
        print("✗ CMS Approve failed")
        return False

def test_principal_accept(request_id, principal_token, response_data):
    """Test principal accept endpoint"""
    print("\n=== Testing Principal Accept ===")
    
    url = f"{BASE_URL}/consent-requests/{request_id}/accept/"
    headers = {
        "Authorization": f"Bearer {principal_token}",
        "Content-Type": "application/json"
    }
    data = {"response_data": response_data}
    
    response = requests.post(url, headers=headers, json=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✓ Principal Accept successful")
        return True
    else:
        print("✗ Principal Accept failed")
        return False

def test_principal_reject(request_id, principal_token, reason):
    """Test principal reject endpoint"""
    print("\n=== Testing Principal Reject ===")
    
    url = f"{BASE_URL}/consent-requests/{request_id}/reject/"
    headers = {
        "Authorization": f"Bearer {principal_token}",
        "Content-Type": "application/json"
    }
    data = {"reason": reason}
    
    response = requests.post(url, headers=headers, json=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✓ Principal Reject successful")
        return True
    else:
        print("✗ Principal Reject failed")
        return False

if __name__ == "__main__":
    # Configuration
    REQUEST_ID = input("Enter Consent Request ID: ")
    CMS_TOKEN = input("Enter CMS Token: ")
    PRINCIPAL_TOKEN = input("Enter Principal Token: ")
    
    # Test CMS Approve
    test_cms_approve(REQUEST_ID, CMS_TOKEN)
    
    # Test Principal Accept
    response_data = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "+1-555-0123"
    }
    test_principal_accept(REQUEST_ID, PRINCIPAL_TOKEN, response_data)
```

Run with:
```bash
python test_consent_endpoints.py
```

---

## Frontend Integration Issues

### Issue: Frontend Not Sending response_data

**Problem:**
Old frontend code doesn't include `response_data` when accepting

**Old Code (Won't Work):**
```javascript
// This will fail with new backend
fetch(`/api/consent-requests/${id}/accept/`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
});
```

**New Code (Required):**
```javascript
// This is required now
const formData = {
  name: document.getElementById('name').value,
  email: document.getElementById('email').value,
  phone: document.getElementById('phone').value
};

fetch(`/api/consent-requests/${id}/accept/`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    response_data: formData
  })
});
```

---

## Database Checks

### Check Consent Request in Database
```bash
python manage.py shell
```

```python
from application.models import ConsentRequest

# Get request
cr = ConsentRequest.objects.get(id='your-request-id')

# Check status
print(f"CMS Status: {cr.cms_status}")
print(f"Status: {cr.status}")
print(f"Principal: {cr.principal.email}")
print(f"Data Requested: {cr.data_requested}")
print(f"CMS Reviewed By: {cr.cms_reviewed_by}")
```

---

## Logs

### Check Application Logs
```bash
# View recent logs
tail -f logs/dpdpa_cms.log

# Search for errors
grep "Error" logs/dpdpa_cms.log

# Search for specific request
grep "REQUEST_ID" logs/dpdpa_cms.log
```

---

## Quick Fix Checklist

- [ ] Fixed `cms_deny` method bug (use `request.user` instead of `request.data.get('reviewer_id')`)
- [ ] Verified user has correct role (processor/dpo for CMS, principal for accept/reject)
- [ ] Checked JWT token is valid and not expired
- [ ] Verified request status is correct (pending_cms for CMS, cms_approved+pending for principal)
- [ ] Included `response_data` when accepting (new requirement)
- [ ] Provided all fields listed in `data_requested`
- [ ] Verified user is the designated principal for the request
- [ ] Checked application logs for errors
- [ ] Tested with cURL or Python script

---

## Still Having Issues?

1. **Enable Debug Mode:**
   ```python
   # In settings.py
   DEBUG = True
   LOGGING = {
       'version': 1,
       'handlers': {
           'console': {
               'class': 'logging.StreamHandler',
           },
       },
       'root': {
           'handlers': ['console'],
           'level': 'DEBUG',
       },
   }
   ```

2. **Check Django Server Output:**
   ```bash
   python manage.py runserver
   # Watch for errors in console
   ```

3. **Test with Django Shell:**
   ```bash
   python manage.py shell
   ```
   ```python
   from application.models import ConsentRequest, User
   from django.utils import timezone
   
   # Get objects
   cr = ConsentRequest.objects.first()
   user = User.objects.get(role='processor')
   
   # Manually approve
   cr.cms_status = 'cms_approved'
   cr.cms_reviewed_by = user
   cr.cms_reviewed_at = timezone.now()
   cr.save()
   
   print("Manually approved!")
   ```

4. **Contact Support:**
   - Check documentation in `CONSENT_REQUEST_FLOW.md`
   - Review API reference in `API_QUICK_REFERENCE.md`
   - Run example script: `python example_consent_flow.py`

---

**Last Updated:** April 5, 2026
**Status:** ✓ Bug Fixed - Ready for Testing
