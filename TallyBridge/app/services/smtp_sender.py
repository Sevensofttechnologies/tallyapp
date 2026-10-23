import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional


def send_smtp_email(
    host: str,
    port: int,
    user: Optional[str],
    password: Optional[str],
    use_tls: bool,
    use_ssl: bool,
    from_email: str,
    from_name: Optional[str],
    reply_to: Optional[str],
    to: List[str],
    cc: Optional[List[str]],
    bcc: Optional[List[str]],
    subject: str,
    text_body: Optional[str],
    html_body: Optional[str],
) -> None:
    msg = MIMEMultipart('alternative')
    msg['From'] = f"{from_name} <{from_email}>" if from_name else from_email
    msg['To'] = ', '.join(to)
    msg['Subject'] = subject
    if cc:
        msg['Cc'] = ', '.join(cc)
    if reply_to:
        msg['Reply-To'] = reply_to

    if text_body:
        msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
    if html_body:
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
    if not text_body and not html_body:
        msg.attach(MIMEText('', 'plain', 'utf-8'))

    recipients = list(to)
    if cc:
        recipients.extend(cc)
    if bcc:
        recipients.extend(bcc)

    if use_ssl:
        server = smtplib.SMTP_SSL(host, port, timeout=30)
    else:
        server = smtplib.SMTP(host, port, timeout=30)

    try:
        server.ehlo()
        if use_tls and not use_ssl:
            server.starttls()
            server.ehlo()
        if user:
            server.login(user, password or '')
        server.sendmail(from_email, recipients, msg.as_string())
    finally:
        try:
            server.quit()
        except Exception:
            pass
