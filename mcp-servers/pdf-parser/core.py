"""Core PDF parsing logic (pure functions, no MCP dependencies)."""

import re
from pathlib import Path

import pdfplumber
from pdfminer.pdfparser import PDFSyntaxError
from schemas import PdfContent, PdfMetadata, Section


class PdfParseError(Exception):
    """Error raised when PDF parsing fails.

    Attributes:
        message: Human-readable error description
        path: Path to the PDF file that failed to parse
    """

    def __init__(self, message: str, path: Path | str) -> None:
        self.message = message
        self.path = Path(path)
        super().__init__(f"{message}: {self.path}")


def _is_section_heading(line: str, font_size: float | None = None) -> bool:
    """Heuristic to detect if a line is a section heading.

    Checks for common heading patterns:
    - Numbered sections: "1.", "1.1.", "1.1.1."
    - Chinese chapters: "第X章", "第X节"
    - Roman numerals: "一、", "二、"
    - All caps short lines (< 50 chars)

    Args:
        line: Text line to check
        font_size: Font size if available (larger fonts indicate headings)

    Returns:
        True if line appears to be a section heading
    """
    line = line.strip()
    if not line or len(line) > 100:
        return False

    # Pattern 1: Numbered sections (1. / 1.1. / 1.1.1.)
    if re.match(r"^\d+(\.\d+)*\.?\s+\S", line):
        return True

    # Pattern 2: Chinese chapters/sections
    if re.match(r"^第[一二三四五六七八九十\d]+[章节部分]\s*[:：]?\s*\S", line):
        return True

    # Pattern 3: Chinese numerals with punctuation
    if re.match(r"^[一二三四五六七八九十]+[、．.]\s*\S", line):
        return True

    # Pattern 4: Short all-caps lines (likely headings)
    if line.isupper() and len(line) < 50:
        return True

    # Pattern 5: Font size heuristic (if available)
    if font_size and font_size > 12:
        return True

    return False


def _extract_sections(pages_text: list[tuple[int, str]]) -> list[Section]:
    """Extract sections from page texts using heuristics.

    Args:
        pages_text: List of (page_number, text) tuples

    Returns:
        List of Section objects with title, content, and page number
    """
    sections: list[Section] = []
    current_title: str | None = None
    current_content: list[str] = []
    current_page: int = 1

    for page_num, text in pages_text:
        lines = text.split("\n")

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            if _is_section_heading(stripped):
                # Save previous section if exists
                if current_title:
                    sections.append(
                        Section(
                            title=current_title,
                            content="\n".join(current_content).strip(),
                            page=current_page,
                        )
                    )

                # Start new section
                current_title = stripped
                current_content = []
                current_page = page_num
            else:
                # Accumulate content
                if current_title:
                    current_content.append(stripped)

    # Save last section
    if current_title:
        sections.append(
            Section(
                title=current_title,
                content="\n".join(current_content).strip(),
                page=current_page,
            )
        )

    return sections


def parse_pdf(path: Path | str) -> PdfContent:
    """Parse a PDF file and extract structured content.

    Extracts sections, metadata, and raw text from a PDF document.
    Uses heuristics to identify section headings based on formatting
    and common patterns (numbered sections, Chinese chapters, etc.).

    Args:
        path: Path to the PDF file

    Returns:
        PdfContent object with sections, metadata, and raw text

    Raises:
        PdfParseError: If the PDF cannot be opened, is empty, or has no text layer
        FileNotFoundError: If the file does not exist
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")

    try:
        with pdfplumber.open(path) as pdf:
            # Extract metadata
            metadata = PdfMetadata(
                page_count=len(pdf.pages),
                title=pdf.metadata.get("Title"),
                author=pdf.metadata.get("Author"),
            )

            # Extract text from all pages
            pages_text: list[tuple[int, str]] = []
            raw_text_parts: list[str] = []

            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text:
                    pages_text.append((i, text))
                    raw_text_parts.append(text)

            raw_text = "\n\n".join(raw_text_parts)

            # Check if PDF has text layer
            if not raw_text.strip():
                raise PdfParseError(
                    "PDF has no text layer (likely a scanned document)", path
                )

            # Extract sections
            sections = _extract_sections(pages_text)

            return PdfContent(
                sections=sections,
                metadata=metadata,
                raw_text=raw_text,
            )

    except PDFSyntaxError as e:
        raise PdfParseError(f"Invalid PDF format: {e}", path) from e
    except Exception as e:
        if isinstance(e, (PdfParseError, FileNotFoundError)):
            raise
        raise PdfParseError(f"Failed to parse PDF: {e}", path) from e
