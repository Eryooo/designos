"""Data models for playwright-driver MCP server."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SelectorType(str, Enum):
    CSS = "css"
    TEXT = "text"
    ROLE = "role"


class ActionType(str, Enum):
    NAVIGATE = "navigate"
    CLICK = "click"
    FILL = "fill"
    SCREENSHOT = "screenshot"
    GET_STATE = "get_state"
    WAIT = "wait"
    SWITCH_PAGE = "switch_page"
    SWITCH_FRAME = "switch_frame"
    EXTRACT_DOM = "extract_dom"


class ScriptStep(BaseModel):
    """A single step in a JSON execution script."""

    model_config = ConfigDict(frozen=True)

    step: int
    action: ActionType
    url: str | None = None
    selector: str | None = None
    selector_type: SelectorType = SelectorType.CSS
    value: str | None = None
    name: str | None = None
    full_page: bool = True
    wait_after_ms: int = 0
    page_index: int | None = None
    frame_selector: str | None = None
    save_as: str | None = None


class EvaluationScript(BaseModel):
    """Complete JSON execution script for a task."""

    task_id: str
    task_title: str
    steps: list[ScriptStep]


class PageState(BaseModel):
    """Snapshot of current page state."""

    url: str
    title: str
    dom_text: str = Field(default="", description="Visible text content")
    visible_elements: list[dict[str, Any]] = Field(default_factory=list)
    page_index: int = 0
    page_count: int = 1
    frame_index: int = 0
    frame_count: int = 1


class SessionInfo(BaseModel):
    """Browser session metadata."""

    session_id: str
    user_data_dir: str
    page_state: PageState


class StepEvidence(BaseModel):
    """Evidence collected from a single step execution."""

    step: int
    action: ActionType
    url: str
    title: str
    screenshot_path: str | None = None
    dom_snapshot: dict[str, Any] | None = None
    page_state: PageState | None = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    confidence: str = "ground_truth"
    evidence_basis: list[str] = Field(default_factory=lambda: ["url", "dom", "screenshot"])
    verification_gap: list[str] = Field(default_factory=list)


class StepResult(BaseModel):
    """Result of executing a single script step."""

    step: int
    action: ActionType
    success: bool
    error: str | None = None
    evidence: StepEvidence | None = None


class ExecutionResult(BaseModel):
    """Result of executing a complete evaluation script."""

    task_id: str
    task_title: str
    status: str = Field(description="completed | partial | failed")
    steps_total: int
    steps_succeeded: int
    steps_failed: int
    evidence: list[StepEvidence] = Field(default_factory=list)
    errors: list[dict[str, Any]] = Field(default_factory=list)
