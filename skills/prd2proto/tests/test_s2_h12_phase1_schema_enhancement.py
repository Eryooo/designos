#!/usr/bin/env python3
"""
S2-H12 Phase 1 Tests — Input Diagnosis Schema Enhancement

验证 01-input-diagnosis.md 补充了10域 readiness 判定字段。
Phase 2 将补充02-17 prompts 的完整测试。
"""

import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PROMPTS_DIR = REPO_ROOT / "skills" / "prd2proto" / "prompts-v2"


def test_input_diagnosis_schema_contains_input_document_type():
    """验证 01-input-diagnosis.md schema 含 input_document_type"""
    prompt_path = PROMPTS_DIR / "01-input-diagnosis.md"
    assert prompt_path.exists()

    content = prompt_path.read_text(encoding='utf-8')

    # 验证 input_document_type 字段存在
    assert '"input_document_type"' in content, \
        "01-input-diagnosis schema 必须包含 input_document_type"

    # 验证枚举值
    assert "mrd" in content
    assert "functional_prd" in content
    assert "flow_detailed_prd" in content
    assert "page_spec_prd" in content
    assert "visual_ready_package" in content


def test_input_diagnosis_schema_contains_can_generate_prototype():
    """验证 01-input-diagnosis.md schema 含 can_generate_prototype_from_input"""
    prompt_path = PROMPTS_DIR / "01-input-diagnosis.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 验证字段存在
    assert '"can_generate_prototype_from_input"' in content, \
        "01-input-diagnosis schema 必须包含 can_generate_prototype_from_input"

    # 验证枚举值
    assert "reasoning_only" in content
    assert "partial_clickable" in content
    assert "clickable_with_gaps" in content
    assert "clickable_with_minor_gaps" in content
    assert "senior_reviewable" in content


def test_input_diagnosis_schema_contains_ten_domain_readiness():
    """验证 01-input-diagnosis.md schema 含 ten_domain_readiness"""
    prompt_path = PROMPTS_DIR / "01-input-diagnosis.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 验证字段存在
    assert '"ten_domain_readiness"' in content, \
        "01-input-diagnosis schema 必须包含 ten_domain_readiness"

    # 验证10个域的字段存在
    expected_domains = [
        "1_problem_framing",
        "2_input_critique",
        "3_goal_decomposition",
        "4_user_task_modeling",
        "5_domain_product_model",
        "6_journey_flow_state",
        "7_ia_navigation_surface",
        "8_page_interaction_design",
        "9_visual_design_system",
        "10_prototype_traceability",
    ]

    for domain in expected_domains:
        assert domain in content, \
            f"ten_domain_readiness 必须包含 {domain}"


def test_input_diagnosis_schema_contains_forced_degradation_triggers():
    """验证 01-input-diagnosis.md schema 含 forced_degradation_triggers"""
    prompt_path = PROMPTS_DIR / "01-input-diagnosis.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 验证字段存在
    assert '"forced_degradation_triggers"' in content, \
        "01-input-diagnosis schema 必须包含 forced_degradation_triggers"

    # 验证关键 trigger 存在
    assert "example_dominance_risk" in content
    assert "visual_source_missing" in content
    assert "state_coverage_gaps" in content


def test_input_diagnosis_schema_contains_missing_for_prototype():
    """验证 01-input-diagnosis.md schema 含 missing_for_X 字段"""
    prompt_path = PROMPTS_DIR / "01-input-diagnosis.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 验证字段存在
    assert '"missing_for_clickable_prototype"' in content, \
        "01-input-diagnosis schema 必须包含 missing_for_clickable_prototype"

    assert '"missing_for_senior_reviewable"' in content, \
        "01-input-diagnosis schema 必须包含 missing_for_senior_reviewable"


def test_s2_h12_audit_document_exists():
    """验证 S2-H12 审计文档存在"""
    audit_path = REPO_ROOT / "docs" / "audits" / "S2-H12-PROMPT-EXECUTION-CHAIN-HARDENING.md"
    assert audit_path.exists(), "S2-H12 审计文档必须存在"

    content = audit_path.read_text(encoding='utf-8')

    # 验证关键章节存在
    assert "## 2. Phase 1 Changes" in content
    assert "## 3. Phase 2 Remaining Work" in content
    assert "## 4. Enforcement Strategy" in content
    assert "## 9. Next Steps" in content

    # 验证说明 Phase 2 留待 S2-H12.1
    assert "Phase 2" in content
    assert "S2-H12.1" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
