"""Pydantic schemas for excel-builder MCP server.

Reuses the Issue type from kernel/contracts/schemas.py for type safety.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class BuildReportRequest(BaseModel):
    """Request payload for build_issue_report tool."""

    issues: list[dict] = Field(
        ...,
        description="List of Issue objects serialized as dicts.",
    )
    output_path: str = Field(
        ...,
        description="Absolute path where the Excel file should be written.",
    )
    template: str = Field(
        ...,
        description="Report template: 'uxeval', 'design-acceptance', or 'competitor'.",
    )


class BuildReportResponse(BaseModel):
    """Response payload for build_issue_report tool."""

    path: str = Field(..., description="Absolute path to the generated Excel file.")
    sheet_count: int = Field(..., description="Number of sheets in the workbook.")


__all__ = ["BuildReportRequest", "BuildReportResponse"]
