"""
EvidenceIQ Users Router
Admin-only CRUD operations for user management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.auth.dependencies import require_admin
from app.users import service as user_service
from app.users.schemas import (
    UserCreate, UserUpdate, UserResponse,
    UserListResponse, UserCreateResponse
)
from app.users.models import User
from app.audit.service import log_action
from app.audit.models import AuditActionType

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=UserListResponse)
def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search by username or email"),
    role: Optional[str] = Query(None, pattern="^(admin|investigator|reviewer|viewer)$"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    List all users (admin only).
    
    Supports pagination, search, and role filtering.
    """
    users, total = user_service.list_users(
        db, skip=skip, limit=limit,
        search=search, role=role, is_active=is_active
    )
    
    return UserListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        total=total
    )


@router.post("", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    request: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new user (admin only).
    
    - **username**: Unique username (3-100 chars)
    - **password**: Initial password (min 8 chars)
    - **email**: Optional email address
    - **role**: One of: admin, investigator, reviewer, viewer
    - **is_active**: Whether user can login (default: true)
    """
    try:
        user = user_service.create_user(db, request, created_by=str(current_user.id))
        
        # Log user creation
        log_action(
            db=db,
            action=AuditActionType.USER_CREATE,
            user_id=current_user.id,
            details={
                "created_user_id": str(user.id),
                "created_username": user.username,
                "created_role": user.role
            },
            ip_address=None
        )
        
        return UserCreateResponse(
            id=str(user.id),
            username=user.username,
            role=user.role,
            message="User created successfully"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "validation_error", "message": str(e)}
        )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get a specific user by ID (admin only).
    """
    user = user_service.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "User not found"}
        )
    
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    request: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update a user (admin only).
    
    Only provided fields will be updated. Cannot update own role to prevent
    lockout - another admin must do this.
    """
    # Prevent self-demotion from admin
    if str(current_user.id) == user_id and request.role and request.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_operation",
                "message": "Cannot demote yourself. Another admin must change your role."
            }
        )
    
    try:
        user = user_service.update_user(db, user_id, request, updated_by=str(current_user.id))
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "not_found", "message": "User not found"}
            )
        
        # Log role change if applicable
        if request.role:
            log_action(
                db=db,
                action=AuditActionType.ROLE_CHANGE,
                user_id=current_user.id,
                details={
                    "target_user_id": user_id,
                    "new_role": request.role
                },
                ip_address=None
            )
        
        # Log update
        log_action(
            db=db,
            action=AuditActionType.USER_UPDATE,
            user_id=current_user.id,
            details={"target_user_id": user_id},
            ip_address=None
        )
        
        return UserResponse.model_validate(user)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "validation_error", "message": str(e)}
        )


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Deactivate a user (soft delete) (admin only).
    
    User is deactivated but retained for audit trail.
    Cannot delete yourself.
    """
    # Prevent self-deletion
    if str(current_user.id) == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_operation",
                "message": "Cannot delete your own account."
            }
        )
    
    # Check target user exists
    target_user = user_service.get_user_by_id(db, user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "User not found"}
        )
    
    # Prevent deleting the last admin
    if target_user.role == "admin":
        admin_count = db.query(User).filter(
            User.role == "admin",
            User.is_active == True
        ).count()
        
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "invalid_operation",
                    "message": "Cannot delete the last admin user."
                }
            )
    
    # Soft delete (deactivate)
    success = user_service.delete_user(db, user_id)
    
    # Log deletion
    log_action(
        db=db,
        action=AuditActionType.USER_DELETE,
        user_id=current_user.id,
        details={
            "deleted_user_id": user_id,
            "deleted_username": target_user.username,
            "soft_delete": True
        },
        ip_address=None
    )
    
    return {"message": "User deactivated successfully"}


@router.get("/stats/by-role")
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get user statistics by role (admin only).
    """
    return user_service.count_users_by_role(db)
