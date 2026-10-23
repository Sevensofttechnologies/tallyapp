"""
Authentication Schemas
Enhanced with comprehensive validation
"""

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional
import re
from app.utils.validators import (
    validate_password_strength,
    validate_phone,
    validate_name,
    validate_no_html,
    sanitize_string,
    normalize_email
)


class UserRegister(BaseModel):
    """
    User registration schema with comprehensive validation
    
    Validations:
    - Email: Valid format, normalized to lowercase
    - Password: Strong password (8+ chars, upper, lower, digit, special)
    - Names: 2-100 chars, letters only, no HTML
    - Phone: Optional, valid format
    """
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    
    @field_validator('email')
    @classmethod
    def normalize_email_field(cls, v):
        return normalize_email(v)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        return validate_password_strength(v)
    
    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_names(cls, v):
        v = sanitize_string(v)
        validate_no_html(v)
        return validate_name(v)
    
    @field_validator('phone')
    @classmethod
    def validate_phone_field(cls, v):
        if v:
            return validate_phone(v)
        return v


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class TokenData(BaseModel):
    """Token payload data"""
    user_id: int
    email: str
    company_id: Optional[int] = None
    role: Optional[str] = None


class ChangePassword(BaseModel):
    """
    Change password schema with validation
    - Current password required
    - New password must be strong
    - New password must be different from current
    """
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        return validate_password_strength(v)
    
    @model_validator(mode='after')
    def passwords_different(self):
        if self.current_password == self.new_password:
            raise ValueError('New password must be different from current password')
        return self


class ForgotPasswordRequest(BaseModel):
    """Forgot password request schema"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request schema"""
    token: str
    new_password: str = Field(..., min_length=8)


class VerifyResetTokenRequest(BaseModel):
    """Verify reset token schema"""
    token: str
