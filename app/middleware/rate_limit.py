"""
Rate Limit Middleware

Per-user (by IP) rate limiting using Redis.
Falls back to allow-all if Redis is unavailable.
"""

import logging
from typing import Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from app.core.config import settings
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Limit each IP to RATE_LIMIT_REQUESTS requests per RATE_LIMIT_WINDOW seconds.
    Only applies to /api/ routes.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        key = f"ratelimit:{client_ip}"

        count = await cache_service.increment(key, ttl=settings.RATE_LIMIT_WINDOW)

        if count and count > settings.RATE_LIMIT_REQUESTS:
            logger.warning("Rate limit exceeded for IP: %s", client_ip)
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "detail": "অনুগ্রহ করে কিছুক্ষণ অপেক্ষা করুন। আপনি অনেক দ্রুত অনুরোধ করছেন।",
                    "retry_after": settings.RATE_LIMIT_WINDOW,
                },
                headers={"Retry-After": str(settings.RATE_LIMIT_WINDOW)},
            )

        response = await call_next(request)
        return response

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"
