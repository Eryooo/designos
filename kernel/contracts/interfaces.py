"""Abstract base classes for every DesignOS kernel boundary.

These interfaces are frozen on T0. Concrete implementations live in
``kernel/pipeline``, ``kernel/llm`` etc. (delivered by the A1 agent), and
in MCP servers / skills (A2-A5). Any change here cascades to every
downstream sub-agent — never edit without coordinating an ADR update.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

from .enums import SkillType
from .schemas import (
    CheckpointSnapshot,
    LLMResponse,
    SkillContext,
    SkillResult,
    StageConfig,
    StageEvent,
    ToolResult,
    WorkflowConfig,
    WorkflowEvent,
)

# ---------------------------------------------------------------------------
# Skill interfaces
# ---------------------------------------------------------------------------


class ISkill(ABC):
    """Common contract every loadable skill must implement.

    Concrete skills declare their identity and form factor via class
    attributes; the kernel uses ``skill_type`` to dispatch to either the
    pipeline engine or the workflow orchestrator.
    """

    name: str
    version: str
    skill_type: SkillType

    @abstractmethod
    async def run(self, ctx: SkillContext) -> SkillResult:
        """Execute the skill end-to-end.

        Args:
            ctx: Runtime context supplied by the kernel.

        Returns:
            Aggregated :class:`SkillResult` describing run status and outputs.
        """


class IPipelineSkill(ISkill):
    """A skill whose execution is a fixed ordered pipeline of stages."""

    @abstractmethod
    def get_stages(self) -> list[StageConfig]:
        """Return the ordered stage configuration parsed from ``pipeline.yaml``.

        Returns:
            List of :class:`StageConfig` in execution order.
        """


class ISkillGroup(ISkill):
    """A skill group: a registry of sub-skills + workflows + parallel calls."""

    @abstractmethod
    def list_sub_skills(self) -> list[str]:
        """Return all sub-skill ids registered in ``GROUP.md``.

        Returns:
            List of sub-skill ids (e.g. ``["competitor-spectrum-analyzer", ...]``).
        """

    @abstractmethod
    def get_workflow(self, name: str) -> WorkflowConfig | None:
        """Look up a predefined workflow by name.

        Args:
            name: Workflow id from ``GROUP.md`` (e.g. ``"full-T1-to-T8"``).

        Returns:
            Matching :class:`WorkflowConfig` or ``None`` if unknown.
        """

    @abstractmethod
    async def run_sub_skill(self, name: str, ctx: SkillContext) -> SkillResult:
        """Execute a single sub-skill by id.

        Args:
            name: Sub-skill id.
            ctx: Runtime context.

        Returns:
            :class:`SkillResult` for the sub-skill run.
        """


# ---------------------------------------------------------------------------
# Engine / orchestrator interfaces
# ---------------------------------------------------------------------------


class IPipelineEngine(ABC):
    """Drives a single Pipeline Skill, emitting streaming events."""

    @abstractmethod
    def execute(
        self,
        skill: IPipelineSkill,
        ctx: SkillContext,
    ) -> AsyncIterator[StageEvent]:
        """Run a Pipeline Skill stage by stage.

        Args:
            skill: The Pipeline Skill instance to execute.
            ctx: Runtime context.

        Returns:
            Async iterator yielding :class:`StageEvent` updates.
        """


class IWorkflowOrchestrator(ABC):
    """Drives a Skill Group through a workflow definition."""

    @abstractmethod
    def execute(
        self,
        group: ISkillGroup,
        workflow: WorkflowConfig,
        ctx: SkillContext,
    ) -> AsyncIterator[WorkflowEvent]:
        """Execute a workflow against the given Skill Group.

        Args:
            group: Owning Skill Group.
            workflow: Resolved :class:`WorkflowConfig`.
            ctx: Runtime context shared across sub-skills.

        Returns:
            Async iterator yielding :class:`WorkflowEvent` updates.
        """

    @abstractmethod
    async def execute_parallel(
        self,
        group: ISkillGroup,
        sub_skill_names: list[str],
        ctx: SkillContext,
    ) -> dict[str, SkillResult]:
        """Run multiple independent sub-skills concurrently and aggregate results.

        Args:
            group: Owning Skill Group.
            sub_skill_names: Sub-skill ids to launch in parallel.
            ctx: Runtime context (shared).

        Returns:
            Mapping from sub-skill id to its :class:`SkillResult`.
        """


# ---------------------------------------------------------------------------
# Client adapters
# ---------------------------------------------------------------------------


class ILLMClient(ABC):
    """Provider-agnostic LLM client used by every llm-type stage."""

    @abstractmethod
    async def call(
        self,
        prompt: str,
        *,
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Invoke the configured model with a single prompt.

        Args:
            prompt: Fully-rendered prompt body.
            model: Optional override of the configured primary model.
            temperature: Sampling temperature.
            max_tokens: Generation cap.

        Returns:
            Normalised :class:`LLMResponse`.
        """


class IMCPClient(ABC):
    """Wraps stdio / SSE transports talking to an MCP server."""

    @abstractmethod
    async def call_tool(
        self,
        server: str,
        tool: str,
        args: dict[str, Any],
    ) -> ToolResult:
        """Invoke a tool on a registered MCP server.

        Args:
            server: Logical MCP server name (matches ``MCPServerConfig.name``).
            tool: Tool name on that server.
            args: JSON-serialisable arguments.

        Returns:
            :class:`ToolResult` envelope.
        """


class IMemoryAdapter(ABC):
    """Three-tier memory access: session / project / organisation."""

    @abstractmethod
    def read_session(self, key: str) -> Any:
        """Read an in-process session-scoped value.

        Args:
            key: Memory key.

        Returns:
            Stored value or ``None`` if missing.
        """

    @abstractmethod
    def write_session(self, key: str, value: Any) -> None:
        """Write a session-scoped value (lives until kernel exit).

        Args:
            key: Memory key.
            value: JSON-serialisable value.
        """

    @abstractmethod
    def read_project(self, key: str) -> Any:
        """Read a project-scoped value persisted under ``.designos/memory``.

        Args:
            key: Memory key.

        Returns:
            Stored value or ``None`` if missing.
        """

    @abstractmethod
    def write_project(self, key: str, value: Any) -> None:
        """Persist a project-scoped value.

        Args:
            key: Memory key.
            value: JSON-serialisable value.
        """

    @abstractmethod
    def search_organization(self, query: str, k: int = 5) -> list[Any]:
        """Semantic search over the organisation memory git repository.

        Args:
            query: Natural-language query.
            k: Maximum number of results to return.

        Returns:
            Up to ``k`` matching memory documents.
        """

    @abstractmethod
    def propose_to_organization(
        self,
        category: str,
        payload: Any,
    ) -> str:
        """Open a sanitiser-checked PR against the organisation memory repo.

        Args:
            category: Top-level memory bucket (e.g. ``"uxeval/golden_samples"``).
            payload: Document to publish (must pass sanitiser).

        Returns:
            URL of the staging pull request.
        """


# ---------------------------------------------------------------------------
# Cross-cutting services
# ---------------------------------------------------------------------------


class IPreflightChecker(ABC):
    """Validates external dependencies declared in ``SKILL.md``."""

    @abstractmethod
    async def check(self, skill: ISkill, ctx: SkillContext) -> list[str]:
        """Run preflight checks against the active environment.

        Args:
            skill: Skill instance about to run.
            ctx: Runtime context (used for mode-conditional checks).

        Returns:
            List of human-readable error messages; empty list means OK.
        """


class IOutputRenderer(ABC):
    """Persists artefacts to Markdown / Excel / HTML / JSON."""

    @abstractmethod
    async def render(
        self,
        artefact_id: str,
        payload: Any,
        *,
        target_path: Path,
        fmt: str,
    ) -> Path:
        """Render and persist a single artefact.

        Args:
            artefact_id: Stable artefact identifier.
            payload: Pydantic model or dict to serialise.
            target_path: Destination path (relative to the run output dir).
            fmt: Physical format (``markdown``/``xlsx``/``html``/``json``).

        Returns:
            Absolute path of the written file.
        """


class ISkillLoader(ABC):
    """Resolves a skill name to a concrete :class:`ISkill` instance."""

    @abstractmethod
    def load(self, skill_name: str) -> ISkill:
        """Locate and instantiate a skill by name.

        Args:
            skill_name: Skill name (with optional ``group:sub-skill`` shorthand).

        Returns:
            A loaded :class:`ISkill` (Pipeline or Group).
        """

    @abstractmethod
    def list_available(self) -> list[str]:
        """List all skill names visible to the loader.

        Returns:
            Sorted list of skill names.
        """


class ICheckpointManager(ABC):
    """Persists and restores pipeline state across pause / resume cycles."""

    @abstractmethod
    def save(self, snapshot: CheckpointSnapshot) -> Path:
        """Persist a checkpoint snapshot to disk.

        Args:
            snapshot: Snapshot to save.

        Returns:
            Path of the persisted snapshot file.
        """

    @abstractmethod
    def load(self, run_id: str) -> CheckpointSnapshot | None:
        """Load the most recent snapshot for a run.

        Args:
            run_id: Run identifier.

        Returns:
            Loaded :class:`CheckpointSnapshot` or ``None`` if no snapshot exists.
        """

    @abstractmethod
    def discard(self, run_id: str) -> None:
        """Delete a checkpoint snapshot once the run completes.

        Args:
            run_id: Run identifier.
        """


__all__ = [
    "ICheckpointManager",
    "ILLMClient",
    "IMCPClient",
    "IMemoryAdapter",
    "IOutputRenderer",
    "IPipelineEngine",
    "IPipelineSkill",
    "IPreflightChecker",
    "ISkill",
    "ISkillGroup",
    "ISkillLoader",
    "IWorkflowOrchestrator",
]
