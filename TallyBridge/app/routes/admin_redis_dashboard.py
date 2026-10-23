from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.email_audit import EmailAudit
from app.models.export_job import ExportJob
from app.models.user import User
from app.services.redis_queue import (
    dlq_delete_one,
    dlq_peek,
    dlq_requeue_one,
    get_queue_lengths,
    peek_queue,
    purge_queue,
    redis_info,
    workers_status,
)
from app.utils.dependencies import get_current_active_user
from app.utils.permissions import check_company_access, check_company_admin


router = APIRouter()


def _require_company_access(db: Session, user: User, company_id: int) -> None:
    if user.role == "super_admin":
        return
    if not check_company_access(user.id, company_id, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to this company")


def _require_company_admin(db: Session, user: User, company_id: int) -> None:
    if user.role == "super_admin":
        return
    if not check_company_admin(user.id, company_id, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")


@router.get("/admin/redis/health")
async def get_health(
    company_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _require_company_access(db, current_user, company_id)
    return {"success": True, "data": redis_info()}


@router.get("/admin/redis/queues")
async def get_queues(
    company_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _require_company_access(db, current_user, company_id)
    return {"success": True, "data": get_queue_lengths()}


@router.get("/admin/redis/peek")
async def get_peek(
    company_id: int,
    queue: str = Query(..., pattern="^(email_jobs|export_jobs)$"),
    side: str = Query("tail", pattern="^(head|tail)$"),
    count: int = Query(20, ge=1, le=200),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _require_company_access(db, current_user, company_id)
    return {"success": True, "data": {"queue": queue, "side": side, "items": peek_queue(queue, side=side, count=count)}}


@router.post("/admin/redis/purge")
async def post_purge(
    company_id: int,
    queue: str = Query(..., pattern="^(email_jobs|export_jobs)$"),
    mode: str = Query("all", pattern="^(all|last_n)$"),
    count: int = Query(0, ge=0, le=100000),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _require_company_admin(db, current_user, company_id)
    removed = purge_queue(queue, mode=mode, count=count)
    return {"success": True, "data": {"removed": removed}}


@router.get("/admin/redis/workers")
async def get_workers(
    company_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _require_company_access(db, current_user, company_id)
    return {"success": True, "data": workers_status()}


@router.get("/admin/redis/dlq")
async def get_dlq(
    company_id: int,
    dlq_type: str = Query(..., pattern="^(email|export)$"),
    count: int = Query(20, ge=1, le=200),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _require_company_access(db, current_user, company_id)
    return {"success": True, "data": {"type": dlq_type, "items": dlq_peek(dlq_type, count=count)}}


@router.post("/admin/redis/dlq/requeue-one")
async def post_dlq_requeue_one(
    company_id: int,
    dlq_type: str = Query(..., pattern="^(email|export)$"),
    index: int = Query(..., ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _require_company_admin(db, current_user, company_id)
    moved = dlq_requeue_one(dlq_type, index=index)
    return {"success": True, "data": {"moved": moved}}


@router.post("/admin/redis/dlq/delete-one")
async def post_dlq_delete_one(
    company_id: int,
    dlq_type: str = Query(..., pattern="^(email|export)$"),
    index: int = Query(..., ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _require_company_admin(db, current_user, company_id)
    removed = dlq_delete_one(dlq_type, index=index)
    return {"success": True, "data": {"removed": removed}}


def _bucket_hour(ts: datetime) -> str:
    return ts.replace(minute=0, second=0, microsecond=0).isoformat()


@router.get("/admin/redis/history")
async def get_history(
    company_id: int,
    hours: int = Query(48, ge=1, le=24 * 30),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _require_company_access(db, current_user, company_id)

    since = datetime.utcnow() - timedelta(hours=hours)

    email_rows: List[EmailAudit] = (
        db.query(EmailAudit)
        .filter(EmailAudit.company_id == company_id, EmailAudit.created_at >= since)
        .all()
    )
    export_rows: List[ExportJob] = (
        db.query(ExportJob)
        .filter(ExportJob.company_id == company_id, ExportJob.created_at >= since)
        .all()
    )

    buckets: Dict[str, Dict[str, int]] = {}

    def inc(bucket_key: str, name: str) -> None:
        if bucket_key not in buckets:
            buckets[bucket_key] = {"emails_total": 0, "emails_sent": 0, "emails_failed": 0, "exports_total": 0, "exports_done": 0, "exports_failed": 0}
        buckets[bucket_key][name] = int(buckets[bucket_key].get(name) or 0) + 1

    for row in email_rows:
        b = _bucket_hour(row.created_at)
        inc(b, "emails_total")
        if row.status == "sent":
            inc(b, "emails_sent")
        elif row.status in {"failed", "dead"}:
            inc(b, "emails_failed")

    for row in export_rows:
        b = _bucket_hour(row.created_at)
        inc(b, "exports_total")
        if row.status == "done":
            inc(b, "exports_done")
        elif row.status in {"failed", "dead"}:
            inc(b, "exports_failed")

    series = [
        {"hour": k, **v}
        for k, v in sorted(buckets.items(), key=lambda x: x[0])
    ]

    return {"success": True, "data": {"hours": hours, "series": series}}
