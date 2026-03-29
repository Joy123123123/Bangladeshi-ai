"""
Data Saver Utilities

Provides image compression and response chunking helpers to reduce mobile
data usage for Bangladeshi students on 2G/3G connections.
"""

import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Image compression
# ---------------------------------------------------------------------------

def compress_image(
    image_bytes: bytes,
    max_width: int = 800,
    quality: int = 60,
    grayscale: bool = False,
    output_format: str = "JPEG",
) -> bytes:
    """
    Compress an image to reduce bandwidth usage.

    Args:
        image_bytes: Raw image bytes (JPEG, PNG, WebP, etc.)
        max_width:   Resize so width ≤ max_width (preserves aspect ratio).
        quality:     JPEG/WebP quality (1–95). Lower = smaller file.
        grayscale:   Convert to grayscale (further reduces size).
        output_format: Output format – "JPEG" or "WEBP".

    Returns:
        Compressed image bytes, or original bytes if Pillow is unavailable.
    """
    try:
        from PIL import Image  # type: ignore
    except ImportError:
        logger.warning("Pillow not installed – returning original image bytes.")
        return image_bytes

    try:
        image = Image.open(io.BytesIO(image_bytes))

        # Convert RGBA → RGB for JPEG compatibility
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        # Grayscale conversion
        if grayscale:
            image = image.convert("L").convert("RGB")

        # Resize if wider than max_width
        if image.width > max_width:
            ratio = max_width / image.width
            new_height = int(image.height * ratio)
            image = image.resize((max_width, new_height), Image.LANCZOS)

        output = io.BytesIO()
        image.save(output, format=output_format, quality=quality, optimize=True)
        compressed = output.getvalue()

        reduction = (1 - len(compressed) / len(image_bytes)) * 100
        logger.info(
            "Image compressed: %d → %d bytes (%.1f%% reduction)",
            len(image_bytes),
            len(compressed),
            reduction,
        )
        return compressed

    except Exception as exc:
        logger.error("Image compression failed: %s", exc)
        return image_bytes


def estimate_bandwidth_kb(image_bytes: bytes) -> float:
    """Return the approximate size of image_bytes in kilobytes."""
    return len(image_bytes) / 1024


# ---------------------------------------------------------------------------
# Response chunking
# ---------------------------------------------------------------------------

def chunk_text(text: str, chunk_size: int = 50) -> list[str]:
    """
    Split *text* into chunks of *chunk_size* characters.

    Useful for streaming responses character-by-character to simulate
    real-time output on low-bandwidth connections.
    """
    return [text[i: i + chunk_size] for i in range(0, len(text), chunk_size)]


async def stream_text_chunks(text: str, chunk_size: int = 50):
    """
    Async generator that yields text chunks with a tiny sleep between them.

    Yields:
        str: A chunk of text.
    """
    import asyncio
    for chunk in chunk_text(text, chunk_size):
        yield chunk
        await asyncio.sleep(0.01)  # allow event loop to process other tasks


# ---------------------------------------------------------------------------
# Bandwidth estimation helpers
# ---------------------------------------------------------------------------

def estimate_tokens(text: str) -> int:
    """Rough token count estimate (≈ 4 chars per token for Bengali text)."""
    return max(1, len(text) // 4)


def estimate_response_kb(text: str) -> float:
    """Estimate the response size in KB (UTF-8 encoded)."""
    return len(text.encode("utf-8")) / 1024
