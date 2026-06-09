"""
logo-design runtime 测试

验证:
- SkillLoader 可加载 brand-creative:logo-design
- stage.knowledge 全部存在
- 输出字段对齐 schema
"""

import pytest
from pathlib import Path


def test_skill_loadable():
    """验证 SkillLoader 可加载 logo-design 子技能"""
    from kernel.skill_loader import SkillLoader

    skill_dir = Path(__file__).parent.parent
    repo_root = skill_dir.resolve().parents[3]
    loader = SkillLoader([repo_root / "skills"])
    skill = loader.load("brand-creative:logo-design")

    assert skill is not None
    assert skill.name == "logo-design"

    # 验证 stages 和 knowledge
    stages = skill.get_stages()
    assert len(stages) > 0, "logo-design 没有 stages"

    # 每个 stage 的 knowledge 非空
    for stage in stages:
        assert len(stage.knowledge) > 0, (
            f"stage {stage.id} 的 knowledge 为空;"
            f"Kernel 不读取顶层 knowledge,必须放在 stage.knowledge"
        )

    # 收集所有 stage 加载的 knowledge 文件名并验证存在
    loaded_files = set()
    for stage in stages:
        for kpath in stage.knowledge:
            assert kpath.exists(), f"knowledge 路径不存在: {kpath}"
            loaded_files.add(kpath.name)

    # 4 份共享知识文件都至少被一个 stage 加载
    expected_files = [
        "logo-design-methodology.md",
        "logo-cognitive-translation.md",
        "image-prompt-system.md",
        "brand-identity-quality-rubric.md",
        "brand-creative-failure-modes.md",
    ]
    for expected_file in expected_files:
        assert expected_file in loaded_files, (
            f"knowledge 缺少必需资产: {expected_file};已加载: {loaded_files}"
        )


def test_pipeline_yaml_exists():
    """验证 pipeline.yaml 存在"""
    skill_dir = Path(__file__).parent.parent
    pipeline_file = skill_dir / "pipeline.yaml"
    assert pipeline_file.exists(), "pipeline.yaml 必须存在"


def test_stage_knowledge_files_exist():
    """验证所有 stage.knowledge 路径真实存在"""
    import yaml

    skill_dir = Path(__file__).parent.parent
    pipeline_file = skill_dir / "pipeline.yaml"

    with open(pipeline_file) as f:
        pipeline = yaml.safe_load(f)

    # 收集所有 knowledge 路径
    knowledge_paths = []
    for stage in pipeline.get("stages", []):
        if "knowledge" in stage:
            knowledge_paths.extend(stage["knowledge"])

    # 验证每个路径存在
    repo_root = skill_dir.parent.parent.parent.parent
    for rel_path in knowledge_paths:
        abs_path = (skill_dir / rel_path).resolve()
        assert abs_path.exists(), f"knowledge 文件不存在: {rel_path}"


def test_schema_files_exist():
    """验证 schema 文件存在"""
    skill_dir = Path(__file__).parent.parent
    schema_dir = skill_dir.parent.parent / "contracts" / "schemas"

    assert (schema_dir / "logo_spec.schema.json").exists()
    assert (schema_dir / "logo_prompt_pack.schema.json").exists()


def test_output_aligns_with_logo_spec_schema():
    """验证输出字段对齐 logo_spec.schema.json"""
    import json

    skill_dir = Path(__file__).parent.parent
    schema_file = skill_dir.parent.parent / "contracts" / "schemas" / "logo_spec.schema.json"

    with open(schema_file) as f:
        schema = json.load(f)

    # 验证必需字段
    required = schema.get("required", [])
    assert "form" in required
    assert "black_white_usable" in required
    assert "min_size_px" in required

    # 验证字段类型
    properties = schema.get("properties", {})
    assert properties["black_white_usable"]["type"] == "boolean"
    assert properties["min_size_px"]["type"] == "integer"

    # 验证认知链路字段存在(optional,向后兼容)
    assert "cognitive_schema" in properties
    assert "mother_shape" in properties
    assert "first_impression_prediction" in properties
    assert "likely_misread" in properties
    assert "avoidance_rule" in properties

    # 验证认知链路字段类型
    assert properties["cognitive_schema"]["type"] == "string"
    assert properties["mother_shape"]["type"] == "string"
    assert properties["first_impression_prediction"]["type"] == "string"
    assert properties["likely_misread"]["type"] == "array"
    assert properties["avoidance_rule"]["type"] == "array"


def test_output_aligns_with_logo_prompt_pack_schema():
    """验证输出字段对齐 logo_prompt_pack.schema.json"""
    import json

    skill_dir = Path(__file__).parent.parent
    schema_file = skill_dir.parent.parent / "contracts" / "schemas" / "logo_prompt_pack.schema.json"

    with open(schema_file) as f:
        schema = json.load(f)

    # 验证必需字段
    required = schema.get("required", [])
    assert "prompts" in required

    # 验证 prompts 数组项结构
    prompts_items = schema["properties"]["prompts"]["items"]
    assert "platform" in prompts_items["required"]
    assert "positive" in prompts_items["required"]
    assert "negative" in prompts_items["required"]


def test_constitution_exists():
    """验证 constitution.md 存在"""
    skill_dir = Path(__file__).parent.parent
    constitution = skill_dir / "constitution.md"
    assert constitution.exists()


def test_readme_exists():
    """验证 README.md 存在"""
    skill_dir = Path(__file__).parent.parent
    readme = skill_dir / "README.md"
    assert readme.exists()


def test_prompts_exist():
    """验证所有 stage prompt 文件存在"""
    skill_dir = Path(__file__).parent.parent
    prompts_dir = skill_dir / "prompts"

    assert (prompts_dir / "01-analyze-brand-form.md").exists()
    assert (prompts_dir / "02-generate-logo-spec.md").exists()
    assert (prompts_dir / "03-generate-prompt-pack.md").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
