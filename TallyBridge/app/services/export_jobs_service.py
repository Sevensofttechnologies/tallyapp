"""Export Jobs Service

DB-backed export job creation/status/download helpers.
"""

import os
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.models.export_job import ExportJob
from app.models.user import User
from app.utils.permissions import check_company_access
from app.services.redis_queue import enqueue_export_job


class ExportJobsService:
    @staticmethod
    def create_job(
        db: Session,
        current_user: User,
        company_id: int,
        report_type: str,
        params: Optional[Dict[str, Any]] = None,
        export_format: Optional[str] = None,
    ) -> ExportJob:
        if current_user.role != "super_admin" and not check_company_access(current_user.id, company_id, db):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to this company")

        job = ExportJob(
            company_id=company_id,
            created_by_user_id=current_user.id,
            job_type="manual",
            report_type=report_type,
            params_json={
                "params": params or {},
                "format": export_format,
            },
            status="queued",
            progress=0,
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        enqueue_export_job(job.id, {"company_id": company_id})
        return job

    @staticmethod
    def get_job(db: Session, current_user: User, company_id: int, job_id: int) -> ExportJob:
        if current_user.role != "super_admin" and not check_company_access(current_user.id, company_id, db):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to this company")

        job = (
            db.query(ExportJob)
            .filter(ExportJob.id == job_id, ExportJob.company_id == company_id)
            .first()
        )
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        return job

    @staticmethod
    def get_download_path(job: ExportJob) -> str:
        if not job.result_file_path:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job has no output file")

        base_dir = os.path.abspath(settings.EXPORT_STORAGE_DIR)
        candidate = os.path.abspath(job.result_file_path)

        if not candidate.startswith(base_dir):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file path")

        if not os.path.exists(candidate):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

        return candidate
