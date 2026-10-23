"""
Email Publisher
Helper to publish email messages to RabbitMQ from main application
This is used by the Starter Kit to send emails
"""

import json
import uuid
import pika
from typing import List, Dict, Any, Optional
from datetime import datetime
from email_service.config import email_settings
from email_service.schemas import EmailMessage, EventType, MessageMetadata, EncryptionInfo
from email_service.encryption import encrypt_payload
import logging

logger = logging.getLogger(__name__)


class EmailPublisher:
    """Publish email messages to RabbitMQ"""
    
    def __init__(self):
        self.connection = None
        self.channel = None
    
    def _get_connection_params(self) -> pika.ConnectionParameters:
        """Get RabbitMQ connection parameters"""
        credentials = pika.PlainCredentials(
            email_settings.RABBITMQ_USER,
            email_settings.RABBITMQ_PASSWORD
        )
        return pika.ConnectionParameters(
            host=email_settings.RABBITMQ_HOST,
            port=email_settings.RABBITMQ_PORT,
            virtual_host=email_settings.RABBITMQ_VHOST,
            credentials=credentials
        )
    
    def connect(self):
        """Connect to RabbitMQ"""
        if self.connection and self.connection.is_open:
            return
        
        try:
            params = self._get_connection_params()
            self.connection = pika.BlockingConnection(params)
            self.channel = self.connection.channel()
            
            # Ensure exchange exists
            self.channel.exchange_declare(
                exchange=email_settings.EMAIL_EXCHANGE,
                exchange_type='topic',
                durable=True
            )
            logger.info("Email publisher connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from RabbitMQ"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info("Email publisher disconnected")
    
    def publish(
        self,
        to: List[str],
        subject: str,
        template: str,
        payload: Dict[str, Any],
        event_type: EventType = EventType.EMAIL_SEND,
        source_service: str = "starter-kit",
        encrypt: bool = True,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> str:
        """
        Publish email message to RabbitMQ
        
        Args:
            to: List of recipient emails
            subject: Email subject
            template: Template filename
            payload: Template variables
            event_type: Type of email event
            source_service: Name of source service
            encrypt: Whether to encrypt payload
            cc: CC recipients
            bcc: BCC recipients
            
        Returns:
            message_id: Unique message ID
        """
        self.connect()
        
        message_id = str(uuid.uuid4())
        
        # Build message
        message_data = {
            "message_id": message_id,
            "event_type": event_type.value,
            "to": to,
            "subject": subject,
            "template": template,
            "metadata": {
                "source_service": source_service,
                "created_at": datetime.utcnow().isoformat()
            }
        }
        
        if cc:
            message_data["cc"] = cc
        if bcc:
            message_data["bcc"] = bcc
        
        # Encrypt or include plain payload
        if encrypt:
            message_data["payload_encrypted"] = encrypt_payload(payload)
            message_data["encryption"] = {
                "alg": "AES-256-GCM",
                "key_id": "email-key-v1"
            }
        else:
            message_data["payload"] = payload
        
        # Publish to RabbitMQ
        try:
            self.channel.basic_publish(
                exchange=email_settings.EMAIL_EXCHANGE,
                routing_key='email.send',
                body=json.dumps(message_data),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent
                    content_type='application/json',
                    message_id=message_id
                )
            )
            logger.info(f"Email message published: {message_id}")
            return message_id
        except Exception as e:
            logger.error(f"Failed to publish email: {e}")
            raise
    
    def send_welcome_email(self, to: str, user_name: str, **kwargs) -> str:
        """Send welcome email"""
        return self.publish(
            to=[to],
            subject="Welcome to Application Starter Kit!",
            template="welcome.html",
            payload={"user_name": user_name, **kwargs},
            event_type=EventType.EMAIL_WELCOME
        )
    
    def send_password_reset_email(self, to: str, reset_link: str, user_name: str = "User") -> str:
        """Send password reset email"""
        return self.publish(
            to=[to],
            subject="Password Reset Request",
            template="password_reset.html",
            payload={"user_name": user_name, "reset_link": reset_link},
            event_type=EventType.EMAIL_PASSWORD_RESET
        )
    
    def send_verification_email(self, to: str, verification_link: str, user_name: str = "User") -> str:
        """Send email verification"""
        return self.publish(
            to=[to],
            subject="Verify Your Email",
            template="verification.html",
            payload={"user_name": user_name, "verification_link": verification_link},
            event_type=EventType.EMAIL_VERIFICATION
        )
    
    def send_notification(self, to: List[str], subject: str, message: str, **kwargs) -> str:
        """Send notification email"""
        return self.publish(
            to=to,
            subject=subject,
            template="notification.html",
            payload={"message": message, **kwargs},
            event_type=EventType.EMAIL_NOTIFICATION
        )


# Global publisher instance
email_publisher = EmailPublisher()


# Convenience functions
def send_email(to: List[str], subject: str, template: str, payload: Dict[str, Any], **kwargs) -> str:
    """Send email helper function"""
    return email_publisher.publish(to, subject, template, payload, **kwargs)


def send_welcome_email(to: str, user_name: str, **kwargs) -> str:
    """Send welcome email helper"""
    return email_publisher.send_welcome_email(to, user_name, **kwargs)


def send_password_reset_email(to: str, reset_link: str, user_name: str = "User") -> str:
    """Send password reset email helper"""
    return email_publisher.send_password_reset_email(to, reset_link, user_name)
