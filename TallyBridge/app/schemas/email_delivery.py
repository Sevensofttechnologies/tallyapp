from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class EmailDeliveryQueueRequest(BaseModel):
    company_id: int = Field(..., ge=1)

    to: List[EmailStr] = Field(..., min_length=1)
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None

    subject: str = Field(..., min_length=1, max_length=500)
    text_body: Optional[str] = None
    html_body: Optional[str] = None

    report_type: str = Field(default="manual")
    report_params: Optional[Dict[str, Any]] = None
    format: str = Field(default="pdf")

    attachment_path: Optional[str] = None
    download_link: Optional[str] = None


class EmailDeliveryQueueResponse(BaseModel):
    audit_id: int
    status: str


class EmailAuditItem(BaseModel):
    id: int
    company_id: int
    sent_by_user_id: Optional[int] = None

    source: str
    report_type: str
    report_params_json: Optional[Dict[str, Any]] = None

    to_email: str
    cc: Optional[str] = None
    bcc: Optional[str] = None

    format: str

    attachment_used: bool
    download_link_used: bool

    result_file_path: Optional[str] = None

    status: str
    error_message: Optional[str] = None

    created_at: str


class EmailAuditListResponse(BaseModel):
    items: List[EmailAuditItem]
    page: int
    per_page: int
    total: int


class EmailAuditRetryResponse(BaseModel):
    audit_id: int
    status: str
