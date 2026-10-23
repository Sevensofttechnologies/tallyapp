"""
SMTP Email Provider
Standard SMTP email delivery
"""

import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional
from email_service.providers.base import EmailProvider, EmailPayload
from email_service.config import email_settings
import logging

logger = logging.getLogger(__name__)


class SMTPProvider(EmailProvider):
    """SMTP email provider"""
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: bool = True,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ):
        self.host = host or email_settings.SMTP_HOST
        self.port = port or email_settings.SMTP_PORT
        self.user = user or email_settings.SMTP_USER
        self.password = password or email_settings.SMTP_PASSWORD
        self.use_tls = use_tls
        self.from_email = from_email or email_settings.SMTP_FROM_EMAIL
        self.from_name = from_name or email_settings.SMTP_FROM_NAME
    
    def _create_message(self, payload: EmailPayload) -> MIMEMultipart:
        """Create MIME message"""
        msg = MIMEMultipart('alternative')
        
        # Set headers
        from_email = payload.from_email or self.from_email
        from_name = payload.from_name or self.from_name
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = ', '.join(payload.to)
        msg['Subject'] = payload.subject
        
        if payload.cc:
            msg['Cc'] = ', '.join(payload.cc)
        
        if payload.reply_to:
            msg['Reply-To'] = payload.reply_to
        
        # Add text body if provided
        if payload.text_body:
            text_part = MIMEText(payload.text_body, 'plain', 'utf-8')
            msg.attach(text_part)
        
        # Add HTML body
        html_part = MIMEText(payload.html_body, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Add attachments
        if payload.attachments:
            for attachment in payload.attachments:
                self._add_attachment(msg, attachment)
        
        return msg
    
    def _add_attachment(self, msg: MIMEMultipart, attachment: dict):
        """Add attachment to message"""
        try:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.get('content', b''))
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f"attachment; filename={attachment.get('filename', 'attachment')}"
            )
            msg.attach(part)
        except Exception as e:
            logger.error(f"Failed to add attachment: {e}")
    
    def _get_recipients(self, payload: EmailPayload) -> List[str]:
        """Get all recipients"""
        recipients = list(payload.to)
        if payload.cc:
            recipients.extend(payload.cc)
        if payload.bcc:
            recipients.extend(payload.bcc)
        return recipients
    
    async def send(self, payload: EmailPayload) -> bool:
        """Send email via SMTP"""
        try:
            msg = self._create_message(payload)
            recipients = self._get_recipients(payload)
            
            # Run SMTP in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._send_sync, msg, recipients)
            
            logger.info(f"Email sent to {payload.to}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            raise
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            raise
    
    def _send_sync(self, msg: MIMEMultipart, recipients: List[str]):
        """Synchronous SMTP send"""
        with smtplib.SMTP(self.host, self.port) as server:
            if self.use_tls:
                server.starttls()
            
            if self.user and self.password:
                server.login(self.user, self.password)
            
            server.send_message(msg, to_addrs=recipients)
    
    async def send_bulk(self, payloads: List[EmailPayload]) -> List[bool]:
        """Send multiple emails"""
        results = []
        for payload in payloads:
            try:
                result = await self.send(payload)
                results.append(result)
            except:
                results.append(False)
        return results
    
    def health_check(self) -> bool:
        """Check SMTP connection"""
        try:
            with smtplib.SMTP(self.host, self.port, timeout=10) as server:
                if self.use_tls:
                    server.starttls()
                return True
        except Exception as e:
            logger.error(f"SMTP health check failed: {e}")
            return False
