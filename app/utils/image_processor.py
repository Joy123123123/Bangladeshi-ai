"""
Image Processor

Pillow-based image compression for the Data Saver mode.
Reduces image file sizes for low-bandwidth mobile users in Bangladesh.
"""

import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def compress_image(
    image_bytes: bytes,
    max_width: int = 640,
    quality: int = 60,
    grayscale: bool = False,
    output_format: str = "JPEG",
    max_size_bytes: int = 200_000,
) -> bytes:
    """
    Compress an image to reduce bandwidth usage.

    Args:
        image_bytes:    Raw image bytes (JPEG, PNG, WebP, etc.)
        max_width:      Resize so width ≤ max_width (preserves aspect ratio).
        quality:        JPEG/WebP quality (1–95). Lower = smaller file.
        grayscale:      Convert to grayscale for extra savings.
        output_format:  Output format – "JPEG" or "WEBP".
        max_size_bytes: If still too large after first compression, reduce quality further.

    Returns:
        Compressed image bytes, or original bytes if Pillow is unavailable.
    """
    try:
        from PIL import Image
    except ImportError:
        logger.warning("Pillow not installed – returning original image bytes.")
        return image_bytes

    try:
        image = Image.open(io.BytesIO(image_bytes))

        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        if grayscale:
            image = image.convert("L").convert("RGB")

        if image.width > max_width:
            ratio = max_width / image.width
            new_height = int(image.height * ratio)
            image = image.resize((max_width, new_height), Image.LANCZOS)

        buf = io.BytesIO()
        image.save(buf, format=output_format, quality=quality, optimize=True)
        compressed = buf.getvalue()

        if len(compressed) > max_size_bytes:
            buf = io.BytesIO()
            image.save(buf, format=output_format, quality=40, optimize=True)
            compressed = buf.getvalue()

        original_kb = len(image_bytes) / 1024
        compressed_kb = len(compressed) / 1024
        logger.info("Image: %.1f KB → %.1f KB (%.0f%% reduction)",
                    original_kb, compressed_kb,
                    (1 - compressed_kb / original_kb) * 100 if original_kb else 0)
        return compressed

    except Exception as exc:
        logger.error("Image compression failed: %s", exc)
        return image_bytes


def compress_image_base64(
    image_base64: str,
    max_width: int = 640,
    quality: int = 60,
    grayscale: bool = False,
) -> str:
    """Accept and return base64-encoded image strings."""
    import base64
    raw = base64.b64decode(image_base64)
    compressed = compress_image(raw, max_width=max_width, quality=quality, grayscale=grayscale)
    return base64.b64encode(compressed).decode()


def to_grayscale_base64(image_base64: str) -> str:
    """Convert base64 image to grayscale and return base64."""
    return compress_image_base64(image_base64, grayscale=True, quality=80)
