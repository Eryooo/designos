"""
P1 Integration Tests

测试 P0+P1 各模块的集成和手动工作流程。
"""

import pytest
import json
import jsonschema
from pathlib import Path

# 导入模块
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kernel.quality_gates.gates import (
    schema_gate,
    gap_transparency_gate,
    inference_limit_gate,
    traceability_gate,
    code_constraint_gate,
    GateStatus,
    QualityGateExecutor,
    QualityGateBlocked
)

from kernel.traceability.tracer import (
    TraceabilityGenerator,
    TraceabilityValidator
)


# ============================================================================
# Test 1: Schema 验证
# ============================================================================

def test_artifact_schemas_are_valid():
    """测试所有 artifact schemas 语法正确"""
    schema_dir = Path(__file__).parent.parent.parent / "kernel/contracts/artifacts"

    schemas = list(schema_dir.glob("*.schema.json"))
    assert len(schemas) >= 20, f"Expected >=20 schemas, found {len(schemas)}"

    for schema_file in schemas:
        with open(schema_file) as f:
            schema = json.load(f)

        # 验证是 valid JSON Schema
        try:
            jsonschema.Draft7Validator.check_schema(schema)
        except jsonschema.SchemaError as e:
            pytest.fail(f"Schema {schema_file.name} is invalid: {e}")


# ============================================================================
# Test 2: Quality Gates 单元测试
# ============================================================================

def test_gap_transparency_gate_blocks_critical_gaps():
    """测试 gap_transparency_gate 能阻塞 critical gaps"""
    requirement_inventory = {
        "gaps": [
            {
                "gap_id": "GAP-001",
                "impact": "critical",
                "description": "Missing user definition"
            }
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


def test_quality_gate_executor_stops_on_blocked():
    """测试 QualityGateExecutor 在 blocked 时停止"""
    executor = QualityGateExecutor()

    requirement_inventory = {
        "gaps": [{"gap_id": "GAP-001", "impact": "critical"}],
        "completeness_assessment": {"overall_score": 0.7},
        "readiness_decision": {"decision": "proceed"}
    }

    with pytest.raises(QualityGateBlocked):
        executor.execute('gap_transparency_gate', requirement_inventory=requirement_inventory)


# ============================================================================
# Test 3: Pipeline v2 定义验证
# ============================================================================

def test_pipeline_v2_yaml_is_valid():
    """测试 pipeline-v2.yaml 语法正确"""
    import yaml

    pipeline_file = Path(__file__).parent.parent.parent / "skills/prd2proto/pipeline-v2.yaml"

    with open(pipeline_file) as f:
        pipeline = yaml.safe_load(f)

    assert 'name' in pipeline
    assert 'stages' in pipeline
    assert len(pipeline['stages']) >= 15


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
