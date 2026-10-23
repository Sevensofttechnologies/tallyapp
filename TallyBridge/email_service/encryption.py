"""
Encryption/Decryption utilities for email payloads
AES-256-GCM encryption
"""

import base64
import json
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from typing import Dict, Any, Optional
from email_service.config import email_settings
import logging

logger = logging.getLogger(__name__)


class PayloadEncryption:
    """AES-256-GCM encryption for email payloads"""
    
    def __init__(self, key: Optional[str] = None):
        """Initialize with encryption key"""
        key_str = key or email_settings.ENCRYPTION_KEY
        # Ensure key is 32 bytes for AES-256
        self.key = self._normalize_key(key_str)
        self.aesgcm = AESGCM(self.key)
    
    def _normalize_key(self, key_str: str) -> bytes:
        """Normalize key to 32 bytes"""
        key_bytes = key_str.encode('utf-8')
        if len(key_bytes) < 32:
            key_bytes = key_bytes.ljust(32, b'\0')
        elif len(key_bytes) > 32:
            key_bytes = key_bytes[:32]
        return key_bytes
    
    def encrypt(self, payload: Dict[str, Any]) -> str:
        """
        Encrypt payload dictionary to base64 string
        Returns: Base64 encoded string (nonce + ciphertext)
        """
        try:
            # Convert payload to JSON bytes
            plaintext = json.dumps(payload).encode('utf-8')
            
            # Generate random 12-byte nonce
            nonce = os.urandom(12)
            
            # Encrypt
            ciphertext = self.aesgcm.encrypt(nonce, plaintext, None)
            
            # Combine nonce + ciphertext and encode to base64
            encrypted_data = nonce + ciphertext
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, encrypted_payload: str) -> Dict[str, Any]:
        """
        Decrypt base64 string to payload dictionary
        """
        try:
            # Decode from base64
            encrypted_data = base64.b64decode(encrypted_payload)
            
            # Extract nonce (first 12 bytes) and ciphertext
            nonce = encrypted_data[:12]
            ciphertext = encrypted_data[12:]
            
            # Decrypt
            plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
            
            # Parse JSON
            return json.loads(plaintext.decode('utf-8'))
            
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise


# Global instance
payload_encryption = PayloadEncryption()


def encrypt_payload(payload: Dict[str, Any]) -> str:
    """Encrypt payload helper function"""
    return payload_encryption.encrypt(payload)


def decrypt_payload(encrypted_payload: str) -> Dict[str, Any]:
    """Decrypt payload helper function"""
    return payload_encryption.decrypt(encrypted_payload)
