"""
Base Email Provider Interface
Abstract base class for all email providers
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from dataclasses import dataclass


@dataclass
class EmailPayload:
    """Email payload for sending"""
    to: List[str]
    subject: str
    html_body: str
    text_body: Optional[str] = None
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    from_email: Optional[str] = None
    from_name: Optional[str] = None
    reply_to: Optional[str] = None
    attachments: Optional[List[Dict]] = None


class EmailProvider(ABC):
    """Abstract base class for email providers"""
    
    @abstractmethod
    async def send(self, payload: EmailPayload) -> bool:
        """
        Send email
        
        Args:
            payload: EmailPayload object
            
        Returns:
            True if sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def send_bulk(self, payloads: List[EmailPayload]) -> List[bool]:
        """
        Send multiple emails
        
        Args:
            payloads: List of EmailPayload objects
            
        Returns:
            List of success/failure booleans
        """
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Check if provider is healthy"""
        pass
