"""
Authentication & Security Module

Provides:
- Password hashing (bcrypt via passlib)
- JWT access / refresh token creation & verification
- FastAPI dependency `get_current_user` for route protection
- In-memory token blacklist for logout support
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Set

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from api.app.core.config import settings
from api.app.db.session import get_db

# ==========================================
# PASSWORD HASHING
# ==========================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ==========================================
# JWT TOKEN MANAGEMENT
# ==========================================

# HTTP Bearer scheme for Swagger UI's Authorize button.
bearer_scheme = HTTPBearer(
    scheme_name="BearerAuth",
    description="Paste only the JWT access token. Swagger will send it as: Bearer <token>.",
)

# In-memory set of revoked JTI (JWT ID) claims for logout.
# In production, replace with Redis or a database table.
_blacklisted_tokens: Set[str] = set()


def create_access_token(subject: str, extra_claims: Optional[dict] = None) -> str:
    """
    Create a short-lived JWT access token.
    
    Args:
        subject: The user ID (stored as ``sub`` claim).
        extra_claims: Optional additional claims to embed.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "type": "access",
    }
    if extra_claims:
        to_encode.update(extra_claims)
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """
    Create a long-lived JWT refresh token.
    
    Args:
        subject: The user ID (stored as ``sub`` claim).
    """
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    
    Raises ``JWTError`` if the token is invalid or expired.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def blacklist_token(token: str) -> None:
    """Add a token to the blacklist so it cannot be reused after logout."""
    _blacklisted_tokens.add(token)


def is_token_blacklisted(token: str) -> bool:
    """Check whether a token has been revoked."""
    return token in _blacklisted_tokens


# ==========================================
# FASTAPI DEPENDENCIES
# ==========================================

def get_bearer_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    """Extract the raw JWT token from the Authorization: Bearer header."""
    return credentials.credentials


async def get_current_user(
    token: str = Depends(get_bearer_token),
    db: Session = Depends(get_db),
):
    """
    FastAPI dependency that extracts and validates the JWT Bearer token,
    then returns the corresponding ``User`` ORM instance.

    Raises ``401 UNAUTHORIZED`` if the token is missing, expired,
    blacklisted, or belongs to a non-existent / inactive user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Check blacklist
    if is_token_blacklisted(token):
        raise credentials_exception

    # 2. Decode the JWT
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 3. Lookup user in the database
    # Import here to avoid circular imports (models → session → security)
    from api.app.models.user import User

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )

    return user
