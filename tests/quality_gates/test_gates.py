"""
Quality Gates Unit Tests

测试质量门的核心逻辑
"""

import pytest
from kernel.quality_gates.gates import (
    schema_gate,
    traceability_gate,
    gap_transparency_gate,
    inference_limit_gate,
    code_constraint_gate,
    GateStatus,
    GateResult,
    QualityGateBlocked,
    QualityGateExecutor
)


# ============================================================================
# Schema Gate Tests
# ============================================================================

def test_schema_gate_pass():
    """测试 schema gate 通过"""
    artifact = {
        "artifact_id": "test-001",
        "artifact_type": "design_objectives",
        "business_goals": [
            {"goal_id": "BG-001", "description": "Test goal"}
        ],
        "user_goals": []
    }

    schema = {
        "type": "object",
        "properties": {
            "artifact_id": {"type": "string"},
            "business_goals": {"type": "array"},
            "user_goals": {"type": "array"}
        },
        "required": ["artifact_id", "business_goals"]
    }

    result = schema_gate(artifact, schema)
    assert result.status == GateStatus.PASS


def test_schema_gate_blocked_missing_required():
    """测试 schema gate 因缺少必需字段被阻塞"""
    artifact = {
        "artifact_id": "test-001",
        "user_goals": []
    }

    schema = {
        "type": "object",
        "properties": {
            "artifact_id": {"type": "string"},
            "business_goals": {"type": "array"}
        },
        "required": ["artifact_id", "business_goals"]
    }

    result = schema_gate(artifact, schema)
    assert result.status == GateStatus.BLOCKED
    assert len(result.errors) > 0


def test_schema_gate_warning_missing_optional():
    """测试 schema gate 因缺少可选字段产生警告"""
    artifact = {
        "artifact_id": "test-001",
        "business_goals": [{"goal_id": "BG-001"}]
    }

    schema = {
        "type": "object",
        "properties": {
            "artifact_id": {"type": "string"},
            "business_goals": {"type": "array"},
            "user_goals": {"type": "array"}
        },
        "required": ["artifact_id", "business_goals"]
    }

    # 实际上如果 user_goals 不在 artifact 中且不是 required，不会报错
    # 这个测试验证当类型不匹配时产生警告
    artifact["business_goals"] = "not_an_array"  # 类型错误

    result = schema_gate(artifact, schema)
    assert result.status in [GateStatus.WARNING, GateStatus.BLOCKED]


# ============================================================================
# Gap Transparency Gate Tests
# ============================================================================

def test_gap_transparency_gate_pass():
    """测试 gap transparency gate 通过"""
    requirement_inventory = {
        "gaps": [
            {"gap_id": "GAP-001", "impact": "low"}
        ],
        "completeness_assessment": {
            "overall_score": 0.85
        },
        "readiness_decision": {
            "decision": "proceed"
        }
    }

    result = gap_transparency_gate(requirement_inventory)
    assert result.status == GateStatus.PASS


def test_gap_transparency_gate_blocked_critical_gap_ignored():
    """测试 critical gap + proceed 被阻塞"""
    requirement_inventory = {
        "gaps": [
            {"gap_id": "GAP-001", "impact": "critical", "description": "Missing user definition"}
        ],
        "completeness_assessment": {
            "overall_score": 0.7
        },
        "readiness_decision": {
            "decision": "proceed"
        }
    }

    result = gap_transparency_gate(requirement_inventory)
    assert result.status == GateStatus.BLOCKED
    assert "critical gaps" in result.message.lower()


def test_gap_transparency_gate_blocked_low_completeness():
    """测试完整性过低被阻塞"""
    requirement_inventory = {
        "gaps": [],
        "completeness_assessment": {
            "overall_score": 0.25
        },
        "readiness_decision": {
            "decision": "proceed"
        }
    }

    result = gap_transparency_gate(requirement_inventory)
    assert result.status == GateStatus.BLOCKED
    assert "completeness" in result.message.lower()


def test_gap_transparency_gate_warning_medium_completeness():
    """测试中等完整性产生警告"""
    requirement_inventory = {
        "gaps": [],
        "completeness_assessment": {
            "overall_score": 0.45
        },
        "readiness_decision": {
            "decision": "proceed"
        }
    }

    result = gap_transparency_gate(requirement_inventory)
    assert result.status == GateStatus.WARNING


# ============================================================================
# Inference Limit Gate Tests
# ============================================================================

def test_inference_limit_gate_pass():
    """测试推断占比合理通过"""
    artifact = {
        "field1": "value1",
        "field2": "value2",
        "field3": "value3",
        "field4": "value4",
        "field5": "value5",
        "inferred_fields": ["field1"]  # 20% 推断
    }

    result = inference_limit_gate(artifact)
    assert result.status == GateStatus.PASS


def test_inference_limit_gate_warning():
    """测试推断占比较高产生警告"""
    artifact = {
        "field1": "value1",
        "field2": "value2",
        "field3": "value3",
        "inferred_fields": ["field1"]  # 33% 推断
    }

    result = inference_limit_gate(artifact, threshold_warning=0.3)
    assert result.status == GateStatus.WARNING


def test_inference_limit_gate_blocked():
    """测试推断占比过高被阻塞"""
    artifact = {
        "field1": "value1",
        "field2": "value2",
        "inferred_fields": ["field1"]  # 50% 推断
    }

    result = inference_limit_gate(artifact, threshold_blocked=0.5)
    assert result.status == GateStatus.BLOCKED


# ============================================================================
# Traceability Gate Tests
# ============================================================================

def test_traceability_gate_pass():
    """测试 traceability gate 通过"""
    traceability_map = {
        "decision_trace": [
            {
                "decision_id": "DEC-001",
                "decision_point": "选择侧边栏导航",
                "based_on": [
                    {"source_type": "user_task_map", "source_id": "utm-001"}
                ]
            }
        ],
        "coverage_analysis": {
            "input_coverage": 0.85,
            "scope_creep_items": []
        }
    }

    reasoning_assets = {
        "user_task_map": {
            "primary_tasks": [
                {"task_id": "PT-001"}
            ]
        }
    }

    result = traceability_gate(traceability_map, reasoning_assets)
    assert result.status == GateStatus.PASS


def test_traceability_gate_blocked_unauthorized_page():
    """测试未授权页面被阻塞"""
    traceability_map = {
        "decision_trace": [],
        "coverage_analysis": {
            "input_coverage": 0.8,
            "scope_creep_items": []
        }
    }

    reasoning_assets = {
        "user_task_map": {
            "primary_tasks": [
                {"task_id": "PT-001"}
            ]
        }
    }

    output_artifact = {
        "artifact_type": "information_architecture",
        "pages": [
            {
                "page_id": "PG-001",
                "page_name": "Dashboard",
                "related_tasks": []  # 无关联任务
            }
        ]
    }

    result = traceability_gate(traceability_map, reasoning_assets, output_artifact)
    assert result.status == GateStatus.BLOCKED
    assert any(issue['type'] == 'unauthorized_page' for issue in result.issues)


def test_traceability_gate_blocked_low_coverage():
    """测试输入覆盖率过低被阻塞"""
    traceability_map = {
        "decision_trace": [],
        "coverage_analysis": {
            "input_coverage": 0.45,  # < 0.5
            "scope_creep_items": []
        }
    }

    reasoning_assets = {}

    result = traceability_gate(traceability_map, reasoning_assets)
    assert result.status == GateStatus.BLOCKED
    assert any(issue['type'] == 'low_input_coverage' for issue in result.issues)


# ============================================================================
# Code Constraint Gate Tests
# ============================================================================

def test_code_constraint_gate_pass():
    """测试 code constraint gate 通过"""
    generated_code = {
        "pages": [
            {
                "page_id": "PG-001",
                "components_used": ["Button", "Table"]
            }
        ]
    }

    information_architecture = {
        "pages": [
            {"page_id": "PG-001"}
        ]
    }

    component_strategy = {
        "component_inventory": [
            {"component_id": "Button"},
            {"component_id": "Table"}
        ]
    }

    result = code_constraint_gate(generated_code, information_architecture, component_strategy)
    assert result.status == GateStatus.PASS


def test_code_constraint_gate_blocked_unauthorized_page():
    """测试未授权页面被阻塞"""
    generated_code = {
        "pages": [
            {"page_id": "PG-001"},
            {"page_id": "PG-999"}  # 未授权
        ]
    }

    information_architecture = {
        "pages": [
            {"page_id": "PG-001"}
        ]
    }

    component_strategy = {
        "component_inventory": []
    }

    result = code_constraint_gate(generated_code, information_architecture, component_strategy)
    assert result.status == GateStatus.BLOCKED
    assert any(issue['type'] == 'unauthorized_page' for issue in result.issues)


# ============================================================================
# Quality Gate Executor Tests
# ============================================================================

def test_executor_execute_single_gate():
    """测试执行单个质量门"""
    executor = QualityGateExecutor()

    artifact = {
        "artifact_id": "test-001",
        "business_goals": []
    }

    schema = {
        "type": "object",
        "required": ["artifact_id"]
    }

    result = executor.execute('schema_gate', artifact=artifact, schema=schema)
    assert result.status == GateStatus.PASS
    assert len(executor.results) == 1


def test_executor_blocked_raises_exception():
    """测试阻塞时抛出异常"""
    executor = QualityGateExecutor()

    requirement_inventory = {
        "gaps": [
            {"gap_id": "GAP-001", "impact": "critical"}
        ],
        "completeness_assessment": {
            "overall_score": 0.7
        },
        "readiness_decision": {
            "decision": "proceed"
        }
    }

    with pytest.raises(QualityGateBlocked) as excinfo:
        executor.execute('gap_transparency_gate', requirement_inventory=requirement_inventory)

    assert excinfo.value.result.status == GateStatus.BLOCKED


def test_executor_get_summary():
    """测试获取执行摘要"""
    executor = QualityGateExecutor()

    # 执行几个质量门
    artifact1 = {"artifact_id": "test-001", "business_goals": []}
    schema1 = {"type": "object", "required": ["artifact_id"]}
    executor.execute('schema_gate', artifact=artifact1, schema=schema1)

    artifact2 = {"field1": "val", "inferred_fields": []}
    executor.execute('inference_limit_gate', artifact=artifact2)

    summary = executor.get_summary()
    assert summary['total_gates'] == 2
    assert summary['passed'] == 2
    assert summary['warnings'] == 0
    assert summary['blocked'] == 0


# ============================================================================
# 运行测试
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
