"""Preflight checker reading SKILL.md ``requires_external`` declarations."""

from __future__ import annotations

import asyncio
import shlex
from typing import Any

from kernel.contracts.interfaces import IPreflightChecker, ISkill
from kernel.contracts.schemas import SkillContext
from kernel.trace import get_logger

from .requirements import ExternalRequirement, requirements_from_skill

_log = get_logger("kernel.preflight.checker")
_PROBE_TIMEOUT_S: float = 5.0


class PreflightChecker(IPreflightChecker):
    """Runs ``requires_external`` probes declared by the active skill."""

    async def check(self, skill: ISkill, ctx: SkillContext) -> list[str]:
        """Return human-readable errors; an empty list means OK."""
        requirements: list[ExternalRequirement] = requirements_from_skill(skill)
        errors: list[str] = []
        for req in requirements:
            if not _condition_satisfied(req.required_when, ctx):
                continue
            ok: bool = await _probe(req)
            if not ok:
                errors.append(_format_error(req))
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


async def _probe(req: ExternalRequirement) -> bool:
    cmd_parts: list[str] = shlex.split(req.command)
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


def _format_error(req: ExternalRequirement) -> str:
    base: str = f"preflight failed: `{req.command}`"
    if req.install_hint:
        return f"{base}; hint: {req.install_hint}"
    return base


def attempt_dict_probe(payload: dict[str, Any]) -> dict[str, Any]:
    """Helper used by tests to inspect the parsed structure."""
    return dict(payload)


__all__ = ["PreflightChecker"]
