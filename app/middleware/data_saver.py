"""
Data Saver Middleware

Compresses images and truncates oversized responses for low-bandwidth
users on 2G/3G connections in Bangladesh.
"""

import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Header sent by the frontend to request low-data mode
HEADER_DATA_SAVER = "X-Data-Saver"


class DataSaverMiddleware(BaseHTTPMiddleware):
    """
    Detect low-data mode from request headers and attach the flag to
    request.state so downstream handlers can adjust response verbosity.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        data_saver = request.headers.get(HEADER_DATA_SAVER, "").lower() in ("1", "true", "yes")
        request.state.data_saver = data_saver

        if data_saver:
            logger.debug("Data saver mode active for %s", request.url.path)

        response = await call_next(request)
        return response
