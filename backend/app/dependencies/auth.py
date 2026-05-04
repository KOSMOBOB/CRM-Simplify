from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import get_settings
from app.core.security import decode_token
from app.schemas import TokenData

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> dict:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    try:
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        token_type: str = payload.get("type")
        
        if email is None or user_id is None:
            raise credentials_exception
        if token_type != "access":
            raise credentials_exception
            
        token_data = TokenData(email=email, user_id=user_id)
    except (JWTError, ValidationError):
        raise credentials_exception
    
    # Return user info (in real app, fetch from DB)
    return {"email": token_data.email, "user_id": token_data.user_id}


async def get_current_active_user(
    current_user: Annotated[dict, Depends(get_current_user)]
) -> dict:
    """Get current active user."""
    return current_user


async def get_current_superuser(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> dict:
    """Get current superuser."""
    # In real app, check is_superuser flag from DB
    # For now, just return the user
    return current_user
