"""Project-scoped memory persisted to ``<workspace>/.designos/memory/<key>.json``.

Keys are slugified to a safe filename; ``/`` is interpreted as a directory
separator so callers can namespace e.g. ``"uxeval/run-001"``.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from kernel.contracts.enums import ErrorCode
from kernel.errors import WorkspaceError

_SAFE_SEGMENT = re.compile(r"[^A-Za-z0-9._-]+")


class ProjectMemory:
    """JSON-file-backed key-value store anchored to a workspace."""

    def __init__(self, workspace: Path) -> None:
        self._root: Path = workspace / ".designos" / "memory"

    def read(self, key: str) -> Any:
        """Return the JSON value for ``key`` or ``None`` when missing."""
        path: Path = self._path_for(key)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise WorkspaceError(
                ErrorCode.E4001,
                f"corrupted memory file: {path}",
                context={"key": key, "path": str(path)},
            ) from exc

    def write(self, key: str, value: Any) -> None:
        """Persist ``value`` under ``key`` as JSON."""
        path: Path = self._path_for(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(value, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )

    def _path_for(self, key: str) -> Path:
        if not key or key.startswith("/"):
            raise WorkspaceError(
                ErrorCode.E4001,
                f"invalid memory key: {key!r}",
                context={"key": key},
            )
        segments: list[str] = [_safe(seg) for seg in key.split("/") if seg]
        if not segments:
            raise WorkspaceError(
                ErrorCode.E4001,
                f"invalid memory key: {key!r}",
                context={"key": key},
            )
        segments[-1] = f"{segments[-1]}.json"
        return self._root.joinpath(*segments)


def _safe(segment: str) -> str:
    cleaned: str = _SAFE_SEGMENT.sub("-", segment).strip("-")
    return cleaned or "_"


__all__ = ["ProjectMemory"]
