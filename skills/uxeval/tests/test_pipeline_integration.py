"""UXEval Skill integration tests.

Verifies:
1. SKILL.md frontmatter parses correctly
2. pipeline.yaml is loadable by the kernel SkillLoader
3. constitution.md exists and contains required rules
4. All referenced prompts and reference files exist
5. The pipeline can be invoked through the kernel with mock LLM/MCP
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from kernel.contracts.enums import SkillType, StageType
from kernel.skill_loader.pipeline_loader import load_pipeline_skill


# ---------------------------------------------------------------------------
# Static structure tests (no kernel runtime needed)
# ---------------------------------------------------------------------------


def test_skill_md_exists(uxeval_skill_dir: Path) -> None:
    assert (uxeval_skill_dir / "SKILL.md").exists()


def test_pipeline_yaml_exists(uxeval_skill_dir: Path) -> None:
    assert (uxeval_skill_dir / "pipeline.yaml").exists()


def test_constitution_exists(uxeval_skill_dir: Path) -> None:
    assert (uxeval_skill_dir / "constitution.md").exists()


def test_constitution_has_seven_rules(uxeval_skill_dir: Path) -> None:
    content = (uxeval_skill_dir / "constitution.md").read_text(encoding="utf-8")
    # Look for rules numbered 1-7
    for i in range(1, 8):
        assert f"## {i}." in content, f"Missing rule #{i} in constitution.md"


def test_reference_index_loads(uxeval_skill_dir: Path) -> None:
    index_path = uxeval_skill_dir / "reference" / "index.json"
    assert index_path.exists()
    data = json.loads(index_path.read_text(encoding="utf-8"))
    assert data["skill"] == "uxeval"
    assert len(data["documents"]) >= 6


def test_all_reference_docs_exist(uxeval_skill_dir: Path) -> None:
    index_path = uxeval_skill_dir / "reference" / "index.json"
    data = json.loads(index_path.read_text(encoding="utf-8"))
    for doc in data["documents"]:
        ref_file = uxeval_skill_dir / "reference" / doc["path"]
        assert ref_file.exists(), f"Missing reference doc: {doc['path']}"


def test_all_prompts_exist(uxeval_skill_dir: Path) -> None:
    expected_prompts = [
        "01-prd-understanding.md",
        "02-principle-mapping.md",
        "03-journey-modeling.md",
        "04-task-generation.md",
        "05a-script-generation.md",
        "05b-screenshot-analysis.md",
        "05c-conflict-analysis.md",
        "06-issue-attribution.md",
    ]
    prompts_dir = uxeval_skill_dir / "prompts"
    for name in expected_prompts:
        assert (prompts_dir / name).exists(), f"Missing prompt: {name}"


def test_all_templates_exist(uxeval_skill_dir: Path) -> None:
    expected_templates = [
        "旅程地图.md",
        "任务清单-完整版.md",
        "任务清单-简洁版.md",
        "问题报告.md",
        "scope.md",
    ]
    templates_dir = uxeval_skill_dir / "templates"
    for name in expected_templates:
        assert (templates_dir / name).exists(), f"Missing template: {name}"


def test_golden_case_001_exists(uxeval_skill_dir: Path) -> None:
    case_dir = uxeval_skill_dir / "eval" / "golden" / "case-001-分类分级"
    assert case_dir.exists()
    assert (case_dir / "annotations.yaml").exists()
    assert (case_dir / "input" / "prd.md").exists()
    assert (case_dir / "input" / "scope.md").exists()
    assert (case_dir / "expected" / "06-问题清单.md").exists()


def test_failure_case_F001_exists(uxeval_skill_dir: Path) -> None:
    f_dir = uxeval_skill_dir / "eval" / "failure" / "F001-功能测试偏移"
    assert f_dir.exists()
    assert (f_dir / "what-happened.md").exists()
    assert (f_dir / "root-cause.md").exists()
    assert (f_dir / "how-to-detect.md").exists()


# ---------------------------------------------------------------------------
# Pipeline-level structural validation
# ---------------------------------------------------------------------------


def test_pipeline_yaml_parses(uxeval_skill_dir: Path) -> None:
    """pipeline.yaml is valid YAML with required top-level keys."""
    pipeline = yaml.safe_load((uxeval_skill_dir / "pipeline.yaml").read_text(encoding="utf-8"))
    assert pipeline["name"] == "uxeval-pipeline"
    assert "version" not in pipeline
    assert "stages" in pipeline
    assert isinstance(pipeline["stages"], list)
    assert len(pipeline["stages"]) >= 6, "Expected at least 6 stages per ADR-002"


def test_pipeline_has_three_checkpoints(uxeval_skill_dir: Path) -> None:
    """C1, C2, C3 checkpoints must be present."""
    pipeline = yaml.safe_load((uxeval_skill_dir / "pipeline.yaml").read_text(encoding="utf-8"))
    checkpoint_ids: set[str] = set()
    for stage in pipeline["stages"]:
        cp = stage.get("checkpoint")
        if cp and "id" in cp:
            checkpoint_ids.add(cp["id"])
    assert {"C1", "C2", "C3"}.issubset(checkpoint_ids), (
        f"Expected C1/C2/C3, got {checkpoint_ids}"
    )


def test_pipeline_has_mode_branches(uxeval_skill_dir: Path) -> None:
    """Web mode and client mode branches must exist."""
    pipeline = yaml.safe_load((uxeval_skill_dir / "pipeline.yaml").read_text(encoding="utf-8"))
    web_only = [s for s in pipeline["stages"] if s.get("only_when") == 'mode == "web"']
    client_only = [s for s in pipeline["stages"] if s.get("only_when") == 'mode == "client"']
    assert len(web_only) >= 2, "Expected ≥ 2 web-only stages (script-gen + automation)"
    assert len(client_only) >= 1, "Expected ≥ 1 client-only stage (screenshot-loading)"


def test_pipeline_constitution_reference(uxeval_skill_dir: Path) -> None:
    pipeline = yaml.safe_load((uxeval_skill_dir / "pipeline.yaml").read_text(encoding="utf-8"))
    assert pipeline.get("constitution") == "constitution.md"


# ---------------------------------------------------------------------------
# SkillLoader integration
# ---------------------------------------------------------------------------


def test_skill_loads_via_pipeline_loader(uxeval_skill_dir: Path) -> None:
    """Kernel can load uxeval as a Pipeline Skill."""
    skill = load_pipeline_skill(uxeval_skill_dir)
    assert skill.name == "uxeval"
    assert skill.skill_type == SkillType.PIPELINE
    assert skill.config.version == "1.0.0"
    assert "web" in skill.config.supported_modes
    assert "client" in skill.config.supported_modes


def test_skill_stages_loaded(uxeval_skill_dir: Path) -> None:
    """All stages parse into StageConfig successfully."""
    skill = load_pipeline_skill(uxeval_skill_dir)
    stages = skill.get_stages()
    stage_ids = [s.id for s in stages]
    expected_ids = {
        "prd-understanding",
        "principle-mapping",
        "journey-modeling",
        "task-generation",
        "evidence-planning",
        "task-script-generation",
        "web-automation",
        "screenshot-loading",
        "prd-screenshot-conflict",
        "issue-attribution",
        "report-generation",
    }
    assert expected_ids.issubset(set(stage_ids)), (
        f"Missing stages: {expected_ids - set(stage_ids)}"
    )


def test_stage_types_correct(uxeval_skill_dir: Path) -> None:
    """LLM stages and tool stages are correctly typed."""
    skill = load_pipeline_skill(uxeval_skill_dir)
    stages = {s.id: s for s in skill.get_stages()}
    assert stages["prd-understanding"].type == StageType.LLM
    assert stages["screenshot-loading"].type == StageType.TOOL
    assert stages["web-automation"].type == StageType.TOOL
    assert stages["report-generation"].type == StageType.TOOL


def test_report_generation_declares_real_stage_outputs(uxeval_skill_dir: Path) -> None:
    """Stage 7 declares the same-named outputs consumed by the runtime."""
    skill = load_pipeline_skill(uxeval_skill_dir)
    stages = {s.id: s for s in skill.get_stages()}

    assert stages["report-generation"].outputs == [
        "issue_report",
        "html_report",
        "evidence_pack",
    ]


def test_screenshot_loading_declares_evidence_assessment_output(uxeval_skill_dir: Path) -> None:
    skill = load_pipeline_skill(uxeval_skill_dir)
    stages = {s.id: s for s in skill.get_stages()}

    assert stages["evidence-planning"].outputs == [
        "capture_mission",
        "required_evidence_plan",
        "critical_page_requirements",
        "critical_state_requirements",
        "evidence_input_guidance",
    ]
    assert stages["screenshot-loading"].outputs == [
        "screenshots",
        "image_analysis",
        "evidence_assessment",
    ]
    assert stages["screenshot-loading"].inputs == [
        "screenshots_dir",
        "task_checklist_lite",
        "required_evidence_plan",
    ]


def test_client_mode_prompts_do_not_depend_on_fake_semantic_fields(uxeval_skill_dir: Path) -> None:
    forbidden = [
        "content_description",
        "matched_task_ids",
        "matched_module_id",
        "sensitive_info_detected",
    ]
    prompt_05b = (uxeval_skill_dir / "prompts" / "05b-screenshot-analysis.md").read_text(encoding="utf-8")
    prompt_05c = (uxeval_skill_dir / "prompts" / "05c-conflict-analysis.md").read_text(encoding="utf-8")
    prompt_06 = (uxeval_skill_dir / "prompts" / "06-issue-attribution.md").read_text(encoding="utf-8")

    for token in forbidden:
        assert token not in prompt_05b
        assert token not in prompt_05c
        assert token not in prompt_06


def test_client_mode_prompts_reference_real_text_evidence_contract(uxeval_skill_dir: Path) -> None:
    prompt_05b = (uxeval_skill_dir / "prompts" / "05b-screenshot-analysis.md").read_text(encoding="utf-8")
    prompt_05c = (uxeval_skill_dir / "prompts" / "05c-conflict-analysis.md").read_text(encoding="utf-8")
    prompt_06 = (uxeval_skill_dir / "prompts" / "06-issue-attribution.md").read_text(encoding="utf-8")

    assert "text_evidence_inventory" in prompt_05b
    assert "ocr_text_preview" in prompt_05b
    assert "evidence_assessment" in prompt_05b
    assert "semantic_analysis_available" in prompt_05b
    assert "final_delivery_ready" in prompt_05b
    assert "fallback_safe" in prompt_05b
    assert "required_evidence_plan" in prompt_05b
    assert "evidence_assessment" in prompt_05c
    assert "delivery_status" in prompt_05c
    assert "page_title_candidates" in prompt_06
    assert "evidence_assessment" in prompt_06
    assert "[证据不足]" in prompt_06
    assert "unverified_issues" in prompt_06
    assert "delivery_assessment" in prompt_06
    assert "runtime 不会允许生成最终 issue_report / html_report" in prompt_06


def test_checkpoints_in_stage_config(uxeval_skill_dir: Path) -> None:
    """Stages with checkpoint config keep them after parsing."""
    skill = load_pipeline_skill(uxeval_skill_dir)
    stages = {s.id: s for s in skill.get_stages()}
    assert stages["journey-modeling"].checkpoint is not None
    assert stages["journey-modeling"].checkpoint.id == "C1"
    assert stages["task-generation"].checkpoint is not None
    assert stages["task-generation"].checkpoint.id == "C2"
    assert stages["issue-attribution"].checkpoint is not None
    assert stages["issue-attribution"].checkpoint.id == "C3"


def test_only_when_clauses_preserved(uxeval_skill_dir: Path) -> None:
    """Mode branching expressions survive YAML → StageConfig roundtrip."""
    skill = load_pipeline_skill(uxeval_skill_dir)
    stages = {s.id: s for s in skill.get_stages()}
    assert stages["task-script-generation"].only_when == 'mode == "web"'
    assert stages["evidence-planning"].only_when == 'mode == "client"'
    assert stages["screenshot-loading"].only_when == 'mode == "client"'


def test_client_evidence_quality_gates_are_declared(uxeval_skill_dir: Path) -> None:
    skill = load_pipeline_skill(uxeval_skill_dir)
    stages = {s.id: s for s in skill.get_stages()}

    conflict_gate = stages["prd-screenshot-conflict"].gate
    issue_gate = stages["issue-attribution"].gate
    audit_stage = stages["delivery-audit"]
    report_gate = stages["report-generation"].gate

    assert stages["evidence-planning"].type.value == "tool"
    assert stages["evidence-planning"].mcp_server == "image-analyzer"
    assert stages["evidence-planning"].mcp_tool == "plan_required_evidence"

    screenshot_gate = stages["screenshot-loading"].gate
    assert screenshot_gate is not None
    assert screenshot_gate.when == 'evidence_input_guidance.pre_run_status in ["supplement_required", "blocked"]'
    assert screenshot_gate.resume_from_stage == "evidence-planning"

    assert conflict_gate is not None
    assert conflict_gate.when == 'evidence_assessment.delivery_status == "blocked"'
    assert conflict_gate.resume_from_stage == "screenshot-loading"

    assert issue_gate is not None
    assert issue_gate.when == 'evidence_assessment.delivery_status in ["blocked", "supplement_required"]'
    assert issue_gate.resume_from_stage == "screenshot-loading"

    assert audit_stage.type.value == "tool"
    assert audit_stage.mcp_server == "excel-builder"
    assert audit_stage.mcp_tool == "audit_delivery_readiness"
    assert audit_stage.inputs == [
        "issues",
        "unverified_issues",
        "evidence_assessment",
        "delivery_assessment",
        "capture_mission",
    ]
    assert audit_stage.outputs == [
        "audited_delivery_assessment",
        "delivery_audit_bundle",
    ]

    assert report_gate is not None
    assert report_gate.when == 'audited_delivery_assessment.delivery_status != "final_delivery_ready"'
    assert report_gate.resume_from_stage == "screenshot-loading"


def test_issue_attribution_declares_unverified_and_delivery_outputs(uxeval_skill_dir: Path) -> None:
    skill = load_pipeline_skill(uxeval_skill_dir)
    stages = {s.id: s for s in skill.get_stages()}

    assert stages["issue-attribution"].outputs == [
        "raw_issues",
        "issues",
        "unverified_issues",
        "delivery_assessment",
    ]


def test_prompt_files_resolved(uxeval_skill_dir: Path) -> None:
    """Loader resolves prompt paths to absolute existing files."""
    skill = load_pipeline_skill(uxeval_skill_dir)
    stages = {s.id: s for s in skill.get_stages()}
    prd_stage = stages["prd-understanding"]
    assert prd_stage.prompt is not None
    assert prd_stage.prompt.exists()


def test_knowledge_files_resolved(uxeval_skill_dir: Path) -> None:
    """Reference knowledge paths resolve to existing markdown files."""
    skill = load_pipeline_skill(uxeval_skill_dir)
    stages = {s.id: s for s in skill.get_stages()}
    prd_stage = stages["prd-understanding"]
    assert len(prd_stage.knowledge) >= 1
    for kpath in prd_stage.knowledge:
        assert kpath.exists(), f"Missing knowledge file: {kpath}"


# ---------------------------------------------------------------------------
# Annotation file integrity
# ---------------------------------------------------------------------------


def test_golden_annotations_parse(uxeval_skill_dir: Path) -> None:
    """Golden case annotations.yaml has the expected scoring schema."""
    annotations_path = (
        uxeval_skill_dir / "eval" / "golden" / "case-001-分类分级" / "annotations.yaml"
    )
    data = yaml.safe_load(annotations_path.read_text(encoding="utf-8"))
    assert data["case_id"] == "case-001-分类分级"
    assert data["mode"] == "client"
    assert data["fictional"] is True
    assert "dimensions" in data
    assert "scoring" in data
    assert "weight" in data["scoring"]
    assert "pass_threshold" in data["scoring"]


def test_promptfoo_yaml_exists(uxeval_skill_dir: Path) -> None:
    yaml_path = uxeval_skill_dir / "eval" / "promptfoo.yaml"
    assert yaml_path.exists()
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    assert "prompts" in data
    assert "tests" in data
    assert len(data["tests"]) >= 5


# ---------------------------------------------------------------------------
# Constitution rule mention test
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rule_keyword",
    [
        "evidence_refs",        # Rule #1
        "敏感信息",              # Rule #2
        "critical / major / minor / suggestion",  # Rule #3
        "功能存在与否",          # Rule #4
        "可执行",                # Rule #5
        "用户影响",              # Rule #6
        "source_basis",          # Rule #7
    ],
)
def test_constitution_mentions_rule(uxeval_skill_dir: Path, rule_keyword: str) -> None:
    content = (uxeval_skill_dir / "constitution.md").read_text(encoding="utf-8")
    assert rule_keyword in content, f"Constitution missing keyword: {rule_keyword}"
