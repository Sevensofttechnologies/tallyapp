"""
Authentication Controller
Handles user authentication logic
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.schemas.auth import UserRegister, UserLogin
from app.utils.security import get_password_hash, verify_password, create_access_token
from app.config import settings
from app.services import log_service, audit_service


class AuthController:
    """Authentication business logic"""
    
    @staticmethod
    def register_user(user_data: UserRegister, db: Session) -> User:
        """Register new user"""
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        hashed_password = get_password_hash(user_data.password)
        is_first_user = db.query(User).count() == 0
        
        new_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            role="super_admin" if is_first_user else "user",
            is_active=True,
            is_verified=False
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Audit log for user registration
        audit_service.log_create(
            db=db,
            user_id=new_user.id,
            user_email=new_user.email,
            resource_type="User",
            resource_id=new_user.id,
            new_values={"email": new_user.email, "first_name": new_user.first_name, "last_name": new_user.last_name},
            message=f"New user registered: {new_user.email}"
        )
        
        return new_user
    
    @staticmethod
    def login_user(login_data: UserLogin, db: Session) -> dict:
        """Authenticate user and generate token"""
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Audit log for login
        audit_service.create_audit_trail(
            db=db,
            user_id=user.id,
            user_email=user.email,
            action="LOGIN",
            resource_type="User",
            resource_id=user.id,
            message=f"User logged in: {user.email}"
        )
        
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role
        }
        access_token = create_access_token(token_data)
        
        # Get company count for redirect logic
        company_count = len(user.companies) if user.companies else 0
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user.to_dict(include_companies=True),
            "company_count": company_count
        }
    
    @staticmethod
    def change_password(user: User, current_password: str, new_password: str, db: Session):
        """Change user password"""
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        
        user.password_hash = get_password_hash(new_password)
        db.commit()
        
        # Audit log for password change
        audit_service.create_audit_trail(
            db=db,
            user_id=user.id,
            user_email=user.email,
            action="PASSWORD_CHANGE",
            resource_type="User",
            resource_id=user.id,
            message=f"Password changed for: {user.email}"
        )
    
    @staticmethod
    def create_password_reset_token(email: str, db: Session) -> dict:
        """Create password reset token"""
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return {
                "message": "If the email exists, a password reset link has been sent",
                "email": email
            }
        
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.is_used == False
        ).update({"is_used": True})
        
        token = PasswordResetToken.generate_token()
        reset_token = PasswordResetToken(
            token=token,
            user_id=user.id,
            email=user.email,
            expires_at=PasswordResetToken.get_expiry_time(hours=24)
        )
        
        db.add(reset_token)
        db.commit()
        
        return {
            "message": "If the email exists, a password reset link has been sent",
            "email": email,
            "token": token,
            "expires_in_hours": 24
        }
    
    @staticmethod
    def verify_reset_token(token: str, db: Session) -> dict:
        """Verify reset token"""
        reset_token = db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token
        ).first()
        
        if not reset_token:
            return {"valid": False, "message": "Invalid or expired reset token"}
        
        if reset_token.is_used:
            return {"valid": False, "message": "This reset token has already been used"}
        
        if reset_token.is_expired:
            return {"valid": False, "message": "This reset token has expired"}
        
        return {"valid": True, "message": "Token is valid", "email": reset_token.email}
    
    @staticmethod
    def reset_password(token: str, new_password: str, db: Session) -> dict:
        """Reset password using token"""
        reset_token = db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token
        ).first()
        
        if not reset_token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
        
        if reset_token.is_used:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token already used")
        
        if reset_token.is_expired:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired")
        
        user = db.query(User).filter(User.id == reset_token.user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        user.password_hash = get_password_hash(new_password)
        reset_token.is_used = True
        reset_token.used_at = datetime.utcnow()
        db.commit()
        
        return {"message": "Password has been reset successfully", "email": user.email}
