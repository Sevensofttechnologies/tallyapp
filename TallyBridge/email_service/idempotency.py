"""
Idempotency handling for email messages
Prevents duplicate email sending using Redis or Database
"""

import redis
from typing import Optional
from datetime import datetime
from email_service.config import email_settings
from email_service.schemas import EmailStatus
import logging

logger = logging.getLogger(__name__)


class RedisIdempotencyStore:
    """Redis-based idempotency store"""
    
    def __init__(self):
        self.client = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis"""
        try:
            self.client = redis.Redis(
                host=email_settings.REDIS_HOST,
                port=email_settings.REDIS_PORT,
                db=email_settings.REDIS_DB,
                password=email_settings.REDIS_PASSWORD,
                decode_responses=True
            )
            self.client.ping()
            logger.info("Connected to Redis for idempotency")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory fallback.")
            self.client = None
    
    def _get_key(self, message_id: str) -> str:
        """Generate Redis key"""
        return f"email:idempotency:{message_id}"
    
    def check_and_set(self, message_id: str) -> bool:
        """
        Check if message was already processed.
        Returns True if this is a NEW message (not duplicate)
        Returns False if this is a DUPLICATE message
        """
        if not self.client:
            return True  # Allow processing if Redis unavailable
        
        try:
            key = self._get_key(message_id)
            # SETNX returns True if key was set (new message)
            result = self.client.setnx(key, EmailStatus.PROCESSING.value)
            if result:
                # Set TTL
                self.client.expire(key, email_settings.IDEMPOTENCY_TTL)
            return result
        except Exception as e:
            logger.error(f"Idempotency check failed: {e}")
            return True  # Allow processing on error
    
    def update_status(self, message_id: str, status: EmailStatus):
        """Update message status"""
        if not self.client:
            return
        
        try:
            key = self._get_key(message_id)
            self.client.setex(key, email_settings.IDEMPOTENCY_TTL, status.value)
        except Exception as e:
            logger.error(f"Status update failed: {e}")
    
    def get_status(self, message_id: str) -> Optional[str]:
        """Get message status"""
        if not self.client:
            return None
        
        try:
            key = self._get_key(message_id)
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Status get failed: {e}")
            return None
    
    def is_duplicate(self, message_id: str) -> bool:
        """Check if message is duplicate"""
        return not self.check_and_set(message_id)


class InMemoryIdempotencyStore:
    """In-memory fallback idempotency store"""
    
    def __init__(self):
        self._store = {}
    
    def check_and_set(self, message_id: str) -> bool:
        """Check and set message"""
        if message_id in self._store:
            return False
        self._store[message_id] = {
            "status": EmailStatus.PROCESSING.value,
            "created_at": datetime.utcnow()
        }
        return True
    
    def update_status(self, message_id: str, status: EmailStatus):
        """Update status"""
        if message_id in self._store:
            self._store[message_id]["status"] = status.value
    
    def get_status(self, message_id: str) -> Optional[str]:
        """Get status"""
        if message_id in self._store:
            return self._store[message_id]["status"]
        return None
    
    def is_duplicate(self, message_id: str) -> bool:
        """Check duplicate"""
        return not self.check_and_set(message_id)


# Create store instance
def get_idempotency_store():
    """Get idempotency store instance"""
    try:
        store = RedisIdempotencyStore()
        if store.client:
            return store
    except:
        pass
    logger.warning("Using in-memory idempotency store")
    return InMemoryIdempotencyStore()


idempotency_store = get_idempotency_store()
