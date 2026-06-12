"""Helpers for parsing SKILL.md / GROUP.md frontmatter blocks.

The frontmatter is YAML delimited by ``---`` lines at the top of the file.
We parse with ``yaml.safe_load`` and return a plain dict — no Pydantic
validation happens here so we can flag schema issues with rich messages.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from kernel.contracts.enums import ErrorCode
from kernel.errors import ConfigError


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    """Return ``(frontmatter_dict, body)`` for a Markdown file.

    Args:
        path: Path to ``SKILL.md`` / ``GROUP.md``.

    Raises:
        ConfigError: When the file is missing or has no frontmatter block.
    """
    if not path.exists():
        raise ConfigError(
            ErrorCode.E1001,
            f"missing skill manifest: {path}",
            context={"path": str(path)},
        )
    text: str = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ConfigError(
            ErrorCode.E1001,
            f"skill manifest is missing YAML frontmatter: {path}",
            context={"path": str(path)},
        )
    parts: list[str] = text.split("---", 2)
    if len(parts) < 3:
        raise ConfigError(
            ErrorCode.E1001,
            f"unterminated frontmatter in {path}",
            context={"path": str(path)},
        )
    raw_yaml: str = parts[1]
    body: str = parts[2].lstrip("\n")
    try:
        loaded: Any = yaml.safe_load(raw_yaml)
    except yaml.YAMLError as exc:
        raise ConfigError(
            ErrorCode.E1001,
            f"invalid frontmatter YAML: {exc}",
            context={"path": str(path)},
        ) from exc
    if not isinstance(loaded, dict):
        raise ConfigError(
            ErrorCode.E1001,
            f"frontmatter must be a mapping: {path}",
            context={"path": str(path)},
        )
    return dict(loaded), body  # type: ignore[arg-type]


__all__ = ["parse_frontmatter"]
