"""Email Audit Model"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON, Index
from sqlalchemy.sql import func

from app.database import Base


class EmailAudit(Base):
    __tablename__ = "email_audit"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    sent_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    source = Column(String(20), nullable=False, default="manual", index=True)

    report_type = Column(String(100), nullable=False, index=True)
    report_params_json = Column(JSON, nullable=True)

    to_email = Column(String(512), nullable=False)
    cc = Column(String(1024), nullable=True)
    bcc = Column(String(1024), nullable=True)

    format = Column(String(20), nullable=False)

    attachment_used = Column(Boolean, default=False, nullable=False)
    download_link_used = Column(Boolean, default=False, nullable=False)

    result_file_path = Column(Text, nullable=True)

    status = Column(String(20), nullable=False, default="queued", index=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)

    __table_args__ = (
        Index("idx_email_audit_company_created", "company_id", "created_at"),
    )
