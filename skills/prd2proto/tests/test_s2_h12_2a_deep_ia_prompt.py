#!/usr/bin/env python3
"""
S2-H12.2A Tests — Deep IA Prompt Hardening

验证 07-information-architecture.md 深度强化:
- 上游消费 (problem/goal/product/task/flow/journey)
- 强制输出 (ia_rationale/experience_surfaces/route_hierarchy等11项)
- 决策规则 (禁止功能1:1页面/禁止example主导IA/必须有rationale)
- Failure Mode 绑定 (FM-009/010/013)
- Quality Gate 绑定 (input-quality-gate/self-review-gate)

不只检查字符串存在,而是验证约束逻辑和推导链路。
"""

import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PROMPTS_DIR = REPO_ROOT / "skills" / "prd2proto" / "prompts-v2"


def test_07_ia_contains_all_mandatory_output_fields():
    """验证 07 包含所有强制输出字段"""
    prompt_path = PROMPTS_DIR / "07-information-architecture.md"
    assert prompt_path.exists()
    content = prompt_path.read_text(encoding='utf-8')

    # 强制输出字段
    mandatory_fields = [
        "ia_rationale",
        "experience_surfaces",
        "route_hierarchy",
        "page_grouping_rationale",
        "task_to_navigation_mapping",
        "domain_object_to_surface_mapping",
        "flat_function_to_page_check",
        "representative_scenario_influence_check",
        "inferred_ia_items",
        "ia_gaps",
        "ia_confidence_score"
    ]

    for field in mandatory_fields:
        assert field in content, f"07 必须包含强制输出字段: {field}"


def test_07_ia_consumes_all_upstream_stages():
    """验证 07 明确消费 02-06 的上游产物"""
    prompt_path = PROMPTS_DIR / "07-information-architecture.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 上游消费
    upstream_artifacts = [
        "problem_statement",
        "goal_tree",
        "product_foundation_map",
        "domain_objects",
        "role_model",
        "task_model",
        "business_flow_map",
        "journey_stages"
    ]

    for artifact in upstream_artifacts:
        assert artifact in content, f"07 必须消费上游产物: {artifact}"


def test_07_ia_explicitly_forbids_flat_function_to_page():
    """验证 07 明确禁止功能列表 1:1 映射成页面"""
    prompt_path = PROMPTS_DIR / "07-information-architecture.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 检查禁止声明
    assert "flat_function_to_page_check" in content
    assert ("不得把功能列表" in content and "1:1" in content and "页面" in content) or \
           ("flat" in content.lower() and "function" in content.lower() and "page" in content.lower())

    # 检查 execution_constraints
    assert "can_flat_function_to_page" in content
    assert "false" in content  # 确保有 false 约束


def test_07_ia_explicitly_forbids_example_dominance():
    """验证 07 明确禁止 representative scenario 主导 IA"""
    prompt_path = PROMPTS_DIR / "07-information-architecture.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 检查字段
    assert "representative_scenario_influence_check" in content
    assert "example_influences_ia" in content or "example主导" in content or "example_dominate" in content.lower()

    # 检查 execution_constraints
    assert "can_let_example_dominate_ia" in content
    assert "FM-010" in content


def test_07_ia_binds_failure_modes():
    """验证 07 绑定 FM-009 / FM-010 / FM-013"""
    prompt_path = PROMPTS_DIR / "07-information-architecture.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 必须引用这3个 failure modes
    assert "FM-009" in content, "07 必须绑定 FM-009 (PRD-to-Page Shortcut)"
    assert "FM-010" in content, "07 必须绑定 FM-010 (Example Dominance)"
    assert "FM-013" in content, "07 必须绑定 FM-013 (IA Unsupported By Evidence)"


def test_07_ia_binds_quality_gates():
    """验证 07 绑定 input-quality-gate 和 self-review-gate"""
    prompt_path = PROMPTS_DIR / "07-information-architecture.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 必须引用 quality gates
    assert "Input-Quality-Gate" in content or "input-quality-gate" in content or "input_quality_gate" in content
    assert "Self-Review-Gate" in content or "self-review-gate" in content or "self_review_gate" in content

    # 必须引用 ten-domain readiness
    assert "ten_domain_readiness" in content or "ten-domain" in content.lower()
    assert "ia_navigation_surface" in content or "Domain 7" in content


def test_07_ia_requires_rationale_or_degrade():
    """验证 07 要求 ia_rationale，否则 degrade"""
    prompt_path = PROMPTS_DIR / "07-information-architecture.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 检查硬约束
    assert "ia_rationale" in content
    assert "degrade" in content.lower()
    assert "can_proceed_without_ia_rationale" in content
    assert "false" in content


def test_07_ia_requires_inferred_items_with_confidence():
    """验证 07 要求 inferred IA 标 confidence + risk_if_wrong"""
    prompt_path = PROMPTS_DIR / "07-information-architecture.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 检查 inferred_ia_items schema
    assert "inferred_ia_items" in content
    assert ("confidence" in content and ("0.0-1.0" in content or "float" in content))
    assert "risk_if_wrong" in content


def test_07_ia_no_overclaim_without_rationale():
    """验证 07 不含 full IA / complete IA / senior IA without rationale 等过度承诺"""
    prompt_path = PROMPTS_DIR / "07-information-architecture.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 禁止的过度承诺
    forbidden_overclaims = [
        "full IA without",
        "complete IA without",
        "senior IA without",
        "完整IA无需",
        "资深IA无需"
    ]

    for overclaim in forbidden_overclaims:
        assert overclaim.lower() not in content.lower(), \
            f"07 不得包含过度承诺: {overclaim}"


def test_07_ia_consumes_input_document_type():
    """验证 07 消费 input_document_type 和 can_generate_prototype_from_input"""
    prompt_path = PROMPTS_DIR / "07-information-architecture.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 必须消费 stage 01 的判定
    assert "input_document_type" in content
    assert "can_generate_prototype_from_input" in content

    # 检查约束逻辑
    assert ("mrd" in content.lower() or "roadmap" in content.lower()) and "reasoning" in content.lower()


def test_07_ia_has_confidence_score():
    """验证 07 包含 ia_confidence_score"""
    prompt_path = PROMPTS_DIR / "07-information-architecture.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 检查 ia_confidence_score schema
    assert "ia_confidence_score" in content
    assert "overall" in content
    assert "evidence_support" in content
    assert "risk_assessment" in content


def test_07_ia_decision_rules_complete():
    """验证 07 Decision Rules 包含 5 层约束"""
    prompt_path = PROMPTS_DIR / "07-information-architecture.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 必须包含 5 层
    assert "Mandatory Outputs" in content or "强制输出" in content
    assert "Upstream Consumption" in content or "上游消费" in content
    assert "Anti-Patterns" in content or "Blocker" in content
    assert "Quality Standards" in content or "质量标准" in content
    assert ("Failure Mode Binding" in content or "FM-009" in content) and \
           ("Quality Gate Binding" in content or "Input-Quality-Gate" in content)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
