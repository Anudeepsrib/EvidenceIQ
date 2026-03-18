"""
EvidenceIQ Authentication Schemas
Pydantic models for auth request/response validation.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


class TokenData(BaseModel):
    """JWT token payload data."""
    sub: str = Field(..., description="User ID (subject)")
    role: str = Field(..., description="User role")
    exp: Optional[datetime] = Field(None, description="Expiration time")


class TokenResponse(BaseModel):
    """Token response with access and refresh tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token expiration in seconds")


class LoginRequest(BaseModel):
    """Login request payload."""
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1)


class RefreshRequest(BaseModel):
    """Token refresh request payload."""
    refresh_token: str


class UserResponse(BaseModel):
    """User data response (safe for API exposure)."""
    id: str
    username: str
    email: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class PasswordChangeRequest(BaseModel):
    """Password change request."""
    current_password: str
    new_password: str = Field(..., min_length=8)


class RoleUpdateRequest(BaseModel):
    """Role update request (admin only)."""
    role: str = Field(..., pattern="^(admin|investigator|reviewer|viewer)$")


# Role permission definitions
ROLE_PERMISSIONS = {
    "admin": {
        "upload_media", "view_search", "tag_classify", "export_report",
        "redact_metadata", "manage_users", "delete_media", "view_audit_logs"
    },
    "investigator": {
        "upload_media", "view_search", "tag_classify", "export_report",
        "redact_metadata", "view_audit_logs"
    },
    "reviewer": {
        "view_search", "export_report"
    },
    "viewer": {
        "view_search"
    }
}


def has_permission(role: str, permission: str) -> bool:
    """Check if a role has a specific permission."""
    return permission in ROLE_PERMISSIONS.get(role, set())


def get_role_permissions(role: str) -> List[str]:
    """Get all permissions for a role."""
    return list(ROLE_PERMISSIONS.get(role, set()))
