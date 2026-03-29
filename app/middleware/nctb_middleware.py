"""
NCTB Middleware

Extracts NCTB parameters (class, subject, board) from request headers or
query parameters and attaches them to the request state for use by
downstream handlers.
"""

import logging
from typing import Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import settings

logger = logging.getLogger(__name__)

# Header names used by the frontend to pass NCTB context
HEADER_CLASS_LEVEL = "X-NCTB-Class"
HEADER_SUBJECT = "X-NCTB-Subject"
HEADER_BOARD = "X-NCTB-Board"
HEADER_EXAM_TYPE = "X-NCTB-Exam-Type"


class NCTBMiddleware(BaseHTTPMiddleware):
    """
    Extract and validate NCTB context headers.

    Attaches the following to request.state:
      - nctb_class_level: Optional[int]
      - nctb_subject: Optional[str]
      - nctb_board: Optional[str]
      - nctb_exam_type: Optional[str]
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Extract NCTB headers
        class_level = self._parse_class_level(request.headers.get(HEADER_CLASS_LEVEL))
        subject = self._parse_subject(request.headers.get(HEADER_SUBJECT))
        board = self._parse_board(request.headers.get(HEADER_BOARD))
        exam_type = request.headers.get(HEADER_EXAM_TYPE)

        # Attach to request state
        request.state.nctb_class_level = class_level
        request.state.nctb_subject = subject
        request.state.nctb_board = board
        request.state.nctb_exam_type = exam_type

        if class_level or subject:
            logger.debug(
                "NCTB context | class=%s | subject=%s | board=%s | exam=%s",
                class_level,
                subject,
                board,
                exam_type,
            )

        response = await call_next(request)
        return response

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    def _parse_class_level(self, value: Optional[str]) -> Optional[int]:
        if value is None:
            return None
        try:
            class_int = int(value)
            if class_int in settings.SUPPORTED_CLASSES:
                return class_int
            logger.warning("Unsupported class level in header: %s", value)
        except ValueError:
            logger.warning("Invalid class level header value: %s", value)
        return None

    def _parse_subject(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        lower = value.lower()
        if lower in settings.SUPPORTED_SUBJECTS:
            return lower
        logger.warning("Unsupported subject in header: %s", value)
        return None

    def _parse_board(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if value in settings.SUPPORTED_BOARDS:
            return value
        logger.warning("Unsupported board in header: %s", value)
        return None
