"""Minimal ``.env`` style file reader, no third-party dependency.

Supports:
- ``KEY=value``
- ``KEY="value with spaces"``
- single quotes
- ``export KEY=value`` prefix
- comments starting with ``#``
- blank lines
"""

from __future__ import annotations

import os
from pathlib import Path

from kernel.contracts.enums import ErrorCode
from kernel.errors import ConfigError


def load_env_file(path: Path) -> dict[str, str]:
    """Parse a dotenv file into a flat dict.

    Args:
        path: Path to ``.env.local`` or similar.

    Returns:
        Dict of variables; empty dict if the file does not exist.

    Raises:
        ConfigError: When a line cannot be parsed.
    """
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line: str = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].lstrip()
        if "=" not in line:
            raise ConfigError(
                ErrorCode.E1001,
                f"invalid env line: {raw_line!r}",
                context={"path": str(path)},
            )
        key, _, value = line.partition("=")
        key = key.strip()
        value = _strip_inline_comment(value.strip())
        value = _unquote(value)
        if not key:
            raise ConfigError(
                ErrorCode.E1001,
                f"empty key in env line: {raw_line!r}",
                context={"path": str(path)},
            )
        out[key] = value
    return out


def apply_to_environ(values: dict[str, str], *, override: bool = False) -> None:
    """Merge a dict of values into ``os.environ``.

    Args:
        values: Variables to apply.
        override: When True, overwrite existing env vars.
    """
    for key, value in values.items():
        if override or key not in os.environ:
            os.environ[key] = value


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _strip_inline_comment(value: str) -> str:
    # Only strip ``#`` outside quotes; cheap heuristic, avoids ``URL#frag`` corner cases.
    if value.startswith(('"', "'")):
        return value
    idx: int = value.find(" #")
    if idx >= 0:
        return value[:idx].rstrip()
    return value


__all__ = ["apply_to_environ", "load_env_file"]
