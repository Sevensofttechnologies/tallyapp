"""Email Settings Service

Stores tenant/company SMTP settings encrypted in DB and provides test email.
"""

import smtplib
from email.mime.text import MIMEText
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.email_settings import EmailSettings
from app.models.user import User
from app.utils.permissions import check_company_admin
from app.utils.crypto import encrypt_text, decrypt_text


class EmailSettingsService:
    @staticmethod
    def _require_company_admin(db: Session, current_user: User, company_id: int) -> None:
        if current_user.role == "super_admin":
            return
        if not check_company_admin(current_user.id, company_id, db):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    @staticmethod
    def get_settings(db: Session, current_user: User, company_id: int) -> Optional[EmailSettings]:
        EmailSettingsService._require_company_admin(db, current_user, company_id)
        return db.query(EmailSettings).filter(EmailSettings.company_id == company_id).first()

    @staticmethod
    def upsert_settings(
        db: Session,
        current_user: User,
        company_id: int,
        smtp_host: str,
        smtp_port: int,
        smtp_user: Optional[str],
        smtp_password: Optional[str],
        use_tls: bool,
        use_ssl: bool,
        from_email: str,
        from_name: Optional[str],
        reply_to: Optional[str],
    ) -> EmailSettings:
        EmailSettingsService._require_company_admin(db, current_user, company_id)

        row = db.query(EmailSettings).filter(EmailSettings.company_id == company_id).first()
        if not row:
            row = EmailSettings(company_id=company_id)
            db.add(row)

        row.smtp_host = smtp_host
        row.smtp_port = smtp_port
        row.smtp_user = smtp_user
        if smtp_password is not None:
            row.smtp_password_encrypted = encrypt_text(smtp_password)

        row.use_tls = use_tls
        row.use_ssl = use_ssl

        row.from_email = from_email
        row.from_name = from_name
        row.reply_to = reply_to

        db.commit()
        db.refresh(row)
        return row

    @staticmethod
    def send_test_email(db: Session, current_user: User, company_id: int, to_email: str, subject: str, body: str) -> None:
        EmailSettingsService._require_company_admin(db, current_user, company_id)

        row = db.query(EmailSettings).filter(EmailSettings.company_id == company_id).first()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email settings not configured")

        password = decrypt_text(row.smtp_password_encrypted) if row.smtp_password_encrypted else None
        if not password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SMTP password not set")

        msg = MIMEText(body, "plain", "utf-8")
        from_addr = row.from_email
        msg["From"] = f"{row.from_name} <{from_addr}>" if row.from_name else from_addr
        msg["To"] = to_email
        msg["Subject"] = subject
        if row.reply_to:
            msg["Reply-To"] = row.reply_to

        try:
            if row.use_ssl:
                server = smtplib.SMTP_SSL(row.smtp_host, row.smtp_port, timeout=30)
            else:
                server = smtplib.SMTP(row.smtp_host, row.smtp_port, timeout=30)

            try:
                server.ehlo()
                if row.use_tls and not row.use_ssl:
                    server.starttls()
                    server.ehlo()

                if row.smtp_user:
                    server.login(row.smtp_user, password)

                server.sendmail(from_addr, [to_email], msg.as_string())
            finally:
                try:
                    server.quit()
                except Exception:
                    pass

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Test email failed: {e}")
