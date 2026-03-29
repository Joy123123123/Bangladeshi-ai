"""Tests for backend/app/middleware/data_saver.py – image compression utility."""
import sys
import os
import io
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from PIL import Image

from backend.app.middleware.data_saver import compress_image


def _create_test_image(path: str, width: int = 200, height: int = 200, mode: str = "RGB") -> None:
    """Create a simple solid-colour JPEG test image at *path*."""
    img = Image.new(mode, (width, height), color=(100, 150, 200))
    img.save(path, "JPEG")


class TestCompressImage:
    """Happy-path tests for compress_image."""

    def test_output_file_is_created(self, tmp_path):
        """compress_image should create the output file."""
        src = str(tmp_path / "src.jpg")
        dst = str(tmp_path / "dst.jpg")
        _create_test_image(src)
        compress_image(src, dst)
        assert os.path.exists(dst)

    def test_output_is_valid_image(self, tmp_path):
        """The compressed output should be a valid, openable image."""
        src = str(tmp_path / "src.jpg")
        dst = str(tmp_path / "dst.jpg")
        _create_test_image(src)
        compress_image(src, dst)
        img = Image.open(dst)
        assert img is not None

    def test_output_is_jpeg_format(self, tmp_path):
        """compress_image should always produce a JPEG output file."""
        src = str(tmp_path / "src.jpg")
        dst = str(tmp_path / "dst.jpg")
        _create_test_image(src)
        compress_image(src, dst)
        img = Image.open(dst)
        assert img.format == "JPEG"

    def test_default_quality_reduces_file_size(self, tmp_path):
        """Default quality=5 should produce a file smaller than the original."""
        src = str(tmp_path / "src.jpg")
        dst = str(tmp_path / "dst.jpg")
        # Use a larger image with more detail to make the size difference visible.
        img = Image.new("RGB", (800, 800), color=(0, 128, 255))
        img.save(src, "JPEG", quality=95)
        original_size = os.path.getsize(src)
        compress_image(src, dst)
        compressed_size = os.path.getsize(dst)
        assert compressed_size <= original_size

    def test_custom_quality_is_respected(self, tmp_path):
        """Higher quality value should generally produce a larger file than lower quality."""
        src = str(tmp_path / "src.jpg")
        dst_low = str(tmp_path / "dst_low.jpg")
        dst_high = str(tmp_path / "dst_high.jpg")
        img = Image.new("RGB", (400, 400), color=(50, 100, 200))
        img.save(src, "JPEG", quality=90)
        compress_image(src, dst_low, quality=1)
        compress_image(src, dst_high, quality=95)
        assert os.path.getsize(dst_high) >= os.path.getsize(dst_low)

    def test_output_dimensions_match_input(self, tmp_path):
        """compress_image should not resize the image."""
        src = str(tmp_path / "src.jpg")
        dst = str(tmp_path / "dst.jpg")
        _create_test_image(src, width=320, height=240)
        compress_image(src, dst)
        img = Image.open(dst)
        assert img.size == (320, 240)

    def test_output_overwrites_existing_file(self, tmp_path):
        """compress_image should silently overwrite an existing output file."""
        src = str(tmp_path / "src.jpg")
        dst = str(tmp_path / "dst.jpg")
        _create_test_image(src)
        # Create a dummy output file first.
        with open(dst, "wb") as f:
            f.write(b"dummy")
        compress_image(src, dst)
        img = Image.open(dst)
        assert img.format == "JPEG"

    def test_quality_boundary_minimum(self, tmp_path):
        """Quality=1 (minimum) should still produce a valid image."""
        src = str(tmp_path / "src.jpg")
        dst = str(tmp_path / "dst.jpg")
        _create_test_image(src)
        compress_image(src, dst, quality=1)
        img = Image.open(dst)
        assert img.format == "JPEG"

    def test_quality_boundary_maximum(self, tmp_path):
        """Quality=95 (near maximum) should produce a valid image."""
        src = str(tmp_path / "src.jpg")
        dst = str(tmp_path / "dst.jpg")
        _create_test_image(src)
        compress_image(src, dst, quality=95)
        img = Image.open(dst)
        assert img.format == "JPEG"

    def test_compress_png_input(self, tmp_path):
        """compress_image should also handle PNG input files."""
        src = str(tmp_path / "src.png")
        dst = str(tmp_path / "dst.jpg")
        img = Image.new("RGB", (100, 100), color=(255, 0, 0))
        img.save(src, "PNG")
        compress_image(src, dst)
        result = Image.open(dst)
        assert result.format == "JPEG"

    def test_compress_returns_none(self, tmp_path):
        """compress_image should have no explicit return value (returns None)."""
        src = str(tmp_path / "src.jpg")
        dst = str(tmp_path / "dst.jpg")
        _create_test_image(src)
        result = compress_image(src, dst)
        assert result is None


class TestCompressImageErrors:
    """Error-handling tests for compress_image."""

    def test_missing_input_file_raises(self, tmp_path):
        """compress_image should raise an error when the input file does not exist."""
        src = str(tmp_path / "nonexistent.jpg")
        dst = str(tmp_path / "dst.jpg")
        with pytest.raises((FileNotFoundError, OSError)):
            compress_image(src, dst)

    def test_invalid_input_raises(self, tmp_path):
        """compress_image should raise when the input file is not a valid image."""
        src = str(tmp_path / "bad.jpg")
        dst = str(tmp_path / "dst.jpg")
        with open(src, "wb") as f:
            f.write(b"not an image")
        with pytest.raises(Exception):
            compress_image(src, dst)
