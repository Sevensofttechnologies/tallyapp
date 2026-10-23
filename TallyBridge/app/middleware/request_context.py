"""
Request Context Middleware
Adds correlation ID, request timing, and context to all requests
"""

import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.utils.logging_config import set_request_id, generate_request_id, get_logger

logger = get_logger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add request context:
    - Unique request ID (correlation ID)
    - Request timing
    - Client IP tracking
    - Request/Response logging
    """
    
    def __init__(self, app: ASGIApp, debug: bool = False):
        super().__init__(app)
        self.debug = debug
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate or get request ID from header
        request_id = request.headers.get("X-Request-ID") or generate_request_id()
        
        # Set request ID in context (thread-safe)
        set_request_id(request_id)
        
        # Store in request state for access in routes
        request.state.request_id = request_id
        request.state.start_time = time.time()
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        request.state.client_ip = client_ip
        
        # Log request start
        if self.debug:
            logger.debug(
                f"Request started: {request.method} {request.url.path}",
                extra={
                    "client_ip": client_ip,
                    "user_agent": request.headers.get("user-agent", ""),
                    "content_type": request.headers.get("content-type", ""),
                }
            )
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise
        
        # Calculate processing time
        process_time = time.time() - request.state.start_time
        
        # Add headers to response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        
        # Log request completion
        log_level = "warning" if response.status_code >= 400 else "info"
        if self.debug or response.status_code >= 400:
            getattr(logger, log_level)(
                f"{request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)",
                extra={
                    "status_code": response.status_code,
                    "process_time": process_time,
                    "client_ip": client_ip,
                }
            )
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract real client IP from headers or connection"""
        # Check for forwarded headers (reverse proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        if request.client:
            return request.client.host
        
        return "unknown"
