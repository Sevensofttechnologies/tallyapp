"""
Common Response Schemas
"""

from pydantic import BaseModel
from typing import Any, Optional, Dict
from datetime import datetime


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    data: Any
    message: str
    timestamp: datetime = datetime.utcnow()


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    details: Optional[Dict] = None
    timestamp: datetime = datetime.utcnow()


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int
    per_page: int
    total: int
    pages: int


class PaginatedResponse(BaseModel):
    """Paginated response"""
    success: bool = True
    data: list
    pagination: PaginationMeta
    message: str
    timestamp: datetime = datetime.utcnow()
