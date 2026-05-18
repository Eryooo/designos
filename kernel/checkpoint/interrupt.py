"""Snapshot integrity helpers used during resume."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from kernel.contracts.enums import ErrorCode
from kernel.contracts.schemas import CheckpointSnapshot
from kernel.errors import PipelineError

from .state_serializer import serialize_state


def compute_state_hash(state: dict[str, Any]) -> str:
    """Return a stable SHA-256 hex digest of a serialised pipeline state."""
    payload: dict[str, Any] = serialize_state(state)
    blob: bytes = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode(
        "utf-8"
    )
    return hashlib.sha256(blob).hexdigest()


def verify_snapshot(snapshot: CheckpointSnapshot, *, expected_hash: str | None) -> None:
    """Raise :class:`PipelineError` when the snapshot hash does not match.

    Args:
        snapshot: Snapshot loaded from disk.
        expected_hash: Optional precomputed hash; when ``None`` no check runs.
    """
    if expected_hash is None:
        return
    actual: str = compute_state_hash(snapshot.state_snapshot)
    if actual != expected_hash:
        raise PipelineError(
            ErrorCode.E2004,
            "checkpoint state hash mismatch",
            context={"run_id": snapshot.run_id, "expected": expected_hash, "actual": actual},
        )


__all__ = ["compute_state_hash", "verify_snapshot"]
