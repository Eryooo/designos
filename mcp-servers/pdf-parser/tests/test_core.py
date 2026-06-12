"""Unit tests for core PDF parsing logic."""

import sys
from pathlib import Path

import pytest

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import PdfParseError, parse_pdf
from schemas import PdfContent, Section


def test_parse_sample_prd(sample_prd_path: Path) -> None:
    """Test parsing a well-structured PRD PDF."""
    result = parse_pdf(sample_prd_path)

    assert isinstance(result, PdfContent)
    assert result.metadata.page_count > 0
    assert len(result.sections) > 0
    assert result.raw_text.strip() != ""

    # Check that sections were extracted
    section_titles = [s.title for s in result.sections]
    assert any("产品概述" in title or "1." in title for title in section_titles)

    # Check section structure
    for section in result.sections:
        assert isinstance(section, Section)
        assert section.title.strip() != ""
        assert section.page >= 1
        assert section.page <= result.metadata.page_count


def test_parse_empty_pdf(empty_pdf_path: Path) -> None:
    """Test parsing an empty PDF returns empty sections."""
    with pytest.raises(PdfParseError) as exc_info:
        parse_pdf(empty_pdf_path)

    assert "no text layer" in str(exc_info.value).lower()
    assert exc_info.value.path == empty_pdf_path


def test_parse_scanned_pdf(scanned_pdf_path: Path) -> None:
    """Test parsing a scanned PDF (no text layer) raises PdfParseError."""
    with pytest.raises(PdfParseError) as exc_info:
        parse_pdf(scanned_pdf_path)

    assert "no text layer" in str(exc_info.value).lower()
    assert exc_info.value.path == scanned_pdf_path


def test_parse_nonexistent_file() -> None:
    """Test parsing a non-existent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        parse_pdf(Path("/nonexistent/file.pdf"))


def test_section_extraction_numbered(sample_prd_path: Path) -> None:
    """Test that numbered sections (1., 2.1., etc.) are correctly extracted."""
    result = parse_pdf(sample_prd_path)

    # Should have sections with numbered titles
    numbered_sections = [
        s for s in result.sections
        if any(s.title.startswith(prefix) for prefix in ["1.", "2.", "3."])
    ]
    assert len(numbered_sections) > 0


def test_section_extraction_chinese_chapters(sample_prd_path: Path) -> None:
    """Test that Chinese chapter headings (第X章) are correctly extracted."""
    result = parse_pdf(sample_prd_path)

    # Should have section with Chinese chapter format
    chinese_sections = [
        s for s in result.sections
        if "第" in s.title and "章" in s.title
    ]
    assert len(chinese_sections) > 0


def test_metadata_extraction(sample_prd_path: Path) -> None:
    """Test that PDF metadata is correctly extracted."""
    result = parse_pdf(sample_prd_path)

    assert result.metadata.page_count > 0
    # Title and author may be None if not set in PDF metadata
    assert result.metadata.title is None or isinstance(result.metadata.title, str)
    assert result.metadata.author is None or isinstance(result.metadata.author, str)


def test_raw_text_extraction(sample_prd_path: Path) -> None:
    """Test that raw text is extracted and non-empty."""
    result = parse_pdf(sample_prd_path)

    assert result.raw_text.strip() != ""
    assert "产品" in result.raw_text or "PDF" in result.raw_text


def test_section_content_not_empty(sample_prd_path: Path) -> None:
    """Test that extracted sections have non-empty content."""
    result = parse_pdf(sample_prd_path)

    # At least some sections should have content
    sections_with_content = [s for s in result.sections if s.content.strip()]
    assert len(sections_with_content) > 0


def test_pdf_parse_error_attributes() -> None:
    """Test PdfParseError has correct attributes."""
    path = Path("/test/file.pdf")
    error = PdfParseError("Test error", path)

    assert error.message == "Test error"
    assert error.path == path
    assert "Test error" in str(error)
    assert str(path) in str(error)
