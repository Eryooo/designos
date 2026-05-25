"""Parsing helpers for ``requires_external`` blocks declared in SKILL.md.

Skills expose their requirements either as a structured attribute on the
loaded skill (preferred) or via a frontmatter dict. This module normalises
both into a list of :class:`ExternalRequirement` records.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from kernel.contracts.interfaces import ISkill
from kernel.contracts.schemas import MCPServerConfig


@dataclass(frozen=True, slots=True)
class ExternalRequirement:
    """Single executable preflight check declared in SKILL.md."""

    command: str
    install_hint: str = ""
    required_when: str | None = None
    server_name: str | None = None


def requirements_from_skill(skill: ISkill) -> list[ExternalRequirement]:
    """Return requirements declared by a loaded skill.

    Primary source is ``skill.config.mcp_servers[*].requires_external`` so the
    runtime consumes parsed SKILL.md frontmatter. The legacy ``skill.preflight``
    attribute is still accepted as a compatibility fallback.
    """
    config: Any = getattr(skill, "config", None)
    if config is not None:
        servers: Any = getattr(config, "mcp_servers", None)
        if isinstance(servers, list):
            parsed = _requirements_from_servers(servers)
            if parsed:
                return parsed

    raw: Any = getattr(skill, "preflight", None)
    if raw is None:
        return []
    if isinstance(raw, list):
        return [_coerce(entry) for entry in raw]  # type: ignore[arg-type]
    return []


def requirements_from_frontmatter(frontmatter: dict[str, Any]) -> list[ExternalRequirement]:
    """Extract requirements from raw SKILL.md frontmatter."""
    requires: Any = frontmatter.get("requires", {}) or {}
    if not isinstance(requires, dict):
        return []
    servers: Any = requires.get("mcp_servers", []) or []
    if not isinstance(servers, list):
        return []
    parsed_servers: list[MCPServerConfig] = []
    for server in servers:
        if not isinstance(server, dict):
            continue
        if not server.get("name"):
            continue
        parsed_servers.append(MCPServerConfig.model_validate(server))
    return _requirements_from_servers(parsed_servers)


def _requirements_from_servers(servers: list[MCPServerConfig]) -> list[ExternalRequirement]:
    out: list[ExternalRequirement] = []
    for server in servers:
        for entry in server.requires_external:
            out.append(
                ExternalRequirement(
                    command=entry.command,
                    install_hint=entry.install_hint,
                    required_when=entry.required_when or server.required_when,
                    server_name=server.name,
                )
            )
    return out


def _coerce(entry: Any) -> ExternalRequirement:
    if isinstance(entry, ExternalRequirement):
        return entry
    if isinstance(entry, dict):
        return ExternalRequirement(
            command=str(entry.get("command", "")),
            install_hint=str(entry.get("install_hint", "")),
            required_when=entry.get("required_when"),
            server_name=entry.get("server_name"),
        )
    return ExternalRequirement(command=str(entry))


__all__ = [
    "ExternalRequirement",
    "requirements_from_frontmatter",
    "requirements_from_skill",
]
