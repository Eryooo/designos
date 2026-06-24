#!/usr/bin/env python3
"""
S2-H11-B Integration Tests — Senior Design Execution Standard Integration

验证 product.senior-design-execution 接入 prd2proto 的完整性:
- knowledge-manifest 引用
- 10域 stage mapping
- input-quality-gate 含 10域 readiness
- self-review-gate 含 10域 critique
- failure modes 含 FM-009~016
- prompts 不含过度承诺

本测试不读取真实 PRD / evidence / prototype 产物。
"""

import pytest
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = REPO_ROOT / "skills" / "prd2proto"
KNOWLEDGE_ROOT = REPO_ROOT / "knowledge"


def test_knowledge_manifest_references_senior_design_execution():
    """验证 prd2proto knowledge-manifest 引用 product.senior-design-execution"""
    manifest_path = SKILL_ROOT / "knowledge-manifest.yaml"
    assert manifest_path.exists(), f"Missing: {manifest_path}"

    manifest = yaml.safe_load(manifest_path.read_text(encoding='utf-8'))
    shared_knowledge_ids = [item['id'] for item in manifest.get('shared_knowledge', [])]

    assert 'product.senior-design-execution' in shared_knowledge_ids, \
        "knowledge-manifest 必须引用 product.senior-design-execution"

    # 验证该条目结构
    senior_exec = next(
        (item for item in manifest['shared_knowledge'] if item['id'] == 'product.senior-design-execution'),
        None
    )
    assert senior_exec is not None
    assert 'used_by' in senior_exec, "必须声明 used_by"
    assert 'use' in senior_exec, "必须声明 use"
    assert 'stage_mapping' in senior_exec, "必须有 stage_mapping"

    # 验证 stage_mapping 包含 10 个域
    stage_mapping = senior_exec['stage_mapping']
    assert len(stage_mapping) == 10, f"stage_mapping 必须包含 10 个域,实际: {len(stage_mapping)}"

    # 验证域名称
    expected_domains = [
        "1. Problem Framing",
        "2. Input / PRD Critique",
        "3. Goal Decomposition",
        "4. User / Task Modeling",
        "5. Domain / Product Model",
        "6. Journey / Flow / State",
        "7. IA / Navigation / Surface Model",
        "8. Page / Interaction Design",
        "9. Visual / Design System / Accessibility",
        "10. Prototype / Traceability / Critique",
    ]
    actual_domains = [item['domain'] for item in stage_mapping]
    assert actual_domains == expected_domains, f"域名称不匹配"


def test_ten_domain_stage_mapping_exists():
    """验证 reference/senior-design-execution-adaptation.md 存在且含 10 域映射"""
    adaptation_path = SKILL_ROOT / "reference" / "senior-design-execution-adaptation.md"
    assert adaptation_path.exists(), f"Missing: {adaptation_path}"

    content = adaptation_path.read_text(encoding='utf-8')

    # 验证包含 10 域标题
    assert "## 1. Ten-Domain to Stage Mapping" in content
    assert "1. Problem Framing" in content
    assert "2. Input / PRD Critique" in content
    assert "3. Goal Decomposition" in content
    assert "4. User / Task Modeling" in content
    assert "5. Domain / Product Model" in content
    assert "6. Journey / Flow / State" in content
    assert "7. IA / Navigation / Surface Model" in content
    assert "8. Page / Interaction Design" in content
    assert "9. Visual / Design System / Accessibility" in content
    assert "10. Prototype / Traceability / Critique" in content

    # 验证包含关键章节
    assert "## 2. PRD-Only Input Degradation Rules" in content
    assert "## 3. Prototype Generation Capability Matrix" in content
    assert "## 4. Not-Allowed Claims" in content
    assert "## 5. Quality Gate Integration" in content


def test_input_gate_ten_domain_readiness():
    """验证 input-quality-gate 含 10 域 readiness assessment"""
    gate_path = SKILL_ROOT / "templates" / "input-quality-gate.md"
    assert gate_path.exists(), f"Missing: {gate_path}"

    content = gate_path.read_text(encoding='utf-8')

    # 验证新增 §8.1
    assert "## 8.1. Ten-Domain Readiness Assessment (S2-H11-B)" in content

    # 验证 10 域表格标题行存在
    assert "| Domain | Input Evidence Required | Input Available | Can Infer | Readiness | Degradation If Missing |" in content

    # 验证 10 域行存在
    assert "| 1. Problem Framing |" in content
    assert "| 2. Input / PRD Critique |" in content
    assert "| 3. Goal Decomposition |" in content
    assert "| 4. User / Task Modeling |" in content
    assert "| 5. Domain / Product Model |" in content
    assert "| 6. Journey / Flow / State |" in content
    assert "| 7. IA / Navigation / Surface Model |" in content
    assert "| 8. Page / Interaction Design |" in content
    assert "| 9. Visual / Design System / Accessibility |" in content
    assert "| 10. Prototype / Traceability / Critique |" in content

    # 验证 Readiness Decision Matrix
    assert "**Readiness Decision Matrix (基于10域)**:" in content

    # 验证 Forced Degradation Triggers
    assert "**Forced Degradation Triggers" in content
    assert "example_dominance_risk" in content
    assert "visual_fidelity_mode=structural_only" in content
    assert "state_coverage_gaps" in content
    assert "ia_inferred_from_features" in content


def test_self_review_gate_ten_domain_critique():
    """验证 self-review-gate 含 10 域 self critique"""
    gate_path = SKILL_ROOT / "templates" / "self-review-gate.md"
    assert gate_path.exists(), f"Missing: {gate_path}"

    content = gate_path.read_text(encoding='utf-8')

    # 验证新增 §9.1
    assert "## 9.1. Ten-Domain Self Critique (S2-H11-B)" in content

    # 验证 10 域表格标题行存在
    assert "| Domain | Delivered Artifact | Quality Check Question | Pass Criteria | Evidence | Blocker If Failed |" in content

    # 验证 10 域行存在
    assert "| 1. Problem Framing |" in content and "design_objectives.problem_statement" in content
    assert "| 2. Input / PRD Critique |" in content and "input_diagnosis.readiness_decision" in content
    assert "| 3. Goal Decomposition |" in content and "design_objectives.goal_tree" in content
    assert "| 4. User / Task Modeling |" in content and "user_task_map.roles/tasks" in content
    assert "| 5. Domain / Product Model |" in content and "product_archetype.foundation/modules" in content
    assert "| 6. Journey / Flow / State |" in content and "state_matrix.states" in content
    assert "| 7. IA / Navigation / Surface |" in content and "information_architecture.ia_rationale" in content
    assert "| 8. Page / Interaction Design |" in content and "page_structure.state_coverage" in content
    assert "| 9. Visual / Design System / Accessibility |" in content and "design_spec.visual_source_status" in content
    assert "| 10. Prototype / Traceability / Critique |" in content and "traceability_map.coverage" in content

    # 验证 Verdict Calibration Matrix
    assert "**Verdict Calibration Matrix (基于10域)**:" in content
    assert "partial_clickable_prototype" in content
    assert "clickable_prototype_ready_with_gaps" in content
    assert "senior_review_ready" in content

    # 验证 Blocker Detection
    assert "**Blocker Detection" in content
    assert "FM-009" in content  # PRD直转页面
    assert "FM-011" in content  # 缺Problem Framing
    assert "FM-015" in content  # Verdict Inflation


def test_failure_modes_senior_execution_gaps():
    """验证 failure-modes.md 含 FM-009~016"""
    fm_path = SKILL_ROOT / "eval" / "failure" / "failure-modes.md"
    assert fm_path.exists(), f"Missing: {fm_path}"

    content = fm_path.read_text(encoding='utf-8')

    # 验证新增 FM-009~016 存在
    new_fms = [
        "FM-PRD2PROTO-009",  # PRD直转页面
        "FM-PRD2PROTO-010",  # Example Flow Dominance
        "FM-PRD2PROTO-011",  # Missing Problem Framing
        "FM-PRD2PROTO-012",  # Missing Product/Domain Model
        "FM-PRD2PROTO-013",  # IA Unsupported By Evidence
        "FM-PRD2PROTO-014",  # State Coverage Illusion
        "FM-PRD2PROTO-015",  # Clickable Prototype Verdict Inflation
        "FM-PRD2PROTO-016",  # Visual Polish Overclaim
    ]

    for fm_id in new_fms:
        assert fm_id in content, f"Missing failure mode: {fm_id}"

        # 验证每个 FM 含必需字段
        fm_section_start = content.find(f"## {fm_id}")
        assert fm_section_start > 0, f"{fm_id} 未找到章节标题"

        # 提取该 FM 章节(到下一个 ## 或文件末尾)
        next_section = content.find("\n## ", fm_section_start + 1)
        if next_section == -1:
            fm_section = content[fm_section_start:]
        else:
            fm_section = content[fm_section_start:next_section]

        # 验证必需字段
        required_fields = [
            "- **id**:",
            "- **name**:",
            "- **severity**:",
            "- **detection_signal**:",
            "- **trigger_condition**:",
            "- **related_kr**:",
            "- **source_reference**:",
            "- **self_review_question**:",
            "- **remediation**:",
            "- **not_allowed_claims**:",
        ]
        for field in required_fields:
            assert field in fm_section, f"{fm_id} 缺失字段: {field}"

    # 验证汇总表更新
    assert "| **合计** | **16** |" in content, "汇总表应显示 16 个 FM(原8个+新8个)"


def test_prompts_no_prd_to_page_shortcut():
    """验证 prompts-v2 不含 PRD 直转页面的过度承诺"""
    prompts_dir = SKILL_ROOT / "prompts-v2"
    assert prompts_dir.exists()

    forbidden_phrases = [
        "直接生成完整页面",
        "直接生成完整原型",
        "一步生成",
        "自动生成完整",
        "完全自动化",
        "production ready",
        "已达资深",
    ]

    for prompt_file in prompts_dir.glob("*.md"):
        if prompt_file.name == "README.md":
            continue

        content = prompt_file.read_text(encoding='utf-8')

        for phrase in forbidden_phrases:
            assert phrase not in content, \
                f"{prompt_file.name} 含过度承诺: '{phrase}'"


def test_shared_knowledge_senior_design_execution_exists():
    """验证 shared knowledge 中 product.senior-design-execution 存在"""
    knowledge_file = KNOWLEDGE_ROOT / "product" / "senior-design-execution.md"
    assert knowledge_file.exists(), f"Missing: {knowledge_file}"

    content = knowledge_file.read_text(encoding='utf-8')

    # 验证包含 10 个执行域
    assert "### 1. Problem Framing" in content
    assert "### 2. Input / PRD Critique" in content
    assert "### 3. Goal Decomposition" in content
    assert "### 4. User / Task Modeling" in content
    assert "### 5. Domain / Product Model" in content
    assert "### 6. Journey / Flow / State" in content
    assert "### 7. IA / Navigation / Surface Model" in content
    assert "### 8. Page / Interaction Design" in content
    assert "### 9. Visual / Design System / Accessibility" in content
    assert "### 10. Prototype / Traceability / Critique" in content

    # 验证包含标准章节
    assert "## purpose" in content
    assert "## decision_framework" in content
    assert "## quality_rubric" in content
    assert "## not_allowed_claims" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
