"""
Backend Validation Utilities
Comprehensive validation for security and data integrity
"""

import re
import html
from typing import Optional, List, Any
from pydantic import field_validator, model_validator
from fastapi import HTTPException, status


# ==================== REGEX PATTERNS ====================

PATTERNS = {
    # Password: min 8 chars, 1 upper, 1 lower, 1 digit, 1 special
    "password_strong": r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
    
    # Phone: Indian format or international
    "phone": r"^(\+91[\-\s]?)?[0]?(91)?[6789]\d{9}$|^\+?[1-9]\d{1,14}$",
    
    # GST Number (India)
    "gst": r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$",
    
    # PAN Number (India)
    "pan": r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$",
    
    # Pincode (India)
    "pincode": r"^[1-9][0-9]{5}$",
    
    # URL
    "url": r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$",
    
    # Alphanumeric with spaces
    "alphanumeric_space": r"^[a-zA-Z0-9\s]+$",
    
    # Name (letters, spaces, hyphens, apostrophes)
    "name": r"^[a-zA-Z\s\-\'\.]+$",
    
    # Username (alphanumeric, underscore, hyphen)
    "username": r"^[a-zA-Z0-9_\-]{3,30}$",
    
    # Slug (URL-friendly)
    "slug": r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
}


# ==================== VALIDATION FUNCTIONS ====================

def validate_password_strength(password: str) -> str:
    """
    Validate password strength
    Requirements:
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit
    - At least 1 special character
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    if not re.search(r'[0-9]', password):
        errors.append("Password must contain at least one digit")
    if not re.search(r'[@$!%*?&#^()_+\-=\[\]{}|;:,.<>]', password):
        errors.append("Password must contain at least one special character (@$!%*?&#)")
    
    if errors:
        raise ValueError("; ".join(errors))
    
    return password


def validate_phone(phone: str) -> str:
    """Validate phone number format"""
    if phone:
        # Remove spaces and dashes for validation
        cleaned = re.sub(r'[\s\-]', '', phone)
        if not re.match(PATTERNS["phone"], cleaned):
            raise ValueError("Invalid phone number format")
    return phone


def validate_gst(gst: str) -> str:
    """Validate GST number (India)"""
    if gst and not re.match(PATTERNS["gst"], gst.upper()):
        raise ValueError("Invalid GST number format")
    return gst.upper() if gst else gst


def validate_pan(pan: str) -> str:
    """Validate PAN number (India)"""
    if pan and not re.match(PATTERNS["pan"], pan.upper()):
        raise ValueError("Invalid PAN number format")
    return pan.upper() if pan else pan


def validate_pincode(pincode: str) -> str:
    """Validate Indian pincode"""
    if pincode and not re.match(PATTERNS["pincode"], pincode):
        raise ValueError("Invalid pincode format")
    return pincode


def validate_url(url: str) -> str:
    """Validate URL format"""
    if url and not re.match(PATTERNS["url"], url):
        raise ValueError("Invalid URL format")
    return url


def validate_name(name: str) -> str:
    """Validate name (letters, spaces, hyphens only)"""
    if name and not re.match(PATTERNS["name"], name):
        raise ValueError("Name can only contain letters, spaces, hyphens, and apostrophes")
    return name.strip()


def validate_no_html(value: str) -> str:
    """Validate that string contains no HTML/script tags"""
    if value:
        # Check for common XSS patterns
        dangerous_patterns = [
            r'<script',
            r'javascript:',
            r'on\w+\s*=',  # onclick, onerror, etc.
            r'<iframe',
            r'<object',
            r'<embed',
            r'<link',
            r'<meta',
        ]
        
        lower_value = value.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, lower_value):
                raise ValueError("Invalid characters detected in input")
    
    return value


# ==================== INPUT SANITIZATION ====================

def sanitize_string(value: str) -> str:
    """
    Sanitize string input
    - Strip whitespace
    - Escape HTML entities
    - Remove null bytes
    """
    if value is None:
        return value
    
    # Strip whitespace
    value = value.strip()
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Escape HTML entities (prevents XSS)
    value = html.escape(value)
    
    return value


def sanitize_html(value: str) -> str:
    """
    Remove all HTML tags from string
    """
    if value is None:
        return value
    
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', value)
    
    # Decode HTML entities
    clean = html.unescape(clean)
    
    return clean.strip()


def normalize_email(email: str) -> str:
    """Normalize email address"""
    if email:
        return email.lower().strip()
    return email


def normalize_phone(phone: str) -> str:
    """Normalize phone number (remove formatting)"""
    if phone:
        # Keep only digits and + sign
        return re.sub(r'[^\d+]', '', phone)
    return phone


# ==================== BUSINESS RULE VALIDATORS ====================

def validate_age(age: int, min_age: int = 0, max_age: int = 150) -> int:
    """Validate age within reasonable range"""
    if age < min_age or age > max_age:
        raise ValueError(f"Age must be between {min_age} and {max_age}")
    return age


def validate_amount(amount: float, min_amount: float = 0, max_amount: float = None) -> float:
    """Validate monetary amount"""
    if amount < min_amount:
        raise ValueError(f"Amount must be at least {min_amount}")
    if max_amount and amount > max_amount:
        raise ValueError(f"Amount cannot exceed {max_amount}")
    return round(amount, 2)


def validate_percentage(value: float) -> float:
    """Validate percentage (0-100)"""
    if value < 0 or value > 100:
        raise ValueError("Percentage must be between 0 and 100")
    return value


def validate_date_range(start_date, end_date) -> bool:
    """Validate that start_date is before end_date"""
    if start_date and end_date and start_date > end_date:
        raise ValueError("Start date must be before end date")
    return True


def validate_future_date(date) -> bool:
    """Validate that date is in the future"""
    from datetime import datetime
    if date and date < datetime.now():
        raise ValueError("Date must be in the future")
    return True


# ==================== DATABASE VALIDATORS ====================

def check_unique_email(db, model, email: str, exclude_id: int = None):
    """
    Check if email is unique in database
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        email: Email to check
        exclude_id: ID to exclude (for updates)
    """
    query = db.query(model).filter(model.email == email.lower())
    
    if exclude_id:
        query = query.filter(model.id != exclude_id)
    
    if query.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )


def check_unique_field(db, model, field_name: str, value: Any, exclude_id: int = None):
    """
    Check if a field value is unique in database
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        field_name: Name of the field to check
        value: Value to check
        exclude_id: ID to exclude (for updates)
    """
    field = getattr(model, field_name)
    query = db.query(model).filter(field == value)
    
    if exclude_id:
        query = query.filter(model.id != exclude_id)
    
    if query.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{field_name.replace('_', ' ').title()} already exists"
        )


def check_exists(db, model, id: int, error_message: str = None):
    """
    Check if record exists in database
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        id: Record ID to check
        error_message: Custom error message
    """
    record = db.query(model).filter(model.id == id).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_message or f"{model.__name__} not found"
        )
    
    return record


# ==================== AUTHORIZATION VALIDATORS ====================

def check_ownership(resource, user_id: int, owner_field: str = "user_id"):
    """
    Check if user owns the resource
    
    Args:
        resource: Database record
        user_id: Current user ID
        owner_field: Name of the owner field
    """
    owner_id = getattr(resource, owner_field, None)
    
    if owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )


def check_company_access(resource, company_id: int, company_field: str = "company_id"):
    """
    Check if resource belongs to user's company
    
    Args:
        resource: Database record
        company_id: Current user's company ID
        company_field: Name of the company field
    """
    resource_company_id = getattr(resource, company_field, None)
    
    if resource_company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Resource belongs to a different company"
        )


def check_role(user_role: str, allowed_roles: List[str]):
    """
    Check if user has required role
    
    Args:
        user_role: Current user's role
        allowed_roles: List of allowed roles
    """
    if user_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This action requires one of these roles: {', '.join(allowed_roles)}"
        )


def check_admin(user_role: str):
    """Check if user is admin or super_admin"""
    check_role(user_role, ["admin", "super_admin"])


def check_super_admin(user_role: str):
    """Check if user is super_admin"""
    check_role(user_role, ["super_admin"])


# ==================== PYDANTIC VALIDATOR DECORATORS ====================

def create_password_validator():
    """Create a reusable password validator for Pydantic models"""
    @field_validator('password', 'new_password', mode='after', check_fields=False)
    @classmethod
    def validate_pwd(cls, v):
        return validate_password_strength(v)
    return validate_pwd


def create_phone_validator():
    """Create a reusable phone validator for Pydantic models"""
    @field_validator('phone', mode='after', check_fields=False)
    @classmethod
    def validate_ph(cls, v):
        if v:
            return validate_phone(v)
        return v
    return validate_ph


def create_sanitize_validator(*fields):
    """Create a validator that sanitizes string fields"""
    @field_validator(*fields, mode='after', check_fields=False)
    @classmethod
    def sanitize(cls, v):
        if isinstance(v, str):
            return sanitize_string(v)
        return v
    return sanitize
