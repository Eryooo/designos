"""Workflow orchestrator for Skill Groups."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

from kernel.contracts.enums import ErrorCode, RunStatus
from kernel.contracts.interfaces import ISkillGroup, IWorkflowOrchestrator
from kernel.contracts.schemas import (
    SkillContext,
    SkillResult,
    WorkflowConfig,
    WorkflowEvent,
    WorkflowStep,
)
from kernel.errors import PipelineError
from kernel.trace import get_logger

from .parallel_executor import ParallelExecutor

_log = get_logger("kernel.pipeline.orchestrator")


class WorkflowOrchestrator(IWorkflowOrchestrator):
    """Drives a Skill Group through a sequential / parallel workflow."""

    def __init__(self, parallel: ParallelExecutor | None = None) -> None:
        self._parallel: ParallelExecutor = parallel or ParallelExecutor()

    def execute(
        self,
        group: ISkillGroup,
        workflow: WorkflowConfig,
        ctx: SkillContext,
    ) -> AsyncIterator[WorkflowEvent]:
        return self._iterate(group, workflow, ctx)

    async def execute_parallel(
        self,
        group: ISkillGroup,
        sub_skill_names: list[str],
        ctx: SkillContext,
    ) -> dict[str, SkillResult]:
        return await self._parallel.run_all(group, sub_skill_names, ctx)

    async def _iterate(
        self,
        group: ISkillGroup,
        workflow: WorkflowConfig,
        ctx: SkillContext,
    ) -> AsyncIterator[WorkflowEvent]:
        for index, step in enumerate(workflow.steps):
            yield _event("step_started", index)
            if step.type == "sequential":
                async for ev in self._run_sequential(group, step, ctx, index):
                    yield ev
            else:
                async for ev in self._run_parallel(group, step, ctx, index):
                    yield ev
            yield _event("step_completed", index)

    async def _run_sequential(
        self,
        group: ISkillGroup,
        step: WorkflowStep,
        ctx: SkillContext,
        index: int,
    ) -> AsyncIterator[WorkflowEvent]:
        for sub in step.sub_skills:
            yield _event("sub_skill_started", index, sub_skill=sub)
            try:
                result: SkillResult = await group.run_sub_skill(sub, ctx)
            except Exception as exc:
                _log.error("orchestrator.sub_skill_failed", sub_skill=sub, error=str(exc))
                yield _event(
                    "sub_skill_failed",
                    index,
                    sub_skill=sub,
                    payload={"error": str(exc)},
                )
                if step.on_failure == "abort":
                    raise PipelineError(
                        ErrorCode.E2001,
                        f"sub-skill {sub} failed",
                        context={"sub_skill": sub, "step": index},
                    ) from exc
                continue
            if result.status is RunStatus.FAILED:
                yield _event("sub_skill_failed", index, sub_skill=sub)
                if step.on_failure == "abort":
                    raise PipelineError(
                        ErrorCode.E2001,
                        f"sub-skill {sub} failed",
                        context={"sub_skill": sub, "step": index},
                    )
                continue
            yield _event("sub_skill_completed", index, sub_skill=sub)

    async def _run_parallel(
        self,
        group: ISkillGroup,
        step: WorkflowStep,
        ctx: SkillContext,
        index: int,
    ) -> AsyncIterator[WorkflowEvent]:
        for sub in step.sub_skills:
            yield _event("sub_skill_started", index, sub_skill=sub)
        results: dict[str, SkillResult] = await self._parallel.run_all(
            group, step.sub_skills, ctx, on_failure=step.on_failure
        )
        for sub in step.sub_skills:
            res: SkillResult | None = results.get(sub)
            if res is None or res.status is RunStatus.FAILED:
                yield _event("sub_skill_failed", index, sub_skill=sub)
            else:
                yield _event("sub_skill_completed", index, sub_skill=sub)


def _event(
    kind: str,
    step_index: int,
    *,
    sub_skill: str | None = None,
    payload: dict[str, Any] | None = None,
) -> WorkflowEvent:
    return WorkflowEvent(
        kind=kind,  # type: ignore[arg-type]
        step_index=step_index,
        sub_skill=sub_skill,
        timestamp=datetime.now(UTC),
        payload=payload or {},
    )


__all__ = ["WorkflowOrchestrator"]
