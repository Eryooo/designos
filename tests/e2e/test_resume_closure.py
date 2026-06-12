"""E2E tests for CLI resume execution."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_designos(*args: str, cwd: Path, home: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["HOME"] = str(home)
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        f"{REPO_ROOT}{os.pathsep}{existing_pythonpath}"
        if existing_pythonpath
        else str(REPO_ROOT)
    )
    return subprocess.run(
        [sys.executable, "-m", "designos.cli.main", *args],
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=env,
        timeout=30,
    )


def _make_workspace(tmp_path: Path) -> tuple[Path, Path]:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    for subdir in ("inputs", "outputs", "runs", ".designos/checkpoints", ".designos/memory"):
        (workspace / subdir).mkdir(parents=True, exist_ok=True)
    (workspace / "designos.project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "batch-3b-e2e",
                "created": datetime.now(UTC).isoformat(),
                "owner": "tester",
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    home = tmp_path / "home"
    home.mkdir()
    return workspace, home


def _write_skill(workspace: Path, name: str, *, outcome: str) -> None:
    skill_dir = workspace / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        f"name: {name}\n"
        "version: 4.2.0\n"
        "type: pipeline\n"
        "requires:\n"
        "  kernel: \">=1.0.0,<2.0.0\"\n"
        "---\n"
        f"# {name}\n",
        encoding="utf-8",
    )

    stages: list[dict[str, object]] = [
        {
            "id": "collect",
            "type": "composite",
            "outputs": ["draft"],
            "checkpoint": {
                "id": "C1",
                "message": "Confirm the draft journey.",
                "allow": ["continue"],
            },
        }
    ]
    if outcome == "pause-again":
        stages.append(
            {
                "id": "review",
                "type": "composite",
                "inputs": ["draft"],
                "outputs": ["review_notes"],
                "checkpoint": {
                    "id": "C2",
                    "message": "Confirm the review notes.",
                    "allow": ["continue"],
                },
            }
        )
    stages.append(
        {
            "id": "finish",
            "type": "composite",
            "inputs": ["draft"],
            "outputs": ["final_report"],
        }
    )
    (skill_dir / "pipeline.yaml").write_text(
        yaml.safe_dump(
            {
                "name": f"{name}-pipeline",
                "stages": stages,
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def _write_evidence_gate_skill(workspace: Path, name: str) -> None:
    skill_dir = workspace / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        f"name: {name}\n"
        "version: 5.4.0\n"
        "type: pipeline\n"
        "modes:\n"
        "  - id: client\n"
        "requires:\n"
        "  kernel: \">=1.0.0,<2.0.0\"\n"
        "---\n"
        f"# {name}\n",
        encoding="utf-8",
    )
    (skill_dir / "pipeline.yaml").write_text(
        yaml.safe_dump(
            {
                "name": f"{name}-pipeline",
                "stages": [
                    {
                        "id": "screenshot-loading",
                        "type": "composite",
                        "outputs": ["evidence_assessment"],
                    },
                    {
                        "id": "prd-screenshot-conflict",
                        "type": "composite",
                        "outputs": ["prd_screenshot_conflicts"],
                        "gate": {
                            "when": 'evidence_assessment.verdict == "blocked"',
                            "action": "pause",
                            "checkpoint_id": "QG1",
                            "message": "Evidence is blocked before conflict analysis.",
                            "status_reason_from": "evidence_assessment.blocking_reasons",
                            "required_actions_from": "evidence_assessment.required_actions",
                            "resume_from_stage": "screenshot-loading",
                        },
                    },
                    {
                        "id": "issue-attribution",
                        "type": "composite",
                        "outputs": ["issues"],
                        "gate": {
                            "when": 'evidence_assessment.verdict in ["blocked", "supplement_needed"]',
                            "action": "pause",
                            "checkpoint_id": "QG2",
                            "message": "Evidence is below final attribution quality.",
                            "status_reason_from": "evidence_assessment.verification_gaps",
                            "required_actions_from": "evidence_assessment.required_actions",
                            "resume_from_stage": "screenshot-loading",
                        },
                    },
                    {
                        "id": "report-generation",
                        "type": "composite",
                        "outputs": ["final_report"],
                        "gate": {
                            "when": 'evidence_assessment.verdict in ["blocked", "supplement_needed"]',
                            "action": "pause",
                            "checkpoint_id": "QG3",
                            "message": "Evidence is below final report quality.",
                            "status_reason_from": "evidence_assessment.verification_gaps",
                            "required_actions_from": "evidence_assessment.required_actions",
                            "resume_from_stage": "screenshot-loading",
                        },
                    },
                ],
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def _write_evidence_assessment(workspace: Path, payload: dict[str, object]) -> None:
    (workspace / "inputs" / "evidence_assessment.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (workspace / "inputs" / "prd_screenshot_conflicts.json").write_text(
        json.dumps({"verification_gaps": []}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (workspace / "inputs" / "issues.json").write_text(
        json.dumps([{"id": "I-001", "title": "Sample"}], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (workspace / "inputs" / "final_report.json").write_text(
        json.dumps({"ready": True}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _read_manifest(workspace: Path, run_id: str) -> dict[str, object]:
    run_yaml = workspace / "runs" / run_id / "run.yaml"
    return yaml.safe_load(run_yaml.read_text(encoding="utf-8"))


@pytest.mark.e2e
def test_resume_completes_from_latest_paused_run(tmp_path: Path) -> None:
    workspace, home = _make_workspace(tmp_path)
    _write_skill(workspace, "demo-older-paused", outcome="complete")
    _write_skill(workspace, "demo-latest-paused", outcome="complete")

    first = _run_designos("run", "demo-older-paused", "--mode", "client", cwd=workspace, home=home)
    assert first.returncode == 2, f"stdout: {first.stdout}\nstderr: {first.stderr}"
    second = _run_designos("run", "demo-latest-paused", "--mode", "web", cwd=workspace, home=home)
    assert second.returncode == 2, f"stdout: {second.stdout}\nstderr: {second.stderr}"

    older_paused = _read_manifest(workspace, "001-demo-older-paused")
    latest_paused = _read_manifest(workspace, "002-demo-latest-paused")
    assert older_paused["status"] == "paused"
    assert older_paused["completed_at"] is None
    assert latest_paused["status"] == "paused"
    assert latest_paused["mode"] == "web"
    assert latest_paused["completed_at"] is None

    resumed = _run_designos("resume", cwd=workspace, home=home)
    assert resumed.returncode == 0, f"stdout: {resumed.stdout}\nstderr: {resumed.stderr}"
    assert "Resuming run '002-demo-latest-paused'" in resumed.stdout + resumed.stderr

    manifest = _read_manifest(workspace, "002-demo-latest-paused")
    assert manifest["status"] == "completed"
    assert manifest["mode"] == "web"
    assert manifest["completed_at"] is not None
    assert not (workspace / ".designos" / "checkpoints" / "session-002-demo-latest-paused.yaml").exists()

    untouched = _read_manifest(workspace, "001-demo-older-paused")
    assert untouched["status"] == "paused"
    assert untouched["completed_at"] is None


@pytest.mark.e2e
def test_resume_can_pause_again(tmp_path: Path) -> None:
    workspace, home = _make_workspace(tmp_path)
    _write_skill(workspace, "demo-pause-again", outcome="pause-again")

    first = _run_designos("run", "demo-pause-again", "--mode", "client", cwd=workspace, home=home)
    assert first.returncode == 2, f"stdout: {first.stdout}\nstderr: {first.stderr}"

    resumed = _run_designos("resume", "--run-id", "001-demo-pause-again", cwd=workspace, home=home)
    assert resumed.returncode == 2, f"stdout: {resumed.stdout}\nstderr: {resumed.stderr}"
    assert "Run paused at C2." in resumed.stdout + resumed.stderr

    manifest = _read_manifest(workspace, "001-demo-pause-again")
    assert manifest["status"] == "paused"
    assert manifest["mode"] == "client"
    assert manifest["completed_at"] is None
    assert (workspace / ".designos" / "checkpoints" / "session-001-demo-pause-again.yaml").exists()


@pytest.mark.e2e
@pytest.mark.parametrize("corrupt", [False, True])
def test_resume_fails_when_checkpoint_is_missing_or_corrupt(tmp_path: Path, corrupt: bool) -> None:
    workspace, home = _make_workspace(tmp_path)
    _write_skill(workspace, "demo-corrupt-resume", outcome="complete")

    first = _run_designos("run", "demo-corrupt-resume", "--mode", "web", cwd=workspace, home=home)
    assert first.returncode == 2, f"stdout: {first.stdout}\nstderr: {first.stderr}"

    checkpoint = workspace / ".designos" / "checkpoints" / "session-001-demo-corrupt-resume.yaml"
    if corrupt:
        checkpoint.write_text("[", encoding="utf-8")
    else:
        checkpoint.unlink()

    resumed = _run_designos("resume", "--run-id", "001-demo-corrupt-resume", cwd=workspace, home=home)
    assert resumed.returncode == 1, f"stdout: {resumed.stdout}\nstderr: {resumed.stderr}"
    if corrupt:
        assert "corrupted checkpoint" in resumed.stdout + resumed.stderr
    else:
        assert "No checkpoint found for run '001-demo-corrupt-resume'." in resumed.stdout + resumed.stderr

    manifest = _read_manifest(workspace, "001-demo-corrupt-resume")
    assert manifest["status"] == "paused"
    assert manifest["completed_at"] is None


@pytest.mark.e2e
def test_evidence_gate_blocked_run_rewinds_to_collection_and_completes_after_resume(tmp_path: Path) -> None:
    workspace, home = _make_workspace(tmp_path)
    _write_evidence_gate_skill(workspace, "evidence-gate")
    _write_evidence_assessment(
        workspace,
        {
            "verdict": "blocked",
            "blocking_reasons": ["no local OCR capability and no markdown description evidence"],
            "required_actions": ["补充 inputs/screens-description.md"],
            "verification_gaps": [],
        },
    )

    first = _run_designos("run", "evidence-gate", "--mode", "client", cwd=workspace, home=home)
    assert first.returncode == 2, f"stdout: {first.stdout}\nstderr: {first.stderr}"
    assert "Run paused at QG1." in first.stdout + first.stderr

    first_manifest = _read_manifest(workspace, "001-evidence-gate")
    assert first_manifest["status"] == "paused"
    assert first_manifest["completed_at"] is None
    assert first_manifest["status_reason"] == "no local OCR capability and no markdown description evidence"
    assert first_manifest["required_actions"] == ["补充 inputs/screens-description.md"]

    checkpoint = yaml.safe_load(
        (workspace / ".designos" / "checkpoints" / "session-001-evidence-gate.yaml").read_text(encoding="utf-8")
    )
    assert checkpoint["current_stage_index"] == 0
    assert checkpoint["completed_stage_ids"] == []

    _write_evidence_assessment(
        workspace,
        {
            "verdict": "sufficient",
            "blocking_reasons": [],
            "required_actions": [],
            "verification_gaps": [],
        },
    )

    resumed = _run_designos("resume", "--run-id", "001-evidence-gate", cwd=workspace, home=home)
    assert resumed.returncode == 0, f"stdout: {resumed.stdout}\nstderr: {resumed.stderr}"
    assert "Resuming run '001-evidence-gate'" in resumed.stdout + resumed.stderr

    manifest = _read_manifest(workspace, "001-evidence-gate")
    assert manifest["status"] == "completed"
    assert manifest["completed_at"] is not None
    assert manifest["status_reason"] is None
    assert manifest["required_actions"] == []


@pytest.mark.e2e
def test_evidence_gate_supplement_needed_does_not_silently_complete(tmp_path: Path) -> None:
    workspace, home = _make_workspace(tmp_path)
    _write_evidence_gate_skill(workspace, "evidence-supplement")
    _write_evidence_assessment(
        workspace,
        {
            "verdict": "supplement_needed",
            "blocking_reasons": [],
            "required_actions": ["补高分辨率截图，建议宽度 >= 1280 像素"],
            "verification_gaps": ["截图可读性偏低，当前主要依赖 markdown 说明补足证据"],
        },
    )

    result = _run_designos("run", "evidence-supplement", "--mode", "client", cwd=workspace, home=home)
    assert result.returncode == 2, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "Run paused at QG2." in result.stdout + result.stderr

    manifest = _read_manifest(workspace, "001-evidence-supplement")
    assert manifest["status"] == "paused"
    assert manifest["completed_at"] is None
    assert manifest["status_reason"] == "截图可读性偏低，当前主要依赖 markdown 说明补足证据"
    assert manifest["required_actions"] == ["补高分辨率截图，建议宽度 >= 1280 像素"]
