"""
Audit Trail Service
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.audit_trail import AuditTrail


def create_audit_trail(
    db: Session,
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
    action: str = "UNKNOWN",
    resource_type: str = "UNKNOWN",
    resource_id: Optional[int] = None,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    status: str = "SUCCESS",
    message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> AuditTrail:
    """Create a new audit trail entry"""
    audit_entry = AuditTrail(
        user_id=user_id,
        user_email=user_email,
        action=action.upper(),
        resource_type=resource_type,
        resource_id=resource_id,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
        user_agent=user_agent,
        status=status.upper(),
        message=message,
        details=details,
        timestamp=datetime.utcnow()
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    return audit_entry


def log_create(db: Session, user_id: Optional[int], user_email: Optional[str],
               resource_type: str, resource_id: int, new_values: Dict[str, Any],
               ip_address: Optional[str] = None, message: Optional[str] = None) -> AuditTrail:
    """Log a CREATE action"""
    if not message:
        message = f"{resource_type} #{resource_id} created"
    return create_audit_trail(db, user_id, user_email, "CREATE", resource_type, 
                              resource_id, None, new_values, ip_address, None, "SUCCESS", message)


def log_update(db: Session, user_id: Optional[int], user_email: Optional[str],
               resource_type: str, resource_id: int, old_values: Dict[str, Any],
               new_values: Dict[str, Any], ip_address: Optional[str] = None,
               message: Optional[str] = None) -> AuditTrail:
    """Log an UPDATE action"""
    if not message:
        message = f"{resource_type} #{resource_id} updated"
    return create_audit_trail(db, user_id, user_email, "UPDATE", resource_type,
                              resource_id, old_values, new_values, ip_address, None, "SUCCESS", message)


def log_delete(db: Session, user_id: Optional[int], user_email: Optional[str],
               resource_type: str, resource_id: int, old_values: Dict[str, Any],
               ip_address: Optional[str] = None, message: Optional[str] = None) -> AuditTrail:
    """Log a DELETE action"""
    if not message:
        message = f"{resource_type} #{resource_id} deleted"
    return create_audit_trail(db, user_id, user_email, "DELETE", resource_type,
                              resource_id, old_values, None, ip_address, None, "SUCCESS", message)


def get_resource_history(db: Session, resource_type: str, resource_id: int, limit: int = 50) -> List[AuditTrail]:
    """Get audit history for a specific resource"""
    return db.query(AuditTrail).filter(
        AuditTrail.resource_type == resource_type,
        AuditTrail.resource_id == resource_id
    ).order_by(desc(AuditTrail.timestamp)).limit(limit).all()
