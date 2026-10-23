"""
Custom Exception Classes and Global Exception Handlers
Industry Standard Error Handling
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Any, Dict, Optional
import traceback
import logging

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base application exception"""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class BadRequestException(AppException):
    """400 Bad Request"""
    def __init__(self, message: str = "Bad request", details: Optional[Dict] = None):
        super().__init__(message, 400, "BAD_REQUEST", details)


class UnauthorizedException(AppException):
    """401 Unauthorized"""
    def __init__(self, message: str = "Unauthorized", details: Optional[Dict] = None):
        super().__init__(message, 401, "UNAUTHORIZED", details)


class ForbiddenException(AppException):
    """403 Forbidden"""
    def __init__(self, message: str = "Forbidden", details: Optional[Dict] = None):
        super().__init__(message, 403, "FORBIDDEN", details)


class NotFoundException(AppException):
    """404 Not Found"""
    def __init__(self, message: str = "Resource not found", details: Optional[Dict] = None):
        super().__init__(message, 404, "NOT_FOUND", details)


class ConflictException(AppException):
    """409 Conflict"""
    def __init__(self, message: str = "Resource conflict", details: Optional[Dict] = None):
        super().__init__(message, 409, "CONFLICT", details)


class ValidationException(AppException):
    """422 Validation Error"""
    def __init__(self, message: str = "Validation error", details: Optional[Dict] = None):
        super().__init__(message, 422, "VALIDATION_ERROR", details)


class RateLimitException(AppException):
    """429 Too Many Requests"""
    def __init__(self, message: str = "Too many requests", details: Optional[Dict] = None):
        super().__init__(message, 429, "RATE_LIMIT_EXCEEDED", details)


class DatabaseException(AppException):
    """500 Database Error"""
    def __init__(self, message: str = "Database error", details: Optional[Dict] = None):
        super().__init__(message, 500, "DATABASE_ERROR", details)


class ServiceUnavailableException(AppException):
    """503 Service Unavailable"""
    def __init__(self, message: str = "Service unavailable", details: Optional[Dict] = None):
        super().__init__(message, 503, "SERVICE_UNAVAILABLE", details)


def create_error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: Optional[Dict] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create standardized error response"""
    response = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    if request_id:
        response["error"]["request_id"] = request_id
    
    return response


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions"""
    request_id = getattr(request.state, "request_id", None)
    
    logger.error(
        f"AppException: {exc.error_code} - {exc.message}",
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "error_code": exc.error_code,
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
            request_id=request_id
        )
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions"""
    request_id = getattr(request.state, "request_id", None)
    
    error_codes = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }
    
    error_code = error_codes.get(exc.status_code, "HTTP_ERROR")
    
    logger.warning(
        f"HTTPException: {exc.status_code} - {exc.detail}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            error_code=error_code,
            message=str(exc.detail),
            request_id=request_id
        )
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors"""
    request_id = getattr(request.state, "request_id", None)
    
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"ValidationError: {len(errors)} validation errors",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "errors": errors,
        }
    )
    
    return JSONResponse(
        status_code=422,
        content=create_error_response(
            status_code=422,
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            details={"errors": errors},
            request_id=request_id
        )
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle SQLAlchemy database errors"""
    request_id = getattr(request.state, "request_id", None)
    
    if isinstance(exc, IntegrityError):
        message = "Database integrity error - duplicate or invalid data"
        error_code = "INTEGRITY_ERROR"
        status_code = 409
    else:
        message = "Database error occurred"
        error_code = "DATABASE_ERROR"
        status_code = 500
    
    logger.error(
        f"DatabaseError: {type(exc).__name__} - {str(exc)}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "exception_type": type(exc).__name__,
        }
    )
    
    return JSONResponse(
        status_code=status_code,
        content=create_error_response(
            status_code=status_code,
            error_code=error_code,
            message=message,
            request_id=request_id
        )
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all uncaught exceptions"""
    request_id = getattr(request.state, "request_id", None)
    
    logger.critical(
        f"UnhandledException: {type(exc).__name__} - {str(exc)}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc(),
        }
    )
    
    return JSONResponse(
        status_code=500,
        content=create_error_response(
            status_code=500,
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred",
            request_id=request_id
        )
    )
