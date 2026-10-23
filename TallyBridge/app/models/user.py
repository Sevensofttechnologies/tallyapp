"""
User Model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """User/Account model"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    avatar = Column(String(500), nullable=True)
    
    # Role & Status
    role = Column(String(50), default="user", nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Activity
    last_login = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    companies = relationship("UserCompany", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.email}>"
    
    @property
    def full_name(self):
        """Get full name"""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self, include_companies=False):
        """Convert model to dictionary"""
        data = {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "phone": self.phone,
            "avatar": self.avatar,
            "role": self.role,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_companies:
            data["companies"] = [
                {
                    "id": uc.company.id,
                    "name": uc.company.name,
                    "role": uc.role,
                    "is_primary": uc.is_primary
                }
                for uc in self.companies
            ]
        
        return data
