"""
EvidenceIQ User Service
CRUD operations for user management (admin only).
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate
from app.auth.service import get_password_hash, validate_role


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def list_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None
) -> tuple[List[User], int]:
    """
    List users with optional filtering.
    
    Returns:
        Tuple of (users list, total count)
    """
    query = db.query(User)
    
    # Apply filters
    if search:
        search_filter = or_(
            User.username.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%") if User.email else False
        )
        query = query.filter(search_filter)
    
    if role:
        query = query.filter(User.role == role)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    users = query.offset(skip).limit(limit).all()
    
    return users, total


def create_user(db: Session, user_data: UserCreate, created_by: Optional[str] = None) -> User:
    """
    Create a new user.
    
    Args:
        db: Database session
        user_data: User creation data
        created_by: ID of admin creating the user (for audit)
    
    Returns:
        Created user
    
    Raises:
        ValueError: If username/email exists or role is invalid
    """
    # Check for existing username
    if get_user_by_username(db, user_data.username):
        raise ValueError(f"Username '{user_data.username}' already exists")
    
    # Check for existing email
    if user_data.email and get_user_by_email(db, user_data.email):
        raise ValueError(f"Email '{user_data.email}' already exists")
    
    # Validate role
    if not validate_role(user_data.role):
        raise ValueError(f"Invalid role: {user_data.role}")
    
    # Create user
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        is_active=user_data.is_active
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


def update_user(
    db: Session,
    user_id: str,
    user_data: UserUpdate,
    updated_by: Optional[str] = None
) -> Optional[User]:
    """
    Update an existing user.
    
    Returns:
        Updated user or None if not found
    
    Raises:
        ValueError: If email is already in use by another user
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    # Update fields if provided
    if user_data.email is not None:
        # Check email uniqueness
        existing = get_user_by_email(db, user_data.email)
        if existing and existing.id != user_id:
            raise ValueError(f"Email '{user_data.email}' already in use")
        user.email = user_data.email
    
    if user_data.role is not None:
        if not validate_role(user_data.role):
            raise ValueError(f"Invalid role: {user_data.role}")
        user.role = user_data.role
    
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    if user_data.password is not None:
        if len(user_data.password) < 8:
            raise ValueError("Password must be at least 8 characters")
        user.hashed_password = get_password_hash(user_data.password)
    
    db.commit()
    db.refresh(user)
    
    return user


def delete_user(db: Session, user_id: str) -> bool:
    """
    Delete a user (soft delete by deactivating).
    
    Note: We deactivate instead of hard delete for audit trail preservation.
    
    Returns:
        True if user was deactivated, False if not found
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    user.is_active = False
    db.commit()
    
    return True


def hard_delete_user(db: Session, user_id: str) -> bool:
    """
    Permanently delete a user.
    
    WARNING: Only use for GDPR/data retention compliance.
    This will cascade delete all related audit logs if configured.
    
    Returns:
        True if deleted, False if not found
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    db.delete(user)
    db.commit()
    
    return True


def count_users_by_role(db: Session) -> dict:
    """Get count of users by role."""
    from sqlalchemy import func
    
    result = db.query(User.role, func.count(User.id)).group_by(User.role).all()
    return {role: count for role, count in result}
