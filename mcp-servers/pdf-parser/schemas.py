"""Pydantic models for PDF parsing."""

from pydantic import BaseModel, Field


class Section(BaseModel):
    """A section extracted from a PDF document.

    Attributes:
        title: Section heading text
        content: Full text content of the section
        page: Starting page number (1-indexed)
    """
    title: str = Field(description="Section heading text")
    content: str = Field(description="Full text content of the section")
    page: int = Field(ge=1, description="Starting page number (1-indexed)")


class PdfMetadata(BaseModel):
    """Metadata extracted from a PDF document.

    Attributes:
        page_count: Total number of pages
        title: Document title from metadata (if available)
        author: Document author from metadata (if available)
    """
    page_count: int = Field(ge=0, description="Total number of pages")
    title: str | None = Field(default=None, description="Document title")
    author: str | None = Field(default=None, description="Document author")


class PdfContent(BaseModel):
    """Complete parsed content from a PDF document.

    Attributes:
        sections: List of extracted sections with titles and content
        metadata: Document metadata
        raw_text: Complete raw text extracted from all pages
    """
    sections: list[Section] = Field(default_factory=list, description="Extracted sections")
    metadata: PdfMetadata = Field(description="Document metadata")
    raw_text: str = Field(default="", description="Complete raw text from all pages")
