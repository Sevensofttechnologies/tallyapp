"""Schemas for Export Jobs"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ExportJobCreateRequest(BaseModel):
    company_id: int = Field(..., ge=1)
    report_type: str = Field(..., min_length=1)
    params: Optional[Dict[str, Any]] = None
    format: Optional[str] = Field(default=None, description="csv/xlsx/pdf")


class ExportJobResponse(BaseModel):
    job_id: int
    status: str
    progress: int = 0
    report_type: str
    error_message: Optional[str] = None
    result_file_path: Optional[str] = None
