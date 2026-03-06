"""
Management command to seed the database with sample data for testing.

Run with: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from application.models import (
    User, Purpose, ConsentRequest, Consent, Grievance, AuditLog,
    RoleChoices, ConsentStatusChoices, CMSStatusChoices,
    GrievanceStatusChoices, GrievancePriorityChoices, AuditActionChoices
)


class Command(BaseCommand):
    help = 'Seed database with sample data for development and testing'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        # self.clear_data()
        
        # Create users
        users = self.create_users()
        
        # Create purposes
        purposes = self.create_purposes(users)
        
        # Create consent requests
        consent_requests = self.create_consent_requests(users, purposes)
        
        # Create consents
        consents = self.create_consents(users, purposes, consent_requests)
        
        # Create grievances
        grievances = self.create_grievances(users)
        
        # Create audit logs
        self.create_audit_logs(users)
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
        self.print_summary(users, purposes, consent_requests, consents, grievances)

    def clear_data(self):
        """Clear all existing data"""
        AuditLog.objects.all().delete()
        Grievance.objects.all().delete()
        Consent.objects.all().delete()
        ConsentRequest.objects.all().delete()
        Purpose.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write('Cleared existing data')

    def create_users(self):
        """Create sample users for each role"""
        users = {}
        
        # Demo Users (for easy login testing)
        demo_users = [
            {'email': 'principal@example.com', 'username': 'principal', 'role': RoleChoices.PRINCIPAL, 'full_name': 'Demo Principal'},
            {'email': 'fiduciary@example.com', 'username': 'fiduciary', 'role': RoleChoices.FIDUCIARY, 'full_name': 'Demo Fiduciary', 'org_name': 'Demo Corp'},
            {'email': 'processor@example.com', 'username': 'processor', 'role': RoleChoices.PROCESSOR, 'full_name': 'Demo Processor'},
            {'email': 'dpo@example.com', 'username': 'dpo', 'role': RoleChoices.DPO, 'full_name': 'Demo DPO'},
        ]
        
        for data in demo_users:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'username': data['username'],
                    'role': data['role'],
                    'full_name': data['full_name'],
                    'organization_name': data.get('org_name', 'ConsentHub'),
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created demo user: {data["email"]} / password123')
        
        # Data Principals (Individuals)
        principals_data = [
            {'email': 'john.doe@email.com', 'full_name': 'John Doe', 'phone': '+91-9876543210'},
            {'email': 'jane.smith@email.com', 'full_name': 'Jane Smith', 'phone': '+91-9876543211'},
            {'email': 'mike.wilson@email.com', 'full_name': 'Mike Wilson', 'phone': '+91-9876543212'},
            {'email': 'sarah.jones@email.com', 'full_name': 'Sarah Jones', 'phone': '+91-9876543213'},
            {'email': 'amit.patel@email.com', 'full_name': 'Amit Patel', 'phone': '+91-9876543214'},
        ]
        
        users['principals'] = []
        for data in principals_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'username': data['email'].split('@')[0],
                    'role': RoleChoices.PRINCIPAL,
                    'full_name': data['full_name'],
                    'phone': data['phone'],
                    'address': 'Mumbai, India',
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            users['principals'].append(user)
        
        # Data Fiduciaries (Organizations)
        fiduciaries_data = [
            {'email': 'admin@techcorp.com', 'username': 'techcorp_admin', 'full_name': 'TechCorp Admin', 'org_name': 'TechCorp Ltd', 'org_id': 'TECH001'},
            {'email': 'admin@marketpro.com', 'username': 'marketpro_admin', 'full_name': 'MarketPro Admin', 'org_name': 'MarketPro Inc', 'org_id': 'MKT002'},
            {'email': 'admin@datainsights.com', 'username': 'datainsights_admin', 'full_name': 'DataInsights Admin', 'org_name': 'DataInsights Co', 'org_id': 'DATA003'},
        ]
        
        users['fiduciaries'] = []
        for data in fiduciaries_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'username': data['username'],
                    'role': RoleChoices.FIDUCIARY,
                    'full_name': data['full_name'],
                    'organization_name': data['org_name'],
                    'organization_id': data['org_id'],
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            users['fiduciaries'].append(user)
        
        # CMS Processors
        processors_data = [
            {'email': 'cms1@consenthub.com', 'full_name': 'CMS Reviewer 1'},
            {'email': 'cms2@consenthub.com', 'full_name': 'CMS Reviewer 2'},
        ]
        
        users['processors'] = []
        for data in processors_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'username': data['email'].split('@')[0],
                    'role': RoleChoices.PROCESSOR,
                    'full_name': data['full_name'],
                    'organization_name': 'ConsentHub CMS',
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            users['processors'].append(user)
        
        # DPOs
        dpos_data = [
            {'email': 'dpo@consenthub.com', 'full_name': 'DPO Officer'},
            {'email': 'dpo2@consenthub.com', 'full_name': 'DPO Assistant'},
        ]
        
        users['dpos'] = []
        for data in dpos_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'username': data['email'].split('@')[0],
                    'role': RoleChoices.DPO,
                    'full_name': data['full_name'],
                    'organization_name': 'ConsentHub DPO Office',
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            users['dpos'].append(user)
        
        self.stdout.write(f'Created {len(users["principals"])} principals, {len(users["fiduciaries"])} fiduciaries, {len(users["processors"])} processors, {len(users["dpos"])} DPOs')
        return users

    def create_purposes(self, users):
        """Create sample purposes for fiduciaries"""
        purposes = []
        
        purposes_data = [
            {
                'fiduciary': users['fiduciaries'][0],
                'name': 'Marketing Communications',
                'description': 'Send promotional emails and marketing materials',
                'data_categories': ['Email', 'Name', 'Preferences'],
                'lawful_basis': 'Consent',
                'retention_period_days': 365,
            },
            {
                'fiduciary': users['fiduciaries'][0],
                'name': 'Analytics & Performance',
                'description': 'Track usage patterns and improve services',
                'data_categories': ['Usage Data', 'Device Info', 'IP Address'],
                'lawful_basis': 'Legitimate Interest',
                'retention_period_days': 180,
            },
            {
                'fiduciary': users['fiduciaries'][1],
                'name': 'Personalization',
                'description': 'Personalize user experience based on preferences',
                'data_categories': ['Preferences', 'Browsing History', 'Purchase History'],
                'lawful_basis': 'Consent',
                'retention_period_days': 90,
            },
            {
                'fiduciary': users['fiduciaries'][1],
                'name': 'Third-party Sharing',
                'description': 'Share data with trusted partners for better services',
                'data_categories': ['Name', 'Email', 'Phone'],
                'lawful_basis': 'Consent',
                'retention_period_days': 30,
            },
            {
                'fiduciary': users['fiduciaries'][2],
                'name': 'Research & Analytics',
                'description': 'Conduct market research and data analysis',
                'data_categories': ['Usage Data', 'Demographics', 'Survey Responses'],
                'lawful_basis': 'Consent',
                'retention_period_days': 730,
            },
        ]
        
        for data in purposes_data:
            purpose, created = Purpose.objects.get_or_create(
                fiduciary=data['fiduciary'],
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'data_categories': data['data_categories'],
                    'lawful_basis': data['lawful_basis'],
                    'retention_period_days': data['retention_period_days'],
                }
            )
            purposes.append(purpose)
        
        self.stdout.write(f'Created {len(purposes)} purposes')
        return purposes

    def create_consent_requests(self, users, purposes):
        """Create sample consent requests"""
        consent_requests = []
        now = timezone.now()
        
        requests_data = [
            # Pending CMS review
            {
                'fiduciary': users['fiduciaries'][0],
                'principal': users['principals'][0],
                'purpose': purposes[0],
                'data_requested': ['Email', 'Name'],
                'cms_status': CMSStatusChoices.PENDING_CMS,
                'status': ConsentStatusChoices.PENDING,
                'expires_at': now + timedelta(days=30),
            },
            # CMS approved, pending principal
            {
                'fiduciary': users['fiduciaries'][0],
                'principal': users['principals'][1],
                'purpose': purposes[1],
                'data_requested': ['Usage Data', 'Device Info'],
                'cms_status': CMSStatusChoices.CMS_APPROVED,
                'cms_reviewed_by': users['processors'][0],
                'cms_reviewed_at': now - timedelta(days=1),
                'status': ConsentStatusChoices.PENDING,
                'expires_at': now + timedelta(days=7),
            },
            # CMS approved, principal accepted (will create consent)
            {
                'fiduciary': users['fiduciaries'][1],
                'principal': users['principals'][2],
                'purpose': purposes[2],
                'data_requested': ['Preferences', 'Browsing History'],
                'cms_status': CMSStatusChoices.CMS_APPROVED,
                'cms_reviewed_by': users['processors'][0],
                'cms_reviewed_at': now - timedelta(days=5),
                'status': ConsentStatusChoices.ACTIVE,
                'responded_at': now - timedelta(days=4),
                'expires_at': now + timedelta(days=90),
            },
            # CMS denied
            {
                'fiduciary': users['fiduciaries'][1],
                'principal': users['principals'][3],
                'purpose': purposes[3],
                'data_requested': ['Name', 'Email', 'Phone'],
                'cms_status': CMSStatusChoices.CMS_DENIED,
                'cms_reviewed_by': users['processors'][1],
                'cms_reviewed_at': now - timedelta(days=2),
                'cms_notes': 'Purpose not clearly defined for DPDPA compliance',
                'status': ConsentStatusChoices.PENDING,
            },
            # Principal rejected
            {
                'fiduciary': users['fiduciaries'][2],
                'principal': users['principals'][4],
                'purpose': purposes[4],
                'data_requested': ['Usage Data', 'Demographics'],
                'cms_status': CMSStatusChoices.CMS_APPROVED,
                'cms_reviewed_by': users['processors'][0],
                'cms_reviewed_at': now - timedelta(days=3),
                'status': ConsentStatusChoices.REJECTED,
                'responded_at': now - timedelta(days=2),
            },
        ]
        
        for data in requests_data:
            cr, created = ConsentRequest.objects.get_or_create(
                fiduciary=data['fiduciary'],
                principal=data['principal'],
                purpose=data['purpose'],
                defaults={
                    'data_requested': data['data_requested'],
                    'cms_status': data['cms_status'],
                    'cms_reviewed_by': data.get('cms_reviewed_by'),
                    'cms_reviewed_at': data.get('cms_reviewed_at'),
                    'cms_notes': data.get('cms_notes', ''),
                    'status': data['status'],
                    'responded_at': data.get('responded_at'),
                    'expires_at': data.get('expires_at'),
                }
            )
            consent_requests.append(cr)
        
        self.stdout.write(f'Created {len(consent_requests)} consent requests')
        return consent_requests

    def create_consents(self, users, purposes, consent_requests):
        """Create sample consents for approved requests"""
        consents = []
        now = timezone.now()
        
        # Find active consent requests and create consents
        for cr in consent_requests:
            if cr.status == ConsentStatusChoices.ACTIVE:
                consent, created = Consent.objects.get_or_create(
                    consent_request=cr,
                    defaults={
                        'principal': cr.principal,
                        'fiduciary': cr.fiduciary,
                        'purpose': cr.purpose,
                        'data_categories': cr.data_requested,
                        'status': ConsentStatusChoices.ACTIVE,
                        'expires_at': cr.expires_at,
                    }
                )
                consents.append(consent)
        
        # Create some additional historical consents
        additional_consents = [
            {
                'principal': users['principals'][0],
                'fiduciary': users['fiduciaries'][0],
                'purpose': purposes[0],
                'data_categories': ['Email'],
                'status': ConsentStatusChoices.REVOKED,
                'revoked_at': now - timedelta(days=10),
                'revocation_reason': 'No longer want marketing emails',
            },
            {
                'principal': users['principals'][1],
                'fiduciary': users['fiduciaries'][2],
                'purpose': purposes[4],
                'data_categories': ['Usage Data'],
                'status': ConsentStatusChoices.EXPIRED,
                'expires_at': now - timedelta(days=5),
            },
        ]
        
        for data in additional_consents:
            # Create a dummy consent request first
            cr = ConsentRequest.objects.create(
                fiduciary=data['fiduciary'],
                principal=data['principal'],
                purpose=data['purpose'],
                data_requested=data['data_categories'],
                cms_status=CMSStatusChoices.CMS_APPROVED,
                status=data['status'],
            )
            
            consent = Consent.objects.create(
                consent_request=cr,
                principal=data['principal'],
                fiduciary=data['fiduciary'],
                purpose=data['purpose'],
                data_categories=data['data_categories'],
                status=data['status'],
                expires_at=data.get('expires_at'),
                revoked_at=data.get('revoked_at'),
                revocation_reason=data.get('revocation_reason'),
            )
            consents.append(consent)
        
        self.stdout.write(f'Created {len(consents)} consents')
        return consents

    def create_grievances(self, users):
        """Create sample grievances"""
        grievances = []
        now = timezone.now()
        
        grievances_data = [
            {
                'complainant': users['principals'][0],
                'against_entity': users['fiduciaries'][0],
                'subject': 'Unauthorized data sharing',
                'description': 'I believe my data was shared with third parties without my consent.',
                'category': 'Data Breach',
                'priority': GrievancePriorityChoices.HIGH,
                'status': GrievanceStatusChoices.OPEN,
            },
            {
                'complainant': users['principals'][1],
                'against_entity': users['fiduciaries'][1],
                'assigned_dpo': users['dpos'][0],
                'subject': 'Unable to withdraw consent',
                'description': 'The withdraw consent feature is not working on the website.',
                'category': 'Technical Issue',
                'priority': GrievancePriorityChoices.MEDIUM,
                'status': GrievanceStatusChoices.IN_PROGRESS,
                'acknowledged_at': now - timedelta(days=1),
            },
            {
                'complainant': users['principals'][2],
                'against_entity': users['fiduciaries'][2],
                'assigned_dpo': users['dpos'][0],
                'subject': 'Delayed response to data access request',
                'description': 'It has been over 30 days since I requested my data copy.',
                'category': 'Data Access',
                'priority': GrievancePriorityChoices.CRITICAL,
                'status': GrievanceStatusChoices.ESCALATED,
                'acknowledged_at': now - timedelta(days=5),
                'sla_deadline': now - timedelta(days=2),
            },
            {
                'complainant': users['principals'][3],
                'subject': 'General inquiry about data usage',
                'description': 'I would like to know how my data is being used across all platforms.',
                'category': 'Inquiry',
                'priority': GrievancePriorityChoices.LOW,
                'status': GrievanceStatusChoices.RESOLVED,
                'assigned_dpo': users['dpos'][1],
                'acknowledged_at': now - timedelta(days=7),
                'resolved_at': now - timedelta(days=3),
                'resolution': 'Provided detailed data usage report to the complainant.',
            },
        ]
        
        for data in grievances_data:
            grievance, created = Grievance.objects.get_or_create(
                complainant=data['complainant'],
                subject=data['subject'],
                defaults={
                    'against_entity': data.get('against_entity'),
                    'assigned_dpo': data.get('assigned_dpo'),
                    'description': data['description'],
                    'category': data['category'],
                    'priority': data['priority'],
                    'status': data['status'],
                    'acknowledged_at': data.get('acknowledged_at'),
                    'resolved_at': data.get('resolved_at'),
                    'resolution': data.get('resolution'),
                    'sla_deadline': data.get('sla_deadline'),
                }
            )
            grievances.append(grievance)
        
        self.stdout.write(f'Created {len(grievances)} grievances')
        return grievances

    def create_audit_logs(self, users):
        """Create sample audit logs"""
        logs_count = 0
        now = timezone.now()
        
        # Login events
        for user in users['principals'][:3]:
            AuditLog.objects.create(
                user=user,
                action=AuditActionChoices.LOGIN,
                entity_type='auth',
                details={'event': 'signin', 'method': 'email'},
            )
            logs_count += 1
        
        # Consent events
        AuditLog.objects.create(
            user=users['principals'][2],
            action=AuditActionChoices.CONSENT_GRANTED,
            entity_type='consent',
            details={'purpose': 'Personalization', 'fiduciary': 'MarketPro Inc'},
        )
        logs_count += 1
        
        AuditLog.objects.create(
            user=users['principals'][0],
            action=AuditActionChoices.CONSENT_REVOKED,
            entity_type='consent',
            details={'purpose': 'Marketing Communications', 'reason': 'No longer want marketing emails'},
        )
        logs_count += 1
        
        # Grievance events
        AuditLog.objects.create(
            user=users['principals'][0],
            action=AuditActionChoices.GRIEVANCE_RAISED,
            entity_type='grievance',
            details={'subject': 'Unauthorized data sharing'},
        )
        logs_count += 1
        
        AuditLog.objects.create(
            user=users['dpos'][1],
            action=AuditActionChoices.GRIEVANCE_RESOLVED,
            entity_type='grievance',
            details={'subject': 'General inquiry about data usage'},
        )
        logs_count += 1
        
        self.stdout.write(f'Created {logs_count} audit logs')

    def print_summary(self, users, purposes, consent_requests, consents, grievances):
        """Print a summary of created data"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('SEED DATA SUMMARY')
        self.stdout.write('='*50)
        self.stdout.write(f'\nUsers created:')
        self.stdout.write(f'  - Principals: {len(users["principals"])}')
        self.stdout.write(f'  - Fiduciaries: {len(users["fiduciaries"])}')
        self.stdout.write(f'  - Processors (CMS): {len(users["processors"])}')
        self.stdout.write(f'  - DPOs: {len(users["dpos"])}')
        self.stdout.write(f'\nPurposes: {len(purposes)}')
        self.stdout.write(f'Consent Requests: {len(consent_requests)}')
        self.stdout.write(f'Consents: {len(consents)}')
        self.stdout.write(f'Grievances: {len(grievances)}')
        self.stdout.write(f'\nTest Login Credentials:')
        self.stdout.write(f'  Email: john.doe@email.com (Principal)')
        self.stdout.write(f'  Email: admin@techcorp.com (Fiduciary)')
        self.stdout.write(f'  Email: cms1@consenthub.com (Processor/CMS)')
        self.stdout.write(f'  Email: dpo@consenthub.com (DPO)')
        self.stdout.write(f'  Password: password123 (for all users)')
        self.stdout.write('='*50 + '\n')
