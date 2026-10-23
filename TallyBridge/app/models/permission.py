"""
Permission Model
Defines permissions for resources and actions
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Permission(Base):
    """Permission model for resource-action based permissions"""
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    resource = Column(String(100), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Permission {self.resource}:{self.action}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "resource": self.resource,
            "action": self.action,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class RolePermission(Base):
    """Role-Permission mapping"""
    __tablename__ = "role_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=True, index=True)
    granted = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    permission = relationship("Permission", back_populates="role_permissions")
    company = relationship("Company", foreign_keys=[company_id])
    
    def __repr__(self):
        return f"<RolePermission {self.role}:{self.permission_id}>"
    
    def to_dict(self, include_permission=False):
        data = {
            "id": self.id,
            "permission_id": self.permission_id,
            "role": self.role,
            "company_id": self.company_id,
            "granted": self.granted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        if include_permission and self.permission:
            data["permission"] = self.permission.to_dict()
        return data
