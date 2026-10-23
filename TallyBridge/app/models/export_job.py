"""Export Job Model"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.sql import func

from app.database import Base


class ExportJob(Base):
    __tablename__ = "export_jobs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    job_type = Column(String(20), nullable=False, default="manual")
    report_type = Column(String(100), nullable=False, index=True)
    params_json = Column(JSON, nullable=True)

    status = Column(String(20), nullable=False, default="queued", index=True)
    progress = Column(Integer, nullable=False, default=0)

    result_file_path = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_export_job_company_status", "company_id", "status"),
    )
