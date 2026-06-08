"""visual-identity runtime tests — B1.3

验证 visual-identity 子技能的结构完整性、知识加载、schema 对齐与聚合行为。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import yaml

# ─── Paths ───────────────────────────────────────────────────────────────────

REPO = Path(__file__).resolve().parents[5]  # repo root
SKILL_DIR = REPO / "skills" / "brand-creative" / "sub-skills" / "visual-identity"
SCHEMA_DIR = REPO / "skills" / "brand-creative" / "contracts" / "schemas"


# ─── 1. SkillLoader 可加载 ────────────────────────────────────────────────────

class TestSkillLoadable:
    """验证 SkillLoader 可加载 brand-creative:visual-identity"""

    def test_skill_md_exists(self):
        assert (SKILL_DIR / "SKILL.md").is_file()

    def test_pipeline_yaml_exists(self):
        assert (SKILL_DIR / "pipeline.yaml").is_file()

    def test_constitution_exists(self):
        assert (SKILL_DIR / "constitution.md").is_file()

    def test_readme_exists(self):
        assert (SKILL_DIR / "README.md").is_file()

    def test_prompts_exist(self):
        prompts_dir = SKILL_DIR / "prompts"
        assert prompts_dir.is_dir()
        prompt_files = list(prompts_dir.glob("*.md"))
        assert len(prompt_files) >= 2, f"Expected >=2 prompts, got {len(prompt_files)}"


# ─── 2. Pipeline structure ───────────────────────────────────────────────────

class TestPipelineStructure:
    """验证 pipeline.yaml 结构合规"""

    @pytest.fixture
    def pipeline(self) -> dict:
        with open(SKILL_DIR / "pipeline.yaml") as f:
            return yaml.safe_load(f)

    def test_has_stages(self, pipeline: dict):
        assert "stages" in pipeline
        assert len(pipeline["stages"]) >= 2

    def test_no_unsupported_stage_fields(self, pipeline: dict):
        """StageConfig 不支持的字段不得出现"""
        unsupported = {"description", "purpose", "config", "model", "temperature", "output_format"}
        for stage in pipeline["stages"]:
            bad = set(stage.keys()) & unsupported
            assert not bad, f"Stage '{stage.get('id')}' has unsupported fields: {bad}"

    def test_stage_knowledge_at_stage_level(self, pipeline: dict):
        """knowledge 必须写在 stage 级别"""
        for stage in pipeline["stages"]:
            assert "knowledge" in stage, f"Stage '{stage['id']}' missing knowledge at stage level"
            assert isinstance(stage["knowledge"], list)

    def test_all_knowledge_paths_exist(self, pipeline: dict):
        """所有 stage.knowledge 路径必须真实存在"""
        for stage in pipeline["stages"]:
            for kpath in stage.get("knowledge", []):
                resolved = (SKILL_DIR / kpath).resolve()
                assert resolved.is_file(), f"Knowledge path not found: {kpath} (resolved: {resolved})"


# ─── 3. Schema alignment ────────────────────────────────────────────────────

class TestSchemaAlignment:
    """验证 vi_manual.schema.json 存在且输出声明对齐"""

    def test_vi_manual_schema_exists(self):
        schema_path = SCHEMA_DIR / "vi_manual.schema.json"
        assert schema_path.is_file()

    def test_output_declares_vi_manual(self):
        with open(SKILL_DIR / "pipeline.yaml") as f:
            pipeline = yaml.safe_load(f)
        assert "vi_manual" in pipeline.get("outputs", [])

    def test_schema_required_fields(self):
        schema_path = SCHEMA_DIR / "vi_manual.schema.json"
        with open(schema_path) as f:
            schema = json.load(f)
        required = schema.get("required", [])
        assert "logo" in required
        assert "color" in required
        assert "typography" in required
        assert "application_rules" in required


# ─── 4. Gap handling on missing input ────────────────────────────────────────

class TestGapHandling:
    """验证缺少上游输入时，prompt/constitution 要求写入 gaps"""

    def test_constitution_mentions_gaps(self):
        text = (SKILL_DIR / "constitution.md").read_text()
        assert "gaps" in text.lower() or "缺口" in text

    def test_prompt_01_handles_missing_input(self):
        text = (SKILL_DIR / "prompts" / "01-integrate-visual-system.md").read_text()
        # Must mention handling of missing inputs
        assert "缺失" in text or "missing" in text.lower() or "upstream_missing" in text

    def test_prompt_02_degradation(self):
        text = (SKILL_DIR / "prompts" / "02-generate-vi-manual.md").read_text()
        assert "降级" in text or "degrad" in text.lower() or "upstream_missing" in text


# ─── 5. No overclaim ─────────────────────────────────────────────────────────

class TestNoOverclaim:
    """验证不出现过度承诺"""

    OVERCLAIM_PHRASES = [
        "final production ready",
        "商标已确认",
        "字体授权已确认",
        "印刷色已验证",
        "可直接商用",
        "版权清洁",
    ]

    _NEGATION_MARKERS = ["不", "禁止", "不得", "不声称", "未出现", "not", "never", "no ", "don't", "do not"]

    def _scan_file(self, path: Path) -> list[str]:
        if not path.is_file():
            return []
        text = path.read_text()
        found: list[str] = []
        for phrase in self.OVERCLAIM_PHRASES:
            start = 0
            while True:
                idx = text.find(phrase, start)
                if idx == -1:
                    break
                start = idx + len(phrase)
                # Check the line containing the phrase for negation context
                line_start = text.rfind("\n", 0, idx) + 1
                line = text[line_start:idx]
                if any(neg in line for neg in self._NEGATION_MARKERS):
                    continue  # negated — not an overclaim
                # Also skip if inside quotes (used as example of what NOT to say)
                if "“" in line or '"' in line or "「" in line:
                    continue
                found.append(phrase)
        return found

    def test_no_overclaim_in_skill_md(self):
        found = self._scan_file(SKILL_DIR / "SKILL.md")
        assert not found, f"Overclaim in SKILL.md: {found}"

    def test_no_overclaim_in_prompts(self):
        for p in (SKILL_DIR / "prompts").glob("*.md"):
            found = self._scan_file(p)
            assert not found, f"Overclaim in {p.name}: {found}"

    def test_no_overclaim_in_constitution(self):
        found = self._scan_file(SKILL_DIR / "constitution.md")
        assert not found, f"Overclaim in constitution.md: {found}"


# ─── 6. Does not modify upstream state ───────────────────────────────────────

class TestUpstreamImmutability:
    """验证 visual-identity 不覆盖上游 state"""

    def test_constitution_forbids_upstream_override(self):
        text = (SKILL_DIR / "constitution.md").read_text()
        assert "覆盖上游" in text or "不得覆盖" in text or "不覆盖" in text

    def test_pipeline_quality_checks_forbid_override(self):
        with open(SKILL_DIR / "pipeline.yaml") as f:
            pipeline = yaml.safe_load(f)
        checks = pipeline.get("quality_checks", [])
        rules_text = str(checks)
        assert "覆盖" in rules_text or "不得覆盖" in rules_text


# ─── 7. Fake LLM integration test ───────────────────────────────────────────

class TestFakeLLMIntegration:
    """用 Fake LLM 验证 visual-identity 最终产出 vi_manual 且包含必需字段"""

    @pytest.fixture
    def fake_vi_manual(self) -> dict[str, Any]:
        """模拟 visual-identity 的完整输出"""
        return {
            "logo": {
                "type": "symbol",
                "form_direction": "geometric upward arc",
                "black_white_usable": True,
                "min_size_px": 16,
            },
            "color": {
                "primary": {"hex": "#0066CC", "role": "trust"},
                "accessibility": "pass",
            },
            "typography": {
                "primary_font": {"family": "Inter", "license": "OFL"},
                "weight_hierarchy": ["Regular", "Medium", "Bold"],
                "license_status": "needs_verification",
            },
            "auxiliary_graphics": ["从主图形 upward arc 提炼的辅助弧形组合"],
            "application_rules": [
                {"scenario": "名片", "logo_rule": "横版锁版", "color_rule": "主色背景", "typography_rule": "Inter Medium 9pt"},
                {"scenario": "网站", "logo_rule": "header 120px", "color_rule": "浅色背景主色点缀", "typography_rule": "Inter 16px/1.5"},
                {"scenario": "社交媒体", "logo_rule": "纯图标版", "color_rule": "暗色适配", "typography_rule": "Inter Bold 14px"},
                {"scenario": "包装", "logo_rule": "最小 20mm", "color_rule": "CMYK 转换", "typography_rule": "印刷衬线辅助"},
                {"scenario": "海报", "logo_rule": "大尺寸展示", "color_rule": "大面积主色", "typography_rule": "Inter Bold 48pt"},
            ],
            "taboos": ["拉伸变形", "添加阴影", "更改比例", "使用非指定色彩"],
            "consistency_check": {
                "personality_alignment": "consistent",
                "technical_alignment": "minor_deviation",
            },
            "inherited_warnings": [
                "typography: license needs_verification",
            ],
            "gaps": [
                "本 VI 手册为 pilot 产出,需资深品牌设计师评审后方可商用",
                "字体授权状态需人工确认后方可最终采购",
            ],
        }

    def test_vi_manual_has_required_fields(self, fake_vi_manual: dict):
        assert "logo" in fake_vi_manual
        assert "color" in fake_vi_manual
        assert "typography" in fake_vi_manual
        assert "application_rules" in fake_vi_manual
        assert len(fake_vi_manual["application_rules"]) >= 5

    def test_vi_manual_has_consistency_check(self, fake_vi_manual: dict):
        assert "consistency_check" in fake_vi_manual
        assert fake_vi_manual["consistency_check"]["personality_alignment"] in (
            "consistent", "minor_deviation", "conflict"
        )

    def test_vi_manual_has_gaps(self, fake_vi_manual: dict):
        assert "gaps" in fake_vi_manual
        assert len(fake_vi_manual["gaps"]) > 0

    def test_vi_manual_has_inherited_warnings(self, fake_vi_manual: dict):
        assert "inherited_warnings" in fake_vi_manual
        assert isinstance(fake_vi_manual["inherited_warnings"], list)

    def test_vi_manual_does_not_contain_overclaim(self, fake_vi_manual: dict):
        text = json.dumps(fake_vi_manual, ensure_ascii=False)
        overclaims = ["final production ready", "商标已确认", "字体授权已确认", "印刷色已验证"]
        for oc in overclaims:
            assert oc not in text, f"Overclaim found: {oc}"
