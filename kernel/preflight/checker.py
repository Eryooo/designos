"""Preflight checker reading SKILL.md ``requires_external`` declarations."""

from __future__ import annotations

import asyncio
import shlex
from pathlib import Path
from typing import Any

from kernel.contracts.interfaces import IPreflightChecker, ISkill
from kernel.contracts.schemas import MCPServerConfig, SkillContext
from kernel.trace import get_logger

from .requirements import ExternalRequirement, requirements_from_skill

_log = get_logger("kernel.preflight.checker")
_PROBE_TIMEOUT_S: float = 5.0


class PreflightChecker(IPreflightChecker):
    """Runs ``requires_external`` probes declared by the active skill."""

    def __init__(self, *, repo_root: Path | None = None) -> None:
        self._repo_root = repo_root

    async def check(self, skill: ISkill, ctx: SkillContext) -> list[str]:
        """Return human-readable errors; an empty list means OK."""
        errors: list[str] = []
        for server in _declared_servers(skill):
            if not _condition_satisfied(server.required_when, ctx):
                continue
            if not _server_available(server, self._repo_root):
                errors.append(_format_server_error(server, self._repo_root))

        requirements: list[ExternalRequirement] = requirements_from_skill(skill)
        for req in requirements:
            if not _condition_satisfied(req.required_when, ctx):
                continue
            ok: bool = await _probe(req, self._repo_root)
            if not ok:
                if req.server_name == "image-analyzer" and _client_description_fallback_available(ctx):
                    continue
                errors.append(_format_error(req, self._repo_root))
        return errors


def _condition_satisfied(expr: str | None, ctx: SkillContext) -> bool:
    if expr is None:
        return True
    # Limited DSL: ``mode == "<value>"`` (matches the SKILL.md spec).
    expr_clean: str = expr.strip()
    if "==" in expr_clean:
        left, _, right = expr_clean.partition("==")
        if left.strip() == "mode":
            wanted: str = right.strip().strip("'\"")
            return ctx.mode == wanted
    _log.warning("preflight.unknown_condition", expr=expr)
    return True


def _declared_servers(skill: ISkill) -> list[MCPServerConfig]:
    config: Any = getattr(skill, "config", None)
    if config is None:
        return []
    servers: Any = getattr(config, "mcp_servers", None)
    if not isinstance(servers, list):
        return []
    return [server for server in servers if isinstance(server, MCPServerConfig)]


def _server_available(server: MCPServerConfig, repo_root: Path | None) -> bool:
    if server.builtin and repo_root is not None:
        return (repo_root / "mcp-servers" / server.name / "core.py").exists()
    return True


async def _probe(req: ExternalRequirement, repo_root: Path | None) -> bool:
    cmd_parts: list[str] = shlex.split(_expand_command(req.command, repo_root))
    if not cmd_parts:
        return True
    try:
        proc: asyncio.subprocess.Process = await asyncio.create_subprocess_exec(
            *cmd_parts,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
    except (OSError, FileNotFoundError):
        return False
    try:
        rc: int = await asyncio.wait_for(proc.wait(), timeout=_PROBE_TIMEOUT_S)
    except TimeoutError:
        proc.kill()
        return False
    return rc == 0


def _format_error(req: ExternalRequirement, repo_root: Path | None) -> str:
    base: str = f"preflight failed: `{_expand_command(req.command, repo_root)}`"
    if req.install_hint:
        return f"{base}; hint: {req.install_hint}"
    return base


def _expand_command(command: str, repo_root: Path | None) -> str:
    if repo_root is None:
        return command
    return command.replace("{repo_root}", str(repo_root))


def _client_description_fallback_available(ctx: SkillContext) -> bool:
    if ctx.mode != "client":
        return False
    workspace = ctx.workspace
    if (workspace / "inputs" / "screens-description.md").exists():
        return True
    screens_dir = workspace / "inputs" / "screens"
    if not screens_dir.exists():
        return False
    return any(path.suffix.lower() == ".md" for path in screens_dir.rglob("*.md"))


def _format_server_error(server: MCPServerConfig, repo_root: Path | None) -> str:
    if server.builtin and repo_root is not None:
        expected = repo_root / "mcp-servers" / server.name / "core.py"
        return f"preflight failed: builtin MCP server `{server.name}` missing at `{expected}`"
    return f"preflight failed: MCP server `{server.name}` is not available"


def attempt_dict_probe(payload: dict[str, Any]) -> dict[str, Any]:
    """Helper used by tests to inspect the parsed structure."""
    return dict(payload)


__all__ = ["PreflightChecker"]
