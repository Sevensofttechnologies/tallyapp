"""
Configuration Management Module
Loads and manages application configuration from config.yaml
"""

import os
import sys
from pathlib import Path
from typing import List, Optional
import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings

# Known weak/placeholder values — must never be used
_BANNED_KEYS = {
    "your-secret-key-change-in-production",
    "your-super-secret-key-change-this-in-production",
    "tallybots-super-secret-key-change-in-production-2026",
    "change-me",
    "secret",
    "password",
}

_MIN_KEY_LENGTH = 32


def _validate_secret_key(value: str, source: str = "JWT_SECRET_KEY") -> str:
    """
    Fail fast if the shared JWT secret is missing, too short, or a known placeholder.
    Called at import time so the app refuses to start with a weak key.
    """
    if not value:
        sys.exit(
            f"\n[FATAL] {source} is not set.\n"
            "Generate one with:  python -c \"import secrets; print(secrets.token_urlsafe(48))\"\n"
            "Then add it to your .env file (same value as TallyBridge SECRET_KEY).\n"
        )
    if value in _BANNED_KEYS:
        sys.exit(
            f"\n[FATAL] {source} is a known placeholder value and must not be used.\n"
            "Generate a real key with:  python -c \"import secrets; print(secrets.token_urlsafe(48))\"\n"
            "Then add it to your .env file (same value as TallyBridge SECRET_KEY).\n"
        )
    if len(value) < _MIN_KEY_LENGTH:
        sys.exit(
            f"\n[FATAL] {source} is too short ({len(value)} chars). "
            f"Minimum is {_MIN_KEY_LENGTH} characters.\n"
            "Generate one with:  python -c \"import secrets; print(secrets.token_urlsafe(48))\"\n"
        )
    return value


class TallyConfig(BaseModel):
    """Tally connection configuration"""
    server: str = "localhost"
    port: int = 9000
    company: str = ""
    from_date: str = "2025-04-01"
    to_date: str = "2026-03-31"


class DatabaseConfig(BaseModel):
    """Database configuration"""
    path: str = "./tally.db"


class SyncConfig(BaseModel):
    """Sync configuration"""
    mode: str = "full"
    batch_size: int = 1000


class ApiConfig(BaseModel):
    """API configuration"""
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8000"))
    # CORS allowed origins — read from CORS_ORIGINS env var (comma-separated).
    # No wildcard is ever used; the app refuses to start without an explicit list.
    cors_origins: List[str] = [
        o.strip()
        for o in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:8501,http://127.0.0.1:8501"
        ).split(",")
        if o.strip()
    ]


class DebugConfig(BaseModel):
    """Debug mode configuration"""
    enabled: bool = False
    verbose_logging: bool = False
    log_sql_queries: bool = False
    log_timing: bool = False
    log_memory: bool = False
    log_http_details: bool = False


class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = "INFO"
    file: str = "./logs/app.log"
    max_size: int = 10
    backup_count: int = 5
    console: bool = True
    colorize: bool = True


class RetryConfig(BaseModel):
    """Retry configuration"""
    enabled: bool = True
    max_attempts: int = 3
    initial_delay: int = 5
    strategy: str = "exponential"
    backoff_multiplier: int = 2
    max_delay: int = 60


class CircuitBreakerConfig(BaseModel):
    """Circuit breaker configuration"""
    enabled: bool = True
    failure_threshold: int = 5
    recovery_timeout: int = 60


class HealthConfig(BaseModel):
    """Health check configuration"""
    check_interval: int = 30
    tally_timeout: int = 5
    database_timeout: int = 2


class AuthConfig(BaseModel):
    """JWT Authentication configuration (shared with TallyBridge).

    The shared secret is read from the environment in this priority order:
      1. JWT_SECRET_KEY  (preferred — explicit name for this service)
      2. SECRET_KEY      (alias — same variable used by TallyBridge)

    Both services MUST use the same value.
    Generate with: python -c "import secrets; print(secrets.token_urlsafe(48))"
    """
    enabled: bool = True
    # Read JWT_SECRET_KEY first, fall back to SECRET_KEY (TallyBridge alias).
    # _validate_secret_key() will sys.exit() if the value is missing or weak.
    secret_key: str = _validate_secret_key(
        os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY", ""),
        source="JWT_SECRET_KEY / SECRET_KEY",
    )
    algorithm: str = os.getenv("JWT_ALGORITHM", os.getenv("ALGORITHM", "HS256"))
    issuer: Optional[str] = os.getenv("JWT_ISSUER", None)
    tallybridge_url: str = os.getenv("TALLYBRIDGE_URL", "http://localhost:8501")


class AppConfig(BaseModel):
    """Main application configuration"""
    tally: TallyConfig = TallyConfig()
    database: DatabaseConfig = DatabaseConfig()
    sync: SyncConfig = SyncConfig()
    api: ApiConfig = ApiConfig()
    debug: DebugConfig = DebugConfig()
    logging: LoggingConfig = LoggingConfig()
    retry: RetryConfig = RetryConfig()
    circuit_breaker: CircuitBreakerConfig = CircuitBreakerConfig()
    health: HealthConfig = HealthConfig()
    auth: AuthConfig = AuthConfig()
    # Feature flag: allow raw SQL via POST /api/data/query.
    # Default is False — the endpoint returns 404 even for admins when disabled.
    # Set ENABLE_RAW_QUERY=true in .env only in trusted, isolated environments.
    enable_raw_query: bool = os.getenv("ENABLE_RAW_QUERY", "false").lower() == "true"


def load_config(config_path: str = "config/config.yaml") -> AppConfig:
    """Load configuration from YAML file"""
    config_file = Path(config_path)
    
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
            return AppConfig(**config_data)
    
    return AppConfig()


def save_config(config: AppConfig, config_path: str = "config/config.yaml") -> None:
    """Save configuration to YAML file"""
    config_file = Path(config_path)
    
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(config.model_dump(), f, default_flow_style=False, allow_unicode=True)


# Global configuration instance
config = load_config()
