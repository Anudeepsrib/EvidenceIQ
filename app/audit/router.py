"""
EvidenceIQ Audit Router
Audit log query endpoints for compliance and investigations.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user, require_permissions
from app.users.models import User
from app.audit import service as audit_service
from app.audit.models import AuditActionType

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/logs")
def get_audit_logs(
    request: Request,
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Records per page"),
    user_id: Optional[str] = Query(None, description="Filter by user"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[str] = Query(None, description="Filter by resource ID"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions({"view_audit_logs"}))
):
    """
    Query audit logs (admin and investigator only).
    
    **Action Types:**
    - LOGIN | LOGOUT | PASSWORD_CHANGE
    - USER_CREATE | USER_UPDATE | USER_DELETE | ROLE_CHANGE
    - UPLOAD | PROCESS | DELETE | REDACT
    - SEARCH | REPORT_GENERATE
    - SYSTEM_ERROR | CONFIG_CHANGE
    
    All permission-sensitive actions are logged here.
    """
    logs, total = audit_service.get_audit_logs(
        db=db,
        skip=skip,
        limit=limit,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Parse JSON details
    import json
    formatted_logs = []
    for log in logs:
        log_dict = {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "timestamp": log.timestamp,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "ip_address": log.ip_address,
            "details": json.loads(log.details) if log.details else None
        }
        formatted_logs.append(log_dict)
    
    return {
        "logs": formatted_logs,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/user/{user_id}")
def get_user_activity(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions({"view_audit_logs"}))
):
    """
    Get all audit log entries for a specific user.
    """
    logs, total = audit_service.get_user_activity(db, user_id, skip, limit)
    
    import json
    formatted_logs = []
    for log in logs:
        log_dict = {
            "id": log.id,
            "action": log.action,
            "timestamp": log.timestamp,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "details": json.loads(log.details) if log.details else None
        }
        formatted_logs.append(log_dict)
    
    return {
        "user_id": user_id,
        "logs": formatted_logs,
        "total": total
    }


@router.get("/actions")
def list_action_types(
    current_user: User = Depends(require_permissions({"view_audit_logs"}))
):
    """
    List all available audit action types.
    """
    return {
        "actions": [
            # Auth
            AuditActionType.LOGIN,
            AuditActionType.LOGOUT,
            AuditActionType.PASSWORD_CHANGE,
            # User management
            AuditActionType.USER_CREATE,
            AuditActionType.USER_UPDATE,
            AuditActionType.USER_DELETE,
            AuditActionType.ROLE_CHANGE,
            # Media
            AuditActionType.UPLOAD,
            AuditActionType.PROCESS,
            AuditActionType.DELETE,
            AuditActionType.REDACT,
            # Search/Reports
            AuditActionType.SEARCH,
            AuditActionType.REPORT_GENERATE,
            # System
            AuditActionType.SYSTEM_ERROR,
            AuditActionType.CONFIG_CHANGE,
        ]
    }
