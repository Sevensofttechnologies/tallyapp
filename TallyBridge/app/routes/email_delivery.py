from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.email_delivery import (
    EmailDeliveryQueueRequest,
    EmailDeliveryQueueResponse,
    EmailAuditListResponse,
    EmailAuditItem,
    EmailAuditRetryResponse,
)
from app.services.email_delivery_service import EmailDeliveryService
from app.utils.dependencies import get_current_active_user
from app.utils.helpers import success_response


router = APIRouter()


@router.post('/email/delivery/queue', response_model=EmailDeliveryQueueResponse)
async def queue_email_delivery(
    body: EmailDeliveryQueueRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    audit = EmailDeliveryService.queue_email(
        db=db,
        current_user=current_user,
        company_id=body.company_id,
        to=[str(x) for x in body.to],
        cc=[str(x) for x in body.cc] if body.cc else None,
        bcc=[str(x) for x in body.bcc] if body.bcc else None,
        subject=body.subject,
        text_body=body.text_body,
        html_body=body.html_body,
        report_type=body.report_type,
        report_params=body.report_params,
        fmt=body.format,
        attachment_path=body.attachment_path,
        download_link=body.download_link,
        source='manual',
    )

    return EmailDeliveryQueueResponse(audit_id=audit.id, status=audit.status)


@router.get('/email/delivery/audit', response_model=EmailAuditListResponse)
async def list_email_audit(
    company_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    items, total = EmailDeliveryService.list_audit(
        db=db,
        current_user=current_user,
        company_id=company_id,
        page=page,
        per_page=per_page,
        status_filter=status,
    )

    return EmailAuditListResponse(
        items=[
            EmailAuditItem(
                id=x.id,
                company_id=x.company_id,
                sent_by_user_id=x.sent_by_user_id,
                source=x.source,
                report_type=x.report_type,
                report_params_json=x.report_params_json,
                to_email=x.to_email,
                cc=x.cc,
                bcc=x.bcc,
                format=x.format,
                attachment_used=x.attachment_used,
                download_link_used=x.download_link_used,
                result_file_path=x.result_file_path,
                status=x.status,
                error_message=x.error_message,
                created_at=x.created_at.isoformat(),
            )
            for x in items
        ],
        page=page,
        per_page=per_page,
        total=total,
    )


@router.post('/email/delivery/{audit_id}/retry', response_model=EmailAuditRetryResponse)
async def retry_email_audit(
    audit_id: int,
    company_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    audit = EmailDeliveryService.retry_audit(
        db=db,
        current_user=current_user,
        company_id=company_id,
        audit_id=audit_id,
    )

    return EmailAuditRetryResponse(audit_id=audit.id, status=audit.status)
