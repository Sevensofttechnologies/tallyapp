"""
Logging Service
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import Optional, Dict, List
from app.models.log import Log


def create_log(
    db: Session,
    level: str,
    category: str,
    action: str,
    message: str,
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict] = None,
    status: str = "Success"
) -> Log:
    """Create a new log entry"""
    log = Log(
        level=level,
        category=category,
        action=action,
        message=message,
        user_id=user_id,
        user_email=user_email,
        ip_address=ip_address,
        details=details,
        status=status,
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def log_info(db: Session, category: str, action: str, message: str, 
             user_id: Optional[int] = None, user_email: Optional[str] = None,
             ip_address: Optional[str] = None, details: Optional[Dict] = None) -> Log:
    """Log INFO level message"""
    return create_log(db, "INFO", category, action, message, user_id, user_email, ip_address, details)


def log_warning(db: Session, category: str, action: str, message: str,
                user_id: Optional[int] = None, user_email: Optional[str] = None,
                ip_address: Optional[str] = None, details: Optional[Dict] = None) -> Log:
    """Log WARNING level message"""
    return create_log(db, "WARNING", category, action, message, user_id, user_email, ip_address, details)


def log_error(db: Session, category: str, action: str, message: str,
              user_id: Optional[int] = None, user_email: Optional[str] = None,
              ip_address: Optional[str] = None, details: Optional[Dict] = None) -> Log:
    """Log ERROR level message"""
    return create_log(db, "ERROR", category, action, message, user_id, user_email, ip_address, details)


def get_recent_logs(db: Session, limit: int = 50) -> List[Log]:
    """Get most recent logs"""
    return db.query(Log).order_by(desc(Log.timestamp)).limit(limit).all()
