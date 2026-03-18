"""
EvidenceIQ Authentication Router
Login, token refresh, and current user endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.config import settings
from app.auth import service as auth_service
from app.auth.schemas import (
    LoginRequest, TokenResponse, RefreshRequest,
    UserResponse, PasswordChangeRequest
)
from app.auth.dependencies import get_current_user, AuthenticationError
from app.users.models import User
from app.audit.service import log_action
from app.audit.models import AuditActionType

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens.
    
    - **username**: User's username
    - **password**: User's password
    
    Returns access token (60 min) and refresh token (7 days).
    """
    user = auth_service.authenticate_user(db, request.username, request.password)
    
    if not user:
        log_action(
            db=db,
            action=AuditActionType.LOGIN,
            details={"username": request.username, "success": False},
            ip_address=None  # Will be set by middleware
        )
        raise AuthenticationError("Invalid credentials")
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Generate tokens
    access_token, refresh_token, expires_in = auth_service.generate_token_pair(user)
    
    # Log successful login
    log_action(
        db=db,
        action=AuditActionType.LOGIN,
        user_id=user.id,
        details={"username": user.username, "success": True},
        ip_address=None
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    request: RefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using a valid refresh token.
    
    - **refresh_token**: Valid refresh token from /auth/login
    
    Returns new access token. Refresh token remains valid until expiration.
    """
    result = auth_service.refresh_access_token(request.refresh_token, db)
    
    if not result:
        raise AuthenticationError("Invalid or expired refresh token")
    
    new_access_token, expires_in = result
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=request.refresh_token,  # Return same refresh token
        token_type="bearer",
        expires_in=expires_in
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's information.
    
    Returns user profile without sensitive data.
    """
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change current user's password.
    
    - **current_password**: Current password for verification
    - **new_password**: New password (min 8 characters)
    """
    # Verify current password
    if not auth_service.verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "invalid_password", "message": "Current password is incorrect"}
        )
    
    # Validate new password length
    if len(request.new_password) < settings.password_min_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "weak_password",
                "message": f"Password must be at least {settings.password_min_length} characters"
            }
        )
    
    # Update password
    current_user.hashed_password = auth_service.get_password_hash(request.new_password)
    db.commit()
    
    # Log password change
    log_action(
        db=db,
        action=AuditActionType.USER_UPDATE,
        user_id=current_user.id,
        details={"action": "password_change"},
        ip_address=None
    )
    
    return {"message": "Password updated successfully"}


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout current user (client should discard tokens).
    
    Note: JWT tokens cannot be truly revoked server-side. 
    Tokens remain valid until expiration.
    """
    log_action(
        db=db,
        action=AuditActionType.LOGIN,
        user_id=current_user.id,
        details={"action": "logout", "username": current_user.username},
        ip_address=None
    )
    
    return {"message": "Logout successful"}
