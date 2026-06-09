"""Top-level :class:`ISkillLoader` implementation."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from kernel.contracts.enums import ErrorCode
from kernel.contracts.interfaces import ISkill, ISkillLoader
from kernel.errors import ConfigError

from .group_loader import load_skill_group
from .pipeline_loader import load_pipeline_skill

if TYPE_CHECKING:
    from kernel.skill_loader.group_loader import SkillGroup


class SkillLoader(ISkillLoader):
    """Resolves skill names against one or more search roots."""

    def __init__(self, search_paths: list[Path]) -> None:
        self._roots: list[Path] = [p.expanduser().resolve() for p in search_paths]

    def load(self, skill_name: str) -> ISkill:
        if ":" in skill_name:
            group_id, _, sub_id = skill_name.partition(":")
            group_dir: Path = self._find_group(group_id)
            # Validate the group manifest parses cleanly before resolving the sub-skill.
            group = load_skill_group(group_dir)
            sub_skill_dir: Path = self._sub_skill_dir(group, sub_id)
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

    def _sub_skill_dir(self, group: "SkillGroup", sub_id: str) -> Path:
        """Resolve sub-skill directory from GROUP.md declaration.

        Args:
            group: The loaded SkillGroup (contains parsed sub_skill_paths).
            sub_id: Sub-skill identifier.

        Returns:
            Absolute path to the sub-skill directory.

        Raises:
            ConfigError: If sub_id not declared or SKILL.md missing.
        """
        # GROUP.md declares path as "sub-skills/<id>/SKILL.md" (B1.1 fixed)
        # or just "sub-skills/<id>" (legacy). Either way, _sub_skill_paths[sub_id]
        # resolves to the absolute path from GROUP.md frontmatter.
        skill_md_path: Path | None = group._sub_skill_paths.get(sub_id)
        if skill_md_path is None:
            raise ConfigError(
                ErrorCode.E1001,
                f"sub-skill not declared in GROUP.md: {sub_id}",
                context={"group": group.name, "available": group.list_sub_skills()},
            )

        # If GROUP.md path points to SKILL.md, parent is the skill dir.
        # If it points to the dir itself (legacy), use it as-is.
        if skill_md_path.name == "SKILL.md":
            skill_dir = skill_md_path.parent
        else:
            skill_dir = skill_md_path

        if not (skill_dir / "SKILL.md").exists():
            raise ConfigError(
                ErrorCode.E1001,
                f"sub-skill SKILL.md not found: {sub_id}",
                context={
                    "group": group.name,
                    "sub_id": sub_id,
                    "expected_path": str(skill_dir / "SKILL.md"),
                },
            )

        return skill_dir


__all__ = ["SkillLoader"]
