"""Schemas for SMTP/Email Settings"""

from typing import Optional

from pydantic import BaseModel, Field


class EmailSettingsResponse(BaseModel):
    company_id: int

    smtp_host: str
    smtp_port: int
    smtp_user: Optional[str] = None

    use_tls: bool
    use_ssl: bool

    from_email: str
    from_name: Optional[str] = None
    reply_to: Optional[str] = None

    has_password: bool


class EmailSettingsUpsertRequest(BaseModel):
    company_id: int = Field(..., ge=1)

    smtp_host: str = Field(..., min_length=1)
    smtp_port: int = Field(default=587, ge=1, le=65535)
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None

    use_tls: bool = True
    use_ssl: bool = False

    from_email: str = Field(..., min_length=3)
    from_name: Optional[str] = None
    reply_to: Optional[str] = None


class EmailSettingsTestRequest(BaseModel):
    company_id: int = Field(..., ge=1)
    to_email: str = Field(..., min_length=3)
    subject: str = Field(default="TallyBridge SMTP Test")
    body: str = Field(default="This is a test email from TallyBridge.")
