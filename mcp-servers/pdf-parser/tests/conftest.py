"""Pytest configuration and shared fixtures."""

import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Return the fixtures directory path."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session", autouse=True)
def generate_fixtures(fixtures_dir: Path) -> None:
    """Generate test fixture PDFs before running tests."""
    import sys
    sys.path.insert(0, str(fixtures_dir))

    from generate import generate_sample_prd, generate_empty_pdf, generate_scanned_pdf

    generate_sample_prd(fixtures_dir / "sample-prd.pdf")
    generate_empty_pdf(fixtures_dir / "empty.pdf")
    generate_scanned_pdf(fixtures_dir / "scanned.pdf")


@pytest.fixture
def sample_prd_path(fixtures_dir: Path) -> Path:
    """Return path to sample PRD PDF."""
    return fixtures_dir / "sample-prd.pdf"


@pytest.fixture
def empty_pdf_path(fixtures_dir: Path) -> Path:
    """Return path to empty PDF."""
    return fixtures_dir / "empty.pdf"


@pytest.fixture
def scanned_pdf_path(fixtures_dir: Path) -> Path:
    """Return path to scanned PDF (no text layer)."""
    return fixtures_dir / "scanned.pdf"
