"""
Email Providers Package
Pluggable email delivery providers
"""

from email_service.providers.base import EmailProvider
from email_service.providers.smtp_provider import SMTPProvider

__all__ = ["EmailProvider", "SMTPProvider"]
