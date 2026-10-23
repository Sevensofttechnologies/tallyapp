"""
Permission Controller
Handles permission management logic
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.models.permission import Permission, RolePermission
from app.models.user import User
from app.schemas.permission import PermissionCreate, PermissionUpdate


class PermissionController:
    """Permission management business logic"""
    
    @staticmethod
    def get_all_permissions(db: Session) -> List[Permission]:
        """Get all permissions"""
        return db.query(Permission).all()
    
    @staticmethod
    def create_permission(permission_data: PermissionCreate, db: Session) -> Permission:
        """Create new permission"""
        existing = db.query(Permission).filter(
            Permission.resource == permission_data.resource,
            Permission.action == permission_data.action
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Permission already exists"
            )
        
        new_permission = Permission(**permission_data.model_dump())
        db.add(new_permission)
        db.commit()
        db.refresh(new_permission)
        return new_permission
    
    @staticmethod
    def get_role_permissions(role: str, company_id: Optional[int], db: Session) -> List[RolePermission]:
        """Get permissions for a role"""
        query = db.query(RolePermission).filter(RolePermission.role == role)
        
        if company_id:
            query = query.filter(RolePermission.company_id == company_id)
        else:
            query = query.filter(RolePermission.company_id.is_(None))
        
        return query.all()
    
    @staticmethod
    def assign_permission_to_role(
        permission_id: int,
        role: str,
        company_id: Optional[int],
        db: Session
    ) -> RolePermission:
        """Assign permission to role"""
        permission = db.query(Permission).filter(Permission.id == permission_id).first()
        if not permission:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
        
        existing = db.query(RolePermission).filter(
            RolePermission.permission_id == permission_id,
            RolePermission.role == role,
            RolePermission.company_id == company_id
        ).first()
        
        if existing:
            existing.granted = True
            db.commit()
            return existing
        
        role_permission = RolePermission(
            permission_id=permission_id,
            role=role,
            company_id=company_id,
            granted=True
        )
        db.add(role_permission)
        db.commit()
        db.refresh(role_permission)
        return role_permission
    
    @staticmethod
    def revoke_permission_from_role(
        permission_id: int,
        role: str,
        company_id: Optional[int],
        db: Session
    ):
        """Revoke permission from role"""
        role_permission = db.query(RolePermission).filter(
            RolePermission.permission_id == permission_id,
            RolePermission.role == role,
            RolePermission.company_id == company_id
        ).first()
        
        if role_permission:
            role_permission.granted = False
            db.commit()
