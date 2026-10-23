"""
Company Controller
Handles company management logic
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.models.company import Company
from app.models.user import User
from app.models.user_company import UserCompany
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.services import audit_service


class CompanyController:
    """Company management business logic"""
    
    @staticmethod
    def get_user_companies(user: User, db: Session, search: Optional[str] = None) -> List[Company]:
        """Get all companies user has access to"""
        if user.role == "super_admin":
            query = db.query(Company)
        else:
            query = db.query(Company).join(UserCompany).filter(UserCompany.user_id == user.id)
        
        if search:
            query = query.filter(
                (Company.name.contains(search)) | (Company.email.contains(search))
            )
        
        return query.all()
    
    @staticmethod
    def create_company(company_data: CompanyCreate, user: User, db: Session) -> Company:
        """Create new company"""
        existing = db.query(Company).filter(Company.email == company_data.email).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Company email already exists")
        
        new_company = Company(**company_data.model_dump())
        db.add(new_company)
        db.flush()
        
        user_company = UserCompany(
            user_id=user.id,
            company_id=new_company.id,
            role="admin",
            is_primary=True
        )
        db.add(user_company)
        db.commit()
        db.refresh(new_company)
        
        # Audit log for company creation
        audit_service.log_create(
            db=db,
            user_id=user.id,
            user_email=user.email,
            resource_type="Company",
            resource_id=new_company.id,
            new_values={"name": new_company.name, "email": new_company.email},
            message=f"Company created: {new_company.name}"
        )
        
        return new_company
    
    @staticmethod
    def get_company(company_id: int, user: User, db: Session) -> Company:
        """Get company by ID"""
        company = db.query(Company).filter(Company.id == company_id).first()
        
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        
        user_company = db.query(UserCompany).filter(
            UserCompany.user_id == user.id,
            UserCompany.company_id == company_id
        ).first()
        
        if not user_company and user.role != "super_admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to this company")
        
        return company
    
    @staticmethod
    def update_company(
        company_id: int,
        company_data: CompanyUpdate,
        user: User,
        db: Session
    ) -> Company:
        """Update company"""
        company = CompanyController.get_company(company_id, user, db)
        
        user_company = db.query(UserCompany).filter(
            UserCompany.user_id == user.id,
            UserCompany.company_id == company_id,
            UserCompany.role == "admin"
        ).first()
        
        if not user_company and user.role != "super_admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        
        update_data = company_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(company, key, value)
        
        db.commit()
        db.refresh(company)
        
        # Audit log for company update
        audit_service.log_update(
            db=db,
            user_id=user.id,
            user_email=user.email,
            resource_type="Company",
            resource_id=company.id,
            old_values={},
            new_values=update_data,
            message=f"Company updated: {company.name}"
        )
        
        return company
    
    @staticmethod
    def delete_company(company_id: int, user: User, db: Session):
        """Delete company"""
        if user.role != "super_admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only super admin can delete companies")
        
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        
        # Audit log before delete
        audit_service.log_delete(
            db=db,
            user_id=user.id,
            user_email=user.email,
            resource_type="Company",
            resource_id=company.id,
            old_values={"name": company.name, "email": company.email},
            message=f"Company deleted: {company.name}"
        )
        
        db.delete(company)
        db.commit()
