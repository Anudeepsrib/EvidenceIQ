"""
EvidenceIQ Authentication Dependencies
FastAPI dependency injection for authentication and RBAC enforcement.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, List, Set

from app.database import get_db
from app.auth.service import decode_token
from app.auth.schemas import ROLE_PERMISSIONS, UserResponse
from app.users.models import User

# Security scheme for JWT tokens
security = HTTPBearer()


class AuthenticationError(HTTPException):
    """Custom authentication error with structured response."""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "authentication_failed", "message": detail},
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(HTTPException):
    """Custom authorization error - hidden, not disabled."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "access_denied", "message": "Access denied"},
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
    
    Returns:
        User model instance
    
    Raises:
        AuthenticationError: If token is invalid or user not found
    """
    token = credentials.credentials
    
    if not token:
        raise AuthenticationError("Token required")
    
    payload = decode_token(token)
    
    if not payload:
        raise AuthenticationError("Invalid or expired token")
    
    if payload.get("type") != "access":
        raise AuthenticationError("Invalid token type")
    
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token payload")
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise AuthenticationError("User not found")
    
    if not user.is_active:
        raise AuthenticationError("User account is disabled")
    
    return user


def require_roles(required_roles: List[str]):
    """
    Dependency factory to require specific roles for an endpoint.
    
    Args:
        required_roles: List of allowed roles (e.g., ["admin", "investigator"])
    
    Returns:
        Dependency function that validates user role
    
    Usage:
        @router.post("/admin-only")
        async def admin_endpoint(
            current_user: User = Depends(require_roles(["admin"]))
        ):
            return {"message": "Admin access granted"}
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in required_roles:
            raise AuthorizationError()
        return current_user
    return role_checker


def require_permissions(required_permissions: Set[str]):
    """
    Dependency factory to require specific permissions for an endpoint.
    
    Args:
        required_permissions: Set of required permission strings
    
    Returns:
        Dependency function that validates user has all required permissions
    """
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        user_permissions = ROLE_PERMISSIONS.get(current_user.role, set())
        
        if not required_permissions.issubset(user_permissions):
            raise AuthorizationError()
        
        return current_user
    return permission_checker


# Common role-based dependencies
require_admin = require_roles(["admin"])
require_investigator_or_above = require_roles(["admin", "investigator"])
require_reviewer_or_above = require_roles(["admin", "investigator", "reviewer"])
require_any_user = require_roles(["admin", "investigator", "reviewer", "viewer"])

# Permission-based dependencies
require_upload = require_permissions({"upload_media"})
require_view = require_permissions({"view_search"})
require_classify = require_permissions({"tag_classify"})
require_export = require_permissions({"export_report"})
require_redact = require_permissions({"redact_metadata"})
require_manage_users = require_permissions({"manage_users"})
require_delete = require_permissions({"delete_media"})
require_audit_access = require_permissions({"view_audit_logs"})


def optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.
    Useful for endpoints that work both authenticated and unauthenticated.
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None
