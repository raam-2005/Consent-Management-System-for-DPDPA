"""
Input Validation and Security Utilities for DPDPA Consent Management System

This module provides security-focused validation functions to:
- Validate and sanitize user input
- Prevent common security vulnerabilities
- Ensure data integrity

Use these validators in serializers and views for consistent security.
"""

import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


# ============================================
# TEXT SANITIZATION
# ============================================
def sanitize_text(text):
    """
    Sanitize text input by removing potentially dangerous characters.
    
    Args:
        text: Input text string
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return text
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def sanitize_html(text):
    """
    Remove HTML tags from text.
    Use this for fields that should not contain HTML.
    
    Args:
        text: Input text that may contain HTML
        
    Returns:
        str: Text with HTML tags removed
    """
    if not text:
        return text
    
    # Simple HTML tag removal
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


# ============================================
# EMAIL VALIDATION
# ============================================
def validate_email_address(email):
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        str: Lowercase email
        
    Raises:
        ValidationError: If email is invalid
    """
    if not email:
        raise ValidationError("Email is required")
    
    email = email.lower().strip()
    
    try:
        validate_email(email)
    except ValidationError:
        raise ValidationError("Invalid email format")
    
    # Additional checks
    if '..' in email:
        raise ValidationError("Invalid email format")
    
    return email


# ============================================
# PASSWORD VALIDATION
# ============================================
def validate_password_strength(password):
    """
    Validate password strength requirements.
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password: Password to validate
        
    Returns:
        str: Password if valid
        
    Raises:
        ValidationError: If password doesn't meet requirements
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    if errors:
        raise ValidationError(errors)
    
    return password


# ============================================
# PHONE NUMBER VALIDATION
# ============================================
def validate_phone_number(phone):
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        str: Cleaned phone number
        
    Raises:
        ValidationError: If phone number is invalid
    """
    if not phone:
        return phone
    
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
    
    # Check if it contains only digits and optional + prefix
    if not re.match(r'^\+?\d{10,15}$', cleaned):
        raise ValidationError("Invalid phone number format")
    
    return cleaned


# ============================================
# UUID VALIDATION
# ============================================
def validate_uuid(uuid_string):
    """
    Validate UUID format.
    
    Args:
        uuid_string: UUID string to validate
        
    Returns:
        str: UUID string if valid
        
    Raises:
        ValidationError: If UUID is invalid
    """
    if not uuid_string:
        raise ValidationError("UUID is required")
    
    uuid_regex = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    
    if not uuid_regex.match(str(uuid_string)):
        raise ValidationError("Invalid UUID format")
    
    return str(uuid_string)


# ============================================
# ROLE VALIDATION
# ============================================
VALID_ROLES = ['principal', 'fiduciary', 'processor', 'dpo']

def validate_role(role):
    """
    Validate user role.
    
    Args:
        role: Role to validate
        
    Returns:
        str: Role if valid
        
    Raises:
        ValidationError: If role is invalid
    """
    if not role:
        raise ValidationError("Role is required")
    
    role = role.lower().strip()
    
    if role not in VALID_ROLES:
        raise ValidationError(f"Invalid role. Must be one of: {', '.join(VALID_ROLES)}")
    
    return role


# ============================================
# JSON DATA VALIDATION
# ============================================
def validate_json_field(data, required_keys=None, max_depth=5):
    """
    Validate JSON data structure.
    
    Args:
        data: JSON data (dict or list)
        required_keys: List of required keys (for dict)
        max_depth: Maximum nesting depth allowed
        
    Returns:
        data: Validated data
        
    Raises:
        ValidationError: If data is invalid
    """
    def check_depth(obj, current_depth=0):
        if current_depth > max_depth:
            raise ValidationError(f"JSON nesting too deep (max {max_depth} levels)")
        
        if isinstance(obj, dict):
            for value in obj.values():
                check_depth(value, current_depth + 1)
        elif isinstance(obj, list):
            for item in obj:
                check_depth(item, current_depth + 1)
    
    check_depth(data)
    
    if required_keys and isinstance(data, dict):
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            raise ValidationError(f"Missing required keys: {', '.join(missing_keys)}")
    
    return data


# ============================================
# REQUEST DATA VALIDATORS
# ============================================
def validate_consent_request_data(data):
    """
    Validate consent request data.
    
    Args:
        data: Request data dict
        
    Returns:
        dict: Validated data
        
    Raises:
        ValidationError: If data is invalid
    """
    required_fields = ['principal', 'purpose']
    
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValidationError(f"{field} is required")
    
    # Validate data_requested if present
    if 'data_requested' in data:
        if not isinstance(data['data_requested'], list):
            raise ValidationError("data_requested must be a list")
    
    return data


def validate_grievance_data(data):
    """
    Validate grievance submission data.
    
    Args:
        data: Grievance data dict
        
    Returns:
        dict: Validated data
        
    Raises:
        ValidationError: If data is invalid
    """
    required_fields = ['subject', 'description']
    
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValidationError(f"{field} is required")
    
    # Validate subject length
    if len(data['subject']) > 255:
        raise ValidationError("Subject must be 255 characters or less")
    
    # Validate description length
    if len(data['description']) < 10:
        raise ValidationError("Description must be at least 10 characters")
    
    return data


# ============================================
# RATE LIMITING HELPERS
# ============================================
class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""
    pass


def check_rate_limit(cache_key, max_requests=10, window_seconds=60):
    """
    Check if rate limit has been exceeded.
    
    Args:
        cache_key: Unique key for the rate limit (e.g., user_id + action)
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds
        
    Returns:
        bool: True if within limit
        
    Raises:
        RateLimitExceeded: If limit exceeded
        
    Note: Requires Django cache to be configured
    """
    from django.core.cache import cache
    
    current_count = cache.get(cache_key, 0)
    
    if current_count >= max_requests:
        raise RateLimitExceeded(
            f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds."
        )
    
    # Increment counter
    cache.set(cache_key, current_count + 1, window_seconds)
    
    return True


# ============================================
# XSS PREVENTION
# ============================================
def escape_html_entities(text):
    """
    Escape HTML entities to prevent XSS attacks.
    
    Args:
        text: Text to escape
        
    Returns:
        str: Escaped text
    """
    if not text:
        return text
    
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&#x27;",
        ">": "&gt;",
        "<": "&lt;",
    }
    
    return "".join(html_escape_table.get(c, c) for c in text)


# ============================================
# SQL INJECTION PREVENTION
# ============================================
def validate_sort_field(field, allowed_fields):
    """
    Validate sort field to prevent SQL injection.
    
    Args:
        field: Field name to sort by
        allowed_fields: List of allowed field names
        
    Returns:
        str: Field name if valid
        
    Raises:
        ValidationError: If field is not allowed
    """
    if not field:
        return None
    
    # Remove potential direction prefix
    clean_field = field.lstrip('-')
    
    if clean_field not in allowed_fields:
        raise ValidationError(f"Invalid sort field. Must be one of: {', '.join(allowed_fields)}")
    
    return field
