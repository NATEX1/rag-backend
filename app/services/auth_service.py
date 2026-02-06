"""
Authentication service with JWT token handling and password management.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from app.core.config import get_settings

settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a plain password."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


class AuthService:
    """Service for handling user authentication."""
    
    @staticmethod
    def create_user(email: str, password: str, name: str) -> dict:
        """Create a new user."""
        if email in _users_db:
            raise ValueError("User with this email already exists")
        
        user_id = str(len(_users_db) + 1)
        hashed_password = get_password_hash(password)
        
        user = {
            "id": user_id,
            "email": email,
            "name": name,
            "hashed_password": hashed_password,
        }
        
        _users_db[email] = user
        return {
            "id": user_id,
            "email": email,
            "name": name,
        }
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[dict]:
        """Authenticate a user with email and password."""
        user = _users_db.get(email)
        if not user:
            return None
        if not verify_password(password, user["hashed_password"]):
            return None
        return {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
        }
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[dict]:
        """Get a user by ID."""
        for user in _users_db.values():
            if user["id"] == user_id:
                return {
                    "id": user["id"],
                    "email": user["email"],
                    "name": user["name"],
                }
        return None


# In-memory user storage (replace with database in production)
_users_db = {}

# Don't create default user to avoid bcrypt issues during import
