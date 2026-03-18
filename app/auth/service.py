"""
EvidenceIQ Authentication Service
JWT handling, bcrypt password hashing, and token management.
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.users.models import User
from app.auth.schemas import TokenData, ROLE_PERMISSIONS

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a plain password using bcrypt."""
    return pwd_context.hash(password)


def create_access_token(data: TokenData, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Token payload data containing user ID and role
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT string
    """
    to_encode = {"sub": data.sub, "role": data.role}
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode["exp"] = expire
    to_encode["type"] = "access"
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def create_refresh_token(user_id: str) -> str:
    """
    Create a JWT refresh token with longer expiration.
    
    Args:
        user_id: The user ID to encode
    
    Returns:
        Encoded JWT refresh token
    """
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode = {
        "sub": user_id,
        "exp": expire,
        "type": "refresh"
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: The JWT token string
    
    Returns:
        Decoded payload dict or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authenticate a user by username and password.
    
    Args:
        db: Database session
        username: Username to authenticate
        password: Plain password to verify
    
    Returns:
        User object if authentication succeeds, None otherwise
    """
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        return None
    
    if not user.is_active:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user


def generate_token_pair(user: User) -> Tuple[str, str, int]:
    """
    Generate both access and refresh tokens for a user.
    
    Args:
        user: The authenticated user
    
    Returns:
        Tuple of (access_token, refresh_token, expires_in_seconds)
    """
    token_data = TokenData(sub=str(user.id), role=user.role)
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(str(user.id))
    expires_in = settings.access_token_expire_minutes * 60
    
    return access_token, refresh_token, expires_in


def refresh_access_token(refresh_token: str, db: Session) -> Optional[Tuple[str, int]]:
    """
    Generate a new access token from a valid refresh token.
    
    Args:
        refresh_token: The refresh token string
        db: Database session
    
    Returns:
        Tuple of (new_access_token, expires_in_seconds) or None if invalid
    """
    payload = decode_token(refresh_token)
    
    if not payload:
        return None
    
    if payload.get("type") != "refresh":
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    # Verify user still exists and is active
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        return None
    
    # Generate new access token
    token_data = TokenData(sub=str(user.id), role=user.role)
    new_access_token = create_access_token(token_data)
    expires_in = settings.access_token_expire_minutes * 60
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return new_access_token, expires_in


def validate_role(role: str) -> bool:
    """Validate that a role is one of the defined roles."""
    return role in ROLE_PERMISSIONS
