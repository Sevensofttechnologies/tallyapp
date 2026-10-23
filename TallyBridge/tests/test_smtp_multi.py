"""
Direct SMTP Test - Multiple Yopmail Recipients
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from email_service.config import email_settings

# Multiple Yopmail addresses
YOPMAIL_ADDRESSES = [
    "ganesha@yopmail.com",
    "starterkit1@yopmail.com",
    "starterkit2@yopmail.com",
    "testuser123@yopmail.com",
]


def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """Send single email"""
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{email_settings.SMTP_FROM_NAME} <{email_settings.SMTP_FROM_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        
        with smtplib.SMTP(email_settings.SMTP_HOST, email_settings.SMTP_PORT, timeout=30) as server:
            if email_settings.SMTP_USE_TLS:
                server.starttls()
            server.login(email_settings.SMTP_USER, email_settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"   Error: {e}")
        return False


def create_welcome_email(user_name: str) -> str:
    """Create welcome email HTML"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #f4f4f4; }}
            .container {{ max-width: 600px; margin: 20px auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
            .content {{ padding: 30px; }}
            .button {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to Application Starter Kit!</h1>
            </div>
            <div class="content">
                <h2>Hello {user_name}!</h2>
                <p>Your account has been successfully created. We're excited to have you on board!</p>
                <p>This is a test email from the <strong>Email Microservice</strong>.</p>
                <ul>
                    <li>Sent via: SMTP</li>
                    <li>From: {email_settings.SMTP_FROM_EMAIL}</li>
                    <li>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                </ul>
                <p style="text-align: center;">
                    <a href="https://example.com/login" class="button">Go to Dashboard</a>
                </p>
            </div>
            <div class="footer">
                <p>Application Starter Kit - Email Microservice Test</p>
                <p>This is an automated test email.</p>
            </div>
        </div>
    </body>
    </html>
    """


def run_test():
    """Send emails to multiple Yopmail addresses"""
    print("=" * 60)
    print("EMAIL MICROSERVICE - MULTI-RECIPIENT TEST")
    print("=" * 60)
    print(f"SMTP Host: {email_settings.SMTP_HOST}")
    print(f"SMTP User: {email_settings.SMTP_USER}")
    print(f"From: {email_settings.SMTP_FROM_EMAIL}")
    print("=" * 60)
    
    results = []
    
    for i, email in enumerate(YOPMAIL_ADDRESSES, 1):
        user_name = email.split('@')[0].title()
        subject = f"Welcome {user_name}! - Test #{i} - {datetime.now().strftime('%H:%M:%S')}"
        html_body = create_welcome_email(user_name)
        
        print(f"\n[{i}/{len(YOPMAIL_ADDRESSES)}] Sending to: {email}")
        
        success = send_email(email, subject, html_body)
        results.append((email, success))
        
        if success:
            print(f"   [PASS] Email sent successfully!")
        else:
            print(f"   [FAIL] Email failed!")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    
    for email, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"  {status} {email}")
    
    print(f"\nTotal: {passed}/{len(results)} emails sent")
    print("=" * 60)
    
    print("\nCheck Yopmail inboxes:")
    for email, success in results:
        if success:
            inbox_name = email.split('@')[0]
            print(f"  https://yopmail.com/{inbox_name}")
    
    print("=" * 60)


if __name__ == "__main__":
    run_test()
