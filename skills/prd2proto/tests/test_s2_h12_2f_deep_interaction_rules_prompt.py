#!/usr/bin/env python3
"""
S2-H12.2F Tests — Deep Interaction Rules Prompt Hardening

验证 12-interaction-rules.md 深度强化:
- 上游消费 (task/flow/page_flow/permission/exception/recovery/page_structure/component_strategy/state_matrix)
- 强制输出 (interaction_rules_rationale等21项)
- 决策规则 (interaction rules≠点击跳转/必须有trigger/feedback/validation/success/failure/recovery)
- Failure Mode 绑定 (FM-009/014/015/016)
- Quality Gate 绑定
"""

import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PROMPTS_DIR = REPO_ROOT / "skills" / "prd2proto" / "prompts-v2"


def test_12_interaction_rules_contains_all_mandatory_output_fields():
    """验证 12 包含所有强制输出字段 (21项)"""
    prompt_path = PROMPTS_DIR / "12-interaction-rules.md"
    assert prompt_path.exists()
    content = prompt_path.read_text(encoding='utf-8')

    mandatory_fields = [
        "interaction_rules_rationale",
        "interaction_rule_inventory",
        "trigger_feedback_mapping",
        "validation_rules",
        "error_recovery_rules",
        "confirmation_rules",
        "irreversible_action_rules",
        "permission_interaction_rules",
        "latency_feedback_rules",
        "keyboard_accessibility_rules",
        "focus_management_rules",
        "gesture_or_shortcut_rules",
        "form_interaction_rules",
        "navigation_interaction_rules",
        "state_transition_interaction_rules",
        "interaction_to_state_mapping",
        "interaction_to_component_mapping",
        "interaction_risk_assessment",
        "interaction_gaps",
        "inferred_interaction_items",
        "interaction_rules_confidence_score"
    ]

    for field in mandatory_fields:
        assert field in content, f"12 必须包含强制输出字段: {field}"


def test_12_interaction_rules_consumes_all_upstream_stages():
    """验证 12 明确消费 01-11 的上游产物"""
    prompt_path = PROMPTS_DIR / "12-interaction-rules.md"
    content = prompt_path.read_text(encoding='utf-8')

    upstream_artifacts = [
        "task_model",
        "page_flow_map",
        "permission_paths",
        "exception_paths",
        "recovery_paths",
        "page_structure_spec",
        "action_hierarchy",
        "component_strategy",
        "state_matrix",
        "state_to_component_mapping",
        "state_transition_rules"
    ]

    for artifact in upstream_artifacts:
        assert artifact in content, f"12 必须消费上游产物: {artifact}"


def test_12_interaction_rules_not_click_jump():
    """验证 12 明确 interaction rules 不是点击跳转"""
    prompt_path = PROMPTS_DIR / "12-interaction-rules.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert ("interaction rules" in content.lower() or "interaction_rules" in content) and \
           ("不是" in content or "not" in content.lower()) and \
           ("点击" in content and ("跳转" in content or "按钮" in content))


def test_12_interaction_rules_requires_trigger_feedback_validation():
    """验证 12 要求每个关键action有 trigger/feedback/validation/success/failure/recovery"""
    prompt_path = PROMPTS_DIR / "12-interaction-rules.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "trigger_feedback_mapping" in content
    assert "validation_rules" in content
    assert ("success" in content.lower() and "failure" in content.lower() and "recovery" in content.lower())


def test_12_interaction_rules_requires_error_recovery():
    """验证 12 要求 error_recovery_rules,否则不得称interaction complete"""
    prompt_path = PROMPTS_DIR / "12-interaction-rules.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "error_recovery_rules" in content
    assert ("can_claim_interaction_complete_without_error_recovery" in content or \
            ("error" in content.lower() and "recovery" in content.lower() and "complete" in content.lower()))


def test_12_interaction_rules_requires_confirmation():
    """验证 12 要求 confirmation_rules / irreversible_action_rules"""
    prompt_path = PROMPTS_DIR / "12-interaction-rules.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "confirmation_rules" in content
    assert "irreversible_action_rules" in content
    assert "二次确认" in content or "confirmation" in content.lower()


def test_12_interaction_rules_requires_keyboard_accessibility():
    """验证 12 要求 keyboard_accessibility_rules / focus_management_rules"""
    prompt_path = PROMPTS_DIR / "12-interaction-rules.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "keyboard_accessibility_rules" in content or "keyboard_rules" in content
    assert "focus_management_rules" in content
    assert "Tab" in content or "Enter" in content or "Escape" in content


def test_12_interaction_rules_requires_interaction_to_state_mapping():
    """验证 12 要求 interaction_to_state_mapping,否则不得进入clickable prototype"""
    prompt_path = PROMPTS_DIR / "12-interaction-rules.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "interaction_to_state_mapping" in content
    assert ("can_proceed_to_clickable_without_interaction_state_mapping" in content or \
            ("interaction" in content.lower() and "state" in content.lower() and ("clickable" in content.lower() or "prototype" in content.lower())))


def test_12_interaction_rules_requires_permission_interaction():
    """验证 12 要求 permission_interaction_rules"""
    prompt_path = PROMPTS_DIR / "12-interaction-rules.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "permission_interaction_rules" in content
    assert ("granted" in content.lower() and "denied" in content.lower()) or "permission" in content.lower()


def test_12_interaction_rules_requires_latency_feedback():
    """验证 12 要求 latency_feedback_rules"""
    prompt_path = PROMPTS_DIR / "12-interaction-rules.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "latency_feedback_rules" in content
    assert ("100ms" in content or "latency" in content.lower() or "延迟" in content)


def test_12_interaction_rules_binds_failure_modes():
    """验证 12 绑定 FM-009 / FM-014 / FM-015 / FM-016"""
    prompt_path = PROMPTS_DIR / "12-interaction-rules.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "FM-009" in content
    assert "FM-014" in content
    assert "FM-015" in content
    assert "FM-016" in content


def test_12_interaction_rules_binds_quality_gates():
    """验证 12 绑定 input-quality-gate 和 self-review-gate"""
    prompt_path = PROMPTS_DIR / "12-interaction-rules.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "Input-Quality-Gate" in content or "input-quality-gate" in content or "input_quality_gate" in content
    assert "Self-Review-Gate" in content or "self-review-gate" in content or "self_review_gate" in content
    assert "ten_domain_readiness" in content or "Domain 11" in content or "interaction_feedback" in content


def test_12_interaction_rules_requires_inferred_items_with_confidence():
    """验证 12 要求 inferred interaction items 标 confidence + risk_if_wrong"""
    prompt_path = PROMPTS_DIR / "12-interaction-rules.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "inferred_interaction_items" in content
    assert "confidence" in content and ("0.0-1.0" in content or "float" in content)
    assert "risk_if_wrong" in content
    assert "validation_method" in content


def test_12_interaction_rules_forbids_visual_in_stage_12():
    """验证 12 明确禁止在stage 12生成视觉样式"""
    prompt_path = PROMPTS_DIR / "12-interaction-rules.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "can_generate_visual_style_in_stage_12" in content or \
           ("visual" in content.lower() and ("deferred" in content.lower() or "留给" in content) and ("13" in content or "14" in content))


def test_12_interaction_rules_has_confidence_score():
    """验证 12 包含 interaction_rules_confidence_score"""
    prompt_path = PROMPTS_DIR / "12-interaction-rules.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "interaction_rules_confidence_score" in content
    assert "overall" in content
    assert "evidence_support" in content
    assert "risk_assessment" in content


def test_12_interaction_rules_decision_rules_complete():
    """验证 12 Decision Rules 包含 5 层约束"""
    prompt_path = PROMPTS_DIR / "12-interaction-rules.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert ("Core Principle" in content or "interaction rules 不是" in content)
    assert ("Mandatory Outputs" in content or "强制输出" in content) and "21" in content
    assert "Upstream Consumption" in content or "上游消费" in content
    assert "Anti-Patterns" in content or "Blocker" in content
    assert "Quality Standards" in content or "质量标准" in content
    assert "Failure Mode Binding" in content and "FM-009" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
