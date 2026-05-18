"""Pydantic models for image-analyzer MCP server."""

from typing import Any

from pydantic import BaseModel, Field


class ScreenshotRef(BaseModel):
    """Reference to a single screenshot or screenshot description file.

    Attributes:
        id: Stable identifier like "S-001", "S-002", ...
        path: Absolute path to the file on disk
        flow: Associated task/journey name (M1: always None)
        description: For .md files, first 200 chars of content
    """

    id: str = Field(description="Stable identifier, e.g. 'S-001'")
    path: str = Field(description="Absolute file path")
    flow: str | None = Field(default=None, description="Associated task/journey (M1: None)")
    description: str | None = Field(
        default=None,
        description="For .md description files: first 200 chars of content",
    )


class LoadAnalyzeResult(BaseModel):
    """Result from load_and_analyze tool call.

    Attributes:
        screenshots: List of discovered ScreenshotRef objects
        image_analysis: Stub analysis dict with found_count, paths, mode
    """

    screenshots: list[ScreenshotRef] = Field(
        default_factory=list,
        description="Ordered list of discovered screenshot references",
    )
    image_analysis: dict[str, Any] = Field(
        description="M1 stub: {'found_count': N, 'paths': [...], 'mode': 'stub'}",
    )
