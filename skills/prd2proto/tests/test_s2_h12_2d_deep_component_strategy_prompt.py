#!/usr/bin/env python3
"""
S2-H12.2D Tests — Deep Component Strategy Prompt Hardening

验证 10-component-strategy.md 深度强化:
- 上游消费 (problem/goal/product/task/flow/journey/IA/page_flow/page_structure)
- 强制输出 (component_strategy_rationale/component_to_task_mapping等18项)
- 决策规则 (component strategy≠UI library selection/禁止Antd默认拼装/visual留给13/14)
- Failure Mode 绑定 (FM-009/014/015/016)
- Quality Gate 绑定
"""

import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PROMPTS_DIR = REPO_ROOT / "skills" / "prd2proto" / "prompts-v2"


def test_10_component_strategy_contains_all_mandatory_output_fields():
    """验证 10 包含所有强制输出字段 (18项)"""
    prompt_path = PROMPTS_DIR / "10-component-strategy.md"
    assert prompt_path.exists()
    content = prompt_path.read_text(encoding='utf-8')

    mandatory_fields = [
        "component_strategy_rationale",
        "component_inventory",
        "component_to_task_mapping",
        "component_to_page_goal_mapping",
        "component_to_state_mapping",
        "component_to_data_dependency_mapping",
        "component_reuse_rationale",
        "component_variant_matrix",
        "interaction_component_contract",
        "feedback_component_contract",
        "accessibility_considerations",
        "design_system_dependency",
        "visual_dependency_boundary",
        "custom_component_candidates",
        "component_risk_assessment",
        "component_gaps",
        "inferred_component_items",
        "component_strategy_confidence_score"
    ]

    for field in mandatory_fields:
        assert field in content, f"10 必须包含强制输出字段: {field}"


def test_10_component_strategy_consumes_all_upstream_stages():
    """验证 10 明确消费 01-09 的上游产物"""
    prompt_path = PROMPTS_DIR / "10-component-strategy.md"
    content = prompt_path.read_text(encoding='utf-8')

    upstream_artifacts = [
        "problem_statement",
        "goal_tree",
        "task_model",
        "page_structure_spec",
        "page_goal",
        "primary_task_supported",
        "state_requirements",
        "content_hierarchy",
        "action_hierarchy"
    ]

    for artifact in upstream_artifacts:
        assert artifact in content, f"10 必须消费上游产物: {artifact}"


def test_10_component_strategy_not_ui_library_selection():
    """验证 10 明确 component strategy 不是 UI library selection"""
    prompt_path = PROMPTS_DIR / "10-component-strategy.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert ("component strategy" in content.lower() or "component_strategy" in content) and \
           ("不是" in content or "not" in content.lower()) and \
           ("UI library" in content or "library selection" in content.lower())


def test_10_component_strategy_forbids_antd_default_assembly():
    """验证 10 明确禁止 Antd 默认拼装 = 组件策略"""
    prompt_path = PROMPTS_DIR / "10-component-strategy.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "Antd" in content or "antd" in content.lower()
    assert ("默认" in content and "拼装" in content) or "default assembly" in content.lower()
    assert "can_antd_default_assembly_be_component_strategy" in content
    assert "FM-009" in content


def test_10_component_strategy_requires_component_to_task_mapping():
    """验证 10 要求 component_to_task_mapping"""
    prompt_path = PROMPTS_DIR / "10-component-strategy.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "component_to_task_mapping" in content
    assert "can_proceed_without_component_to_task_mapping" in content


def test_10_component_strategy_requires_component_to_state_mapping():
    """验证 10 要求 component_to_state_mapping,否则 degrade_to_lo_fi"""
    prompt_path = PROMPTS_DIR / "10-component-strategy.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "component_to_state_mapping" in content
    assert "can_proceed_without_component_to_state_mapping" in content
    assert "can_proceed_to_high_fidelity_without_state_mapping" in content
    assert "degrade" in content.lower() or "lo_fi" in content.lower()


def test_10_component_strategy_requires_accessibility():
    """验证 10 要求 accessibility_considerations"""
    prompt_path = PROMPTS_DIR / "10-component-strategy.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "accessibility_considerations" in content
    assert "keyboard" in content.lower() or "screen_reader" in content.lower()


def test_10_component_strategy_requires_design_system_dependency():
    """验证 10 要求 design_system_dependency,无source时只能structural"""
    prompt_path = PROMPTS_DIR / "10-component-strategy.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "design_system_dependency" in content
    assert "has_design_system" in content or "design_system_source" in content
    assert ("structural" in content.lower() and "visual" in content.lower()) or "structural_only" in content


def test_10_component_strategy_requires_visual_dependency_boundary():
    """验证 10 要求 visual_dependency_boundary,说明视觉留给13/14"""
    prompt_path = PROMPTS_DIR / "10-component-strategy.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "visual_dependency_boundary" in content
    assert ("13" in content and "14" in content) or "visual context" in content.lower()
    assert "not in scope" in content.lower() or "deferred" in content.lower()


def test_10_component_strategy_forbids_visual_in_stage_10():
    """验证 10 明确禁止在stage 10生成视觉风格"""
    prompt_path = PROMPTS_DIR / "10-component-strategy.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "can_generate_visual_style_in_stage_10" in content
    assert "false" in content
    assert "visual" in content.lower() and ("deferred" in content.lower() or "留给" in content)


def test_10_component_strategy_binds_failure_modes():
    """验证 10 绑定 FM-009 / FM-014 / FM-015 / FM-016"""
    prompt_path = PROMPTS_DIR / "10-component-strategy.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "FM-009" in content
    assert "FM-014" in content
    assert "FM-015" in content
    assert "FM-016" in content


def test_10_component_strategy_binds_quality_gates():
    """验证 10 绑定 input-quality-gate 和 self-review-gate"""
    prompt_path = PROMPTS_DIR / "10-component-strategy.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "Input-Quality-Gate" in content or "input-quality-gate" in content or "input_quality_gate" in content
    assert "Self-Review-Gate" in content or "self-review-gate" in content or "self_review_gate" in content
    assert "ten_domain_readiness" in content or "Domain 9" in content or "component_system" in content


def test_10_component_strategy_requires_inferred_items_with_confidence():
    """验证 10 要求 inferred component items 标 confidence + risk_if_wrong"""
    prompt_path = PROMPTS_DIR / "10-component-strategy.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "inferred_component_items" in content
    assert "confidence" in content and ("0.0-1.0" in content or "float" in content)
    assert "risk_if_wrong" in content
    assert "validation_method" in content


def test_10_component_strategy_requires_custom_component_rationale():
    """验证 10 要求 custom_component_candidates 说明为何定制"""
    prompt_path = PROMPTS_DIR / "10-component-strategy.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "custom_component_candidates" in content
    assert "why_custom" in content or "library_component_gap" in content
    assert "alternatives_rejected" in content


def test_10_component_strategy_has_confidence_score():
    """验证 10 包含 component_strategy_confidence_score"""
    prompt_path = PROMPTS_DIR / "10-component-strategy.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "component_strategy_confidence_score" in content
    assert "overall" in content
    assert "evidence_support" in content
    assert "risk_assessment" in content


def test_10_component_strategy_decision_rules_complete():
    """验证 10 Decision Rules 包含 5 层约束"""
    prompt_path = PROMPTS_DIR / "10-component-strategy.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert ("Core Principle" in content or "component strategy 不是 UI library" in content)
    assert ("Mandatory Outputs" in content or "强制输出" in content) and "18" in content
    assert "Upstream Consumption" in content or "上游消费" in content
    assert "Anti-Patterns" in content or "Blocker" in content
    assert "Quality Standards" in content or "质量标准" in content
    assert "Failure Mode Binding" in content and "FM-009" in content
    assert "Visual Dependency Boundary" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
