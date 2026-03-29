"""
User management API routes.

Handles registration, login, token refresh, and profile.
"""

from fastapi import APIRouter, HTTPException, status

from app.services.auth_service import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.utils.validators import UserCreateRequest, UserLoginRequest

router = APIRouter()

# NOTE: In production, replace this in-memory store with PostgreSQL via SQLAlchemy.
# This simple dict is only for MVP/demo purposes.
_users_db: dict = {}


@router.post(
    "/register",
    summary="Register a new user account",
    status_code=status.HTTP_201_CREATED,
)
async def register(body: UserCreateRequest):
    """
    Create a new user account.

    - **username**: Alphanumeric + underscores, 3–50 characters
    - **email**: Valid email address
    - **password**: At least 8 characters
    - **full_name**: *(optional)* Display name
    """
    if body.username in _users_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken.",
        )

    _users_db[body.username] = {
        "username": body.username,
        "email": body.email,
        "hashed_password": hash_password(body.password),
        "full_name": body.full_name,
        "is_active": True,
    }

    return {"message": "Account created successfully! Welcome to Bangladeshi-ai 🇧🇩"}


@router.post("/login", summary="Log in and receive JWT tokens")
async def login(body: UserLoginRequest):
    """
    Log in with username and password to receive access and refresh tokens.
    """
    user = _users_db.get(body.username)
    if user is None or not verify_password(body.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    token_data = {"sub": body.username}
    return {
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type": "bearer",
    }


@router.get("/me", summary="Get current user profile")
async def get_me(username: str):
    """
    Return the profile of the currently authenticated user.
    (Requires valid JWT — wire up `get_current_user` dependency in production.)
    """
    user = _users_db.get(username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return {
        "username": user["username"],
        "email": user["email"],
        "full_name": user["full_name"],
        "is_active": user["is_active"],
    }
