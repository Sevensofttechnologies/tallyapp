"""
RabbitMQ Email Consumer
Main consumer that processes email messages from queue
"""

import json
import asyncio
import pika
from pika.adapters.asyncio_connection import AsyncioConnection
from typing import Optional, Callable
from email_service.config import email_settings
from email_service.schemas import EmailMessage, EmailStatus, ProcessingResult
from email_service.idempotency import idempotency_store
from email_service.encryption import decrypt_payload
from email_service.template_renderer import render_email
from email_service.providers.smtp_provider import SMTPProvider
from email_service.providers.base import EmailPayload
from email_service.metrics import metrics
import logging

logger = logging.getLogger(__name__)


class EmailError(Exception):
    """Base email error"""
    pass


class RetryableError(EmailError):
    """Error that should trigger retry"""
    pass


class NonRetryableError(EmailError):
    """Error that should go to DLQ"""
    pass


class EmailConsumer:
    """RabbitMQ consumer for email processing"""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.email_provider = SMTPProvider()
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup structured logging"""
        logging.basicConfig(
            level=getattr(logging, email_settings.LOG_LEVEL),
            format='{"timestamp":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}'
        )
    
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
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
    
    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            params = self._get_connection_params()
            self.connection = pika.BlockingConnection(params)
            self.channel = self.connection.channel()
            self.channel.basic_qos(prefetch_count=email_settings.RABBITMQ_PREFETCH_COUNT)
            logger.info("Connected to RabbitMQ")
            self._setup_exchanges_and_queues()
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    def _setup_exchanges_and_queues(self):
        """Setup all exchanges and queues"""
        # Declare exchanges
        self.channel.exchange_declare(
            exchange=email_settings.EMAIL_EXCHANGE,
            exchange_type='topic',
            durable=True
        )
        self.channel.exchange_declare(
            exchange=email_settings.EMAIL_RETRY_EXCHANGE,
            exchange_type='direct',
            durable=True
        )
        self.channel.exchange_declare(
            exchange=email_settings.EMAIL_DLX,
            exchange_type='direct',
            durable=True
        )
        
        # Declare main queue with DLX
        self.channel.queue_declare(
            queue=email_settings.EMAIL_QUEUE,
            durable=True,
            arguments={
                'x-dead-letter-exchange': email_settings.EMAIL_DLX,
                'x-dead-letter-routing-key': 'dlq'
            }
        )
        
        # Declare retry queues with TTL
        retry_configs = [
            (email_settings.EMAIL_RETRY_30S_QUEUE, 30000),
            (email_settings.EMAIL_RETRY_2M_QUEUE, 120000),
            (email_settings.EMAIL_RETRY_5M_QUEUE, 300000),
        ]
        
        for queue_name, ttl in retry_configs:
            self.channel.queue_declare(
                queue=queue_name,
                durable=True,
                arguments={
                    'x-message-ttl': ttl,
                    'x-dead-letter-exchange': email_settings.EMAIL_EXCHANGE,
                    'x-dead-letter-routing-key': 'email.send'
                }
            )
        
        # Declare DLQ
        self.channel.queue_declare(
            queue=email_settings.EMAIL_DLQ,
            durable=True
        )
        
        # Bind queues
        self.channel.queue_bind(
            queue=email_settings.EMAIL_QUEUE,
            exchange=email_settings.EMAIL_EXCHANGE,
            routing_key='email.#'
        )
        self.channel.queue_bind(
            queue=email_settings.EMAIL_DLQ,
            exchange=email_settings.EMAIL_DLX,
            routing_key='dlq'
        )
        
        logger.info("Exchanges and queues setup complete")
    
    def _parse_message(self, body: bytes) -> EmailMessage:
        """Parse and validate message"""
        try:
            data = json.loads(body.decode('utf-8'))
            return EmailMessage(**data)
        except json.JSONDecodeError as e:
            raise NonRetryableError(f"Invalid JSON: {e}")
        except Exception as e:
            raise NonRetryableError(f"Message validation failed: {e}")
    
    def _get_payload(self, message: EmailMessage) -> dict:
        """Get decrypted payload from message"""
        if message.payload_encrypted:
            try:
                return decrypt_payload(message.payload_encrypted)
            except Exception as e:
                raise NonRetryableError(f"Decryption failed: {e}")
        elif message.payload:
            return message.payload
        return {}
    
    async def _send_email(self, message: EmailMessage, payload: dict) -> bool:
        """Render template and send email"""
        try:
            # Render template
            html_body = render_email(message.template, payload)
            
            # Create email payload
            email_payload = EmailPayload(
                to=message.to,
                cc=message.cc,
                bcc=message.bcc,
                subject=message.subject,
                html_body=html_body
            )
            
            # Send via provider
            return await self.email_provider.send(email_payload)
            
        except FileNotFoundError:
            raise NonRetryableError(f"Template not found: {message.template}")
        except Exception as e:
            # Check if retryable
            error_str = str(e).lower()
            if any(x in error_str for x in ['timeout', 'connection', 'temporary', 'rate limit']):
                raise RetryableError(str(e))
            raise NonRetryableError(str(e))
    
    def _route_to_retry(self, message: EmailMessage, channel, method):
        """Route message to appropriate retry queue"""
        retry_count = message.retry_count
        
        if retry_count >= email_settings.MAX_RETRY_COUNT:
            # Max retries exceeded, send to DLQ
            self._route_to_dlq(message, channel, method, "Max retries exceeded")
            return
        
        # Select retry queue based on count
        retry_queues = [
            email_settings.EMAIL_RETRY_30S_QUEUE,
            email_settings.EMAIL_RETRY_2M_QUEUE,
            email_settings.EMAIL_RETRY_5M_QUEUE,
        ]
        retry_queue = retry_queues[min(retry_count, len(retry_queues) - 1)]
        
        # Update retry count
        message.retry_count += 1
        
        # Publish to retry queue
        channel.basic_publish(
            exchange='',
            routing_key=retry_queue,
            body=message.model_dump_json(),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type='application/json'
            )
        )
        
        # ACK original message
        channel.basic_ack(delivery_tag=method.delivery_tag)
        metrics.increment('email_retry_total')
        logger.info(f"Message {message.message_id} routed to retry queue {retry_queue}")
    
    def _route_to_dlq(self, message: EmailMessage, channel, method, reason: str):
        """Route message to DLQ"""
        # Add error info to message
        dlq_data = message.model_dump()
        dlq_data['dlq_reason'] = reason
        
        channel.basic_publish(
            exchange=email_settings.EMAIL_DLX,
            routing_key='dlq',
            body=json.dumps(dlq_data),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type='application/json'
            )
        )
        
        channel.basic_ack(delivery_tag=method.delivery_tag)
        idempotency_store.update_status(message.message_id, EmailStatus.DLQ)
        metrics.increment('email_failed_total')
        logger.error(f"Message {message.message_id} sent to DLQ: {reason}")
    
    def _process_message(self, channel, method, properties, body):
        """Process a single message"""
        message = None
        
        try:
            metrics.increment('email_received_total')
            
            # Parse message
            message = self._parse_message(body)
            logger.info(f"Processing message: {message.message_id}")
            
            # Check idempotency
            if idempotency_store.is_duplicate(message.message_id):
                logger.info(f"Duplicate message ignored: {message.message_id}")
                channel.basic_ack(delivery_tag=method.delivery_tag)
                return
            
            # Get payload
            payload = self._get_payload(message)
            
            # Send email (run async in sync context)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self._send_email(message, payload))
            finally:
                loop.close()
            
            # Success
            channel.basic_ack(delivery_tag=method.delivery_tag)
            idempotency_store.update_status(message.message_id, EmailStatus.SENT)
            metrics.increment('email_sent_total')
            logger.info(f"Email sent successfully: {message.message_id}")
            
        except RetryableError as e:
            logger.warning(f"Retryable error for {message.message_id if message else 'unknown'}: {e}")
            if message:
                self._route_to_retry(message, channel, method)
            else:
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                
        except NonRetryableError as e:
            logger.error(f"Non-retryable error: {e}")
            if message:
                self._route_to_dlq(message, channel, method, str(e))
            else:
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            if message:
                self._route_to_dlq(message, channel, method, f"Unexpected: {e}")
            else:
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def start_consuming(self):
        """Start consuming messages"""
        if not self.channel:
            self.connect()
        
        self.channel.basic_consume(
            queue=email_settings.EMAIL_QUEUE,
            on_message_callback=self._process_message,
            auto_ack=False
        )
        
        logger.info(f"Started consuming from {email_settings.EMAIL_QUEUE}")
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Consumer stopped by user")
            self.stop()
    
    def stop(self):
        """Stop consumer and close connection"""
        if self.channel:
            self.channel.stop_consuming()
        if self.connection:
            self.connection.close()
        logger.info("Consumer stopped")


def run_consumer():
    """Run the email consumer"""
    consumer = EmailConsumer()
    consumer.start_consuming()


if __name__ == "__main__":
    run_consumer()
