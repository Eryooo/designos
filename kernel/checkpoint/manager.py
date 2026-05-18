"""YAML-backed :class:`ICheckpointManager` implementation."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import yaml

from kernel.contracts.enums import ErrorCode
from kernel.contracts.interfaces import ICheckpointManager
from kernel.contracts.schemas import CheckpointSnapshot
from kernel.errors import PipelineError
from kernel.trace import get_logger

from .state_serializer import deserialize_state, serialize_state

_log = get_logger("kernel.checkpoint.manager")


class CheckpointManager(ICheckpointManager):
    """Persists snapshots to ``<workspace>/.designos/checkpoints``."""

    def __init__(self, workspace: Path) -> None:
        self._dir: Path = workspace / ".designos" / "checkpoints"

    def save(self, snapshot: CheckpointSnapshot) -> Path:
        """Write a snapshot YAML and return its path."""
        self._dir.mkdir(parents=True, exist_ok=True)
        target: Path = self._path_for(snapshot.run_id)
        payload: dict[str, object] = snapshot.model_dump(mode="json")
        # Re-encode state via our typed serializer to handle Path / Enum / model.
        payload["state_snapshot"] = serialize_state(snapshot.state_snapshot)
        payload["last_updated"] = datetime.now(UTC).isoformat()
        target.write_text(
            yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        _log.info("checkpoint.saved", run_id=snapshot.run_id, path=str(target))
        return target

    def load(self, run_id: str) -> CheckpointSnapshot | None:
        """Return the snapshot for ``run_id`` or ``None`` when none exists."""
        target: Path = self._path_for(run_id)
        if not target.exists():
            return None
        try:
            raw: object = yaml.safe_load(target.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise PipelineError(
                ErrorCode.E2004,
                f"corrupted checkpoint: {target}",
                context={"run_id": run_id, "path": str(target)},
            ) from exc
        if not isinstance(raw, dict):
            raise PipelineError(
                ErrorCode.E2004,
                f"checkpoint payload is not a mapping: {target}",
                context={"run_id": run_id},
            )
        raw_dict: dict[str, object] = dict(raw)  # type: ignore[arg-type]
        state_payload: object = raw_dict.get("state_snapshot") or {}
        if isinstance(state_payload, dict):
            raw_dict["state_snapshot"] = deserialize_state(state_payload)  # type: ignore[arg-type]
        return CheckpointSnapshot.model_validate(raw_dict)

    def discard(self, run_id: str) -> None:
        """Delete the checkpoint snapshot for ``run_id`` if it exists."""
        target: Path = self._path_for(run_id)
        if target.exists():
            target.unlink()
            _log.info("checkpoint.discarded", run_id=run_id)

    def _path_for(self, run_id: str) -> Path:
        return self._dir / f"session-{run_id}.yaml"


__all__ = ["CheckpointManager"]
