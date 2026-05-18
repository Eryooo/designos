"""Global DesignOS installation: API keys, IDE configs, connectivity check."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import structlog
import typer

from designos.cli.ide_detector import IDE, detect_ide, ide_config_path

_log: structlog.stdlib.BoundLogger = structlog.get_logger("designos.cli.installer")

_DESIGNOS_HOME: Path = Path.home() / ".designos"
_ENV_FILE: Path = _DESIGNOS_HOME / ".env.local"

_DEFAULT_MODEL: str = "claude-opus-4-7"
_API_TIMEOUT_SECONDS: int = 10


def _find_source_repo() -> Path | None:
    """Locate the DesignOS source repository root.

    Checks:
    1. Development mode: relative to this file (../../)
    2. Installed mode: ~/.designos/skills/ parent
    """
    # Dev mode: this file lives at designos/cli/installer.py
    dev_root = Path(__file__).resolve().parents[2]
    if (dev_root / "AGENTS.md").exists() and (dev_root / "kernel").is_dir():
        return dev_root

    # Installed mode fallback
    if (_DESIGNOS_HOME / "skills").is_dir():
        return _DESIGNOS_HOME

    return None


def ask_api_key(existing: str | None = None) -> str:
    """Prompt user for Anthropic API key with hidden input.

    Args:
        existing: Previously stored key (shown masked for confirmation).

    Returns:
        The API key string entered by the user.
    """
    if existing:
        masked = f"{'*' * (len(existing) - 4)}{existing[-4:]}"
        typer.echo(f"  Current key: {masked}")
        if not typer.confirm("  Replace existing key?", default=False):
            return existing

    key: str = typer.prompt(
        "  Anthropic API key (sk-ant-...)",
        hide_input=True,
    )
    if not key.startswith("sk-"):
        typer.echo(
            typer.style(
                "  Warning: key does not start with 'sk-'. "
                "Verify you copied the correct key from console.anthropic.com",
                fg=typer.colors.YELLOW,
            )
        )
    return key


def check_api_connectivity(
    key: str, base_url: str | None = None
) -> tuple[bool, str]:
    """Test Anthropic API connectivity with a minimal request.

    Returns:
        (success, error_message) tuple.
    """
    import httpx

    url = (base_url or "https://api.anthropic.com").rstrip("/")
    endpoint = f"{url}/v1/messages"

    headers: dict[str, str] = {
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload: dict[str, Any] = {
        "model": "claude-haiku-3-5",
        "max_tokens": 1,
        "messages": [{"role": "user", "content": "hi"}],
    }

    try:
        resp = httpx.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=_API_TIMEOUT_SECONDS,
        )
        if resp.status_code in (200, 201):
            return True, ""
        elif resp.status_code == 401:
            return False, "Authentication failed. Check your API key."
        elif resp.status_code == 403:
            return False, "Access denied. Your key may lack permissions."
        else:
            return False, f"HTTP {resp.status_code}: {resp.text[:200]}"
    except httpx.TimeoutException:
        return False, (
            "Connection timed out. Check your network or ANTHROPIC_BASE_URL."
        )
    except httpx.ConnectError as exc:
        return False, f"Connection error: {exc}"
    except Exception as exc:  # noqa: BLE001
        return False, f"Unexpected error: {exc}"


def install_ide_configs(
    ide: IDE, target_dir: Path, source_repo: Path
) -> list[Path]:
    """Copy IDE-specific configs from source repo to target_dir.

    Args:
        ide: Detected IDE.
        target_dir: Where to install configs (usually cwd or project root).
        source_repo: DesignOS repo root containing AGENTS.md etc.

    Returns:
        List of paths written.
    """
    written: list[Path] = []
    paths = ide_config_path(ide, target_dir)
    agents_src = source_repo / "AGENTS.md"

    if "agents" in paths and agents_src.exists():
        dst = paths["agents"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(agents_src, dst)
        written.append(dst)
        _log.info("installed.agents_md", path=str(dst))

    if "commands" in paths:
        cmd_dir = paths["commands"]
        cmd_dir.mkdir(parents=True, exist_ok=True)
        written.append(cmd_dir)
        _log.info("installed.commands_dir", path=str(cmd_dir))

    if "rules" in paths:
        rules_dir = paths["rules"]
        rules_dir.mkdir(parents=True, exist_ok=True)
        # Copy AGENTS.md content as a rule file for Cursor
        if agents_src.exists():
            dst = rules_dir / "designos.md"
            shutil.copy2(agents_src, dst)
            written.append(dst)
        _log.info("installed.cursor_rules", path=str(rules_dir))

    if "cursorrules" in paths:
        if agents_src.exists():
            dst = paths["cursorrules"]
            shutil.copy2(agents_src, dst)
            written.append(dst)
            _log.info("installed.cursorrules", path=str(dst))

    return written


def _read_env_file() -> dict[str, str]:
    """Read existing .env.local into a dict."""
    env: dict[str, str] = {}
    if _ENV_FILE.exists():
        for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def _write_env_file(env: dict[str, str]) -> None:
    """Write env dict back to .env.local."""
    _DESIGNOS_HOME.mkdir(parents=True, exist_ok=True)
    lines = [f"{k}={v}" for k, v in env.items()]
    _ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_global_install(force: bool = False) -> None:
    """Interactive global setup for DesignOS.

    Steps:
    1. Detect IDE
    2. Create ~/.designos/ if needed
    3. Prompt for API key and base URL
    4. Test API connectivity
    5. Install IDE configs
    6. Print success summary
    """
    typer.echo(typer.style("DesignOS Global Setup", bold=True))
    typer.echo("")

    # Step 1: Detect IDE
    ide = detect_ide()
    typer.echo(f"  Detected IDE: {ide.value}")
    _log.info("global_install.ide_detected", ide=ide.value)

    # Step 2: Ensure ~/.designos/ exists
    _DESIGNOS_HOME.mkdir(parents=True, exist_ok=True)

    # Step 3: API key configuration
    typer.echo("")
    typer.echo(typer.style("API Configuration", bold=True))
    env = _read_env_file()
    existing_key = env.get("ANTHROPIC_API_KEY")

    if existing_key and not force:
        masked = f"{'*' * (len(existing_key) - 4)}{existing_key[-4:]}"
        typer.echo(f"  API key already configured: {masked}")
        typer.echo("  Use --force to reconfigure.")
        api_key = existing_key
    else:
        api_key = ask_api_key(existing_key if force else None)

    # Base URL (optional)
    base_url: str = typer.prompt(
        "  Base URL (leave empty for api.anthropic.com)",
        default="",
        show_default=False,
    )

    # Model selection
    model: str = typer.prompt(
        "  Primary model",
        default=_DEFAULT_MODEL,
    )

    # Step 4: Test API connectivity
    typer.echo("")
    typer.echo(typer.style("Testing API connectivity...", bold=True))
    success, err_msg = check_api_connectivity(
        api_key, base_url or None
    )
    if success:
        typer.echo(typer.style("  API connection successful.", fg=typer.colors.GREEN))
    else:
        typer.echo(typer.style(f"  API test failed: {err_msg}", fg=typer.colors.RED))
        typer.echo("  Tip: verify your key at console.anthropic.com")
        if not typer.confirm("  Continue anyway?", default=True):
            raise typer.Exit(1)

    # Save env config
    env["ANTHROPIC_API_KEY"] = api_key
    if base_url:
        env["ANTHROPIC_BASE_URL"] = base_url
    env["DESIGNOS_MODEL"] = model
    _write_env_file(env)
    typer.echo(f"  Config saved to {_ENV_FILE}")

    # Step 5: Install IDE configs
    typer.echo("")
    typer.echo(typer.style("Installing IDE configs...", bold=True))
    source_repo = _find_source_repo()
    if source_repo is None:
        typer.echo(
            typer.style(
                "  Could not locate DesignOS source repo. "
                "Skipping IDE config installation.",
                fg=typer.colors.YELLOW,
            )
        )
    else:
        target_dir = Path.cwd()
        written = install_ide_configs(ide, target_dir, source_repo)
        if written:
            for p in written:
                typer.echo(f"  Installed: {p}")
        else:
            typer.echo("  No IDE configs to install.")

    # Step 6: Success summary
    typer.echo("")
    typer.echo(typer.style("Setup complete!", fg=typer.colors.GREEN, bold=True))
    typer.echo("")
    typer.echo("  Next steps:")
    typer.echo("    1. designos init <project-name>  — create a workspace")
    typer.echo("    2. designos run <skill>          — execute a skill")
    typer.echo("")
    _log.info("global_install.complete", ide=ide.value, model=model)
