"""Core consent business logic: validation, review, and consent capture."""

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from application.models import (
	CMSStatusChoices,
	Consent,
	ConsentLifecycleChoices,
	ConsentRequest,
	ConsentStatusChoices,
	RoleChoices,
)


def validate_consent_request_input(fiduciary, principal, purpose, data_requested, expires_at=None):
	"""Validate business rules before creating a consent request."""
	if not fiduciary or fiduciary.role != RoleChoices.FIDUCIARY:
		raise ValidationError("Only a fiduciary can create consent requests")

	if not principal or principal.role != RoleChoices.PRINCIPAL:
		raise ValidationError("Consent request must target a valid data principal")

	if not purpose:
		raise ValidationError("Purpose is required")

	if purpose.fiduciary_id != fiduciary.id:
		raise ValidationError("Purpose does not belong to the requesting fiduciary")

	if not purpose.is_active:
		raise ValidationError("Cannot create consent request for an inactive purpose")

	if not isinstance(data_requested, list) or not data_requested:
		raise ValidationError("data_requested must be a non-empty list")

	allowed_categories = set(purpose.data_categories or [])
	invalid_categories = [cat for cat in data_requested if cat not in allowed_categories]
	if invalid_categories:
		raise ValidationError(f"Invalid data categories requested: {', '.join(invalid_categories)}")

	if expires_at:
		if expires_at <= timezone.now():
			raise ValidationError("expires_at must be in the future")

		max_expiry = timezone.now() + timedelta(days=purpose.retention_period_days)
		if expires_at > max_expiry:
			raise ValidationError(
				f"expires_at cannot exceed purpose retention period ({purpose.retention_period_days} days)"
			)

	duplicate_exists = ConsentRequest.objects.filter(
		principal=principal,
		fiduciary=fiduciary,
		purpose=purpose,
		cms_status__in=[CMSStatusChoices.PENDING_CMS, CMSStatusChoices.CMS_APPROVED],
		status=ConsentStatusChoices.PENDING,
	).exists()
	if duplicate_exists:
		raise ValidationError("A pending consent request already exists for this principal and purpose")


def review_consent_request(consent_request, reviewer, approve, notes=""):
	"""Handle CMS review decision for a consent request."""
	if reviewer.role not in [RoleChoices.PROCESSOR, RoleChoices.DPO]:
		raise ValidationError("Only Processor or DPO can review consent requests")

	if consent_request.cms_status != CMSStatusChoices.PENDING_CMS:
		raise ValidationError("Request has already been reviewed")

	with transaction.atomic():
		consent_request.cms_reviewed_by = reviewer
		consent_request.cms_reviewed_at = timezone.now()
		consent_request.cms_notes = (notes or "").strip()

		if approve:
			consent_request.cms_status = CMSStatusChoices.CMS_APPROVED
		else:
			consent_request.cms_status = CMSStatusChoices.CMS_DENIED
			consent_request.status = ConsentStatusChoices.REJECTED
			consent_request.responded_at = timezone.now()

		consent_request.save(
			update_fields=[
				"cms_reviewed_by",
				"cms_reviewed_at",
				"cms_notes",
				"cms_status",
				"status",
				"responded_at",
				"updated_at",
			]
		)


def capture_consent_response(consent_request, principal, accepted):
	"""Capture principal response and create a Consent if accepted."""
	if consent_request.principal_id != principal.id:
		raise ValidationError("Only the data principal can respond to this request")

	if consent_request.cms_status != CMSStatusChoices.CMS_APPROVED:
		raise ValidationError("Request is not CMS approved")

	if consent_request.status != ConsentStatusChoices.PENDING:
		raise ValidationError("Request has already been responded to")

	with transaction.atomic():
		if accepted:
			consent_request.status = ConsentStatusChoices.ACTIVE
			consent_request.responded_at = timezone.now()
			consent_request.save(update_fields=["status", "responded_at", "updated_at"])

			consent = Consent.objects.create(
				consent_request=consent_request,
				principal=consent_request.principal,
				fiduciary=consent_request.fiduciary,
				purpose=consent_request.purpose,
				data_categories=consent_request.data_requested,
				status=ConsentStatusChoices.ACTIVE,
				lifecycle_state=ConsentLifecycleChoices.ACTIVE,
				expires_at=consent_request.expires_at,
			)
			return consent

		consent_request.status = ConsentStatusChoices.REJECTED
		consent_request.responded_at = timezone.now()
		consent_request.save(update_fields=["status", "responded_at", "updated_at"])
		return None

