"""Unit tests for kernel.workspace."""

from __future__ import annotations

from pathlib import Path

import pytest

from kernel.contracts.enums import RunStatus
from kernel.contracts.schemas import RunManifest
from kernel.errors import WorkspaceError
from kernel.workspace import RunManager, Workspace, WorkspaceInitializer


def test_initialize_creates_layout(tmp_path: Path) -> None:
    init = WorkspaceInitializer()
    ws = init.initialize(tmp_path / "demo", name="demo", owner="young", skill="uxeval")
    assert (ws.root / "designos.project.yaml").exists()
    assert ws.runs_dir.exists()
    assert ws.inputs_dir.exists()
    assert ws.outputs_dir.exists()
    assert ws.checkpoints_dir.exists()
    assert ws.memory_dir.exists()
    assert (ws.root / "README.md").exists()


def test_initialize_refuses_existing_unless_force(tmp_path: Path) -> None:
    init = WorkspaceInitializer()
    init.initialize(tmp_path / "demo", name="demo")
    with pytest.raises(WorkspaceError):
        init.initialize(tmp_path / "demo", name="demo")
    init.initialize(tmp_path / "demo", name="demo", force=True)


def test_workspace_find_walks_up(tmp_path: Path) -> None:
    init = WorkspaceInitializer()
    ws = init.initialize(tmp_path / "demo", name="demo")
    nested = ws.root / "a" / "b"
    nested.mkdir(parents=True)
    found = Workspace.find(nested)
    assert found.root == ws.root


def test_run_manager_allocate_increments(tmp_path: Path) -> None:
    init = WorkspaceInitializer()
    ws = init.initialize(tmp_path / "demo", name="demo")
    rm = RunManager(ws)
    a = rm.allocate("uxeval")
    assert a == "001-uxeval"
    rm.run_dir(a)
    b = rm.allocate("uxeval")
    assert b == "002-uxeval"


def test_run_manager_writes_manifest(tmp_path: Path) -> None:
    init = WorkspaceInitializer()
    ws = init.initialize(tmp_path / "demo", name="demo")
    rm = RunManager(ws)
    run_id = rm.allocate("uxeval")
    manifest: RunManifest = rm.start_manifest(run_id, "uxeval", "1.0.0", "claude")
    assert manifest.status is RunStatus.RUNNING
    target = rm.write_manifest(manifest)
    assert target.exists()
