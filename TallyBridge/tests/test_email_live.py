"""
Live Email Testing Script
Tests email sending to Yopmail using RabbitMQ + SMTP
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime

# Test Configuration
YOPMAIL_ADDRESS = "starterkit-test@yopmail.com"  # Check at https://yopmail.com/starterkit-test


def test_direct_smtp():
    """Test 1: Direct SMTP send (without RabbitMQ)"""
    print("\n" + "="*60)
    print("TEST 1: Direct SMTP Email Send")
    print("="*60)
    
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email_service.config import email_settings
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{email_settings.SMTP_FROM_NAME} <{email_settings.SMTP_FROM_EMAIL}>"
        msg['To'] = YOPMAIL_ADDRESS
        msg['Subject'] = f"Test Email - Direct SMTP - {datetime.now().strftime('%H:%M:%S')}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #667eea;">Direct SMTP Test</h2>
            <p>This email was sent directly via SMTP.</p>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>From:</strong> {email_settings.SMTP_FROM_EMAIL}</p>
            <hr>
            <p style="color: #666; font-size: 12px;">Application Starter Kit - Email Test</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        
        # Send via SMTP
        print(f"Connecting to {email_settings.SMTP_HOST}:{email_settings.SMTP_PORT}...")
        
        with smtplib.SMTP(email_settings.SMTP_HOST, email_settings.SMTP_PORT, timeout=30) as server:
            server.set_debuglevel(1)  # Show SMTP conversation
            
            if email_settings.SMTP_USE_TLS:
                print("Starting TLS...")
                server.starttls()
            
            print(f"Logging in as {email_settings.SMTP_USER}...")
            server.login(email_settings.SMTP_USER, email_settings.SMTP_PASSWORD)
            
            print(f"Sending email to {YOPMAIL_ADDRESS}...")
            server.send_message(msg)
        
        print("\n[PASS] Direct SMTP email sent successfully!")
        print(f"Check: https://yopmail.com/starterkit-test")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n[FAIL] SMTP Authentication Error: {e}")
        print("Check your SMTP_USER and SMTP_PASSWORD in .env")
        return False
    except smtplib.SMTPException as e:
        print(f"\n[FAIL] SMTP Error: {e}")
        return False
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        return False


def test_rabbitmq_connection():
    """Test 2: RabbitMQ Connection"""
    print("\n" + "="*60)
    print("TEST 2: RabbitMQ Connection")
    print("="*60)
    
    try:
        import pika
        from email_service.config import email_settings
        
        credentials = pika.PlainCredentials(
            email_settings.RABBITMQ_USER,
            email_settings.RABBITMQ_PASSWORD
        )
        params = pika.ConnectionParameters(
            host=email_settings.RABBITMQ_HOST,
            port=email_settings.RABBITMQ_PORT,
            virtual_host=email_settings.RABBITMQ_VHOST,
            credentials=credentials
        )
        
        print(f"Connecting to RabbitMQ at {email_settings.RABBITMQ_HOST}:{email_settings.RABBITMQ_PORT}...")
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        
        print("[PASS] RabbitMQ connection successful!")
        connection.close()
        return True
        
    except Exception as e:
        print(f"[FAIL] RabbitMQ connection failed: {e}")
        print("\nMake sure RabbitMQ is running:")
        print("  docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management")
        return False


def test_redis_connection():
    """Test 3: Redis Connection"""
    print("\n" + "="*60)
    print("TEST 3: Redis Connection")
    print("="*60)
    
    try:
        import redis
        from email_service.config import email_settings
        
        print(f"Connecting to Redis at {email_settings.REDIS_HOST}:{email_settings.REDIS_PORT}...")
        
        client = redis.Redis(
            host=email_settings.REDIS_HOST,
            port=email_settings.REDIS_PORT,
            db=email_settings.REDIS_DB,
            password=email_settings.REDIS_PASSWORD
        )
        
        client.ping()
        print("[PASS] Redis connection successful!")
        return True
        
    except Exception as e:
        print(f"[WARN] Redis connection failed: {e}")
        print("Email service will use in-memory idempotency (OK for testing)")
        return False


def test_email_via_publisher():
    """Test 4: Send email via RabbitMQ Publisher"""
    print("\n" + "="*60)
    print("TEST 4: Email via RabbitMQ Publisher")
    print("="*60)
    
    try:
        from email_service.publisher import email_publisher
        
        print("Publishing email message to RabbitMQ...")
        
        message_id = email_publisher.publish(
            to=[YOPMAIL_ADDRESS],
            subject=f"RabbitMQ Test - {datetime.now().strftime('%H:%M:%S')}",
            template="welcome.html",
            payload={
                "user_name": "Test User",
                "login_url": "https://example.com/login"
            },
            source_service="test-script",
            encrypt=False  # Don't encrypt for easier debugging
        )
        
        print(f"[PASS] Message published! ID: {message_id}")
        print("\nNow start the consumer to process this message:")
        print("  python -m email_service.run_consumer")
        return True
        
    except Exception as e:
        print(f"[FAIL] Publisher error: {e}")
        return False


def test_encryption():
    """Test 5: Encryption/Decryption"""
    print("\n" + "="*60)
    print("TEST 5: Payload Encryption")
    print("="*60)
    
    try:
        from email_service.encryption import encrypt_payload, decrypt_payload
        
        original = {"user_name": "Test", "email": "test@example.com"}
        print(f"Original: {original}")
        
        encrypted = encrypt_payload(original)
        print(f"Encrypted: {encrypted[:50]}...")
        
        decrypted = decrypt_payload(encrypted)
        print(f"Decrypted: {decrypted}")
        
        if original == decrypted:
            print("[PASS] Encryption/Decryption working!")
            return True
        else:
            print("[FAIL] Decrypted data doesn't match!")
            return False
            
    except Exception as e:
        print(f"[FAIL] Encryption error: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("EMAIL MICROSERVICE - LIVE TESTING")
    print(f"Target: {YOPMAIL_ADDRESS}")
    print(f"Check inbox: https://yopmail.com/starterkit-test")
    print("="*60)
    
    results = []
    
    # Test 1: Direct SMTP
    results.append(("Direct SMTP", test_direct_smtp()))
    
    # Test 2: RabbitMQ
    results.append(("RabbitMQ Connection", test_rabbitmq_connection()))
    
    # Test 3: Redis
    results.append(("Redis Connection", test_redis_connection()))
    
    # Test 4: Encryption
    results.append(("Encryption", test_encryption()))
    
    # Test 5: Publisher (only if RabbitMQ works)
    if results[1][1]:  # RabbitMQ passed
        results.append(("Email Publisher", test_email_via_publisher()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {name}")
    
    print(f"\nTotal: {passed}/{total} passed")
    print("="*60)
    
    if results[0][1]:  # Direct SMTP passed
        print(f"\nCheck Yopmail inbox: https://yopmail.com/starterkit-test")


if __name__ == "__main__":
    # Check if only direct SMTP test requested
    if len(sys.argv) > 1 and sys.argv[1] == "--smtp-only":
        test_direct_smtp()
    else:
        run_all_tests()
