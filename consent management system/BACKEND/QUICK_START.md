# Quick Start Guide - Enhanced Consent Request Flow

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.8+
- Django installed
- Database configured

### Step 1: Apply Database Changes
```bash
cd "consent management system/BACKEND"
python manage.py migrate
```

Expected output:
```
Applying application.0010_add_response_data_fields... OK
```

### Step 2: Start the Server
```bash
python manage.py runserver
```

### Step 3: Test the New Flow

#### Option A: Using cURL

1. **Login as Principal**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "principal@example.com",
    "password": "your-password"
  }'
```

2. **View Pending Requests**
```bash
curl -X GET http://localhost:8000/api/consent-requests/pending_principal/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

3. **Accept with Data**
```bash
curl -X POST http://localhost:8000/api/consent-requests/REQUEST_ID/accept/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "response_data": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1-555-0123"
    }
  }'
```

#### Option B: Using Python Script

```bash
# Update tokens in the script first
python example_consent_flow.py
```

### Step 4: Verify in Database

```bash
python manage.py shell
```

```python
from application.models import ConsentRequest, Consent

# Check consent request with response data
cr = ConsentRequest.objects.filter(status='active').first()
print(cr.principal_response_data)

# Check consent with provided data
consent = Consent.objects.filter(status='active').first()
print(consent.provided_data)
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `CONSENT_REQUEST_FLOW.md` | Complete workflow documentation |
| `API_QUICK_REFERENCE.md` | API endpoints and examples |
| `VISUAL_FLOW_GUIDE.md` | Visual diagrams and UI examples |
| `IMPLEMENTATION_SUMMARY.md` | Technical implementation details |
| `example_consent_flow.py` | Interactive testing script |

---

## 🔑 Key Changes

### What's New?

1. **Principal Response Data**
   - Principals now provide actual data when accepting
   - Data is validated against requested fields
   - Stored in `principal_response_data` field

2. **Enhanced Accept Endpoint**
   - Requires `response_data` in request body
   - Validates all fields are provided
   - Returns detailed success response

3. **Data Storage**
   - ConsentRequest stores `principal_response_data`
   - Consent stores `provided_data`
   - Both accessible through API

### API Changes

**Before:**
```bash
POST /api/consent-requests/{id}/accept/
# No body needed
```

**After:**
```bash
POST /api/consent-requests/{id}/accept/
{
  "response_data": {
    "field1": "value1",
    "field2": "value2"
  }
}
```

---

## 🧪 Testing Scenarios

### Scenario 1: Happy Path
```bash
# 1. Create consent request (as fiduciary)
# 2. CMS approves
# 3. Principal accepts with complete data
# 4. Fiduciary accesses data
# Result: ✓ Success
```

### Scenario 2: Missing Data
```bash
# 1. Principal tries to accept without all fields
# Result: ✗ Error "Missing required data fields"
```

### Scenario 3: Rejection
```bash
# 1. Principal rejects with reason
# Result: ✓ Rejected, no data shared
```

---

## 🐛 Troubleshooting

### Error: "response_data is required"
**Solution:** Include response_data in request body
```json
{
  "response_data": { /* your data */ }
}
```

### Error: "Missing required data fields"
**Solution:** Provide all fields listed in `data_requested`

### Error: "Request has already been responded to"
**Solution:** This request was already accepted/rejected

### Error: "Request not yet approved by CMS"
**Solution:** Wait for CMS processor to approve

---

## 📊 Database Schema

### New Fields Added

**ConsentRequest:**
```python
principal_response_data = JSONField(default=dict)
# Stores: {"name": "John", "email": "john@example.com", ...}
```

**Consent:**
```python
provided_data = JSONField(default=dict)
# Stores: {"name": "John", "email": "john@example.com", ...}
```

---

## 🔐 Security Notes

### Current Implementation
- ✅ JWT authentication required
- ✅ Role-based access control
- ✅ Input validation
- ✅ Audit logging

### Recommended for Production
- ⚠️ Encrypt `provided_data` at rest
- ⚠️ Use HTTPS only
- ⚠️ Implement rate limiting
- ⚠️ Add CAPTCHA for sensitive operations
- ⚠️ Mask data in logs

---

## 📱 Frontend Integration

### React Example
```jsx
const handleAccept = async (requestId, formData) => {
  const response = await fetch(
    `/api/consent-requests/${requestId}/accept/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        response_data: formData
      })
    }
  );
  
  if (response.ok) {
    const result = await response.json();
    console.log('Consent granted:', result.consent_id);
  }
};
```

### Vue Example
```javascript
async acceptConsent(requestId, formData) {
  try {
    const response = await this.$axios.post(
      `/api/consent-requests/${requestId}/accept/`,
      { response_data: formData }
    );
    this.$toast.success('Consent granted successfully');
  } catch (error) {
    this.$toast.error(error.response.data.error);
  }
}
```

---

## 📞 Support

### Need Help?

1. **Check Documentation**
   - Read `CONSENT_REQUEST_FLOW.md` for detailed workflow
   - Check `API_QUICK_REFERENCE.md` for API examples

2. **Run Example Script**
   ```bash
   python example_consent_flow.py
   ```

3. **Check Logs**
   ```bash
   tail -f logs/dpdpa_cms.log
   ```

4. **Verify Database**
   ```bash
   python manage.py shell
   ```

---

## ✅ Checklist

Before deploying to production:

- [ ] Run migrations
- [ ] Test accept flow with data
- [ ] Test reject flow
- [ ] Test validation errors
- [ ] Update frontend to collect data
- [ ] Implement data encryption
- [ ] Add field-level validation
- [ ] Configure HTTPS
- [ ] Set up monitoring
- [ ] Review audit logs
- [ ] Test consent revocation
- [ ] Verify data access controls

---

## 🎯 Next Steps

1. **Test the implementation**
   ```bash
   python manage.py test application
   ```

2. **Update your frontend**
   - Add form to collect response_data
   - Handle validation errors
   - Display success/error messages

3. **Add security enhancements**
   - Implement field encryption
   - Add rate limiting
   - Configure CORS properly

4. **Monitor and optimize**
   - Set up logging
   - Monitor API performance
   - Track consent metrics

---

## 📖 Additional Resources

- Django Documentation: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- DPDPA 2023 Guidelines: [Official Government Website]

---

**Ready to go!** 🚀

Your consent management system now supports the complete data collection flow. Principals can view requests, fill in required data, and make informed decisions about sharing their information.
