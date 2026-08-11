"""
Authentication Router

Provides endpoints for user registration, login, logout,
token refresh, and profile retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from api.app.core.security import (
    blacklist_token,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_bearer_token,
    get_current_user,
    hash_password,
    is_token_blacklisted,
    verify_password,
)
from api.app.db.session import get_db
from api.app.models.user import User
from api.app.schemas.user import (
    RefreshRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ==========================================
# SIGNUP
# ==========================================

@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.

    - Validates that the email is not already registered.
    - Hashes the password before storing.
    """
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ==========================================
# LOGIN
# ==========================================

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive JWT tokens",
)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate with email and password.

    Returns a short-lived **access token** and a long-lived **refresh token**.
    """
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )

    return TokenResponse(
        access_token=create_access_token(subject=user.id),
        refresh_token=create_refresh_token(subject=user.id),
    )


# ==========================================
# LOGOUT
# ==========================================

@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Invalidate the current access token",
)
def logout(token: str = Depends(get_bearer_token)):
    """
    Blacklists the current access token so it can no longer be used.
    The client should also discard its stored tokens.
    """
    blacklist_token(token)
    return {"message": "Successfully logged out."}


# ==========================================
# REFRESH TOKEN
# ==========================================

@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Get a new access token using a refresh token",
)
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    """
    Exchange a valid refresh token for a new access + refresh token pair.

    The old refresh token is blacklisted to prevent replay.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if is_token_blacklisted(payload.refresh_token):
        raise credentials_exception

    try:
        token_data = decode_token(payload.refresh_token)
        user_id = token_data.get("sub")
        token_type = token_data.get("type")

        if user_id is None or token_type != "refresh":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception

    # Rotate: blacklist the old refresh token
    blacklist_token(payload.refresh_token)

    return TokenResponse(
        access_token=create_access_token(subject=user.id),
        refresh_token=create_refresh_token(subject=user.id),
    )


# ==========================================
# CURRENT USER PROFILE
# ==========================================

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the authenticated user's profile",
)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    return current_user
