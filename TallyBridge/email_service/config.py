"""
Email Microservice Configuration
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class EmailServiceSettings(BaseSettings):
    """Email service configuration"""
    
    # RabbitMQ Configuration
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_VHOST: str = "/"
    RABBITMQ_PREFETCH_COUNT: int = 10
    
    # Exchange & Queue Names
    EMAIL_EXCHANGE: str = "email.exchange"
    EMAIL_RETRY_EXCHANGE: str = "email.retry.exchange"
    EMAIL_DLX: str = "email.dlx"
    
    EMAIL_QUEUE: str = "email.queue"
    EMAIL_RETRY_30S_QUEUE: str = "email.retry.30s.queue"
    EMAIL_RETRY_2M_QUEUE: str = "email.retry.2m.queue"
    EMAIL_RETRY_5M_QUEUE: str = "email.retry.5m.queue"
    EMAIL_DLQ: str = "email.dlq"
    
    # Retry Configuration
    MAX_RETRY_COUNT: int = 3
    RETRY_DELAYS: list = [30000, 120000, 300000]  # 30s, 2m, 5m in ms
    
    # SMTP Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@example.com"
    SMTP_FROM_NAME: str = "Application Starter Kit"
    SMTP_USE_TLS: bool = True
    
    # Email Provider (smtp, ses, sendgrid)
    EMAIL_PROVIDER: str = "smtp"
    
    # AWS SES Configuration
    AWS_REGION: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    
    # SendGrid Configuration
    SENDGRID_API_KEY: Optional[str] = None
    
    # Redis Configuration (for idempotency)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    IDEMPOTENCY_TTL: int = 86400  # 24 hours in seconds
    
    # Encryption
    ENCRYPTION_KEY: str = "your-32-byte-encryption-key-here"
    
    # Templates
    TEMPLATE_DIR: str = "email_service/templates"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


email_settings = EmailServiceSettings()
