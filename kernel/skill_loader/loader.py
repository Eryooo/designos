"""Top-level :class:`ISkillLoader` implementation."""

from __future__ import annotations

from pathlib import Path

from kernel.contracts.enums import ErrorCode
from kernel.contracts.interfaces import ISkill, ISkillLoader
from kernel.errors import ConfigError

from .group_loader import load_skill_group
from .pipeline_loader import load_pipeline_skill


class SkillLoader(ISkillLoader):
    """Resolves skill names against one or more search roots."""

    def __init__(self, search_paths: list[Path]) -> None:
        self._roots: list[Path] = [p.expanduser().resolve() for p in search_paths]

    def load(self, skill_name: str) -> ISkill:
        if ":" in skill_name:
            group_id, _, sub_id = skill_name.partition(":")
            group_dir: Path = self._find_group(group_id)
            # Validate the group manifest parses cleanly before resolving the sub-skill.
            load_skill_group(group_dir)
            sub_skill_dir: Path = self._sub_skill_dir(group_dir, sub_id)
            return load_pipeline_skill(sub_skill_dir)
        skill_dir: Path = self._find_skill(skill_name)
        if (skill_dir / "GROUP.md").exists():
            return load_skill_group(skill_dir)
        return load_pipeline_skill(skill_dir)

    def list_available(self) -> list[str]:
        names: set[str] = set()
        for root in self._roots:
            if not root.exists():
                continue
            for entry in root.iterdir():
                if not entry.is_dir():
                    continue
                if (entry / "SKILL.md").exists() or (entry / "GROUP.md").exists():
                    names.add(entry.name)
        return sorted(names)

    def _find_skill(self, name: str) -> Path:
        for root in self._roots:
            candidate: Path = root / name
            if (candidate / "SKILL.md").exists() or (candidate / "GROUP.md").exists():
                return candidate
        raise ConfigError(
            ErrorCode.E1001,
            f"skill not found: {name}",
            context={"name": name, "search_paths": [str(r) for r in self._roots]},
        )

    def _find_group(self, name: str) -> Path:
        for root in self._roots:
            candidate: Path = root / name
            if (candidate / "GROUP.md").exists():
                return candidate
        raise ConfigError(
            ErrorCode.E1001,
            f"skill group not found: {name}",
            context={"name": name},
        )

    def _sub_skill_dir(self, group_dir: Path, sub_id: str) -> Path:
        candidate: Path = group_dir / "skills" / sub_id
        if (candidate / "SKILL.md").exists():
            return candidate
        raise ConfigError(
            ErrorCode.E1001,
            f"sub-skill not found: {sub_id}",
            context={"group_dir": str(group_dir), "sub_id": sub_id},
        )


__all__ = ["SkillLoader"]
