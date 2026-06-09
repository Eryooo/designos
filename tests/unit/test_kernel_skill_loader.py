"""Unit tests for kernel.skill_loader."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
import yaml

from kernel.contracts.enums import ErrorCode, OutputType, RunStatus, SkillType, StageStatus
from kernel.contracts.interfaces import IPipelineEngine, IPipelineSkill
from kernel.contracts.schemas import (
    DesignOSConfig,
    ErrorInfo,
    GlobalConfig,
    SkillContext,
    StageEvent,
    StageResult,
    ArtifactRef,
)
from kernel.skill_loader import (
    SkillLoader,
    load_pipeline_skill,
    load_skill_group,
    parse_frontmatter,
)


def _make_pipeline_skill(
    root: Path,
    name: str = "uxeval",
    *,
    skill_version: str = "1.0.0",
    pipeline_version: str | None = None,
) -> Path:
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        f"name: {name}\n"
        f"version: {skill_version}\n"
        "type: pipeline\n"
        "modes:\n"
        "  - id: web\n"
        "  - id: client\n"
        "requires:\n"
        "  kernel: \">=1.0.0,<2.0.0\"\n"
        "outputs:\n"
        "  - id: issue_report\n"
        "    type: issue_report\n"
        "    format: xlsx\n"
        "---\n"
        "# body\n",
        encoding="utf-8",
    )
    pipeline = {
        "name": f"{name}-pipeline",
        "stages": [
            {
                "id": "stage-1",
                "type": "llm",
                "prompt": "prompts/p1.md",
                "inputs": [],
                "outputs": ["x"],
                "knowledge": [],
            }
        ],
    }
    if pipeline_version is not None:
        pipeline["version"] = pipeline_version
    (skill_dir / "pipeline.yaml").write_text(yaml.safe_dump(pipeline), encoding="utf-8")
    (skill_dir / "prompts").mkdir(exist_ok=True)
    (skill_dir / "prompts" / "p1.md").write_text("body", encoding="utf-8")
    return skill_dir


def _ctx(workspace: Path, *, run_id: str = "001-test") -> SkillContext:
    return SkillContext(
        workspace=workspace,
        skill_name="uxeval",
        skill_version="1.0.0",
        run_id=run_id,
        config=DesignOSConfig(workspace=workspace, global_config=GlobalConfig()),
    )


def _event(kind: str, stage_id: str, **payload: Any) -> StageEvent:
    return StageEvent(
        kind=kind,  # type: ignore[arg-type]
        stage_id=stage_id,
        timestamp=datetime.now(UTC),
        payload=payload,
    )


class FakePipelineEngine(IPipelineEngine):
    def __init__(self, *, events: list[StageEvent], results: list[StageResult]) -> None:
        self._events = events
        self._results = results
        self.last_results: dict[str, list[StageResult]] = {}

    def execute(
        self,
        skill: IPipelineSkill,
        ctx: SkillContext,
    ) -> AsyncIterator[StageEvent]:
        self.last_results[ctx.run_id] = list(self._results)
        return self._iterate()

    async def _iterate(self) -> AsyncIterator[StageEvent]:
        for event in self._events:
            yield event


def test_parse_frontmatter(tmp_path: Path) -> None:
    p = tmp_path / "SKILL.md"
    p.write_text(
        "---\nname: x\nversion: 1.0.0\n---\nbody\n", encoding="utf-8"
    )
    fm, body = parse_frontmatter(p)
    assert fm["name"] == "x"
    assert body.startswith("body")


def test_load_pipeline_skill(tmp_path: Path) -> None:
    skill_dir = _make_pipeline_skill(tmp_path)
    skill = load_pipeline_skill(skill_dir)
    assert skill.name == "uxeval"
    assert skill.skill_type is SkillType.PIPELINE
    assert skill.config.version == "1.0.0"
    assert skill.config.supported_modes == ["web", "client"]
    assert skill.config.outputs[0].id == "issue_report"
    stages = skill.get_stages()
    assert len(stages) == 1
    assert stages[0].id == "stage-1"
    assert stages[0].prompt is not None
    assert stages[0].prompt.exists()


def test_load_pipeline_skill_version_comes_from_skill_frontmatter(tmp_path: Path) -> None:
    skill_dir = _make_pipeline_skill(
        tmp_path,
        skill_version="2.4.6",
        pipeline_version="9.9.9",
    )

    skill = load_pipeline_skill(skill_dir)

    assert skill.config.version == "2.4.6"


@pytest.mark.asyncio
async def test_pipeline_skill_run_returns_completed_on_success(tmp_path: Path) -> None:
    skill_dir = _make_pipeline_skill(tmp_path)
    skill = load_pipeline_skill(skill_dir)
    engine = FakePipelineEngine(
        events=[
            _event("stage_started", "stage-1"),
            _event("stage_completed", "stage-1", outputs=["x"]),
        ],
        results=[
            StageResult(
                stage_id="stage-1",
                status=StageStatus.COMPLETED,
                outputs={"x": "done"},
            )
        ],
    )
    skill.attach(engine=engine)

    result = await skill.run(_ctx(tmp_path, run_id="run-success"))

    assert result.status is RunStatus.COMPLETED
    assert result.paused_at_checkpoint is None
    assert [stage.stage_id for stage in result.stages] == ["stage-1"]


@pytest.mark.asyncio
async def test_pipeline_skill_run_aggregates_stage_artifacts(tmp_path: Path) -> None:
    skill_dir = _make_pipeline_skill(tmp_path)
    skill = load_pipeline_skill(skill_dir)
    artifacts = [
        ArtifactRef(
            id="issue_report",
            output_type=OutputType.ISSUE_REPORT,
            path=Path("outputs/issue_report.xlsx"),
            format="xlsx",
            summary="Issue workbook",
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
    engine = FakePipelineEngine(
        events=[
            _event("stage_started", "stage-1"),
            _event("stage_completed", "stage-1", outputs=["issue_report", "html_report", "evidence_pack"]),
        ],
        results=[
            StageResult(
                stage_id="stage-1",
                status=StageStatus.COMPLETED,
                outputs={"issue_report": {"id": "issue_report"}},
                artifacts=artifacts,
            )
        ],
    )
    skill.attach(engine=engine)

    result = await skill.run(_ctx(tmp_path, run_id="run-artifacts"))

    assert result.status is RunStatus.COMPLETED
    assert [artifact.id for artifact in result.artifacts] == [
        "issue_report",
        "html_report",
        "evidence_pack",
    ]


@pytest.mark.asyncio
async def test_pipeline_skill_run_returns_paused_on_checkpoint(tmp_path: Path) -> None:
    skill_dir = _make_pipeline_skill(tmp_path)
    skill = load_pipeline_skill(skill_dir)
    engine = FakePipelineEngine(
        events=[
            _event("stage_started", "stage-1"),
            _event("stage_completed", "stage-1", outputs=["x"]),
            _event("checkpoint", "stage-1", checkpoint_id="C1", message="confirm"),
        ],
        results=[
            StageResult(
                stage_id="stage-1",
                status=StageStatus.COMPLETED,
                outputs={"x": "done"},
            )
        ],
    )
    skill.attach(engine=engine)

    result = await skill.run(_ctx(tmp_path, run_id="run-paused"))

    assert result.status is RunStatus.PAUSED
    assert result.paused_at_checkpoint == "C1"
    assert result.pause_kind == "checkpoint"
    assert [stage.stage_id for stage in result.stages] == ["stage-1"]


@pytest.mark.asyncio
async def test_pipeline_skill_run_preserves_gate_pause_metadata(tmp_path: Path) -> None:
    skill_dir = _make_pipeline_skill(tmp_path)
    skill = load_pipeline_skill(skill_dir)
    engine = FakePipelineEngine(
        events=[
            _event("stage_started", "stage-1"),
            _event("stage_completed", "stage-1", outputs=["evidence_assessment"]),
            _event(
                "checkpoint",
                "stage-2",
                checkpoint_id="QG2",
                message="Evidence quality gate",
                pause_kind="gate",
                status_reason="current screenshots do not provide enough trustworthy text evidence",
                required_actions=["补 screens-description.md，说明页面名称、关键按钮、状态与流程"],
            ),
        ],
        results=[
            StageResult(
                stage_id="stage-1",
                status=StageStatus.COMPLETED,
                outputs={"evidence_assessment": {"verdict": "supplement_needed"}},
            )
        ],
    )
    skill.attach(engine=engine)

    result = await skill.run(_ctx(tmp_path, run_id="run-gate-paused"))

    assert result.status is RunStatus.PAUSED
    assert result.paused_at_checkpoint == "QG2"
    assert result.pause_kind == "gate"
    assert "trustworthy text evidence" in (result.status_reason or "")
    assert result.required_actions == ["补 screens-description.md，说明页面名称、关键按钮、状态与流程"]


@pytest.mark.asyncio
async def test_pipeline_skill_run_returns_failed_on_stage_failure(tmp_path: Path) -> None:
    skill_dir = _make_pipeline_skill(tmp_path)
    skill = load_pipeline_skill(skill_dir)
    engine = FakePipelineEngine(
        events=[
            _event("stage_started", "stage-1"),
            _event(
                "stage_failed",
                "stage-1",
                error={
                    "code": ErrorCode.E2001.value,
                    "message": "boom",
                },
            ),
        ],
        results=[
            StageResult(
                stage_id="stage-1",
                status=StageStatus.FAILED,
                error=ErrorInfo(
                    code=ErrorCode.E2001,
                    message="boom",
                ),
            )
        ],
    )
    skill.attach(engine=engine)

    result = await skill.run(_ctx(tmp_path, run_id="run-failed"))

    assert result.status is RunStatus.FAILED
    assert result.paused_at_checkpoint is None
    assert result.stages[0].status is StageStatus.FAILED


def test_skill_loader_lists_and_loads(tmp_path: Path) -> None:
    _make_pipeline_skill(tmp_path, "uxeval")
    _make_pipeline_skill(tmp_path, "prd2proto")
    loader = SkillLoader([tmp_path])
    assert loader.list_available() == ["prd2proto", "uxeval"]
    skill = loader.load("uxeval")
    assert skill.name == "uxeval"


def test_load_skill_group(tmp_path: Path) -> None:
    group_dir = tmp_path / "brand-creative"
    group_dir.mkdir()
    skills_dir = group_dir / "skills"
    skills_dir.mkdir()
    _make_pipeline_skill(skills_dir, "competitor")
    workflows = group_dir / "workflows"
    workflows.mkdir()
    workflow_yaml = workflows / "wf.yaml"
    workflow_yaml.write_text(
        yaml.safe_dump(
            {
                "name": "wf",
                "description": "test",
                "steps": [
                    {"type": "sequential", "sub_skills": ["competitor"]},
                ],
            }
        ),
        encoding="utf-8",
    )
    (group_dir / "GROUP.md").write_text(
        "---\n"
        "name: brand-creative\n"
        "version: 1.0.0\n"
        "type: group\n"
        "sub_skills:\n"
        "  - id: competitor\n"
        "    path: skills/competitor/SKILL.md\n"
        "workflows:\n"
        "  - id: wf\n"
        "    file: workflows/wf.yaml\n"
        "---\n",
        encoding="utf-8",
    )
    group = load_skill_group(group_dir)
    assert group.skill_type is SkillType.GROUP
    assert group.list_sub_skills() == ["competitor"]
    wf = group.get_workflow("wf")
    assert wf is not None
    assert wf.steps[0].sub_skills == ["competitor"]


# ─────────────────────────────────────────────────────────────────────────────
# B1.1 runtime tests — SkillGroup loadability, attach, sub-skill resolution
# ─────────────────────────────────────────────────────────────────────────────


def test_skill_group_attach_propagates_to_cached_sub_skills(tmp_path: Path) -> None:
    """B1.1: SkillGroup.attach() attaches engine/llm/mcp to already-cached sub-skills."""
    group_dir = tmp_path / "brand-creative"
    group_dir.mkdir()
    sub_skills_dir = group_dir / "sub-skills"
    sub_skills_dir.mkdir()
    _make_pipeline_skill(sub_skills_dir, "competitive-analysis")
    (group_dir / "GROUP.md").write_text(
        "---\n"
        "name: brand-creative\n"
        "version: 1.0.0\n"
        "type: group\n"
        "sub_skills:\n"
        "  - id: competitive-analysis\n"
        "    path: sub-skills/competitive-analysis/SKILL.md\n"
        "---\n",
        encoding="utf-8",
    )
    group = load_skill_group(group_dir)
    # Load sub-skill before attach
    sub_skill = group._load_sub_skill("competitive-analysis")
    assert sub_skill._engine is None

    # Attach group
    fake_engine = FakePipelineEngine(events=[], results=[])
    group.attach(engine=fake_engine)

    # Already-cached sub-skill should now have engine
    assert sub_skill._engine is fake_engine


def test_skill_loader_resolves_sub_skill_from_group_md(tmp_path: Path) -> None:
    """B1.1: SkillLoader resolves brand-creative:competitive-analysis from GROUP.md path."""
    group_dir = tmp_path / "brand-creative"
    group_dir.mkdir()
    sub_skills_dir = group_dir / "sub-skills"
    sub_skills_dir.mkdir()
    _make_pipeline_skill(sub_skills_dir, "competitive-analysis")
    (group_dir / "GROUP.md").write_text(
        "---\n"
        "name: brand-creative\n"
        "version: 1.0.0\n"
        "type: group\n"
        "sub_skills:\n"
        "  - id: competitive-analysis\n"
        "    path: sub-skills/competitive-analysis/SKILL.md\n"
        "---\n",
        encoding="utf-8",
    )
    loader = SkillLoader([tmp_path])
    skill = loader.load("brand-creative:competitive-analysis")
    assert skill.name == "competitive-analysis"
    assert skill.skill_type is SkillType.PIPELINE
