"""Pydantic schemas for excel-builder MCP server.

Reuses the Issue type from kernel/contracts/schemas.py for type safety.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BuildReportRequest(BaseModel):
    """Request payload for build_issue_report tool."""

    issues: list[dict[str, Any]] = Field(
        ...,
        description="List of Issue objects serialized as dicts.",
    )
    output_path: str | None = Field(
        default=None,
        description="Optional absolute path where the Excel workbook should be written.",
    )
    output_dir: str | None = Field(
        default=None,
        description="Optional directory used to derive stable issue_report/html/evidence paths.",
    )
    template: str = Field(
        default="uxeval",
        description="Report template: 'uxeval', 'design-acceptance', or 'competitor'.",
    )
    journey_map: Any = Field(default=None, description="Optional journey map context.")
    principles: Any = Field(default=None, description="Optional principles context.")


class AuditDeliveryRequest(BaseModel):
    """Request payload for deterministic delivery-audit packaging."""

    issues: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Main issue list proposed by Stage 6.",
    )
    unverified_issues: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Issues that Stage 6 already kept out of the main list.",
    )
    evidence_assessment: dict[str, Any] = Field(
        default_factory=dict,
        description="Runtime evidence sufficiency assessment from client-mode evidence analysis.",
    )
    delivery_assessment: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional Stage 6 self-reported delivery assessment for comparison only.",
    )
    output_dir: str = Field(
        ...,
        description="Absolute run output directory where the audit bundle should be written.",
    )


class ArtifactPayload(BaseModel):
    """Structured artifact metadata returned to the runtime."""

    id: str = Field(..., description="Stable artifact id matching the stage output name.")
    type: str = Field(..., description="Canonical output type consumed by the runtime.")
    path: str = Field(..., description="Absolute artifact path written by the tool.")
    format: str = Field(..., description="Physical artifact format.")
    summary: str = Field(default="", description="One-line artifact summary.")
    issue_count: int | None = Field(default=None, description="Issue count when relevant.")
    sheet_count: int | None = Field(default=None, description="Workbook sheet count when relevant.")
    file_count: int | None = Field(default=None, description="Directory file count when relevant.")


class BuildReportResponse(BaseModel):
    """Response payload for build_issue_report tool."""

    issue_report: ArtifactPayload = Field(..., description="Structured Excel report artifact.")
    html_report: ArtifactPayload = Field(..., description="Structured HTML report artifact.")
    evidence_pack: ArtifactPayload = Field(..., description="Structured evidence pack artifact.")


class AuditDeliveryResponse(BaseModel):
    """Response payload for audit_delivery_readiness tool."""

    audited_delivery_assessment: dict[str, Any] = Field(
        ...,
        description="Deterministic runtime verdict that Stage 7 must trust.",
    )
    delivery_audit_bundle: ArtifactPayload = Field(
        ...,
        description="Structured bounded fallback / audit package artifact.",
    )


__all__ = [
    "ArtifactPayload",
    "AuditDeliveryRequest",
    "AuditDeliveryResponse",
    "BuildReportRequest",
    "BuildReportResponse",
]
