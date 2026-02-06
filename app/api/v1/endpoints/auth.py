"""
Authentication endpoints for login, register, and user management.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings
from app.schemas.auth import UserCreate, UserLogin, User, AuthResponse
from app.services.auth_service import AuthService, create_access_token, decode_token

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Authentication"])

# HTTP Bearer scheme for token authentication
bearer_scheme = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = AuthService.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    return user


@router.post("/register", response_model=AuthResponse)
async def register(user_data: UserCreate):
    """Register a new user."""
    try:
        user = AuthService.create_user(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name
        )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["id"]}, expires_delta=access_token_expires
        )
        
        return AuthResponse(user=User(**user), token=access_token)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=AuthResponse)
async def login(user_data: UserLogin):
    """Login with email and password."""
    user = AuthService.authenticate_user(user_data.email, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["id"]}, expires_delta=access_token_expires
    )
    
    return AuthResponse(user=User(**user), token=access_token)


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    return User(**current_user)
