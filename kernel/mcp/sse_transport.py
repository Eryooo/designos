"""SSE-mode MCP transport (M1 stub).

The full SSE client is deferred to M2; the stub raises
:class:`MCPError` so skills relying on SSE fail loud rather than hang.
"""

from __future__ import annotations

from typing import Any

from kernel.contracts.enums import ErrorCode
from kernel.contracts.schemas import MCPServerConfig, ToolResult
from kernel.errors import MCPError


class SSETransport:
    """Placeholder SSE transport — raises on every call."""

    def __init__(self, server: MCPServerConfig) -> None:
        self._server: MCPServerConfig = server

    async def call(self, tool: str, args: dict[str, Any]) -> ToolResult:
        """Raise :class:`MCPError` — SSE transport not implemented in M1."""
        raise MCPError(
            ErrorCode.E3001,
            "SSE transport is not implemented in M1",
            context={"server": self._server.name, "tool": tool, "args_keys": sorted(args)},
        )

    async def close(self) -> None:  # pragma: no cover - no resources held
        """No-op — provided for protocol parity with stdio."""
        return None


__all__ = ["SSETransport"]
