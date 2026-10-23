"""Crypto Utilities

AES-256-GCM encryption/decryption helpers.
Used for encrypting sensitive fields like SMTP password stored in DB.
"""

import base64
import os
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.config import settings


def _normalize_key(key_str: str) -> bytes:
    key_bytes = (key_str or "").encode("utf-8")
    if len(key_bytes) < 32:
        key_bytes = key_bytes.ljust(32, b"\0")
    elif len(key_bytes) > 32:
        key_bytes = key_bytes[:32]
    return key_bytes


def encrypt_text(plain_text: Optional[str], key: Optional[str] = None) -> Optional[str]:
    if plain_text is None:
        return None

    key_str = key or settings.EMAIL_SETTINGS_ENCRYPTION_KEY
    aesgcm = AESGCM(_normalize_key(key_str))

    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plain_text.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("utf-8")


def decrypt_text(encrypted_text: Optional[str], key: Optional[str] = None) -> Optional[str]:
    if encrypted_text is None:
        return None

    key_str = key or settings.EMAIL_SETTINGS_ENCRYPTION_KEY
    aesgcm = AESGCM(_normalize_key(key_str))

    encrypted_data = base64.b64decode(encrypted_text)
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]

    plain = aesgcm.decrypt(nonce, ciphertext, None)
    return plain.decode("utf-8")
