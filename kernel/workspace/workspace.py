"""Workspace abstraction: discovery, layout, and run directory access."""

from __future__ import annotations

from pathlib import Path

import yaml

from kernel.contracts.enums import ErrorCode
from kernel.errors import WorkspaceError

WORKSPACE_MARKER: str = "designos.project.yaml"
DOTDIR: str = ".designos"


class Workspace:
    """Represents a single DesignOS project workspace on disk."""

    def __init__(self, root: Path) -> None:
        self._root: Path = root.expanduser().resolve()

    # --- discovery ---------------------------------------------------------

    @classmethod
    def find(cls, start: Path) -> Workspace:
        """Locate the nearest workspace by walking up from ``start``.

        Raises:
            WorkspaceError: When no marker is found.
        """
        cur: Path = start.expanduser().resolve()
        for candidate in [cur, *cur.parents]:
            if (candidate / WORKSPACE_MARKER).exists():
                return cls(candidate)
        raise WorkspaceError(
            ErrorCode.E4001,
            f"no DesignOS workspace found from {start}",
            context={"start": str(start)},
        )

    # --- layout ------------------------------------------------------------

    @property
    def root(self) -> Path:
        return self._root

    @property
    def project_yaml(self) -> Path:
        return self._root / WORKSPACE_MARKER

    @property
    def runs_dir(self) -> Path:
        return self._root / "runs"

    @property
    def inputs_dir(self) -> Path:
        return self._root / "inputs"

    @property
    def outputs_dir(self) -> Path:
        return self._root / "outputs"

    @property
    def dot_dir(self) -> Path:
        return self._root / DOTDIR

    @property
    def checkpoints_dir(self) -> Path:
        return self.dot_dir / "checkpoints"

    @property
    def memory_dir(self) -> Path:
        return self.dot_dir / "memory"

    # --- helpers -----------------------------------------------------------

    def read_project_yaml(self) -> dict[str, object]:
        """Return the parsed ``designos.project.yaml`` content."""
        if not self.project_yaml.exists():
            raise WorkspaceError(
                ErrorCode.E4001,
                f"missing project file: {self.project_yaml}",
                context={"path": str(self.project_yaml)},
            )
        try:
            loaded: object = yaml.safe_load(self.project_yaml.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise WorkspaceError(
                ErrorCode.E4001,
                f"invalid project YAML: {exc}",
                context={"path": str(self.project_yaml)},
            ) from exc
        if not isinstance(loaded, dict):
            raise WorkspaceError(
                ErrorCode.E4001,
                "project file did not parse to a mapping",
                context={"path": str(self.project_yaml)},
            )
        return dict(loaded)  # type: ignore[arg-type]


__all__ = ["DOTDIR", "WORKSPACE_MARKER", "Workspace"]
