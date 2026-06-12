"""
typography-system runtime 测试

验证:
- SkillLoader 可加载 brand-creative:typography-system
- stage.knowledge 全部存在
- 输出字段对齐 schema
"""

import pytest
from pathlib import Path


def test_skill_loadable():
    """验证 SkillLoader 可加载 typography-system 子技能"""
    from kernel.skill_loader import SkillLoader

    skill_dir = Path(__file__).parent.parent
    repo_root = skill_dir.resolve().parents[3]
    loader = SkillLoader([repo_root / "skills"])
    skill = loader.load("brand-creative:typography-system")

    assert skill is not None
    assert skill.name == "typography-system"

    # 验证 stages 和 knowledge
    stages = skill.get_stages()
    assert len(stages) > 0, "typography-system 没有 stages"

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

    # 3 份共享知识文件都至少被一个 stage 加载
    expected_files = [
        "typography-system-methodology.md",
        "brand-identity-quality-rubric.md",
        "brand-creative-failure-modes.md",
    ]
    for fname in expected_files:
        assert fname in loaded_files, f"knowledge 文件 {fname} 未被任何 stage 加载"


def test_stage_knowledge_not_in_top_level():
    """验证 knowledge 写在 stage 级别,不在 pipeline 顶层"""
    from kernel.skill_loader import SkillLoader

    skill_dir = Path(__file__).parent.parent
    repo_root = skill_dir.resolve().parents[3]
    loader = SkillLoader([repo_root / "skills"])
    skill = loader.load("brand-creative:typography-system")

    # 读取原始 pipeline.yaml
    import yaml
    pipeline_path = skill_dir / "pipeline.yaml"
    with open(pipeline_path) as f:
        raw_pipeline = yaml.safe_load(f)

    # 顶层不应有 knowledge 字段
    assert "knowledge" not in raw_pipeline, (
        "pipeline.yaml 顶层不应有 knowledge 字段;Kernel 只读 stage.knowledge"
    )


def test_output_schema_alignment():
    """验证输出字段对齐 typography_spec.schema.json"""
    skill_dir = Path(__file__).parent.parent
    schema_path = skill_dir.parent.parent / "contracts/schemas/typography_spec.schema.json"

    assert schema_path.exists(), f"schema 文件不存在: {schema_path}"

    import json
    with open(schema_path) as f:
        schema = json.load(f)

    # 验证 schema 必需字段
    assert "required" in schema
    assert "primary_font" in schema["required"]
    assert "weight_hierarchy" in schema["required"]

    # 验证 properties
    assert "properties" in schema
    expected_props = [
        "primary_font", "weight_hierarchy", "cjk_latin_pairing",
        "license_status", "cross_platform"
    ]
    for prop in expected_props:
        assert prop in schema["properties"], f"schema 缺少字段: {prop}"


def test_quality_checks_defined():
    """验证 quality_checks 定义了字重/授权等硬约束"""
    skill_dir = Path(__file__).parent.parent

    import yaml
    pipeline_path = skill_dir / "pipeline.yaml"
    with open(pipeline_path) as f:
        pipeline = yaml.safe_load(f)

    assert "quality_checks" in pipeline
    quality_checks = pipeline["quality_checks"]
    assert len(quality_checks) > 0

    checkpoint = quality_checks[0]
    assert checkpoint["checkpoint"] == "C4-typography-system"
    assert "rules" in checkpoint

    rules_text = " ".join(checkpoint["rules"])
    # 验证包含核心质量约束
    assert "weight_hierarchy" in rules_text
    assert "license_status" in rules_text
    assert "cross_platform" in rules_text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
