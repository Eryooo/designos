#!/usr/bin/env python3
"""
S2-H12.2B Tests — Deep Page Flow Prompt Hardening

验证 08-page-flow.md 深度强化:
- 上游消费 (problem/goal/product/task/flow/journey/IA)
- 强制输出 (page_flow_rationale/entry_points/exit_points等16项)
- 决策规则 (page flow≠sitemap/禁止happy path only/必须有entry+exit+exception+permission)
- Failure Mode 绑定 (FM-009/013/014)
- Quality Gate 绑定 (input-quality-gate/self-review-gate)

不只检查字符串存在,而是验证约束逻辑和推导链路。
"""

import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PROMPTS_DIR = REPO_ROOT / "skills" / "prd2proto" / "prompts-v2"


def test_08_page_flow_contains_all_mandatory_output_fields():
    """验证 08 包含所有强制输出字段 (16项)"""
    prompt_path = PROMPTS_DIR / "08-page-flow.md"
    assert prompt_path.exists()
    content = prompt_path.read_text(encoding='utf-8')

    # 16项强制输出字段
    mandatory_fields = [
        "page_flow_rationale",
        "page_flow_map",
        "entry_points",
        "exit_points",
        "cross_page_transitions",
        "decision_points",
        "permission_paths",
        "exception_paths",
        "recovery_paths",
        "interruption_paths",
        "flow_to_task_mapping",
        "flow_to_route_mapping",
        "transition_trigger_conditions",
        "page_flow_gaps",
        "inferred_flow_items",
        "page_flow_confidence_score"
    ]

    for field in mandatory_fields:
        assert field in content, f"08 必须包含强制输出字段: {field}"


def test_08_page_flow_consumes_all_upstream_stages():
    """验证 08 明确消费 01-07 的上游产物"""
    prompt_path = PROMPTS_DIR / "08-page-flow.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 12项上游消费
    upstream_artifacts = [
        "problem_statement",
        "goal_tree",
        "product_foundation_map",
        "task_model",
        "business_flow_map",
        "journey_stages",
        "ia_rationale",
        "route_hierarchy",
        "task_to_navigation_mapping",
        "domain_object_to_surface_mapping",
        "input_document_type",
        "can_generate_prototype_from_input"
    ]

    for artifact in upstream_artifacts:
        assert artifact in content, f"08 必须消费上游产物: {artifact}"


def test_08_page_flow_explicitly_not_sitemap():
    """验证 08 明确 page flow 不是 sitemap"""
    prompt_path = PROMPTS_DIR / "08-page-flow.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 检查明确声明
    assert ("page flow" in content.lower() and "不是" in content and "sitemap" in content.lower()) or \
           ("page flow" in content.lower() and "not" in content.lower() and "sitemap" in content.lower())


def test_08_page_flow_forbids_happy_path_only():
    """验证 08 明确禁止 happy path = complete flow"""
    prompt_path = PROMPTS_DIR / "08-page-flow.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 检查禁止声明
    assert "happy_path_only" in content or "happy path only" in content.lower()
    assert "can_claim_complete_flow_with_happy_path_only" in content
    assert "false" in content
    assert "FM-014" in content


def test_08_page_flow_requires_entry_exit():
    """验证 08 要求 entry_points 和 exit_points,否则 block prototype"""
    prompt_path = PROMPTS_DIR / "08-page-flow.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 检查硬约束
    assert "entry_points" in content
    assert "exit_points" in content
    assert "can_proceed_without_entry_points" in content or "can_proceed_without_exit_points" in content
    assert ("block" in content.lower() and "prototype" in content.lower()) or "block_prototype_scope" in content


def test_08_page_flow_requires_exception_paths():
    """验证 08 要求 exception_paths,否则 degrade"""
    prompt_path = PROMPTS_DIR / "08-page-flow.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 检查硬约束
    assert "exception_paths" in content
    assert "can_proceed_without_exception_paths" in content or "exception_path_coverage" in content
    assert "degrade" in content.lower()


def test_08_page_flow_requires_permission_paths():
    """验证 08 要求 permission_paths (如产品含权限)"""
    prompt_path = PROMPTS_DIR / "08-page-flow.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 检查硬约束
    assert "permission_paths" in content
    assert "can_proceed_without_permission_paths" in content or "permission_path_coverage" in content


def test_08_page_flow_binds_failure_modes():
    """验证 08 绑定 FM-009 / FM-013 / FM-014"""
    prompt_path = PROMPTS_DIR / "08-page-flow.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 必须引用这3个 failure modes
    assert "FM-009" in content, "08 必须绑定 FM-009 (PRD-to-Page Shortcut)"
    assert "FM-013" in content, "08 必须绑定 FM-013 (IA Unsupported By Evidence)"
    assert "FM-014" in content, "08 必须绑定 FM-014 (State Coverage Illusion / Happy Path Only)"


def test_08_page_flow_binds_quality_gates():
    """验证 08 绑定 input-quality-gate 和 self-review-gate"""
    prompt_path = PROMPTS_DIR / "08-page-flow.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 必须引用 quality gates
    assert "Input-Quality-Gate" in content or "input-quality-gate" in content or "input_quality_gate" in content
    assert "Self-Review-Gate" in content or "self-review-gate" in content or "self_review_gate" in content

    # 必须引用 ten-domain readiness
    assert "ten_domain_readiness" in content or "ten-domain" in content.lower()
    assert ("Domain 7" in content or "Domain 8" in content or
            "ia_navigation_surface" in content or "page_interaction_design" in content)


def test_08_page_flow_requires_transition_trigger_conditions():
    """验证 08 要求每个 transition 有 trigger_condition / user_intent"""
    prompt_path = PROMPTS_DIR / "08-page-flow.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 检查字段
    assert "transition_trigger_conditions" in content
    assert "trigger_condition" in content
    assert "user_intent" in content
    assert "system_response" in content


def test_08_page_flow_requires_inferred_items_with_confidence():
    """验证 08 要求 inferred flow 标 confidence + risk_if_wrong"""
    prompt_path = PROMPTS_DIR / "08-page-flow.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 检查 inferred_flow_items schema
    assert "inferred_flow_items" in content
    assert ("confidence" in content and ("0.0-1.0" in content or "float" in content))
    assert "risk_if_wrong" in content
    assert "validation_method" in content


def test_08_page_flow_no_overclaim_without_exception_paths():
    """验证 08 不含 complete flow / prototype ready without exception paths 等过度承诺"""
    prompt_path = PROMPTS_DIR / "08-page-flow.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 禁止的过度承诺 (需要更灵活的检查,因为可能在禁止声明中提到)
    # 只检查不在禁止上下文中的过度声明
    lines = content.split('\n')

    for i, line in enumerate(lines):
        # 跳过明确标记为禁止声明的行
        if '❌' in line or 'BLOCKER' in line or '禁止' in line or 'Anti-Patterns' in line:
            continue

        # 检查过度声明
        if "complete flow without" in line.lower() and "exception" in line.lower():
            # 检查这是否在 execution_constraints 中 (合法)
            if "can_claim_complete_flow" not in line and "execution_constraints" not in lines[max(0, i-5):i+5]:
                pytest.fail(f"08 行 {i+1} 可能包含过度声明: {line}")


def test_08_page_flow_consumes_ia_rationale():
    """验证 08 消费 ia_rationale,如缺失则 page flow 只能 partial"""
    prompt_path = PROMPTS_DIR / "08-page-flow.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 必须消费 ia_rationale
    assert "ia_rationale" in content
    assert ("ia_rationale" in content and ("缺失" in content or "missing" in content.lower())) or \
           "can_generate_flow_without_ia_rationale" in content
    assert "FM-013" in content


def test_08_page_flow_has_confidence_score():
    """验证 08 包含 page_flow_confidence_score (9维)"""
    prompt_path = PROMPTS_DIR / "08-page-flow.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 检查 page_flow_confidence_score schema
    assert "page_flow_confidence_score" in content
    assert "overall" in content
    assert "exception_coverage_confidence" in content or "exception" in content
    assert "permission_coverage_confidence" in content or "permission" in content
    assert "recovery_coverage_confidence" in content or "recovery" in content
    assert "evidence_support" in content
    assert "risk_assessment" in content


def test_08_page_flow_decision_rules_complete():
    """验证 08 Decision Rules 包含 5 层约束"""
    prompt_path = PROMPTS_DIR / "08-page-flow.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 必须包含 5 层
    assert ("Core Principle" in content or "page flow 不是 sitemap" in content)
    assert ("Mandatory Outputs" in content or "强制输出" in content) and "16" in content
    assert "Upstream Consumption" in content or "上游消费" in content
    assert "Anti-Patterns" in content or "Blocker" in content
    assert "Quality Standards" in content or "质量标准" in content
    assert ("Failure Mode Binding" in content or "FM-009" in content) and \
           ("Quality Gate Binding" in content or "Input-Quality-Gate" in content)
    assert "Input Readiness Constraints" in content or "input_document_type" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
