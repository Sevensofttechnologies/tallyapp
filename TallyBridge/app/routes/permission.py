"""
Permission Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.permission import PermissionCreate, CheckPermissionRequest
from app.controllers.permission_controller import PermissionController
from app.utils.dependencies import get_current_active_user
from app.utils.permissions import require_super_admin, has_permission
from app.utils.helpers import success_response
from app.models.user import User

router = APIRouter()


@router.get("/permissions")
async def get_permissions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all permissions"""
    try:
        permissions = PermissionController.get_all_permissions(db)
        return success_response(
            data=[p.to_dict() for p in permissions],
            message="Permissions fetched successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/permissions", status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission_data: PermissionCreate,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Create new permission"""
    try:
        permission = PermissionController.create_permission(permission_data, db)
        return success_response(data=permission.to_dict(), message="Permission created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/permissions/role/{role}")
async def get_role_permissions(
    role: str,
    company_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get permissions for a role"""
    try:
        role_permissions = PermissionController.get_role_permissions(role, company_id, db)
        return success_response(
            data=[rp.to_dict(include_permission=True) for rp in role_permissions],
            message="Role permissions fetched successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/permissions/check")
async def check_permission_endpoint(
    request: CheckPermissionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Check if current user has permission"""
    try:
        has_perm = has_permission(current_user, request.resource, request.action, request.company_id, db)
        return success_response(
            data={"has_permission": has_perm, "resource": request.resource, "action": request.action},
            message="Permission check complete"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/permissions/assign")
async def assign_permission(
    permission_id: int,
    role: str,
    company_id: Optional[int] = None,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Assign permission to role"""
    try:
        role_permission = PermissionController.assign_permission_to_role(permission_id, role, company_id, db)
        return success_response(data=role_permission.to_dict(), message="Permission assigned successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/permissions/revoke")
async def revoke_permission(
    permission_id: int,
    role: str,
    company_id: Optional[int] = None,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Revoke permission from role"""
    try:
        PermissionController.revoke_permission_from_role(permission_id, role, company_id, db)
        return success_response(data={}, message="Permission revoked successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
