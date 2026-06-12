"""In-process MCP transport for builtin servers.

Bypasses subprocess + JSON-RPC for builtin MCP servers in the same repo by
directly importing their ``core.py`` and calling the exposed function.

This is an M1 pragmatic shortcut so end-to-end Skill runs work without each
MCP server being packaged as a separate executable. M2 will replace this with
real stdio + JSON-RPC once each MCP server has its own entry point.
"""

from __future__ import annotations

import importlib.util
import sys
import time
from pathlib import Path
from typing import Any, Callable

from kernel.contracts.enums import ErrorCode
from kernel.contracts.schemas import ErrorInfo, MCPServerConfig, ToolResult
from kernel.errors import MCPError
from kernel.trace import get_logger

_log = get_logger("kernel.mcp.inprocess")


def _drop_none_recursive(value: Any) -> Any:
    """Recursively strip None values so frozen Pydantic models with str defaults
    don't reject upstream None placeholders. Lists/dicts are walked in-place.
    """
    if isinstance(value, dict):
        return {k: _drop_none_recursive(v) for k, v in value.items() if v is not None}
    if isinstance(value, list):
        return [_drop_none_recursive(v) for v in value]
    return value


_ARG_ALIASES: dict[str, str] = {
    # Pipeline state name → tool argument name. Lets skills export richer
    # state keys (e.g. ``task_checklist_lite``) while tools accept a single
    # canonical name (``task_checklist``).
    "screens_description": "screenshots_description",
    "prd_text": "prd",
}


class InProcessTransport:
    """Direct-import transport for builtin MCP servers."""

    def __init__(self, server: MCPServerConfig, *, repo_root: Path) -> None:
        self._server: MCPServerConfig = server
        self._repo_root: Path = repo_root
        self._tool_fns: dict[str, Callable[..., Any]] = {}
        self._loaded: bool = False

    async def call(self, tool: str, args: dict[str, Any]) -> ToolResult:
        """Invoke a tool by directly importing the MCP server's core module."""
        if not self._loaded:
            self._load()
        fn: Callable[..., Any] | None = self._tool_fns.get(tool)
        if fn is None:
            raise MCPError(
                ErrorCode.E3001,
                f"tool {tool} not found in {self._server.name}",
                context={"server": self._server.name, "available": sorted(self._tool_fns)},
            )
        # Apply pipeline → tool argument aliases.
        aliased: dict[str, Any] = {_ARG_ALIASES.get(k, k): v for k, v in args.items()}
        started: float = time.monotonic()
        try:
            coerced = self._coerce_args(fn, aliased)
            result: Any = fn(**coerced)
        except TypeError as exc:
            raise MCPError(
                ErrorCode.E3003,
                f"tool {self._server.name}.{tool} call failed: {exc}",
                context={"server": self._server.name, "tool": tool, "args": list(args)},
            ) from exc
        except Exception as exc:
            duration_ms: int = int((time.monotonic() - started) * 1000)
            return ToolResult(
                server=self._server.name,
                tool=tool,
                ok=False,
                data={},
                error=ErrorInfo(
                    code=ErrorCode.E3003,
                    message=str(exc),
                    context={"server": self._server.name, "tool": tool},
                ),
                duration_ms=duration_ms,
            )
        duration_ms = int((time.monotonic() - started) * 1000)
        data: dict[str, Any] = self._normalise_result(result)
        return ToolResult(
            server=self._server.name,
            tool=tool,
            ok=True,
            data=data,
            error=None,
            duration_ms=duration_ms,
        )

    def _load(self) -> None:
        server_dir: Path = self._repo_root / "mcp-servers" / self._server.name
        core_path: Path = server_dir / "core.py"
        if not core_path.exists():
            raise MCPError(
                ErrorCode.E3001,
                f"builtin MCP server {self._server.name} has no core.py",
                context={"path": str(core_path)},
            )
        # Each server has its own ``core``/``schemas`` modules; isolate to avoid clobbering
        # one another in ``sys.modules``.
        mod_name: str = f"_designos_mcp_{self._server.name.replace('-', '_')}"
        spec = importlib.util.spec_from_file_location(mod_name, core_path)
        if spec is None or spec.loader is None:
            raise MCPError(
                ErrorCode.E3001,
                f"could not load {self._server.name}/core.py",
                context={"path": str(core_path)},
            )
        # Make schemas.py importable from inside core.py.
        old_path = list(sys.path)
        sys.path.insert(0, str(server_dir))
        # Evict potentially stale sibling modules so the right schemas/core are used.
        for stale in ("schemas", "core"):
            sys.modules.pop(stale, None)
        try:
            module = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = module
            spec.loader.exec_module(module)
        finally:
            sys.path[:] = old_path
        # Discover candidate tool functions: any module-level callable whose name
        # is a public identifier and isn't a class.
        self._tool_fns = {
            name: obj
            for name, obj in vars(module).items()
            if callable(obj) and not name.startswith("_") and not isinstance(obj, type)
        }
        self._loaded = True
        _log.debug(
            "mcp.inprocess.loaded",
            server=self._server.name,
            tools=sorted(self._tool_fns),
        )

    @staticmethod
    def _coerce_args(fn: Callable[..., Any], args: dict[str, Any]) -> dict[str, Any]:
        """Filter / coerce args to match the function signature.

        Three cases handled:
          1. ``**kwargs`` → pass everything.
          2. Single positional Pydantic-Model parameter → wrap ``args`` into
             that model so callers can pass a flat dict.
          3. Otherwise filter to declared parameter names and convert ``str``
             values to ``Path`` when annotated as such.
        """
        import inspect
        import typing

        try:
            sig = inspect.signature(fn)
        except (TypeError, ValueError):
            return args

        # Resolve string annotations (from __future__ import annotations).
        try:
            hints = typing.get_type_hints(fn)
        except Exception:
            hints = {}

        params = list(sig.parameters.values())

        # Case 1: **kwargs
        for p in params:
            if p.kind is inspect.Parameter.VAR_KEYWORD:
                return args

        # Case 2: a single required positional whose annotation is a Pydantic
        # model. We allow other parameters as long as they have defaults
        # (e.g. ``judge: LLMJudge | None = None``).
        required_positional = [
            p
            for p in params
            if p.kind
            in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            and p.default is inspect.Parameter.empty
        ]
        if len(required_positional) == 1:
            ann: Any = hints.get(required_positional[0].name, required_positional[0].annotation)
            if hasattr(ann, "model_validate"):
                cleaned = _drop_none_recursive(args)
                try:
                    return {required_positional[0].name: ann.model_validate(cleaned)}
                except Exception as exc:
                    _log.warning(
                        "mcp.inprocess.model_validate_failed",
                        target=getattr(ann, "__name__", str(ann)),
                        error=str(exc)[:300],
                    )
                    # fall through to filter mode

        # Case 3: filter to accepted names + path coercion
        accepted: set[str] = {p.name for p in params}
        out: dict[str, Any] = {}
        for k, v in args.items():
            if k not in accepted:
                continue
            ann = hints.get(k, sig.parameters[k].annotation)
            if ann is Path and isinstance(v, str):
                out[k] = Path(v)
            else:
                out[k] = v
        return out

    @staticmethod
    def _normalise_result(result: Any) -> dict[str, Any]:
        """Convert function return value into a flat dict for ToolResult.data.

        Stage runner will look up output names directly against this dict, so
        Pydantic models / dicts are flattened to top-level keys (with the raw
        ``structuredContent`` mirror retained for MCP compatibility).
        """
        if hasattr(result, "model_dump"):
            dumped = result.model_dump()
            return {**dumped, "structuredContent": dumped}
        if isinstance(result, dict):
            return {**result, "structuredContent": result}
        if isinstance(result, list):
            return {"items": result, "structuredContent": {"items": result}}
        return {"value": result, "structuredContent": {"value": result}}

    async def close(self) -> None:
        """No-op; in-process transport has no resources to release."""
        return


__all__ = ["InProcessTransport"]
