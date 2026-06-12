"""Preflight: validate external dependencies declared in SKILL.md."""

from __future__ import annotations

from .checker import PreflightChecker
from .requirements import (
    ExternalRequirement,
    requirements_from_frontmatter,
    requirements_from_skill,
)

__all__ = [
    "ExternalRequirement",
    "PreflightChecker",
    "requirements_from_frontmatter",
    "requirements_from_skill",
]
