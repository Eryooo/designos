"""Stdio JSON-RPC transport for MCP servers.

Spawns the MCP server as a subprocess and exchanges JSON-RPC 2.0 messages over
its stdin/stdout. Implements just enough of the MCP protocol for ``call_tool``
in M1 — initialize handshake + ``tools/call``. SSE is deferred.
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any

from kernel.contracts.enums import ErrorCode
from kernel.contracts.schemas import ErrorInfo, MCPServerConfig, ToolResult
from kernel.errors import MCPError
from kernel.trace import get_logger

_log = get_logger("kernel.mcp.stdio")
_DEFAULT_TIMEOUT_S: float = 30.0


class StdioTransport:
    """Subprocess-based JSON-RPC client for an MCP server."""

    def __init__(self, server: MCPServerConfig, *, timeout_s: float = _DEFAULT_TIMEOUT_S) -> None:
        self._server: MCPServerConfig = server
        self._timeout_s: float = timeout_s
        self._proc: asyncio.subprocess.Process | None = None
        self._next_id: int = 0
        self._lock: asyncio.Lock = asyncio.Lock()

    async def _ensure_started(self) -> asyncio.subprocess.Process:
        if self._proc is not None and self._proc.returncode is None:
            return self._proc
        if not self._server.command:
            raise MCPError(
                ErrorCode.E3001,
                f"MCP server {self._server.name} has no stdio command",
                context={"server": self._server.name},
            )
        try:
            self._proc = await asyncio.create_subprocess_exec(
                *self._server.command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=None if not self._server.env else _merged_env(self._server.env),
            )
        except (OSError, FileNotFoundError) as exc:
            raise MCPError(
                ErrorCode.E3001,
                f"failed to spawn MCP server {self._server.name}: {exc}",
                context={"server": self._server.name},
            ) from exc
        await self._initialize()
        return self._proc

    async def _initialize(self) -> None:
        await self._send_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "designos-kernel", "version": "0.1.0"},
            },
        )
        await self._send_notification("notifications/initialized", {})

    async def call(self, tool: str, args: dict[str, Any]) -> ToolResult:
        """Invoke a tool and return a normalised :class:`ToolResult`."""
        async with self._lock:
            await self._ensure_started()
            started: float = time.monotonic()
            try:
                response: dict[str, Any] = await asyncio.wait_for(
                    self._send_request("tools/call", {"name": tool, "arguments": args}),
                    timeout=self._timeout_s,
                )
            except TimeoutError as exc:
                raise MCPError(
                    ErrorCode.E3002,
                    f"MCP tool {self._server.name}.{tool} timed out after {self._timeout_s}s",
                    context={"server": self._server.name, "tool": tool},
                ) from exc
            duration_ms: int = int((time.monotonic() - started) * 1000)
            return _to_tool_result(self._server.name, tool, response, duration_ms)

    async def _send_request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        proc: asyncio.subprocess.Process = await self._ensure_started()
        self._next_id += 1
        rpc_id: int = self._next_id
        message: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "method": method,
            "params": params,
        }
        assert proc.stdin is not None and proc.stdout is not None
        proc.stdin.write((json.dumps(message) + "\n").encode("utf-8"))
        await proc.stdin.drain()

        while True:
            raw: bytes = await proc.stdout.readline()
            if not raw:
                raise MCPError(
                    ErrorCode.E3003,
                    f"MCP server {self._server.name} closed unexpectedly",
                    context={"server": self._server.name, "method": method},
                )
            try:
                payload: dict[str, Any] = json.loads(raw.decode("utf-8").strip())
            except json.JSONDecodeError:
                _log.debug("mcp.stdio.skip_non_json", line=raw[:200])
                continue
            if payload.get("id") != rpc_id:
                continue
            if "error" in payload:
                err: dict[str, Any] = payload["error"]
                raise MCPError(
                    ErrorCode.E3003,
                    f"MCP {method} failed: {err.get('message', 'unknown')}",
                    context={"server": self._server.name, "method": method, "rpc_error": err},
                )
            return payload

    async def _send_notification(self, method: str, params: dict[str, Any]) -> None:
        proc: asyncio.subprocess.Process = await self._ensure_started()
        assert proc.stdin is not None
        message: dict[str, Any] = {"jsonrpc": "2.0", "method": method, "params": params}
        proc.stdin.write((json.dumps(message) + "\n").encode("utf-8"))
        await proc.stdin.drain()

    async def close(self) -> None:
        """Terminate the subprocess if still running."""
        if self._proc is None or self._proc.returncode is not None:
            return
        try:
            self._proc.terminate()
            await asyncio.wait_for(self._proc.wait(), timeout=2.0)
        except (TimeoutError, ProcessLookupError):
            self._proc.kill()


def _to_tool_result(
    server: str, tool: str, response: dict[str, Any], duration_ms: int
) -> ToolResult:
    result: dict[str, Any] = response.get("result", {}) or {}
    is_error: bool = bool(result.get("isError"))
    data: dict[str, Any] = {"content": result.get("content", [])}
    if "structuredContent" in result:
        data["structuredContent"] = result["structuredContent"]
    error: ErrorInfo | None = None
    if is_error:
        error = ErrorInfo(
            code=ErrorCode.E3003,
            message=str(result.get("content", "tool reported error")),
            context={"server": server, "tool": tool},
        )
    return ToolResult(
        server=server,
        tool=tool,
        ok=not is_error,
        data=data,
        error=error,
        duration_ms=duration_ms,
    )


def _merged_env(extra: dict[str, str]) -> dict[str, str]:
    import os

    env: dict[str, str] = dict(os.environ)
    env.update(extra)
    return env


__all__ = ["StdioTransport"]
