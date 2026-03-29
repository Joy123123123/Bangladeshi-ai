"""
Rate limiting middleware using slowapi.

Provides per-IP rate limiting for public endpoints and
higher limits for authenticated users.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.utils.config import settings

# The limiter instance is shared across the application
limiter = Limiter(key_func=get_remote_address)

# Convenient limit strings built from config
ANONYMOUS_LIMIT = f"{settings.rate_limit_anonymous}/minute"
AUTHENTICATED_LIMIT = f"{settings.rate_limit_authenticated}/minute"
