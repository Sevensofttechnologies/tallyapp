"""
Application Configuration
Environment variables and settings
"""

import sys
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional, Union
import os

# Known weak/placeholder values that must never be used in any environment
_BANNED_KEYS = {
    "your-secret-key-change-in-production",
    "your-super-secret-key-change-this-in-production",
    "tallybots-super-secret-key-change-in-production-2026",
    "change-me",
    "secret",
    "password",
}

_MIN_KEY_LENGTH = 32


def _validate_secret_key(value: str) -> str:
    """
    Fail fast if SECRET_KEY is missing, too short, or a known placeholder.
    Called at import time so the app refuses to start with a weak key.
    """
    if not value:
        sys.exit(
            "\n[FATAL] SECRET_KEY is not set.\n"
            "Generate one with:  python -c \"import secrets; print(secrets.token_urlsafe(48))\"\n"
            "Then add it to your .env file.\n"
        )
    if value in _BANNED_KEYS:
        sys.exit(
            f"\n[FATAL] SECRET_KEY is a known placeholder value and must not be used.\n"
            f"Generate a real key with:  python -c \"import secrets; print(secrets.token_urlsafe(48))\"\n"
            f"Then add it to your .env file.\n"
        )
    if len(value) < _MIN_KEY_LENGTH:
        sys.exit(
            f"\n[FATAL] SECRET_KEY is too short ({len(value)} chars). "
            f"Minimum is {_MIN_KEY_LENGTH} characters.\n"
            f"Generate one with:  python -c \"import secrets; print(secrets.token_urlsafe(48))\"\n"
        )
    return value


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Application Starter Kit"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # Security
    # SECRET_KEY must be set in the environment / .env file.
    # No default is provided — the app will refuse to start without a strong key.
    # Generate with: python -c "import secrets; print(secrets.token_urlsafe(48))"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email Settings Encryption
    EMAIL_SETTINGS_ENCRYPTION_KEY: str = "change-me-email-settings-key"
    
    # Allowed Hosts
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0", "*"]
    
    # CORS - stored as string, parsed to list
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000,http://localhost:8080,http://localhost:8901,http://127.0.0.1:8901"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string to list"""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        return self.ALLOWED_ORIGINS
    
    # Worker Configuration
    WORKERS: int = 1

    # Redis (Queue/Status)
    REDIS_URL: str = "redis://localhost:6379/0"
    EXPORT_JOBS_QUEUE_NAME: str = "export_jobs"
    EMAIL_JOBS_QUEUE_NAME: str = "email_jobs"

    EMAIL_MAX_RETRY_COUNT: int = 5
    EMAIL_RETRY_BACKOFF_SECONDS: str = "30,120,300,900,1800"
    EMAIL_RETRY_SWEEP_INTERVAL_SECONDS: int = 5

    # Export file storage (Local Disk)
    EXPORT_STORAGE_DIR: str = "./export_files"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Password hashing
    PWD_SCHEME: str = "bcrypt"
    PWD_DEPRECATED: str = "auto"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_be_strong(cls, v: str) -> str:
        return _validate_secret_key(v)


settings = Settings()
