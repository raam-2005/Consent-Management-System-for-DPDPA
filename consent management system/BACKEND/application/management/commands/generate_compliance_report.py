"""
Management command to generate weekly compliance reports.

This command should be run weekly (e.g., via cron or Windows Task Scheduler):

    python manage.py generate_compliance_report

What it does:
1. Generates compliance statistics
2. Identifies issues (expired consents, SLA breaches, pending requests)
3. Creates a report file (JSON format)
4. Optionally sends email summary

Usage:
    python manage.py generate_compliance_report                    # Generate report
    python manage.py generate_compliance_report --email admin@example.com  # With email
    python manage.py generate_compliance_report --output report.json       # Custom output
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Avg
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
import json
import os

from application.models import (
    User, Consent, ConsentRequest, Grievance, DataPrincipalRightsRequest,
    AuditLog, RoleChoices, ConsentStatusChoices, GrievanceStatusChoices,
    DataRightsRequestStatusChoices
)


class Command(BaseCommand):
    help = 'Generate weekly compliance report for DPDPA system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send report summary',
        )
        parser.add_argument(
            '--output',
            type=str,
            default='compliance_report.json',
            help='Output file name for the report',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to include in the report (default: 7)',
        )

    def handle(self, *args, **options):
        email = options.get('email')
        output_file = options.get('output')
        days = options.get('days')
        
        self.stdout.write(self.style.SUCCESS(f'\n{"="*60}'))
        self.stdout.write(self.style.SUCCESS('DPDPA COMPLIANCE REPORT GENERATOR'))
        self.stdout.write(self.style.SUCCESS(f'{"="*60}\n'))
        
        # Calculate date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        self.stdout.write(f'Report Period: {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}')
        
        # Generate report data
        report = self.generate_report(start_date, end_date)
        
        # Save to file
        self.save_report(report, output_file)
        
        # Print summary
        self.print_summary(report)
        
        # Send email if requested
        if email:
            self.send_email_summary(report, email)
        
        return json.dumps(report, indent=2, default=str)

    def generate_report(self, start_date, end_date):
        """Generate comprehensive compliance report"""
        
        report = {
            'report_id': f'COMPLIANCE-{timezone.now().strftime("%Y%m%d-%H%M%S")}',
            'generated_at': timezone.now().isoformat(),
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
            },
            'summary': {},
            'users': {},
            'consents': {},
            'grievances': {},
            'rights_requests': {},
            'audit': {},
            'issues': [],
            'recommendations': [],
        }
        
        # 1. User Statistics
        report['users'] = self.get_user_stats()
        
        # 2. Consent Statistics
        report['consents'] = self.get_consent_stats(start_date, end_date)
        
        # 3. Grievance Statistics
        report['grievances'] = self.get_grievance_stats(start_date, end_date)
        
        # 4. Rights Request Statistics
        report['rights_requests'] = self.get_rights_request_stats(start_date, end_date)
        
        # 5. Audit Statistics
        report['audit'] = self.get_audit_stats(start_date, end_date)
        
        # 6. Calculate Compliance Score
        report['summary'] = self.calculate_compliance_score(report)
        
        # 7. Identify Issues
        report['issues'] = self.identify_issues(report)
        
        # 8. Generate Recommendations
        report['recommendations'] = self.generate_recommendations(report)
        
        return report

    def get_user_stats(self):
        """Get user statistics by role"""
        return {
            'total_users': User.objects.count(),
            'by_role': {
                'principals': User.objects.filter(role=RoleChoices.PRINCIPAL).count(),
                'fiduciaries': User.objects.filter(role=RoleChoices.FIDUCIARY).count(),
                'processors': User.objects.filter(role=RoleChoices.PROCESSOR).count(),
                'dpos': User.objects.filter(role=RoleChoices.DPO).count(),
            },
            'active_users': User.objects.filter(is_active=True).count(),
        }

    def get_consent_stats(self, start_date, end_date):
        """Get consent statistics"""
        total = Consent.objects.count()
        active = Consent.objects.filter(status=ConsentStatusChoices.ACTIVE).count()
        expired = Consent.objects.filter(status=ConsentStatusChoices.EXPIRED).count()
        revoked = Consent.objects.filter(status=ConsentStatusChoices.REVOKED).count()
        
        # Expiring soon (next 7 days)
        expiring_soon = Consent.objects.filter(
            status=ConsentStatusChoices.ACTIVE,
            expires_at__lte=timezone.now() + timedelta(days=7),
            expires_at__gt=timezone.now()
        ).count()
        
        # New consents in period
        new_in_period = Consent.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).count()
        
        # Pending requests
        pending_requests = ConsentRequest.objects.filter(
            status=ConsentStatusChoices.PENDING
        ).count()
        
        return {
            'total': total,
            'active': active,
            'expired': expired,
            'revoked': revoked,
            'expiring_soon': expiring_soon,
            'new_in_period': new_in_period,
            'pending_requests': pending_requests,
            'active_rate': round((active / total * 100) if total > 0 else 0, 2),
        }

    def get_grievance_stats(self, start_date, end_date):
        """Get grievance statistics"""
        total = Grievance.objects.count()
        open_grievances = Grievance.objects.filter(status=GrievanceStatusChoices.OPEN).count()
        in_progress = Grievance.objects.filter(status=GrievanceStatusChoices.IN_PROGRESS).count()
        resolved = Grievance.objects.filter(status=GrievanceStatusChoices.RESOLVED).count()
        escalated = Grievance.objects.filter(status=GrievanceStatusChoices.ESCALATED).count()
        
        # SLA breached
        sla_breached = Grievance.objects.filter(sla_breached=True).count()
        
        # New in period
        new_in_period = Grievance.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).count()
        
        # Average resolution time
        resolved_grievances = Grievance.objects.filter(
            status=GrievanceStatusChoices.RESOLVED,
            resolved_at__isnull=False
        )
        
        avg_resolution_hours = 0
        if resolved_grievances.exists():
            total_hours = sum([
                (g.resolved_at - g.filed_at).total_seconds() / 3600
                for g in resolved_grievances
                if g.resolved_at and g.filed_at
            ])
            avg_resolution_hours = round(total_hours / resolved_grievances.count(), 2)
        
        return {
            'total': total,
            'open': open_grievances,
            'in_progress': in_progress,
            'resolved': resolved,
            'escalated': escalated,
            'sla_breached': sla_breached,
            'new_in_period': new_in_period,
            'avg_resolution_hours': avg_resolution_hours,
            'resolution_rate': round((resolved / total * 100) if total > 0 else 0, 2),
        }

    def get_rights_request_stats(self, start_date, end_date):
        """Get data rights request statistics"""
        total = DataPrincipalRightsRequest.objects.count()
        pending = DataPrincipalRightsRequest.objects.filter(
            status=DataRightsRequestStatusChoices.PENDING
        ).count()
        completed = DataPrincipalRightsRequest.objects.filter(
            status=DataRightsRequestStatusChoices.COMPLETED
        ).count()
        
        # By type
        by_type = dict(DataPrincipalRightsRequest.objects.values('request_type').annotate(
            count=Count('id')
        ).values_list('request_type', 'count'))
        
        return {
            'total': total,
            'pending': pending,
            'completed': completed,
            'by_type': by_type,
            'completion_rate': round((completed / total * 100) if total > 0 else 0, 2),
        }

    def get_audit_stats(self, start_date, end_date):
        """Get audit log statistics"""
        total_actions = AuditLog.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).count()
        
        # Actions by type
        actions_by_type = dict(AuditLog.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).values('action').annotate(count=Count('id')).values_list('action', 'count'))
        
        return {
            'total_actions_in_period': total_actions,
            'actions_by_type': actions_by_type,
        }

    def calculate_compliance_score(self, report):
        """Calculate overall compliance score (0-100)"""
        score = 100
        issues = []
        
        # Deduct for SLA breaches
        sla_breached = report['grievances'].get('sla_breached', 0)
        if sla_breached > 0:
            deduction = min(sla_breached * 5, 20)  # Max 20 points deduction
            score -= deduction
            issues.append(f'SLA breaches: -{deduction} points')
        
        # Deduct for pending grievances
        open_grievances = report['grievances'].get('open', 0)
        if open_grievances > 10:
            deduction = min((open_grievances - 10), 10)
            score -= deduction
            issues.append(f'High open grievances: -{deduction} points')
        
        # Deduct for pending rights requests
        pending_rights = report['rights_requests'].get('pending', 0)
        if pending_rights > 5:
            deduction = min((pending_rights - 5) * 2, 10)
            score -= deduction
            issues.append(f'Pending rights requests: -{deduction} points')
        
        # Deduct for expiring consents (should be notified)
        expiring = report['consents'].get('expiring_soon', 0)
        if expiring > 10:
            deduction = min((expiring - 10), 10)
            score -= deduction
            issues.append(f'Many expiring consents: -{deduction} points')
        
        return {
            'compliance_score': max(score, 0),
            'score_breakdown': issues,
            'rating': 'Excellent' if score >= 90 else 'Good' if score >= 70 else 'Fair' if score >= 50 else 'Poor',
        }

    def identify_issues(self, report):
        """Identify compliance issues"""
        issues = []
        
        if report['grievances'].get('sla_breached', 0) > 0:
            issues.append({
                'severity': 'critical',
                'type': 'sla_breach',
                'message': f"{report['grievances']['sla_breached']} grievance(s) have breached SLA deadlines",
                'recommendation': 'Immediate attention required. Assign DPOs to resolve breached grievances.',
            })
        
        if report['consents'].get('expiring_soon', 0) > 0:
            issues.append({
                'severity': 'warning',
                'type': 'expiring_consents',
                'message': f"{report['consents']['expiring_soon']} consent(s) expiring in next 7 days",
                'recommendation': 'Send renewal notices to data principals.',
            })
        
        if report['rights_requests'].get('pending', 0) > 0:
            issues.append({
                'severity': 'warning',
                'type': 'pending_rights_requests',
                'message': f"{report['rights_requests']['pending']} data rights request(s) pending",
                'recommendation': 'Process pending rights requests within DPDPA timeline.',
            })
        
        if report['grievances'].get('open', 0) > 10:
            issues.append({
                'severity': 'warning',
                'type': 'high_grievances',
                'message': f"{report['grievances']['open']} open grievances require attention",
                'recommendation': 'Allocate more resources to grievance resolution.',
            })
        
        return issues

    def generate_recommendations(self, report):
        """Generate compliance recommendations"""
        recommendations = []
        
        score = report['summary'].get('compliance_score', 0)
        
        if score < 70:
            recommendations.append('Priority: Address all SLA breaches immediately.')
        
        if report['grievances'].get('avg_resolution_hours', 0) > 48:
            recommendations.append('Consider streamlining grievance resolution process.')
        
        if report['consents'].get('active_rate', 0) < 50:
            recommendations.append('Low active consent rate. Review consent request process.')
        
        recommendations.append('Run expire_consents command daily to maintain data hygiene.')
        recommendations.append('Review and update data retention policies quarterly.')
        
        return recommendations

    def save_report(self, report, output_file):
        """Save report to JSON file"""
        reports_dir = settings.BASE_DIR / 'reports'
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        filepath = reports_dir / output_file
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.stdout.write(self.style.SUCCESS(f'\nReport saved to: {filepath}'))

    def print_summary(self, report):
        """Print report summary to console"""
        self.stdout.write(f'\n{"="*60}')
        self.stdout.write('COMPLIANCE SUMMARY')
        self.stdout.write(f'{"="*60}')
        
        summary = report['summary']
        self.stdout.write(f'Compliance Score: {summary["compliance_score"]}/100 ({summary["rating"]})')
        
        self.stdout.write(f'\nConsents:')
        self.stdout.write(f'  - Total: {report["consents"]["total"]}')
        self.stdout.write(f'  - Active: {report["consents"]["active"]}')
        self.stdout.write(f'  - Expiring Soon: {report["consents"]["expiring_soon"]}')
        
        self.stdout.write(f'\nGrievances:')
        self.stdout.write(f'  - Open: {report["grievances"]["open"]}')
        self.stdout.write(f'  - SLA Breached: {report["grievances"]["sla_breached"]}')
        
        if report['issues']:
            self.stdout.write(f'\n⚠️  Issues Found: {len(report["issues"])}')
            for issue in report['issues']:
                self.stdout.write(f'  [{issue["severity"].upper()}] {issue["message"]}')

    def send_email_summary(self, report, email):
        """Send email summary of the report"""
        try:
            subject = f'DPDPA Compliance Report - {report["report_id"]}'
            summary = report['summary']
            
            message = f"""
DPDPA Compliance Report
=======================

Report ID: {report['report_id']}
Generated: {report['generated_at']}

COMPLIANCE SCORE: {summary['compliance_score']}/100 ({summary['rating']})

SUMMARY
-------
Users: {report['users']['total_users']}
Active Consents: {report['consents']['active']}
Expiring Soon: {report['consents']['expiring_soon']}
Open Grievances: {report['grievances']['open']}
SLA Breaches: {report['grievances']['sla_breached']}

ISSUES: {len(report['issues'])}
"""
            for issue in report['issues']:
                message += f"\n[{issue['severity'].upper()}] {issue['message']}"
            
            message += "\n\nThis is an automated report from the DPDPA Consent Management System."
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            self.stdout.write(self.style.SUCCESS(f'\nEmail sent to: {email}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nFailed to send email: {e}'))
