"""Trace recorder writing JSON-Lines events to ``runs/<id>/trace.jsonl``."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .logger import get_logger

_log = get_logger("kernel.trace.recorder")


class TraceRecorder:
    """Append-only JSONL writer used to record stage / tool / llm events."""

    def __init__(self, trace_path: Path) -> None:
        self._path: Path = trace_path
        self._path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def path(self) -> Path:
        return self._path

    def record(self, kind: str, **payload: Any) -> None:
        """Append a single event to the trace file."""
        event: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "kind": kind,
            **payload,
        }
        line: str = json.dumps(event, default=_json_default, ensure_ascii=False)
        with self._path.open("a", encoding="utf-8") as fp:
            fp.write(line + "\n")
        _log.debug("trace.record", kind=kind, path=str(self._path))


def _json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return str(value)


__all__ = ["TraceRecorder"]
