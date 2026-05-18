"""Parsing helpers for ``requires_external`` blocks declared in SKILL.md.

Skills expose their requirements either as a structured attribute on the
loaded skill (preferred) or via a frontmatter dict. This module normalises
both into a list of :class:`ExternalRequirement` records.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from kernel.contracts.interfaces import ISkill


@dataclass(frozen=True, slots=True)
class ExternalRequirement:
    """Single executable preflight check declared in SKILL.md."""

    command: str
    install_hint: str = ""
    required_when: str | None = None


def requirements_from_skill(skill: ISkill) -> list[ExternalRequirement]:
    """Return requirements declared by a loaded skill.

    Looks at the (optional) ``preflight`` attribute on the skill instance for
    a list of dicts or :class:`ExternalRequirement` entries.
    """
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
    out: list[ExternalRequirement] = []
    servers: Any = requires.get("mcp_servers", []) or []
    if isinstance(servers, list):
        for server in servers:
            if not isinstance(server, dict):
                continue
            entries: Any = server.get("requires_external", []) or []
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if isinstance(entry, dict):
                    out.append(_coerce(entry))
    return out


def _coerce(entry: Any) -> ExternalRequirement:
    if isinstance(entry, ExternalRequirement):
        return entry
    if isinstance(entry, dict):
        return ExternalRequirement(
            command=str(entry.get("command", "")),
            install_hint=str(entry.get("install_hint", "")),
            required_when=entry.get("required_when"),
        )
    return ExternalRequirement(command=str(entry))


__all__ = [
    "ExternalRequirement",
    "requirements_from_frontmatter",
    "requirements_from_skill",
]
