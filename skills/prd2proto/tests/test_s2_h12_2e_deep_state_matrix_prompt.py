#!/usr/bin/env python3
"""
S2-H12.2E Tests — Deep State Matrix Prompt Hardening

验证 11-state-matrix.md 深度强化:
- 上游消费 (task/flow/page_flow/permission/exception/recovery/page_structure/component_strategy)
- 强制输出 (state_matrix_rationale/state_taxonomy等22项)
- 决策规则 (state matrix≠状态名列表/禁止happy path only/视觉留给13/14)
- Failure Mode 绑定 (FM-014/015/016)
- Quality Gate 绑定
"""

import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PROMPTS_DIR = REPO_ROOT / "skills" / "prd2proto" / "prompts-v2"


def test_11_state_matrix_contains_all_mandatory_output_fields():
    """验证 11 包含所有强制输出字段 (22项)"""
    prompt_path = PROMPTS_DIR / "11-state-matrix.md"
    assert prompt_path.exists()
    content = prompt_path.read_text(encoding='utf-8')

    mandatory_fields = [
        "state_matrix_rationale",
        "state_taxonomy",
        "page_state_matrix",
        "component_state_matrix",
        "flow_state_matrix",
        "loading_state_specs",
        "empty_state_specs",
        "error_state_specs",
        "disabled_state_specs",
        "permission_state_specs",
        "success_state_specs",
        "conflict_state_specs",
        "recovery_state_specs",
        "latency_feedback_states",
        "offline_or_retry_states",
        "state_to_component_mapping",
        "state_to_interaction_mapping",
        "state_transition_rules",
        "state_coverage_score",
        "state_coverage_gaps",
        "inferred_state_items",
        "state_matrix_confidence_score"
    ]

    for field in mandatory_fields:
        assert field in content, f"11 必须包含强制输出字段: {field}"


def test_11_state_matrix_consumes_all_upstream_stages():
    """验证 11 明确消费 01-10 的上游产物"""
    prompt_path = PROMPTS_DIR / "11-state-matrix.md"
    content = prompt_path.read_text(encoding='utf-8')

    upstream_artifacts = [
        "task_model",
        "page_flow_map",
        "permission_paths",
        "exception_paths",
        "recovery_paths",
        "page_structure_spec",
        "state_requirements",
        "component_strategy",
        "component_to_state_mapping"
    ]

    for artifact in upstream_artifacts:
        assert artifact in content, f"11 必须消费上游产物: {artifact}"


def test_11_state_matrix_not_state_name_list():
    """验证 11 明确 state matrix 不是状态名列表"""
    prompt_path = PROMPTS_DIR / "11-state-matrix.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert ("state matrix" in content.lower() or "state_matrix" in content) and \
           ("不是" in content or "not" in content.lower()) and \
           ("状态名列表" in content or "state name list" in content.lower() or "状态列表" in content)


def test_11_state_matrix_forbids_happy_path_only():
    """验证 11 明确禁止 happy path = state coverage sufficient"""
    prompt_path = PROMPTS_DIR / "11-state-matrix.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "happy path" in content.lower() or "happy_path" in content
    assert ("coverage sufficient" in content.lower() or "state_coverage_sufficient" in content) or \
           ("can_proceed_with_happy_path_only" in content or "can_claim_state_coverage_sufficient_with_happy_path" in content)
    assert "FM-014" in content


def test_11_state_matrix_requires_loading_empty_error():
    """验证 11 要求 loading / empty / error / success"""
    prompt_path = PROMPTS_DIR / "11-state-matrix.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "loading_state_specs" in content or ("loading" in content.lower() and "state" in content.lower())
    assert "empty_state_specs" in content or ("empty" in content.lower() and "state" in content.lower())
    assert "error_state_specs" in content or ("error" in content.lower() and "state" in content.lower())
    assert "success_state_specs" in content


def test_11_state_matrix_requires_permission_states():
    """验证 11 要求 permission states (granted/denied/restricted/expired)"""
    prompt_path = PROMPTS_DIR / "11-state-matrix.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "permission_state_specs" in content or "permission_states" in content
    assert "granted" in content.lower() and "denied" in content.lower()


def test_11_state_matrix_requires_recovery_states():
    """验证 11 要求 recovery states"""
    prompt_path = PROMPTS_DIR / "11-state-matrix.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "recovery_state_specs" in content or "recovery_states" in content
    assert "recovery_steps" in content or "recovery" in content.lower()


def test_11_state_matrix_requires_state_to_component_mapping():
    """验证 11 要求 state_to_component_mapping,否则不得进入high fidelity"""
    prompt_path = PROMPTS_DIR / "11-state-matrix.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "state_to_component_mapping" in content
    assert ("high fidelity" in content.lower() or "high_fidelity" in content) and \
           ("state_to_component_mapping" in content or "state matrix" in content.lower())


def test_11_state_matrix_requires_state_coverage_score():
    """验证 11 要求 state_coverage_score,低分degrade"""
    prompt_path = PROMPTS_DIR / "11-state-matrix.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "state_coverage_score" in content
    assert "low_state_coverage_score_action" in content or ("coverage" in content.lower() and "degrade" in content.lower())


def test_11_state_matrix_binds_failure_modes():
    """验证 11 绑定 FM-014 / FM-015 / FM-016"""
    prompt_path = PROMPTS_DIR / "11-state-matrix.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "FM-014" in content
    assert "FM-015" in content
    assert "FM-016" in content


def test_11_state_matrix_binds_quality_gates():
    """验证 11 绑定 input-quality-gate 和 self-review-gate"""
    prompt_path = PROMPTS_DIR / "11-state-matrix.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "Input-Quality-Gate" in content or "input-quality-gate" in content or "input_quality_gate" in content
    assert "Self-Review-Gate" in content or "self-review-gate" in content or "self_review_gate" in content
    assert "ten_domain_readiness" in content or "Domain 10" in content or "state_feedback_rules" in content


def test_11_state_matrix_requires_inferred_items_with_confidence():
    """验证 11 要求 inferred state items 标 confidence + risk_if_wrong"""
    prompt_path = PROMPTS_DIR / "11-state-matrix.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "inferred_state_items" in content
    assert "confidence" in content and ("0.0-1.0" in content or "float" in content)
    assert "risk_if_wrong" in content
    assert "validation_method" in content


def test_11_state_matrix_forbids_visual_in_stage_11():
    """验证 11 明确禁止在stage 11生成视觉样式"""
    prompt_path = PROMPTS_DIR / "11-state-matrix.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "can_generate_visual_style_in_stage_11" in content or \
           ("visual" in content.lower() and ("deferred" in content.lower() or "留给" in content) and ("13" in content or "14" in content))


def test_11_state_matrix_has_confidence_score():
    """验证 11 包含 state_matrix_confidence_score"""
    prompt_path = PROMPTS_DIR / "11-state-matrix.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "state_matrix_confidence_score" in content
    assert "overall" in content
    assert "evidence_support" in content
    assert "risk_assessment" in content


def test_11_state_matrix_decision_rules_complete():
    """验证 11 Decision Rules 包含 5 层约束"""
    prompt_path = PROMPTS_DIR / "11-state-matrix.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert ("Core Principle" in content or "state matrix 不是状态名列表" in content)
    assert ("Mandatory Outputs" in content or "强制输出" in content) and "22" in content
    assert "Upstream Consumption" in content or "上游消费" in content
    assert "Anti-Patterns" in content or "Blocker" in content
    assert "Quality Standards" in content or "质量标准" in content
    assert "Failure Mode Binding" in content and "FM-014" in content
    assert "State Coverage Rules" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
