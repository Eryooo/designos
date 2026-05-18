"""DesignOS CLI — real command implementations (M1 A6).

Commands are organised into three layers:
  - Top-level: init, run, resume, config, history, preflight, version
  - ``input`` sub-group: check, scaffold
  - ``skill`` sub-group: list, versions
  - ``mcp`` sub-group: install (stub)
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Optional

import typer

from designos import __version__

# ---------------------------------------------------------------------------
# App + sub-app wiring
# ---------------------------------------------------------------------------

app: typer.Typer = typer.Typer(
    help="DesignOS — AI-native design capability suite.",
    no_args_is_help=True,
    add_completion=False,
)

input_app: typer.Typer = typer.Typer(
    help="Manage skill inputs for the current workspace.",
    no_args_is_help=True,
)
app.add_typer(input_app, name="input")

skill_app: typer.Typer = typer.Typer(
    help="Inspect installed skills.",
    no_args_is_help=True,
)
app.add_typer(skill_app, name="skill")

mcp_app: typer.Typer = typer.Typer(
    help="Manage MCP server integrations.",
    no_args_is_help=True,
)
app.add_typer(mcp_app, name="mcp")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_DESIGNOS_HOME: Path = Path.home() / ".designos"
_GLOBAL_SKILLS_DIR: Path = _DESIGNOS_HOME / "skills"
_LOCAL_SKILLS_DIR: Path = Path(".claude") / "skills"


def _skill_search_paths() -> list[Path]:
    """Return skill search paths: global then project-local."""
    paths: list[Path] = [_GLOBAL_SKILLS_DIR]
    local = Path.cwd() / _LOCAL_SKILLS_DIR
    if local.exists():
        paths.append(local)
    # Also check a top-level skills/ dir in the repo (dev convenience).
    repo_skills = Path.cwd() / "skills"
    if repo_skills.exists():
        paths.append(repo_skills)
    return paths


def _load_workspace_inputs(ws_root: Path) -> dict[str, Any]:
    """Read every file under ``<workspace>/inputs/`` into a state dict.

    Mapping convention (state key ← file basename):
      - ``prd.md``  → keys ``prd_text``, ``prd_file`` (file path), ``prd``
      - ``scope.md`` → keys ``scope_md``, ``scope``
      - ``screens-description.md`` → ``screens_description``, ``screenshots``
      - ``raw_issues.json`` → ``raw_issues`` (parsed as list/dict)
      - other ``.md`` → key = file stem with ``-`` → ``_``
      - other ``.json`` → key = file stem, parsed
      - other ``.txt`` / ``.yaml`` → key = file stem, raw text

    Always sets ``screenshots_dir`` to ``inputs/`` for skills that need it.
    """
    inputs_dir = ws_root / "inputs"
    state: dict[str, Any] = {"screenshots_dir": inputs_dir}
    if not inputs_dir.is_dir():
        return state
    for f in sorted(inputs_dir.iterdir()):
        if not f.is_file() or f.name.startswith("."):
            continue
        stem_key = f.stem.replace("-", "_")
        suffix = f.suffix.lower()
        try:
            if suffix == ".json":
                state[stem_key] = json.loads(f.read_text(encoding="utf-8"))
            else:
                state[stem_key] = f.read_text(encoding="utf-8")
        except Exception:
            state[stem_key] = f.read_text(encoding="utf-8", errors="ignore")
        # Common aliases used by uxeval skill.
        if f.name == "prd.md":
            state["prd_text"] = state[stem_key]
            state["prd_file"] = str(f)
        if f.name == "scope.md":
            state["scope_md"] = state[stem_key]
        if f.name == "screens-description.md":
            state["screens_description"] = state[stem_key]
            state.setdefault("screenshots", state[stem_key])
    return state


def _find_workspace() -> Path | None:
    """Walk up from cwd looking for designos.project.yaml."""
    cur = Path.cwd()
    for candidate in [cur, *cur.parents]:
        if (candidate / "designos.project.yaml").exists():
            return candidate
    return None


def _err(msg: str) -> None:
    typer.echo(typer.style(f"Error: {msg}", fg=typer.colors.RED), err=True)


def _ok(msg: str) -> None:
    typer.echo(typer.style(msg, fg=typer.colors.GREEN))


def _info(msg: str) -> None:
    typer.echo(msg)


# ---------------------------------------------------------------------------
# version
# ---------------------------------------------------------------------------


@app.command()
def version() -> None:
    """Print DesignOS version."""
    typer.echo(f"DesignOS {__version__}")


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------


@app.command()
def init(
    name: str = typer.Argument(..., help="Project name for the new workspace."),
    skill: Optional[str] = typer.Option(None, "--skill", "-s", help="Skill to associate with this workspace."),
    force: bool = typer.Option(False, "--force", "-f", help="Re-initialise an existing workspace."),
) -> None:
    """Create a new DesignOS workspace in ./<name>."""
    from kernel.contracts.errors import DesignOSError
    from kernel.workspace.initializer import WorkspaceInitializer

    target = Path.cwd() / name
    try:
        ws = WorkspaceInitializer().initialize(target, name=name, skill=skill, force=force)
        _ok(f"Workspace '{name}' created at {ws.root}")
        if skill:
            _info(f"  Skill: {skill}")
        _info("  Run `designos run <skill>` to execute a skill.")
    except DesignOSError as exc:
        _err(str(exc))
        raise typer.Exit(1) from exc


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------


@app.command()
def run(
    skill: str = typer.Argument(..., help="Skill name to execute."),
    mode: Optional[str] = typer.Option(None, "--mode", "-m", help="Execution mode (e.g. web, client)."),
    auto_confirm: bool = typer.Option(False, "--auto-confirm", help="Skip checkpoint confirmation prompts."),
    run_id: Optional[str] = typer.Option(None, "--run-id", help="Explicit run id (auto-assigned if omitted)."),
) -> None:
    """Execute a Skill against the current workspace."""
    from kernel.config.loader import load_config
    from kernel.contracts.errors import DesignOSError
    from kernel.contracts.schemas import SkillContext
    from kernel.llm.client import LLMClient
    from kernel.pipeline.engine import make_engine
    from kernel.skill_loader.loader import SkillLoader
    from kernel.workspace.run_manager import RunManager
    from kernel.workspace.workspace import Workspace

    ws_root = _find_workspace()
    if ws_root is None:
        _err("No DesignOS workspace found. Run `designos init <name>` first.")
        raise typer.Exit(1)

    try:
        ws = Workspace(ws_root)
        loader = SkillLoader(_skill_search_paths())
        loaded_skill = loader.load(skill)

        rm = RunManager(ws)
        resolved_run_id = run_id or rm.allocate(skill)
        rm.run_dir(resolved_run_id, create=True)

        cfg = load_config(workspace=ws_root)

        initial_state: dict[str, Any] = _load_workspace_inputs(ws_root)

        ctx = SkillContext(
            run_id=resolved_run_id,
            workspace=ws_root,
            skill_name=skill,
            skill_version=getattr(loaded_skill, "version", "0.0.0"),
            mode=mode,  # type: ignore[arg-type]
            config=cfg,
            state=initial_state,
        )

        llm_client = LLMClient.from_global_config(cfg.global_config)
        engine = make_engine(workspace=ws, llm=llm_client)

        _info(f"Running skill '{skill}' (run_id={resolved_run_id}) …")

        async def _drive_once() -> bool:
            """Drive engine.execute once, returning True if a checkpoint paused the run."""
            paused = False
            async for event in engine.execute(loaded_skill, ctx):  # type: ignore[arg-type]
                kind: str = event.kind
                stage: str = event.stage_id
                if kind == "stage_started":
                    _info(f"  → {stage}")
                elif kind == "stage_completed":
                    _info(typer.style(f"  ✓ {stage}", fg=typer.colors.GREEN))
                elif kind == "stage_failed":
                    _err(f"  ✗ {stage} failed")
                elif kind == "checkpoint":
                    msg: str = event.payload.get("message", "Checkpoint reached.")
                    _info(typer.style(f"\nCheckpoint: {msg}", fg=typer.colors.YELLOW))
                    if not auto_confirm:
                        typer.confirm("Continue?", default=True, abort=True)
                    paused = True
            return paused

        async def _drive() -> None:
            # With ``--auto-confirm``, automatically resume past every checkpoint.
            while True:
                paused = await _drive_once()
                if not paused or not auto_confirm:
                    break

        asyncio.run(_drive())
        _ok("Run complete.")
    except DesignOSError as exc:
        _err(str(exc))
        raise typer.Exit(1) from exc


# ---------------------------------------------------------------------------
# resume
# ---------------------------------------------------------------------------


@app.command()
def resume(
    run_id: Optional[str] = typer.Option(None, "--run-id", help="Run id to resume (latest paused run if omitted)."),
) -> None:
    """Resume a paused Skill run from the latest checkpoint."""
    from kernel.contracts.errors import DesignOSError
    from kernel.checkpoint.manager import CheckpointManager
    from kernel.workspace.workspace import Workspace

    ws_root = _find_workspace()
    if ws_root is None:
        _err("No DesignOS workspace found.")
        raise typer.Exit(1)

    try:
        ws = Workspace(ws_root)
        cm = CheckpointManager(ws_root)

        # Resolve run_id: use provided or find the most recent checkpoint file.
        resolved: str | None = run_id
        if resolved is None:
            checkpoints_dir = ws.checkpoints_dir
            if checkpoints_dir.exists():
                files = sorted(checkpoints_dir.glob("session-*.yaml"), key=lambda p: p.stat().st_mtime, reverse=True)
                if files:
                    # Extract run_id from filename: session-<run_id>.yaml
                    resolved = files[0].stem[len("session-"):]

        if resolved is None:
            _err("No paused run found. Start a run with `designos run <skill>` first.")
            raise typer.Exit(1)

        snap = cm.load(resolved)
        if snap is None:
            _err(f"No checkpoint found for run '{resolved}'.")
            raise typer.Exit(1)

        _info(f"Resuming run '{resolved}' (skill={snap.skill}, stage={snap.current_stage_index}) …")
        _info("Use `designos run <skill> --run-id <id>` to re-execute from the checkpoint.")
    except DesignOSError as exc:
        _err(str(exc))
        raise typer.Exit(1) from exc


# ---------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------

_MODEL_CHOICES: list[str] = [
    "claude-opus-4-5",
    "claude-sonnet-4-5",
    "claude-haiku-3-5",
    "gpt-4o",
    "deepseek-chat",
]


@app.command()
def config() -> None:
    """Interactive configuration wizard: choose model and set API key."""
    _info(typer.style("DesignOS Configuration Wizard", bold=True))
    _info("Settings are written to ~/.designos/.env.local\n")

    # Model selection
    _info("Available models:")
    for i, m in enumerate(_MODEL_CHOICES, 1):
        _info(f"  {i}. {m}")
    choice_str: str = typer.prompt("Select model (number or name)", default="2")
    if choice_str.isdigit():
        idx = int(choice_str) - 1
        model = _MODEL_CHOICES[idx] if 0 <= idx < len(_MODEL_CHOICES) else choice_str
    else:
        model = choice_str

    # API key
    api_key: str = typer.prompt("Anthropic API key", hide_input=True, default="")

    # Write to ~/.designos/.env.local
    _DESIGNOS_HOME.mkdir(parents=True, exist_ok=True)
    env_path = _DESIGNOS_HOME / ".env.local"
    lines: list[str] = []
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()

    def _set_env(key: str, value: str) -> None:
        prefix = f"{key}="
        updated = False
        for i, line in enumerate(lines):
            if line.startswith(prefix):
                lines[i] = f"{prefix}{value}"
                updated = True
                break
        if not updated:
            lines.append(f"{prefix}{value}")

    _set_env("DESIGNOS_MODEL", model)
    if api_key:
        _set_env("ANTHROPIC_API_KEY", api_key)

    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    _ok(f"\nConfiguration saved to {env_path}")
    _info(f"  Model: {model}")
    if api_key:
        _info(f"  API key: {'*' * (len(api_key) - 4)}{api_key[-4:]}")


# ---------------------------------------------------------------------------
# history
# ---------------------------------------------------------------------------


@app.command()
def history() -> None:
    """List historical Skill runs in the current workspace."""
    ws_root = _find_workspace()
    if ws_root is None:
        _err("No DesignOS workspace found.")
        raise typer.Exit(1)

    runs_dir = ws_root / "runs"
    if not runs_dir.exists():
        _info("No runs yet.")
        return

    entries = sorted(
        [e for e in runs_dir.iterdir() if e.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not entries:
        _info("No runs yet.")
        return

    import yaml

    _info(typer.style(f"{'RUN ID':<30} {'SKILL':<20} {'STATUS':<12} STARTED", bold=True))
    _info("-" * 80)
    for entry in entries:
        manifest_path = entry / "run.yaml"
        if manifest_path.exists():
            try:
                data: dict = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
                run_id_col = data.get("id", entry.name)
                skill_col = data.get("skill", "-")
                status_col = data.get("status", "-")
                started_col = str(data.get("started_at", "-"))[:19]
                _info(f"{run_id_col:<30} {skill_col:<20} {status_col:<12} {started_col}")
            except Exception:
                _info(f"{entry.name:<30} {'?':<20} {'?':<12} ?")
        else:
            _info(f"{entry.name:<30} {'?':<20} {'?':<12} ?")


# ---------------------------------------------------------------------------
# preflight
# ---------------------------------------------------------------------------


@app.command()
def preflight(
    skill: str = typer.Argument(..., help="Skill name to check."),
    mode: Optional[str] = typer.Option(None, "--mode", "-m", help="Execution mode for conditional checks."),
) -> None:
    """Run preflight checks for a Skill without executing it."""
    from kernel.config.loader import load_config
    from kernel.contracts.errors import DesignOSError
    from kernel.contracts.schemas import SkillContext
    from kernel.preflight.checker import PreflightChecker
    from kernel.skill_loader.loader import SkillLoader

    ws_root = _find_workspace() or Path.cwd()

    try:
        loader = SkillLoader(_skill_search_paths())
        loaded_skill = loader.load(skill)
        cfg = load_config(workspace=ws_root)
        ctx = SkillContext(
            run_id="preflight",
            workspace=ws_root,
            skill_name=skill,
            skill_version=getattr(loaded_skill, "version", "0.0.0"),
            mode=mode,  # type: ignore[arg-type]
            config=cfg,
            state={},
        )
        checker = PreflightChecker()
        errors: list[str] = asyncio.run(checker.check(loaded_skill, ctx))
        if errors:
            _err(f"Preflight failed for '{skill}':")
            for e in errors:
                typer.echo(f"  • {e}", err=True)
            raise typer.Exit(1)
        _ok(f"Preflight passed for '{skill}'.")
    except DesignOSError as exc:
        _err(str(exc))
        raise typer.Exit(1) from exc


# ---------------------------------------------------------------------------
# input sub-commands
# ---------------------------------------------------------------------------


@input_app.command("check")
def input_check() -> None:
    """Check whether the current workspace inputs satisfy the active Skill's INPUT.md."""
    ws_root = _find_workspace()
    if ws_root is None:
        _err("No DesignOS workspace found.")
        raise typer.Exit(1)

    # Determine active skill from project yaml.
    import yaml

    project_yaml = ws_root / "designos.project.yaml"
    if not project_yaml.exists():
        _err("designos.project.yaml not found.")
        raise typer.Exit(1)

    data: dict = yaml.safe_load(project_yaml.read_text(encoding="utf-8")) or {}
    skills: dict = data.get("skills", {})
    if not skills:
        _err("No skill configured in this workspace. Run `designos init <name> --skill <skill>`.")
        raise typer.Exit(1)

    skill_name = next(iter(skills))
    inputs_dir = ws_root / "inputs"

    # Find INPUT.md for the skill.
    input_md: Path | None = None
    for search_root in _skill_search_paths():
        candidate = search_root / skill_name / "INPUT.md"
        if candidate.exists():
            input_md = candidate
            break

    if input_md is None:
        _info(f"No INPUT.md found for skill '{skill_name}'. Skipping requirement check.")
        return

    requirements = input_md.read_text(encoding="utf-8")
    _info(f"INPUT.md requirements for '{skill_name}':\n")
    _info(requirements)

    if not inputs_dir.exists() or not any(inputs_dir.iterdir()):
        _err("inputs/ directory is empty. Run `designos input scaffold <skill>` to create templates.")
        raise typer.Exit(1)

    _ok("inputs/ directory is non-empty. Manual review against INPUT.md recommended.")


@input_app.command("scaffold")
def input_scaffold(
    skill: str = typer.Argument(..., help="Skill name whose templates to copy."),
) -> None:
    """Copy a Skill's input templates into the current workspace inputs/ directory."""
    import shutil

    ws_root = _find_workspace()
    if ws_root is None:
        _err("No DesignOS workspace found.")
        raise typer.Exit(1)

    templates_dir: Path | None = None
    for search_root in _skill_search_paths():
        candidate = search_root / skill / "templates"
        if candidate.exists():
            templates_dir = candidate
            break

    if templates_dir is None:
        _err(f"No templates/ directory found for skill '{skill}'.")
        raise typer.Exit(1)

    inputs_dir = ws_root / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    for src in templates_dir.iterdir():
        dst = inputs_dir / src.name
        if dst.exists():
            _info(f"  skip (exists): {src.name}")
            continue
        if src.is_file():
            shutil.copy2(src, dst)
        else:
            shutil.copytree(src, dst)
        _info(f"  copied: {src.name}")
        copied += 1

    if copied == 0:
        _info("All templates already present in inputs/.")
    else:
        _ok(f"Scaffolded {copied} template(s) into {inputs_dir}")


# ---------------------------------------------------------------------------
# skill sub-commands
# ---------------------------------------------------------------------------


@skill_app.command("list")
def skill_list() -> None:
    """List all installed Skills (global ~/.designos/skills/ and project .claude/skills/)."""
    from kernel.skill_loader.loader import SkillLoader

    loader = SkillLoader(_skill_search_paths())
    skills = loader.list_available()
    if not skills:
        _info("No skills installed.")
        _info("Install skills to ~/.designos/skills/ or .claude/skills/")
        return

    _info(typer.style(f"{'SKILL':<30} LOCATION", bold=True))
    _info("-" * 60)
    for name in skills:
        location = "-"
        for search_root in _skill_search_paths():
            candidate = search_root / name
            if (candidate / "SKILL.md").exists() or (candidate / "GROUP.md").exists():
                location = str(candidate)
                break
        _info(f"{name:<30} {location}")


@skill_app.command("versions")
def skill_versions(
    skill: str = typer.Argument(..., help="Skill name to inspect."),
) -> None:
    """List available prompt versions for a Skill (prompts/ subdirectories)."""
    skill_dir: Path | None = None
    for search_root in _skill_search_paths():
        candidate = search_root / skill
        if (candidate / "SKILL.md").exists() or (candidate / "GROUP.md").exists():
            skill_dir = candidate
            break

    if skill_dir is None:
        _err(f"Skill '{skill}' not found.")
        raise typer.Exit(1)

    prompts_dir = skill_dir / "prompts"
    if not prompts_dir.exists():
        _info(f"No prompts/ directory found for skill '{skill}'.")
        return

    versions = sorted([d.name for d in prompts_dir.iterdir() if d.is_dir()])
    if not versions:
        _info(f"No version directories found in {prompts_dir}")
        return

    _info(typer.style(f"Versions for '{skill}':", bold=True))
    for v in versions:
        _info(f"  {v}")


# ---------------------------------------------------------------------------
# mcp sub-commands (stub)
# ---------------------------------------------------------------------------


@mcp_app.command("install")
def mcp_install(
    name: str = typer.Argument(..., help="MCP server name to install."),
) -> None:
    """Install an MCP server integration (stub — M2)."""
    _info(f"TODO: mcp install {name}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":  # pragma: no cover
    app()
