"""
FastAPI Main Application Entry Point
Application Starter Kit - Backend Only
Industry Standard Implementation
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.config import settings
from app.database import engine, Base, get_db_info
from app.routes import auth, company, user, permission, email, tally, reports, exports_jobs, admin_email_settings, email_delivery
from app.routes import admin_redis_dashboard
import app.models
from app.middleware import (
    RequestContextMiddleware,
    RateLimiterMiddleware,
    SecurityHeadersMiddleware
)
from app.utils.exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    global_exception_handler
)
from app.utils.logging_config import setup_logging, get_logger

# Setup structured logging
setup_logging(
    level=settings.LOG_LEVEL,
    json_format=not settings.DEBUG,  # JSON in production, colored in dev
)
logger = get_logger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Application Starter Kit - FastAPI MVC Backend Boilerplate",
    docs_url="/docs",
    redoc_url="/redoc",
)


# ==================== EXCEPTION HANDLERS ====================
# Register exception handlers (order matters - most specific first)
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)


# ==================== MIDDLEWARE STACK ====================
# Order: Last added = First executed (LIFO)

# 0. HTTPS Redirect (Production only)
if not settings.DEBUG and settings.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# 1. Security Headers (outermost - runs first)
app.add_middleware(
    SecurityHeadersMiddleware,
    enable_hsts=not settings.DEBUG  # Enable HSTS in production
)

# 2. Rate Limiter
app.add_middleware(
    RateLimiterMiddleware,
    requests_per_minute=60,
    requests_per_hour=1000,
    enabled=not settings.DEBUG  # Disable in debug mode
)

# 3. Request Context (correlation ID, timing)
app.add_middleware(
    RequestContextMiddleware,
    debug=settings.DEBUG
)

# 4. Trusted Hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# 5. CORS (innermost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint - Serve website landing page
@app.get("/")
async def root():
    """Root endpoint - Serve website landing page"""
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "website", "index.html")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/html")
    return RedirectResponse(url="/frontend/website/index.html")


# API info endpoint
@app.get("/api")
@app.get("/api/")
async def api_info():
    """API info endpoint"""
    return {
        "success": True,
        "message": f"{settings.APP_NAME} API is running",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


# Health check endpoint (Kubernetes/Docker ready)
@app.get("/health")
@app.get("/api/health")
@app.get("/api/v1/health")
async def health_check():
    """
    Health check endpoint for load balancers and orchestrators
    Returns: Basic health status with service info
    """
    return {
        "success": True,
        "status": "UP",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "connected",
        "message": "API is operational"
    }


# Readiness check (for Kubernetes)
@app.get("/ready")
@app.get("/api/ready")
async def readiness_check():
    """
    Readiness check - verifies all dependencies are ready
    """
    db_info = get_db_info()
    return {
        "success": True,
        "status": "ready",
        "checks": {
            "database": db_info,
            "api": "operational"
        }
    }


# System Info endpoint
@app.get("/api/system/info")
async def get_system_info():
    """Get system configuration info"""
    db_info = get_db_info()
    return {
        "success": True,
        "data": {
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "database": db_info,
        },
        "message": "System info"
    }


# ==================== API VERSIONING ====================
# Version 1 API routes
API_V1_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=f"{API_V1_PREFIX}/auth", tags=["v1 - Authentication"])
app.include_router(company.router, prefix=f"{API_V1_PREFIX}/companies", tags=["v1 - Companies"])
app.include_router(user.router, prefix=f"{API_V1_PREFIX}/companies", tags=["v1 - Users"])
app.include_router(permission.router, prefix=API_V1_PREFIX, tags=["v1 - Permissions"])
app.include_router(email.router, prefix=f"{API_V1_PREFIX}/email", tags=["v1 - Email Operations"])
app.include_router(tally.router, prefix=API_V1_PREFIX, tags=["v1 - Tally Integration"])
app.include_router(reports.router, prefix=API_V1_PREFIX, tags=["v1 - Reports"])
app.include_router(exports_jobs.router, prefix=API_V1_PREFIX, tags=["v1 - Export Jobs"])
app.include_router(admin_email_settings.router, prefix=API_V1_PREFIX, tags=["v1 - Admin Email Settings"])
app.include_router(email_delivery.router, prefix=API_V1_PREFIX, tags=["v1 - Email Delivery"])
app.include_router(admin_redis_dashboard.router, prefix=API_V1_PREFIX, tags=["v1 - Admin Redis Dashboard"])

# Legacy routes (backward compatibility) - will be deprecated
LEGACY_PREFIX = "/api"
app.include_router(auth.router, prefix=f"{LEGACY_PREFIX}/auth", tags=["Legacy - Auth"], include_in_schema=False)
app.include_router(company.router, prefix=f"{LEGACY_PREFIX}/companies", tags=["Legacy"], include_in_schema=False)
app.include_router(user.router, prefix=f"{LEGACY_PREFIX}/companies", tags=["Legacy"], include_in_schema=False)
app.include_router(permission.router, prefix=LEGACY_PREFIX, tags=["Legacy"], include_in_schema=False)
app.include_router(exports_jobs.router, prefix=LEGACY_PREFIX, tags=["Legacy"], include_in_schema=False)
app.include_router(admin_email_settings.router, prefix=LEGACY_PREFIX, tags=["Legacy"], include_in_schema=False)
app.include_router(email_delivery.router, prefix=LEGACY_PREFIX, tags=["Legacy"], include_in_schema=False)


@app.get("/admin/redis-dashboard.html")
async def admin_redis_dashboard_shortcut():
    return RedirectResponse(url="/frontend/admin/redis-dashboard.html")


@app.get("/admin/{path:path}")
async def admin_frontend_redirect(path: str):
    return RedirectResponse(url=f"/frontend/admin/{path}")


# ==================== STATIC FILES (Frontend) ====================
# Mount frontend static files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/frontend", StaticFiles(directory=frontend_path, html=True), name="frontend")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    db_info = get_db_info()
    logger.info(f"Database: {db_info['type']}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logger.info("Shutting down application...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8451,
        reload=settings.DEBUG
    )
