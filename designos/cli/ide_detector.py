"""Detect which AI-powered IDE the user is running in."""

from __future__ import annotations

import os
import shutil
from enum import Enum
from pathlib import Path


class IDE(str, Enum):
    """Supported IDE identifiers."""

    CLAUDE_CODE = "claude-code"
    CURSOR = "cursor"
    TRAE = "trae"
    CODEX = "codex"
    WORKBUDDY = "workbuddy"
    CODEBUDDY = "codebuddy"
    VSCODE = "vscode"
    UNKNOWN = "unknown"


# Mapping: env-var name -> IDE enum value
_ENV_HINTS: dict[str, IDE] = {
    "CLAUDE_CODE_ENTRYPOINT": IDE.CLAUDE_CODE,
    "CURSOR_TRACE_ID": IDE.CURSOR,
    "CURSOR": IDE.CURSOR,
    "TRAE_IDE": IDE.TRAE,
    "CODEX_CLI": IDE.CODEX,
    "WORKBUDDY_ENV": IDE.WORKBUDDY,
    "CODEBUDDY_ENV": IDE.CODEBUDDY,
}

# Mapping: binary name on PATH -> IDE enum value
_BIN_HINTS: dict[str, IDE] = {
    "claude": IDE.CLAUDE_CODE,
    "cursor": IDE.CURSOR,
    "trae": IDE.TRAE,
    "codex": IDE.CODEX,
}


def detect_ide() -> IDE:
    """Detect the current IDE by environment variables or PATH binaries.

    Detection order:
    1. Environment variables (most reliable, set by IDE processes)
    2. PATH commands (fallback heuristic)

    Returns IDE.UNKNOWN if none match.
    """
    # 1. Check environment variables
    for env_var, ide in _ENV_HINTS.items():
        if os.environ.get(env_var):
            return ide

    # 2. Check for known binaries on PATH
    for binary, ide in _BIN_HINTS.items():
        if shutil.which(binary) is not None:
            return ide

    return IDE.UNKNOWN


def ide_config_path(ide: IDE, project_dir: Path) -> dict[str, Path]:
    """Return paths where DesignOS should write IDE-specific configs.

    Args:
        ide: Detected IDE enum value.
        project_dir: Root directory of the target project.

    Returns:
        Mapping of config-name to file/directory path.
    """
    project_dir = project_dir.resolve()

    if ide == IDE.CLAUDE_CODE:
        return {
            "agents": project_dir / "AGENTS.md",
            "commands": project_dir / ".claude" / "commands",
        }
    elif ide == IDE.CURSOR:
        return {
            "rules": project_dir / ".cursor" / "rules",
            "cursorrules": project_dir / ".cursorrules",
        }
    elif ide == IDE.TRAE:
        return {
            "agents": project_dir / "AGENTS.md",
        }
    elif ide == IDE.CODEX:
        return {
            "agents": project_dir / "AGENTS.md",
        }
    elif ide == IDE.WORKBUDDY:
        return {
            "agents": project_dir / "AGENTS.md",
        }
    elif ide == IDE.CODEBUDDY:
        return {
            "agents": project_dir / "AGENTS.md",
        }
    else:
        # VSCODE / UNKNOWN fallback
        return {
            "agents": project_dir / "AGENTS.md",
        }
