"""
User Schemas
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = None


class UserCreate(UserBase):
    """Create user schema"""
    password: str = Field(..., min_length=8)
    role: Optional[str] = "user"


class UserUpdate(BaseModel):
    """Update user schema"""
    first_name: Optional[str] = Field(None, min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = None
    avatar: Optional[str] = None
    is_active: Optional[bool] = None


class UserRoleUpdate(BaseModel):
    """Update user role schema"""
    role: str = Field(..., pattern="^(super_admin|admin|manager|user)$")


class UserResponse(UserBase):
    """User response schema"""
    id: int
    avatar: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
