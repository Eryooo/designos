"""Unit tests for kernel.checkpoint."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

import pytest

from kernel.checkpoint import (
    CheckpointManager,
    compute_state_hash,
    deserialize_state,
    serialize_state,
    verify_snapshot,
)
from kernel.contracts.enums import ErrorCode
from kernel.contracts.schemas import CheckpointSnapshot, ErrorInfo
from kernel.errors import PipelineError


class _Color(str, Enum):
    RED = "red"
    BLUE = "blue"


def test_serialize_round_trip_handles_path_datetime_enum() -> None:
    state = {
        "path": Path("/tmp/x"),
        "ts": datetime(2026, 5, 18, 12, 0, tzinfo=timezone.utc),
        "color": _Color.RED,
        "model": ErrorInfo(code=ErrorCode.E1001, message="m"),
        "nested": {"a": [Path("/a"), 1, "s"]},
    }
    encoded = serialize_state(state)
    decoded = deserialize_state(encoded)
    assert decoded["path"] == Path("/tmp/x")
    assert decoded["ts"].year == 2026
    assert decoded["color"] is _Color.RED
    assert decoded["model"].message == "m"
    assert decoded["nested"]["a"][0] == Path("/a")


def test_save_and_load_round_trip(tmp_path: Path) -> None:
    cm = CheckpointManager(tmp_path)
    snap = CheckpointSnapshot(
        run_id="001-test",
        skill="stub",
        current_stage_index=1,
        completed_stage_ids=["s1"],
        pending_stage_ids=["s2"],
        state_snapshot={"answer": 42, "where": Path("/x")},
        last_updated=datetime.now(timezone.utc),
    )
    persisted = cm.save(snap)
    assert persisted.exists()
    loaded = cm.load("001-test")
    assert loaded is not None
    assert loaded.current_stage_index == 1
    assert loaded.state_snapshot["answer"] == 42
    assert loaded.state_snapshot["where"] == Path("/x")


def test_load_returns_none_when_missing(tmp_path: Path) -> None:
    cm = CheckpointManager(tmp_path)
    assert cm.load("nope") is None


def test_discard_removes_file(tmp_path: Path) -> None:
    cm = CheckpointManager(tmp_path)
    snap = CheckpointSnapshot(
        run_id="r",
        skill="s",
        current_stage_index=0,
        last_updated=datetime.now(timezone.utc),
    )
    cm.save(snap)
    cm.discard("r")
    assert cm.load("r") is None


def test_state_hash_detects_modification(tmp_path: Path) -> None:
    snap = CheckpointSnapshot(
        run_id="r",
        skill="s",
        current_stage_index=0,
        state_snapshot={"a": 1},
        last_updated=datetime.now(timezone.utc),
    )
    hash_before = compute_state_hash(snap.state_snapshot)
    verify_snapshot(snap, expected_hash=hash_before)
    snap2 = snap.model_copy(update={"state_snapshot": {"a": 2}})
    with pytest.raises(PipelineError):
        verify_snapshot(snap2, expected_hash=hash_before)
