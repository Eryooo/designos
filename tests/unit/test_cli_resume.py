"""Unit tests for CLI resume execution."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from designos.cli.main import app
from kernel.checkpoint import CheckpointManager
from kernel.contracts.enums import RunStatus, SkillType
from kernel.contracts.schemas import CheckpointSnapshot, RunManifest, SkillConfig, SkillResult
from kernel.skill_loader.loader import SkillLoader
from kernel.workspace import RunManager, Workspace, WorkspaceInitializer


runner = CliRunner()


def _init_workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))

    ws = WorkspaceInitializer().initialize(
        tmp_path / "workspace",
        name="workspace",
        owner="tester",
    )
    monkeypatch.chdir(ws.root)
    return ws.root


def _read_manifest(workspace: Path, run_id: str) -> RunManifest:
    raw = yaml.safe_load((workspace / "runs" / run_id / "run.yaml").read_text(encoding="utf-8"))
    return RunManifest.model_validate(raw)


def _write_paused_run(
    workspace: Path,
    *,
    run_id: str,
    skill: str = "demo-skill",
    version: str = "1.2.3",
    mode: str = "client",
    snapshot_updated_at: datetime | None = None,
    write_snapshot: bool = True,
) -> RunManifest:
    rm = RunManager(Workspace(workspace))
    manifest = rm.start_manifest(
        run_id,
        skill,
        version,
        "claude-opus-4-7",
        mode=mode,
    )
    if snapshot_updated_at is not None:
        manifest = manifest.model_copy(update={"started_at": snapshot_updated_at - timedelta(seconds=1)})
    paused = rm.finish_manifest(manifest, status=RunStatus.PAUSED)
    rm.write_manifest(paused)

    if write_snapshot:
        CheckpointManager(workspace).save(
            CheckpointSnapshot(
                run_id=run_id,
                skill=skill,
                current_stage_index=1,
                completed_stage_ids=["collect"],
                pending_stage_ids=["finish"],
                state_snapshot={"restored": True},
                last_updated=snapshot_updated_at or datetime.now(UTC),
            )
        )
    return paused


class _FakeLoadedSkill:
    def __init__(self, *, result: SkillResult) -> None:
        self.name = "demo-skill"
        self.version = "1.2.3"
        self.skill_type = SkillType.PIPELINE
        self.config = SkillConfig(
            name="demo-skill",
            version="1.2.3",
            skill_type=SkillType.PIPELINE,
        )
        self.result = result
        self.running_manifest: RunManifest | None = None
        self.received_run_id: str | None = None
        self.received_mode: str | None = None

    def attach(self, **_: object) -> None:
        return

    async def run(self, ctx) -> SkillResult:  # type: ignore[no-untyped-def]
        self.received_run_id = ctx.run_id
        self.received_mode = ctx.mode
        self.running_manifest = _read_manifest(ctx.workspace, ctx.run_id)
        return self.result


def test_resume_defaults_to_latest_paused_run_and_completes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = _init_workspace(tmp_path, monkeypatch)
    older = datetime(2026, 5, 21, 8, 0, tzinfo=UTC)
    newer = older + timedelta(minutes=5)
    _write_paused_run(workspace, run_id="001-demo-skill", snapshot_updated_at=older)
    _write_paused_run(workspace, run_id="002-demo-skill", snapshot_updated_at=newer, mode="web")

    fake_skill = _FakeLoadedSkill(
        result=SkillResult(
            skill_name="demo-skill",
            skill_version="1.2.3",
            status=RunStatus.COMPLETED,
        )
    )
    monkeypatch.setattr(SkillLoader, "load", lambda self, _: fake_skill)

    result = runner.invoke(app, ["resume"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Resuming run '002-demo-skill'" in result.output
    assert fake_skill.received_run_id == "002-demo-skill"
    assert fake_skill.received_mode == "web"
    assert fake_skill.running_manifest is not None
    assert fake_skill.running_manifest.status is RunStatus.RUNNING
    assert fake_skill.running_manifest.mode == "web"

    resumed = _read_manifest(workspace, "002-demo-skill")
    assert resumed.status is RunStatus.COMPLETED
    assert resumed.mode == "web"
    assert resumed.completed_at is not None

    untouched = _read_manifest(workspace, "001-demo-skill")
    assert untouched.status is RunStatus.PAUSED
    assert untouched.completed_at is None


def test_resume_can_pause_again(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = _init_workspace(tmp_path, monkeypatch)
    _write_paused_run(workspace, run_id="001-demo-skill", mode="client")

    fake_skill = _FakeLoadedSkill(
        result=SkillResult(
            skill_name="demo-skill",
            skill_version="1.2.3",
            status=RunStatus.PAUSED,
            paused_at_checkpoint="C2",
        )
    )
    monkeypatch.setattr(SkillLoader, "load", lambda self, _: fake_skill)

    result = runner.invoke(app, ["resume", "--run-id", "001-demo-skill"], catch_exceptions=False)

    assert result.exit_code == 2
    assert "Run paused at C2." in result.output
    assert fake_skill.received_run_id == "001-demo-skill"
    assert fake_skill.received_mode == "client"
    assert fake_skill.running_manifest is not None
    assert fake_skill.running_manifest.status is RunStatus.RUNNING

    manifest = _read_manifest(workspace, "001-demo-skill")
    assert manifest.status is RunStatus.PAUSED
    assert manifest.mode == "client"
    assert manifest.completed_at is None


@pytest.mark.parametrize("failure_kind", ["missing", "corrupt"])
def test_resume_fails_when_checkpoint_missing_or_corrupt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_kind: str,
) -> None:
    workspace = _init_workspace(tmp_path, monkeypatch)
    _write_paused_run(workspace, run_id="001-demo-skill", write_snapshot=failure_kind != "missing")

    checkpoint_path = workspace / ".designos" / "checkpoints" / "session-001-demo-skill.yaml"
    if failure_kind == "corrupt":
        checkpoint_path.write_text("[", encoding="utf-8")

    result = runner.invoke(app, ["resume", "--run-id", "001-demo-skill"], catch_exceptions=False)

    assert result.exit_code == 1
    if failure_kind == "corrupt":
        assert "corrupted checkpoint" in result.output
    else:
        assert "No checkpoint found for run '001-demo-skill'." in result.output

    manifest = _read_manifest(workspace, "001-demo-skill")
    assert manifest.status is RunStatus.PAUSED
    assert manifest.completed_at is None
