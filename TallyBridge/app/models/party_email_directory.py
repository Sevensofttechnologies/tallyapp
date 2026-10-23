"""Party Email Directory Model"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.sql import func

from app.database import Base


class PartyEmailDirectory(Base):
    __tablename__ = "party_email_directory"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)

    company_name = Column(String(255), nullable=True)
    party_name = Column(String(255), nullable=False, index=True)

    email = Column(String(255), nullable=False)
    is_primary = Column(Boolean, default=True, nullable=False)

    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_party_email_company_party", "company_id", "party_name"),
    )
