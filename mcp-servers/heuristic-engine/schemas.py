"""Pydantic schemas for the heuristic-engine MCP server.

Mirrors the canonical kernel contracts (``kernel.contracts.schemas``) but
keeps a local copy so the MCP server can run as a standalone uv project
without importing the full DesignOS kernel package.

Field semantics must stay aligned with ``docs/schemas/output-types.md``;
when in doubt the kernel contracts win.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Enums (mirrored from kernel.contracts.enums)
# ---------------------------------------------------------------------------


SeverityLevel = Literal["critical", "major", "minor", "suggestion"]
"""Severity grade reported on every issue. Mirrors ``SeverityLevel`` enum."""

DetectorMode = Literal["web", "client"]
"""Skill execution mode. ``web`` adds DOM snapshots; ``client`` is screenshot-only."""

IssueSource = Literal["rule", "llm_judge"]
"""Provenance of a raw issue: deterministic rule engine or LLM vision judge."""


# ---------------------------------------------------------------------------
# Domain inputs
# ---------------------------------------------------------------------------


class ScreenshotRef(BaseModel):
    """Reference to a single screenshot evaluated by the engine."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Screenshot identifier (e.g. 'S-001').")
    path: Path = Field(..., description="Filesystem path to the screenshot image.")
    flow: str = Field(
        default="",
        description="Flow / journey-stage name this screenshot belongs to.",
    )
    region: str = Field(
        default="",
        description="Optional UI region tag (e.g. 'header', 'detail-drawer').",
    )
    page_url: str = Field(
        default="",
        description="Source URL when captured from a web app (web mode only).",
    )
    note: str = Field(default="", description="Free-form annotation.")


class HeuristicPrinciple(BaseModel):
    """A single heuristic evaluation principle (Nielsen-style or custom)."""

    id: str = Field(..., description="Principle identifier (e.g. 'H1').")
    name: str = Field(..., description="Short name shown in reports.")
    description: str = Field(..., description="Full principle description.")
    source: str = Field(
        default="",
        description="Where the principle came from (paper / book / internal doc).",
    )


class TaskItem(BaseModel):
    """A single task entry in the user-task checklist."""

    id: str = Field(..., description="Task identifier (e.g. 'T-001').")
    title: str = Field(..., description="Short task name.")
    description: str = Field(default="", description="What the user is trying to accomplish.")
    journey_stage: str = Field(
        default="",
        description="Owning journey-stage label.",
    )
    role: str = Field(default="", description="User role performing this task.")


class TaskChecklist(BaseModel):
    """The active task checklist passed to the engine."""

    tasks: list[TaskItem] = Field(default_factory=list, description="Ordered task list.")
    journey_summary: str = Field(
        default="",
        description="One-paragraph summary of the user journey for LLM context.",
    )


class DomNode(BaseModel):
    """A simplified DOM node captured by the runner (web mode only)."""

    tag: str = Field(..., description="Element tag (e.g. 'button', 'input').")
    role: str = Field(default="", description="ARIA role attribute, if present.")
    text: str = Field(default="", description="Visible text content.")
    placeholder: str = Field(default="", description="Placeholder attribute for form fields.")
    aria_label: str = Field(default="", description="aria-label attribute, if present.")
    classes: list[str] = Field(default_factory=list, description="CSS class tokens.")
    attrs: dict[str, str] = Field(
        default_factory=dict,
        description="Other attributes (data-*, type, name, …).",
    )


class DomSnapshot(BaseModel):
    """Per-screenshot DOM snapshot used by the rule engine in web mode."""

    screenshot_id: str = Field(..., description="ScreenshotRef.id this snapshot belongs to.")
    nodes: list[DomNode] = Field(default_factory=list, description="Captured DOM nodes.")
    has_loading_indicator: bool = Field(
        default=False,
        description="True when a spinner / progress indicator was detected.",
    )
    has_error_message: bool = Field(
        default=False,
        description="True when an error/notification element was detected.",
    )
    page_url: str = Field(default="", description="Source URL for this snapshot.")


# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------


class RawIssue(BaseModel):
    """A single experience issue produced by the engine.

    Constitution invariants (enforced in :mod:`core`):

    * ``evidence_refs`` must be non-empty (each id must reference a
      ``ScreenshotRef.id`` from the input).
    * ``severity`` must be a member of :data:`SeverityLevel`.
    * ``confidence`` is bounded in ``[0, 1]``.
    """

    title: str = Field(..., description="Short issue summary.")
    description: str = Field(..., description="Detailed issue description.")
    principle: str = Field(..., description="Heuristic principle id this violates.")
    severity: SeverityLevel = Field(..., description="Severity grade.")
    evidence_refs: list[str] = Field(
        ...,
        min_length=1,
        description="Screenshot ids backing this issue (constitution rule, non-empty).",
    )
    source: IssueSource = Field(..., description="Origin: rule engine or LLM judge.")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Detector confidence in [0, 1].",
    )
    suggestion: str = Field(default="", description="Optional fix recommendation.")
    user_impact: str = Field(default="", description="Optional user-impact statement.")


class DetectionSummary(BaseModel):
    """Aggregate counters returned alongside the raw issues."""

    total_issues: int = Field(..., ge=0, description="Total number of issues detected.")
    by_severity: dict[str, int] = Field(
        default_factory=dict,
        description="Count keyed by severity level.",
    )
    by_principle: dict[str, int] = Field(
        default_factory=dict,
        description="Count keyed by principle id.",
    )
    rule_hits: int = Field(default=0, ge=0, description="Issues raised by the rule engine.")
    llm_hits: int = Field(default=0, ge=0, description="Issues raised by the LLM judge.")


class DetectionResult(BaseModel):
    """Top-level response payload returned by the ``detect`` tool."""

    raw_issues: list[RawIssue] = Field(
        default_factory=list,
        description="Detected issues (rule + llm_judge).",
    )
    summary: DetectionSummary = Field(..., description="Aggregate counters.")


class DetectionRequest(BaseModel):
    """Top-level request payload accepted by the ``detect`` tool."""

    screenshots: list[ScreenshotRef] = Field(
        ...,
        min_length=1,
        description="Screenshots to evaluate.",
    )
    principles: list[HeuristicPrinciple] = Field(
        ...,
        min_length=1,
        description="Heuristic principles in scope.",
    )
    task_checklist: TaskChecklist = Field(
        default_factory=TaskChecklist,
        description="Task checklist supplying journey context.",
    )
    constitution: str = Field(
        default="",
        description="Skill evaluation constitution (constrains LLM judge).",
    )
    mode: DetectorMode = Field(
        default="client",
        description="Detector mode; web requires dom_data.",
    )
    dom_data: list[DomSnapshot] | None = Field(
        default=None,
        description="DOM snapshots, populated only in web mode.",
    )


__all__ = [
    "DetectionRequest",
    "DetectionResult",
    "DetectionSummary",
    "DetectorMode",
    "DomNode",
    "DomSnapshot",
    "HeuristicPrinciple",
    "IssueSource",
    "RawIssue",
    "ScreenshotRef",
    "SeverityLevel",
    "TaskChecklist",
    "TaskItem",
]
