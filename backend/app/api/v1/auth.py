"""Authentication API endpoints"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import re

from app.db.database import get_db
from app.models.user import User
from app.core.auth import authenticate_user, get_current_active_user
from app.core.security import get_password_hash, create_access_token
from app.core.config import settings
from app.core.audit import log_audit_event
from app.utils.security import validate_password_strength

router = APIRouter()


class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    """User creation model"""
    email: EmailStr
    username: str
    password: str
    role: str = "operator"


class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: str
    username: str
    role: str
    is_active: bool
    mfa_enabled: bool
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        """Convert ORM object to response model with proper UUID serialization"""
        return cls(
            id=str(obj.id),
            email=obj.email,
            username=obj.username,
            role=obj.role,
            is_active=obj.is_active,
            mfa_enabled=getattr(obj, 'mfa_enabled', False)
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Authenticate user and return access token"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # Log failed login attempt for security audit
        # Try to find user by username to get user_id for audit log
        failed_user = db.query(User).filter(User.username == form_data.username).first()
        log_audit_event(
            db=db,
            user=failed_user,  # May be None if user doesn't exist
            action="LOGIN_FAILED",
            resource_type="user",
            resource_id=failed_user.id if failed_user else None,
            details={
                "username": form_data.username,
                "ip_address": request.client.host if request and request.client else None
            },
            request=request
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    # Log audit event
    log_audit_event(
        db=db,
        user=user,
        action="LOGIN",
        request=request
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return UserResponse.from_orm(current_user)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Register a new user (admin only)"""
    # Only admins can create users
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create users"
        )
    
    # Validate password strength
    password_valid, password_error = validate_password_strength(user_data.password)
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=password_error
        )
    
    # Validate username format
    if not user_data.username or len(user_data.username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters long"
        )
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username can only contain letters, numbers, underscores, and hyphens"
        )
    
    # Validate role
    valid_roles = ["admin", "operator", "viewer"]
    if user_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    try:
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=get_password_hash(user_data.password),
            role=user_data.role
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    # Log audit event
    log_audit_event(
        db=db,
        user=current_user,
        action="CREATE_USER",
        resource_type="user",
        resource_id=new_user.id,
        details={"username": new_user.username, "role": new_user.role}
    )
    
    return UserResponse.from_orm(new_user)


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Logout user (logs audit event)"""
    log_audit_event(
        db=db,
        user=current_user,
        action="LOGOUT",
        request=request
    )
    
    return {"message": "Successfully logged out"}

