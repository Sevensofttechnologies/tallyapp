"""
Test All Email Templates
Sends all email types to Yopmail for verification
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from email_service.config import email_settings
from email_service.template_renderer import render_email

# Test email address
TEST_EMAIL = "ganesha@yopmail.com"
USER_NAME = "Ganesha"


def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """Send email via SMTP"""
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


def test_welcome_email():
    """Test 1: Welcome Email"""
    print("\n[1/10] Welcome Email")
    html = render_email("welcome.html", {
        "user_name": USER_NAME,
        "login_url": "https://app.example.com/login"
    })
    return send_email(TEST_EMAIL, f"Welcome to Application Starter Kit! - {datetime.now().strftime('%H:%M')}", html)


def test_otp_email():
    """Test 2: OTP Email"""
    print("\n[2/10] OTP Verification Email")
    html = render_email("otp.html", {
        "user_name": USER_NAME,
        "otp_code": "847291",
        "expiry_minutes": "10"
    })
    return send_email(TEST_EMAIL, f"Your OTP Code: 847291 - {datetime.now().strftime('%H:%M')}", html)


def test_verification_email():
    """Test 3: Email Verification"""
    print("\n[3/10] Email Verification")
    html = render_email("verification.html", {
        "user_name": USER_NAME,
        "verification_link": "https://app.example.com/verify?token=abc123xyz"
    })
    return send_email(TEST_EMAIL, f"Verify Your Email - {datetime.now().strftime('%H:%M')}", html)


def test_password_reset_email():
    """Test 4: Password Reset"""
    print("\n[4/10] Password Reset Email")
    html = render_email("password_reset.html", {
        "user_name": USER_NAME,
        "reset_link": "https://app.example.com/reset?token=reset123"
    })
    return send_email(TEST_EMAIL, f"Reset Your Password - {datetime.now().strftime('%H:%M')}", html)


def test_password_changed_email():
    """Test 5: Password Changed Notification"""
    print("\n[5/10] Password Changed Notification")
    html = render_email("password_changed.html", {
        "user_name": USER_NAME,
        "changed_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "ip_address": "192.168.1.100",
        "device": "Chrome on Windows",
        "reset_link": "https://app.example.com/reset"
    })
    return send_email(TEST_EMAIL, f"Your Password Was Changed - {datetime.now().strftime('%H:%M')}", html)


def test_login_alert_email():
    """Test 6: New Login Alert"""
    print("\n[6/10] New Login Alert")
    html = render_email("login_alert.html", {
        "user_name": USER_NAME,
        "login_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "ip_address": "103.45.67.89",
        "location": "Mumbai, India",
        "device": "Windows PC",
        "browser": "Chrome 120",
        "secure_account_link": "https://app.example.com/security"
    })
    return send_email(TEST_EMAIL, f"New Login to Your Account - {datetime.now().strftime('%H:%M')}", html)


def test_account_deactivated_email():
    """Test 7: Account Deactivated"""
    print("\n[7/10] Account Deactivated")
    html = render_email("account_deactivated.html", {
        "user_name": USER_NAME,
        "deactivated_at": datetime.now().strftime('%Y-%m-%d'),
        "reason": "Account deactivated at user request",
        "support_email": "support@vrushaliinfotech.com"
    })
    return send_email(TEST_EMAIL, f"Your Account Has Been Deactivated - {datetime.now().strftime('%H:%M')}", html)


def test_company_invitation_email():
    """Test 8: Company Invitation"""
    print("\n[8/10] Company Invitation")
    html = render_email("company_invitation.html", {
        "user_name": USER_NAME,
        "company_name": "Vrushali Infotech Pvt Ltd",
        "role": "Manager",
        "invited_by": "Admin User",
        "invitation_link": "https://app.example.com/invite/accept?token=inv123",
        "expiry_days": "7"
    })
    return send_email(TEST_EMAIL, f"You're Invited to Join Vrushali Infotech! - {datetime.now().strftime('%H:%M')}", html)


def test_role_changed_email():
    """Test 9: Role Changed"""
    print("\n[9/10] Role Changed Notification")
    html = render_email("role_changed.html", {
        "user_name": USER_NAME,
        "company_name": "Vrushali Infotech Pvt Ltd",
        "old_role": "User",
        "new_role": "Admin",
        "changed_by": "Super Admin",
        "changed_at": datetime.now().strftime('%Y-%m-%d'),
        "new_permissions": ["Manage Users", "View Reports", "Edit Settings"],
        "dashboard_link": "https://app.example.com/dashboard"
    })
    return send_email(TEST_EMAIL, f"Your Role Has Been Updated - {datetime.now().strftime('%H:%M')}", html)


def test_account_reactivated_email():
    """Test 10: Account Reactivated"""
    print("\n[10/10] Account Reactivated")
    html = render_email("account_reactivated.html", {
        "user_name": USER_NAME,
        "login_link": "https://app.example.com/login"
    })
    return send_email(TEST_EMAIL, f"Welcome Back! Your Account is Active - {datetime.now().strftime('%H:%M')}", html)


def test_notification_email():
    """Bonus: General Notification"""
    print("\n[Bonus] General Notification")
    html = render_email("notification.html", {
        "user_name": USER_NAME,
        "title": "Important Update",
        "message": "Your subscription will expire in 7 days. Please renew to continue using all features.",
        "details": {
            "Plan": "Premium",
            "Expiry Date": "2026-01-17",
            "Amount Due": "Rs. 999"
        },
        "action_url": "https://app.example.com/billing",
        "action_text": "Renew Now"
    })
    return send_email(TEST_EMAIL, f"Important: Subscription Expiring Soon - {datetime.now().strftime('%H:%M')}", html)


def run_all_tests():
    """Run all email tests"""
    print("=" * 60)
    print("EMAIL MICROSERVICE - ALL TEMPLATES TEST")
    print("=" * 60)
    print(f"Sending to: {TEST_EMAIL}")
    print(f"From: {email_settings.SMTP_FROM_EMAIL}")
    print("=" * 60)
    
    tests = [
        ("Welcome Email", test_welcome_email),
        ("OTP Verification", test_otp_email),
        ("Email Verification", test_verification_email),
        ("Password Reset", test_password_reset_email),
        ("Password Changed", test_password_changed_email),
        ("Login Alert", test_login_alert_email),
        ("Account Deactivated", test_account_deactivated_email),
        ("Company Invitation", test_company_invitation_email),
        ("Role Changed", test_role_changed_email),
        ("Account Reactivated", test_account_reactivated_email),
        ("General Notification", test_notification_email),
    ]
    
    results = []
    for name, test_func in tests:
        success = test_func()
        results.append((name, success))
        status = "[PASS]" if success else "[FAIL]"
        print(f"   {status}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    
    for name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"  {status} {name}")
    
    print(f"\nTotal: {passed}/{len(results)} emails sent")
    print("=" * 60)
    print(f"\nCheck inbox: https://yopmail.com/ganesha")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
