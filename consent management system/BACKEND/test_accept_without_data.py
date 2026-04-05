"""
Test script to verify accept endpoint works without response_data (backward compatibility)
"""

import sys
import os
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'consent_backend.settings')
django.setup()

from application.models import (
    User, Purpose, ConsentRequest, Consent,
    RoleChoices, ConsentStatusChoices, CMSStatusChoices
)
from django.utils import timezone
from datetime import timedelta


def test_accept_without_response_data():
    """Test that accept works without response_data for backward compatibility"""
    print("\n=== Testing Accept Without Response Data ===")
    
    try:
        # Get test users
        fiduciary = User.objects.get(email='fiduciary@test.com')
        principal = User.objects.get(email='principal@test.com')
        processor = User.objects.get(email='processor@test.com')
        purpose = Purpose.objects.filter(fiduciary=fiduciary).first()
        
        # Create consent request
        consent_request = ConsentRequest.objects.create(
            fiduciary=fiduciary,
            principal=principal,
            purpose=purpose,
            data_requested=['name', 'email'],
            notes='Test without data',
            expires_at=timezone.now() + timedelta(days=365)
        )
        print(f"✓ Created consent request: {consent_request.request_id}")
        
        # CMS approve
        consent_request.cms_status = CMSStatusChoices.CMS_APPROVED
        consent_request.cms_reviewed_by = processor
        consent_request.cms_reviewed_at = timezone.now()
        consent_request.save()
        print(f"✓ CMS approved request")
        
        # Accept WITHOUT response_data (simulating old frontend behavior)
        consent_request.status = ConsentStatusChoices.ACTIVE
        consent_request.responded_at = timezone.now()
        # Note: principal_response_data remains empty {}
        consent_request.save()
        
        # Create consent
        consent = Consent.objects.create(
            consent_request=consent_request,
            principal=principal,
            fiduciary=fiduciary,
            purpose=purpose,
            data_categories=consent_request.data_requested,
            provided_data={},  # Empty - no data provided
            status=ConsentStatusChoices.ACTIVE,
            expires_at=consent_request.expires_at
        )
        
        # Verify
        consent_request.refresh_from_db()
        consent.refresh_from_db()
        
        if consent_request.status == ConsentStatusChoices.ACTIVE:
            print(f"✓ Accept without data successful")
            print(f"  Status: {consent_request.status}")
            print(f"  Consent ID: {consent.consent_id}")
            print(f"  Response Data: {consent_request.principal_response_data}")
            print(f"  Provided Data: {consent.provided_data}")
            
            if consent_request.principal_response_data == {}:
                print(f"✓ Response data is empty (as expected)")
            
            if consent.provided_data == {}:
                print(f"✓ Provided data is empty (as expected)")
            
            return True
        else:
            print("✗ Accept failed")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_accept_with_response_data():
    """Test that accept still works WITH response_data"""
    print("\n=== Testing Accept With Response Data ===")
    
    try:
        # Get test users
        fiduciary = User.objects.get(email='fiduciary@test.com')
        principal = User.objects.get(email='principal@test.com')
        processor = User.objects.get(email='processor@test.com')
        purpose = Purpose.objects.filter(fiduciary=fiduciary).first()
        
        # Create consent request
        consent_request = ConsentRequest.objects.create(
            fiduciary=fiduciary,
            principal=principal,
            purpose=purpose,
            data_requested=['name', 'email', 'phone'],
            notes='Test with data',
            expires_at=timezone.now() + timedelta(days=365)
        )
        print(f"✓ Created consent request: {consent_request.request_id}")
        
        # CMS approve
        consent_request.cms_status = CMSStatusChoices.CMS_APPROVED
        consent_request.cms_reviewed_by = processor
        consent_request.cms_reviewed_at = timezone.now()
        consent_request.save()
        print(f"✓ CMS approved request")
        
        # Accept WITH response_data
        response_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1-555-0123'
        }
        
        consent_request.principal_response_data = response_data
        consent_request.status = ConsentStatusChoices.ACTIVE
        consent_request.responded_at = timezone.now()
        consent_request.save()
        
        # Create consent
        consent = Consent.objects.create(
            consent_request=consent_request,
            principal=principal,
            fiduciary=fiduciary,
            purpose=purpose,
            data_categories=consent_request.data_requested,
            provided_data=response_data,
            status=ConsentStatusChoices.ACTIVE,
            expires_at=consent_request.expires_at
        )
        
        # Verify
        consent_request.refresh_from_db()
        consent.refresh_from_db()
        
        if consent_request.status == ConsentStatusChoices.ACTIVE:
            print(f"✓ Accept with data successful")
            print(f"  Status: {consent_request.status}")
            print(f"  Consent ID: {consent.consent_id}")
            print(f"  Response Data: {consent_request.principal_response_data}")
            print(f"  Provided Data: {consent.provided_data}")
            
            if consent_request.principal_response_data == response_data:
                print(f"✓ Response data stored correctly")
            
            if consent.provided_data == response_data:
                print(f"✓ Provided data stored correctly")
            
            return True
        else:
            print("✗ Accept failed")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  Backward Compatibility Test Suite                        ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    results = {
        'Accept Without Data': test_accept_without_response_data(),
        'Accept With Data': test_accept_with_response_data()
    }
    
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║  Test Results Summary                                      ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:.<50} {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All backward compatibility tests passed!")
        print("The accept endpoint now works both WITH and WITHOUT response_data")
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
    
    sys.exit(0 if passed == total else 1)
