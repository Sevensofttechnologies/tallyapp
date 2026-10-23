"""
Permission Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PermissionBase(BaseModel):
    """Base permission schema"""
    resource: str = Field(..., description="Resource name")
    action: str = Field(..., description="Action name")
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    """Create permission schema"""
    pass


class PermissionUpdate(BaseModel):
    """Update permission schema"""
    resource: Optional[str] = None
    action: Optional[str] = None
    description: Optional[str] = None


class PermissionResponse(PermissionBase):
    """Permission response schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RolePermissionBase(BaseModel):
    """Base role permission schema"""
    permission_id: int
    role: str
    company_id: Optional[int] = None
    granted: bool = True


class RolePermissionCreate(RolePermissionBase):
    """Create role permission schema"""
    pass


class RolePermissionResponse(RolePermissionBase):
    """Role permission response schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CheckPermissionRequest(BaseModel):
    """Check permission request"""
    resource: str
    action: str
    company_id: Optional[int] = None


class CheckPermissionResponse(BaseModel):
    """Check permission response"""
    has_permission: bool
    permission: Optional[PermissionResponse] = None
