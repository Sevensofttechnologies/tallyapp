from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.email_audit import EmailAudit
from app.models.email_settings import EmailSettings
from app.models.user import User
from app.services.redis_queue import dlq_push, enqueue_email_job
from app.services.smtp_sender import send_smtp_email
from app.config import settings
from app.utils.crypto import decrypt_text
from app.utils.permissions import check_company_access, check_company_admin


class EmailDeliveryService:
    @staticmethod
    def _parse_backoff_seconds() -> List[int]:
        raw = settings.EMAIL_RETRY_BACKOFF_SECONDS or ""
        values: List[int] = []
        for part in raw.split(','):
            part = part.strip()
            if not part:
                continue
            try:
                values.append(max(1, int(part)))
            except Exception:
                continue
        return values or [30, 120, 300, 900, 1800]

    @staticmethod
    def _get_retry_meta(audit: EmailAudit) -> Dict[str, Any]:
        if isinstance(audit.report_params_json, dict):
            return audit.report_params_json.get('delivery_retry') or {}
        return {}

    @staticmethod
    def _set_retry_meta(audit: EmailAudit, meta: Dict[str, Any]) -> None:
        base: Dict[str, Any] = audit.report_params_json if isinstance(audit.report_params_json, dict) else {}
        base['delivery_retry'] = meta
        audit.report_params_json = base
    @staticmethod
    def _require_company_access(db: Session, current_user: User, company_id: int) -> None:
        if current_user.role == 'super_admin':
            return
        if not check_company_access(current_user.id, company_id, db):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No access to this company')

    @staticmethod
    def _require_company_admin(db: Session, current_user: User, company_id: int) -> None:
        if current_user.role == 'super_admin':
            return
        if not check_company_admin(current_user.id, company_id, db):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin access required')

    @staticmethod
    def queue_email(
        db: Session,
        current_user: User,
        company_id: int,
        to: List[str],
        cc: Optional[List[str]],
        bcc: Optional[List[str]],
        subject: str,
        text_body: Optional[str],
        html_body: Optional[str],
        report_type: str,
        report_params: Optional[Dict[str, Any]],
        fmt: str,
        attachment_path: Optional[str],
        download_link: Optional[str],
        source: str = 'manual',
    ) -> EmailAudit:
        EmailDeliveryService._require_company_access(db, current_user, company_id)

        delivery_payload: Dict[str, Any] = {
            'company_id': company_id,
            'subject': subject,
            'text_body': text_body,
            'html_body': html_body,
            'to': to,
            'cc': cc,
            'bcc': bcc,
            'attachment_path': attachment_path,
            'download_link': download_link,
        }

        audit = EmailAudit(
            company_id=company_id,
            sent_by_user_id=current_user.id,
            source=source,
            report_type=report_type,
            report_params_json={
                'report_params': report_params,
                'delivery': delivery_payload,
            },
            to_email=','.join(to),
            cc=','.join(cc) if cc else None,
            bcc=','.join(bcc) if bcc else None,
            format=fmt,
            attachment_used=bool(attachment_path),
            download_link_used=bool(download_link),
            result_file_path=attachment_path,
            status='queued',
            error_message=None,
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)

        enqueue_email_job(audit.id, delivery_payload)
        return audit

    @staticmethod
    def list_audit(
        db: Session,
        current_user: User,
        company_id: int,
        page: int,
        per_page: int,
        status_filter: Optional[str] = None,
    ) -> Tuple[List[EmailAudit], int]:
        EmailDeliveryService._require_company_access(db, current_user, company_id)

        q = db.query(EmailAudit).filter(EmailAudit.company_id == company_id)
        if status_filter:
            q = q.filter(EmailAudit.status == status_filter)

        total = q.count()
        items = (
            q.order_by(EmailAudit.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return items, total

    @staticmethod
    def retry_audit(db: Session, current_user: User, company_id: int, audit_id: int) -> EmailAudit:
        EmailDeliveryService._require_company_admin(db, current_user, company_id)

        audit = db.query(EmailAudit).filter(EmailAudit.id == audit_id, EmailAudit.company_id == company_id).first()
        if not audit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Audit not found')

        if audit.status not in ['failed', 'queued']:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Only failed/queued can be retried')

        audit.status = 'queued'
        audit.error_message = None
        db.commit()
        db.refresh(audit)

        stored = audit.report_params_json or {}
        delivery_payload = stored.get('delivery') if isinstance(stored, dict) else None
        enqueue_email_job(audit.id, delivery_payload or {})
        return audit

    @staticmethod
    def sweep_due_retries(db: Session, limit: int = 50) -> int:
        """Auto requeue failed emails that are due for retry.

        This avoids DB schema changes by storing retry metadata inside report_params_json.
        """

        now = datetime.utcnow()
        backoffs = EmailDeliveryService._parse_backoff_seconds()

        # NOTE: JSON field querying differs across DBs; keep it portable by filtering in Python.
        candidates: List[EmailAudit] = (
            db.query(EmailAudit)
            .filter(EmailAudit.status == 'failed')
            .order_by(EmailAudit.created_at.asc())
            .limit(500)
            .all()
        )

        requeued = 0
        for audit in candidates:
            if requeued >= limit:
                break

            meta = EmailDeliveryService._get_retry_meta(audit)
            retry_count = int(meta.get('retry_count') or 0)
            next_retry_at = meta.get('next_retry_at')

            if retry_count <= 0 or not next_retry_at:
                continue

            try:
                due = datetime.fromisoformat(next_retry_at)
            except Exception:
                continue

            if due > now:
                continue

            if retry_count > settings.EMAIL_MAX_RETRY_COUNT:
                audit.status = 'dead'
                EmailDeliveryService._set_retry_meta(
                    audit,
                    {
                        'retry_count': retry_count,
                        'next_retry_at': None,
                        'last_error': meta.get('last_error'),
                    },
                )
                requeued += 1
                continue

            stored = audit.report_params_json or {}
            delivery_payload = stored.get('delivery') if isinstance(stored, dict) else None

            audit.status = 'queued'
            db.add(audit)
            enqueue_email_job(audit.id, delivery_payload or {})

            # Compute a fresh next_retry_at so we don't hot-loop if send fails again quickly.
            idx = min(max(0, retry_count - 1), len(backoffs) - 1)
            next_due = now + timedelta(seconds=backoffs[idx])
            EmailDeliveryService._set_retry_meta(
                audit,
                {
                    'retry_count': retry_count,
                    'next_retry_at': next_due.isoformat(),
                    'last_error': meta.get('last_error'),
                },
            )
            requeued += 1

        if requeued:
            db.commit()

        return requeued

    @staticmethod
    def process_audit_send(db: Session, audit_id: int, payload: Dict[str, Any]) -> None:
        audit = db.query(EmailAudit).filter(EmailAudit.id == audit_id).first()
        if not audit:
            return

        settings = db.query(EmailSettings).filter(EmailSettings.company_id == audit.company_id).first()
        if not settings:
            audit.status = 'failed'
            audit.error_message = 'Email settings not configured'
            db.commit()
            return

        password = decrypt_text(settings.smtp_password_encrypted) if settings.smtp_password_encrypted else None
        if settings.smtp_user and not password:
            audit.status = 'failed'
            audit.error_message = 'SMTP password not set'
            db.commit()
            return

        to = payload.get('to') or (audit.to_email.split(',') if audit.to_email else [])
        cc = payload.get('cc') or (audit.cc.split(',') if audit.cc else None)
        bcc = payload.get('bcc') or (audit.bcc.split(',') if audit.bcc else None)

        subject = payload.get('subject') or f"Report: {audit.report_type}"
        text_body = payload.get('text_body')
        html_body = payload.get('html_body')

        if not text_body and not html_body:
            link = payload.get('download_link')
            if link:
                text_body = f"Download: {link}"
            else:
                text_body = 'Report is ready.'

        audit.status = 'sending'
        audit.error_message = None
        db.commit()

        try:
            send_smtp_email(
                host=settings.smtp_host,
                port=settings.smtp_port,
                user=settings.smtp_user,
                password=password,
                use_tls=settings.use_tls,
                use_ssl=settings.use_ssl,
                from_email=settings.from_email,
                from_name=settings.from_name,
                reply_to=settings.reply_to,
                to=to,
                cc=cc,
                bcc=bcc,
                subject=subject,
                text_body=text_body,
                html_body=html_body,
            )
            audit.status = 'sent'
            audit.error_message = None
        except Exception as e:
            err = str(e)
            retry_meta = EmailDeliveryService._get_retry_meta(audit)
            retry_count = int(retry_meta.get('retry_count') or 0)
            retry_count += 1

            if retry_count > settings.EMAIL_MAX_RETRY_COUNT:
                audit.status = 'dead'
                audit.error_message = err
                try:
                    dlq_push(
                        "email",
                        {
                            "audit_id": audit.id,
                            "payload": payload,
                            "error": err,
                        },
                    )
                except Exception:
                    pass
                EmailDeliveryService._set_retry_meta(
                    audit,
                    {
                        'retry_count': retry_count,
                        'next_retry_at': None,
                        'last_error': err,
                    },
                )
            else:
                backoffs = EmailDeliveryService._parse_backoff_seconds()
                idx = min(retry_count - 1, len(backoffs) - 1)
                next_retry_at = datetime.utcnow() + timedelta(seconds=backoffs[idx])
                audit.status = 'failed'
                audit.error_message = err
                EmailDeliveryService._set_retry_meta(
                    audit,
                    {
                        'retry_count': retry_count,
                        'next_retry_at': next_retry_at.isoformat(),
                        'last_error': err,
                    },
                )
        finally:
            db.commit()
