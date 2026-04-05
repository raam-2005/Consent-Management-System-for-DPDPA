# Visual Guide: Consent Request Flow with Data Collection

## 🎯 Overview

This guide provides a visual representation of how data principals receive consent requests, fill in required data, and make decisions.

---

## 📊 Complete Flow Diagram

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    CONSENT REQUEST LIFECYCLE                      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Fiduciary Creates Request                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Company: ABC Corporation                                  │  │
│  │ Purpose: Account Creation                                 │  │
│  │ Data Needed:                                              │  │
│  │   • Name                                                  │  │
│  │   • Email                                                 │  │
│  │   • Phone                                                 │  │
│  │   • Address                                               │  │
│  │   • Date of Birth                                         │  │
│  │ Retention: 365 days                                       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  Status: pending_cms                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: CMS Processor Reviews                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Reviewer: CMS Processor                                   │  │
│  │ Checks:                                                   │  │
│  │   ✓ Purpose is legitimate                                 │  │
│  │   ✓ Data requested is appropriate                         │  │
│  │   ✓ Complies with DPDPA regulations                       │  │
│  │   ✓ Retention period is reasonable                        │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  Action: APPROVE ✓  or  DENY ✗                                   │
│  Status: cms_approved                                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Principal Receives Notification                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ 🔔 New Consent Request                                    │  │
│  │                                                           │  │
│  │ From: ABC Corporation                                     │  │
│  │ Purpose: Account Creation                                 │  │
│  │ Click to review →                                         │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Principal Views Request Details                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ CONSENT REQUEST DETAILS                                   │  │
│  │ ═══════════════════════════════════════════════════════   │  │
│  │                                                           │  │
│  │ From: ABC Corporation                                     │  │
│  │ Contact: contact@abc.com                                  │  │
│  │                                                           │  │
│  │ Purpose: Account Creation                                 │  │
│  │ Description: To create and manage your user account      │  │
│  │                                                           │  │
│  │ Why we need this data:                                    │  │
│  │ We need this information to create your account and       │  │
│  │ provide personalized services                             │  │
│  │                                                           │  │
│  │ Data Retention: 365 days                                  │  │
│  │ Consent Expires: April 5, 2027                            │  │
│  │                                                           │  │
│  │ ─────────────────────────────────────────────────────     │  │
│  │ REQUIRED INFORMATION:                                     │  │
│  │   • Name                                                  │  │
│  │   • Email                                                 │  │
│  │   • Phone                                                 │  │
│  │   • Address                                               │  │
│  │   • Date of Birth                                         │  │
│  │ ─────────────────────────────────────────────────────     │  │
│  │                                                           │  │
│  │ [Continue to Fill Data] [Reject Request]                  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: Principal Fills Required Data                           │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ PROVIDE YOUR INFORMATION                                  │  │
│  │ ═══════════════════════════════════════════════════════   │  │
│  │                                                           │  │
│  │ Name *                                                    │  │
│  │ ┌─────────────────────────────────────────────────────┐   │  │
│  │ │ John Doe                                            │   │  │
│  │ └─────────────────────────────────────────────────────┘   │  │
│  │                                                           │  │
│  │ Email *                                                   │  │
│  │ ┌─────────────────────────────────────────────────────┐   │  │
│  │ │ john.doe@example.com                                │   │  │
│  │ └─────────────────────────────────────────────────────┘   │  │
│  │                                                           │  │
│  │ Phone *                                                   │  │
│  │ ┌─────────────────────────────────────────────────────┐   │  │
│  │ │ +1-555-0123                                         │   │  │
│  │ └─────────────────────────────────────────────────────┘   │  │
│  │                                                           │  │
│  │ Address *                                                 │  │
│  │ ┌─────────────────────────────────────────────────────┐   │  │
│  │ │ 123 Main St, City, State 12345                      │   │  │
│  │ └─────────────────────────────────────────────────────┘   │  │
│  │                                                           │  │
│  │ Date of Birth *                                           │  │
│  │ ┌─────────────────────────────────────────────────────┐   │  │
│  │ │ 1990-01-15                                          │   │  │
│  │ └─────────────────────────────────────────────────────┘   │  │
│  │                                                           │  │
│  │ * Required fields                                         │  │
│  │                                                           │  │
│  │ [✓ Accept & Share Data] [✗ Reject]                       │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────┴─────────┐
                    │                   │
         ┌──────────▼──────────┐   ┌───▼──────────┐
         │  ACCEPT PATH        │   │  REJECT PATH │
         └──────────┬──────────┘   └───┬──────────┘
                    │                   │
                    ↓                   ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6A: Accept - Data Stored & Shared                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ ✓ SUCCESS                                                 │  │
│  │                                                           │  │
│  │ Your consent has been granted!                            │  │
│  │                                                           │  │
│  │ Consent ID: CON-20260405-0001                             │  │
│  │ Status: Active                                            │  │
│  │ Expires: April 5, 2027                                    │  │
│  │                                                           │  │
│  │ Your data has been securely shared with:                  │  │
│  │ ABC Corporation                                           │  │
│  │                                                           │  │
│  │ You can revoke this consent at any time.                  │  │
│  │                                                           │  │
│  │ [View My Consents] [Done]                                 │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  Database Updates:                                                │
│  • ConsentRequest.status = "active"                               │
│  • ConsentRequest.principal_response_data = {filled data}         │
│  • New Consent created with provided_data                         │
│  • Audit log created                                              │
│  • Notification sent to fiduciary                                 │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 7: Fiduciary Accesses Data                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ CONSENT DETAILS                                           │  │
│  │ ═══════════════════════════════════════════════════════   │  │
│  │                                                           │  │
│  │ Consent ID: CON-20260405-0001                             │  │
│  │ Principal: John Doe (john.doe@example.com)                │  │
│  │ Purpose: Account Creation                                 │  │
│  │ Status: Active                                            │  │
│  │ Granted: April 5, 2026 10:30 AM                           │  │
│  │ Expires: April 5, 2027                                    │  │
│  │                                                           │  │
│  │ ─────────────────────────────────────────────────────     │  │
│  │ PROVIDED DATA:                                            │  │
│  │   Name: John Doe                                          │  │
│  │   Email: john.doe@example.com                             │  │
│  │   Phone: +1-555-0123                                      │  │
│  │   Address: 123 Main St, City, State 12345                 │  │
│  │   Date of Birth: 1990-01-15                               │  │
│  │ ─────────────────────────────────────────────────────     │  │
│  │                                                           │  │
│  │ [Export Data] [View Audit Log]                            │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  STEP 6B: Reject - No Data Shared                                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ ✗ REQUEST REJECTED                                        │  │
│  │                                                           │  │
│  │ You have declined to share your data.                     │  │
│  │                                                           │  │
│  │ Reason: I don't feel comfortable sharing this             │  │
│  │         information at this time.                         │  │
│  │                                                           │  │
│  │ The organization has been notified of your decision.      │  │
│  │                                                           │  │
│  │ [Done]                                                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  Database Updates:                                                │
│  • ConsentRequest.status = "rejected"                             │
│  • Audit log created with rejection reason                        │
│  • Notification sent to fiduciary                                 │
│  • NO Consent record created                                      │
│  • NO data shared                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 State Transitions

```
ConsentRequest States:
┌──────────────┐
│ pending_cms  │ ← Initial state when fiduciary creates request
└──────┬───────┘
       │
       ├─→ cms_approved ← CMS processor approves
       │
       └─→ cms_denied ← CMS processor denies (END)

┌──────────────┐
│ cms_approved │
└──────┬───────┘
       │
       ├─→ active ← Principal accepts with data
       │
       └─→ rejected ← Principal rejects (END)

┌──────────────┐
│   active     │ ← Consent granted, data shared
└──────────────┘
```

---

## 📦 Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA JOURNEY                              │
└─────────────────────────────────────────────────────────────────┘

1. FIDUCIARY SPECIFIES NEEDS
   ┌────────────────────────────────┐
   │ data_requested: [              │
   │   "name",                      │
   │   "email",                     │
   │   "phone",                     │
   │   "address",                   │
   │   "date_of_birth"              │
   │ ]                              │
   └────────────────────────────────┘
                ↓
2. PRINCIPAL FILLS DATA
   ┌────────────────────────────────┐
   │ response_data: {               │
   │   "name": "John Doe",          │
   │   "email": "john@example.com", │
   │   "phone": "+1-555-0123",      │
   │   "address": "123 Main St",    │
   │   "date_of_birth": "1990-01-15"│
   │ }                              │
   └────────────────────────────────┘
                ↓
3. STORED IN CONSENT REQUEST
   ┌────────────────────────────────┐
   │ ConsentRequest                 │
   │ ├─ data_requested: [...]       │
   │ └─ principal_response_data: {} │
   └────────────────────────────────┘
                ↓
4. COPIED TO CONSENT
   ┌────────────────────────────────┐
   │ Consent                        │
   │ ├─ data_categories: [...]      │
   │ └─ provided_data: {}           │
   └────────────────────────────────┘
                ↓
5. ACCESSIBLE TO FIDUCIARY
   ┌────────────────────────────────┐
   │ GET /api/consents/{id}/        │
   │ Returns: provided_data         │
   └────────────────────────────────┘
```

---

## 🔐 Security & Privacy

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY MEASURES                             │
└─────────────────────────────────────────────────────────────────┘

1. AUTHENTICATION
   ┌────────────────────────────────┐
   │ JWT Token Required             │
   │ Role-Based Access Control      │
   │ Only Principal can accept      │
   └────────────────────────────────┘

2. VALIDATION
   ┌────────────────────────────────┐
   │ All fields must be provided    │
   │ Format validation              │
   │ XSS prevention                 │
   └────────────────────────────────┘

3. AUDIT TRAIL
   ┌────────────────────────────────┐
   │ Every action logged            │
   │ Who, What, When recorded       │
   │ IP address tracked             │
   └────────────────────────────────┘

4. DATA PROTECTION
   ┌────────────────────────────────┐
   │ Encrypted in transit (HTTPS)   │
   │ Access controlled by role      │
   │ Time-bound (expiry dates)      │
   └────────────────────────────────┘

5. CONSENT MANAGEMENT
   ┌────────────────────────────────┐
   │ Can be revoked anytime         │
   │ Automatic expiry               │
   │ Notification on changes        │
   └────────────────────────────────┘
```

---

## 📱 User Interface Examples

### Principal's View - Pending Request

```
╔════════════════════════════════════════════════════════════╗
║  📋 Consent Requests                                       ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  🔔 NEW REQUEST                                            ║
║  ┌────────────────────────────────────────────────────┐   ║
║  │ From: ABC Corporation                              │   ║
║  │ Purpose: Account Creation                          │   ║
║  │ Requested: 2 hours ago                             │   ║
║  │                                                    │   ║
║  │ They need: name, email, phone, address             │   ║
║  │                                                    │   ║
║  │ [Review Request →]                                 │   ║
║  └────────────────────────────────────────────────────┘   ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

### Principal's View - Fill Data Form

```
╔════════════════════════════════════════════════════════════╗
║  📝 Provide Your Information                               ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  ABC Corporation needs the following information:          ║
║                                                            ║
║  Name *                                                    ║
║  ┌──────────────────────────────────────────────────────┐ ║
║  │ John Doe                                             │ ║
║  └──────────────────────────────────────────────────────┘ ║
║                                                            ║
║  Email *                                                   ║
║  ┌──────────────────────────────────────────────────────┐ ║
║  │ john.doe@example.com                                 │ ║
║  └──────────────────────────────────────────────────────┘ ║
║                                                            ║
║  Phone *                                                   ║
║  ┌──────────────────────────────────────────────────────┐ ║
║  │ +1-555-0123                                          │ ║
║  └──────────────────────────────────────────────────────┘ ║
║                                                            ║
║  ℹ️  Your data will be stored for 365 days                ║
║  ℹ️  You can revoke consent at any time                   ║
║                                                            ║
║  ┌──────────────────┐  ┌──────────────────┐              ║
║  │ ✓ Accept & Share │  │ ✗ Reject         │              ║
║  └──────────────────┘  └──────────────────┘              ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

### Fiduciary's View - Consented Data

```
╔════════════════════════════════════════════════════════════╗
║  📊 Consent Details                                        ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  Consent ID: CON-20260405-0001                             ║
║  Principal: John Doe                                       ║
║  Status: ✓ Active                                          ║
║  Granted: April 5, 2026 10:30 AM                           ║
║  Expires: April 5, 2027                                    ║
║                                                            ║
║  ─────────────────────────────────────────────────────     ║
║  PROVIDED DATA                                             ║
║  ─────────────────────────────────────────────────────     ║
║                                                            ║
║  Name:          John Doe                                   ║
║  Email:         john.doe@example.com                       ║
║  Phone:         +1-555-0123                                ║
║  Address:       123 Main St, City, State 12345             ║
║  Date of Birth: January 15, 1990                           ║
║                                                            ║
║  ─────────────────────────────────────────────────────     ║
║                                                            ║
║  [📥 Export Data] [📜 View Audit Log] [🔔 Notify User]    ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

---

## ✅ Validation Checklist

When principal accepts a consent request:

```
┌─────────────────────────────────────────────────────────────────┐
│  VALIDATION STEPS                                                │
└─────────────────────────────────────────────────────────────────┘

☑ User is authenticated
☑ User is the designated principal
☑ Request is CMS approved
☑ Request status is "pending"
☑ response_data is provided
☑ All requested fields are present
☑ Data formats are valid
☑ No XSS/injection attempts

If all pass → Create Consent ✓
If any fail → Return error ✗
```

---

## 🎓 Key Concepts

### Data Requested vs Provided Data

```
data_requested (List)          principal_response_data (Dict)
─────────────────────          ──────────────────────────────
["name", "email", "phone"] →   {"name": "John Doe",
                                "email": "john@example.com",
                                "phone": "+1-555-0123"}

What fiduciary needs            What principal provides
```

### Consent Request vs Consent

```
ConsentRequest                  Consent
──────────────                  ───────
The ask/request                 The granted permission
Status: pending → active        Status: active
Has: data_requested             Has: provided_data
Can be: accepted/rejected       Can be: revoked
```

---

This visual guide should help you understand the complete flow of how data principals interact with consent requests in your system!
