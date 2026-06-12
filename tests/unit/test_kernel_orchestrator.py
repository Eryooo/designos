"""Unit tests for kernel.pipeline.WorkflowOrchestrator."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from kernel.contracts.enums import RunStatus, SkillType
from kernel.contracts.interfaces import ISkillGroup
from kernel.contracts.schemas import (
    DesignOSConfig,
    SkillContext,
    SkillResult,
    WorkflowConfig,
    WorkflowConfig as _WC,  # noqa: F401  alias kept for typing clarity
    WorkflowEvent,
    WorkflowStep,
)
from kernel.pipeline import WorkflowOrchestrator


class FakeGroup(ISkillGroup):
    name = "fake-group"
    version = "1.0.0"
    skill_type = SkillType.GROUP

    def __init__(self) -> None:
        self.calls: list[str] = []
        self._sub_skills: list[str] = ["a", "b", "c"]

    def list_sub_skills(self) -> list[str]:
        return list(self._sub_skills)

    def get_workflow(self, name: str) -> WorkflowConfig | None:
        return None

    async def run_sub_skill(self, name: str, ctx: SkillContext) -> SkillResult:
        await asyncio.sleep(0)
        self.calls.append(name)
        return SkillResult(
            skill_name=name,
            skill_version="1.0.0",
            status=RunStatus.COMPLETED,
        )

    async def run(self, ctx: SkillContext) -> SkillResult:  # pragma: no cover
        return SkillResult(skill_name=self.name, skill_version=self.version, status=RunStatus.COMPLETED)


def _ctx(tmp_path: Path) -> SkillContext:
    cfg = DesignOSConfig(workspace=tmp_path)
    return SkillContext(
        workspace=tmp_path,
        skill_name="fake",
        skill_version="1.0.0",
        run_id="001-fake",
        config=cfg,
    )


@pytest.mark.asyncio
async def test_sequential_runs_in_order(tmp_path: Path) -> None:
    group = FakeGroup()
    workflow = WorkflowConfig(
        name="wf",
        description="seq",
        steps=[WorkflowStep(type="sequential", sub_skills=["a", "b"])],
    )
    orch = WorkflowOrchestrator()
    events: list[WorkflowEvent] = [
        ev async for ev in orch.execute(group, workflow, _ctx(tmp_path))
    ]
    assert group.calls == ["a", "b"]
    assert any(ev.kind == "step_completed" for ev in events)


@pytest.mark.asyncio
async def test_parallel_runs_concurrently(tmp_path: Path) -> None:
    group = FakeGroup()
    workflow = WorkflowConfig(
        name="wf",
        description="par",
        steps=[WorkflowStep(type="parallel", sub_skills=["a", "b", "c"])],
    )
    orch = WorkflowOrchestrator()
    events: list[WorkflowEvent] = [
        ev async for ev in orch.execute(group, workflow, _ctx(tmp_path))
    ]
    assert sorted(group.calls) == ["a", "b", "c"]
    assert sum(1 for ev in events if ev.kind == "sub_skill_completed") == 3


@pytest.mark.asyncio
async def test_execute_parallel_aggregates(tmp_path: Path) -> None:
    group = FakeGroup()
    orch = WorkflowOrchestrator()
    results = await orch.execute_parallel(group, ["a", "b"], _ctx(tmp_path))
    assert set(results) == {"a", "b"}
    assert all(r.status is RunStatus.COMPLETED for r in results.values())
