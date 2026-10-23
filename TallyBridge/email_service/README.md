# Email Microservice

RabbitMQ-based Email Consumer Service for Application Starter Kit.

## Architecture

```
┌─────────────────┐     ┌───────────────┐     ┌──────────────────┐     ┌────────────────┐
│  Main App       │────▶│   RabbitMQ    │────▶│ Email Consumer   │────▶│ Email Provider │
│  (Publisher)    │     │   (Broker)    │     │ (This Service)   │     │ (SMTP/SES)     │
└─────────────────┘     └───────────────┘     └──────────────────┘     └────────────────┘
```

## Features

- **Consumer-Only Architecture** - No exposed APIs
- **Retry Mechanism** - 3 retries with exponential backoff (30s, 2m, 5m)
- **Dead Letter Queue** - Failed messages preserved for investigation
- **Idempotency** - Duplicate message prevention via Redis
- **Encrypted Payloads** - AES-256-GCM encryption
- **Template Rendering** - Jinja2 HTML templates
- **Pluggable Providers** - SMTP, SES, SendGrid support
- **Structured Logging** - JSON formatted logs
- **Metrics** - Counter-based monitoring

## Quick Start

### 1. Install Dependencies

```bash
pip install pika redis jinja2 cryptography
```

### 2. Start RabbitMQ

```bash
# Using Docker
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
```

### 3. Configure Environment

```bash
# .env file
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@example.com

REDIS_HOST=localhost
REDIS_PORT=6379

ENCRYPTION_KEY=your-32-byte-encryption-key-here
```

### 4. Run Consumer

```bash
python -m email_service.run_consumer
```

## Usage in Main Application

### Send Email from Starter Kit

```python
from email_service.publisher import email_publisher, send_welcome_email

# Method 1: Using helper functions
send_welcome_email(
    to="user@example.com",
    user_name="John Doe",
    login_url="https://app.example.com/login"
)

# Method 2: Using publisher directly
email_publisher.publish(
    to=["user@example.com"],
    subject="Custom Email",
    template="notification.html",
    payload={
        "user_name": "John",
        "message": "Your order has been shipped!"
    }
)

# Method 3: Send password reset
from email_service.publisher import send_password_reset_email

send_password_reset_email(
    to="user@example.com",
    reset_link="https://app.example.com/reset?token=abc123",
    user_name="John Doe"
)
```

## Message Format

```json
{
  "message_id": "uuid",
  "event_type": "EMAIL_SEND",
  "to": ["user@example.com"],
  "subject": "Welcome",
  "template": "welcome.html",
  "payload_encrypted": "BASE64_STRING",
  "encryption": {
    "alg": "AES-256-GCM",
    "key_id": "email-key-v1"
  },
  "metadata": {
    "source_service": "starter-kit",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

## Queues

| Queue | Purpose |
|-------|---------|
| email.queue | Main processing queue |
| email.retry.30s.queue | Retry after 30 seconds |
| email.retry.2m.queue | Retry after 2 minutes |
| email.retry.5m.queue | Retry after 5 minutes |
| email.dlq | Dead letter queue |

## Templates

Templates are stored in `email_service/templates/`:

- `base.html` - Base template with styling
- `welcome.html` - Welcome email
- `password_reset.html` - Password reset
- `verification.html` - Email verification
- `notification.html` - General notifications

### Creating Custom Templates

```html
{% extends "base.html" %}

{% block title %}My Email{% endblock %}

{% block content %}
<h2>Hello {{ user_name }}!</h2>
<p>{{ message }}</p>
{% endblock %}
```

## Error Handling

| Error Type | Action |
|------------|--------|
| SMTP Timeout | Retry |
| Network Error | Retry |
| Rate Limit | Retry |
| Invalid Schema | DLQ |
| Template Missing | DLQ |
| Auth Error | DLQ |
| Duplicate | ACK + Ignore |

## Monitoring

### Metrics Available

```python
from email_service.metrics import metrics

stats = metrics.get_stats()
# {
#   'total_received': 100,
#   'total_sent': 95,
#   'total_failed': 3,
#   'total_retries': 5,
#   'success_rate_percent': 95.0
# }
```

## File Structure

```
email_service/
├── __init__.py
├── config.py           # Configuration
├── schemas.py          # Pydantic schemas
├── consumer.py         # RabbitMQ consumer
├── publisher.py        # Message publisher
├── encryption.py       # AES-256-GCM encryption
├── idempotency.py      # Duplicate prevention
├── template_renderer.py # Jinja2 rendering
├── metrics.py          # Metrics collection
├── run_consumer.py     # Consumer runner
├── providers/
│   ├── __init__.py
│   ├── base.py         # Provider interface
│   └── smtp_provider.py # SMTP implementation
└── templates/
    ├── base.html
    ├── welcome.html
    ├── password_reset.html
    ├── verification.html
    └── notification.html
```

## Production Considerations

1. **Use Redis** for idempotency in production
2. **Configure proper SMTP** credentials
3. **Set strong encryption key** (32 bytes)
4. **Monitor DLQ** for failed messages
5. **Scale consumers** horizontally as needed
6. **Use separate vhost** per environment
