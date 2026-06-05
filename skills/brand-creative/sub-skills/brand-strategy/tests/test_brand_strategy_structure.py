"""
brand-strategy 子技能结构与契约测试

验证:
1. SKILL.md 加载成功
2. pipeline.yaml 解析成功
3. knowledge 路径真实存在
4. outputs 与 B1.0 contract 一致
"""

import pytest
import yaml
import os
from pathlib import Path


SKILL_DIR = Path(__file__).parent.parent
REPO_ROOT = SKILL_DIR.parent.parent.parent


class TestBrandStrategyStructure:
    """测试 brand-strategy 子技能基础结构"""

    def test_skill_md_exists(self):
        """SKILL.md 存在"""
        skill_md = SKILL_DIR / "SKILL.md"
        assert skill_md.exists(), "SKILL.md 不存在"

    def test_pipeline_yaml_exists(self):
        """pipeline.yaml 存在"""
        pipeline_yaml = SKILL_DIR / "pipeline.yaml"
        assert pipeline_yaml.exists(), "pipeline.yaml 不存在"

    def test_constitution_md_exists(self):
        """constitution.md 存在"""
        constitution_md = SKILL_DIR / "constitution.md"
        assert constitution_md.exists(), "constitution.md 不存在"

    def test_prompts_directory_exists(self):
        """prompts 目录存在且至少有 1 个 prompt"""
        prompts_dir = SKILL_DIR / "prompts"
        assert prompts_dir.exists(), "prompts 目录不存在"
        prompts = list(prompts_dir.glob("*.md"))
        assert len(prompts) >= 1, "prompts 目录至少需要 1 个 .md 文件"


class TestPipelineYaml:
    """测试 pipeline.yaml 内容合规性"""

    @pytest.fixture
    def pipeline_config(self):
        """加载 pipeline.yaml"""
        pipeline_yaml = SKILL_DIR / "pipeline.yaml"
        with open(pipeline_yaml, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_pipeline_has_stages(self, pipeline_config):
        """pipeline 包含 stages"""
        assert "stages" in pipeline_config, "pipeline.yaml 缺少 stages"
        assert len(pipeline_config["stages"]) >= 2, "至少需要 2 个 stage"

    def test_pipeline_outputs(self, pipeline_config):
        """pipeline outputs 包含 brand_brief"""
        assert "outputs" in pipeline_config, "pipeline.yaml 缺少 outputs"
        assert "brand_brief" in pipeline_config["outputs"], \
            "outputs 必须包含 brand_brief"

    def test_pipeline_inputs(self, pipeline_config):
        """pipeline inputs 包含必需字段"""
        assert "inputs" in pipeline_config, "pipeline.yaml 缺少 inputs"
        inputs = pipeline_config["inputs"]

        # 必须包含 product_brief, target_user
        required_inputs = {"product_brief", "target_user"}
        for inp in required_inputs:
            assert inp in inputs, f"inputs 缺少必需字段: {inp}"

        # 必须包含 competitor_matrix (可选消费)
        assert "competitor_matrix" in inputs, \
            "inputs 必须包含 competitor_matrix (可选消费)"


class TestKnowledgeDependencies:
    """测试 knowledge 依赖路径真实存在"""

    @pytest.fixture
    def pipeline_config(self):
        """加载 pipeline.yaml"""
        pipeline_yaml = SKILL_DIR / "pipeline.yaml"
        with open(pipeline_yaml, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_knowledge_paths_exist(self, pipeline_config):
        """knowledge 通过 SkillLoader 读取 StageConfig 验证(B1.1.1 起 knowledge 在 stage 级)。

        Kernel 不读取 pipeline.yaml 顶层 knowledge,只读取 stage.knowledge。
        本测试通过真实 load 验证:
        - 每个关键 stage 的 knowledge 非空
        - 3 份共享知识文件都至少被一个 stage 加载
        - 所有 stage.knowledge 路径真实存在
        """
        from kernel.skill_loader import SkillLoader

        repo_root = SKILL_DIR.resolve().parents[3]
        loader = SkillLoader([repo_root / "skills"])
        skill = loader.load("brand-creative:brand-strategy")
        stages = skill.get_stages()

        assert len(stages) > 0, "brand-strategy 没有 stages"

        # 每个 stage 的 knowledge 非空
        for stage in stages:
            assert len(stage.knowledge) > 0, (
                f"stage {stage.id} 的 knowledge 为空;"
                f"Kernel 不读取顶层 knowledge,必须放在 stage.knowledge"
            )

        # 收集所有 stage 加载的 knowledge 文件名
        loaded_files = set()
        for stage in stages:
            for kpath in stage.knowledge:
                assert kpath.exists(), f"knowledge 路径不存在: {kpath}"
                loaded_files.add(kpath.name)

        # 3 份共享知识文件都至少被一个 stage 加载
        expected_files = [
            "brand-strategy-methodology.md",
            "brand-identity-quality-rubric.md",
            "brand-creative-failure-modes.md",
        ]
        for expected_file in expected_files:
            assert expected_file in loaded_files, (
                f"knowledge 缺少必需资产: {expected_file};已加载: {loaded_files}"
            )


class TestContractCompliance:
    """测试 B1.0 contract 合规性"""

    @pytest.fixture
    def skill_frontmatter(self):
        """解析 SKILL.md frontmatter"""
        skill_md = SKILL_DIR / "SKILL.md"
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()

        # 简单解析 frontmatter (---\n...\n---)
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter_str = parts[1]
                return yaml.safe_load(frontmatter_str)
        return {}

    def test_skill_name(self, skill_frontmatter):
        """skill name 为 brand-strategy"""
        assert skill_frontmatter.get("name") == "brand-strategy", \
            "SKILL.md name 必须是 brand-strategy"

    def test_skill_type(self, skill_frontmatter):
        """skill type 为 pipeline"""
        assert skill_frontmatter.get("type") == "pipeline", \
            "SKILL.md type 必须是 pipeline"

    def test_skill_outputs(self, skill_frontmatter):
        """skill outputs 包含 brand_brief"""
        outputs = skill_frontmatter.get("outputs", [])
        assert len(outputs) == 1, "outputs 必须只有 1 个(brand_brief)"

        output = outputs[0]
        assert output["id"] == "brand_brief", "output id 必须是 brand_brief"
        assert output["type"] == "brand_brief", "output type 必须是 brand_brief"
        assert output["format"] == "json", "output format 必须是 json"

    def test_skill_version(self, skill_frontmatter):
        """skill version 为 0.1.0-pilot"""
        version = skill_frontmatter.get("version", "")
        assert version.startswith("0.1.0"), "version 必须是 0.1.0-pilot"
        assert "pilot" in version, "version 必须标注 pilot"


class TestEvalStructure:
    """测试 eval 目录结构"""

    def test_eval_golden_exists(self):
        """eval/golden 至少 1 个 golden case"""
        golden_dir = SKILL_DIR / "eval" / "golden"
        assert golden_dir.exists(), "eval/golden 目录不存在"

        golden_cases = list(golden_dir.glob("*.yaml"))
        assert len(golden_cases) >= 1, "eval/golden 至少需要 1 个 .yaml 文件"

    def test_eval_failure_exists(self):
        """eval/failure 至少 1 个 failure case"""
        failure_dir = SKILL_DIR / "eval" / "failure"
        assert failure_dir.exists(), "eval/failure 目录不存在"

        failure_cases = list(failure_dir.glob("*.yaml"))
        assert len(failure_cases) >= 1, "eval/failure 至少需要 1 个 .yaml 文件"

    def test_promptfoo_yaml_exists(self):
        """eval/promptfoo.yaml 存在"""
        promptfoo_yaml = SKILL_DIR / "eval" / "promptfoo.yaml"
        assert promptfoo_yaml.exists(), "eval/promptfoo.yaml 不存在"


class TestReferenceStructure:
    """测试 reference 目录结构"""

    def test_reference_exists(self):
        """reference 目录至少 1 个参考案例"""
        reference_dir = SKILL_DIR / "reference"
        assert reference_dir.exists(), "reference 目录不存在"

        references = list(reference_dir.glob("*.md"))
        assert len(references) >= 1, "reference 目录至少需要 1 个 .md 文件"

    def test_reference_has_matrix_case(self):
        """reference 包含 competitor_matrix 存在场景案例"""
        reference_dir = SKILL_DIR / "reference"
        cases = list(reference_dir.glob("*matrix*.md"))
        assert len(cases) >= 1, \
            "reference 必须包含 competitor_matrix 存在场景案例(文件名含 'matrix')"

    def test_reference_has_inferred_case(self):
        """reference 包含 competitor_matrix 缺失(inferred)场景案例"""
        reference_dir = SKILL_DIR / "reference"
        cases = list(reference_dir.glob("*inferred*.md"))
        assert len(cases) >= 1, \
            "reference 必须包含 competitor_matrix 缺失场景案例(文件名含 'inferred')"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
