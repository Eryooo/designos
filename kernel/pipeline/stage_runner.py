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
    ArtifactRef,
    ErrorInfo,
    SkillContext,
    SkillOutputConfig,
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
            outputs, artifacts = await self._dispatch(stage, ctx)
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
            artifacts=artifacts,
            duration_ms=duration_ms,
            started_at=started,
            completed_at=datetime.now(UTC),
        )

    async def _dispatch(
        self,
        stage: StageConfig,
        ctx: SkillContext,
    ) -> tuple[dict[str, Any], list[ArtifactRef]]:
        if stage.type is StageType.LLM:
            return await self._run_llm(stage, ctx)
        if stage.type is StageType.TOOL:
            return await self._run_tool(stage, ctx)
        if stage.type is StageType.COMPOSITE:
            # Composite stages aggregate explicit sub-outputs from state; they
            # are pure passthroughs in M1 — skills can override by emitting
            # outputs prior to this stage.
            return {name: ctx.state.get(name) for name in stage.outputs}, []
        raise PipelineError(
            ErrorCode.E2001,
            f"unsupported stage type: {stage.type}",
            context={"stage": stage.id},
        )

    async def _run_llm(
        self,
        stage: StageConfig,
        ctx: SkillContext,
    ) -> tuple[dict[str, Any], list[ArtifactRef]]:
        if self._llm is None:
            raise PipelineError(
                ErrorCode.E2001,
                "no LLM client attached to runner",
                context={"stage": stage.id},
            )
        prompt: str = self._render_prompt(stage, ctx)
        resp = await self._llm.call(prompt, max_tokens=4096)
        outputs: dict[str, Any] = _parse_llm_outputs(resp.text, stage.outputs)
        outputs["__llm_meta__"] = {
            "model": resp.model,
            "input_tokens": resp.input_tokens,
            "output_tokens": resp.output_tokens,
        }
        return outputs, []

    async def _run_tool(
        self,
        stage: StageConfig,
        ctx: SkillContext,
    ) -> tuple[dict[str, Any], list[ArtifactRef]]:
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
        args = self._augment_tool_args(stage, ctx, args)
        result = await self._mcp.call_tool(stage.mcp_server, stage.mcp_tool, args)
        if not result.ok:
            err: ErrorInfo | None = result.error
            message = (
                err.message
                if err is not None and err.message.strip()
                else f"tool {stage.mcp_server}.{stage.mcp_tool} failed"
            )
            raise PipelineError(
                ErrorCode.E3003,
                message,
                context={"stage": stage.id, "error": err.model_dump() if err else None},
            )
        outputs: dict[str, Any] = {}
        artifacts: list[ArtifactRef] = []
        data: dict[str, Any] = result.data or {}
        declared_artifacts = self._declared_artifact_outputs(ctx)
        for name in stage.outputs:
            if name not in data:
                raise PipelineError(
                    ErrorCode.E3003,
                    f"tool {stage.mcp_server}.{stage.mcp_tool} did not return declared output '{name}'",
                    context={"stage": stage.id, "missing_output": name, "returned_keys": sorted(data)},
                )
            outputs[name] = data[name]
            artifact_spec = declared_artifacts.get(name)
            artifact = self._artifact_from_output(name, outputs[name], ctx, artifact_spec)
            if artifact is not None:
                artifacts.append(artifact)
        return outputs, artifacts

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
                # M1 pragmatic default: missing inputs become empty so optional
                # upstream-injected fields (e.g. existing_personas from
                # ai-analytics) don't break the pipeline. M2 will introduce
                # explicit ``required: bool`` markers per input.
                inputs[name] = ""
        return inputs

    def _augment_tool_args(
        self,
        stage: StageConfig,
        ctx: SkillContext,
        args: dict[str, Any],
    ) -> dict[str, Any]:
        run_dir = (ctx.workspace / "runs" / ctx.run_id).resolve()
        output_dir = run_dir / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)

        augmented = dict(args)
        augmented.setdefault("run_id", ctx.run_id)
        augmented.setdefault("skill_name", ctx.skill_name)
        augmented.setdefault("skill_version", ctx.skill_version)
        augmented.setdefault("stage_id", stage.id)
        augmented.setdefault("output_dir", str(output_dir))

        if stage.mcp_server == "excel-builder" and stage.mcp_tool == "build_issue_report":
            augmented.setdefault("output_path", str(output_dir / "issue_report.xlsx"))
        return augmented

    def _declared_artifact_outputs(self, ctx: SkillContext) -> dict[str, SkillOutputConfig]:
        skill_config = getattr(ctx.config, "skill_config", None)
        outputs = getattr(skill_config, "outputs", None)
        if not isinstance(outputs, list):
            return {}
        return {
            output.id: output
            for output in outputs
            if isinstance(output, SkillOutputConfig)
        }

    def _artifact_from_output(
        self,
        output_name: str,
        payload: Any,
        ctx: SkillContext,
        artifact_spec: SkillOutputConfig | None,
    ) -> ArtifactRef | None:
        if artifact_spec is None:
            return None
        if not isinstance(payload, dict):
            raise PipelineError(
                ErrorCode.E3003,
                f"tool output {output_name} must be a structured artifact payload",
                context={"stage_output": output_name, "payload": payload},
            )
        artifact_type = payload.get("type") or payload.get("output_type")
        artifact_path = payload.get("path")
        artifact_format = payload.get("format")
        if artifact_type is None or artifact_path is None or artifact_format is None:
            raise PipelineError(
                ErrorCode.E3003,
                f"tool output {output_name} is missing artifact fields",
                context={"stage_output": output_name, "payload": payload},
            )
        if str(artifact_type) != artifact_spec.type.value:
            raise PipelineError(
                ErrorCode.E3003,
                f"tool output {output_name} declared type {artifact_spec.type.value} but returned {artifact_type}",
                context={"stage_output": output_name, "payload": payload},
            )
        if str(artifact_format) != artifact_spec.format:
            raise PipelineError(
                ErrorCode.E3003,
                f"tool output {output_name} declared format {artifact_spec.format} but returned {artifact_format}",
                context={"stage_output": output_name, "payload": payload},
            )

        run_dir = (ctx.workspace / "runs" / ctx.run_id).resolve()
        resolved_path = Path(str(artifact_path)).expanduser()
        if resolved_path.is_absolute():
            try:
                normalised_path = resolved_path.resolve().relative_to(run_dir)
            except ValueError:
                normalised_path = resolved_path.resolve()
        else:
            normalised_path = resolved_path

        try:
            return ArtifactRef.model_validate(
                {
                    "id": str(payload.get("id") or output_name),
                    "output_type": artifact_type,
                    "path": normalised_path,
                    "format": artifact_format,
                    "summary": str(payload.get("summary", "")),
                }
            )
        except Exception as exc:
            raise PipelineError(
                ErrorCode.E3003,
                f"tool output {output_name} is not a valid artifact payload",
                context={"stage_output": output_name, "payload": payload},
            ) from exc


def _stringify(value: Any) -> str:
    if isinstance(value, str):
        return value
    if hasattr(value, "model_dump_json"):
        return value.model_dump_json()  # type: ignore[no-any-return]
    return str(value)


def _parse_llm_outputs(text: str, output_names: list[str]) -> dict[str, Any]:
    """Map LLM ``text`` to the declared ``output_names``.

    Tries three strategies:
      1. If the response contains a JSON block whose top-level keys match the
         declared outputs, split the JSON into per-output values.
      2. If only one output is declared, assign the full text.
      3. Otherwise put the full text in the first output and empty strings in
         the rest (legacy behaviour, kept as a safety net for non-JSON skills).
    """
    import json
    import re

    if not output_names:
        return {}

    # Strategy 1: extract a fenced JSON block or the first top-level JSON object.
    candidate: str | None = None
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        candidate = fence.group(1)
    else:
        brace = re.search(r"\{.*\}", text, re.DOTALL)
        if brace:
            candidate = brace.group(0)
    if candidate is not None:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict):
            mapped: dict[str, Any] = {}
            for name in output_names:
                if name in parsed:
                    mapped[name] = parsed[name]
                else:
                    mapped[name] = ""
            # Treat as a successful split only if at least one declared output
            # appeared in the JSON; otherwise fall through to legacy behaviour.
            if any(mapped[n] != "" for n in output_names):
                return mapped

    # Strategy 2/3: single output gets full text; multi-output keeps legacy
    # behaviour of putting full text in the first slot.
    outputs: dict[str, Any] = {output_names[0]: text}
    for extra in output_names[1:]:
        outputs[extra] = ""
    return outputs


__all__ = ["StageRunner"]
