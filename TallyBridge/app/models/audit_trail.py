"""
Audit Trail Model
Tracks all important changes and activities in the system
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class AuditTrail(Base):
    __tablename__ = "audit_trails"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    user_email = Column(String(255), nullable=True, index=True)
    
    action = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)
    resource_id = Column(Integer, nullable=True, index=True)
    
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    status = Column(String(20), default="SUCCESS", nullable=False, index=True)
    message = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)
    
    user = relationship("User", backref="audit_trails")
    
    __table_args__ = (
        Index('idx_audit_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_action_timestamp', 'action', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<AuditTrail(id={self.id}, action='{self.action}', resource='{self.resource_type}')>"
