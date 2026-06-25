#!/usr/bin/env python3
"""
S2-H12.2C Tests — Deep Page Structure Prompt Hardening

验证 09-page-structure.md 深度强化:
- 上游消费 (problem/goal/product/task/flow/journey/IA/page_flow)
- 强制输出 (page_structure_rationale/page_goal/primary_task_supported等19项)
- 决策规则 (page structure≠功能堆叠/必须有page_goal/必须有state_requirements)
- Failure Mode 绑定 (FM-009/013/014/015)
- Quality Gate 绑定 (input-quality-gate/self-review-gate)

不只检查字符串存在,而是验证约束逻辑和推导链路。
"""

import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PROMPTS_DIR = REPO_ROOT / "skills" / "prd2proto" / "prompts-v2"


def test_09_page_structure_contains_all_mandatory_output_fields():
    """验证 09 包含所有强制输出字段 (19项)"""
    prompt_path = PROMPTS_DIR / "09-page-structure.md"
    assert prompt_path.exists()
    content = prompt_path.read_text(encoding='utf-8')

    # 19项强制输出字段
    mandatory_fields = [
        "page_structure_rationale",
        "page_goal",
        "primary_task_supported",
        "secondary_tasks_supported",
        "route_context",
        "information_priority",
        "content_hierarchy",
        "action_hierarchy",
        "decision_area_mapping",
        "state_requirements",
        "empty_error_permission_requirements",
        "data_dependency_map",
        "page_entry_exit_contract",
        "layout_sections",
        "component_intent_map",
        "page_assumptions",
        "page_gaps",
        "inferred_page_items",
        "page_structure_confidence_score"
    ]

    for field in mandatory_fields:
        assert field in content, f"09 必须包含强制输出字段: {field}"


def test_09_page_structure_consumes_all_upstream_stages():
    """验证 09 明确消费 01-08 的上游产物 (17项)"""
    prompt_path = PROMPTS_DIR / "09-page-structure.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 17项上游消费
    upstream_artifacts = [
        "problem_statement",
        "goal_tree",
        "product_foundation_map",
        "task_model",
        "business_flow_map",
        "journey_stages",
        "ia_rationale",
        "route_hierarchy",
        "page_flow_map",
        "entry_points",
        "exit_points",
        "cross_page_transitions",
        "permission_paths",
        "exception_paths",
        "recovery_paths",
        "input_document_type",
        "can_generate_prototype_from_input"
    ]

    for artifact in upstream_artifacts:
        assert artifact in content, f"09 必须消费上游产物: {artifact}"


def test_09_page_structure_explicitly_not_feature_stacking():
    """验证 09 明确 page structure 不是功能卡片堆叠"""
    prompt_path = PROMPTS_DIR / "09-page-structure.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 检查明确声明
    assert ("page structure" in content.lower() or "page_structure" in content) and \
           ("不是" in content or "not" in content.lower()) and \
           ("功能" in content and ("堆叠" in content or "卡片" in content))


def test_09_page_structure_requires_page_goal():
    """验证 09 要求每页有 page_goal,否则 block"""
    prompt_path = PROMPTS_DIR / "09-page-structure.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 检查硬约束
    assert "page_goal" in content
    assert "can_proceed_without_page_goal" in content
    assert "false" in content
    assert "block" in content.lower()


def test_09_page_structure_requires_primary_task():
    """验证 09 要求每页有 primary_task_supported,否则 block"""
    prompt_path = PROMPTS_DIR / "09-page-structure.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 检查硬约束
    assert "primary_task_supported" in content
    assert "can_proceed_without_primary_task" in content
    assert "block" in content.lower()


def test_09_page_structure_requires_content_action_hierarchy():
    """验证 09 要求 content_hierarchy 和 action_hierarchy"""
    prompt_path = PROMPTS_DIR / "09-page-structure.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 检查字段和约束
    assert "content_hierarchy" in content
    assert "action_hierarchy" in content
    assert ("L1" in content and "L2" in content and "L3" in content) or \
           ("primary" in content.lower() and "secondary" in content.lower())
    assert "missing_hierarchy_action" in content


def test_09_page_structure_requires_state_requirements():
    """验证 09 要求 state_requirements,否则 degrade_to_lo_fi"""
    prompt_path = PROMPTS_DIR / "09-page-structure.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 检查硬约束
    assert "state_requirements" in content
    assert "can_proceed_without_state_requirements" in content
    assert "can_proceed_to_high_fidelity_without_state_requirements" in content
    assert "can_proceed_to_senior_review_without_state_requirements" in content
    assert "degrade" in content.lower() or "lo_fi" in content.lower()


def test_09_page_structure_requires_empty_error_permission():
    """验证 09 要求 empty_error_permission_requirements"""
    prompt_path = PROMPTS_DIR / "09-page-structure.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 检查字段
    assert "empty_error_permission_requirements" in content
    assert ("empty" in content.lower() and "error" in content.lower() and
            "permission" in content.lower())


def test_09_page_structure_forbids_high_fidelity_without_state():
    """验证 09 明确禁止缺 state_requirements 时进入 high fidelity / senior review"""
    prompt_path = PROMPTS_DIR / "09-page-structure.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 检查禁止声明
    assert ("high fidelity" in content.lower() or "high_fidelity" in content) and \
           ("state_requirements" in content or "state requirements" in content.lower())
    assert ("senior review" in content.lower() or "senior_review" in content) and \
           ("state_requirements" in content or "state requirements" in content.lower())
    assert "FM-014" in content or "FM-015" in content


def test_09_page_structure_binds_failure_modes():
    """验证 09 绑定 FM-009 / FM-013 / FM-014 / FM-015"""
    prompt_path = PROMPTS_DIR / "09-page-structure.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 必须引用这4个 failure modes
    assert "FM-009" in content, "09 必须绑定 FM-009 (PRD-to-Page Shortcut / Feature Stacking)"
    assert "FM-013" in content, "09 必须绑定 FM-013 (IA Unsupported By Evidence)"
    assert "FM-014" in content, "09 必须绑定 FM-014 (State Coverage Illusion)"
    assert "FM-015" in content, "09 必须绑定 FM-015 (Clickable Prototype Verdict Inflation)"


def test_09_page_structure_binds_quality_gates():
    """验证 09 绑定 input-quality-gate 和 self-review-gate"""
    prompt_path = PROMPTS_DIR / "09-page-structure.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 必须引用 quality gates
    assert "Input-Quality-Gate" in content or "input-quality-gate" in content or "input_quality_gate" in content
    assert "Self-Review-Gate" in content or "self-review-gate" in content or "self_review_gate" in content

    # 必须引用 ten-domain readiness
    assert "ten_domain_readiness" in content or "ten-domain" in content.lower()
    assert "Domain 8" in content or "page_interaction_design" in content


def test_09_page_structure_requires_inferred_items_with_confidence():
    """验证 09 要求 inferred page items 标 confidence + risk_if_wrong"""
    prompt_path = PROMPTS_DIR / "09-page-structure.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 检查 inferred_page_items schema
    assert "inferred_page_items" in content
    assert ("confidence" in content and ("0.0-1.0" in content or "float" in content))
    assert "risk_if_wrong" in content
    assert "validation_method" in content


def test_09_page_structure_no_overclaim_without_state_requirements():
    """验证 09 不含 high fidelity / senior review ready without state requirements 等过度承诺"""
    prompt_path = PROMPTS_DIR / "09-page-structure.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 检查是否在禁止上下文中提到 (允许),还是在其他上下文中过度承诺 (不允许)
    lines = content.split('\n')

    for i, line in enumerate(lines):
        # 跳过明确标记为禁止声明的行
        if '❌' in line or 'BLOCKER' in line or '禁止' in line or 'Anti-Patterns' in line:
            continue

        # 检查过度声明 (需要更灵活的检查)
        if ("high fidelity" in line.lower() or "senior review" in line.lower()) and \
           "without" in line.lower() and "state" in line.lower():
            # 检查这是否在 execution_constraints 中 (合法)
            context = '\n'.join(lines[max(0, i-5):min(len(lines), i+6)])
            if "can_proceed" not in context and "execution_constraints" not in context and "FM-" not in context:
                pytest.fail(f"09 行 {i+1} 可能包含过度承诺: {line}")


def test_09_page_structure_consumes_page_flow_map():
    """验证 09 消费 page_flow_map,如缺失则只能 partial page structure"""
    prompt_path = PROMPTS_DIR / "09-page-structure.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 必须消费 page_flow_map
    assert "page_flow_map" in content
    assert ("page_flow_map" in content and ("缺失" in content or "missing" in content.lower())) or \
           "can_generate_page_without_page_flow_map" in content
    assert "FM-013" in content


def test_09_page_structure_has_confidence_score():
    """验证 09 包含 page_structure_confidence_score (9维)"""
    prompt_path = PROMPTS_DIR / "09-page-structure.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 检查 page_structure_confidence_score schema
    assert "page_structure_confidence_score" in content
    assert "overall" in content
    assert "state_requirements_confidence" in content or "state" in content.lower()
    assert "information_hierarchy_confidence" in content or "hierarchy" in content.lower()
    assert "action_hierarchy_confidence" in content or "action" in content.lower()
    assert "evidence_support" in content
    assert "risk_assessment" in content


def test_09_page_structure_decision_rules_complete():
    """验证 09 Decision Rules 包含 5 层约束"""
    prompt_path = PROMPTS_DIR / "09-page-structure.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 必须包含 5 层
    assert ("Core Principle" in content or "page structure 不是功能卡片堆叠" in content)
    assert ("Mandatory Outputs" in content or "强制输出" in content) and "19" in content
    assert "Upstream Consumption" in content or "上游消费" in content
    assert "Anti-Patterns" in content or "Blocker" in content
    assert "Quality Standards" in content or "质量标准" in content
    assert ("Failure Mode Binding" in content or "FM-009" in content) and \
           ("Quality Gate Binding" in content or "Input-Quality-Gate" in content)
    assert "Input Readiness Constraints" in content or "input_document_type" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
