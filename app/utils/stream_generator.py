"""
Stream Generator

Server-Sent Events (SSE) chunk generator utilities.
"""

import asyncio
import json
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)


async def sse_generator(
    text_stream: AsyncGenerator[str, None],
    chunk_size: int = 50,
    data_saver_mode: bool = False,
) -> AsyncGenerator[bytes, None]:
    """
    Wrap an async text stream into an SSE-formatted byte generator.

    Each event is formatted as:
        data: {"content": "...", "done": false}\n\n

    The final event signals completion:
        data: [DONE]\n\n
    """
    effective_chunk_size = chunk_size // 2 if data_saver_mode else chunk_size
    buffer = ""

    try:
        async for text_chunk in text_stream:
            buffer += text_chunk

            while len(buffer) >= effective_chunk_size:
                emit, buffer = buffer[:effective_chunk_size], buffer[effective_chunk_size:]
                payload = json.dumps({"content": emit, "done": False}, ensure_ascii=False)
                yield f"data: {payload}\n\n".encode("utf-8")

        if buffer:
            payload = json.dumps({"content": buffer, "done": False}, ensure_ascii=False)
            yield f"data: {payload}\n\n".encode("utf-8")

        yield b"data: [DONE]\n\n"

    except Exception as exc:
        logger.error("SSE stream error: %s", exc)
        error_payload = json.dumps(
            {"content": "", "done": True, "error": str(exc)},
            ensure_ascii=False,
        )
        yield f"data: {error_payload}\n\n".encode("utf-8")


async def collect_stream(
    text_stream: AsyncGenerator[str, None],
) -> str:
    """Collect all chunks from an async text stream into a single string."""
    parts: list[str] = []
    async for chunk in text_stream:
        parts.append(chunk)
    return "".join(parts)
