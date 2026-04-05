"""
Example script demonstrating the enhanced consent request flow
This shows how the data principal receives, fills, and responds to consent requests
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"
PRINCIPAL_TOKEN = "your-principal-jwt-token"
FIDUCIARY_TOKEN = "your-fiduciary-jwt-token"

def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

# ============================================
# STEP 1: Fiduciary creates consent request
# ============================================
def create_consent_request():
    """Fiduciary creates a consent request for a data principal"""
    
    url = f"{BASE_URL}/consent-requests/"
    
    payload = {
        "principal": "uuid-of-principal",  # Replace with actual principal UUID
        "purpose": "uuid-of-purpose",      # Replace with actual purpose UUID
        "data_requested": [
            "name",
            "email", 
            "phone",
            "address",
            "date_of_birth"
        ],
        "notes": "We need this information to create your account and provide personalized services",
        "expires_at": "2027-04-05T00:00:00Z"
    }
    
    response = requests.post(
        url,
        headers=get_headers(FIDUCIARY_TOKEN),
        json=payload
    )
    
    if response.status_code == 201:
        print("✅ Consent request created successfully")
        print(json.dumps(response.json(), indent=2))
        return response.json()['id']
    else:
        print(f"❌ Error creating consent request: {response.status_code}")
        print(response.text)
        return None


# ============================================
# STEP 2: Principal views pending requests
# ============================================
def view_pending_requests():
    """Data principal views their pending consent requests"""
    
    url = f"{BASE_URL}/consent-requests/pending_principal/"
    
    response = requests.get(
        url,
        headers=get_headers(PRINCIPAL_TOKEN)
    )
    
    if response.status_code == 200:
        requests_data = response.json()
        print(f"\n📋 You have {len(requests_data)} pending consent request(s)\n")
        
        for req in requests_data:
            print("=" * 60)
            print(f"Request ID: {req['request_id']}")
            print(f"From: {req['fiduciary_details']['organization_name']}")
            print(f"Purpose: {req['purpose_details']['name']}")
            print(f"Description: {req['purpose_details']['description']}")
            print(f"\nData Requested:")
            for field in req['data_requested']:
                print(f"  - {field}")
            print(f"\nNotes: {req['notes']}")
            print(f"Expires: {req['expires_at']}")
            print(f"Retention Period: {req['purpose_details']['retention_period_days']} days")
            print("=" * 60)
        
        return requests_data
    else:
        print(f"❌ Error fetching requests: {response.status_code}")
        return []


# ============================================
# STEP 3: Principal fills and accepts request
# ============================================
def accept_consent_request(request_id):
    """Data principal accepts consent request with filled data"""
    
    url = f"{BASE_URL}/consent-requests/{request_id}/accept/"
    
    # Simulate user filling in the form
    print("\n📝 Please fill in the requested information:\n")
    
    response_data = {
        "name": input("Name: ") or "John Doe",
        "email": input("Email: ") or "john.doe@example.com",
        "phone": input("Phone: ") or "+1-555-0123",
        "address": input("Address: ") or "123 Main St, City, State 12345",
        "date_of_birth": input("Date of Birth (YYYY-MM-DD): ") or "1990-01-15"
    }
    
    print("\n📤 Submitting your response...\n")
    
    payload = {
        "response_data": response_data
    }
    
    response = requests.post(
        url,
        headers=get_headers(PRINCIPAL_TOKEN),
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Consent request accepted successfully!")
        print(f"Consent ID: {result['consent_id']}")
        print("\nYour data has been securely shared with the organization.")
        return result
    else:
        print(f"❌ Error accepting request: {response.status_code}")
        print(response.text)
        return None


# ============================================
# STEP 4: Principal rejects request
# ============================================
def reject_consent_request(request_id):
    """Data principal rejects consent request"""
    
    url = f"{BASE_URL}/consent-requests/{request_id}/reject/"
    
    reason = input("\nReason for rejection (optional): ") or "I don't feel comfortable sharing this information"
    
    payload = {
        "reason": reason
    }
    
    response = requests.post(
        url,
        headers=get_headers(PRINCIPAL_TOKEN),
        json=payload
    )
    
    if response.status_code == 200:
        print("✅ Consent request rejected successfully")
        print("The organization has been notified of your decision.")
        return response.json()
    else:
        print(f"❌ Error rejecting request: {response.status_code}")
        print(response.text)
        return None


# ============================================
# STEP 5: Fiduciary views consented data
# ============================================
def view_consent_data(consent_id):
    """Fiduciary views the data from an accepted consent"""
    
    url = f"{BASE_URL}/consents/{consent_id}/"
    
    response = requests.get(
        url,
        headers=get_headers(FIDUCIARY_TOKEN)
    )
    
    if response.status_code == 200:
        consent = response.json()
        print("\n📊 Consent Details:\n")
        print("=" * 60)
        print(f"Consent ID: {consent['consent_id']}")
        print(f"Principal: {consent['principal_details']['full_name']}")
        print(f"Status: {consent['status_display']}")
        print(f"Granted: {consent['granted_at']}")
        print(f"Expires: {consent['expires_at']}")
        print(f"\n📦 Provided Data:")
        for key, value in consent['provided_data'].items():
            print(f"  {key}: {value}")
        print("=" * 60)
        return consent
    else:
        print(f"❌ Error fetching consent: {response.status_code}")
        return None


# ============================================
# STEP 6: Principal revokes consent
# ============================================
def revoke_consent(consent_id):
    """Data principal revokes a previously granted consent"""
    
    url = f"{BASE_URL}/consents/{consent_id}/revoke/"
    
    reason = input("\nReason for revocation (optional): ") or "I no longer wish to share this data"
    
    payload = {
        "reason": reason
    }
    
    response = requests.post(
        url,
        headers=get_headers(PRINCIPAL_TOKEN),
        json=payload
    )
    
    if response.status_code == 200:
        print("✅ Consent revoked successfully")
        print("Your data will no longer be accessible to the organization.")
        return response.json()
    else:
        print(f"❌ Error revoking consent: {response.status_code}")
        print(response.text)
        return None


# ============================================
# Interactive Demo
# ============================================
def interactive_demo():
    """Run an interactive demonstration of the consent flow"""
    
    print("\n" + "=" * 60)
    print("  CONSENT MANAGEMENT SYSTEM - Interactive Demo")
    print("=" * 60)
    
    while True:
        print("\n📋 Menu:")
        print("1. View pending consent requests (as Principal)")
        print("2. Accept a consent request (as Principal)")
        print("3. Reject a consent request (as Principal)")
        print("4. View consent data (as Fiduciary)")
        print("5. Revoke a consent (as Principal)")
        print("6. Exit")
        
        choice = input("\nSelect an option (1-6): ")
        
        if choice == "1":
            view_pending_requests()
        
        elif choice == "2":
            request_id = input("Enter consent request ID: ")
            accept_consent_request(request_id)
        
        elif choice == "3":
            request_id = input("Enter consent request ID: ")
            reject_consent_request(request_id)
        
        elif choice == "4":
            consent_id = input("Enter consent ID: ")
            view_consent_data(consent_id)
        
        elif choice == "5":
            consent_id = input("Enter consent ID: ")
            revoke_consent(consent_id)
        
        elif choice == "6":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option. Please try again.")


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║  Enhanced Consent Request Flow - Example Script           ║
    ║                                                            ║
    ║  This script demonstrates the complete consent flow:      ║
    ║  1. Fiduciary creates request                             ║
    ║  2. Principal views request with purposes & data needed   ║
    ║  3. Principal fills required data                         ║
    ║  4. Principal accepts/rejects                             ║
    ║  5. Data forwarded to fiduciary (if accepted)             ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    print("\n⚠️  Before running this script:")
    print("1. Update BASE_URL if your server is not on localhost:8000")
    print("2. Replace PRINCIPAL_TOKEN and FIDUCIARY_TOKEN with valid JWT tokens")
    print("3. Ensure the Django server is running")
    print("4. Run migrations: python manage.py migrate")
    
    proceed = input("\nReady to proceed? (y/n): ")
    
    if proceed.lower() == 'y':
        interactive_demo()
    else:
        print("\n📖 Usage Instructions:")
        print("1. Start Django server: python manage.py runserver")
        print("2. Login to get JWT tokens")
        print("3. Update tokens in this script")
        print("4. Run: python example_consent_flow.py")
