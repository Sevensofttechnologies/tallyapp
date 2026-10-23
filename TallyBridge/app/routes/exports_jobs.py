"""Export Jobs Routes

API endpoints for job-based exports.
"""

import os

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.export_jobs import ExportJobCreateRequest, ExportJobResponse
from app.services.export_jobs_service import ExportJobsService
from app.utils.dependencies import get_current_active_user
from app.models.user import User


router = APIRouter()


@router.post("/exports/jobs", response_model=ExportJobResponse)
async def create_export_job(
    body: ExportJobCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    job = ExportJobsService.create_job(
        db=db,
        current_user=current_user,
        company_id=body.company_id,
        report_type=body.report_type,
        params=body.params,
        export_format=body.format,
    )

    return ExportJobResponse(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        report_type=job.report_type,
        error_message=job.error_message,
        result_file_path=job.result_file_path,
    )


@router.get("/exports/jobs/{job_id}", response_model=ExportJobResponse)
async def get_export_job_status(
    job_id: int,
    company_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    job = ExportJobsService.get_job(db=db, current_user=current_user, company_id=company_id, job_id=job_id)

    return ExportJobResponse(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        report_type=job.report_type,
        error_message=job.error_message,
        result_file_path=job.result_file_path,
    )


@router.get("/exports/jobs/{job_id}/download")
async def download_export_job_file(
    job_id: int,
    company_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    job = ExportJobsService.get_job(db=db, current_user=current_user, company_id=company_id, job_id=job_id)
    path = ExportJobsService.get_download_path(job)

    return FileResponse(
        path,
        filename=os.path.basename(path),
        media_type="application/octet-stream",
    )
