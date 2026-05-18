"""MCP server registry.

Resolves logical server names to :class:`MCPServerConfig` entries supplied
by the active :class:`SkillConfig`. The registry is intentionally minimal
in M1 — auto-discovery from ``mcp-servers/*/SKILL.md`` is deferred.
"""

from __future__ import annotations

from kernel.contracts.enums import ErrorCode
from kernel.contracts.schemas import MCPServerConfig, SkillConfig
from kernel.errors import MCPError


class MCPRegistry:
    """In-memory registry of MCP server configurations."""

    def __init__(self, servers: dict[str, MCPServerConfig] | None = None) -> None:
        self._servers: dict[str, MCPServerConfig] = dict(servers or {})

    @classmethod
    def from_skill_config(cls, skill: SkillConfig) -> MCPRegistry:
        """Build a registry from the MCP servers declared by a skill."""
        return cls({srv.name: srv for srv in skill.mcp_servers})

    def register(self, server: MCPServerConfig) -> None:
        """Add or overwrite an entry."""
        self._servers[server.name] = server

    def get(self, name: str) -> MCPServerConfig:
        """Return the config for ``name`` or raise :class:`MCPError`."""
        try:
            return self._servers[name]
        except KeyError as exc:
            raise MCPError(
                ErrorCode.E3001,
                f"MCP server not registered: {name}",
                context={"name": name, "known": sorted(self._servers)},
            ) from exc

    def names(self) -> list[str]:
        """Return registered server names sorted alphabetically."""
        return sorted(self._servers)


__all__ = ["MCPRegistry"]
