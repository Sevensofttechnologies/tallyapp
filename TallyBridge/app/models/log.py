"""
Log Model for Activity Logging
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from datetime import datetime
from app.database import Base


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    level = Column(String(20), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    user_id = Column(Integer, nullable=True, index=True)
    user_email = Column(String(100), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    details = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False, default="Success")
    message = Column(Text, nullable=False)

    def __repr__(self):
        return f"<Log(id={self.id}, level='{self.level}', category='{self.category}')>"
