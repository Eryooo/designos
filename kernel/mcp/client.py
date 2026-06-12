"""Unified MCP client dispatching to per-server transports."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from kernel.contracts.enums import ErrorCode, MCPTransport
from kernel.contracts.interfaces import IMCPClient
from kernel.contracts.schemas import MCPServerConfig, ToolResult
from kernel.errors import MCPError
from kernel.trace import get_logger

from .inprocess_transport import InProcessTransport
from .registry import MCPRegistry
from .sse_transport import SSETransport
from .stdio_transport import StdioTransport

_log = get_logger("kernel.mcp.client")


class MCPClient(IMCPClient):
    """Routes ``call_tool`` to the transport configured for each server."""

    def __init__(self, registry: MCPRegistry, *, repo_root: Path | None = None) -> None:
        self._registry: MCPRegistry = registry
        self._repo_root: Path | None = repo_root
        self._transports: dict[str, StdioTransport | SSETransport | InProcessTransport] = {}

    async def call_tool(
        self,
        server: str,
        tool: str,
        args: dict[str, Any],
    ) -> ToolResult:
        config: MCPServerConfig = self._registry.get(server)
        transport = self._transport_for(config)
        _log.info("mcp.call", server=server, tool=tool)
        return await transport.call(tool, args)

    def _transport_for(
        self, config: MCPServerConfig
    ) -> StdioTransport | SSETransport | InProcessTransport:
        if config.name in self._transports:
            return self._transports[config.name]
        # M1 shortcut: builtin servers without an explicit ``command`` use the
        # in-process transport that imports their ``core.py`` directly.
        if config.builtin and not config.command and self._repo_root is not None:
            transport: StdioTransport | SSETransport | InProcessTransport = InProcessTransport(
                config, repo_root=self._repo_root
            )
        elif config.transport is MCPTransport.STDIO:
            transport = StdioTransport(config)
        elif config.transport is MCPTransport.SSE:
            transport = SSETransport(config)
        else:  # pragma: no cover - exhaustive enum
            raise MCPError(
                ErrorCode.E3001,
                f"unsupported transport: {config.transport}",
                context={"server": config.name},
            )
        self._transports[config.name] = transport
        return transport

    async def close(self) -> None:
        """Tear down all open transports."""
        for transport in self._transports.values():
            await transport.close()
        self._transports.clear()


__all__ = ["MCPClient"]
