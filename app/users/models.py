"""
EvidenceIQ User Models
SQLAlchemy models for user management with RBAC.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.types import TypeDecorator, CHAR

from app.database import Base


class UUID(TypeDecorator):
    """Platform-independent UUID type for SQLAlchemy."""
    impl = CHAR(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return str(value)


class User(Base):
    """
    User model with RBAC support.
    
    Roles:
    - admin: Full system access
    - investigator: Upload, process, redact, view audit
    - reviewer: View, export reports
    - viewer: View/search only
    """
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="viewer")
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Indexes for common queries
    __table_args__ = (
        Index('ix_users_role_active', 'role', 'is_active'),
    )

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"
