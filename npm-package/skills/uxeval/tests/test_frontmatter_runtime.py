"""Runtime-facing frontmatter checks for the shipped uxeval skill."""

from __future__ import annotations

from kernel.skill_loader.pipeline_loader import load_pipeline_skill
from kernel.skill_loader import parse_frontmatter


def test_uxeval_frontmatter_loads_runtime_config(uxeval_skill_dir) -> None:
    skill = load_pipeline_skill(uxeval_skill_dir)

    assert skill.config.version == "1.0.0"
    assert skill.config.supported_modes == ["web", "client"]

    server_names = [server.name for server in skill.config.mcp_servers]
    assert server_names == [
        "pdf-parser",
        "excel-builder",
        "image-analyzer",
        "heuristic-engine",
        "playwright-driver",
    ]
    assert [output.id for output in skill.config.outputs] == [
        "journey_map",
        "task_checklist_full",
        "delivery_audit_bundle",
        "issue_report",
        "html_report",
        "evidence_pack",
    ]


def test_uxeval_frontmatter_declares_mode_specific_dependencies(uxeval_skill_dir) -> None:
    skill = load_pipeline_skill(uxeval_skill_dir)
    servers = {server.name: server for server in skill.config.mcp_servers}

    assert servers["image-analyzer"].required_when == 'mode == "client"'
    assert servers["image-analyzer"].requires_external[0].command == (
        "python3 {repo_root}/mcp-servers/image-analyzer/probe_ocr.py"
    )
    assert servers["playwright-driver"].required_when == 'mode == "web"'
    assert servers["playwright-driver"].requires_external[0].command == "playwright --version"


def test_uxeval_pipeline_yaml_has_no_independent_runtime_version(uxeval_skill_dir) -> None:
    pipeline_path = uxeval_skill_dir / "pipeline.yaml"
    raw = pipeline_path.read_text(encoding="utf-8")

    assert "version:" not in raw


def test_uxeval_frontmatter_declares_stage_7_artifact_types(uxeval_skill_dir) -> None:
    frontmatter, _body = parse_frontmatter(uxeval_skill_dir / "SKILL.md")
    outputs = {entry["id"]: entry for entry in frontmatter["outputs"]}

    assert outputs["delivery_audit_bundle"]["type"] == "delivery_audit_bundle"
    assert outputs["issue_report"]["type"] == "issue_report"
    assert outputs["html_report"]["type"] == "html_report"
    assert outputs["evidence_pack"]["type"] == "evidence_pack"


def test_uxeval_skill_md_describes_real_client_evidence_mode(uxeval_skill_dir) -> None:
    skill_md = (uxeval_skill_dir / "SKILL.md").read_text(encoding="utf-8")

    assert "本地证据分析工具" in skill_md
    assert "required_evidence_plan" in skill_md
    assert "evidence_input_guidance" in skill_md
    assert "evidence_assessment" in skill_md
    assert "final_delivery_ready" in skill_md
    assert "fallback_safe" in skill_md
    assert "content_description" not in skill_md
    assert "matched_task_ids" not in skill_md
