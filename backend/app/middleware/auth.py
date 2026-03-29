"""
JWT authentication middleware / dependency.

Use `get_current_user` as a FastAPI dependency on protected routes.
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.auth_service import decode_token

_security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_security),
) -> dict:
    """
    Require a valid JWT Bearer token.

    Raises:
        HTTPException 401 if the token is missing or invalid.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_security),
) -> Optional[dict]:
    """
    Optionally authenticate — returns None for unauthenticated requests
    instead of raising an error.
    """
    if credentials is None:
        return None
    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        return None
    return payload
