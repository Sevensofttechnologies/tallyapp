"""
Email Message Schemas
Pydantic models for message validation
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    EMAIL_SEND = "EMAIL_SEND"
    EMAIL_WELCOME = "EMAIL_WELCOME"
    EMAIL_PASSWORD_RESET = "EMAIL_PASSWORD_RESET"
    EMAIL_VERIFICATION = "EMAIL_VERIFICATION"
    EMAIL_NOTIFICATION = "EMAIL_NOTIFICATION"


class EncryptionInfo(BaseModel):
    """Encryption metadata"""
    alg: str = "AES-256-GCM"
    key_id: str = "email-key-v1"


class MessageMetadata(BaseModel):
    """Message metadata"""
    source_service: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    priority: Optional[int] = 0


class EmailMessage(BaseModel):
    """Email message schema for RabbitMQ consumption"""
    message_id: str = Field(..., description="Unique message ID for idempotency")
    event_type: EventType = EventType.EMAIL_SEND
    to: List[EmailStr] = Field(..., min_length=1)
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    subject: str = Field(..., min_length=1, max_length=500)
    template: str = Field(..., description="Template filename")
    payload_encrypted: Optional[str] = Field(None, description="Base64 encrypted payload")
    payload: Optional[Dict[str, Any]] = Field(None, description="Unencrypted payload (dev only)")
    encryption: Optional[EncryptionInfo] = None
    metadata: MessageMetadata
    attachments: Optional[List[Dict[str, str]]] = None
    retry_count: int = 0
    
    @field_validator('template')
    @classmethod
    def validate_template(cls, v):
        if not v.endswith('.html'):
            v = f"{v}.html"
        return v


class EmailStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SENT = "SENT"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    DLQ = "DLQ"


class ProcessingResult(BaseModel):
    """Result of email processing"""
    message_id: str
    status: EmailStatus
    error_message: Optional[str] = None
    retry_count: int = 0
    processed_at: datetime = Field(default_factory=datetime.utcnow)
