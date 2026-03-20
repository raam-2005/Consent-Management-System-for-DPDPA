"""Core business logic for consent workflows."""

from .consent_logic import (
	capture_consent_response,
	review_consent_request,
	validate_consent_request_input,
)

__all__ = [
	"validate_consent_request_input",
	"review_consent_request",
	"capture_consent_response",
]

