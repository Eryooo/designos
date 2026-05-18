"""Multi-layer configuration loader.

Merge order (highest priority first):

    1. CLI overrides (dict passed in)
    2. ``designos.project.yaml`` (workspace root)
    3. ``~/.designos/config.yaml`` (user-level)
    4. ``.env.local`` (workspace-local secrets)
    5. ``SkillConfig`` defaults
    6. ``GlobalConfig`` defaults (Kernel built-ins)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from kernel.contracts.enums import ErrorCode
from kernel.contracts.schemas import (
    DesignOSConfig,
    GlobalConfig,
    MCPServerConfig,
    ProjectConfig,
    SkillConfig,
)
from kernel.errors import ConfigError

from .env_loader import apply_to_environ, load_env_file


def load_config(
    *,
    workspace: Path,
    cli_overrides: dict[str, Any] | None = None,
    user_config_path: Path | None = None,
    skill_config: SkillConfig | None = None,
) -> DesignOSConfig:
    """Resolve the final :class:`DesignOSConfig` for a run.

    Args:
        workspace: Absolute path to the active workspace.
        cli_overrides: Dict of CLI-supplied overrides (top-priority).
        user_config_path: Override path to user config (defaults to ``~/.designos/config.yaml``).
        skill_config: Active skill metadata, when known.

    Returns:
        Fully merged :class:`DesignOSConfig`.

    Raises:
        ConfigError: When YAML parsing fails or paths are malformed.
    """
    workspace = workspace.expanduser().resolve()
    cli_overrides = cli_overrides or {}

    env_file = workspace / ".env.local"
    apply_to_environ(load_env_file(env_file), override=False)

    global_dict: dict[str, Any] = _read_yaml(_user_config_path(user_config_path))
    global_cfg = GlobalConfig(**global_dict) if global_dict else GlobalConfig()

    project_path = workspace / "designos.project.yaml"
    project_dict: dict[str, Any] = _read_yaml(project_path)
    project_cfg = ProjectConfig(**project_dict) if project_dict else None

    mcp_servers: dict[str, MCPServerConfig] = {}
    if skill_config is not None:
        for srv in skill_config.mcp_servers:
            mcp_servers[srv.name] = srv

    env_snapshot: dict[str, str] = {
        k: v for k, v in os.environ.items() if k.startswith("DESIGNOS_") or k in _ALLOWLIST_ENV
    }

    merged: dict[str, Any] = {
        "workspace": workspace,
        "global_config": global_cfg,
        "project_config": project_cfg,
        "skill_config": skill_config,
        "mcp_servers": mcp_servers,
        "env": env_snapshot,
    }
    merged.update(cli_overrides)
    return DesignOSConfig(**merged)


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        loaded: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(
            ErrorCode.E1001,
            f"invalid YAML at {path}: {exc}",
            context={"path": str(path)},
        ) from exc
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise ConfigError(
            ErrorCode.E1001,
            f"expected mapping in {path}, got {type(loaded).__name__}",
            context={"path": str(path)},
        )
    return dict(loaded)  # type: ignore[arg-type]


def _user_config_path(override: Path | None) -> Path:
    if override is not None:
        return override
    return Path.home() / ".designos" / "config.yaml"


_ALLOWLIST_ENV: set[str] = {
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_BASE_URL",
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "DEEPSEEK_API_KEY",
    "DEEPSEEK_BASE_URL",
}


__all__ = ["load_config"]
