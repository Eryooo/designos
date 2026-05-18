"""Single-stage execution: LLM, MCP tool, or composite (sub-stages).

The runner is intentionally separate from the engine so it can be reused by
the workflow orchestrator and unit-tested in isolation.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from kernel.contracts.enums import ErrorCode, StageStatus, StageType
from kernel.contracts.interfaces import ILLMClient, IMCPClient
from kernel.contracts.schemas import (
    ErrorInfo,
    SkillContext,
    StageConfig,
    StageResult,
)
from kernel.errors import DesignOSError, PipelineError
from kernel.trace import get_logger

_log = get_logger("kernel.pipeline.stage")


class StageRunner:
    """Executes a single :class:`StageConfig` against the active context."""

    def __init__(self, *, llm: ILLMClient | None, mcp: IMCPClient | None) -> None:
        self._llm: ILLMClient | None = llm
        self._mcp: IMCPClient | None = mcp

    async def run(self, stage: StageConfig, ctx: SkillContext) -> StageResult:
        started: datetime = datetime.now(UTC)
        t0: float = time.monotonic()
        try:
            outputs: dict[str, Any] = await self._dispatch(stage, ctx)
        except DesignOSError as exc:
            duration_ms: int = int((time.monotonic() - t0) * 1000)
            _log.error("stage.failed", stage=stage.id, code=exc.error_code.value)
            return StageResult(
                stage_id=stage.id,
                status=StageStatus.FAILED,
                error=ErrorInfo(
                    code=exc.error_code,
                    message=exc.message,
                    context=exc.context,
                ),
                duration_ms=duration_ms,
                started_at=started,
                completed_at=datetime.now(UTC),
            )
        duration_ms = int((time.monotonic() - t0) * 1000)
        _log.info("stage.completed", stage=stage.id, ms=duration_ms)
        return StageResult(
            stage_id=stage.id,
            status=StageStatus.COMPLETED,
            outputs=outputs,
            duration_ms=duration_ms,
            started_at=started,
            completed_at=datetime.now(UTC),
        )

    async def _dispatch(self, stage: StageConfig, ctx: SkillContext) -> dict[str, Any]:
        if stage.type is StageType.LLM:
            return await self._run_llm(stage, ctx)
        if stage.type is StageType.TOOL:
            return await self._run_tool(stage, ctx)
        if stage.type is StageType.COMPOSITE:
            # Composite stages aggregate explicit sub-outputs from state; they
            # are pure passthroughs in M1 — skills can override by emitting
            # outputs prior to this stage.
            return {name: ctx.state.get(name) for name in stage.outputs}
        raise PipelineError(
            ErrorCode.E2001,
            f"unsupported stage type: {stage.type}",
            context={"stage": stage.id},
        )

    async def _run_llm(self, stage: StageConfig, ctx: SkillContext) -> dict[str, Any]:
        if self._llm is None:
            raise PipelineError(
                ErrorCode.E2001,
                "no LLM client attached to runner",
                context={"stage": stage.id},
            )
        prompt: str = self._render_prompt(stage, ctx)
        resp = await self._llm.call(prompt, max_tokens=4096)
        outputs: dict[str, Any] = {}
        if stage.outputs:
            outputs[stage.outputs[0]] = resp.text
            for extra in stage.outputs[1:]:
                outputs[extra] = ""
        outputs["__llm_meta__"] = {
            "model": resp.model,
            "input_tokens": resp.input_tokens,
            "output_tokens": resp.output_tokens,
        }
        return outputs

    async def _run_tool(self, stage: StageConfig, ctx: SkillContext) -> dict[str, Any]:
        if self._mcp is None:
            raise PipelineError(
                ErrorCode.E2001,
                "no MCP client attached to runner",
                context={"stage": stage.id},
            )
        if not stage.mcp_server or not stage.mcp_tool:
            raise PipelineError(
                ErrorCode.E2001,
                f"stage {stage.id} is type=tool but missing mcp_server/mcp_tool",
                context={"stage": stage.id},
            )
        args: dict[str, Any] = self._collect_inputs(stage, ctx)
        result = await self._mcp.call_tool(stage.mcp_server, stage.mcp_tool, args)
        if not result.ok:
            err: ErrorInfo | None = result.error
            raise PipelineError(
                ErrorCode.E3003,
                f"tool {stage.mcp_server}.{stage.mcp_tool} failed",
                context={"stage": stage.id, "error": err.model_dump() if err else None},
            )
        outputs: dict[str, Any] = {}
        data: dict[str, Any] = result.data or {}
        for name in stage.outputs:
            outputs[name] = data.get(name, data)
        return outputs

    def _render_prompt(self, stage: StageConfig, ctx: SkillContext) -> str:
        if stage.prompt is None:
            raise PipelineError(
                ErrorCode.E2001,
                f"stage {stage.id} is type=llm but has no prompt path",
                context={"stage": stage.id},
            )
        prompt_path: Path = stage.prompt
        body: str = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else ""
        knowledge: str = "\n\n".join(
            kpath.read_text(encoding="utf-8") for kpath in stage.knowledge if kpath.exists()
        )
        inputs: dict[str, Any] = self._collect_inputs(stage, ctx)
        rendered: str = body
        for key, value in inputs.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", _stringify(value))
        if knowledge:
            rendered = f"{rendered}\n\n# Reference knowledge\n{knowledge}"
        return rendered

    def _collect_inputs(self, stage: StageConfig, ctx: SkillContext) -> dict[str, Any]:
        inputs: dict[str, Any] = {}
        for name in stage.inputs:
            if name in ctx.state:
                inputs[name] = ctx.state[name]
            elif name in ctx.upstream_data:
                inputs[name] = ctx.upstream_data[name]
            else:
                raise PipelineError(
                    ErrorCode.E2002,
                    f"missing stage input: {name}",
                    context={"stage": stage.id, "input": name},
                )
        return inputs


def _stringify(value: Any) -> str:
    if isinstance(value, str):
        return value
    if hasattr(value, "model_dump_json"):
        return value.model_dump_json()  # type: ignore[no-any-return]
    return str(value)


__all__ = ["StageRunner"]
