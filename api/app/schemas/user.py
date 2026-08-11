"""
User & Authentication Pydantic Schemas

Used for request validation and response serialisation
across the auth endpoints.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ==========================================
# USER SCHEMAS
# ==========================================

class UserCreate(BaseModel):
    """Payload for the signup endpoint."""
    email: EmailStr
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    """Payload for the login endpoint."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Public user profile returned by the API."""
    id: str
    email: str
    username: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# TOKEN SCHEMAS
# ==========================================

class TokenResponse(BaseModel):
    """Returned after successful login or token refresh."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Payload for the token refresh endpoint."""
    refresh_token: str


class TokenPayload(BaseModel):
    """Decoded JWT payload structure (internal use)."""
    sub: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None
