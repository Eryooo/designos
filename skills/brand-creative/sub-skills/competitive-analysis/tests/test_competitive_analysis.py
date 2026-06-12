"""
competitive-analysis 子技能结构与契约测试

测试范围:
1. SKILL.md 加载成功
2. pipeline.yaml 解析成功
3. knowledge 路径真实存在
4. outputs 与 B1.0 contract 一致
5. schema 文件存在且格式正确
"""

import pytest
import yaml
import json
from pathlib import Path


# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────

@pytest.fixture
def sub_skill_dir():
    """竞品分析子技能目录"""
    return Path(__file__).parent.parent


@pytest.fixture
def skill_md(sub_skill_dir):
    """加载 SKILL.md frontmatter"""
    skill_path = sub_skill_dir / "SKILL.md"
    assert skill_path.exists(), "SKILL.md 不存在"

    content = skill_path.read_text()
    # 简单解析 frontmatter(假设在 --- 之间)
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 2:
            return yaml.safe_load(parts[1])
    return {}


@pytest.fixture
def pipeline_yaml(sub_skill_dir):
    """加载 pipeline.yaml"""
    pipeline_path = sub_skill_dir / "pipeline.yaml"
    assert pipeline_path.exists(), "pipeline.yaml 不存在"

    with open(pipeline_path) as f:
        return yaml.safe_load(f)


@pytest.fixture
def contract_schemas():
    """加载 B1.0 frozen contract schemas"""
    schema_dir = Path(__file__).parent.parent.parent.parent / "contracts" / "schemas"
    competitor_matrix_schema = schema_dir / "competitor_matrix.schema.json"
    market_gap_schema = schema_dir / "market_gap_report.schema.json"

    assert competitor_matrix_schema.exists(), "competitor_matrix.schema.json 不存在"
    assert market_gap_schema.exists(), "market_gap_report.schema.json 不存在"

    with open(competitor_matrix_schema) as f:
        competitor_matrix = json.load(f)
    with open(market_gap_schema) as f:
        market_gap = json.load(f)

    return {
        "competitor_matrix": competitor_matrix,
        "market_gap_report": market_gap
    }


# ─────────────────────────────────────────────────────────────
# Test Cases
# ─────────────────────────────────────────────────────────────

def test_skill_md_structure(skill_md):
    """测试 SKILL.md frontmatter 结构"""
    assert skill_md.get("skill") == "competitive-analysis"
    assert skill_md.get("name") == "Competitive Analysis"
    assert skill_md.get("version") == "0.1.0-pilot"
    assert skill_md.get("type") == "pipeline"
    assert skill_md.get("status") == "pilot"

    outputs = skill_md.get("outputs", [])
    assert len(outputs) >= 2, "至少应有 2 个 output"

    output_ids = [o["id"] for o in outputs]
    assert "competitor_matrix" in output_ids
    assert "market_gap_report" in output_ids


def test_pipeline_yaml_structure(pipeline_yaml):
    """测试 pipeline.yaml 结构"""
    assert "name" in pipeline_yaml
    assert "stages" in pipeline_yaml
    assert len(pipeline_yaml["stages"]) >= 2, "至少应有 2 个 stage"

    # 检查 outputs
    outputs = pipeline_yaml.get("outputs", [])
    assert "competitor_matrix" in outputs
    assert "comparison_matrix" in outputs
    assert "market_gap_report" in outputs


def test_pipeline_stages(pipeline_yaml):
    """测试 pipeline stages 配置"""
    stages = pipeline_yaml["stages"]

    for stage in stages:
        assert "id" in stage
        assert "type" in stage
        assert stage["type"] == "llm", "所有 stage 应为 llm 类型"
        assert "prompt" in stage
        assert "inputs" in stage
        assert "outputs" in stage
        assert "knowledge" in stage


def test_knowledge_paths_exist(pipeline_yaml, sub_skill_dir):
    """测试 knowledge 路径真实存在"""
    stages = pipeline_yaml["stages"]

    for stage in stages:
        knowledge_refs = stage.get("knowledge", [])
        for ref in knowledge_refs:
            # 检查相对路径引用
            if isinstance(ref, str) and ref.endswith(".md"):
                knowledge_path = sub_skill_dir / ref
                assert knowledge_path.exists(), f"Knowledge 文件不存在: {ref}"


def test_outputs_match_contract(skill_md, pipeline_yaml):
    """测试 outputs 与 B1.0 contract 一致"""
    skill_outputs = {o["id"] for o in skill_md.get("outputs", [])}
    pipeline_outputs = set(pipeline_yaml.get("outputs", []))

    # B1.0 frozen contract 要求的 outputs
    required_outputs = {"competitor_matrix", "comparison_matrix", "market_gap_report"}

    assert required_outputs.issubset(pipeline_outputs), \
        f"pipeline.yaml outputs 缺少必需项: {required_outputs - pipeline_outputs}"


def test_schema_files_exist(contract_schemas):
    """测试 schema 文件存在且格式正确"""
    competitor_matrix = contract_schemas["competitor_matrix"]
    market_gap = contract_schemas["market_gap_report"]

    # 检查 competitor_matrix schema
    assert competitor_matrix["type"] == "object"
    assert "competitors" in competitor_matrix["properties"]
    assert competitor_matrix["properties"]["competitors"]["minItems"] == 3

    required_fields = competitor_matrix["properties"]["competitors"]["items"]["required"]
    assert "name" in required_fields
    assert "visual_style" in required_fields

    # 检查 status enum
    status_enum = competitor_matrix["properties"]["status"]["enum"]
    assert "complete" in status_enum
    assert "insufficient_data" in status_enum

    # 检查 market_gap_report schema
    assert market_gap["type"] == "object"
    assert "gaps" in market_gap["properties"]
    assert market_gap["properties"]["gaps"]["minItems"] == 1


def test_prompts_exist(sub_skill_dir, pipeline_yaml):
    """测试 prompt 文件存在"""
    stages = pipeline_yaml["stages"]

    for stage in stages:
        prompt_path = sub_skill_dir / stage["prompt"]
        assert prompt_path.exists(), f"Prompt 文件不存在: {stage['prompt']}"


def test_constitution_exists(sub_skill_dir):
    """测试 constitution.md 存在"""
    constitution_path = sub_skill_dir / "constitution.md"
    assert constitution_path.exists(), "constitution.md 不存在"

    content = constitution_path.read_text()
    # 检查关键约束
    assert "observed" in content
    assert "inferred" in content
    assert "unknown" in content
    assert "insufficient_data" in content


def test_reference_case_exists(sub_skill_dir):
    """测试至少 1 个 reference case 存在"""
    reference_dir = sub_skill_dir / "reference"
    assert reference_dir.exists(), "reference/ 目录不存在"

    reference_files = list(reference_dir.glob("*.md"))
    assert len(reference_files) >= 1, "至少应有 1 个 reference case"


def test_eval_cases_exist(sub_skill_dir):
    """测试至少 1 个 golden 和 1 个 failure case 存在"""
    golden_dir = sub_skill_dir / "eval" / "golden"
    failure_dir = sub_skill_dir / "eval" / "failure"

    assert golden_dir.exists(), "eval/golden/ 目录不存在"
    assert failure_dir.exists(), "eval/failure/ 目录不存在"

    golden_files = list(golden_dir.glob("*.yaml"))
    failure_files = list(failure_dir.glob("*.yaml"))

    assert len(golden_files) >= 1, "至少应有 1 个 golden case"
    assert len(failure_files) >= 1, "至少应有 1 个 failure case"


def test_promptfoo_config_exists(sub_skill_dir):
    """测试 promptfoo.yaml 存在且格式正确"""
    promptfoo_path = sub_skill_dir / "eval" / "promptfoo.yaml"
    assert promptfoo_path.exists(), "eval/promptfoo.yaml 不存在"

    with open(promptfoo_path) as f:
        config = yaml.safe_load(f)

    assert "tests" in config
    assert len(config["tests"]) >= 2, "至少应有 2 个 test case"
