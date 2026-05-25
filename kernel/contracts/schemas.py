"""Pydantic v2 schemas for DesignOS kernel contracts.

These models are the single source of truth for every cross-module data
shape: pipeline configuration, runtime context, stage / workflow events,
LLM and MCP payloads, configuration trees, run manifests and the uxeval
domain entities (``Issue``, ``JourneyStage`` …).

All fields carry a ``Field(..., description=...)`` so docs generators and
LLM consumers can introspect them. Frozen models are used for value
objects that should never mutate after construction.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .enums import (
    CheckpointAction,
    ErrorCode,
    MCPTransport,
    Mode,
    OutputType,
    RunStatus,
    SeverityLevel,
    SkillType,
    StageStatus,
    StageType,
)

# ---------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------


class ErrorInfo(BaseModel):
    """Structured error payload embedded in stage / skill results."""

    model_config = ConfigDict(frozen=True)

    code: ErrorCode = Field(..., description="Canonical DesignOS error code.")
    message: str = Field(..., description="Human-readable error message.")
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional structured debug payload.",
    )


class ArtifactRef(BaseModel):
    """Reference to a file produced by a stage or skill run."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Stable id used for upstream references.")
    output_type: OutputType = Field(..., description="Canonical product type.")
    path: Path = Field(..., description="Path relative to the run output directory.")
    format: Literal["markdown", "xlsx", "html", "json", "directory"] = Field(
        ...,
        description="Physical artefact format.",
    )
    summary: str = Field(
        default="",
        description="One-line description rendered in the run manifest.",
    )


class RetryConfig(BaseModel):
    """Per-stage retry policy."""

    max_attempts: int = Field(
        default=2,
        ge=1,
        le=10,
        description="Maximum invocation attempts including the first call.",
    )
    backoff_seconds: float = Field(
        default=1.0,
        ge=0.0,
        description="Base backoff delay; effective delay is backoff * 2**(attempt-1).",
    )
    retry_on: list[ErrorCode] = Field(
        default_factory=list,
        description="Error codes that trigger a retry; empty means retry on any error.",
    )


# ---------------------------------------------------------------------------
# Pipeline & workflow configuration
# ---------------------------------------------------------------------------


class CheckpointConfig(BaseModel):
    """Definition of a pause point inside a pipeline."""

    id: str = Field(..., description="Checkpoint identifier (e.g. 'C1').")
    message: str = Field(..., description="Prompt shown to the user when paused.")
    allow: list[CheckpointAction] = Field(
        default_factory=lambda: [CheckpointAction.CONTINUE],
        description="Actions the user is allowed to take at this checkpoint.",
    )


class StageGateConfig(BaseModel):
    """Runtime quality or safety gate evaluated before a stage executes."""

    when: str = Field(
        ...,
        description="Conditional expression that triggers the gate when truthy.",
    )
    action: Literal["pause", "fail"] = Field(
        default="pause",
        description="Whether the gate pauses for user action or fails the stage immediately.",
    )
    checkpoint_id: str | None = Field(
        default=None,
        description="Checkpoint id surfaced when action == pause.",
    )
    message: str = Field(
        default="",
        description="User-facing gate summary shown when execution is paused or failed.",
    )
    status_reason_from: str | None = Field(
        default=None,
        description="Optional dotted path resolved from runtime state for a more specific pause reason.",
    )
    required_actions_from: str | None = Field(
        default=None,
        description="Optional dotted path resolved from runtime state for required follow-up actions.",
    )
    resume_from_stage: str | None = Field(
        default=None,
        description="Optional stage id to rewind to when resuming after this gate.",
    )


class StageConfig(BaseModel):
    """One node in a Pipeline Skill's execution graph."""

    id: str = Field(..., description="Stage identifier, unique within the pipeline.")
    type: StageType = Field(..., description="Execution shape (LLM / TOOL / COMPOSITE).")
    prompt: Path | None = Field(
        default=None,
        description="Path to the prompt file when type == LLM.",
    )
    mcp_server: str | None = Field(
        default=None,
        description="MCP server name when type == TOOL.",
    )
    mcp_tool: str | None = Field(
        default=None,
        description="MCP tool name on that server.",
    )
    inputs: list[str] = Field(
        default_factory=list,
        description="Variable names consumed from prior stages or upstream refs.",
    )
    outputs: list[str] = Field(
        default_factory=list,
        description="Variable names produced into the pipeline state.",
    )
    knowledge: list[Path] = Field(
        default_factory=list,
        description="Knowledge-base files lazy-loaded into the LLM context.",
    )
    only_when: str | None = Field(
        default=None,
        description="Conditional expression (e.g. \"mode == 'web'\").",
    )
    checkpoint: CheckpointConfig | None = Field(
        default=None,
        description="Optional checkpoint to pause after this stage.",
    )
    gate: StageGateConfig | None = Field(
        default=None,
        description="Optional runtime gate evaluated before this stage executes.",
    )
    retry: RetryConfig = Field(
        default_factory=RetryConfig,
        description="Retry policy applied to this stage.",
    )


class WorkflowStep(BaseModel):
    """A single step inside a Skill Group workflow definition."""

    type: Literal["sequential", "parallel"] = Field(
        ...,
        description="Whether sub-skills run sequentially or concurrently.",
    )
    sub_skills: list[str] = Field(
        ...,
        description="Sub-skill ids (within the owning Skill Group) to execute.",
        min_length=1,
    )
    on_failure: Literal["abort", "continue", "skip"] = Field(
        default="abort",
        description="How to handle a failing sub-skill in this step.",
    )


class WorkflowConfig(BaseModel):
    """Workflow definition consumed by :class:`IWorkflowOrchestrator`."""

    name: str = Field(..., description="Workflow identifier.")
    description: str = Field(..., description="Human-readable summary.")
    steps: list[WorkflowStep] = Field(
        ...,
        description="Ordered list of workflow steps.",
        min_length=1,
    )


# ---------------------------------------------------------------------------
# Configuration tree
# ---------------------------------------------------------------------------


class ExternalRequirementConfig(BaseModel):
    """Declarative preflight probe attached to a skill or MCP dependency."""

    command: str = Field(..., description="Shell command used as a preflight probe.")
    install_hint: str = Field(
        default="",
        description="User-facing install or remediation hint shown when the probe fails.",
    )
    required_when: str | None = Field(
        default=None,
        description="Conditional expression controlling when this probe is required.",
    )


class MCPServerConfig(BaseModel):
    """Connection settings for a single MCP server."""

    name: str = Field(..., description="Logical server name referenced by skills.")
    transport: MCPTransport = Field(
        default=MCPTransport.STDIO,
        description="Wire transport (stdio for built-ins, sse for browser tools).",
    )
    command: list[str] | None = Field(
        default=None,
        description="Command + args for stdio servers.",
    )
    url: str | None = Field(
        default=None,
        description="Endpoint URL for SSE servers.",
    )
    env: dict[str, str] = Field(
        default_factory=dict,
        description="Extra environment variables passed to the server process.",
    )
    builtin: bool = Field(
        default=True,
        description="True if maintained by DesignOS, false if user-installed.",
    )
    required_when: str | None = Field(
        default=None,
        description="Conditional expression controlling when this server is required.",
    )
    requires_external: list[ExternalRequirementConfig] = Field(
        default_factory=list,
        description="External commands or probes required before this server can run.",
    )


class GlobalConfig(BaseModel):
    """User-level configuration (``~/.designos/config.yaml``)."""

    primary_model: str = Field(
        default="claude-opus-4-7",
        description="Preferred LLM model identifier.",
    )
    fallback_model: str = Field(
        default="deepseek-v3",
        description="Fallback LLM model used when the primary fails.",
    )
    anthropic_base_url: str | None = Field(
        default=None,
        description="Optional Anthropic-compatible base URL (intranet proxies).",
    )
    memory_repo: str | None = Field(
        default=None,
        description="Git URL of the organisation memory repository.",
    )
    default_output_formats: list[Literal["markdown", "xlsx", "html", "json"]] = Field(
        default_factory=lambda: ["markdown", "xlsx", "html"],
        description="Default formats produced by the output renderer.",
    )
    auto_upstream_inject: bool = Field(
        default=True,
        description="Prompt the user to inject matching upstream products by default.",
    )


class ProjectConfig(BaseModel):
    """Project-level configuration (``designos.project.yaml``)."""

    name: str = Field(..., description="Project name.")
    created: datetime = Field(..., description="Project creation timestamp.")
    owner: str = Field(..., description="Project owner identifier.")
    business_unit: str = Field(default="", description="Owning business unit / team.")
    tags: list[str] = Field(default_factory=list, description="Free-form tags.")
    skills: dict[str, str] = Field(
        default_factory=dict,
        description="Locked skill versions, mapping skill name to semver range.",
    )


class SkillConfig(BaseModel):
    """Skill-level defaults, parsed from a skill's ``SKILL.md`` frontmatter."""

    name: str = Field(..., description="Skill name.")
    version: str = Field(..., description="Skill semver version.")
    skill_type: SkillType = Field(..., description="Pipeline or Group form factor.")
    supported_modes: list[str] = Field(
        default_factory=list,
        description="Mode ids the skill exposes; empty means single-mode.",
    )
    requires_kernel: str = Field(
        default=">=1.0.0,<2.0.0",
        description="Kernel version range required by this skill.",
    )
    mcp_servers: list[MCPServerConfig] = Field(
        default_factory=list,
        description="MCP servers the skill depends on.",
    )
    outputs: list["SkillOutputConfig"] = Field(
        default_factory=list,
        description="Runtime-declared artifact outputs surfaced by this skill.",
    )


class SkillOutputConfig(BaseModel):
    """Declared artifact contract for a skill output in ``SKILL.md``."""

    id: str = Field(..., description="Stable output id used in pipeline/runtime wiring.")
    type: OutputType = Field(..., description="Canonical output type exposed by the skill.")
    format: Literal["markdown", "xlsx", "html", "json", "directory"] = Field(
        ...,
        description="Physical artifact format.",
    )


SkillConfig.model_rebuild()


class DesignOSConfig(BaseModel):
    """Merged runtime configuration assembled by the kernel ConfigLoader.

    The merge order is documented in ``docs/architecture/02-Kernel-设计.md`` §7:
    CLI flags > project > user > .env.local > skill defaults > kernel defaults.
    """

    workspace: Path = Field(..., description="Absolute path to the active workspace.")
    global_config: GlobalConfig = Field(
        default_factory=GlobalConfig,
        description="Effective user-level configuration.",
    )
    project_config: ProjectConfig | None = Field(
        default=None,
        description="Project-level configuration, when invoked inside a project.",
    )
    skill_config: SkillConfig | None = Field(
        default=None,
        description="Active skill's metadata, populated after skill load.",
    )
    mcp_servers: dict[str, MCPServerConfig] = Field(
        default_factory=dict,
        description="Effective MCP server registry keyed by logical name.",
    )
    env: dict[str, str] = Field(
        default_factory=dict,
        description="Process environment snapshot (filtered to DESIGNOS_*).",
    )


# ---------------------------------------------------------------------------
# Runtime context, stage results, events
# ---------------------------------------------------------------------------


class SkillContext(BaseModel):
    """Container passed to every skill invocation by the kernel.

    Skills must treat this as read-mostly: mutate ``state`` for cross-stage
    bookkeeping but never reach into kernel internals. Clients (LLM / MCP /
    Memory) are injected via the kernel's runtime adapters, not via this
    Pydantic model, so the schema stays serialisable for checkpointing.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    workspace: Path = Field(..., description="Absolute path to the project workspace.")
    skill_name: str = Field(..., description="Active skill name.")
    skill_version: str = Field(..., description="Active skill semver version.")
    run_id: str = Field(..., description="Run identifier (e.g. '001-uxeval').")
    mode: Mode | None = Field(
        default=None,
        description="Execution mode chosen by the user, if the skill is multi-mode.",
    )
    config: DesignOSConfig = Field(..., description="Effective merged configuration.")
    upstream_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Products injected from upstream skill runs, keyed by inject_as.",
    )
    state: dict[str, Any] = Field(
        default_factory=dict,
        description="Mutable per-stage state shared across the pipeline.",
    )


class StageResult(BaseModel):
    """Outcome of a single stage execution."""

    stage_id: str = Field(..., description="Stage identifier from the pipeline.")
    status: StageStatus = Field(..., description="Terminal stage status.")
    outputs: dict[str, Any] = Field(
        default_factory=dict,
        description="Variables produced into the pipeline state.",
    )
    artifacts: list[ArtifactRef] = Field(
        default_factory=list,
        description="Persisted artefacts written by the stage.",
    )
    error: ErrorInfo | None = Field(
        default=None,
        description="Populated when status == FAILED.",
    )
    duration_ms: int = Field(
        default=0,
        ge=0,
        description="Wall-clock duration of the stage in milliseconds.",
    )
    started_at: datetime | None = Field(
        default=None,
        description="Stage start timestamp (UTC).",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="Stage completion timestamp (UTC).",
    )


class SkillResult(BaseModel):
    """Aggregate result returned by a skill invocation."""

    skill_name: str = Field(..., description="Skill that produced this result.")
    skill_version: str = Field(..., description="Skill version that ran.")
    status: RunStatus = Field(..., description="Lifecycle status of the run.")
    stages: list[StageResult] = Field(
        default_factory=list,
        description="Per-stage outcomes, in execution order.",
    )
    artifacts: list[ArtifactRef] = Field(
        default_factory=list,
        description="Aggregated artefacts produced by the run.",
    )
    paused_at_checkpoint: str | None = Field(
        default=None,
        description="Checkpoint id the run is paused at, when status == PAUSED.",
    )
    pause_kind: Literal["checkpoint", "gate"] | None = Field(
        default=None,
        description="Whether a paused run stopped at a normal checkpoint or a runtime gate.",
    )
    status_reason: str | None = Field(
        default=None,
        description="Human-readable reason for the current paused/failed state.",
    )
    required_actions: list[str] = Field(
        default_factory=list,
        description="Concrete next actions required before the run can continue safely.",
    )


class StageEvent(BaseModel):
    """Streaming event emitted by :class:`IPipelineEngine`."""

    kind: Literal["stage_started", "stage_completed", "stage_failed", "checkpoint", "error"]
    stage_id: str = Field(..., description="Stage that produced the event.")
    timestamp: datetime = Field(..., description="Event timestamp (UTC).")
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific structured data.",
    )


class WorkflowEvent(BaseModel):
    """Streaming event emitted by :class:`IWorkflowOrchestrator`."""

    kind: Literal[
        "step_started",
        "sub_skill_started",
        "sub_skill_completed",
        "sub_skill_failed",
        "step_completed",
    ]
    step_index: int = Field(..., ge=0, description="Workflow step index.")
    sub_skill: str | None = Field(
        default=None,
        description="Sub-skill id when the event is sub-skill-scoped.",
    )
    timestamp: datetime = Field(..., description="Event timestamp (UTC).")
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific structured data.",
    )


class CheckpointEvent(BaseModel):
    """Persistent record of a user decision at a checkpoint."""

    checkpoint_id: str = Field(..., description="Checkpoint identifier (e.g. 'C1').")
    decision: CheckpointAction = Field(..., description="User-selected action.")
    note: str = Field(default="", description="Free-form note from the user.")
    timestamp: datetime = Field(..., description="Decision timestamp (UTC).")


# ---------------------------------------------------------------------------
# LLM / MCP envelopes
# ---------------------------------------------------------------------------


class LLMResponse(BaseModel):
    """Normalised response returned by every :class:`ILLMClient`."""

    model_config = ConfigDict(frozen=True)

    text: str = Field(..., description="Full text completion.")
    model: str = Field(..., description="Concrete model identifier that served the request.")
    input_tokens: int = Field(default=0, ge=0, description="Prompt token count.")
    output_tokens: int = Field(default=0, ge=0, description="Completion token count.")
    finish_reason: Literal["stop", "length", "tool_use", "error"] = Field(
        default="stop",
        description="Why the model stopped generating.",
    )
    raw: dict[str, Any] = Field(
        default_factory=dict,
        description="Provider-specific payload (kept for trace).",
    )


class ToolResult(BaseModel):
    """Normalised response returned by every :class:`IMCPClient` tool call."""

    model_config = ConfigDict(frozen=True)

    server: str = Field(..., description="MCP server logical name.")
    tool: str = Field(..., description="Tool name on that server.")
    ok: bool = Field(..., description="True when the tool succeeded without errors.")
    data: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured tool output payload.",
    )
    error: ErrorInfo | None = Field(
        default=None,
        description="Populated when ``ok`` is False.",
    )
    duration_ms: int = Field(
        default=0,
        ge=0,
        description="Wall-clock duration of the tool call in milliseconds.",
    )


# ---------------------------------------------------------------------------
# Persistence: run manifest, checkpoint snapshot
# ---------------------------------------------------------------------------


class InputUsed(BaseModel):
    """Single input file recorded in the run manifest."""

    model_config = ConfigDict(frozen=True)

    path: Path = Field(..., description="Path to the input file.")
    type: str = Field(..., description="Free-form description (e.g. 'PRD', 'screenshots').")


class OutputManifest(BaseModel):
    """Single output entry recorded in the run manifest."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Stable artefact id.")
    type: OutputType = Field(..., description="Canonical product type.")
    path: Path = Field(..., description="Relative path inside the run directory.")
    format: Literal["markdown", "xlsx", "html", "json", "directory"] = Field(
        ...,
        description="Physical artefact format.",
    )
    summary: str = Field(default="", description="One-line description.")


class CheckpointDecision(BaseModel):
    """User decision persisted on the run manifest."""

    model_config = ConfigDict(frozen=True)

    checkpoint: str = Field(..., description="Checkpoint identifier.")
    decision: CheckpointAction = Field(..., description="Action taken by the user.")
    note: str = Field(default="", description="Optional user note.")
    timestamp: datetime = Field(..., description="Decision timestamp (UTC).")


class RunManifest(BaseModel):
    """``runs/<id>/run.yaml`` schema."""

    id: str = Field(..., description="Run identifier (e.g. '001-uxeval').")
    skill: str = Field(..., description="Skill name.")
    version: str = Field(..., description="Skill version that ran.")
    status: RunStatus = Field(..., description="Run lifecycle status.")
    started_at: datetime = Field(..., description="Run start timestamp (UTC).")
    completed_at: datetime | None = Field(
        default=None,
        description="Run completion timestamp (UTC).",
    )
    model: str = Field(..., description="LLM model identifier used.")
    mode: Mode | None = Field(
        default=None,
        description="Execution mode used for the run, when the skill is multi-mode.",
    )
    depends_on: list[str] = Field(
        default_factory=list,
        description="Upstream run ids this run consumed.",
    )
    inputs_used: list[InputUsed] = Field(
        default_factory=list,
        description="Inputs supplied by the user.",
    )
    outputs: list[OutputManifest] = Field(
        default_factory=list,
        description="Artefacts produced by the run.",
    )
    checkpoint_decisions: list[CheckpointDecision] = Field(
        default_factory=list,
        description="User decisions at every checkpoint encountered.",
    )
    status_reason: str | None = Field(
        default=None,
        description="Human-readable reason for the current paused/failed state.",
    )
    required_actions: list[str] = Field(
        default_factory=list,
        description="Concrete next actions required before the run can continue safely.",
    )


class CheckpointSnapshot(BaseModel):
    """Persisted pipeline state for resume after a checkpoint pause.

    Stored at ``.designos/checkpoints/session-{run_id}.yaml``.
    """

    run_id: str = Field(..., description="Run identifier.")
    skill: str = Field(..., description="Skill name.")
    current_stage_index: int = Field(
        ...,
        ge=0,
        description="Zero-based index of the next stage to execute.",
    )
    completed_stage_ids: list[str] = Field(
        default_factory=list,
        description="Stage ids that have already completed.",
    )
    pending_stage_ids: list[str] = Field(
        default_factory=list,
        description="Stage ids still to execute.",
    )
    state_snapshot: dict[str, Any] = Field(
        default_factory=dict,
        description="Pipeline variable state at the pause point.",
    )
    last_checkpoint_decision: CheckpointDecision | None = Field(
        default=None,
        description="Last checkpoint decision recorded before pausing.",
    )
    last_updated: datetime = Field(..., description="Snapshot timestamp (UTC).")


# ---------------------------------------------------------------------------
# Domain models (uxeval pilot) — referenced by heuristic-engine and reports
# ---------------------------------------------------------------------------


class Evidence(BaseModel):
    """A single piece of evidence anchoring an Issue to a screenshot or DOM ref."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Evidence identifier (e.g. 'E-001').")
    kind: Literal["screenshot", "dom", "trace", "video"] = Field(
        ...,
        description="Evidence medium.",
    )
    path: Path = Field(..., description="File path relative to the run output directory.")
    bbox: tuple[int, int, int, int] | None = Field(
        default=None,
        description="Optional bounding box (x, y, w, h) on the source artefact.",
    )
    note: str = Field(default="", description="Optional human-readable annotation.")


class HeuristicPrinciple(BaseModel):
    """A single heuristic evaluation principle (Nielsen-style or custom)."""

    id: str = Field(..., description="Principle identifier (e.g. 'H1').")
    name: str = Field(..., description="Short name shown in reports.")
    description: str = Field(..., description="Full principle description.")
    source: str = Field(
        default="",
        description="Where the principle came from (paper / book / internal doc).",
    )


class Task(BaseModel):
    """A single task in the user-task checklist."""

    id: str = Field(..., description="Task identifier (e.g. 'T-001').")
    title: str = Field(..., description="Short task name.")
    description: str = Field(..., description="What the user is trying to accomplish.")
    role: str = Field(..., description="User role performing this task.")
    journey_stage_id: str | None = Field(
        default=None,
        description="Owning JourneyStage id, if mapped.",
    )
    success_criteria: list[str] = Field(
        default_factory=list,
        description="Acceptance criteria for considering the task successful.",
    )


class UserRole(BaseModel):
    """A user persona / role consumed by uxeval prompts."""

    id: str = Field(..., description="Role identifier.")
    name: str = Field(..., description="Role display name.")
    goals: list[str] = Field(
        default_factory=list,
        description="Primary goals the role wants to achieve.",
    )
    pain_points: list[str] = Field(
        default_factory=list,
        description="Known pain points reported in research.")


class JourneyStage(BaseModel):
    """A stage in the user journey map."""

    id: str = Field(..., description="Stage identifier.")
    name: str = Field(..., description="Stage display name.")
    description: str = Field(..., description="What happens during this stage.")
    role_ids: list[str] = Field(
        default_factory=list,
        description="UserRole ids that act in this stage.",
    )
    task_ids: list[str] = Field(
        default_factory=list,
        description="Task ids attached to this stage.",
    )


class Module(BaseModel):
    """A logical module / feature area inside the product under evaluation."""

    id: str = Field(..., description="Module identifier.")
    name: str = Field(..., description="Module display name.")
    description: str = Field(..., description="Short scope description.")
    pages: list[str] = Field(
        default_factory=list,
        description="Page ids / URLs that belong to this module.",
    )


class Issue(BaseModel):
    """A single experience issue raised by uxeval / design-acceptance."""

    id: str = Field(..., description="Issue identifier (e.g. 'I-001').")
    title: str = Field(..., description="Short issue summary.")
    description: str = Field(..., description="What the user observes / experiences.")
    severity: SeverityLevel = Field(..., description="Severity grade.")
    principle_ids: list[str] = Field(
        default_factory=list,
        description="HeuristicPrinciple ids violated by this issue.",
    )
    journey_stage_id: str | None = Field(
        default=None,
        description="Owning JourneyStage id, if attributable.",
    )
    task_id: str | None = Field(
        default=None,
        description="Owning Task id, if attributable.",
    )
    module_id: str | None = Field(
        default=None,
        description="Owning Module id, if attributable.",
    )
    evidence_refs: list[str] = Field(
        ...,
        description="Evidence ids backing this issue (must be non-empty per constitution).",
        min_length=1,
    )
    user_impact: str = Field(
        ...,
        description="Concrete user impact statement (constitution rule #6).",
    )
    suggestion: str = Field(
        ...,
        description="Actionable fix recommendation (constitution rule #5).",
    )
    confidence: Literal["high", "medium", "low"] = Field(
        default="medium",
        description="Confidence that the issue is sufficiently evidenced for the main issue list.",
    )
    evidence_basis: list[str] = Field(
        default_factory=list,
        description="Concrete evidence snippets that justify why this issue can stay in the main list.",
    )
    verification_status: Literal["verified", "needs_verification"] = Field(
        default="verified",
        description="Whether the issue is verified enough for the main issue list or should remain in a verification bucket.",
    )
    source_basis: Literal["prd", "screenshot", "inferred"] = Field(
        default="screenshot",
        description="Authoritative basis when PRD and implementation conflict.",
    )


__all__ = [
    "ArtifactRef",
    "CheckpointConfig",
    "CheckpointDecision",
    "CheckpointEvent",
    "CheckpointSnapshot",
    "DesignOSConfig",
    "ErrorInfo",
    "Evidence",
    "GlobalConfig",
    "HeuristicPrinciple",
    "InputUsed",
    "Issue",
    "JourneyStage",
    "LLMResponse",
    "MCPServerConfig",
    "Module",
    "OutputManifest",
    "ProjectConfig",
    "RetryConfig",
    "RunManifest",
    "SkillConfig",
    "SkillOutputConfig",
    "SkillContext",
    "SkillResult",
    "StageConfig",
    "StageEvent",
    "StageResult",
    "Task",
    "ToolResult",
    "UserRole",
    "WorkflowConfig",
    "WorkflowEvent",
    "WorkflowStep",
]
