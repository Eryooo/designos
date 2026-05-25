"""Unit tests for CLI run/history manifest closure."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from designos.cli.main import app
from kernel.contracts.enums import OutputType, RunStatus, SkillType
from kernel.contracts.schemas import ArtifactRef, RunManifest, SkillConfig, SkillResult
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


class _FakeLoadedSkill:
    def __init__(
        self,
        *,
        name: str,
        version: str,
        result: SkillResult,
    ) -> None:
        self.name = name
        self.version = version
        self.skill_type = SkillType.PIPELINE
        self.config = SkillConfig(
            name=name,
            version=version,
            skill_type=SkillType.PIPELINE,
        )
        self.result = result
        self.running_manifest: RunManifest | None = None
        self.call_count = 0

    def attach(self, **_: object) -> None:
        return

    async def run(self, ctx) -> SkillResult:  # type: ignore[no-untyped-def]
        self.call_count += 1
        manifest = _read_manifest(ctx.workspace, ctx.run_id)
        self.running_manifest = manifest
        return self.result


@pytest.mark.parametrize(
    ("status", "exit_code", "paused_at", "pause_kind", "status_reason", "required_actions", "message", "expect_completed_at"),
    [
        (RunStatus.COMPLETED, 0, None, None, None, [], "Run complete.", True),
        (RunStatus.FAILED, 1, None, None, None, [], "Run failed.", True),
        (
            RunStatus.PAUSED,
            2,
            "QG2",
            "gate",
            "current screenshots do not provide enough trustworthy text evidence",
            ["补 screens-description.md，说明页面名称、关键按钮、状态与流程"],
            "Run paused at QG2.",
            False,
        ),
    ],
)
def test_run_persists_running_then_terminal_manifest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    status: RunStatus,
    exit_code: int,
    paused_at: str | None,
    pause_kind: str | None,
    status_reason: str | None,
    required_actions: list[str],
    message: str,
    expect_completed_at: bool,
) -> None:
    workspace = _init_workspace(tmp_path, monkeypatch)
    artifacts = [
        ArtifactRef(
            id="issue_report",
            output_type=OutputType.ISSUE_REPORT,
            path=Path("outputs/issue_report.xlsx"),
            format="xlsx",
            summary="Issue workbook",
        ),
        ArtifactRef(
            id="html_report",
            output_type=OutputType.HTML_REPORT,
            path=Path("outputs/issue_report.html"),
            format="html",
            summary="HTML report",
        ),
        ArtifactRef(
            id="evidence_pack",
            output_type=OutputType.EVIDENCE_PACK,
            path=Path("outputs/evidence_pack"),
            format="directory",
            summary="Evidence pack",
        ),
    ]
    fake_skill = _FakeLoadedSkill(
        name="demo-skill",
        version="9.9.9",
        result=SkillResult(
            skill_name="demo-skill",
            skill_version="9.9.9",
            status=status,
            artifacts=artifacts,
            paused_at_checkpoint=paused_at,
            pause_kind=pause_kind,  # type: ignore[arg-type]
            status_reason=status_reason,
            required_actions=required_actions,
        ),
    )
    monkeypatch.setattr(SkillLoader, "load", lambda self, _: fake_skill)

    result = runner.invoke(app, ["run", "demo-skill", "--mode", "web"], catch_exceptions=False)

    assert result.exit_code == exit_code
    assert message in result.output
    assert fake_skill.running_manifest is not None
    assert fake_skill.running_manifest.status is RunStatus.RUNNING
    assert fake_skill.running_manifest.completed_at is None
    assert fake_skill.running_manifest.mode == "web"

    manifest = _read_manifest(workspace, "001-demo-skill")
    assert manifest.status is status
    assert manifest.version == "9.9.9"
    assert manifest.model == "claude-opus-4-7"
    assert manifest.mode == "web"
    if expect_completed_at:
        assert manifest.completed_at is not None
    else:
        assert manifest.completed_at is None
    assert manifest.status_reason == status_reason
    assert manifest.required_actions == required_actions
    assert [output.id for output in manifest.outputs] == [
        "issue_report",
        "html_report",
        "evidence_pack",
    ]
    assert manifest.outputs[0].path == Path("outputs/issue_report.xlsx")
    assert manifest.outputs[1].path == Path("outputs/issue_report.html")
    assert manifest.outputs[2].path == Path("outputs/evidence_pack")


def test_history_only_lists_real_run_manifests(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    workspace = _init_workspace(tmp_path, monkeypatch)

    stray = workspace / "runs" / "001-stray"
    stray.mkdir(parents=True, exist_ok=True)

    invalid = workspace / "runs" / "002-invalid"
    invalid.mkdir(parents=True, exist_ok=True)
    (invalid / "run.yaml").write_text("[", encoding="utf-8")

    rm = RunManager(Workspace(workspace))
    manifest = rm.start_manifest("003-real", "uxeval", "1.0.0", "claude-opus-4-7")
    rm.write_manifest(rm.finish_manifest(manifest, status=RunStatus.COMPLETED))

    result = runner.invoke(app, ["history"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "003-real" in result.stdout
    assert "completed" in result.stdout
    assert "001-stray" not in result.stdout
    assert "002-invalid" not in result.stdout


def test_run_does_not_auto_confirm_through_gate_pause(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _init_workspace(tmp_path, monkeypatch)
    fake_skill = _FakeLoadedSkill(
        name="demo-skill",
        version="9.9.9",
        result=SkillResult(
            skill_name="demo-skill",
            skill_version="9.9.9",
            status=RunStatus.PAUSED,
            paused_at_checkpoint="QG2",
            pause_kind="gate",
            status_reason="current screenshots do not provide enough trustworthy text evidence",
            required_actions=["补 screens-description.md，说明页面名称、关键按钮、状态与流程"],
        ),
    )
    monkeypatch.setattr(SkillLoader, "load", lambda self, _: fake_skill)

    result = runner.invoke(
        app,
        ["run", "demo-skill", "--mode", "client", "--auto-confirm"],
        catch_exceptions=False,
    )

    assert result.exit_code == 2
    assert fake_skill.call_count == 1
    assert "Run paused at QG2." in result.output
