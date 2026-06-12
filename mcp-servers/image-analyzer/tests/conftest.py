"""Pytest configuration and shared fixtures for image-analyzer tests."""

import struct
import zlib
from pathlib import Path

import pytest


def _make_1x1_png(color: tuple[int, int, int] = (255, 0, 0)) -> bytes:
    """Generate a minimal valid 1x1 PNG in memory.

    Args:
        color: RGB tuple for the single pixel.

    Returns:
        Raw PNG bytes.
    """
    # PNG signature
    sig = b"\x89PNG\r\n\x1a\n"

    def chunk(tag: bytes, data: bytes) -> bytes:
        length = struct.pack(">I", len(data))
        crc = struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return length + tag + data + crc

    # IHDR: 1x1, 8-bit RGB
    ihdr_data = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    ihdr = chunk(b"IHDR", ihdr_data)

    # IDAT: filter byte 0x00 + RGB pixel, compressed
    raw_row = bytes([0, color[0], color[1], color[2]])
    compressed = zlib.compress(raw_row)
    idat = chunk(b"IDAT", compressed)

    # IEND
    iend = chunk(b"IEND", b"")

    return sig + ihdr + idat + iend


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Return the fixtures directory path."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session", autouse=True)
def generate_fixtures(fixtures_dir: Path) -> None:
    """Generate test fixture files before running tests."""
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    # Two 1x1 PNG screenshots
    (fixtures_dir / "screen-01.png").write_bytes(_make_1x1_png((255, 0, 0)))
    (fixtures_dir / "screen-02.png").write_bytes(_make_1x1_png((0, 255, 0)))

    # One markdown description file (> 200 chars to test truncation)
    long_text = (
        "# Screen Description\n\n"
        "This is a description of the login screen. "
        "The user sees a form with username and password fields. "
        "There is a submit button labelled 'Sign In'. "
        "A 'Forgot password?' link appears below the form. "
        "The header shows the product logo on the left.\n"
    )
    (fixtures_dir / "screens-description.md").write_text(long_text, encoding="utf-8")


@pytest.fixture
def fixtures_path(fixtures_dir: Path) -> Path:
    """Return the fixtures directory (alias used in tests)."""
    return fixtures_dir


@pytest.fixture
def empty_dir(tmp_path: Path) -> Path:
    """Return a temporary empty directory."""
    d = tmp_path / "empty_screenshots"
    d.mkdir()
    return d
