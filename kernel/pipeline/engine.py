"""Concrete :class:`IPipelineEngine` driving a Pipeline Skill stage by stage."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

from kernel.checkpoint import CheckpointManager
from kernel.contracts.enums import ErrorCode, StageStatus
from kernel.contracts.interfaces import (
    ICheckpointManager,
    ILLMClient,
    IMCPClient,
    IPipelineEngine,
    IPipelineSkill,
)
from kernel.contracts.schemas import (
    CheckpointSnapshot,
    SkillContext,
    StageConfig,
    StageEvent,
    StageGateConfig,
    StageResult,
)
from kernel.errors import PipelineError
from kernel.trace import get_logger

from .condition import condition_satisfied, context_value
from .stage_runner import StageRunner

_log = get_logger("kernel.pipeline.engine")


class PipelineEngine(IPipelineEngine):
    """Sequential stage executor with checkpoint pause/resume support."""

    def __init__(
        self,
        *,
        llm: ILLMClient | None = None,
        mcp: IMCPClient | None = None,
        checkpoint_manager: ICheckpointManager | None = None,
        runner: StageRunner | None = None,
    ) -> None:
        self._runner: StageRunner = runner or StageRunner(llm=llm, mcp=mcp)
        self._checkpoint_manager: ICheckpointManager | None = checkpoint_manager
        self._last_results: dict[str, list[StageResult]] = {}

    @property
    def last_results(self) -> dict[str, list[StageResult]]:
        """Return the per-run stage results recorded during the latest execute()."""
        return dict(self._last_results)

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
        stages: list[StageConfig] = skill.get_stages()
        stage_index_by_id: dict[str, int] = {stage.id: idx for idx, stage in enumerate(stages)}
        completed: list[StageResult] = []
        self._last_results[ctx.run_id] = completed

        # Resume support: if a snapshot exists, fast-forward through done stages.
        start_index: int = 0
        if self._checkpoint_manager is not None:
            snap: CheckpointSnapshot | None = self._checkpoint_manager.load(ctx.run_id)
            if snap is not None:
                start_index = snap.current_stage_index
                restored_state = dict(snap.state_snapshot)
                restored_state.update(ctx.state)
                ctx.state = restored_state

        for idx in range(start_index, len(stages)):
            stage: StageConfig = stages[idx]
            if not condition_satisfied(stage.only_when, ctx):
                yield _event("stage_completed", stage.id, payload={"status": StageStatus.SKIPPED.value})
                continue
            gate_event = self._gate_event(
                skill=skill,
                stages=stages,
                stage=stage,
                stage_index=idx,
                stage_index_by_id=stage_index_by_id,
                completed=completed,
                ctx=ctx,
            )
            if gate_event is not None:
                yield gate_event
                return
            yield _event("stage_started", stage.id)
            result: StageResult = await self._run_with_retry(stage, ctx)
            completed.append(result)
            if result.status is StageStatus.COMPLETED:
                ctx.state.update(result.outputs)
                yield _event(
                    "stage_completed",
                    stage.id,
                    payload={"outputs": list(result.outputs)},
                )
                if stage.checkpoint is not None:
                    self._save_checkpoint(
                        skill=skill,
                        stages=stages,
                        resume_index=idx + 1,
                        completed=completed,
                        stage_index_by_id=stage_index_by_id,
                        ctx=ctx,
                    )
                    yield _event(
                        "checkpoint",
                        stage.id,
                        payload={
                            "checkpoint_id": stage.checkpoint.id,
                            "message": stage.checkpoint.message,
                            "pause_kind": "checkpoint",
                            "required_actions": [],
                        },
                    )
                    return
            else:
                yield _event(
                    "stage_failed",
                    stage.id,
                    payload={"error": result.error.model_dump() if result.error else None},
                )
                return

        if self._checkpoint_manager is not None:
            self._checkpoint_manager.discard(ctx.run_id)

    async def _run_with_retry(self, stage: StageConfig, ctx: SkillContext) -> StageResult:
        attempts: int = max(1, stage.retry.max_attempts)
        last: StageResult | None = None
        for attempt in range(1, attempts + 1):
            result: StageResult = await self._runner.run(stage, ctx)
            if result.status is StageStatus.COMPLETED:
                return result
            last = result
            if not _retryable(result, stage):
                break
            _log.warning("stage.retry", stage=stage.id, attempt=attempt)
        if last is None:
            raise PipelineError(
                ErrorCode.E2001,
                f"stage {stage.id} produced no result",
                context={"stage": stage.id},
            )
        return last

    def _gate_event(
        self,
        *,
        skill: IPipelineSkill,
        stages: list[StageConfig],
        stage: StageConfig,
        stage_index: int,
        stage_index_by_id: dict[str, int],
        completed: list[StageResult],
        ctx: SkillContext,
    ) -> StageEvent | None:
        gate: StageGateConfig | None = stage.gate
        if gate is None or not condition_satisfied(gate.when, ctx):
            return None

        status_reason = _gate_status_reason(gate, ctx)
        required_actions = _string_list(context_value(ctx, gate.required_actions_from))
        if gate.action == "fail":
            return _event(
                "stage_failed",
                stage.id,
                payload={
                    "error": {
                        "code": ErrorCode.E2001.value,
                        "message": status_reason or gate.message or f"runtime gate failed before {stage.id}",
                        "context": {
                            "stage": stage.id,
                            "required_actions": required_actions,
                        },
                    }
                },
            )

        resume_index = stage_index
        if gate.resume_from_stage:
            resume_index = stage_index_by_id.get(gate.resume_from_stage, stage_index)
        self._save_checkpoint(
            skill=skill,
            stages=stages,
            resume_index=resume_index,
            completed=completed,
            stage_index_by_id=stage_index_by_id,
            ctx=ctx,
        )
        return _event(
            "checkpoint",
            stage.id,
            payload={
                "checkpoint_id": gate.checkpoint_id or stage.id,
                "message": gate.message or f"runtime gate paused before {stage.id}",
                "pause_kind": "gate",
                "status_reason": status_reason,
                "required_actions": required_actions,
            },
        )

    def _save_checkpoint(
        self,
        *,
        skill: IPipelineSkill,
        stages: list[StageConfig],
        resume_index: int,
        completed: list[StageResult],
        stage_index_by_id: dict[str, int],
        ctx: SkillContext,
    ) -> None:
        if self._checkpoint_manager is None:
            return
        bounded_resume_index = max(0, min(resume_index, len(stages)))
        completed_stage_ids = [
            result.stage_id
            for result in completed
            if stage_index_by_id.get(result.stage_id, len(stages)) < bounded_resume_index
        ]
        snapshot = CheckpointSnapshot(
            run_id=ctx.run_id,
            skill=skill.name,
            current_stage_index=bounded_resume_index,
            completed_stage_ids=completed_stage_ids,
            pending_stage_ids=[stage.id for stage in stages[bounded_resume_index:]],
            state_snapshot=dict(ctx.state),
            last_updated=datetime.now(UTC),
        )
        self._checkpoint_manager.save(snapshot)


def _retryable(result: StageResult, stage: StageConfig) -> bool:
    if result.error is None:
        return False
    retry_on = stage.retry.retry_on
    if not retry_on:
        return True
    return result.error.code in retry_on


def _gate_status_reason(gate: StageGateConfig, ctx: SkillContext) -> str | None:
    value = context_value(ctx, gate.status_reason_from)
    if isinstance(value, str) and value.strip():
        return value.strip()
    values = _string_list(value)
    if values:
        return "; ".join(values)
    if gate.message.strip():
        return gate.message.strip()
    return None


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        cleaned = value.strip()
        return [cleaned] if cleaned else []
    if isinstance(value, list):
        items: list[str] = []
        for item in value:
            if item is None:
                continue
            cleaned = str(item).strip()
            if cleaned:
                items.append(cleaned)
        return items
    return []


def _event(kind: str, stage_id: str, *, payload: dict[str, Any] | None = None) -> StageEvent:
    return StageEvent(
        kind=kind,  # type: ignore[arg-type]
        stage_id=stage_id,
        timestamp=datetime.now(UTC),
        payload=payload or {},
    )


def make_engine(
    *,
    workspace: Any | None = None,
    llm: ILLMClient | None = None,
    mcp: IMCPClient | None = None,
) -> PipelineEngine:
    """Convenience constructor wiring a :class:`CheckpointManager` to ``workspace``."""
    cm: ICheckpointManager | None = None
    if workspace is not None:
        cm = CheckpointManager(workspace.root if hasattr(workspace, "root") else workspace)
    return PipelineEngine(llm=llm, mcp=mcp, checkpoint_manager=cm)


__all__ = ["PipelineEngine", "make_engine"]
