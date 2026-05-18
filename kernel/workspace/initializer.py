"""``designos init`` implementation."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import yaml

from kernel.contracts.enums import ErrorCode
from kernel.contracts.schemas import ProjectConfig
from kernel.errors import WorkspaceError
from kernel.trace import get_logger

from .workspace import DOTDIR, WORKSPACE_MARKER, Workspace

_log = get_logger("kernel.workspace.initializer")

_README_TEMPLATE: str = (
    "# {name}\n\n"
    "DesignOS project workspace. Run `designos run <skill>` to execute a skill.\n"
)


class WorkspaceInitializer:
    """Creates the on-disk layout for ``designos init``."""

    def initialize(
        self,
        root: Path,
        *,
        name: str,
        owner: str = "",
        skill: str | None = None,
        force: bool = False,
    ) -> Workspace:
        """Create or refresh a workspace at ``root``.

        Args:
            root: Target directory (will be created).
            name: Project name written into ``designos.project.yaml``.
            owner: Project owner identifier.
            skill: Optional skill name to record in the project file.
            force: When True, allow re-initialising a non-empty directory.

        Returns:
            Loaded :class:`Workspace`.
        """
        root = root.expanduser().resolve()
        existing_marker: Path = root / WORKSPACE_MARKER
        if existing_marker.exists() and not force:
            raise WorkspaceError(
                ErrorCode.E4001,
                f"workspace already initialised at {root}",
                context={"path": str(root)},
            )
        root.mkdir(parents=True, exist_ok=True)
        for sub in ("inputs", "outputs", "runs", DOTDIR):
            (root / sub).mkdir(parents=True, exist_ok=True)
        (root / DOTDIR / "checkpoints").mkdir(parents=True, exist_ok=True)
        (root / DOTDIR / "memory").mkdir(parents=True, exist_ok=True)

        skills_section: dict[str, str] = {skill: "*"} if skill else {}
        project = ProjectConfig(
            name=name,
            created=datetime.now(UTC),
            owner=owner or "unknown",
            skills=skills_section,
        )
        existing_marker.write_text(
            yaml.safe_dump(
                project.model_dump(mode="json"),
                allow_unicode=True,
                sort_keys=False,
            ),
            encoding="utf-8",
        )

        readme: Path = root / "README.md"
        if not readme.exists():
            readme.write_text(_README_TEMPLATE.format(name=name), encoding="utf-8")

        gitignore: Path = root / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text(f"{DOTDIR}/checkpoints/\n{DOTDIR}/memory/staging/\n", encoding="utf-8")

        _log.info("workspace.initialised", path=str(root), skill=skill)
        return Workspace(root)


__all__ = ["WorkspaceInitializer"]
