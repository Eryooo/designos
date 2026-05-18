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
    SkillResult,
    StageConfig,
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
        async for _ in events:
            pass
        # Final aggregation is the engine's responsibility; if it returns the
        # iterator only, attach() must wire a wrapper. Return a default
        # COMPLETED to keep the surface minimal in M1.
        return SkillResult(
            skill_name=self.name,
            skill_version=self.version,
            status=RunStatus.COMPLETED,
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
    stages: list[StageConfig] = _read_pipeline_yaml(skill_dir / "pipeline.yaml", base=skill_dir)
    return PipelineSkill(config=config, stages=stages, skill_dir=skill_dir)


def _config_from_frontmatter(fm: dict[str, Any]) -> SkillConfig:
    modes_raw: Any = fm.get("modes", []) or []
    modes: list[str] = [str(m.get("id", "")) for m in modes_raw if isinstance(m, dict)]
    requires: dict[str, Any] = fm.get("requires", {}) or {}
    mcp_raw: Any = requires.get("mcp_servers", []) or []
    mcp_servers: list[MCPServerConfig] = []
    for entry in mcp_raw:
        if not isinstance(entry, dict):
            continue
        name: str = str(entry.get("name", "")).strip()
        if not name:
            continue
        mcp_servers.append(
            MCPServerConfig(
                name=name,
                builtin=bool(entry.get("builtin", False)),
            )
        )
    return SkillConfig(
        name=str(fm.get("name", "")),
        version=str(fm.get("version", "0.0.0")),
        skill_type=SkillType.PIPELINE,
        supported_modes=[m for m in modes if m],
        requires_kernel=str(requires.get("kernel", ">=1.0.0,<2.0.0")),
        mcp_servers=mcp_servers,
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


def _build_stage(entry: dict[str, Any], base: Path) -> StageConfig:
    fixed: dict[str, Any] = dict(entry)
    if isinstance(fixed.get("prompt"), str):
        fixed["prompt"] = (base / fixed["prompt"]).resolve()
    knowledge: Any = fixed.get("knowledge") or []
    if isinstance(knowledge, list):
        fixed["knowledge"] = [(base / str(p)).resolve() for p in knowledge]
    return StageConfig.model_validate(fixed)


__all__ = ["PipelineSkill", "load_pipeline_skill"]
