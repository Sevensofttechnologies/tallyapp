"""
Security Headers Middleware
Adds industry-standard security headers to all responses
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Dict, Optional


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security headers to all responses
    
    Headers added:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Strict-Transport-Security (HSTS)
    - Content-Security-Policy
    - Referrer-Policy
    - Permissions-Policy
    """
    
    def __init__(
        self,
        app: ASGIApp,
        enable_hsts: bool = False,
        hsts_max_age: int = 31536000,
        custom_headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(app)
        self.enable_hsts = enable_hsts
        self.hsts_max_age = hsts_max_age
        self.custom_headers = custom_headers or {}
    
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # XSS Protection (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy (formerly Feature-Policy)
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), camera=(), geolocation=(), "
            "gyroscope=(), magnetometer=(), microphone=(), "
            "payment=(), usb=()"
        )
        
        # HSTS (only enable in production with HTTPS)
        if self.enable_hsts:
            response.headers["Strict-Transport-Security"] = (
                f"max-age={self.hsts_max_age}; includeSubDomains"
            )
        
        # Content Security Policy (basic - customize as needed)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' data: https://fonts.gstatic.com https://fonts.googleapis.com https://cdn.jsdelivr.net; "
            "connect-src 'self' https://cdn.jsdelivr.net https://fonts.googleapis.com https://fonts.gstatic.com"
        )
        
        # Add custom headers
        for header, value in self.custom_headers.items():
            response.headers[header] = value
        
        return response
