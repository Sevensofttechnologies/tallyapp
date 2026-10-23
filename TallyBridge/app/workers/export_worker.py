"""Export Jobs Worker (Skeleton)

Run as a separate process:
    python -m app.workers.export_worker

This worker consumes Redis queue messages and updates DB job status.
For now, it generates a dummy file so we can verify end-to-end flow.
"""

import os
import time
from datetime import datetime

from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models.export_job import ExportJob
from app.services.redis_queue import dequeue_export_job, inflight_add, inflight_remove, set_worker_heartbeat


def _ensure_export_dir() -> str:
    export_dir = os.path.abspath(settings.EXPORT_STORAGE_DIR)
    os.makedirs(export_dir, exist_ok=True)
    return export_dir


def _set_job_status(db: Session, job: ExportJob, status: str, progress: int = None, error: str = None) -> None:
    job.status = status
    if progress is not None:
        job.progress = progress
    if error is not None:
        job.error_message = error
    db.commit()
    db.refresh(job)


def _process_job(job_id: int) -> None:
    db: Session = SessionLocal()
    try:
        job = db.query(ExportJob).filter(ExportJob.id == job_id).first()
        if not job:
            return

        _set_job_status(db, job, status="running", progress=5)

        export_dir = _ensure_export_dir()
        filename = f"export_job_{job.id}_{int(time.time())}.txt"
        out_path = os.path.join(export_dir, filename)

        payload = job.params_json or {}
        report_type = job.report_type

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(f"Export Job ID: {job.id}\n")
            f.write(f"Report Type: {report_type}\n")
            f.write(f"Generated At: {datetime.utcnow().isoformat()}Z\n")
            f.write(f"Params: {payload}\n")

        job.result_file_path = out_path
        _set_job_status(db, job, status="done", progress=100)

    except Exception as e:
        try:
            job = db.query(ExportJob).filter(ExportJob.id == job_id).first()
            if job:
                _set_job_status(db, job, status="failed", error=str(e))
        except Exception:
            pass
    finally:
        db.close()


def run_forever(poll_timeout_seconds: int = 5) -> None:
    _ensure_export_dir()

    last_heartbeat = 0.0

    while True:
        now = time.time()
        if now - last_heartbeat >= 5.0:
            set_worker_heartbeat("export", ttl_seconds=60)
            last_heartbeat = now

        msg = dequeue_export_job(timeout=poll_timeout_seconds)
        if not msg:
            continue

        job_id = msg.get("job_id")
        if not isinstance(job_id, int):
            continue

        inflight_add(settings.EXPORT_JOBS_QUEUE_NAME, str(job_id))
        try:
            _process_job(job_id)
        finally:
            inflight_remove(settings.EXPORT_JOBS_QUEUE_NAME, str(job_id))


if __name__ == "__main__":
    run_forever()
