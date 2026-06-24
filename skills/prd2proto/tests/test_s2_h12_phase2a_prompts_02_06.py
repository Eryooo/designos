#!/usr/bin/env python3
"""
S2-H12.1 Phase 2A Tests — Prompts 02-06 Senior Design Execution Enhancement

验证 02-design-objectives, 03-product-archetype, 04-user-task-modeling,
05-business-flow-modeling, 06-user-journey-mapping 补充了资深设计执行约束。
"""

import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PROMPTS_DIR = REPO_ROOT / "skills" / "prd2proto" / "prompts-v2"


def test_02_design_objectives_contains_problem_statement():
    """验证 02-design-objectives.md 含 problem_statement"""
    prompt_path = PROMPTS_DIR / "02-design-objectives.md"
    assert prompt_path.exists()
    content = prompt_path.read_text(encoding='utf-8')

    # 验证 problem_statement 字段
    assert "problem_statement:" in content
    assert "business_problem:" in content
    assert "user_problem:" in content
    assert "success_criteria:" in content
    assert "problem_statement_confidence:" in content

    # 验证消费 input-diagnosis 产出
    assert "input_readiness_consumed:" in content
    assert "input_document_type:" in content
    assert "can_generate_prototype_from_input:" in content
    assert "problem_framing_readiness:" in content

    # 验证硬约束
    assert "can_proceed_to_ia_without_problem_statement: false" in content
    assert "can_proceed_to_page_structure_without_goal_tree: false" in content


def test_02_design_objectives_decision_rules():
    """验证 02 Decision Rules 含资深设计执行约束"""
    prompt_path = PROMPTS_DIR / "02-design-objectives.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 验证 Senior Design Execution Constraints
    assert "S2-H12.1" in content
    assert "MUST output `problem_statement`" in content or "MUST output problem_statement" in content
    assert "FM-011" in content  # 引用 failure mode


def test_03_product_archetype_contains_product_foundation_map():
    """验证 03-product-archetype.md 含 product_foundation_map"""
    prompt_path = PROMPTS_DIR / "03-product-archetype.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 验证 product_foundation_map 字段
    assert "product_foundation_map:" in content
    assert "core_capabilities:" in content
    assert "core_modules:" in content
    assert "domain_objects:" in content
    assert "role_model:" in content
    assert "representative_scenarios:" in content

    # 验证 example_dominance_check
    assert "example_dominance_check:" in content
    assert "example_dominates_foundation:" in content
    assert "FM-010" in content  # 引用 failure mode

    # 验证硬约束
    assert "can_claim_full_product_architecture_without_foundation: false" in content
    assert "can_let_example_dominate_ia: false" in content


def test_03_product_archetype_decision_rules():
    """验证 03 Decision Rules 含 example dominance 约束"""
    prompt_path = PROMPTS_DIR / "03-product-archetype.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "S2-H12.1" in content
    assert "example_dominates_foundation" in content or "example主导" in content
    assert "representative_scenario" in content


def test_04_user_task_modeling_contains_task_to_goal_mapping():
    """验证 04-user-task-modeling.md 含 task_to_goal_mapping"""
    prompt_path = PROMPTS_DIR / "04-user-task-modeling.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 验证关键字段
    assert "task_to_goal_mapping" in content
    assert "edge_tasks_gap_check" in content
    assert "edge_tasks_identified" in content or "edge_tasks_identified:" in content
    assert "missing_edge_tasks" in content

    # 验证硬约束
    assert "can_proceed_to_page_map_without_task_model" in content
    assert "can_proceed_to_ia_without_completion_criteria" in content


def test_04_user_task_modeling_decision_rules():
    """验证 04 Decision Rules 含任务映射约束"""
    prompt_path = PROMPTS_DIR / "04-user-task-modeling.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "S2-H12.1" in content
    assert "task_to_goal_mapping" in content
    assert "completion_criteria" in content or "completion criteria" in content


def test_05_business_flow_modeling_contains_flow_coverage_check():
    """验证 05-business-flow-modeling.md 含 flow_coverage_check"""
    prompt_path = PROMPTS_DIR / "05-business-flow-modeling.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 验证关键字段
    assert "flow_coverage_check" in content
    assert "happy_path_covered" in content
    assert "exception_paths_covered" in content
    assert "state_coverage_gaps" in content
    assert "unsupported_flow_gaps" in content

    # 验证硬约束
    assert "can_claim_complete_flow_without_exception_paths" in content
    assert "FM-014" in content  # 引用 failure mode


def test_05_business_flow_modeling_decision_rules():
    """验证 05 Decision Rules 含 state coverage 约束"""
    prompt_path = PROMPTS_DIR / "05-business-flow-modeling.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "S2-H12.1" in content
    assert "flow_coverage_check" in content
    assert "exception_paths" in content or "异常" in content


def test_06_user_journey_mapping_contains_user_intent_by_stage():
    """验证 06-user-journey-mapping.md 含 user_intent_by_stage"""
    prompt_path = PROMPTS_DIR / "06-user-journey-mapping.md"
    content = prompt_path.read_text(encoding='utf-8')

    # 验证关键字段
    assert "user_intent_by_stage" in content
    assert "journey_assumptions" in content
    assert "journey_gaps" in content

    # 验证硬约束
    assert "can_proceed_to_page_structure_without_user_intent" in content
    assert "can_treat_journey_as_feature_steps" in content


def test_06_user_journey_mapping_decision_rules():
    """验证 06 Decision Rules 含 journey≠功能 约束"""
    prompt_path = PROMPTS_DIR / "06-user-journey-mapping.md"
    content = prompt_path.read_text(encoding='utf-8')

    assert "S2-H12.1" in content
    assert "user_intent" in content
    assert "journey" in content


def test_prompts_02_06_no_direct_prd_to_page():
    """验证 02-06 不含 PRD 直转页面的过度承诺"""
    forbidden_phrases = [
        "直接生成页面",
        "直接生成完整原型",
        "自动生成完整",
        "一步生成",
    ]

    for i in range(2, 7):
        prompt_file = PROMPTS_DIR / f"0{i}-*.md"
        # 使用 glob 匹配
        matched = list(PROMPTS_DIR.glob(f"0{i}-*.md"))
        assert len(matched) == 1, f"应该只有一个 0{i}-*.md 文件"

        content = matched[0].read_text(encoding='utf-8')

        for phrase in forbidden_phrases:
            assert phrase not in content, \
                f"{matched[0].name} 含过度承诺: '{phrase}'"


def test_prompts_02_06_consume_upstream():
    """验证 02-06 消费上游产出"""
    # 02 应该消费 01
    prompt_02 = PROMPTS_DIR / "02-design-objectives.md"
    content_02 = prompt_02.read_text(encoding='utf-8')
    assert "input_document_type" in content_02
    assert "can_generate_prototype" in content_02

    # 03 应该消费 02
    prompt_03 = PROMPTS_DIR / "03-product-archetype.md"
    content_03 = prompt_03.read_text(encoding='utf-8')
    assert "problem_statement" in content_03 or "goal_tree" in content_03

    # 04 应该消费 02+03
    prompt_04 = PROMPTS_DIR / "04-user-task-modeling.md"
    content_04 = prompt_04.read_text(encoding='utf-8')
    assert "product_foundation" in content_04

    # 05 应该消费 04
    prompt_05 = PROMPTS_DIR / "05-business-flow-modeling.md"
    content_05 = prompt_05.read_text(encoding='utf-8')
    assert "task_model" in content_05

    # 06 应该消费 04+05
    prompt_06 = PROMPTS_DIR / "06-user-journey-mapping.md"
    content_06 = prompt_06.read_text(encoding='utf-8')
    assert "task_model" in content_06 or "business_flow" in content_06


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
