"""Email Settings Model"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.sql import func

from app.database import Base


class EmailSettings(Base):
    __tablename__ = "email_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True, unique=True)

    smtp_host = Column(String(255), nullable=False)
    smtp_port = Column(Integer, nullable=False, default=587)
    smtp_user = Column(String(255), nullable=True)
    smtp_password_encrypted = Column(String(2048), nullable=True)

    use_tls = Column(Boolean, default=True, nullable=False)
    use_ssl = Column(Boolean, default=False, nullable=False)

    from_email = Column(String(255), nullable=False)
    from_name = Column(String(255), nullable=True)
    reply_to = Column(String(255), nullable=True)

    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_email_settings_company", "company_id"),
    )
