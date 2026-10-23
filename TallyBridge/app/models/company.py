"""
Company Model
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Company(Base):
    """Company/Organization model"""
    
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Company Information
    name = Column(String(255), nullable=False)
    logo = Column(String(500), nullable=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    
    # Address Information
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    zip_code = Column(String(20), nullable=True)
    
    # Additional Information
    website = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)
    
    # Status
    status = Column(String(20), default="active", nullable=False, index=True)
    
    # Tally Integration Fields
    tally_guid = Column(String(100), nullable=True, unique=True, index=True)
    tally_server = Column(String(100), nullable=True, default="localhost")
    tally_port = Column(Integer, nullable=True, default=9000)
    last_sync_at = Column(DateTime, nullable=True)
    last_alter_id = Column(Integer, nullable=True, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    users = relationship("UserCompany", back_populates="company")
    
    def __repr__(self):
        return f"<Company {self.name}>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "logo": self.logo,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "zip_code": self.zip_code,
            "website": self.website,
            "industry": self.industry,
            "company_size": self.company_size,
            "status": self.status,
            "tally_guid": self.tally_guid,
            "tally_server": self.tally_server,
            "tally_port": self.tally_port,
            "last_sync_at": self.last_sync_at.isoformat() if self.last_sync_at else None,
            "last_alter_id": self.last_alter_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
