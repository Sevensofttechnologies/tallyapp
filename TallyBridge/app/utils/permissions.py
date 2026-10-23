"""
Permission Utilities
Role-Based Access Control (RBAC) helper functions
"""

from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User
from app.models.user_company import UserCompany
from app.models.permission import Permission, RolePermission
from app.database import get_db
from app.utils.dependencies import get_current_active_user


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Require admin or super_admin role"""
    if current_user.role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


def require_super_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Require super_admin role"""
    if current_user.role != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Super admin access required")
    return current_user


def check_company_admin(user_id: int, company_id: int, db: Session) -> bool:
    """Check if user is admin in the company"""
    user_company = db.query(UserCompany).filter(
        UserCompany.user_id == user_id,
        UserCompany.company_id == company_id,
        UserCompany.role == "admin"
    ).first()
    return user_company is not None


def check_company_access(user_id: int, company_id: int, db: Session) -> bool:
    """Check if user has any access to the company"""
    user_company = db.query(UserCompany).filter(
        UserCompany.user_id == user_id,
        UserCompany.company_id == company_id
    ).first()
    return user_company is not None


def get_company_role(user_id: int, company_id: int, db: Session) -> Optional[str]:
    """Get user's role in a specific company"""
    user_company = db.query(UserCompany).filter(
        UserCompany.user_id == user_id,
        UserCompany.company_id == company_id
    ).first()
    return user_company.role if user_company else None


def has_permission(
    user: User,
    resource: str,
    action: str,
    company_id: Optional[int] = None,
    db: Optional[Session] = None
) -> bool:
    """Check if user has permission for a resource-action combination"""
    if user.role == "super_admin":
        return True
    
    if user.role == "admin":
        if company_id and db:
            return check_company_admin(user.id, company_id, db)
        return True
    
    if company_id and db:
        company_role = get_company_role(user.id, company_id, db)
        if company_role == "admin":
            return True
    
    if db is not None:
        permission = db.query(Permission).filter(
            Permission.resource == resource,
            Permission.action == action
        ).first()
        
        if permission:
            roles_to_check = []
            if user.role:
                roles_to_check.append(("global", user.role))
            
            if company_id:
                company_role = get_company_role(user.id, company_id, db)
                if company_role:
                    roles_to_check.append(("company", company_role))
            
            for scope, role in roles_to_check:
                role_perm = db.query(RolePermission).filter(
                    RolePermission.permission_id == permission.id,
                    RolePermission.role == role,
                    RolePermission.granted == True
                )
                
                if scope == "company":
                    role_perm = role_perm.filter(RolePermission.company_id == company_id)
                else:
                    role_perm = role_perm.filter(RolePermission.company_id.is_(None))
                
                if role_perm.first():
                    return True
            return False
    
    # Fallback role-based logic
    if user.role == "manager":
        if resource in ["user", "company"] and action == "delete":
            return False
        return True
    
    if user.role == "user":
        return action == "read"
    
    return False


def check_permission(
    user: User,
    resource: str,
    action: str,
    company_id: Optional[int] = None,
    db: Optional[Session] = None
):
    """Check permission and raise HTTPException if denied"""
    if not has_permission(user, resource, action, company_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {resource}:{action}"
        )


PERMISSIONS = {
    "user": ["create", "read", "update", "delete"],
    "company": ["create", "read", "update", "delete"],
}
