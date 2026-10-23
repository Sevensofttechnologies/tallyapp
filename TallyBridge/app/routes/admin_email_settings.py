"""Admin Email Settings Routes (SMTP)

Admin-only endpoints for saving SMTP settings and sending test email.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.email_settings import (
    EmailSettingsResponse,
    EmailSettingsUpsertRequest,
    EmailSettingsTestRequest,
)
from app.services.email_settings_service import EmailSettingsService
from app.utils.dependencies import get_current_active_user
from app.utils.helpers import success_response


router = APIRouter()


@router.get("/admin/email-settings", response_model=EmailSettingsResponse)
async def get_email_settings(
    company_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    row = EmailSettingsService.get_settings(db=db, current_user=current_user, company_id=company_id)
    if not row:
        return EmailSettingsResponse(
            company_id=company_id,
            smtp_host="",
            smtp_port=587,
            smtp_user=None,
            use_tls=True,
            use_ssl=False,
            from_email="",
            from_name=None,
            reply_to=None,
            has_password=False,
        )

    return EmailSettingsResponse(
        company_id=row.company_id,
        smtp_host=row.smtp_host,
        smtp_port=row.smtp_port,
        smtp_user=row.smtp_user,
        use_tls=row.use_tls,
        use_ssl=row.use_ssl,
        from_email=row.from_email,
        from_name=row.from_name,
        reply_to=row.reply_to,
        has_password=bool(row.smtp_password_encrypted),
    )


@router.put("/admin/email-settings")
async def upsert_email_settings(
    body: EmailSettingsUpsertRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    row = EmailSettingsService.upsert_settings(
        db=db,
        current_user=current_user,
        company_id=body.company_id,
        smtp_host=body.smtp_host,
        smtp_port=body.smtp_port,
        smtp_user=body.smtp_user,
        smtp_password=body.smtp_password,
        use_tls=body.use_tls,
        use_ssl=body.use_ssl,
        from_email=body.from_email,
        from_name=body.from_name,
        reply_to=body.reply_to,
    )

    return success_response(
        data={"company_id": row.company_id, "updated": True},
        message="Email settings saved",
    )


@router.post("/admin/email-settings/test")
async def test_email_settings(
    body: EmailSettingsTestRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    EmailSettingsService.send_test_email(
        db=db,
        current_user=current_user,
        company_id=body.company_id,
        to_email=body.to_email,
        subject=body.subject,
        body=body.body,
    )

    return success_response(data={"sent": True}, message="Test email sent")
