"""
Management command to expire consents and check SLA deadlines.

This command should be run periodically (e.g., daily via cron or Windows Task Scheduler):

    python manage.py expire_consents

What it does:
1. Expires all consents past their expiry date
2. Marks grievances as SLA breached if past deadline
3. Creates audit logs for expired consents

For production, set up a scheduled task:
- Linux: Add to crontab (e.g., `0 0 * * * python manage.py expire_consents`)
- Windows: Use Task Scheduler
- Or use Celery Beat for more advanced scheduling
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from application.models import (
    Consent, Grievance, DataPrincipalRightsRequest,
    ConsentStatusChoices, GrievanceStatusChoices,
    DataRightsRequestStatusChoices, AuditLog, AuditActionChoices
)


class Command(BaseCommand):
    help = 'Expire consents past their expiry date and check SLA deadlines'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be made'))
        
        # 1. Expire consents
        expired_count = self.expire_consents(dry_run)
        
        # 2. Check grievance SLA deadlines
        sla_breached_count = self.check_grievance_sla(dry_run)
        
        # 3. Check rights request SLA deadlines
        rights_sla_count = self.check_rights_request_sla(dry_run)
        
        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(f'Consents expired: {expired_count}')
        self.stdout.write(f'Grievances with SLA breach: {sla_breached_count}')
        self.stdout.write(f'Rights requests with SLA breach: {rights_sla_count}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN - No changes were made'))

    def expire_consents(self, dry_run):
        """Expire all consents past their expiry date"""
        self.stdout.write('\n--- Checking for expired consents ---')
        
        now = timezone.now()
        expiring_consents = Consent.objects.filter(
            status=ConsentStatusChoices.ACTIVE,
            expires_at__lt=now
        )
        
        count = expiring_consents.count()
        
        if count == 0:
            self.stdout.write('No consents to expire')
            return 0
        
        self.stdout.write(f'Found {count} consents to expire')
        
        if not dry_run:
            for consent in expiring_consents:
                # Expire the consent
                consent.expire()
                
                # Create audit log
                AuditLog.objects.create(
                    user=None,  # System action
                    action=AuditActionChoices.CONSENT_EXPIRED,
                    entity_type='consent',
                    entity_id=str(consent.id),
                    details={
                        'consent_id': consent.consent_id,
                        'expired_at': now.isoformat(),
                        'principal': str(consent.principal.email),
                        'fiduciary': str(consent.fiduciary.organization_name or consent.fiduciary.email)
                    }
                )
                
                self.stdout.write(
                    self.style.WARNING(f'  Expired: {consent.consent_id}')
                )
        
        return count

    def check_grievance_sla(self, dry_run):
        """Check and mark grievances that have breached SLA"""
        self.stdout.write('\n--- Checking grievance SLA deadlines ---')
        
        now = timezone.now()
        overdue_grievances = Grievance.objects.filter(
            sla_breached=False,
            sla_deadline__lt=now
        ).exclude(
            status__in=[
                GrievanceStatusChoices.RESOLVED,
                GrievanceStatusChoices.CLOSED
            ]
        )
        
        count = overdue_grievances.count()
        
        if count == 0:
            self.stdout.write('No grievances with SLA breach')
            return 0
        
        self.stdout.write(f'Found {count} grievances past SLA deadline')
        
        if not dry_run:
            for grievance in overdue_grievances:
                grievance.sla_breached = True
                grievance.save()
                
                self.stdout.write(
                    self.style.WARNING(f'  SLA Breached: {grievance.grievance_id}')
                )
        
        return count

    def check_rights_request_sla(self, dry_run):
        """Check and flag rights requests past SLA deadline"""
        self.stdout.write('\n--- Checking rights request SLA deadlines ---')
        
        now = timezone.now()
        overdue_requests = DataPrincipalRightsRequest.objects.filter(
            sla_deadline__lt=now
        ).exclude(
            status__in=[
                DataRightsRequestStatusChoices.COMPLETED,
                DataRightsRequestStatusChoices.REJECTED
            ]
        )
        
        count = overdue_requests.count()
        
        if count == 0:
            self.stdout.write('No rights requests past SLA deadline')
            return 0
        
        self.stdout.write(f'Found {count} rights requests past SLA deadline')
        
        for request in overdue_requests:
            self.stdout.write(
                self.style.WARNING(f'  Overdue: {request.request_id}')
            )
        
        return count
