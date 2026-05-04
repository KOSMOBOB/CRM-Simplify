from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_password_hash, create_access_token, create_refresh_token
from app.schemas import UserCreate, UserResponse, UserUpdate, Token
from app.dependencies.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Register a new user."""
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
    )
    
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
async def login(
    email: str,
    password: str,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Login and get access/refresh tokens."""
    from app.core.security import verify_password
    
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
    refresh_token = create_refresh_token(data={"sub": user.email, "user_id": user.id})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Refresh access token using refresh token."""
    from app.core.security import decode_token
    
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("user_id")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    new_access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
    new_refresh_token = create_refresh_token(data={"sub": user.email, "user_id": user.id})
    
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get current user information."""
    result = await db.execute(select(User).where(User.id == current_user["user_id"]))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Update current user information."""
    result = await db.execute(select(User).where(User.id == current_user["user_id"]))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.flush()
    await db.refresh(user)
    
    return user


@router.get("/oauth/google")
async def google_oauth_initiate():
    """Initiate Google OAuth2 flow (placeholder)."""
    # In production, redirect to Google OAuth2 consent screen
    # For now, return placeholder URL
    return {
        "oauth_url": "https://accounts.google.com/o/oauth2/v2/auth?"
                     "client_id=YOUR_CLIENT_ID&"
                     "redirect_uri=http://localhost:8000/api/v1/auth/oauth/google/callback&"
                     "response_type=code&"
                     "scope=email%20profile&"
                     "access_type=offline&"
                     "prompt=consent"
    }


@router.get("/oauth/google/callback")
async def google_oauth_callback(
    code: str,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Handle Google OAuth2 callback (placeholder)."""
    # In production:
    # 1. Exchange code for tokens
    # 2. Get user info from Google
    # 3. Create/find user in DB
    # 4. Return JWT tokens
    
    # Placeholder implementation
    return {
        "message": "OAuth callback received. Implement token exchange here.",
        "code": code[:10] + "..."  # Log partial code for debugging
    }
