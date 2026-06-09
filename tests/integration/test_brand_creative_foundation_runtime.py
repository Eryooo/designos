"""B1.1 Integration test: brand-creative foundation runtime vertical slice.

Proves the first basic chain can run end-to-end:
  competitive-analysis → competitor_matrix → brand-strategy → brand_brief

Real runtime proof points:
- SkillGroup.attach propagates engine/llm/mcp to lazily-loaded sub-skills
- competitive-analysis loads, runs, outputs competitor_matrix to shared state
- brand-strategy loads, runs, consumes competitor_matrix, outputs brand_brief
- Both sub-skills' pipeline knowledge paths resolve to real files
- When competitor_matrix is missing/insufficient, brand_brief marks differentiation [inferred]
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from kernel.contracts.enums import ErrorCode, RunStatus, StageStatus
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
from kernel.pipeline.orchestrator import WorkflowOrchestrator
from kernel.skill_loader import SkillLoader, load_skill_group


class DeterministicFakeLLM(ILLMClient):
    """Deterministic LLM that returns scripted JSON responses by matching a
    distinctive substring of the rendered prompt to a stage's outputs.

    The kernel StageRunner renders prompts from the on-disk prompt files, so we
    dispatch on the unique Stage header text rather than a synthetic stage_id.
    """

    def __init__(self, responses: dict[str, dict[str, Any]]) -> None:
        # responses: {marker_substring: {output_name: value}}
        self._responses = responses
        self._call_log: list[tuple[str, str]] = []  # [(marker, prompt_snippet)]
        self.full_prompts: list[str] = []  # B1.1.1: record full prompts for verification

    async def call(
        self,
        prompt: str,
        *,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> LLMResponse:
        self.full_prompts.append(prompt)  # B1.1.1: record full prompt

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
async def test_foundation_chain_with_competitor_matrix(tmp_path: Path) -> None:
    """B1.1: competitive-analysis → competitor_matrix → brand-strategy → brand_brief.

    Real runtime proof: SkillGroup loads, attaches engine, lazily loads sub-skills,
    competitive-analysis outputs competitor_matrix to state, brand-strategy consumes it.
    """
    repo_root = Path(__file__).parent.parent.parent
    loader = SkillLoader([repo_root / "skills"])

    # Load brand-creative group
    group = loader.load("brand-creative")
    assert group.name == "brand-creative"

    # Scripted LLM responses keyed by distinctive prompt header (real prompts on disk)
    fake_llm = DeterministicFakeLLM(
        {
            # competitive-analysis stages
            "Stage 1: 竞品资料整合": {
                "competitor_raw_data": [
                    {"name": "CompetitorA", "visual_style": "minimalist"},
                    {"name": "CompetitorB", "visual_style": "bold"},
                    {"name": "CompetitorC", "visual_style": "friendly"},
                ],
            },
            "Stage 2: 竞品矩阵生成与市场空白识别": {
                "competitor_matrix": {
                    "competitors": [
                        {
                            "name": "CompetitorA",
                            "visual_style": "minimalist",
                            "communication": "professional",
                            "market_position": "premium",
                        },
                        {
                            "name": "CompetitorB",
                            "visual_style": "bold",
                            "communication": "edgy",
                            "market_position": "mainstream",
                        },
                        {
                            "name": "CompetitorC",
                            "visual_style": "friendly",
                            "communication": "approachable",
                            "market_position": "mid-tier",
                        },
                    ],
                    "status": "complete",
                },
                "comparison_matrix": {
                    "competitors": [
                        {"name": "CompetitorA", "visual_style": "minimalist"},
                        {"name": "CompetitorB", "visual_style": "bold"},
                        {"name": "CompetitorC", "visual_style": "friendly"},
                    ],
                    "status": "complete",
                },
                "market_gap_report": {
                    "gaps": [
                        {
                            "dimension": "emotional_tone",
                            "description": "No competitor occupies the 'empowering yet humble' space",
                        }
                    ],
                },
            },
            # brand-strategy stages
            "Stage 1: 分析上下文": {"context_summary": "3 competitors identified"},
            "Stage 2: 产出品牌策略基线": {
                "brand_brief": {
                    "north_star": "让创业者感到被理解与支持",
                    "positioning": "为创业者提供温暖而专业的品牌服务",
                    "differentiation": {
                        "statement": "我们不追求冷淡极简或过度张扬，而是在专业与亲和之间找到平衡",
                        "basis": "competitor_matrix",
                    },
                    "core_values": ["专业", "温暖", "可信赖"],
                    "personality_keywords": ["可靠", "温暖", "专业", "理解", "支持"],
                    "target_user": "早期创业者",
                },
            },
        }
    )

    engine = FakePipelineEngine(llm=fake_llm)
    group.attach(engine=engine, llm=fake_llm)

    # Run competitive-analysis
    ctx_comp = _ctx(tmp_path, run_id="run-comp")
    ctx_comp.state.update(
        {
            "product_brief": "AI-powered brand design tool for startups",
            "target_market": "China tech startup ecosystem",
            "competitor_hints": ["CompetitorA", "CompetitorB", "CompetitorC"],
        }
    )
    result_comp = await group.run_sub_skill("competitive-analysis", ctx_comp)
    assert result_comp.status is RunStatus.COMPLETED

    # competitive-analysis outputs should be in state
    assert "competitor_matrix" in ctx_comp.state
    assert "comparison_matrix" in ctx_comp.state
    assert ctx_comp.state["competitor_matrix"]["status"] == "complete"
    assert len(ctx_comp.state["competitor_matrix"]["competitors"]) == 3

    # Run brand-strategy (consumes competitor_matrix)
    ctx_brand = _ctx(tmp_path, run_id="run-brand")
    ctx_brand.state.update(
        {
            "product_brief": "AI-powered brand design tool for startups",
            "target_user": "Early-stage founders in tech",
            "competitor_matrix": ctx_comp.state["competitor_matrix"],
        }
    )
    result_brand = await group.run_sub_skill("brand-strategy", ctx_brand)
    assert result_brand.status is RunStatus.COMPLETED

    # brand_brief output should exist and use competitor_matrix as basis
    assert "brand_brief" in ctx_brand.state
    brand_brief = ctx_brand.state["brand_brief"]
    assert brand_brief["differentiation"]["basis"] == "competitor_matrix"
    assert brand_brief["north_star"]  # must not be empty
    assert 3 <= len(brand_brief["personality_keywords"]) <= 5


@pytest.mark.asyncio
async def test_foundation_chain_without_competitor_matrix_marks_inferred(tmp_path: Path) -> None:
    """B1.1: brand-strategy without competitor_matrix marks differentiation basis as 'inferred'.

    Real runtime proof: when competitor_matrix is missing or status=insufficient_data,
    brand-strategy must output differentiation.basis = "inferred".
    """
    repo_root = Path(__file__).parent.parent.parent
    loader = SkillLoader([repo_root / "skills"])
    group = loader.load("brand-creative")

    fake_llm = DeterministicFakeLLM(
        {
            "Stage 1: 分析上下文": {"context_summary": "no competitor data available"},
            "Stage 2: 产出品牌策略基线": {
                "brand_brief": {
                    "north_star": "让用户感到被支持",
                    "positioning": "专业工具提供商",
                    "differentiation": {
                        "statement": "基于用户洞察推断的差异化方向",
                        "basis": "inferred",
                    },
                    "core_values": ["可靠", "专业"],
                    "personality_keywords": ["可靠", "专业", "友好"],
                    "target_user": "创业者",
                },
            },
        }
    )

    engine = FakePipelineEngine(llm=fake_llm)
    group.attach(engine=engine, llm=fake_llm)

    # Run brand-strategy without competitor_matrix
    ctx = _ctx(tmp_path, run_id="run-no-matrix")
    ctx.state.update(
        {
            "product_brief": "AI tool",
            "target_user": "startups",
        }
    )
    result = await group.run_sub_skill("brand-strategy", ctx)
    assert result.status is RunStatus.COMPLETED

    assert "brand_brief" in ctx.state
    brand_brief = ctx.state["brand_brief"]
    assert brand_brief["differentiation"]["basis"] == "inferred"


def test_brand_creative_sub_skills_loadable(tmp_path: Path) -> None:
    """B1.1: SkillLoader can load brand-creative:competitive-analysis and brand-strategy.
    B1.2: Also load logo-design, color-system, typography-system."""
    repo_root = Path(__file__).parent.parent.parent
    loader = SkillLoader([repo_root / "skills"])

    # B1.1 sub-skills
    comp_skill = loader.load("brand-creative:competitive-analysis")
    assert comp_skill.name == "Competitive Analysis"

    brand_skill = loader.load("brand-creative:brand-strategy")
    assert brand_skill.name == "brand-strategy"

    # B1.2 visual identity sub-skills
    logo_skill = loader.load("brand-creative:logo-design")
    assert logo_skill.name == "logo-design"

    color_skill = loader.load("brand-creative:color-system")
    assert color_skill.name == "color-system"

    typo_skill = loader.load("brand-creative:typography-system")
    assert typo_skill.name == "typography-system"


def test_sub_skill_pipeline_knowledge_paths_exist(tmp_path: Path) -> None:
    """B1.1: Both sub-skills' pipeline.yaml knowledge paths resolve to real files.
    B1.2: Also check logo-design, color-system, typography-system."""
    repo_root = Path(__file__).parent.parent.parent
    loader = SkillLoader([repo_root / "skills"])

    # B1.1 sub-skills
    comp_skill = loader.load("brand-creative:competitive-analysis")
    comp_stages = comp_skill.get_stages()
    for stage in comp_stages:
        for kpath in stage.knowledge:
            assert kpath.exists(), f"competitive-analysis knowledge not found: {kpath}"

    brand_skill = loader.load("brand-creative:brand-strategy")
    brand_stages = brand_skill.get_stages()
    for stage in brand_stages:
        for kpath in stage.knowledge:
            assert kpath.exists(), f"brand-strategy knowledge not found: {kpath}"

    # B1.2 visual identity sub-skills
    for sub_id in ["logo-design", "color-system", "typography-system"]:
        skill = loader.load(f"brand-creative:{sub_id}")
        stages = skill.get_stages()
        for stage in stages:
            for kpath in stage.knowledge:
                assert kpath.exists(), f"{sub_id} knowledge not found: {kpath}"


def test_brand_strategy_knowledge_really_loaded() -> None:
    """B1.1.1: brand-strategy stages真实加载知识文件,不是仅顶层声明."""
    repo_root = Path(__file__).parent.parent.parent
    loader = SkillLoader([repo_root / "skills"])

    brand_skill = loader.load("brand-creative:brand-strategy")
    stages = brand_skill.get_stages()

    # 每个 stage 必须有 knowledge
    assert len(stages) == 2, "brand-strategy should have 2 stages"
    for stage in stages:
        assert len(stage.knowledge) > 0, (
            f"stage {stage.id} has no knowledge loaded. "
            f"Kernel does not read top-level 'knowledge' field in pipeline.yaml; "
            f"knowledge must be in stage.knowledge."
        )

    # 验证预期的 3 个共享知识文件至少被一个 stage 加载
    expected_knowledge_files = {
        "brand-strategy-methodology.md",
        "brand-identity-quality-rubric.md",
        "brand-creative-failure-modes.md",
    }

    all_loaded_files = set()
    for stage in stages:
        for kpath in stage.knowledge:
            all_loaded_files.add(kpath.name)

    for expected_file in expected_knowledge_files:
        assert expected_file in all_loaded_files, (
            f"Expected knowledge file '{expected_file}' not loaded by any stage. "
            f"Loaded: {all_loaded_files}"
        )


@pytest.mark.asyncio
async def test_real_workflow_orchestrator_state_passing(tmp_path: Path) -> None:
    """B1.1.1: 真实 WorkflowOrchestrator 自动传递 state, 不手动拷贝.

    证明:
    1. 使用真实 WorkflowOrchestrator
    2. 两个 sub-skill 顺序执行在同一个 SkillContext
    3. competitive-analysis 输出的 competitor_matrix 自动进入 ctx.state
    4. brand-strategy 从同一个 ctx.state 消费 competitor_matrix
    5. 最终 brand_brief.differentiation.basis == "competitor_matrix"
    """
    repo_root = Path(__file__).parent.parent.parent
    loader = SkillLoader([repo_root / "skills"])

    # 构造测试专用 WorkflowConfig: 两个顺序步骤
    workflow_config = WorkflowConfig(
        name="test-foundation-chain",
        description="B1.1 Foundation Chain Test: competitive-analysis → brand-strategy",
        steps=[
            WorkflowStep(
                type="sequential",
                sub_skills=["competitive-analysis"],
            ),
            WorkflowStep(
                type="sequential",
                sub_skills=["brand-strategy"],
            ),
        ],
    )

    # Fake LLM for both sub-skills
    fake_llm = DeterministicFakeLLM(
        {
            # competitive-analysis stages
            "Stage 1: 竞品资料整合": {
                "competitor_raw_data": [
                    {"name": "CompA", "visual_style": "minimal"},
                    {"name": "CompB", "visual_style": "bold"},
                    {"name": "CompC", "visual_style": "friendly"},
                ],
            },
            "Stage 2: 竞品矩阵生成与市场空白识别": {
                "competitor_matrix": {
                    "competitors": [
                        {"name": "CompA", "visual_style": "minimal"},
                        {"name": "CompB", "visual_style": "bold"},
                        {"name": "CompC", "visual_style": "friendly"},
                    ],
                    "status": "complete",
                },
                "comparison_matrix": {
                    "competitors": [
                        {"name": "CompA", "visual_style": "minimal"},
                        {"name": "CompB", "visual_style": "bold"},
                        {"name": "CompC", "visual_style": "friendly"},
                    ],
                    "status": "complete",
                },
                "market_gap_report": {
                    "gaps": [
                        {
                            "dimension": "emotional_tone",
                            "description": "No competitor uses empowering tone",
                        }
                    ],
                },
            },
            # brand-strategy stages
            "Stage 1: 分析上下文": {"context_analysis": {"context_summary": "3 competitors"}},
            "Stage 2: 产出品牌策略基线": {
                "brand_brief": {
                    "north_star": "让用户感到被理解",
                    "positioning": "专业且亲和的品牌服务",
                    "differentiation": {
                        "statement": "在专业与亲和之间找平衡",
                        "basis": "competitor_matrix",
                    },
                    "core_values": ["专业", "温暖"],
                    "personality_keywords": ["专业", "温暖", "可靠"],
                    "target_user": "创业者",
                },
            },
        }
    )

    engine = FakePipelineEngine(llm=fake_llm)

    # 构造 SkillContext（同一个 context 用于整个 workflow）
    ctx = _ctx(tmp_path, run_id="workflow-test")
    ctx.state.update(
        {
            "product_brief": "AI startup tool",
            "target_market": "early-stage founders",
            "competitor_hints": ["CompA", "CompB", "CompC"],
            "target_user": "startup founders",
        }
    )

    # 使用真实 WorkflowOrchestrator
    group = loader.load("brand-creative")
    group.attach(engine=engine, llm=fake_llm, mcp=None)

    orchestrator = WorkflowOrchestrator()

    # 执行 workflow
    events = []
    async for event in orchestrator.execute(group, workflow_config, ctx):
        events.append(event)

    # 验证执行顺序: competitive-analysis 在 brand-strategy 前
    skill_order = []
    for event in events:
        if event.kind == "sub_skill_completed" and event.sub_skill:
            if event.sub_skill not in skill_order:
                skill_order.append(event.sub_skill)

    assert len(skill_order) >= 2, f"Expected 2 skills executed, got: {skill_order}"
    assert skill_order[0] == "competitive-analysis", f"First skill should be competitive-analysis, got: {skill_order}"
    assert skill_order[1] == "brand-strategy", f"Second skill should be brand-strategy, got: {skill_order}"

    # 验证同一个 ctx.state 中同时出现 competitor_matrix 和 brand_brief
    assert "competitor_matrix" in ctx.state, "competitor_matrix should be in shared state"
    assert "brand_brief" in ctx.state, "brand_brief should be in shared state"

    # 验证 brand_brief 的 basis 是 competitor_matrix（证明真实消费了）
    brand_brief = ctx.state["brand_brief"]
    assert brand_brief["differentiation"]["basis"] == "competitor_matrix", (
        "brand_brief should use competitor_matrix basis when matrix is available. "
        "If this fails, brand-strategy did not consume competitor_matrix from shared state."
    )


@pytest.mark.asyncio
async def test_brand_strategy_prompt_contains_competitor_matrix(tmp_path: Path) -> None:
    """B1.1.1: 证明 brand-strategy 的 rendered prompt 真实包含 competitor_matrix 内容.

    验证:
    1. 当 competitor_matrix 存在时，brand-strategy 的 prompt 包含竞品矩阵关键信息
    2. 当 competitor_matrix 缺失时，prompt 不包含竞品信息，输出 basis="inferred"
    """
    repo_root = Path(__file__).parent.parent.parent
    loader = SkillLoader([repo_root / "skills"])
    group = loader.load("brand-creative")

    # Test case 1: WITH competitor_matrix
    fake_llm_with_matrix = DeterministicFakeLLM(
        {
            "Stage 1: 分析上下文": {"context_analysis": {"context_summary": "3 competitors"}},
            "Stage 2: 产出品牌策略基线": {
                "brand_brief": {
                    "north_star": "让用户感到被理解",
                    "positioning": "专业服务",
                    "differentiation": {
                        "statement": "差异化",
                        "basis": "competitor_matrix",
                    },
                    "core_values": ["专业"],
                    "personality_keywords": ["专业", "可靠", "温暖"],
                    "target_user": "用户",
                },
            },
        }
    )
    engine_with = FakePipelineEngine(llm=fake_llm_with_matrix)
    group.attach(engine=engine_with, llm=fake_llm_with_matrix, mcp=None)

    ctx_with = _ctx(tmp_path, run_id="with-matrix")
    ctx_with.state.update(
        {
            "product_brief": "AI tool",
            "target_user": "startups",
            "competitor_matrix": {
                "competitors": [
                    {"name": "CompA", "visual_style": "minimal"},
                    {"name": "CompB", "visual_style": "bold"},
                    {"name": "CompC", "visual_style": "friendly"},
                ],
                "status": "complete",
            },
        }
    )

    result_with = await group.run_sub_skill("brand-strategy", ctx_with)
    assert result_with.status is RunStatus.COMPLETED

    # 验证 brand-strategy 的 prompt 包含竞品信息
    brand_strategy_prompts = fake_llm_with_matrix.full_prompts
    # brand-strategy 有两个 stage，所以至少应该有 2 个 prompt
    assert len(brand_strategy_prompts) >= 2, f"Expected at least 2 prompts, got {len(brand_strategy_prompts)}"

    # 至少一个 prompt 应该包含竞品名称
    has_competitor_info = any(
        "CompA" in prompt or "CompB" in prompt or "CompC" in prompt
        for prompt in brand_strategy_prompts
    )
    assert has_competitor_info, (
        "brand-strategy prompts should contain competitor names from competitor_matrix. "
        "Prompts recorded: " + str([p[:200] for p in brand_strategy_prompts])
    )

    # Test case 2: WITHOUT competitor_matrix
    fake_llm_without_matrix = DeterministicFakeLLM(
        {
            "Stage 1: 分析上下文": {"context_analysis": {"context_summary": "no competitors"}},
            "Stage 2: 产出品牌策略基线": {
                "brand_brief": {
                    "north_star": "让用户感到被理解",
                    "positioning": "专业服务",
                    "differentiation": {
                        "statement": "差异化",
                        "basis": "inferred",
                    },
                    "core_values": ["专业"],
                    "personality_keywords": ["专业", "可靠", "温暖"],
                    "target_user": "用户",
                },
            },
        }
    )
    engine_without = FakePipelineEngine(llm=fake_llm_without_matrix)
    group.attach(engine=engine_without, llm=fake_llm_without_matrix, mcp=None)

    ctx_without = _ctx(tmp_path, run_id="without-matrix")
    ctx_without.state.update(
        {
            "product_brief": "AI tool",
            "target_user": "startups",
            # NO competitor_matrix
        }
    )

    result_without = await group.run_sub_skill("brand-strategy", ctx_without)
    assert result_without.status is RunStatus.COMPLETED

    # 验证 brand_brief.basis == "inferred"
    assert ctx_without.state["brand_brief"]["differentiation"]["basis"] == "inferred", (
        "When competitor_matrix is missing, basis should be 'inferred'"
    )

    # 验证 prompt 不包含竞品信息（因为没有提供）
    prompts_without = fake_llm_without_matrix.full_prompts
    has_competitor_in_no_matrix = any(
        "CompA" in prompt or "CompB" in prompt or "CompC" in prompt
        for prompt in prompts_without
    )
    assert not has_competitor_in_no_matrix, (
        "When competitor_matrix is not provided, prompts should not contain competitor names. "
        "This proves the prompt is not hallucinating competitor data."
    )
