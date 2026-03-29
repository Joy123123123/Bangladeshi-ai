"""
Auth Middleware & Helpers

JWT-based authentication. Routes protected by the /api/v1/admin prefix
require a valid Bearer token. Public endpoints (/docs, /health, /api/v1/chat)
are accessible without authentication.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

logger = logging.getLogger(__name__)

# Public paths that don't require authentication
PUBLIC_PATHS = {
    "/",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/health",
    "/api/v1/chat/stream",
    "/api/v1/chat",
    "/api/v1/subjects",
    "/api/v1/classes",
    "/api/v1/study/stream",
    "/api/v1/admission/stream",
    "/api/v1/admission/strategy",
}

security = HTTPBearer(auto_error=False)


def _get_jose():
    try:
        from jose import jwt, JWTError
        return jwt, JWTError
    except ImportError:
        return None, None


def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    """Create a signed JWT access token."""
    jwt_mod, _ = _get_jose()
    if jwt_mod is None:
        raise RuntimeError("python-jose is not installed")

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.JWT_EXPIRE_MINUTES
    )
    to_encode["exp"] = expire
    return jwt_mod.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token. Returns payload or None if invalid."""
    jwt_mod, JWTError = _get_jose()
    if jwt_mod is None:
        return None
    try:
        payload = jwt_mod.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except Exception:
        return None


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[dict]:
    """
    Dependency: returns the decoded token payload if a valid Bearer token is
    provided, otherwise None (allows anonymous access).
    """
    if credentials is None:
        return None
    return decode_access_token(credentials.credentials)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    """
    Dependency: requires a valid Bearer token. Raises 401 if missing/invalid.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload
