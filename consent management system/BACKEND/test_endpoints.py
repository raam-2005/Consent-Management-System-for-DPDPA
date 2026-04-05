"""
Quick test script to verify consent request endpoints are working
Run this after fixing the cms_deny bug
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


def create_test_data():
    """Create test data for testing"""
    print("\n=== Creating Test Data ===")
    
    # Create users
    try:
        fiduciary = User.objects.get(email='fiduciary@test.com')
        print("✓ Fiduciary user exists")
    except User.DoesNotExist:
        fiduciary = User.objects.create_user(
            username='fiduciary_test',
            email='fiduciary@test.com',
            password='test123',
            role=RoleChoices.FIDUCIARY,
            full_name='Test Fiduciary',
            organization_name='Test Corp'
        )
        print("✓ Created fiduciary user")
    
    try:
        principal = User.objects.get(email='principal@test.com')
        print("✓ Principal user exists")
    except User.DoesNotExist:
        principal = User.objects.create_user(
            username='principal_test',
            email='principal@test.com',
            password='test123',
            role=RoleChoices.PRINCIPAL,
            full_name='Test Principal'
        )
        print("✓ Created principal user")
    
    try:
        processor = User.objects.get(email='processor@test.com')
        print("✓ Processor user exists")
    except User.DoesNotExist:
        processor = User.objects.create_user(
            username='processor_test',
            email='processor@test.com',
            password='test123',
            role=RoleChoices.PROCESSOR,
            full_name='Test Processor'
        )
        print("✓ Created processor user")
    
    # Create purpose
    purpose, created = Purpose.objects.get_or_create(
        name='Test Purpose',
        fiduciary=fiduciary,
        defaults={
            'description': 'Test purpose for consent',
            'data_categories': ['name', 'email', 'phone'],
            'retention_period_days': 365
        }
    )
    if created:
        print("✓ Created test purpose")
    else:
        print("✓ Test purpose exists")
    
    # Create consent request
    consent_request = ConsentRequest.objects.create(
        fiduciary=fiduciary,
        principal=principal,
        purpose=purpose,
        data_requested=['name', 'email', 'phone'],
        notes='Test consent request',
        expires_at=timezone.now() + timedelta(days=365)
    )
    print(f"✓ Created consent request: {consent_request.request_id}")
    
    return {
        'fiduciary': fiduciary,
        'principal': principal,
        'processor': processor,
        'purpose': purpose,
        'consent_request': consent_request
    }


def test_cms_approve(consent_request, processor):
    """Test CMS approve functionality"""
    print("\n=== Testing CMS Approve ===")
    
    try:
        # Check initial status
        print(f"Initial CMS Status: {consent_request.cms_status}")
        
        if consent_request.cms_status != CMSStatusChoices.PENDING_CMS:
            print("⚠ Request not in pending_cms status")
            return False
        
        # Approve
        consent_request.cms_status = CMSStatusChoices.CMS_APPROVED
        consent_request.cms_reviewed_by = processor
        consent_request.cms_reviewed_at = timezone.now()
        consent_request.cms_notes = 'Test approval'
        consent_request.save()
        
        # Verify
        consent_request.refresh_from_db()
        if consent_request.cms_status == CMSStatusChoices.CMS_APPROVED:
            print(f"✓ CMS Approve successful")
            print(f"  Status: {consent_request.cms_status}")
            print(f"  Reviewed by: {consent_request.cms_reviewed_by.email}")
            return True
        else:
            print("✗ CMS Approve failed")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_cms_deny(consent_request, processor):
    """Test CMS deny functionality"""
    print("\n=== Testing CMS Deny ===")
    
    try:
        # Create a new request for deny test
        new_request = ConsentRequest.objects.create(
            fiduciary=consent_request.fiduciary,
            principal=consent_request.principal,
            purpose=consent_request.purpose,
            data_requested=['name', 'email'],
            notes='Test deny request',
            expires_at=timezone.now() + timedelta(days=365)
        )
        
        print(f"Created test request: {new_request.request_id}")
        print(f"Initial CMS Status: {new_request.cms_status}")
        
        # Deny
        new_request.cms_status = CMSStatusChoices.CMS_DENIED
        new_request.status = ConsentStatusChoices.REJECTED
        new_request.cms_reviewed_by = processor
        new_request.cms_reviewed_at = timezone.now()
        new_request.cms_notes = 'Test denial'
        new_request.responded_at = timezone.now()
        new_request.save()
        
        # Verify
        new_request.refresh_from_db()
        if new_request.cms_status == CMSStatusChoices.CMS_DENIED:
            print(f"✓ CMS Deny successful")
            print(f"  CMS Status: {new_request.cms_status}")
            print(f"  Status: {new_request.status}")
            print(f"  Reviewed by: {new_request.cms_reviewed_by.email}")
            return True
        else:
            print("✗ CMS Deny failed")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_principal_accept(consent_request, principal):
    """Test principal accept functionality"""
    print("\n=== Testing Principal Accept ===")
    
    try:
        # Check status
        print(f"CMS Status: {consent_request.cms_status}")
        print(f"Status: {consent_request.status}")
        
        if consent_request.cms_status != CMSStatusChoices.CMS_APPROVED:
            print("⚠ Request not CMS approved")
            return False
        
        if consent_request.status != ConsentStatusChoices.PENDING:
            print("⚠ Request not in pending status")
            return False
        
        # Prepare response data
        response_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+1-555-0123'
        }
        
        # Accept
        consent_request.principal_response_data = response_data
        consent_request.status = ConsentStatusChoices.ACTIVE
        consent_request.responded_at = timezone.now()
        consent_request.save()
        
        # Create consent
        consent = Consent.objects.create(
            consent_request=consent_request,
            principal=principal,
            fiduciary=consent_request.fiduciary,
            purpose=consent_request.purpose,
            data_categories=consent_request.data_requested,
            provided_data=response_data,
            status=ConsentStatusChoices.ACTIVE,
            expires_at=consent_request.expires_at
        )
        
        # Verify
        consent_request.refresh_from_db()
        if consent_request.status == ConsentStatusChoices.ACTIVE:
            print(f"✓ Principal Accept successful")
            print(f"  Status: {consent_request.status}")
            print(f"  Consent ID: {consent.consent_id}")
            print(f"  Response Data: {consent_request.principal_response_data}")
            return True
        else:
            print("✗ Principal Accept failed")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_principal_reject():
    """Test principal reject functionality"""
    print("\n=== Testing Principal Reject ===")
    
    try:
        # Get test data
        fiduciary = User.objects.get(email='fiduciary@test.com')
        principal = User.objects.get(email='principal@test.com')
        processor = User.objects.get(email='processor@test.com')
        purpose = Purpose.objects.filter(fiduciary=fiduciary).first()
        
        # Create and approve a new request
        new_request = ConsentRequest.objects.create(
            fiduciary=fiduciary,
            principal=principal,
            purpose=purpose,
            data_requested=['name', 'email'],
            notes='Test reject request',
            expires_at=timezone.now() + timedelta(days=365)
        )
        
        # CMS approve it first
        new_request.cms_status = CMSStatusChoices.CMS_APPROVED
        new_request.cms_reviewed_by = processor
        new_request.cms_reviewed_at = timezone.now()
        new_request.save()
        
        print(f"Created test request: {new_request.request_id}")
        
        # Reject
        new_request.status = ConsentStatusChoices.REJECTED
        new_request.responded_at = timezone.now()
        new_request.save()
        
        # Verify
        new_request.refresh_from_db()
        if new_request.status == ConsentStatusChoices.REJECTED:
            print(f"✓ Principal Reject successful")
            print(f"  Status: {new_request.status}")
            return True
        else:
            print("✗ Principal Reject failed")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  Consent Request Endpoints Test Suite                     ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    # Create test data
    test_data = create_test_data()
    
    # Run tests
    results = {
        'CMS Approve': test_cms_approve(
            test_data['consent_request'],
            test_data['processor']
        ),
        'CMS Deny': test_cms_deny(
            test_data['consent_request'],
            test_data['processor']
        ),
        'Principal Accept': test_principal_accept(
            test_data['consent_request'],
            test_data['principal']
        ),
        'Principal Reject': test_principal_reject()
    }
    
    # Summary
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
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
