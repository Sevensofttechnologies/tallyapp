"""
Authentication Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import UserRegister, UserLogin, ChangePassword, ForgotPasswordRequest, ResetPasswordRequest, VerifyResetTokenRequest
from app.controllers.auth_controller import AuthController
from app.utils.dependencies import get_current_active_user
from app.utils.helpers import success_response
from app.models.user import User

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register new user"""
    try:
        user = AuthController.register_user(user_data, db)
        return success_response(data=user.to_dict(), message="User registered successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/login")
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """User login"""
    try:
        token_data = AuthController.login_user(login_data, db)
        return success_response(data=token_data, message="Login successful")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current authenticated user"""
    user_data = current_user.to_dict(include_companies=True)
    user_data["company_count"] = len(current_user.companies) if current_user.companies else 0
    return success_response(data=user_data, message="User data fetched successfully")


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """User logout"""
    return success_response(data={}, message="Logged out successfully")


@router.put("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    try:
        AuthController.change_password(current_user, password_data.current_password, password_data.new_password, db)
        return success_response(data={}, message="Password changed successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Request password reset"""
    try:
        result = AuthController.create_password_reset_token(request.email, db)
        return success_response(data=result, message="Password reset request processed")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/verify-reset-token")
async def verify_reset_token(request: VerifyResetTokenRequest, db: Session = Depends(get_db)):
    """Verify reset token"""
    try:
        result = AuthController.verify_reset_token(request.token, db)
        return success_response(data=result, message="Token verification complete")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using token"""
    try:
        result = AuthController.reset_password(request.token, request.new_password, db)
        return success_response(data=result, message="Password reset successful")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
