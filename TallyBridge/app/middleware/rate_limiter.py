"""
Rate Limiter Middleware
Prevents API abuse with configurable rate limits
"""

import time
from collections import defaultdict
from typing import Dict, Tuple, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from fastapi.responses import JSONResponse
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiter
    For production, use Redis-based rate limiting
    
    Features:
    - Per-IP rate limiting
    - Configurable requests per window
    - Sliding window algorithm
    - Whitelist support
    """
    
    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        whitelist: Optional[list] = None,
        enabled: bool = True
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.whitelist = whitelist or ["127.0.0.1", "localhost"]
        self.enabled = enabled
        
        # In-memory storage: {ip: [(timestamp, count), ...]}
        self._minute_requests: Dict[str, list] = defaultdict(list)
        self._hour_requests: Dict[str, list] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next) -> Response:
        if not self.enabled:
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Skip rate limiting for whitelisted IPs
        if client_ip in self.whitelist:
            return await call_next(request)
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/health", "/"]:
            return await call_next(request)
        
        # Check rate limits
        is_limited, retry_after = self._check_rate_limit(client_ip)
        
        if is_limited:
            logger.warning(
                f"Rate limit exceeded for {client_ip}",
                extra={"client_ip": client_ip, "path": request.url.path}
            )
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please try again later.",
                        "retry_after": retry_after
                    }
                },
                headers={"Retry-After": str(retry_after)}
            )
        
        # Record this request
        self._record_request(client_ip)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining_minute = max(0, self.requests_per_minute - len(self._minute_requests[client_ip]))
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining_minute)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _check_rate_limit(self, client_ip: str) -> Tuple[bool, int]:
        """
        Check if client has exceeded rate limits
        Returns: (is_limited, retry_after_seconds)
        """
        current_time = time.time()
        
        # Clean old entries
        self._cleanup_old_entries(client_ip, current_time)
        
        # Check minute limit
        minute_count = len(self._minute_requests[client_ip])
        if minute_count >= self.requests_per_minute:
            oldest = self._minute_requests[client_ip][0] if self._minute_requests[client_ip] else current_time
            retry_after = int(60 - (current_time - oldest)) + 1
            return True, max(1, retry_after)
        
        # Check hour limit
        hour_count = len(self._hour_requests[client_ip])
        if hour_count >= self.requests_per_hour:
            oldest = self._hour_requests[client_ip][0] if self._hour_requests[client_ip] else current_time
            retry_after = int(3600 - (current_time - oldest)) + 1
            return True, max(1, retry_after)
        
        return False, 0
    
    def _record_request(self, client_ip: str) -> None:
        """Record a request timestamp"""
        current_time = time.time()
        self._minute_requests[client_ip].append(current_time)
        self._hour_requests[client_ip].append(current_time)
    
    def _cleanup_old_entries(self, client_ip: str, current_time: float) -> None:
        """Remove entries older than the window"""
        minute_ago = current_time - 60
        hour_ago = current_time - 3600
        
        self._minute_requests[client_ip] = [
            t for t in self._minute_requests[client_ip] if t > minute_ago
        ]
        self._hour_requests[client_ip] = [
            t for t in self._hour_requests[client_ip] if t > hour_ago
        ]
