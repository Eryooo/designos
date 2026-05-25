"""Pipeline-form Skill loader.

Reads ``SKILL.md`` (frontmatter) + ``pipeline.yaml`` (stages) from a directory
and returns a concrete :class:`IPipelineSkill` whose :meth:`run` executes via
:class:`PipelineEngine`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from kernel.contracts.enums import ErrorCode, RunStatus, SkillType
from kernel.contracts.interfaces import (
    ILLMClient,
    IMCPClient,
    IPipelineEngine,
    IPipelineSkill,
)
from kernel.contracts.schemas import (
    MCPServerConfig,
    SkillConfig,
    SkillContext,
    SkillOutputConfig,
    SkillResult,
    StageConfig,
    StageResult,
)
from kernel.errors import ConfigError

from .frontmatter import parse_frontmatter


class PipelineSkill(IPipelineSkill):
    """Concrete :class:`IPipelineSkill` built from on-disk SKILL.md + pipeline.yaml."""

    def __init__(
        self,
        *,
        config: SkillConfig,
        stages: list[StageConfig],
        skill_dir: Path,
        engine: IPipelineEngine | None = None,
        llm: ILLMClient | None = None,
        mcp: IMCPClient | None = None,
    ) -> None:
        self.name: str = config.name
        self.version: str = config.version
        self.skill_type: SkillType = SkillType.PIPELINE
        self._config: SkillConfig = config
        self._stages: list[StageConfig] = stages
        self._dir: Path = skill_dir
        self._engine: IPipelineEngine | None = engine
        self._llm: ILLMClient | None = llm
        self._mcp: IMCPClient | None = mcp

    @property
    def config(self) -> SkillConfig:
        return self._config

    @property
    def directory(self) -> Path:
        return self._dir

    def get_stages(self) -> list[StageConfig]:
        return list(self._stages)

    def attach(
        self,
        *,
        engine: IPipelineEngine | None = None,
        llm: ILLMClient | None = None,
        mcp: IMCPClient | None = None,
    ) -> None:
        """Late-bind kernel runtime dependencies (used after construction)."""
        if engine is not None:
            self._engine = engine
        if llm is not None:
            self._llm = llm
        if mcp is not None:
            self._mcp = mcp

    async def run(self, ctx: SkillContext) -> SkillResult:
        if self._engine is None:
            raise ConfigError(
                ErrorCode.E2001,
                f"pipeline engine not attached to skill {self.name}",
                context={"skill": self.name},
            )
        events = self._engine.execute(self, ctx)
        status = RunStatus.COMPLETED
        paused_at_checkpoint: str | None = None
        pause_kind: str | None = None
        status_reason: str | None = None
        required_actions: list[str] = []
        async for event in events:
            if event.kind == "checkpoint":
                status = RunStatus.PAUSED
                checkpoint_id = event.payload.get("checkpoint_id")
                paused_at_checkpoint = str(checkpoint_id) if checkpoint_id is not None else None
                pause_kind_value = event.payload.get("pause_kind")
                if pause_kind_value in {"checkpoint", "gate"}:
                    pause_kind = str(pause_kind_value)
                else:
                    pause_kind = "checkpoint"
                reason_value = event.payload.get("status_reason")
                if isinstance(reason_value, str) and reason_value.strip():
                    status_reason = reason_value.strip()
                payload_actions = event.payload.get("required_actions")
                if isinstance(payload_actions, list):
                    required_actions = [str(item).strip() for item in payload_actions if str(item).strip()]
            elif event.kind in {"stage_failed", "error"}:
                status = RunStatus.FAILED
                paused_at_checkpoint = None
                pause_kind = None
                error_payload = event.payload.get("error")
                if isinstance(error_payload, dict):
                    message = error_payload.get("message")
                    if isinstance(message, str) and message.strip():
                        status_reason = message.strip()
                    context = error_payload.get("context")
                    if isinstance(context, dict):
                        context_actions = context.get("required_actions")
                        if isinstance(context_actions, list):
                            required_actions = [str(item).strip() for item in context_actions if str(item).strip()]

        stages = _stage_results_from_engine(self._engine, ctx.run_id)
        return SkillResult(
            skill_name=self.name,
            skill_version=self.version,
            status=status,
            stages=stages,
            artifacts=[artifact for stage in stages for artifact in stage.artifacts],
            paused_at_checkpoint=paused_at_checkpoint,
            pause_kind=pause_kind,  # type: ignore[arg-type]
            status_reason=status_reason,
            required_actions=required_actions,
        )


def load_pipeline_skill(skill_dir: Path) -> PipelineSkill:
    """Construct a :class:`PipelineSkill` from a directory."""
    skill_dir = skill_dir.expanduser().resolve()
    manifest: Path = skill_dir / "SKILL.md"
    fm, _body = parse_frontmatter(manifest)
    if str(fm.get("type", "pipeline")) != "pipeline":
        raise ConfigError(
            ErrorCode.E1001,
            f"SKILL.md is not a pipeline skill (type={fm.get('type')})",
            context={"path": str(manifest)},
        )
    config: SkillConfig = _config_from_frontmatter(fm)
    # Runtime metadata comes from SKILL.md frontmatter. pipeline.yaml only
    # contributes the stage graph and must not act as an independent version source.
    stages: list[StageConfig] = _read_pipeline_yaml(skill_dir / "pipeline.yaml", base=skill_dir)
    return PipelineSkill(config=config, stages=stages, skill_dir=skill_dir)


def _config_from_frontmatter(fm: dict[str, Any]) -> SkillConfig:
    modes_raw: Any = fm.get("modes", []) or []
    modes: list[str] = []
    for mode in modes_raw:
        if isinstance(mode, dict):
            mode_id = str(mode.get("id", "")).strip()
            if mode_id:
                modes.append(mode_id)
        elif isinstance(mode, str):
            mode_id = mode.strip()
            if mode_id:
                modes.append(mode_id)
    requires: dict[str, Any] = fm.get("requires", {}) or {}
    mcp_raw: Any = requires.get("mcp_servers", []) or []
    mcp_servers: list[MCPServerConfig] = []
    for entry in mcp_raw:
        if not isinstance(entry, dict):
            continue
        name: str = str(entry.get("name", "")).strip()
        if not name:
            continue
        payload: dict[str, Any] = {"name": name}
        for key in ("transport", "command", "url", "env", "builtin", "required_when", "requires_external"):
            if key in entry:
                payload[key] = entry[key]
        mcp_servers.append(MCPServerConfig.model_validate(payload))
    outputs_raw: Any = fm.get("outputs", []) or []
    outputs: list[SkillOutputConfig] = []
    for entry in outputs_raw:
        if not isinstance(entry, dict):
            continue
        if "id" not in entry or "type" not in entry or "format" not in entry:
            continue
        outputs.append(SkillOutputConfig.model_validate(entry))
    return SkillConfig(
        name=str(fm.get("name", "")),
        version=str(fm.get("version", "0.0.0")),
        skill_type=SkillType.PIPELINE,
        supported_modes=[m for m in modes if m],
        requires_kernel=str(requires.get("kernel", ">=1.0.0,<2.0.0")),
        mcp_servers=mcp_servers,
        outputs=outputs,
    )


def _read_pipeline_yaml(path: Path, *, base: Path) -> list[StageConfig]:
    if not path.exists():
        raise ConfigError(
            ErrorCode.E2001,
            f"missing pipeline.yaml at {path}",
            context={"path": str(path)},
        )
    try:
        loaded: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(
            ErrorCode.E2001,
            f"invalid pipeline.yaml: {exc}",
            context={"path": str(path)},
        ) from exc
    if not isinstance(loaded, dict):
        raise ConfigError(
            ErrorCode.E2001,
            f"pipeline.yaml must be a mapping: {path}",
            context={"path": str(path)},
        )
    raw_stages: Any = loaded.get("stages", [])
    if not isinstance(raw_stages, list):
        raise ConfigError(
            ErrorCode.E2001,
            "pipeline.yaml `stages` must be a list",
            context={"path": str(path)},
        )
    stages: list[StageConfig] = []
    for entry in raw_stages:
        if not isinstance(entry, dict):
            raise ConfigError(
                ErrorCode.E2001,
                f"stage entry must be a mapping in {path}",
                context={"path": str(path)},
            )
        stages.append(_build_stage(entry, base))
    return stages


def _stage_results_from_engine(engine: IPipelineEngine, run_id: str) -> list[StageResult]:
    last_results: Any = getattr(engine, "last_results", None)
    if not isinstance(last_results, dict):
        return []

    stages: Any = last_results.get(run_id, [])
    if not isinstance(stages, list):
        return []
    return [stage for stage in stages if isinstance(stage, StageResult)]


def _build_stage(entry: dict[str, Any], base: Path) -> StageConfig:
    fixed: dict[str, Any] = dict(entry)
    if isinstance(fixed.get("prompt"), str):
        fixed["prompt"] = (base / fixed["prompt"]).resolve()
    knowledge: Any = fixed.get("knowledge") or []
    if isinstance(knowledge, list):
        fixed["knowledge"] = [(base / str(p)).resolve() for p in knowledge]
    return StageConfig.model_validate(fixed)


__all__ = ["PipelineSkill", "load_pipeline_skill"]
