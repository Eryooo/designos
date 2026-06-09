"""
P1 Integration Tests - 文件和结构验证

由于 Python 模块导入问题，这里只验证文件结构和定义的完整性。
"""

import pytest
import json
import yaml
from pathlib import Path


# ============================================================================
# Test 1: 文件结构验证
# ============================================================================

def test_p0_schemas_exist():
    """测试 P0 schemas 存在"""
    schema_dir = Path(__file__).parent.parent.parent / "kernel/contracts/artifacts"

    required_schemas = [
        "artifact-base.schema.json",
        "design-objectives.schema.json",
        "user-task-map.schema.json",
        "information-architecture.schema.json",
        "component-strategy.schema.json",
        "state-matrix.schema.json",
        "professional-gap-report.schema.json",
        "traceability-map.schema.json"
    ]

    for schema_name in required_schemas:
        schema_file = schema_dir / schema_name
        assert schema_file.exists(), f"Missing schema: {schema_name}"


def test_p1_quality_gates_exist():
    """测试 P1.1 质量门文件存在"""
    gates_dir = Path(__file__).parent.parent.parent / "kernel/quality-gates"

    assert (gates_dir / "gates.py").exists()
    assert (gates_dir / "gate-config.yaml").exists()
    assert (gates_dir / "README.md").exists()


def test_p1_traceability_exist():
    """测试 P1.2 追溯性文件存在"""
    trace_dir = Path(__file__).parent.parent.parent / "kernel/traceability"

    assert (trace_dir / "tracer.py").exists()
    assert (trace_dir / "README.md").exists()


def test_p1_prompts_exist():
    """测试 P1.3 prompts 存在"""
    prompts_dir = Path(__file__).parent.parent.parent / "skills/prd2proto/prompts-v2"

    assert (prompts_dir / "README.md").exists()
    assert (prompts_dir / "01-input-diagnosis.md").exists()

    # 检查 02-17 框架版本存在
    for i in range(2, 18):
        prompts = list(prompts_dir.glob(f"{i:02d}-*.md"))
        assert len(prompts) == 1, f"Missing prompt {i:02d}"


def test_pipeline_v2_exists():
    """测试 pipeline-v2.yaml 存在"""
    pipeline_dir = Path(__file__).parent.parent.parent / "skills/prd2proto"

    assert (pipeline_dir / "pipeline-v2.yaml").exists()
    assert (pipeline_dir / "PIPELINE-INTEGRATION.md").exists()


# ============================================================================
# Test 2: Schema 语法验证
# ============================================================================

def test_all_schemas_are_valid_json():
    """测试所有 schemas 是有效的 JSON"""
    schema_dir = Path(__file__).parent.parent.parent / "kernel/contracts/artifacts"

    schemas = list(schema_dir.glob("*.schema.json"))
    assert len(schemas) >= 20, f"Expected >=20 schemas, found {len(schemas)}"

    for schema_file in schemas:
        with open(schema_file) as f:
            try:
                json.load(f)
            except json.JSONDecodeError as e:
                pytest.fail(f"Schema {schema_file.name} has invalid JSON: {e}")


def test_artifact_base_structure():
    """测试 artifact-base.schema.json 结构"""
    schema_file = Path(__file__).parent.parent.parent / "kernel/contracts/artifacts/artifact-base.schema.json"

    with open(schema_file) as f:
        schema = json.load(f)

    # 验证关键字段存在
    assert "properties" in schema
    properties = schema["properties"]

    required_fields = [
        "artifact_id",
        "artifact_type",
        "confidence",
        "gaps",
        "inferred_fields",
        "warnings"
    ]

    for field in required_fields:
        assert field in properties, f"artifact-base missing: {field}"


# ============================================================================
# Test 3: YAML 配置验证
# ============================================================================

def test_gate_config_is_valid_yaml():
    """测试 gate-config.yaml 语法正确"""
    config_file = Path(__file__).parent.parent.parent / "kernel/quality-gates/gate-config.yaml"

    with open(config_file) as f:
        config = yaml.safe_load(f)

    # 验证基本结构
    assert "stages" in config
    assert "thresholds" in config
    assert len(config["stages"]) >= 10


def test_pipeline_v2_is_valid_yaml():
    """测试 pipeline-v2.yaml 语法正确"""
    pipeline_file = Path(__file__).parent.parent.parent / "skills/prd2proto/pipeline-v2.yaml"

    with open(pipeline_file) as f:
        pipeline = yaml.safe_load(f)

    # 验证基本结构
    assert "name" in pipeline
    assert "stages" in pipeline
    assert len(pipeline["stages"]) >= 15


def test_pipeline_v2_stages_structure():
    """测试 pipeline-v2 stages 结构完整"""
    pipeline_file = Path(__file__).parent.parent.parent / "skills/prd2proto/pipeline-v2.yaml"

    with open(pipeline_file) as f:
        pipeline = yaml.safe_load(f)

    for stage in pipeline["stages"]:
        # 每个 stage 必须有 id
        assert "id" in stage, f"Stage missing id"

        # 每个 stage 必须有 type 或 prompt
        assert "type" in stage or "prompt" in stage, f"Stage {stage['id']} missing type/prompt"


# ============================================================================
# Test 4: Prompts 完整性验证
# ============================================================================

def test_prompt_01_is_complete():
    """测试 01-input-diagnosis.md 是完整版"""
    prompt_file = Path(__file__).parent.parent.parent / "skills/prd2proto/prompts-v2/01-input-diagnosis.md"

    with open(prompt_file) as f:
        content = f.read()

    # 验证包含关键章节
    assert "系统指令" in content
    assert "输出规范" in content
    assert "评分规则" in content
    assert "readiness_decision 规则" in content
    assert "完整示例" in content
    assert "Quality Gate" in content


def test_prompts_02_17_are_frameworks():
    """测试 02-17 标注为框架版"""
    prompts_dir = Path(__file__).parent.parent.parent / "skills/prd2proto/prompts-v2"

    for i in range(2, 18):
        prompt_files = list(prompts_dir.glob(f"{i:02d}-*.md"))
        assert len(prompt_files) == 1

        with open(prompt_files[0]) as f:
            content = f.read()

        # 应该标注为 FRAMEWORK
        assert "FRAMEWORK" in content or "框架版本" in content, \
            f"Prompt {i:02d} should be marked as FRAMEWORK"


# ============================================================================
# Test 5: 文档一致性验证
# ============================================================================

def test_pilot_boundary_has_p1_updates():
    """测试 PILOT-BOUNDARY.md 包含 P1 更新"""
    doc_file = Path(__file__).parent.parent.parent / "skills/prd2proto/PILOT-BOUNDARY.md"

    with open(doc_file) as f:
        content = f.read()

    # 验证包含 P1 章节
    assert "P1 更新" in content or "P1.1" in content
    assert "P1 已知限制" in content or "P1 Known Limitations" in content


def test_pilot_boundary_lists_critical_issues():
    """测试 PILOT-BOUNDARY.md 列出 critical 问题"""
    doc_file = Path(__file__).parent.parent.parent / "skills/prd2proto/PILOT-BOUNDARY.md"

    with open(doc_file) as f:
        content = f.read()

    # 应该明确标注关键限制
    critical_keywords = [
        "pipeline-v2.yaml",
        "runtime",
        "框架版" or "framework",
        "质量门" or "quality gate"
    ]

    found = sum(1 for keyword in critical_keywords if keyword in content)
    assert found >= 3, "PILOT-BOUNDARY.md should mention critical limitations"


def test_pipeline_integration_guide_exists():
    """测试 PIPELINE-INTEGRATION.md 存在且完整"""
    doc_file = Path(__file__).parent.parent.parent / "skills/prd2proto/PIPELINE-INTEGRATION.md"

    assert doc_file.exists()

    with open(doc_file) as f:
        content = f.read()

    # 验证包含关键章节
    assert "Quality Gates 集成" in content or "Quality Gates Integration" in content
    assert "Traceability 集成" in content or "Traceability Integration" in content
    assert "P1 Limitations" in content or "P1 限制" in content


# ============================================================================
# Test 6: Git 提交历史验证
# ============================================================================

def test_p0_commit_exists():
    """测试 P0 commits 存在"""
    import subprocess

    result = subprocess.run(
        ["git", "log", "--oneline", "--grep=P0", "-10"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent
    )

    assert "P0" in result.stdout, "Should have P0 commits"


def test_p1_commits_exist():
    """测试 P1 commits 存在"""
    import subprocess

    result = subprocess.run(
        ["git", "log", "--oneline", "--grep=P1", "-10"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent
    )

    assert "P1" in result.stdout, "Should have P1 commits"


# ============================================================================
# 运行测试
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
