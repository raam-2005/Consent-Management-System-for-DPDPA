# ✅ Data Collection Feature - Complete Implementation

## Feature Overview

When a data principal accepts a consent request, they now must fill in the actual data (like email, phone, name, etc.) that was requested by the data fiduciary. This ensures that the consent process includes explicit data sharing.

## What Was Implemented

### Backend (Already Done) ✅
- Accept endpoint supports `response_data` parameter
- Validates all requested fields are provided
- Stores data in `principal_response_data` and `provided_data` fields
- Backward compatible (works with or without data)

### Frontend (New Implementation) ✅

#### 1. New Component: ConsentDataDialog
**File:** `src/components/consent/ConsentDataDialog.tsx`

**Features:**
- Dynamic form generation based on `data_requested` fields
- Field type detection (email, phone, date, text)
- Real-time validation
- User-friendly placeholders
- Shows purpose and CMS verification
- Data retention information

**Validation:**
- Required field validation
- Email format validation
- Phone number format validation
- Date format validation (YYYY-MM-DD)

#### 2. Updated API Service
**File:** `src/services/api.ts`

**Changes:**
```typescript
// Before
accept: (id: string) => ...

// After
accept: (id: string, responseData?: Record<string, any>) => ...
```

Now supports optional `responseData` parameter.

#### 3. Updated Components

**PrincipalConsentRequests.tsx:**
- Shows data collection dialog when "Accept" is clicked
- Collects data before submitting
- Validates all fields
- Shows success message after submission

**PrincipalDashboard.tsx:**
- Same data collection flow
- Integrated with dashboard quick actions

---

## User Flow

### Step 1: View Consent Request
User sees a consent request with:
- Organization name
- Purpose
- Data categories requested (e.g., name, email, phone)
- CMS verification badge

### Step 2: Click "I Agree" / "Accept"
Instead of immediately accepting, a dialog opens.

### Step 3: Fill Required Data
Dialog shows:
```
┌─────────────────────────────────────────────┐
│ Provide Your Information                   │
├─────────────────────────────────────────────┤
│ Purpose: Account Creation                   │
│ From: ABC Corporation                       │
│ ✓ CMS Verified                             │
├─────────────────────────────────────────────┤
│ Required Information (3 fields)             │
│                                             │
│ Name *                                      │
│ [John Doe                              ]    │
│                                             │
│ Email *                                     │
│ [john@example.com                      ]    │
│                                             │
│ Phone *                                     │
│ [+1-555-0123                           ]    │
│                                             │
│ ℹ Data Retention: 365 days                 │
│ ℹ You can withdraw consent anytime         │
├─────────────────────────────────────────────┤
│ [Cancel]  [Confirm & Share Data]           │
└─────────────────────────────────────────────┘
```

### Step 4: Validation
- All fields must be filled
- Email must be valid format
- Phone must be valid format
- Shows error messages if validation fails

### Step 5: Submit
- Data is sent to backend
- Consent is granted
- Success message shown
- User redirected/refreshed

---

## Field Types & Validation

### Automatic Field Type Detection

| Field Name Contains | Input Type | Validation | Placeholder |
|---------------------|------------|------------|-------------|
| `email` | email | Email format | example@email.com |
| `phone` | tel | Phone format | +1-555-0123 |
| `date`, `birth` | date | YYYY-MM-DD | YYYY-MM-DD |
| `age` | number | Numeric | 25 |
| `name` | text | Required | John Doe |
| `address` | text | Required | 123 Main St |
| Other | text | Required | Enter your {field} |

### Validation Rules

1. **Required Fields:**
   - All fields are required
   - Shows error: "This field is required"

2. **Email Validation:**
   - Must match: `user@domain.com`
   - Shows error: "Please enter a valid email address"

3. **Phone Validation:**
   - Must contain only: digits, spaces, +, -, (, )
   - Shows error: "Please enter a valid phone number"

4. **Date Validation:**
   - Must match: `YYYY-MM-DD`
   - Shows error: "Please enter date in YYYY-MM-DD format"

---

## API Request/Response

### Request Format
```bash
POST /api/consent-requests/{id}/accept/
Authorization: Bearer {token}
Content-Type: application/json

{
  "response_data": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-555-0123",
    "address": "123 Main St, City, State 12345"
  }
}
```

### Success Response
```json
{
  "message": "Consent request accepted successfully",
  "consent_request": {
    "id": "uuid",
    "status": "active",
    "principal_response_data": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1-555-0123",
      "address": "123 Main St, City, State 12345"
    }
  },
  "consent_id": "consent-uuid"
}
```

### Error Response (Missing Fields)
```json
{
  "error": "Missing required data fields: phone, address",
  "code": "INCOMPLETE_RESPONSE_DATA"
}
```

---

## Screenshots / UI Examples

### Dialog Appearance

```
╔═══════════════════════════════════════════════════════════╗
║ ✓ Provide Your Information                               ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║ Please fill in the following information to grant        ║
║ consent to ABC Corporation                                ║
║                                                           ║
║ ┌───────────────────────────────────────────────────┐   ║
║ │ ℹ Purpose: Account Creation                       │   ║
║ │   To create and manage your user account          │   ║
║ └───────────────────────────────────────────────────┘   ║
║                                                           ║
║ ┌───────────────────────────────────────────────────┐   ║
║ │ ✓ This request has been verified by the CMS      │   ║
║ └───────────────────────────────────────────────────┘   ║
║                                                           ║
║ Required Information  [3 fields]                          ║
║                                                           ║
║ Name *                                                    ║
║ ┌─────────────────────────────────────────────────┐     ║
║ │ John Doe                                        │     ║
║ └─────────────────────────────────────────────────┘     ║
║                                                           ║
║ Email *                                                   ║
║ ┌─────────────────────────────────────────────────┐     ║
║ │ john@example.com                                │     ║
║ └─────────────────────────────────────────────────┘     ║
║                                                           ║
║ Phone *                                                   ║
║ ┌─────────────────────────────────────────────────┐     ║
║ │ +1-555-0123                                     │     ║
║ └─────────────────────────────────────────────────┘     ║
║                                                           ║
║ ┌───────────────────────────────────────────────────┐   ║
║ │ ℹ Data Retention: 365 days                       │   ║
║ │ ℹ Your Rights: You can withdraw consent anytime  │   ║
║ └───────────────────────────────────────────────────┘   ║
║                                                           ║
║                    [Cancel]  [Confirm & Share Data]      ║
╚═══════════════════════════════════════════════════════════╝
```

---

## Testing

### Manual Testing Steps

1. **Login as Data Principal**
   ```
   Email: principal@test.com
   Password: test123
   ```

2. **Navigate to Consent Requests**
   - Go to "Consent Requests" page
   - Or use dashboard quick action

3. **Find Pending Request**
   - Look for requests with "CMS Verified" badge
   - Status should be "Pending"

4. **Click "I Agree" or "Accept"**
   - Dialog should open
   - Should show all requested fields

5. **Fill in Data**
   - Enter valid data for each field
   - Try invalid data to test validation

6. **Submit**
   - Click "Confirm & Share Data"
   - Should show success message
   - Request should disappear from pending list

### Test Cases

#### Test 1: Valid Data Submission ✅
```
Input:
- Name: John Doe
- Email: john@example.com
- Phone: +1-555-0123

Expected: Success, consent granted
```

#### Test 2: Missing Required Field ❌
```
Input:
- Name: John Doe
- Email: john@example.com
- Phone: (empty)

Expected: Error "This field is required"
```

#### Test 3: Invalid Email ❌
```
Input:
- Name: John Doe
- Email: invalid-email
- Phone: +1-555-0123

Expected: Error "Please enter a valid email address"
```

#### Test 4: Invalid Phone ❌
```
Input:
- Name: John Doe
- Email: john@example.com
- Phone: abc123

Expected: Error "Please enter a valid phone number"
```

---

## Files Modified/Created

### Backend (No Changes Needed)
- ✅ Already supports `response_data`
- ✅ Already validates fields
- ✅ Already stores data

### Frontend

#### Created:
1. ✅ `src/components/consent/ConsentDataDialog.tsx` - Data collection dialog

#### Modified:
1. ✅ `src/services/api.ts` - Updated accept method signature
2. ✅ `src/pages/principal/PrincipalConsentRequests.tsx` - Added dialog integration
3. ✅ `src/pages/dashboard/PrincipalDashboard.tsx` - Added dialog integration

---

## Benefits

### For Data Principals
- ✅ Clear understanding of what data is being shared
- ✅ Explicit data entry (no hidden data collection)
- ✅ Validation ensures correct format
- ✅ Can review before submitting
- ✅ Transparent process

### For Data Fiduciaries
- ✅ Receive structured, validated data
- ✅ Compliance with DPDPA requirements
- ✅ Audit trail of data collection
- ✅ Reduced data quality issues

### For Compliance
- ✅ Explicit consent with data sharing
- ✅ Clear purpose specification
- ✅ Audit trail maintained
- ✅ User-friendly process
- ✅ DPDPA 2023 compliant

---

## Future Enhancements (Optional)

1. **Field-Specific Validation Rules**
   - Custom regex patterns per field
   - Min/max length validation
   - Custom error messages

2. **Conditional Fields**
   - Show/hide fields based on other inputs
   - Optional vs required fields

3. **Data Prefill**
   - Prefill from user profile
   - Remember previous entries

4. **File Uploads**
   - Support document uploads
   - Image uploads for verification

5. **Multi-Step Form**
   - Break long forms into steps
   - Progress indicator

6. **Data Preview**
   - Show summary before submission
   - Edit capability

---

## Summary

The data collection feature is now **fully implemented** and working. When a data principal accepts a consent request, they must fill in the actual data that was requested. This provides:

- ✅ Explicit data sharing
- ✅ User-friendly interface
- ✅ Validation and error handling
- ✅ DPDPA compliance
- ✅ Transparent process

**Status:** ✅ **COMPLETE AND READY TO USE**

---

**Date:** April 5, 2026

**Version:** 1.0

**Tested:** ✅ Yes
