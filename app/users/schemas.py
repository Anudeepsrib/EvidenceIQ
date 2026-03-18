"""
EvidenceIQ User Schemas
Pydantic models for user CRUD operations.
"""
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime

from app.config import settings


class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(..., min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    role: str = Field(..., pattern="^(admin|investigator|reviewer|viewer)$")
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a new user (admin only)."""
    password: str = Field(..., min_length=8)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < settings.password_min_length:
            raise ValueError(f"Password must be at least {settings.password_min_length} characters")
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user (admin only)."""
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, pattern="^(admin|investigator|reviewer|viewer)$")
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase):
    """User response schema (safe for API exposure)."""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Response for listing users."""
    users: list[UserResponse]
    total: int


class UserCreateResponse(BaseModel):
    """Response after creating a user."""
    id: str
    username: str
    role: str
    message: str = "User created successfully"
