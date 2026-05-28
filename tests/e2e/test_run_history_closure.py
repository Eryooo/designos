"""E2E tests for CLI run manifest closure."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest
import yaml
from PIL import Image


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


def _make_workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    for subdir in ("inputs", "outputs", "runs", ".designos/checkpoints", ".designos/memory"):
        (workspace / subdir).mkdir(parents=True, exist_ok=True)
    (workspace / "designos.project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "batch-3a-e2e",
                "created": datetime.now(UTC).isoformat(),
                "owner": "tester",
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return workspace


def _write_png(path: Path, *, size: tuple[int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, "white").save(path)


def _make_run_skill(workspace: Path, name: str, *, outcome: str) -> None:
    skill_dir = workspace / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)

    requires_block = "requires:\n  kernel: \">=1.0.0,<2.0.0\"\n"
    if outcome == "failed":
        requires_block = (
            "requires:\n"
            "  kernel: \">=1.0.0,<2.0.0\"\n"
            "  mcp_servers:\n"
            "    - name: missing-mcp\n"
            "      builtin: true\n"
        )

    (skill_dir / "SKILL.md").write_text(
        "---\n"
        f"name: {name}\n"
        "version: 3.1.4\n"
        "type: pipeline\n"
        f"{requires_block}"
        "---\n"
        f"# {name}\n",
        encoding="utf-8",
    )

    stage: dict[str, object]
    if outcome == "failed":
        stage = {
            "id": "broken-tool",
            "type": "tool",
            "mcp_server": "missing-mcp",
            "mcp_tool": "explode",
            "outputs": ["report"],
        }
    else:
        stage = {
            "id": "collect",
            "type": "composite",
            "outputs": ["report"],
        }
        if outcome == "paused":
            stage["checkpoint"] = {
                "id": "C1",
                "message": "Confirm the draft journey.",
                "allow": ["continue"],
            }

    (skill_dir / "pipeline.yaml").write_text(
        yaml.safe_dump(
            {
                "name": f"{name}-pipeline",
                "stages": [stage],
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def _make_report_contract_skill(workspace: Path, name: str) -> None:
    skill_dir = workspace / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)

    (skill_dir / "SKILL.md").write_text(
        "---\n"
        f"name: {name}\n"
        "version: 7.0.0\n"
        "type: pipeline\n"
        "requires:\n"
        "  kernel: \">=1.0.0,<2.0.0\"\n"
        "  mcp_servers:\n"
        "    - name: excel-builder\n"
        "      builtin: true\n"
        "outputs:\n"
        "  - id: issue_report\n"
        "    type: issue_report\n"
        "    format: xlsx\n"
        "  - id: html_report\n"
        "    type: html_report\n"
        "    format: html\n"
        "  - id: evidence_pack\n"
        "    type: evidence_pack\n"
        "    format: directory\n"
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
                        "id": "report-generation",
                        "type": "tool",
                        "mcp_server": "excel-builder",
                        "mcp_tool": "build_issue_report",
                        "inputs": ["issues", "journey_map", "principles"],
                        "outputs": ["issue_report", "html_report", "evidence_pack"],
                    }
                ],
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def _make_delivery_gate_skill(workspace: Path, name: str) -> None:
    skill_dir = workspace / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)

    (skill_dir / "SKILL.md").write_text(
        "---\n"
        f"name: {name}\n"
        "version: 8.1.0\n"
        "type: pipeline\n"
        "requires:\n"
        "  kernel: \">=1.0.0,<2.0.0\"\n"
        "  mcp_servers:\n"
        "    - name: excel-builder\n"
        "      builtin: true\n"
        "outputs:\n"
        "  - id: issue_report\n"
        "    type: issue_report\n"
        "    format: xlsx\n"
        "  - id: html_report\n"
        "    type: html_report\n"
        "    format: html\n"
        "  - id: evidence_pack\n"
        "    type: evidence_pack\n"
        "    format: directory\n"
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
                        "id": "issue-attribution",
                        "type": "composite",
                        "outputs": ["issues", "unverified_issues", "delivery_assessment"],
                    },
                    {
                        "id": "report-generation",
                        "type": "tool",
                        "mcp_server": "excel-builder",
                        "mcp_tool": "build_issue_report",
                        "inputs": ["issues", "journey_map", "principles"],
                        "outputs": ["issue_report", "html_report", "evidence_pack"],
                        "gate": {
                            "when": 'delivery_assessment.delivery_status != "final_delivery_ready"',
                            "action": "pause",
                            "checkpoint_id": "QG3",
                            "message": "Delivery quality gate blocked final report generation.",
                            "status_reason_from": "delivery_assessment.status_reason",
                            "required_actions_from": "delivery_assessment.required_actions",
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


def _make_client_remediation_skill(workspace: Path, name: str) -> None:
    skill_dir = workspace / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)

    (skill_dir / "SKILL.md").write_text(
        "---\n"
        f"name: {name}\n"
        "version: 8.2.0\n"
        "type: pipeline\n"
        "requires:\n"
        "  kernel: \">=1.0.0,<2.0.0\"\n"
        "  mcp_servers:\n"
        "    - name: image-analyzer\n"
        "      builtin: true\n"
        "    - name: excel-builder\n"
        "      builtin: true\n"
        "outputs:\n"
        "  - id: issue_report\n"
        "    type: issue_report\n"
        "    format: xlsx\n"
        "  - id: html_report\n"
        "    type: html_report\n"
        "    format: html\n"
        "  - id: evidence_pack\n"
        "    type: evidence_pack\n"
        "    format: directory\n"
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
                        "type": "tool",
                        "mcp_server": "image-analyzer",
                        "mcp_tool": "load_and_analyze",
                        "inputs": ["screenshots_dir", "task_checklist_lite"],
                        "outputs": ["screenshots", "image_analysis", "evidence_assessment"],
                    },
                    {
                        "id": "issue-attribution",
                        "type": "composite",
                        "outputs": ["issues"],
                        "gate": {
                            "when": 'evidence_assessment.delivery_status in ["blocked", "supplement_required"]',
                            "action": "pause",
                            "checkpoint_id": "QG2",
                            "message": "Evidence quality is still below the issue-attribution threshold.",
                            "status_reason_from": "evidence_assessment.missing_coverage",
                            "required_actions_from": "evidence_assessment.required_actions",
                            "resume_from_stage": "screenshot-loading",
                        },
                    },
                    {
                        "id": "report-generation",
                        "type": "tool",
                        "mcp_server": "excel-builder",
                        "mcp_tool": "build_issue_report",
                        "inputs": ["issues", "journey_map", "principles"],
                        "outputs": ["issue_report", "html_report", "evidence_pack"],
                        "gate": {
                            "when": 'evidence_assessment.delivery_status != "final_delivery_ready"',
                            "action": "pause",
                            "checkpoint_id": "QG3",
                            "message": "Delivery quality gate blocked final report generation.",
                            "status_reason_from": "evidence_assessment.missing_coverage",
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


def _make_proactive_planning_skill(workspace: Path, name: str) -> None:
    skill_dir = workspace / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)

    (skill_dir / "SKILL.md").write_text(
        "---\n"
        f"name: {name}\n"
        "version: 8.5.0\n"
        "type: pipeline\n"
        "requires:\n"
        "  kernel: \">=1.0.0,<2.0.0\"\n"
        "  mcp_servers:\n"
        "    - name: image-analyzer\n"
        "      builtin: true\n"
        "    - name: excel-builder\n"
        "      builtin: true\n"
        "outputs:\n"
        "  - id: delivery_audit_bundle\n"
        "    type: delivery_audit_bundle\n"
        "    format: directory\n"
        "  - id: issue_report\n"
        "    type: issue_report\n"
        "    format: xlsx\n"
        "  - id: html_report\n"
        "    type: html_report\n"
        "    format: html\n"
        "  - id: evidence_pack\n"
        "    type: evidence_pack\n"
        "    format: directory\n"
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
                        "id": "evidence-planning",
                        "type": "tool",
                        "mcp_server": "image-analyzer",
                        "mcp_tool": "plan_required_evidence",
                        "inputs": [
                            "modules",
                            "key_features",
                            "task_checklist_lite",
                            "journey_map",
                            "journey_stages",
                            "screenshots_dir",
                        ],
                        "outputs": [
                            "capture_mission",
                            "required_evidence_plan",
                            "critical_page_requirements",
                            "critical_state_requirements",
                            "evidence_input_guidance",
                        ],
                    },
                    {
                        "id": "screenshot-loading",
                        "type": "tool",
                        "mcp_server": "image-analyzer",
                        "mcp_tool": "load_and_analyze",
                        "inputs": ["screenshots_dir", "task_checklist_lite", "required_evidence_plan"],
                        "outputs": ["screenshots", "image_analysis", "evidence_assessment"],
                        "gate": {
                            "when": 'evidence_input_guidance.pre_run_status in ["supplement_required", "blocked"]',
                            "action": "pause",
                            "checkpoint_id": "QG0",
                            "message": "Pre-run evidence planning requires a one-shot supplement before screenshot analysis.",
                            "status_reason_from": "evidence_input_guidance.status_reason",
                            "required_actions_from": "evidence_input_guidance.required_actions",
                            "resume_from_stage": "evidence-planning",
                        },
                    },
                    {
                        "id": "issue-attribution",
                        "type": "composite",
                        "outputs": ["issues", "unverified_issues", "delivery_assessment"],
                        "gate": {
                            "when": 'evidence_assessment.delivery_status in ["blocked", "supplement_required"]',
                            "action": "pause",
                            "checkpoint_id": "QG2",
                            "message": "Evidence quality is still below the issue-attribution threshold.",
                            "status_reason_from": "evidence_assessment.missing_coverage",
                            "required_actions_from": "evidence_assessment.required_actions",
                            "resume_from_stage": "screenshot-loading",
                        },
                    },
                    {
                        "id": "delivery-audit",
                        "type": "tool",
                        "mcp_server": "excel-builder",
                        "mcp_tool": "audit_delivery_readiness",
                        "inputs": ["issues", "unverified_issues", "evidence_assessment", "delivery_assessment", "capture_mission"],
                        "outputs": ["audited_delivery_assessment", "delivery_audit_bundle"],
                    },
                    {
                        "id": "report-generation",
                        "type": "tool",
                        "mcp_server": "excel-builder",
                        "mcp_tool": "build_issue_report",
                        "inputs": ["issues", "journey_map", "principles"],
                        "outputs": ["issue_report", "html_report", "evidence_pack"],
                        "gate": {
                            "when": 'audited_delivery_assessment.delivery_status != "final_delivery_ready"',
                            "action": "pause",
                            "checkpoint_id": "QG3",
                            "message": "Delivery audit blocked final report generation.",
                            "status_reason_from": "audited_delivery_assessment.status_reason",
                            "required_actions_from": "audited_delivery_assessment.required_actions",
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


def _make_audited_delivery_skill(workspace: Path, name: str) -> None:
    skill_dir = workspace / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)

    (skill_dir / "SKILL.md").write_text(
        "---\n"
        f"name: {name}\n"
        "version: 8.3.0\n"
        "type: pipeline\n"
        "requires:\n"
        "  kernel: \">=1.0.0,<2.0.0\"\n"
        "  mcp_servers:\n"
        "    - name: excel-builder\n"
        "      builtin: true\n"
        "outputs:\n"
        "  - id: delivery_audit_bundle\n"
        "    type: delivery_audit_bundle\n"
        "    format: directory\n"
        "  - id: issue_report\n"
        "    type: issue_report\n"
        "    format: xlsx\n"
        "  - id: html_report\n"
        "    type: html_report\n"
        "    format: html\n"
        "  - id: evidence_pack\n"
        "    type: evidence_pack\n"
        "    format: directory\n"
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
                        "id": "issue-attribution",
                        "type": "composite",
                        "outputs": ["issues", "unverified_issues", "delivery_assessment"],
                    },
                    {
                        "id": "delivery-audit",
                        "type": "tool",
                        "mcp_server": "excel-builder",
                        "mcp_tool": "audit_delivery_readiness",
                        "inputs": ["issues", "unverified_issues", "evidence_assessment", "delivery_assessment", "capture_mission"],
                        "outputs": ["audited_delivery_assessment", "delivery_audit_bundle"],
                    },
                    {
                        "id": "report-generation",
                        "type": "tool",
                        "mcp_server": "excel-builder",
                        "mcp_tool": "build_issue_report",
                        "inputs": ["issues", "journey_map", "principles"],
                        "outputs": ["issue_report", "html_report", "evidence_pack"],
                        "gate": {
                            "when": 'audited_delivery_assessment.delivery_status != "final_delivery_ready"',
                            "action": "pause",
                            "checkpoint_id": "QG3",
                            "message": "Delivery audit blocked final report generation.",
                            "status_reason_from": "audited_delivery_assessment.status_reason",
                            "required_actions_from": "audited_delivery_assessment.required_actions",
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


def _write_delivery_inputs(
    workspace: Path,
    *,
    evidence_assessment: dict[str, object],
    delivery_assessment: dict[str, object],
    unverified_issues: list[dict[str, object]] | None = None,
) -> None:
    (workspace / "inputs" / "evidence_assessment.json").write_text(
        json.dumps(evidence_assessment, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (workspace / "inputs" / "delivery_assessment.json").write_text(
        json.dumps(delivery_assessment, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (workspace / "inputs" / "issues.json").write_text(
        json.dumps(
            [
                {
                    "id": "I-001",
                    "title": "Primary action is buried",
                    "severity": "major",
                    "principle_ids": ["H1"],
                    "description": "CTA is below the fold.",
                    "evidence_refs": ["E-001"],
                    "suggestion": "Move CTA above the fold.",
                    "confidence": "high",
                    "verification_status": "verified",
                    "evidence_basis": ["ocr CTA cue", "markdown description"],
                }
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (workspace / "inputs" / "unverified_issues.json").write_text(
        json.dumps(unverified_issues or [], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (workspace / "inputs" / "journey_map.md").write_text("# Journey\n", encoding="utf-8")
    (workspace / "inputs" / "principles.json").write_text(
        json.dumps([{"id": "H1", "name": "Visibility"}], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _write_audited_delivery_inputs(
    workspace: Path,
    *,
    evidence_assessment: dict[str, object],
    issues: list[dict[str, object]],
    unverified_issues: list[dict[str, object]],
    delivery_assessment: dict[str, object],
) -> None:
    (workspace / "inputs" / "evidence_assessment.json").write_text(
        json.dumps(evidence_assessment, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (workspace / "inputs" / "issues.json").write_text(
        json.dumps(issues, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (workspace / "inputs" / "unverified_issues.json").write_text(
        json.dumps(unverified_issues, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (workspace / "inputs" / "delivery_assessment.json").write_text(
        json.dumps(delivery_assessment, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (workspace / "inputs" / "journey_map.md").write_text("# Journey\n", encoding="utf-8")
    (workspace / "inputs" / "principles.json").write_text(
        json.dumps([{"id": "H1", "name": "Visibility"}], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _write_client_remediation_inputs(
    workspace: Path,
    *,
    image_count: int,
    screen_size: tuple[int, int],
    description_lines: list[str] | None,
) -> None:
    screens_dir = workspace / "inputs" / "screens"
    for idx in range(1, image_count + 1):
        _write_png(screens_dir / f"screen-{idx:02d}.png", size=screen_size)

    if description_lines is not None:
        (workspace / "inputs" / "screens-description.md").write_text(
            "\n".join(description_lines),
            encoding="utf-8",
        )

    (workspace / "inputs" / "task_checklist_lite.txt").write_text(
        "- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 导出成功\n",
        encoding="utf-8",
    )
    (workspace / "inputs" / "issues.json").write_text(
        json.dumps(
            [
                {
                    "id": "I-001",
                    "title": "Primary action is buried",
                    "severity": "major",
                    "principle_ids": ["H1"],
                    "description": "CTA is below the fold.",
                    "evidence_refs": ["E-001"],
                    "suggestion": "Move CTA above the fold.",
                    "confidence": "high",
                    "verification_status": "verified",
                    "evidence_basis": ["ocr CTA cue", "markdown description"],
                }
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (workspace / "inputs" / "journey_map.txt").write_text("# Journey\n", encoding="utf-8")
    (workspace / "inputs" / "principles.json").write_text(
        json.dumps([{"id": "H1", "name": "Visibility"}], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _write_planned_client_inputs(
    workspace: Path,
    *,
    filenames: list[str],
    description_lines: list[str] | None,
) -> None:
    screens_dir = workspace / "inputs" / "screens"
    for name in filenames:
        _write_png(screens_dir / name, size=(1440, 900))

    if description_lines is not None:
        (workspace / "inputs" / "screens-description.md").write_text(
            "\n".join(description_lines),
            encoding="utf-8",
        )

    (workspace / "inputs" / "modules.json").write_text(
        json.dumps(
            [{"name": "登录"}, {"name": "工作台首页"}, {"name": "设置页"}, {"name": "报表列表"}],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (workspace / "inputs" / "key_features.json").write_text(
        json.dumps(
            [{"name": "登录"}, {"name": "查看工作台"}, {"name": "保存设置"}, {"name": "查看报表"}],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (workspace / "inputs" / "task_checklist_lite.txt").write_text(
        "- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n",
        encoding="utf-8",
    )
    (workspace / "inputs" / "journey_map.md").write_text(
        "# Journey\n\n- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n",
        encoding="utf-8",
    )
    (workspace / "inputs" / "journey_stages.json").write_text(
        json.dumps(["登录", "工作台首页", "设置页", "报表列表"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (workspace / "inputs" / "issues.json").write_text(
        json.dumps(
            [
                {
                    "id": "I-001",
                    "title": "Primary action is buried",
                    "severity": "major",
                    "principle_ids": ["H1"],
                    "description": "CTA is below the fold.",
                    "evidence_refs": ["E-001"],
                    "suggestion": "Move CTA above the fold.",
                    "confidence": "high",
                    "verification_status": "verified",
                    "evidence_basis": ["ocr CTA cue", "markdown description"],
                }
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (workspace / "inputs" / "unverified_issues.json").write_text(
        json.dumps([], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (workspace / "inputs" / "delivery_assessment.json").write_text(
        json.dumps(
            {
                "delivery_status": "final_delivery_ready",
                "final_delivery_ready": True,
                "fallback_safe": False,
                "status_reason": "LLM judged the issue set as final-ready.",
                "required_actions": [],
                "verification_gaps": [],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (workspace / "inputs" / "principles.json").write_text(
        json.dumps([{"id": "H1", "name": "Visibility"}], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


@pytest.mark.e2e
@pytest.mark.parametrize(
    ("outcome", "exit_code", "expected_status", "expect_completed_at"),
    [
        ("completed", 0, "completed", True),
        ("failed", 1, "failed", True),
        ("paused", 2, "paused", False),
    ],
)
def test_run_writes_terminal_manifest_for_each_cli_outcome(
    tmp_path: Path,
    outcome: str,
    exit_code: int,
    expected_status: str,
    expect_completed_at: bool,
) -> None:
    workspace = _make_workspace(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    skill_name = f"demo-{outcome}"
    _make_run_skill(workspace, skill_name, outcome=outcome)

    result = _run_designos("run", skill_name, cwd=workspace, home=home)

    assert result.returncode == exit_code, (
        f"Unexpected exit code for {outcome}\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )

    run_yaml = workspace / "runs" / f"001-{skill_name}" / "run.yaml"
    assert run_yaml.exists()

    manifest = yaml.safe_load(run_yaml.read_text(encoding="utf-8"))
    assert manifest["status"] == expected_status
    assert manifest["version"] == "3.1.4"
    assert manifest["model"] == "claude-opus-4-7"
    if expect_completed_at:
        assert manifest["completed_at"] is not None
    else:
        assert manifest["completed_at"] is None


@pytest.mark.e2e
def test_run_records_real_stage7_outputs_in_manifest(tmp_path: Path) -> None:
    workspace = _make_workspace(tmp_path)
    home = tmp_path / "home"
    home.mkdir()

    (workspace / "inputs" / "issues.json").write_text(
        json.dumps(
            [
                {
                    "id": "I-001",
                    "title": "Primary action is buried",
                    "severity": "major",
                    "principle_ids": ["H1"],
                    "description": "CTA is below the fold.",
                    "evidence_refs": ["E-001"],
                    "suggestion": "Move CTA above the fold.",
                }
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (workspace / "inputs" / "journey_map.md").write_text("# Journey\n", encoding="utf-8")
    (workspace / "inputs" / "principles.json").write_text(
        json.dumps([{"id": "H1", "name": "Visibility"}], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    skill_name = "stage7-contract"
    _make_report_contract_skill(workspace, skill_name)

    result = _run_designos("run", skill_name, cwd=workspace, home=home)
    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"

    run_yaml = workspace / "runs" / f"001-{skill_name}" / "run.yaml"
    manifest = yaml.safe_load(run_yaml.read_text(encoding="utf-8"))
    assert manifest["status"] == "completed"
    assert [entry["id"] for entry in manifest["outputs"]] == [
        "issue_report",
        "html_report",
        "evidence_pack",
    ]
    assert manifest["outputs"][0]["path"] == "outputs/issue_report.xlsx"
    assert manifest["outputs"][1]["path"] == "outputs/issue_report.html"
    assert manifest["outputs"][2]["path"] == "outputs/evidence_pack"
    assert (run_yaml.parent / "outputs" / "issue_report.xlsx").exists()
    assert (run_yaml.parent / "outputs" / "issue_report.html").exists()
    assert (run_yaml.parent / "outputs" / "evidence_pack").is_dir()
    assert (run_yaml.parent / "outputs" / "evidence_pack" / "manifest.json").exists()


@pytest.mark.e2e
def test_run_allows_final_report_only_when_delivery_is_ready(tmp_path: Path) -> None:
    workspace = _make_workspace(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    skill_name = "delivery-final-ready"
    _make_delivery_gate_skill(workspace, skill_name)
    _write_delivery_inputs(
        workspace,
        evidence_assessment={
            "verdict": "sufficient",
            "delivery_status": "final_delivery_ready",
            "final_delivery_ready": True,
            "fallback_safe": False,
            "required_actions": [],
            "verification_gaps": [],
        },
        delivery_assessment={
            "delivery_status": "final_delivery_ready",
            "final_delivery_ready": True,
            "fallback_safe": False,
            "status_reason": "Main issue list is fully verified for final delivery.",
            "required_actions": [],
            "verification_gaps": [],
        },
    )

    result = _run_designos("run", skill_name, cwd=workspace, home=home)
    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"

    manifest = yaml.safe_load((workspace / "runs" / f"001-{skill_name}" / "run.yaml").read_text(encoding="utf-8"))
    assert manifest["status"] == "completed"
    assert [entry["id"] for entry in manifest["outputs"]] == [
        "issue_report",
        "html_report",
        "evidence_pack",
    ]


@pytest.mark.e2e
def test_run_pauses_when_only_fallback_safe_delivery_is_available(tmp_path: Path) -> None:
    workspace = _make_workspace(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    skill_name = "delivery-fallback-safe"
    _make_delivery_gate_skill(workspace, skill_name)
    _write_delivery_inputs(
        workspace,
        evidence_assessment={
            "verdict": "sufficient",
            "delivery_status": "fallback_safe",
            "final_delivery_ready": False,
            "fallback_safe": True,
            "required_actions": ["补关键流程的成功/失败状态截图"],
            "verification_gaps": ["关键状态覆盖不足"],
        },
        delivery_assessment={
            "delivery_status": "fallback_safe",
            "final_delivery_ready": False,
            "fallback_safe": True,
            "status_reason": "Current issue list is only safe for bounded intermediate sharing, not final delivery.",
            "required_actions": ["补关键流程的成功/失败状态截图"],
            "verification_gaps": ["关键状态覆盖不足"],
        },
        unverified_issues=[
            {
                "id": "I-099-unverified",
                "title": "Export result feedback may be missing",
                "reason": "Only filename hint is available.",
            }
        ],
    )

    result = _run_designos("run", skill_name, cwd=workspace, home=home)
    assert result.returncode == 2, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "Run paused at QG3." in result.stdout + result.stderr

    manifest = yaml.safe_load((workspace / "runs" / f"001-{skill_name}" / "run.yaml").read_text(encoding="utf-8"))
    assert manifest["status"] == "paused"
    assert manifest["completed_at"] is None
    assert manifest["status_reason"] == "Current issue list is only safe for bounded intermediate sharing, not final delivery."
    assert manifest["required_actions"] == ["补关键流程的成功/失败状态截图"]
    assert manifest["outputs"] == []


@pytest.mark.e2e
def test_runtime_delivery_audit_blocks_final_report_when_main_issue_is_not_verified(tmp_path: Path) -> None:
    workspace = _make_workspace(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    skill_name = "delivery-audit-rejects-llm-final"
    _make_audited_delivery_skill(workspace, skill_name)
    _write_audited_delivery_inputs(
        workspace,
        evidence_assessment={
            "delivery_status": "final_delivery_ready",
            "final_delivery_ready": True,
            "fallback_safe": False,
            "required_actions": [],
            "missing_coverage": [],
            "verification_gaps": [],
            "coverage_summary": {},
        },
        issues=[
            {
                "id": "I-001",
                "title": "Primary action is buried",
                "severity": "major",
                "description": "CTA is below the fold.",
                "evidence_refs": ["E-001"],
                "suggestion": "Move CTA above the fold.",
                "user_impact": "Users miss the primary action.",
                "confidence": "high",
                "evidence_basis": ["ocr CTA cue"],
                "verification_status": "verified",
            },
            {
                "id": "I-002",
                "title": "Error feedback may be inconsistent",
                "severity": "major",
                "description": "Feedback copy changes across pages.",
                "evidence_refs": ["E-002"],
                "suggestion": "Unify error state copy.",
                "user_impact": "Users cannot trust result feedback.",
                "confidence": "medium",
                "evidence_basis": [],
                "verification_status": "needs_verification",
            },
        ],
        unverified_issues=[],
        delivery_assessment={
            "delivery_status": "final_delivery_ready",
            "final_delivery_ready": True,
            "fallback_safe": False,
            "status_reason": "LLM judged the issue set as final-ready.",
            "required_actions": [],
            "verification_gaps": [],
        },
    )

    result = _run_designos("run", skill_name, cwd=workspace, home=home)
    assert result.returncode == 2, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "Run paused at QG3." in result.stdout + result.stderr

    run_dir = workspace / "runs" / f"001-{skill_name}"
    manifest = yaml.safe_load((run_dir / "run.yaml").read_text(encoding="utf-8"))
    assert manifest["status"] == "paused"
    assert [entry["id"] for entry in manifest["outputs"]] == ["delivery_audit_bundle"]
    bundle_dir = run_dir / "outputs" / "delivery_audit_bundle"
    assert (bundle_dir / "bounded_issue_pass.md").exists()
    assert (bundle_dir / "unverified_issues.json").exists()
    assert (bundle_dir / "supplement_request.md").exists()
    audited = json.loads((bundle_dir / "audited_delivery_assessment.json").read_text(encoding="utf-8"))
    assert audited["delivery_status"] == "fallback_safe"
    assert audited["final_delivery_ready"] is False


@pytest.mark.e2e
def test_fallback_safe_run_emits_bounded_delivery_package(tmp_path: Path) -> None:
    workspace = _make_workspace(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    skill_name = "delivery-audit-fallback-package"
    _make_audited_delivery_skill(workspace, skill_name)
    _write_audited_delivery_inputs(
        workspace,
        evidence_assessment={
            "delivery_status": "fallback_safe",
            "final_delivery_ready": False,
            "fallback_safe": True,
            "required_actions": ["补关键流程的成功/失败状态截图"],
            "missing_coverage": ["关键状态覆盖不足"],
            "verification_gaps": ["导出成功状态未覆盖"],
            "coverage_summary": {
                "missing_state_categories": ["success"],
                "missing_tasks": ["导出成功"],
            },
        },
        issues=[
            {
                "id": "I-001",
                "title": "Primary action is buried",
                "severity": "major",
                "description": "CTA is below the fold.",
                "evidence_refs": ["E-001"],
                "suggestion": "Move CTA above the fold.",
                "user_impact": "Users miss the primary action.",
                "confidence": "high",
                "evidence_basis": ["ocr CTA cue", "markdown description"],
                "verification_status": "verified",
            }
        ],
        unverified_issues=[
            {
                "id": "I-099",
                "title": "Export result feedback may be missing",
                "severity": "major",
                "reason": "Only partial state evidence is available.",
                "blocked_by": ["缺导出成功状态截图"],
            }
        ],
        delivery_assessment={
            "delivery_status": "fallback_safe",
            "final_delivery_ready": False,
            "fallback_safe": True,
            "status_reason": "LLM only trusts a bounded issue set.",
            "required_actions": ["补关键流程的成功/失败状态截图"],
            "verification_gaps": ["关键状态覆盖不足"],
        },
    )

    result = _run_designos("run", skill_name, cwd=workspace, home=home)
    assert result.returncode == 2, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "Run paused at QG3." in result.stdout + result.stderr

    run_dir = workspace / "runs" / f"001-{skill_name}"
    manifest = yaml.safe_load((run_dir / "run.yaml").read_text(encoding="utf-8"))
    assert manifest["status"] == "paused"
    assert [entry["id"] for entry in manifest["outputs"]] == ["delivery_audit_bundle"]
    bundle_dir = run_dir / "outputs" / "delivery_audit_bundle"
    bounded_issue_pass = (bundle_dir / "bounded_issue_pass.md").read_text(encoding="utf-8")
    supplement_request = (bundle_dir / "supplement_request.md").read_text(encoding="utf-8")
    assert "Primary action is buried" in bounded_issue_pass
    assert "success" in supplement_request
    assert "导出成功" in supplement_request


@pytest.mark.e2e
def test_runtime_delivery_audit_allows_final_report_when_all_rules_pass(tmp_path: Path) -> None:
    workspace = _make_workspace(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    skill_name = "delivery-audit-final-ready"
    _make_audited_delivery_skill(workspace, skill_name)
    _write_audited_delivery_inputs(
        workspace,
        evidence_assessment={
            "delivery_status": "final_delivery_ready",
            "final_delivery_ready": True,
            "fallback_safe": False,
            "required_actions": [],
            "missing_coverage": [],
            "verification_gaps": [],
            "coverage_summary": {},
        },
        issues=[
            {
                "id": "I-001",
                "title": "Primary action is buried",
                "severity": "major",
                "description": "CTA is below the fold.",
                "evidence_refs": ["E-001"],
                "suggestion": "Move CTA above the fold.",
                "user_impact": "Users miss the primary action.",
                "confidence": "high",
                "evidence_basis": ["ocr CTA cue", "markdown description"],
                "verification_status": "verified",
            }
        ],
        unverified_issues=[],
        delivery_assessment={
            "delivery_status": "final_delivery_ready",
            "final_delivery_ready": True,
            "fallback_safe": False,
            "status_reason": "LLM judged the issue set as final-ready.",
            "required_actions": [],
            "verification_gaps": [],
        },
    )

    result = _run_designos("run", skill_name, cwd=workspace, home=home)
    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"

    run_dir = workspace / "runs" / f"001-{skill_name}"
    manifest = yaml.safe_load((run_dir / "run.yaml").read_text(encoding="utf-8"))
    assert manifest["status"] == "completed"
    assert [entry["id"] for entry in manifest["outputs"]] == [
        "delivery_audit_bundle",
        "issue_report",
        "html_report",
        "evidence_pack",
    ]


@pytest.mark.e2e
def test_client_auto_remediation_can_complete_without_user_pause(tmp_path: Path) -> None:
    workspace = _make_workspace(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    skill_name = "client-remediation-final"
    _make_client_remediation_skill(workspace, skill_name)
    _write_client_remediation_inputs(
        workspace,
        image_count=5,
        screen_size=(1440, 900),
        description_lines=[
            "# 关键页面说明",
            "",
            "## screen-01.png",
            "这是登录页，主按钮为登录。",
            "",
            "## screen-02.png",
            "这是工作台首页，顶部有首页导航。",
            "",
            "## screen-03.png",
            "这是设置页，包含设置项确认按钮。",
            "",
            "## screen-04.png",
            "这是报表列表页，可查看报表列表。",
            "",
            "## screen-05.png",
            "这是导出成功状态页，页面提示导出成功。",
        ],
    )

    result = _run_designos("run", skill_name, "--mode", "client", cwd=workspace, home=home)
    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"

    run_dir = workspace / "runs" / f"001-{skill_name}"
    manifest = yaml.safe_load((run_dir / "run.yaml").read_text(encoding="utf-8"))
    assert manifest["status"] == "completed"
    remediation_dir = run_dir / "outputs" / "evidence-remediation" / "generated-notes"
    assert not remediation_dir.exists()


@pytest.mark.e2e
def test_client_auto_remediation_allows_bounded_result_but_blocks_final_report(tmp_path: Path) -> None:
    workspace = _make_workspace(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    skill_name = "client-remediation-fallback"
    _make_client_remediation_skill(workspace, skill_name)
    _write_client_remediation_inputs(
        workspace,
        image_count=2,
        screen_size=(1440, 900),
        description_lines=[
            "# 关键页面说明",
            "",
            "## screen-01.png",
            "这是登录页，主按钮为登录。",
            "",
            "## screen-02.png",
            "这是工作台首页，顶部有首页导航，错误态会提示重试。",
        ],
    )

    result = _run_designos("run", skill_name, "--mode", "client", cwd=workspace, home=home)
    assert result.returncode == 2, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "Run paused at QG3." in result.stdout + result.stderr

    run_dir = workspace / "runs" / f"001-{skill_name}"
    manifest = yaml.safe_load((run_dir / "run.yaml").read_text(encoding="utf-8"))
    assert manifest["status"] == "paused"
    assert manifest["completed_at"] is None
    assert any("关键页面截图数量不足" in item for item in manifest["required_actions"] + [manifest["status_reason"]])
    remediation_dir = run_dir / "outputs" / "evidence-remediation" / "generated-notes"
    assert remediation_dir.is_dir()
    assert len(list(remediation_dir.glob("*.md"))) == 2


@pytest.mark.e2e
def test_client_auto_remediation_avoids_repeat_pause_loop_on_resume(tmp_path: Path) -> None:
    workspace = _make_workspace(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    skill_name = "client-remediation-loop"
    _make_client_remediation_skill(workspace, skill_name)
    _write_client_remediation_inputs(
        workspace,
        image_count=1,
        screen_size=(320, 200),
        description_lines=None,
    )

    first = _run_designos("run", skill_name, "--mode", "client", cwd=workspace, home=home)
    assert first.returncode == 2, f"stdout: {first.stdout}\nstderr: {first.stderr}"
    assert "Run paused at QG2." in first.stdout + first.stderr

    resumed = _run_designos(
        "resume",
        "--run-id",
        f"001-{skill_name}",
        cwd=workspace,
        home=home,
    )
    assert resumed.returncode == 1, f"stdout: {resumed.stdout}\nstderr: {resumed.stderr}"
    assert "did not change the unresolved client-evidence gap" in resumed.stdout + resumed.stderr
    assert "Run paused at" not in resumed.stdout + resumed.stderr

    manifest = yaml.safe_load((workspace / "runs" / f"001-{skill_name}" / "run.yaml").read_text(encoding="utf-8"))
    assert manifest["status"] == "failed"


@pytest.mark.e2e
def test_client_proactive_planning_allows_run_to_finish_when_inputs_already_cover_plan(tmp_path: Path) -> None:
    workspace = _make_workspace(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    skill_name = "client-planning-ready"
    _make_proactive_planning_skill(workspace, skill_name)
    _write_planned_client_inputs(
        workspace,
        filenames=[
            "登录-加载.png",
            "登录-错误.png",
            "登录-成功.png",
            "工作台首页-加载.png",
            "工作台首页-空状态.png",
            "设置页-加载.png",
            "设置页-成功.png",
            "设置页-错误.png",
            "报表列表-加载.png",
            "报表列表-空状态.png",
        ],
        description_lines=[
            "# 登录-加载.png",
            "登录页加载态。",
            "",
            "# 登录-错误.png",
            "登录页错误态。",
            "",
            "# 登录-成功.png",
            "登录成功后进入首页。",
            "",
            "# 工作台首页-加载.png",
            "工作台首页加载态。",
            "",
            "# 工作台首页-空状态.png",
            "工作台首页空状态。",
            "",
            "# 设置页-加载.png",
            "设置页加载态。",
            "",
            "# 设置页-成功.png",
            "设置页保存成功态。",
            "",
            "# 设置页-错误.png",
            "设置页错误态。",
            "",
            "# 报表列表-加载.png",
            "报表列表加载态。",
            "",
            "# 报表列表-空状态.png",
            "报表列表空状态。",
        ],
    )

    result = _run_designos("run", skill_name, "--mode", "client", cwd=workspace, home=home)
    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"

    run_dir = workspace / "runs" / f"001-{skill_name}"
    manifest = yaml.safe_load((run_dir / "run.yaml").read_text(encoding="utf-8"))
    assert manifest["status"] == "completed"
    assert [entry["id"] for entry in manifest["outputs"]] == [
        "delivery_audit_bundle",
        "issue_report",
        "html_report",
        "evidence_pack",
    ]


@pytest.mark.e2e
def test_client_proactive_planning_pauses_once_with_structured_gap_list(tmp_path: Path) -> None:
    workspace = _make_workspace(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    skill_name = "client-planning-gap"
    _make_proactive_planning_skill(workspace, skill_name)
    _write_planned_client_inputs(
        workspace,
        filenames=["login-default.png", "dashboard-default.png"],
        description_lines=None,
    )

    result = _run_designos("run", skill_name, "--mode", "client", cwd=workspace, home=home)
    assert result.returncode == 2, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "Run paused at QG0." in result.stdout + result.stderr

    run_dir = workspace / "runs" / f"001-{skill_name}"
    manifest = yaml.safe_load((run_dir / "run.yaml").read_text(encoding="utf-8"))
    assert manifest["status"] == "paused"
    assert manifest["completed_at"] is None
    assert any("设置页" in action or "报表列表" in action for action in manifest["required_actions"])
    assert any("一次性补料" in part or "关键页面" in part for part in manifest["required_actions"] + [manifest["status_reason"]])


@pytest.mark.e2e
def test_client_proactive_planning_does_not_repeat_same_pause_on_resume(tmp_path: Path) -> None:
    workspace = _make_workspace(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    skill_name = "client-planning-loop"
    _make_proactive_planning_skill(workspace, skill_name)
    _write_planned_client_inputs(
        workspace,
        filenames=["login-default.png"],
        description_lines=None,
    )

    first = _run_designos("run", skill_name, "--mode", "client", cwd=workspace, home=home)
    assert first.returncode == 2, f"stdout: {first.stdout}\nstderr: {first.stderr}"
    assert "Run paused at QG0." in first.stdout + first.stderr

    resumed = _run_designos(
        "resume",
        "--run-id",
        f"001-{skill_name}",
        cwd=workspace,
        home=home,
    )
    assert resumed.returncode == 1, f"stdout: {resumed.stdout}\nstderr: {resumed.stderr}"
    assert "same unresolved critical input gap again" in resumed.stdout + resumed.stderr
    assert "Run paused at QG0." not in resumed.stdout + resumed.stderr

    manifest = yaml.safe_load((workspace / "runs" / f"001-{skill_name}" / "run.yaml").read_text(encoding="utf-8"))
    assert manifest["status"] == "failed"
