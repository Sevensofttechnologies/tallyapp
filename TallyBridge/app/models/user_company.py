"""
User-Company Relationship Model (Many-to-Many)
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class UserCompany(Base):
    """User-Company association table"""
    
    __tablename__ = "user_companies"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Role in this company
    role = Column(String(50), nullable=False)
    
    # Primary company flag
    is_primary = Column(Boolean, default=False, nullable=False)
    
    # Custom permissions (JSON)
    permissions = Column(JSON, nullable=True)
    
    # Timestamps
    joined_at = Column(DateTime, default=func.now(), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="companies")
    company = relationship("Company", back_populates="users")
    
    def __repr__(self):
        return f"<UserCompany user_id={self.user_id} company_id={self.company_id}>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "company_id": self.company_id,
            "role": self.role,
            "is_primary": self.is_primary,
            "permissions": self.permissions,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
