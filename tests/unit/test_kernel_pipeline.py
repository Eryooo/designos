"""Unit tests for kernel.pipeline."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from kernel.contracts.enums import OutputType, RunStatus, SkillType, StageStatus, StageType
from kernel.contracts.interfaces import ILLMClient, IMCPClient, IPipelineSkill
from kernel.contracts.schemas import (
    ArtifactRef,
    CheckpointConfig,
    DesignOSConfig,
    LLMResponse,
    SkillConfig,
    SkillContext,
    SkillOutputConfig,
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


class ArtifactMCP(IMCPClient):
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, dict[str, Any]]] = []

    async def call_tool(
        self,
        server: str,
        tool: str,
        args: dict[str, Any],
    ) -> ToolResult:
        self.calls.append((server, tool, args))
        output_dir = Path(str(args["output_dir"]))
        output_dir.mkdir(parents=True, exist_ok=True)
        issue_report = output_dir / "issue_report.xlsx"
        html_report = output_dir / "issue_report.html"
        evidence_pack = output_dir / "evidence_pack"
        issue_report.write_text("xlsx", encoding="utf-8")
        html_report.write_text("<html></html>", encoding="utf-8")
        evidence_pack.mkdir(parents=True, exist_ok=True)
        (evidence_pack / "manifest.json").write_text("{}", encoding="utf-8")
        return ToolResult(
            server=server,
            tool=tool,
            ok=True,
            data={
                "issue_report": {
                    "id": "issue_report",
                    "type": "issue_report",
                    "path": str(issue_report),
                    "format": "xlsx",
                    "summary": "Excel report",
                },
                "html_report": {
                    "id": "html_report",
                    "type": "html_report",
                    "path": str(html_report),
                    "format": "html",
                    "summary": "HTML report",
                },
                "evidence_pack": {
                    "id": "evidence_pack",
                    "type": "evidence_pack",
                    "path": str(evidence_pack),
                    "format": "directory",
                    "summary": "Evidence pack",
                },
            },
            duration_ms=1,
        )


class MissingOutputMCP(IMCPClient):
    async def call_tool(
        self,
        server: str,
        tool: str,
        args: dict[str, Any],
    ) -> ToolResult:
        output_dir = Path(str(args["output_dir"]))
        output_dir.mkdir(parents=True, exist_ok=True)
        issue_report = output_dir / "issue_report.xlsx"
        issue_report.write_text("xlsx", encoding="utf-8")
        return ToolResult(
            server=server,
            tool=tool,
            ok=True,
            data={
                "issue_report": {
                    "id": "issue_report",
                    "type": "issue_report",
                    "path": str(issue_report),
                    "format": "xlsx",
                    "summary": "Excel report",
                },
                "html_report": {
                    "id": "html_report",
                    "type": "html_report",
                    "path": str(output_dir / "issue_report.html"),
                    "format": "html",
                    "summary": "HTML report",
                },
            },
            duration_ms=1,
        )


class InvalidArtifactMCP(IMCPClient):
    async def call_tool(
        self,
        server: str,
        tool: str,
        args: dict[str, Any],
    ) -> ToolResult:
        output_dir = Path(str(args["output_dir"]))
        output_dir.mkdir(parents=True, exist_ok=True)
        return ToolResult(
            server=server,
            tool=tool,
            ok=True,
            data={
                "issue_report": {
                    "id": "issue_report",
                    "type": "issue_report",
                    "path": str(output_dir / "issue_report.xlsx"),
                    "format": "xlsx",
                    "summary": "Excel report",
                },
                "html_report": {
                    "id": "html_report",
                    "path": str(output_dir / "issue_report.html"),
                    "format": "html",
                    "summary": "HTML report",
                },
                "evidence_pack": {
                    "id": "evidence_pack",
                    "type": "evidence_pack",
                    "path": str(output_dir / "evidence_pack"),
                    "format": "directory",
                    "summary": "Evidence pack",
                },
            },
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


def _ctx(
    workspace: Path,
    mode: str | None = None,
    *,
    declared_outputs: list[SkillOutputConfig] | None = None,
) -> SkillContext:
    cfg = DesignOSConfig(
        workspace=workspace,
        skill_config=SkillConfig(
            name="stub",
            version="1.0.0",
            skill_type=SkillType.PIPELINE,
            outputs=list(declared_outputs or []),
        ),
    )
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
async def test_tool_stage_outputs_are_promoted_to_artifacts(tmp_path: Path) -> None:
    stages = [
        StageConfig(
            id="report-generation",
            type=StageType.TOOL,
            mcp_server="excel-builder",
            mcp_tool="build_issue_report",
            inputs=["issues"],
            outputs=["issue_report", "html_report", "evidence_pack"],
        )
    ]
    mcp = ArtifactMCP()
    engine = PipelineEngine(mcp=mcp)
    ctx = _ctx(
        tmp_path,
        declared_outputs=[
            SkillOutputConfig(id="issue_report", type=OutputType.ISSUE_REPORT, format="xlsx"),
            SkillOutputConfig(id="html_report", type=OutputType.HTML_REPORT, format="html"),
            SkillOutputConfig(id="evidence_pack", type=OutputType.EVIDENCE_PACK, format="directory"),
        ],
    )
    ctx.state["issues"] = [{"id": "I-001", "title": "Sample"}]

    events = [ev async for ev in engine.execute(StubPipelineSkill(stages), ctx)]
    assert events[-1].kind == "stage_completed"

    stage_result = engine.last_results[ctx.run_id][0]
    assert stage_result.outputs["issue_report"]["id"] == "issue_report"
    assert [artifact.id for artifact in stage_result.artifacts] == [
        "issue_report",
        "html_report",
        "evidence_pack",
    ]
    assert stage_result.artifacts == [
        ArtifactRef(
            id="issue_report",
            output_type=OutputType.ISSUE_REPORT,
            path=Path("outputs/issue_report.xlsx"),
            format="xlsx",
            summary="Excel report",
        ),
        ArtifactRef(
            id="html_report",
            output_type=OutputType.HTML_REPORT,
            path=Path("outputs/issue_report.html"),
            format="html",
            summary="HTML report",
        ),
        ArtifactRef(
            id="evidence_pack",
            output_type=OutputType.EVIDENCE_PACK,
            path=Path("outputs/evidence_pack"),
            format="directory",
            summary="Evidence pack",
        ),
    ]
    assert "template" not in mcp.calls[0][2]


@pytest.mark.asyncio
async def test_tool_stage_fails_when_declared_output_is_missing(tmp_path: Path) -> None:
    stage = StageConfig(
        id="report-generation",
        type=StageType.TOOL,
        mcp_server="excel-builder",
        mcp_tool="build_issue_report",
        inputs=["issues"],
        outputs=["issue_report", "html_report", "evidence_pack"],
    )
    engine = PipelineEngine(mcp=MissingOutputMCP())
    ctx = _ctx(
        tmp_path,
        declared_outputs=[
            SkillOutputConfig(id="issue_report", type=OutputType.ISSUE_REPORT, format="xlsx"),
            SkillOutputConfig(id="html_report", type=OutputType.HTML_REPORT, format="html"),
            SkillOutputConfig(id="evidence_pack", type=OutputType.EVIDENCE_PACK, format="directory"),
        ],
    )
    ctx.state["issues"] = [{"id": "I-001"}]

    events = [ev async for ev in engine.execute(StubPipelineSkill([stage]), ctx)]

    assert events[-1].kind == "stage_failed"
    stage_result = engine.last_results[ctx.run_id][0]
    assert stage_result.status is StageStatus.FAILED
    assert stage_result.error is not None
    assert "evidence_pack" in stage_result.error.message


@pytest.mark.asyncio
async def test_tool_stage_fails_when_artifact_payload_is_invalid(tmp_path: Path) -> None:
    stage = StageConfig(
        id="report-generation",
        type=StageType.TOOL,
        mcp_server="excel-builder",
        mcp_tool="build_issue_report",
        inputs=["issues"],
        outputs=["issue_report", "html_report", "evidence_pack"],
    )
    engine = PipelineEngine(mcp=InvalidArtifactMCP())
    ctx = _ctx(
        tmp_path,
        declared_outputs=[
            SkillOutputConfig(id="issue_report", type=OutputType.ISSUE_REPORT, format="xlsx"),
            SkillOutputConfig(id="html_report", type=OutputType.HTML_REPORT, format="html"),
            SkillOutputConfig(id="evidence_pack", type=OutputType.EVIDENCE_PACK, format="directory"),
        ],
    )
    ctx.state["issues"] = [{"id": "I-001"}]

    events = [ev async for ev in engine.execute(StubPipelineSkill([stage]), ctx)]

    assert events[-1].kind == "stage_failed"
    stage_result = engine.last_results[ctx.run_id][0]
    assert stage_result.status is StageStatus.FAILED
    assert stage_result.error is not None
    assert "html_report" in stage_result.error.message


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


def test_condition_dsl_supports_runtime_state_paths(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path, mode="client")
    ctx.state["evidence_assessment"] = {
        "verdict": "supplement_needed",
        "required_actions": ["补 screens-description.md"],
    }
    assert condition_satisfied('evidence_assessment.verdict == "supplement_needed"', ctx)
    assert condition_satisfied(
        'evidence_assessment.verdict in ["blocked", "supplement_needed"]',
        ctx,
    )
    assert not condition_satisfied('evidence_assessment.verdict == "sufficient"', ctx)


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


@pytest.mark.asyncio
async def test_stage_gate_pauses_and_rewinds_resume_index(tmp_path: Path) -> None:
    from kernel.checkpoint import CheckpointManager

    stages: list[StageConfig] = [
        StageConfig(
            id="screenshot-loading",
            type=StageType.COMPOSITE,
            outputs=["evidence_assessment"],
        ),
        StageConfig(
            id="issue-attribution",
            type=StageType.COMPOSITE,
            outputs=["issues"],
            gate={
                "when": 'evidence_assessment.verdict in ["blocked", "supplement_needed"]',
                "action": "pause",
                "checkpoint_id": "QG2",
                "message": "Need better evidence before issue attribution.",
                "status_reason_from": "evidence_assessment.blocking_reasons",
                "required_actions_from": "evidence_assessment.required_actions",
                "resume_from_stage": "screenshot-loading",
            },
        ),
        StageConfig(id="report-generation", type=StageType.COMPOSITE, outputs=["report"]),
    ]
    cm = CheckpointManager(tmp_path)
    engine = PipelineEngine(checkpoint_manager=cm)
    ctx = _ctx(tmp_path, mode="client")
    ctx.state["evidence_assessment"] = {
        "verdict": "blocked",
        "blocking_reasons": ["no OCR capability and no markdown description evidence"],
        "required_actions": ["补充 inputs/screens-description.md"],
    }
    ctx.state["issues"] = [{"id": "I-001"}]
    ctx.state["report"] = {"ready": True}

    events = [ev async for ev in engine.execute(StubPipelineSkill(stages), ctx)]

    assert [event.kind for event in events] == ["stage_started", "stage_completed", "checkpoint"]
    gate_event = events[-1]
    assert gate_event.payload["pause_kind"] == "gate"
    assert gate_event.payload["checkpoint_id"] == "QG2"
    assert gate_event.payload["required_actions"] == ["补充 inputs/screens-description.md"]
    assert "no OCR capability" in gate_event.payload["status_reason"]

    snap = cm.load(ctx.run_id)
    assert snap is not None
    assert snap.current_stage_index == 0
    assert snap.completed_stage_ids == []
    assert snap.pending_stage_ids == ["screenshot-loading", "issue-attribution", "report-generation"]
    assert [stage.stage_id for stage in engine.last_results[ctx.run_id]] == ["screenshot-loading"]


@pytest.mark.asyncio
async def test_stage_gate_allows_sufficient_evidence_to_continue(tmp_path: Path) -> None:
    stages: list[StageConfig] = [
        StageConfig(
            id="screenshot-loading",
            type=StageType.COMPOSITE,
            outputs=["evidence_assessment"],
        ),
        StageConfig(
            id="issue-attribution",
            type=StageType.COMPOSITE,
            outputs=["issues"],
            gate={
                "when": 'evidence_assessment.verdict in ["blocked", "supplement_needed"]',
                "action": "pause",
                "checkpoint_id": "QG2",
                "message": "Need better evidence before issue attribution.",
                "required_actions_from": "evidence_assessment.required_actions",
                "resume_from_stage": "screenshot-loading",
            },
        ),
        StageConfig(id="report-generation", type=StageType.COMPOSITE, outputs=["report"]),
    ]
    engine = PipelineEngine()
    ctx = _ctx(tmp_path, mode="client")
    ctx.state["evidence_assessment"] = {
        "verdict": "sufficient",
        "required_actions": [],
    }
    ctx.state["issues"] = [{"id": "I-001"}]
    ctx.state["report"] = {"ready": True}

    events = [ev async for ev in engine.execute(StubPipelineSkill(stages), ctx)]

    assert [event.kind for event in events].count("checkpoint") == 0
    assert [stage.stage_id for stage in engine.last_results[ctx.run_id]] == [
        "screenshot-loading",
        "issue-attribution",
        "report-generation",
    ]


@pytest.mark.asyncio
async def test_stage_gate_blocks_report_generation_when_evidence_is_not_sufficient(
    tmp_path: Path,
) -> None:
    stages: list[StageConfig] = [
        StageConfig(
            id="screenshot-loading",
            type=StageType.COMPOSITE,
            outputs=["evidence_assessment"],
        ),
        StageConfig(
            id="issue-attribution",
            type=StageType.COMPOSITE,
            outputs=["issues"],
        ),
        StageConfig(
            id="report-generation",
            type=StageType.COMPOSITE,
            outputs=["report"],
            gate={
                "when": 'evidence_assessment.verdict in ["blocked", "supplement_needed"]',
                "action": "pause",
                "checkpoint_id": "QG3",
                "message": "Need better evidence before final report generation.",
                "required_actions_from": "evidence_assessment.required_actions",
                "resume_from_stage": "screenshot-loading",
            },
        ),
    ]
    engine = PipelineEngine()
    ctx = _ctx(tmp_path, mode="client")
    ctx.state["evidence_assessment"] = {
        "verdict": "supplement_needed",
        "required_actions": ["补高分辨率截图，建议宽度 >= 1280 像素"],
    }
    ctx.state["issues"] = [{"id": "I-001"}]
    ctx.state["report"] = {"ready": True}

    events = [ev async for ev in engine.execute(StubPipelineSkill(stages), ctx)]

    assert [event.kind for event in events] == [
        "stage_started",
        "stage_completed",
        "stage_started",
        "stage_completed",
        "checkpoint",
    ]
    assert events[-1].payload["checkpoint_id"] == "QG3"
    assert [stage.stage_id for stage in engine.last_results[ctx.run_id]] == [
        "screenshot-loading",
        "issue-attribution",
    ]


def test_datetime_module_imported() -> None:
    # Smoke check that the module imports without circular issues.
    assert datetime.now(timezone.utc).tzinfo is not None
