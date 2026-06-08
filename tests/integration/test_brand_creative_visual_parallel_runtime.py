"""B1.2 Integration test: brand-creative visual identity parallel runtime.

Proves that logo-design / color-system / typography-system can run in parallel
with the same brand_brief input and produce independent outputs without state pollution.

Runtime proof points:
- Three sub-skills load successfully via SkillGroup
- All three can execute with the same brand_brief input
- Final state contains: visual_spec + image_prompt_pack + color_palette + typography_spec
- State keys do not conflict or pollute each other
- Each sub-skill's outputs are independently verifiable
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from kernel.contracts.enums import RunStatus, StageStatus
from kernel.contracts.interfaces import ILLMClient, IPipelineEngine, IPipelineSkill
from kernel.contracts.schemas import (
    DesignOSConfig,
    GlobalConfig,
    LLMResponse,
    SkillContext,
    StageEvent,
    StageResult,
    WorkflowConfig,
    WorkflowStep,
)
from kernel.skill_loader import SkillLoader


class DeterministicFakeLLM(ILLMClient):
    """Deterministic LLM that returns scripted JSON responses by matching prompt markers."""

    def __init__(self, responses: dict[str, dict[str, Any]]) -> None:
        # responses: {marker_substring: {output_name: value}}
        self._responses = responses
        self._call_log: list[tuple[str, str]] = []

    async def call(
        self,
        prompt: str,
        *,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> LLMResponse:
        matched: str | None = None
        for marker in self._responses:
            if marker in prompt:
                matched = marker
                break

        if matched is None:
            raise RuntimeError(
                f"DeterministicFakeLLM: no response matched prompt; "
                f"known markers={list(self._responses)}; prompt head={prompt[:80]!r}"
            )

        self._call_log.append((matched, prompt[:100]))
        outputs = self._responses[matched]
        response_text = json.dumps(outputs, ensure_ascii=False, indent=2)

        return LLMResponse(
            text=response_text,
            model="fake-deterministic",
            input_tokens=len(prompt) // 4,
            output_tokens=len(response_text) // 4,
            finish_reason="stop",
        )


class FakePipelineEngine(IPipelineEngine):
    """Minimal engine that runs stages via StageRunner (real runner, fake LLM)."""

    def __init__(self, *, llm: ILLMClient) -> None:
        from kernel.pipeline.stage_runner import StageRunner
        self._runner = StageRunner(llm=llm, mcp=None)
        self.last_results: dict[str, list[StageResult]] = {}

    def execute(
        self,
        skill: IPipelineSkill,
        ctx: SkillContext,
    ) -> AsyncIterator[StageEvent]:
        return self._iterate(skill, ctx)

    async def _iterate(
        self,
        skill: IPipelineSkill,
        ctx: SkillContext,
    ) -> AsyncIterator[StageEvent]:
        stages = skill.get_stages()
        completed: list[StageResult] = []
        self.last_results[ctx.run_id] = completed

        for stage in stages:
            yield StageEvent(
                kind="stage_started",
                stage_id=stage.id,
                timestamp=datetime.now(UTC),
                payload={},
            )
            result = await self._runner.run(stage, ctx)
            completed.append(result)

            if result.status is StageStatus.COMPLETED:
                ctx.state.update(result.outputs)
                yield StageEvent(
                    kind="stage_completed",
                    stage_id=stage.id,
                    timestamp=datetime.now(UTC),
                    payload={"outputs": list(result.outputs)},
                )
            else:
                yield StageEvent(
                    kind="stage_failed",
                    stage_id=stage.id,
                    timestamp=datetime.now(UTC),
                    payload={"error": result.error.model_dump() if result.error else None},
                )
                return


def _ctx(workspace: Path, *, run_id: str = "001-test") -> SkillContext:
    return SkillContext(
        workspace=workspace,
        skill_name="brand-creative",
        skill_version="0.1.0-baseline",
        run_id=run_id,
        config=DesignOSConfig(workspace=workspace, global_config=GlobalConfig()),
    )


@pytest.mark.asyncio
async def test_parallel_visual_identity_three_sub_skills(tmp_path: Path) -> None:
    """B1.2: logo-design / color-system / typography-system can run in parallel.

    Real runtime proof:
    - All three sub-skills load successfully
    - All consume the same brand_brief input
    - Execute in parallel via WorkflowOrchestrator
    - Final state contains: visual_spec + image_prompt_pack + color_palette + typography_spec
    - No state pollution between sub-skills
    """
    repo_root = Path(__file__).parent.parent.parent
    loader = SkillLoader([repo_root / "skills"])
    group = loader.load("brand-creative")

    # Fake LLM responses for all three sub-skills
    fake_llm = DeterministicFakeLLM(
        {
            # logo-design stages
            "Stage: analyze_brand_form": {
                "form_direction": {
                    "primary_shape": "geometric",
                    "rationale": "品牌人格关键词:专业/现代,推导几何形态"
                },
            },
            "Stage: generate_logo_spec": {
                "visual_spec": {
                    "form": {"primary_shape": "geometric", "rationale": "专业现代"},
                    "black_white_usable": True,
                    "min_size_px": 32,
                    "trademark_risk_signals": ["low_risk"],
                },
            },
            "Stage: generate_prompt_pack": {
                "image_prompt_pack": {
                    "prompts": [
                        {
                            "platform": "midjourney",
                            "positive": "geometric logo, modern, professional",
                            "negative": "complex, cluttered",
                        },
                    ],
                    "status": "available",
                },
            },
            # color-system stages
            "Stage 1: 色彩情绪分析": {
                "color_emotion_analysis": {
                    "primary_emotion": "专业可靠",
                    "color_roles": ["主色:蓝", "辅色:灰"]
                },
            },
            "Stage 2: 色彩系统产出": {
                "color_palette": {
                    "primary": {"hex": "#0066CC", "role": "品牌主色"},
                    "secondary": [{"hex": "#6C757D", "role": "辅助灰"}],
                    "contrast_ratios": {"primary_on_white": 4.5},
                    "accessibility": "pass",
                    "print_color_risk": "低饱和度,色差风险小",
                    "dark_light_usage": "明暗双模式定义",
                },
            },
            # typography-system stages
            "Stage 1: 字体气质方向分析": {
                "typography_direction": {
                    "primary_font_personality": "几何现代",
                    "primary_font_role": "标题",
                    "cjk_latin_pairing_needs": "中文市场,需配对",
                    "tone_keywords": ["专业", "现代", "清晰"],
                },
            },
            "Stage 2: 字体系统产出": {
                "typography_spec": {
                    "primary_font": {"family": "Inter", "license": "SIL OFL"},
                    "weight_hierarchy": ["Light", "Regular", "Medium", "Bold"],
                    "cjk_latin_pairing": "中文:思源黑体,西文:Inter,字重匹配",
                    "license_status": "verified",
                    "cross_platform": {
                        "web": {"format": "WOFF2", "fallback": "sans-serif"},
                        "ios": {"availability": "内嵌", "fallback": "PingFang SC"},
                        "android": {"availability": "内嵌", "fallback": "Roboto"},
                    },
                },
            },
        }
    )

    engine = FakePipelineEngine(llm=fake_llm)
    group.attach(engine=engine, llm=fake_llm, mcp=None)

    # Construct workflow with one parallel step containing all three sub-skills
    workflow_config = WorkflowConfig(
        name="test-visual-parallel",
        description="B1.2 Parallel Visual Identity: logo + color + typography",
        steps=[
            WorkflowStep(
                type="parallel",
                sub_skills=["logo-design", "color-system", "typography-system"],
            ),
        ],
    )

    ctx = _ctx(tmp_path, run_id="parallel-visual")
    ctx.state.update(
        {
            "brand_brief": {
                "north_star": "让专业人士感到被支持",
                "positioning": "专业工具提供商",
                "personality_keywords": ["专业", "现代", "可靠", "清晰"],
                "target_user": "专业人士",
            },
        }
    )

    # Execute parallel workflow
    from kernel.pipeline.orchestrator import WorkflowOrchestrator
    orchestrator = WorkflowOrchestrator()

    events = []
    async for event in orchestrator.execute(group, workflow_config, ctx):
        events.append(event)

    # Verify all three sub-skills completed
    completed_skills = [
        event.sub_skill
        for event in events
        if event.kind == "sub_skill_completed" and event.sub_skill
    ]
    assert len(completed_skills) == 3, f"Expected 3 skills completed, got: {completed_skills}"
    assert "logo-design" in completed_skills
    assert "color-system" in completed_skills
    assert "typography-system" in completed_skills

    # Verify all outputs exist in shared state
    assert "visual_spec" in ctx.state, "logo-design should output visual_spec"
    assert "image_prompt_pack" in ctx.state, "logo-design should output image_prompt_pack"
    assert "color_palette" in ctx.state, "color-system should output color_palette"
    assert "typography_spec" in ctx.state, "typography-system should output typography_spec"

    # Verify outputs are independent (no pollution)
    assert ctx.state["visual_spec"]["black_white_usable"] is True
    assert ctx.state["color_palette"]["accessibility"] == "pass"
    assert ctx.state["typography_spec"]["license_status"] == "verified"

    # Verify brand_brief still exists (not overwritten)
    assert "brand_brief" in ctx.state
    assert ctx.state["brand_brief"]["north_star"] == "让专业人士感到被支持"


@pytest.mark.asyncio
async def test_parallel_visual_system_then_visual_identity_sequential(tmp_path: Path) -> None:
    """B1.3: visual-identity runs after the three visual sub-skills.

    Real runtime proof:
    - logo-design / color-system / typography-system run in a parallel step
    - visual-identity runs in the following sequential step
    - Final state contains visual_spec + image_prompt_pack + color_palette + typography_spec + vi_manual
    - visual-identity does not overwrite upstream outputs
    """
    repo_root = Path(__file__).parent.parent.parent
    loader = SkillLoader([repo_root / "skills"])
    group = loader.load("brand-creative")

    fake_llm = DeterministicFakeLLM(
        {
            # logo-design stages
            "Stage: analyze_brand_form": {
                "form_direction": {
                    "primary_shape": "geometric",
                    "rationale": "品牌人格关键词:专业/现代,推导几何形态",
                    "cognitive_chain": {
                        "cognitive_schema": "Verticality",
                        "mother_shape": "upward arc",
                    },
                },
            },
            "Stage: generate_logo_spec": {
                "visual_spec": {
                    "form": {"primary_shape": "geometric", "rationale": "专业现代"},
                    "cognitive_schema": "Verticality",
                    "mother_shape": "upward arc",
                    "black_white_usable": True,
                    "min_size_px": 16,
                    "trademark_risk_signals": ["low_risk"],
                    "color_refs": ["#0066CC"],
                    "application_scenarios": ["website", "social", "business_card"],
                },
            },
            "Stage: generate_prompt_pack": {
                "image_prompt_pack": {
                    "prompts": [
                        {"platform": "midjourney", "positive": "geometric logo", "negative": "cluttered"},
                    ],
                    "status": "available",
                },
            },
            # color-system stages
            "Stage 1: 色彩情绪分析": {
                "color_emotion_analysis": {"primary_emotion": "专业可靠", "color_roles": ["主色:蓝"]},
            },
            "Stage 2: 色彩系统产出": {
                "color_palette": {
                    "primary": {"hex": "#0066CC", "role": "品牌主色/信赖"},
                    "secondary": [{"hex": "#6C757D", "role": "辅助灰"}],
                    "contrast_ratios": {"primary_on_white": 4.5},
                    "accessibility": "pass",
                    "print_color_risk": "需印刷打样验证",
                    "dark_light_usage": {"light": "主色点缀", "dark": "反白 logo"},
                },
            },
            # typography-system stages
            "Stage 1: 字体气质方向分析": {
                "typography_direction": {
                    "primary_font_personality": "几何现代",
                    "primary_font_role": "标题",
                    "tone_keywords": ["专业", "现代", "清晰"],
                },
            },
            "Stage 2: 字体系统产出": {
                "typography_spec": {
                    "primary_font": {"family": "Inter", "license": "SIL OFL"},
                    "weight_hierarchy": ["Regular", "Medium", "Bold"],
                    "size_scale": [12, 14, 16, 20, 32],
                    "cjk_latin_pairing": "中文:思源黑体,西文:Inter",
                    "license_status": "needs_verification",
                    "cross_platform": {"web": {"fallback": "sans-serif"}, "ios": {}, "android": {}},
                },
            },
            # visual-identity stages
            "Stage: integrate_visual_system": {
                "integration_analysis": {
                    "consistency_check": {
                        "personality_alignment": "consistent",
                        "personality_detail": "logo 几何现代、蓝色专业可靠、Inter 清晰现代，三者一致",
                        "technical_alignment": "minor_deviation",
                        "technical_detail": "字体 license needs_verification，需继承警告",
                        "conflict_resolution": ["保留现有方向，但字体授权需人工确认"],
                    },
                    "inherited_warnings": ["typography: license needs_verification", "color: print color needs proofing"],
                    "gaps": ["字体授权未确认", "印刷色值未经打样验证"],
                    "auxiliary_graphics_direction": "从 upward arc 提炼辅助弧形图案",
                },
            },
            "Stage: generate_vi_manual": {
                "vi_manual": {
                    "logo": {"form_direction": "geometric upward arc", "black_white_usable": True, "min_size_px": 16},
                    "color": {"primary": {"hex": "#0066CC", "role": "品牌主色/信赖"}, "accessibility": "pass"},
                    "typography": {
                        "primary_font": {"family": "Inter", "license": "SIL OFL"},
                        "weight_hierarchy": ["Regular", "Medium", "Bold"],
                        "license_status": "needs_verification",
                    },
                    "auxiliary_graphics": ["从 upward arc 提炼辅助弧形图案"],
                    "application_rules": [
                        {"scenario": "名片", "logo_rule": "横版锁版", "color_rule": "主色点缀", "typography_rule": "Inter Medium"},
                        {"scenario": "网站", "logo_rule": "header 120px", "color_rule": "浅色背景", "typography_rule": "Inter 16px"},
                        {"scenario": "社交媒体", "logo_rule": "纯图标", "color_rule": "暗色适配", "typography_rule": "Inter Bold"},
                        {"scenario": "包装", "logo_rule": "最小 20mm", "color_rule": "需打样", "typography_rule": "印刷字体确认"},
                        {"scenario": "海报", "logo_rule": "大尺寸", "color_rule": "主色大面积", "typography_rule": "标题层级"},
                    ],
                    "taboos": ["拉伸变形", "更改比例", "未经确认使用商业字体"],
                    "consistency_check": {"personality_alignment": "consistent", "technical_alignment": "minor_deviation"},
                    "inherited_warnings": ["typography: license needs_verification", "color: print color needs proofing"],
                    "gaps": ["字体授权未确认", "印刷色值未经打样验证"],
                },
            },
        }
    )

    engine = FakePipelineEngine(llm=fake_llm)
    group.attach(engine=engine, llm=fake_llm, mcp=None)

    workflow_config = WorkflowConfig(
        name="test-visual-parallel-then-vi",
        description="B1.3 visual-identity aggregation after B1.2 parallel visual system",
        steps=[
            WorkflowStep(type="parallel", sub_skills=["logo-design", "color-system", "typography-system"]),
            WorkflowStep(type="sequential", sub_skills=["visual-identity"]),
        ],
    )

    ctx = _ctx(tmp_path, run_id="parallel-then-vi")
    ctx.state.update(
        {
            "brand_brief": {
                "north_star": "让专业人士感到被支持",
                "positioning": "专业工具提供商",
                "personality_keywords": ["专业", "现代", "可靠", "清晰"],
                "target_user": "专业人士",
            },
        }
    )

    from kernel.pipeline.orchestrator import WorkflowOrchestrator
    orchestrator = WorkflowOrchestrator()

    events = []
    async for event in orchestrator.execute(group, workflow_config, ctx):
        events.append(event)

    completed = [event.sub_skill for event in events if event.kind == "sub_skill_completed" and event.sub_skill]
    assert completed[:3] == ["logo-design", "color-system", "typography-system"]
    assert completed[-1] == "visual-identity"

    assert "visual_spec" in ctx.state
    assert "image_prompt_pack" in ctx.state
    assert "color_palette" in ctx.state
    assert "typography_spec" in ctx.state
    assert "vi_manual" in ctx.state

    # Preserve upstream snapshots: visual-identity must not overwrite them.
    assert ctx.state["visual_spec"]["mother_shape"] == "upward arc"
    assert ctx.state["color_palette"]["primary"]["hex"] == "#0066CC"
    assert ctx.state["typography_spec"]["license_status"] == "needs_verification"

    vi_manual = ctx.state["vi_manual"]
    assert "logo" in vi_manual
    assert "color" in vi_manual
    assert "typography" in vi_manual
    assert "gaps" in vi_manual and vi_manual["gaps"]
    assert "inherited_warnings" in vi_manual
