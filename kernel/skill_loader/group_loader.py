"""Skill Group loader.

Builds a concrete :class:`ISkillGroup` from ``GROUP.md`` and a workflows
directory. Sub-skills are loaded lazily via :func:`load_pipeline_skill` when
:meth:`SkillGroup.run_sub_skill` is called.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from kernel.contracts.enums import ErrorCode, RunStatus, SkillType
from kernel.contracts.interfaces import ISkillGroup
from kernel.contracts.schemas import (
    SkillConfig,
    SkillContext,
    SkillResult,
    WorkflowConfig,
)
from kernel.errors import ConfigError

from .frontmatter import parse_frontmatter
from .pipeline_loader import PipelineSkill, load_pipeline_skill

if TYPE_CHECKING:
    from kernel.contracts.interfaces import ILLMClient, IMCPClient, IPipelineEngine


class SkillGroup(ISkillGroup):
    """Concrete :class:`ISkillGroup` backed by a directory of sub-skills."""

    def __init__(
        self,
        *,
        config: SkillConfig,
        group_dir: Path,
        sub_skill_paths: dict[str, Path],
        workflows: dict[str, WorkflowConfig],
    ) -> None:
        self.name: str = config.name
        self.version: str = config.version
        self.skill_type: SkillType = SkillType.GROUP
        self._config: SkillConfig = config
        self._dir: Path = group_dir
        self._sub_skill_paths: dict[str, Path] = sub_skill_paths
        self._workflows: dict[str, WorkflowConfig] = workflows
        self._cache: dict[str, PipelineSkill] = {}
        # Runtime dependencies attached after construction (B1.1 runtime fix)
        self._engine: "IPipelineEngine | None" = None
        self._llm: "ILLMClient | None" = None
        self._mcp: "IMCPClient | None" = None

    @property
    def config(self) -> SkillConfig:
        return self._config

    def list_sub_skills(self) -> list[str]:
        return sorted(self._sub_skill_paths)

    def get_workflow(self, name: str) -> WorkflowConfig | None:
        return self._workflows.get(name)

    async def run_sub_skill(self, name: str, ctx: SkillContext) -> SkillResult:
        skill: PipelineSkill = self._load_sub_skill(name)
        return await skill.run(ctx)

    async def run(self, ctx: SkillContext) -> SkillResult:
        # Default group invocation: nothing to do unless a workflow is chosen.
        return SkillResult(
            skill_name=self.name,
            skill_version=self.version,
            status=RunStatus.COMPLETED,
        )

    def attach(
        self,
        *,
        engine: "IPipelineEngine | None" = None,
        llm: "ILLMClient | None" = None,
        mcp: "IMCPClient | None" = None,
    ) -> None:
        """Attach runtime dependencies to this SkillGroup and all cached sub-skills.

        B1.1 runtime fix: SkillGroup now stores engine/llm/mcp and attaches them
        to lazily-loaded sub-skills. Already-cached sub-skills are also attached.
        """
        if engine is not None:
            self._engine = engine
        if llm is not None:
            self._llm = llm
        if mcp is not None:
            self._mcp = mcp

        # Attach to already-cached sub-skills
        for skill in self._cache.values():
            skill.attach(engine=self._engine, llm=self._llm, mcp=self._mcp)

    def _load_sub_skill(self, name: str) -> PipelineSkill:
        if name in self._cache:
            return self._cache[name]
        path: Path | None = self._sub_skill_paths.get(name)
        if path is None:
            raise ConfigError(
                ErrorCode.E1001,
                f"unknown sub-skill: {name}",
                context={"group": self.name, "available": self.list_sub_skills()},
            )
        # B1.1 fix: GROUP.md path can be "sub-skills/<id>/SKILL.md" or "sub-skills/<id>"
        if path.name == "SKILL.md":
            skill_dir = path.parent
        else:
            skill_dir = path
        skill: PipelineSkill = load_pipeline_skill(skill_dir)
        # B1.1 runtime fix: attach group's runtime dependencies to newly-loaded sub-skill
        skill.attach(engine=self._engine, llm=self._llm, mcp=self._mcp)
        self._cache[name] = skill
        return skill


def load_skill_group(group_dir: Path) -> SkillGroup:
    """Load a Skill Group from ``group_dir/GROUP.md``."""
    group_dir = group_dir.expanduser().resolve()
    manifest: Path = group_dir / "GROUP.md"
    fm, _body = parse_frontmatter(manifest)
    if str(fm.get("type", "group")) != "group":
        raise ConfigError(
            ErrorCode.E1001,
            f"GROUP.md is not a group skill (type={fm.get('type')})",
            context={"path": str(manifest)},
        )
    config: SkillConfig = SkillConfig(
        name=str(fm.get("name", "")),
        version=str(fm.get("version", "0.0.0")),
        skill_type=SkillType.GROUP,
        requires_kernel=str((fm.get("requires") or {}).get("kernel", ">=1.0.0,<2.0.0")),
    )
    sub_skill_paths: dict[str, Path] = _resolve_sub_skills(fm.get("sub_skills", []) or [], group_dir)
    workflows: dict[str, WorkflowConfig] = _resolve_workflows(fm.get("workflows", []) or [], group_dir)
    return SkillGroup(
        config=config,
        group_dir=group_dir,
        sub_skill_paths=sub_skill_paths,
        workflows=workflows,
    )


def _resolve_sub_skills(entries: Any, base: Path) -> dict[str, Path]:
    if not isinstance(entries, list):
        return {}
    out: dict[str, Path] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        sub_id: str = str(entry.get("id", ""))
        rel: str = str(entry.get("path", ""))
        if not sub_id or not rel:
            continue
        out[sub_id] = (base / rel).resolve()
    return out


def _resolve_workflows(entries: Any, base: Path) -> dict[str, WorkflowConfig]:
    if not isinstance(entries, list):
        return {}
    out: dict[str, WorkflowConfig] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        workflow_id: str = str(entry.get("id", ""))
        rel: str = str(entry.get("file", ""))
        if not workflow_id or not rel:
            continue
        path: Path = (base / rel).resolve()
        out[workflow_id] = _load_workflow(path)
    return out


def _load_workflow(path: Path) -> WorkflowConfig:
    if not path.exists():
        raise ConfigError(
            ErrorCode.E2001,
            f"missing workflow file: {path}",
            context={"path": str(path)},
        )
    try:
        loaded: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(
            ErrorCode.E2001,
            f"invalid workflow YAML: {exc}",
            context={"path": str(path)},
        ) from exc
    if not isinstance(loaded, dict):
        raise ConfigError(
            ErrorCode.E2001,
            f"workflow file must be a mapping: {path}",
            context={"path": str(path)},
        )
    return WorkflowConfig.model_validate(loaded)


__all__ = ["SkillGroup", "load_skill_group"]
