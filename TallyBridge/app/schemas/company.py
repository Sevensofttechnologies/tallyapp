"""
Company Schemas
Enhanced with comprehensive validation
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from app.utils.validators import (
    validate_phone,
    validate_url,
    validate_pincode,
    validate_no_html,
    sanitize_string,
    normalize_email
)


class CompanyBase(BaseModel):
    """
    Base company schema with validation
    
    Validations:
    - Name: 2-255 chars, no HTML
    - Email: Valid format
    - Phone: Valid format (optional)
    - Website: Valid URL (optional)
    - All text fields: Sanitized, no HTML
    """
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    
    @field_validator('email')
    @classmethod
    def normalize_email_field(cls, v):
        return normalize_email(v)
    
    @field_validator('name', 'address', 'city', 'state', 'country', 'industry')
    @classmethod
    def sanitize_text_fields(cls, v):
        if v:
            v = sanitize_string(v)
            validate_no_html(v)
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone_field(cls, v):
        if v:
            return validate_phone(v)
        return v
    
    @field_validator('website')
    @classmethod
    def validate_website_field(cls, v):
        if v:
            return validate_url(v)
        return v


class CompanyCreate(CompanyBase):
    """Create company schema"""
    pass


class CompanyUpdate(BaseModel):
    """Update company schema"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    status: Optional[str] = None
    # Tally Integration Fields
    tally_guid: Optional[str] = None
    tally_server: Optional[str] = None
    tally_port: Optional[int] = None


class CompanyResponse(CompanyBase):
    """Company response schema"""
    id: int
    logo: Optional[str] = None
    company_size: Optional[str] = None
    status: str
    # Tally Integration Fields
    tally_guid: Optional[str] = None
    tally_server: Optional[str] = None
    tally_port: Optional[int] = None
    last_sync_at: Optional[datetime] = None
    last_alter_id: Optional[int] = None
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CompanyTallySync(BaseModel):
    """Schema for syncing company from Tally"""
    tally_guid: str
    name: str
    tally_server: str = "localhost"
    tally_port: int = 9000
