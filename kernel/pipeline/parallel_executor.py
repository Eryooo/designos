"""Parallel sub-skill executor for Skill Groups."""

from __future__ import annotations

import asyncio
from typing import Any

from kernel.contracts.enums import ErrorCode, RunStatus
from kernel.contracts.interfaces import ISkillGroup
from kernel.contracts.schemas import SkillContext, SkillResult
from kernel.errors import PipelineError
from kernel.trace import get_logger

_log = get_logger("kernel.pipeline.parallel")


class ParallelExecutor:
    """Runs a list of sub-skills concurrently and aggregates their results."""

    async def run_all(
        self,
        group: ISkillGroup,
        sub_skill_names: list[str],
        ctx: SkillContext,
        *,
        on_failure: str = "abort",
    ) -> dict[str, SkillResult]:
        if not sub_skill_names:
            return {}
        tasks: list[asyncio.Task[SkillResult]] = [
            asyncio.create_task(self._run_one(group, name, ctx)) for name in sub_skill_names
        ]
        gathered: list[Any] = await asyncio.gather(*tasks, return_exceptions=True)
        results: dict[str, SkillResult] = {}
        for name, outcome in zip(sub_skill_names, gathered, strict=True):
            if isinstance(outcome, BaseException):
                _log.error("parallel.sub_skill_failed", sub_skill=name, error=str(outcome))
                if on_failure == "abort":
                    raise PipelineError(
                        ErrorCode.E2001,
                        f"parallel sub-skill {name} failed: {outcome}",
                        context={"sub_skill": name},
                    ) from outcome
                results[name] = SkillResult(
                    skill_name=name,
                    skill_version="0.0.0",
                    status=RunStatus.FAILED,
                )
                continue
            assert isinstance(outcome, SkillResult)
            results[name] = outcome
        return results

    async def _run_one(
        self,
        group: ISkillGroup,
        name: str,
        ctx: SkillContext,
    ) -> SkillResult:
        return await group.run_sub_skill(name, ctx)


__all__ = ["ParallelExecutor"]
