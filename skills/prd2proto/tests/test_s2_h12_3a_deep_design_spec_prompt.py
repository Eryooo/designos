#!/usr/bin/env python3
"""
S2-H12.3A Tests — Deep Design Spec / Visual Context Prompt Hardening

验证 13-design-spec-generation.md 深度强化:
- 8 层 visual_context_model 完整
- 禁止 AI 自由发挥视觉风格 / 禁止 Antd 默认样式当最终视觉
- visual_source_status / design_system_dependency_assessment / token_rationale_for_stage_14
- 上游 10/11/12 component/state/interaction 约束被显式消费
- 无 visual source 不得称 visual-ready;Stage 13 不替代 Stage 14
- visual_assumptions / visual_gaps / inferred_visual_items 诚实台账
- Failure Mode 绑定 (FM-009/014/015/016) + Quality Gate 绑定
- 非粗糙分类 (platform/device、user group、business model、task frequency、information density)
- 无未否定的 production-ready / final UI / visual-ready 过度声明

只检查 13 prompt,不要求 14 改动。
"""

import re
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PROMPTS_DIR = REPO_ROOT / "skills" / "prd2proto" / "prompts-v2"
PROMPT_13 = PROMPTS_DIR / "13-design-spec-generation.md"


def _content():
    assert PROMPT_13.exists(), "13-design-spec-generation.md 必须存在"
    return PROMPT_13.read_text(encoding="utf-8")


# 1. 只检查 13 prompt,不要求 14 改动
def test_only_targets_stage_13_not_requiring_stage_14_change():
    """本测试仅针对 13 prompt,不读取/不断言 14 文件内容"""
    content = _content()
    assert "13" in content
    # 明确声明不替代 Stage 14,而非要求修改 14
    assert "不替代 Stage 14" in content or "replace_stage14_token_extraction: false" in content


# 2. prompt 包含 8 层视觉上下文模型
def test_contains_eight_layer_visual_context_model():
    content = _content()
    assert "visual_context_model" in content
    eight_layers = [
        "business_model_context",
        "user_group_context",
        "carrier_platform_context",
        "task_frequency_context",
        "information_density_context",
        "brand_and_emotion_context",
        "design_system_maturity_context",
        "implementation_constraint_context",
    ]
    for layer in eight_layers:
        assert layer in content, f"13 必须包含 8 层视觉上下文模型层: {layer}"
    # 每层需有推导三元组语义
    for token in ["context_value", "visual_implication", "source"]:
        assert token in content, f"8 层上下文必须含推导三元组: {token}"


# 3. prompt 明确禁止 AI 自由发挥视觉风格
def test_forbids_ai_free_visual_style():
    content = _content()
    assert "自由发挥" in content, "13 必须明确禁止 AI 自由发挥视觉风格"
    # 不得用空泛词替代推导
    assert ("简洁" in content and "现代" in content and "专业" in content), \
        "13 必须点名空泛词(简洁/现代/专业)并禁止其替代推导"
    assert ("替代视觉推导" in content or "禁止只写" in content or "不得只写" in content)


# 4. prompt 明确禁止 Antd 默认样式等同最终视觉
def test_forbids_antd_default_as_final_visual():
    content = _content()
    assert "Antd" in content
    assert "antd_is_structural_reference_only" in content
    assert "treat_antd_default_as_final_visual: false" in content
    assert ("structural reference" in content or "structural reference only" in content.lower())
    assert "最终视觉" in content


# 5. prompt 包含 visual_source_status
def test_contains_visual_source_status():
    content = _content()
    assert "visual_source_status" in content
    assert "visual_fidelity_mode" in content
    assert "can_claim_visual_ready" in content


# 6. prompt 包含 design_system_dependency_assessment
def test_contains_design_system_dependency_assessment():
    content = _content()
    assert "design_system_dependency_assessment" in content
    assert "can_claim_design_system_ready" in content
    assert "has_design_system" in content


# 7. prompt 包含 token_rationale_for_stage_14
def test_contains_token_rationale_for_stage_14():
    content = _content()
    assert "token_rationale_for_stage_14" in content
    # 必须明确是 rationale 而非最终 token
    assert ("不做最终 token extraction" in content or "只给 rationale" in content
            or "rationale,而不是" in content or "提供 token rationale" in content
            or "提供" in content and "token rationale" in content.lower())


# 8. prompt 消费 10/11/12 的 component/state/interaction 约束
def test_consumes_upstream_component_state_interaction():
    content = _content()
    # Stage 10 组件约束
    assert "component_strategy" in content
    assert "visual_dependency_boundary" in content
    assert "component_visual_contract" in content
    # Stage 11 状态约束
    assert "state_matrix" in content
    assert "state_to_component_mapping" in content
    assert "state_visual_contract" in content
    # Stage 12 交互约束
    assert "interaction_rules" in content
    assert "interaction_feedback_visual_contract" in content
    # 消费证据
    assert "stage10_component_strategy_consumed" in content
    assert "stage11_state_matrix_consumed" in content
    assert "stage12_interaction_rules_consumed" in content


# 9. prompt 明确无 visual source 不得称 visual-ready
def test_no_visual_source_no_visual_ready():
    content = _content()
    assert "无 visual source 不得称 visual-ready" in content \
        or ("无 visual source" in content and "visual-ready" in content)
    assert "can_claim_visual_ready_without_visual_source: false" in content
    # fidelity 降级
    assert "missing_visual_source_action" in content
    assert ("structural" in content and "visual_direction" in content)


# 10. prompt 明确 Stage 13 不替代 Stage 14 token extraction
def test_stage_13_does_not_replace_stage_14():
    content = _content()
    assert "replace_stage14_token_extraction: false" in content
    assert "不替代 Stage 14" in content or "不直接替代 Stage 14" in content


# 11. prompt 包含 visual_assumptions / visual_gaps / inferred_visual_items
def test_contains_honesty_ledger():
    content = _content()
    for field in ["visual_assumptions", "visual_gaps", "inferred_visual_items"]:
        assert field in content, f"13 必须包含诚实台账字段: {field}"
    # inferred 必须带风险与置信
    assert "risk_if_wrong" in content
    assert "confidence" in content


# 12. prompt 绑定 FM-015 / FM-016 / FM-009 / FM-014
def test_failure_mode_binding():
    content = _content()
    for fm in ["FM-015", "FM-016", "FM-009", "FM-014"]:
        assert fm in content, f"13 必须绑定 failure mode: {fm}"
    # 绑定语义而非仅出现编号
    assert "Visual Polish Overclaim" in content
    assert "PRD-to-Page Shortcut" in content
    assert "State Coverage Illusion" in content
    assert "Verdict Inflation" in content


# 13. prompt 绑定 Input Quality Gate / Self Review Gate / Progressive Checkpoints
def test_quality_gate_binding():
    content = _content()
    assert "Input Quality Gate" in content
    assert "Self Review Gate" in content
    assert "Progressive Checkpoints" in content
    # gate 绑定语义
    assert "ten_domain_readiness" in content
    assert "design_spec_confidence_score" in content


# 14. prompt 包含非粗糙分类(platform/device、user group、business model、task frequency、information density)
def test_contains_non_coarse_categories():
    content = _content()
    # business model 细分
    assert "B2B" in content and "B2C" in content
    assert ("internal enterprise tool" in content or "operations platform" in content)
    # platform/device 细分
    assert "desktop web" in content and "mobile web" in content
    assert ("tablet" in content or "multi-device" in content)
    # user group 细分
    assert ("运营人员" in content or "审批人员" in content or "一线执行人员" in content)
    # task frequency 细分
    assert "高频任务" in content and ("低频配置" in content or "审批流" in content)
    # information density 细分
    assert ("数据密集" in content or "表单密集" in content)
    assert ("对话式 agent" in content or "命令式工作台" in content)


# 15. prompt 不出现未否定的 production-ready / final UI / visual-ready 等过度声明
def test_no_unnegated_overclaim():
    content = _content()
    # 显式存在"禁止过度声明"的自检条款
    assert "未出现未否定的" in content or "不得越权" in content

    negation_markers = [
        "不得", "禁止", "block", "false", "只能", "不能", "无 ", "缺",
        "能否", "判定", "Overclaim", "标 ", "宣称", "未否定", "未出现",
    ]
    overclaim_terms = ["production-ready", "final UI", "visual-ready", "design-system-ready"]
    for line in content.splitlines():
        for term in overclaim_terms:
            if term in line:
                assert any(m in line for m in negation_markers), \
                    f"过度声明 '{term}' 必须处于否定/约束上下文: {line!r}"


# 16. prompt 包含完整强制输出字段清单(语义完整性)
def test_all_mandatory_output_fields_present():
    content = _content()
    mandatory = [
        "design_spec_rationale",
        "visual_context_model",
        "visual_direction_rationale",
        "product_tone_and_visual_principles",
        "information_density_strategy",
        "platform_adaptation_strategy",
        "user_group_visual_implications",
        "component_visual_contract",
        "state_visual_contract",
        "interaction_feedback_visual_contract",
        "accessibility_visual_requirements",
        "design_system_dependency_assessment",
        "visual_source_status",
        "token_rationale_for_stage_14",
        "visual_assumptions",
        "visual_gaps",
        "inferred_visual_items",
        "design_spec_confidence_score",
    ]
    for field in mandatory:
        assert field in content, f"13 必须包含强制输出字段: {field}"


# 17. Decision Rules 链路完整(上游消费 + 视觉推导 + 边界 + FM/gate + 不越权)
def test_decision_rules_chain_complete():
    content = _content()
    assert "Decision Rules" in content
    # 上游消费链路
    assert "Required Upstream Inputs" in content
    assert "断链" in content
    # 视觉上下文推导链路
    assert "8 层" in content and "推导" in content
    # 边界声明
    assert "能力边界" in content or "do_not_claim" in content
    # 不越权声明
    assert "不得越权" in content
    # Anti-Patterns / Blockers 存在
    assert "Anti-Patterns" in content or "Blockers" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
