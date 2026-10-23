"""
Company Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.controllers.company_controller import CompanyController
from app.utils.dependencies import get_current_active_user
from app.utils.permissions import require_super_admin, check_company_admin
from app.utils.helpers import success_response
from app.models.user import User

router = APIRouter()


@router.get("")
async def get_companies(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all companies accessible to current user"""
    try:
        companies = CompanyController.get_user_companies(current_user, db, search)
        
        start = (page - 1) * per_page
        end = start + per_page
        paginated_companies = companies[start:end]
        
        total = len(companies)
        pages = (total + per_page - 1) // per_page
        
        return {
            "success": True,
            "data": [company.to_dict() for company in paginated_companies],
            "pagination": {"page": page, "per_page": per_page, "total": total, "pages": pages},
            "message": "Companies fetched successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("", status_code=status.HTTP_403_FORBIDDEN)
async def create_company(
    company_data: CompanyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new company - DISABLED: Use Tally Sync instead"""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Manual company creation is disabled. Please use Tally Sync to add companies."
    )


@router.get("/{company_id}")
async def get_company(
    company_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get company details"""
    try:
        company = CompanyController.get_company(company_id, current_user, db)
        return success_response(data=company.to_dict(), message="Company details fetched successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{company_id}")
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update company"""
    if current_user.role != "super_admin" and not check_company_admin(current_user.id, company_id, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    try:
        company = CompanyController.update_company(company_id, company_data, current_user, db)
        return success_response(data=company.to_dict(), message="Company updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{company_id}")
async def delete_company(
    company_id: int,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Delete company"""
    try:
        CompanyController.delete_company(company_id, current_user, db)
        return success_response(data={}, message="Company deleted successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/select/{company_id}")
async def select_company(
    company_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Select company (set as active)"""
    try:
        from app.utils.security import create_access_token
        
        company = CompanyController.get_company(company_id, current_user, db)
        
        token_data = {
            "user_id": current_user.id,
            "email": current_user.email,
            "role": current_user.role,
            "company_id": company_id
        }
        new_token = create_access_token(token_data)
        
        return success_response(
            data={
                "company_id": company.id,
                "company_name": company.name,
                "user_role": current_user.role,
                "new_token": new_token
            },
            message="Company selected successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
