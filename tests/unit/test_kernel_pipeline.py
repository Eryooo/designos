"""Unit tests for kernel.pipeline."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from kernel.contracts.enums import RunStatus, SkillType, StageStatus, StageType
from kernel.contracts.interfaces import ILLMClient, IMCPClient, IPipelineSkill
from kernel.contracts.schemas import (
    CheckpointConfig,
    DesignOSConfig,
    LLMResponse,
    SkillContext,
    SkillResult,
    StageConfig,
    StageEvent,
    ToolResult,
)
from kernel.pipeline import PipelineEngine, condition_satisfied


class FakeLLM(ILLMClient):
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def call(
        self,
        prompt: str,
        *,
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        self.calls.append(prompt)
        return LLMResponse(
            text=f"echo:{prompt[:30]}",
            model="fake",
            input_tokens=len(prompt),
            output_tokens=10,
            finish_reason="stop",
        )


class FakeMCP(IMCPClient):
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, dict[str, Any]]] = []

    async def call_tool(
        self, server: str, tool: str, args: dict[str, Any]
    ) -> ToolResult:
        self.calls.append((server, tool, args))
        return ToolResult(
            server=server,
            tool=tool,
            ok=True,
            data={"summary": f"{server}:{tool}", "raw_issues": ["one", "two"]},
            duration_ms=1,
        )


class StubPipelineSkill(IPipelineSkill):
    name = "stub"
    version = "1.0.0"
    skill_type = SkillType.PIPELINE

    def __init__(self, stages: list[StageConfig]) -> None:
        self._stages: list[StageConfig] = stages

    def get_stages(self) -> list[StageConfig]:
        return list(self._stages)

    async def run(self, ctx: SkillContext) -> SkillResult:
        return SkillResult(
            skill_name=self.name,
            skill_version=self.version,
            status=RunStatus.COMPLETED,
        )


def _ctx(workspace: Path, mode: str | None = None) -> SkillContext:
    cfg = DesignOSConfig(workspace=workspace)
    return SkillContext(
        workspace=workspace,
        skill_name="stub",
        skill_version="1.0.0",
        run_id="001-stub",
        mode=mode,  # type: ignore[arg-type]
        config=cfg,
    )


@pytest.mark.asyncio
async def test_pipeline_runs_three_stages(tmp_path: Path) -> None:
    prompt = tmp_path / "p.md"
    prompt.write_text("hello {{topic}}", encoding="utf-8")

    stages: list[StageConfig] = [
        StageConfig(
            id="seed",
            type=StageType.COMPOSITE,
            inputs=[],
            outputs=["topic"],
        ),
        StageConfig(
            id="ask",
            type=StageType.LLM,
            prompt=prompt,
            inputs=["topic"],
            outputs=["answer"],
        ),
        StageConfig(
            id="tool",
            type=StageType.TOOL,
            mcp_server="x",
            mcp_tool="y",
            inputs=["answer"],
            outputs=["summary"],
        ),
    ]
    engine = PipelineEngine(llm=FakeLLM(), mcp=FakeMCP())
    ctx = _ctx(tmp_path)
    ctx.state["topic"] = "kernel"  # COMPOSITE forwards from state
    events: list[StageEvent] = [ev async for ev in engine.execute(StubPipelineSkill(stages), ctx)]
    kinds = [ev.kind for ev in events]
    assert "stage_started" in kinds
    assert kinds.count("stage_completed") == 3
    assert ctx.state["answer"].startswith("echo:")
    assert ctx.state["summary"] == "x:y"


@pytest.mark.asyncio
async def test_only_when_skips_stage(tmp_path: Path) -> None:
    stages: list[StageConfig] = [
        StageConfig(
            id="web-only",
            type=StageType.COMPOSITE,
            inputs=[],
            outputs=["web_flag"],
            only_when='mode == "web"',
        ),
        StageConfig(
            id="always",
            type=StageType.COMPOSITE,
            inputs=[],
            outputs=["seen"],
        ),
    ]
    engine = PipelineEngine()
    ctx = _ctx(tmp_path, mode="client")
    ctx.state["seen"] = "yes"
    events = [ev async for ev in engine.execute(StubPipelineSkill(stages), ctx)]
    completed = [e for e in events if e.kind == "stage_completed"]
    assert any(e.payload.get("status") == StageStatus.SKIPPED.value for e in completed)


def test_condition_only_when_dsl(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path, mode="web")
    assert condition_satisfied('mode == "web"', ctx)
    assert not condition_satisfied('mode == "client"', ctx)
    assert condition_satisfied('mode in ["web","client"]', ctx)
    assert condition_satisfied(None, ctx)


@pytest.mark.asyncio
async def test_pipeline_defaults_missing_input_to_empty(tmp_path: Path) -> None:
    """M1: missing inputs default to empty so optional upstream fields don't break the pipeline."""
    prompt = tmp_path / "p.md"
    prompt.write_text("x", encoding="utf-8")
    stage = StageConfig(
        id="needs-foo",
        type=StageType.LLM,
        prompt=prompt,
        inputs=["foo"],
        outputs=["answer"],
    )
    engine = PipelineEngine(llm=FakeLLM())
    events = [ev async for ev in engine.execute(StubPipelineSkill([stage]), _ctx(tmp_path))]
    assert events[-1].kind == "stage_completed"


@pytest.mark.asyncio
async def test_checkpoint_stops_execution(tmp_path: Path) -> None:
    from kernel.checkpoint import CheckpointManager

    stages: list[StageConfig] = [
        StageConfig(
            id="s1",
            type=StageType.COMPOSITE,
            outputs=["x"],
            checkpoint=CheckpointConfig(id="C1", message="confirm"),
        ),
        StageConfig(id="s2", type=StageType.COMPOSITE, outputs=["y"]),
    ]
    cm = CheckpointManager(tmp_path)
    engine = PipelineEngine(checkpoint_manager=cm)
    ctx = _ctx(tmp_path)
    ctx.state["x"] = 1
    ctx.state["y"] = 2
    events = [ev async for ev in engine.execute(StubPipelineSkill(stages), ctx)]
    assert any(e.kind == "checkpoint" for e in events)
    snap = cm.load(ctx.run_id)
    assert snap is not None
    assert snap.current_stage_index == 1


def test_datetime_module_imported() -> None:
    # Smoke check that the module imports without circular issues.
    assert datetime.now(timezone.utc).tzinfo is not None
