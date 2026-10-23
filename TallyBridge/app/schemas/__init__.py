"""
Schemas Package
Pydantic validation schemas
"""

from app.schemas.auth import UserRegister, UserLogin, Token, TokenData, ChangePassword
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from app.schemas.company import CompanyBase, CompanyCreate, CompanyUpdate, CompanyResponse
from app.schemas.permission import PermissionBase, PermissionCreate, PermissionResponse
from app.schemas.response import SuccessResponse, ErrorResponse, PaginatedResponse
