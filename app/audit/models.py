"""
EvidenceIQ Audit Models
Append-only audit log for compliance and chain of custody.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Index, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base
from app.users.models import UUID


class AuditActionType:
    """Audit action type constants."""
    # Auth actions
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    
    # User management
    USER_CREATE = "USER_CREATE"
    USER_UPDATE = "USER_UPDATE"
    USER_DELETE = "USER_DELETE"
    ROLE_CHANGE = "ROLE_CHANGE"
    
    # Media actions
    UPLOAD = "UPLOAD"
    PROCESS = "PROCESS"
    DELETE = "DELETE"
    REDACT = "REDACT"
    
    # Search and reports
    SEARCH = "SEARCH"
    REPORT_GENERATE = "REPORT_GENERATE"
    
    # System
    SYSTEM_ERROR = "SYSTEM_ERROR"
    CONFIG_CHANGE = "CONFIG_CHANGE"


class AuditLog(Base):
    """
    Append-only audit log entry.
    
    All permission-sensitive actions are logged here.
    Records are immutable once created.
    """
    __tablename__ = "audit_logs"

    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Who performed the action
    user_id = Column(UUID, ForeignKey("users.id"), nullable=True, index=True)
    
    # Action details
    action = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # What was affected
    resource_type = Column(String(50), nullable=True)  # "media", "user", "report"
    resource_id = Column(UUID, nullable=True)
    
    # Additional context (JSON string)
    details = Column(Text, nullable=True)
    
    # Client context
    ip_address = Column(String(45), nullable=True)  # IPv6 max length
    user_agent = Column(String(255), nullable=True)
    
    # Relationship (optional, for querying)
    user = relationship("User", foreign_keys=[user_id])
    
    # Indexes for common queries
    __table_args__ = (
        Index('ix_audit_logs_action_timestamp', 'action', 'timestamp'),
        Index('ix_audit_logs_user_timestamp', 'user_id', 'timestamp'),
        Index('ix_audit_logs_resource', 'resource_type', 'resource_id'),
    )

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user={self.user_id})>"
