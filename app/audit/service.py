"""
EvidenceIQ Audit Service
Logging service for compliance and chain of custody.
"""
import json
from typing import Optional, Any, Dict
from sqlalchemy.orm import Session

from app.audit.models import AuditLog


def log_action(
    db: Session,
    action: str,
    user_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> AuditLog:
    """
    Log an action to the audit log.
    
    Args:
        db: Database session
        action: Action type (from AuditActionType)
        user_id: User who performed the action
        resource_type: Type of resource affected
        resource_id: ID of resource affected
        details: Additional JSON-serializable details
        ip_address: Client IP address
        user_agent: Client user agent
    
    Returns:
        Created audit log entry
    """
    # Serialize details to JSON string if provided
    details_json = json.dumps(details) if details else None
    
    log_entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details_json,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    
    return log_entry


def get_audit_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Query audit logs with filters.
    
    Returns:
        Tuple of (logs list, total count)
    """
    from datetime import datetime
    
    query = db.query(AuditLog)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if action:
        query = query.filter(AuditLog.action == action)
    
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    
    if resource_id:
        query = query.filter(AuditLog.resource_id == resource_id)
    
    if start_date:
        query = query.filter(AuditLog.timestamp >= datetime.fromisoformat(start_date))
    
    if end_date:
        query = query.filter(AuditLog.timestamp <= datetime.fromisoformat(end_date))
    
    # Order by timestamp descending (newest first)
    query = query.order_by(AuditLog.timestamp.desc())
    
    total = query.count()
    logs = query.offset(skip).limit(limit).all()
    
    return logs, total


def get_user_activity(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 100
):
    """Get all activity for a specific user."""
    query = db.query(AuditLog).filter(
        AuditLog.user_id == user_id
    ).order_by(AuditLog.timestamp.desc())
    
    total = query.count()
    logs = query.offset(skip).limit(limit).all()
    
    return logs, total
