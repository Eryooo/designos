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
from typing import Any, Optional, cast

import typer
import yaml

from designos import __version__
from kernel.contracts.enums import Mode, RunStatus
from kernel.contracts.schemas import OutputManifest, RunManifest, SkillResult

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
    """Return skill search paths with the current project taking precedence."""
    paths: list[Path] = []
    local = Path.cwd() / _LOCAL_SKILLS_DIR
    if local.exists():
        paths.append(local)
    # Also check a top-level skills/ dir in the repo (dev convenience).
    repo_skills = Path.cwd() / "skills"
    if repo_skills.exists():
        paths.append(repo_skills)
    # Walk up from cwd to find a sibling `skills/` (dev convenience).
    for parent in Path.cwd().parents:
        candidate = parent / "skills"
        if candidate.is_dir() and (parent / "kernel").exists():
            if candidate not in paths:
                paths.append(candidate)
            break
    if _GLOBAL_SKILLS_DIR not in paths:
        paths.append(_GLOBAL_SKILLS_DIR)
    return paths


def _detect_repo_root() -> Path | None:
    """Locate the DesignOS repo root (the dir containing ``mcp-servers/``)."""
    # Walk up from this file's location.
    here = Path(__file__).resolve()
    for ancestor in (here, *here.parents):
        if (ancestor / "mcp-servers").is_dir() and (ancestor / "kernel").is_dir():
            return ancestor
    # Fallback: cwd ancestors.
    cwd = Path.cwd().resolve()
    for ancestor in (cwd, *cwd.parents):
        if (ancestor / "mcp-servers").is_dir() and (ancestor / "kernel").is_dir():
            return ancestor
    return None


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


def _manifest_outputs(result: SkillResult) -> list[OutputManifest]:
    return [
        OutputManifest(
            id=artifact.id,
            type=artifact.output_type,
            path=artifact.path,
            format=artifact.format,
            summary=artifact.summary,
        )
        for artifact in result.artifacts
    ]


def _exit_code_for_status(status: RunStatus) -> int:
    if status is RunStatus.COMPLETED:
        return 0
    if status is RunStatus.PAUSED:
        return 2
    return 1


def _find_workspace() -> Path | None:
    """Walk up from cwd looking for designos.project.yaml."""
    cur = Path.cwd()
    for candidate in [cur, *cur.parents]:
        if (candidate / "designos.project.yaml").exists():
            return candidate
    return None


def _load_run_manifest(ws_root: Path, run_id: str) -> RunManifest:
    from kernel.contracts.enums import ErrorCode
    from kernel.errors import WorkspaceError

    manifest_path = ws_root / "runs" / run_id / "run.yaml"
    if not manifest_path.exists():
        raise WorkspaceError(
            ErrorCode.E4001,
            f"run manifest not found: {manifest_path}",
            context={"run_id": run_id, "path": str(manifest_path)},
        )
    try:
        loaded: Any = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise WorkspaceError(
            ErrorCode.E4001,
            f"invalid run manifest: {manifest_path}",
            context={"run_id": run_id, "path": str(manifest_path)},
        ) from exc
    if not isinstance(loaded, dict):
        raise WorkspaceError(
            ErrorCode.E4001,
            f"run manifest is not a mapping: {manifest_path}",
            context={"run_id": run_id, "path": str(manifest_path)},
        )
    try:
        return RunManifest.model_validate(loaded)
    except Exception as exc:
        raise WorkspaceError(
            ErrorCode.E4001,
            f"run manifest failed validation: {manifest_path}",
            context={"run_id": run_id, "path": str(manifest_path)},
        ) from exc


def _latest_paused_run_id(ws_root: Path) -> str | None:
    from kernel.checkpoint.manager import CheckpointManager

    runs_dir = ws_root / "runs"
    if not runs_dir.exists():
        return None

    cm = CheckpointManager(ws_root)
    paused: list[tuple[RunManifest, Any]] = []
    for entry in runs_dir.iterdir():
        if not entry.is_dir():
            continue
        manifest_path = entry / "run.yaml"
        if not manifest_path.exists():
            continue
        try:
            manifest = _load_run_manifest(ws_root, entry.name)
        except Exception:
            continue
        if manifest.status is not RunStatus.PAUSED:
            continue
        try:
            snapshot = cm.load(manifest.id)
        except Exception:
            continue
        if snapshot is None:
            continue
        paused.append((manifest, snapshot))

    if not paused:
        return None

    paused.sort(
        key=lambda item: item[1].last_updated,
        reverse=True,
    )
    return paused[0][0].id


def _prepare_skill_runtime(
    *,
    ws_root: Path,
    skill: str,
    run_id: str,
    mode: str | None,
    skill_version: str | None = None,
    model: str | None = None,
) -> tuple[Any, Any, Any]:
    from kernel.config.loader import load_config
    from kernel.contracts.schemas import SkillContext
    from kernel.llm.client import LLMClient
    from kernel.mcp.client import MCPClient
    from kernel.mcp.registry import MCPRegistry
    from kernel.pipeline.engine import make_engine
    from kernel.skill_loader.loader import SkillLoader
    from kernel.workspace.workspace import Workspace

    ws = Workspace(ws_root)
    loader = SkillLoader(_skill_search_paths())
    loaded_skill = loader.load(skill)
    cfg = load_config(workspace=ws_root, skill_config=loaded_skill.config)  # type: ignore[attr-defined]
    if model is not None:
        cfg = cfg.model_copy(
            update={
                "global_config": cfg.global_config.model_copy(update={"primary_model": model}),
            }
        )

    ctx = SkillContext(
        run_id=run_id,
        workspace=ws_root,
        skill_name=skill,
        skill_version=skill_version or getattr(loaded_skill, "version", "0.0.0"),
        mode=mode,  # type: ignore[arg-type]
        config=cfg,
        state=_load_workspace_inputs(ws_root),
    )

    llm_client = LLMClient.from_global_config(cfg.global_config)
    repo_root = _detect_repo_root()
    registry = MCPRegistry(cfg.mcp_servers)
    mcp_client = MCPClient(registry, repo_root=repo_root) if repo_root else None
    engine = make_engine(workspace=ws, llm=llm_client, mcp=mcp_client)
    attach = getattr(loaded_skill, "attach", None)
    if callable(attach):
        attach(engine=engine, llm=llm_client, mcp=mcp_client)
    return loaded_skill, ctx, cfg


def _drive_skill(loaded_skill: Any, ctx: Any, *, auto_confirm: bool) -> SkillResult:
    async def _drive() -> SkillResult:
        result: SkillResult
        while True:
            result = await loaded_skill.run(ctx)  # type: ignore[func-returns-value]
            if result.status is not RunStatus.PAUSED or not auto_confirm:
                return result
            if result.pause_kind != "checkpoint":
                return result

    return asyncio.run(_drive())


def _write_terminal_manifest(rm: Any, manifest: RunManifest, result: SkillResult) -> RunManifest:
    final_manifest = rm.finish_manifest(
        manifest,
        status=result.status,
        outputs=_manifest_outputs(result),
        status_reason=result.status_reason,
        required_actions=result.required_actions,
    )
    rm.write_manifest(final_manifest)
    return final_manifest


def _emit_terminal_status(result: SkillResult) -> None:
    if result.status is RunStatus.COMPLETED:
        _ok("Run complete.")
    elif result.status is RunStatus.PAUSED:
        checkpoint = result.paused_at_checkpoint or "checkpoint"
        _info(typer.style(f"Run paused at {checkpoint}.", fg=typer.colors.YELLOW))
        if result.status_reason:
            _info(f"Reason: {result.status_reason}")
        for action in result.required_actions:
            _info(f"Required action: {action}")
    else:
        _err("Run failed.")
        if result.status_reason:
            _info(f"Reason: {result.status_reason}")


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
    name: Optional[str] = typer.Argument(None, help="Project name. Omit for global install."),
    skill: Optional[str] = typer.Option(None, "--skill", "-s", help="Skill to associate with this workspace."),
    force: bool = typer.Option(False, "--force", "-f", help="Re-run setup even if already configured."),
) -> None:
    """Initialize DesignOS.

    Without arguments: runs global setup (detect IDE, configure API key, install IDE configs).
    With <name>: creates a project workspace in ./<name>.
    """
    if name is None:
        # Global install mode
        from designos.cli.installer import run_global_install

        run_global_install(force=force)
        return

    # Project workspace mode (existing logic)
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
    from kernel.contracts.errors import DesignOSError
    from kernel.workspace.run_manager import RunManager
    from kernel.workspace.workspace import Workspace

    ws_root = _find_workspace()
    if ws_root is None:
        _err("No DesignOS workspace found. Run `designos init <name>` first.")
        raise typer.Exit(1)

    manifest: RunManifest | None = None
    rm: RunManager | None = None
    try:
        ws = Workspace(ws_root)
        rm = RunManager(ws)
        resolved_run_id = run_id or rm.allocate(skill)
        rm.run_dir(resolved_run_id, create=True)

        loaded_skill, ctx, cfg = _prepare_skill_runtime(
            ws_root=ws_root,
            skill=skill,
            run_id=resolved_run_id,
            mode=mode,
        )

        manifest = rm.start_manifest(
            resolved_run_id,
            skill,
            getattr(loaded_skill, "version", "0.0.0"),
            cfg.global_config.primary_model,
            mode=cast(Mode | None, mode),
        )
        rm.write_manifest(manifest)

        _info(f"Running skill '{skill}' (run_id={resolved_run_id}) …")
        result = _drive_skill(loaded_skill, ctx, auto_confirm=auto_confirm)
        _write_terminal_manifest(rm, manifest, result)
        _emit_terminal_status(result)
        raise typer.Exit(_exit_code_for_status(result.status))
    except DesignOSError as exc:
        if manifest is not None and rm is not None:
            failed_manifest = rm.finish_manifest(manifest, status=RunStatus.FAILED)
            rm.write_manifest(failed_manifest)
        _err(str(exc))
        raise typer.Exit(1) from exc


# ---------------------------------------------------------------------------
# resume
# ---------------------------------------------------------------------------


@app.command()
def resume(
    run_id: Optional[str] = typer.Option(None, "--run-id", help="Run id to resume (latest paused run if omitted)."),
    auto_confirm: bool = typer.Option(False, "--auto-confirm", help="Skip checkpoint confirmation prompts."),
) -> None:
    """Resume a paused Skill run from the latest checkpoint."""
    from kernel.checkpoint.manager import CheckpointManager
    from kernel.contracts.enums import ErrorCode
    from kernel.contracts.errors import DesignOSError
    from kernel.errors import WorkspaceError
    from kernel.workspace.run_manager import RunManager
    from kernel.workspace.workspace import Workspace

    ws_root = _find_workspace()
    if ws_root is None:
        _err("No DesignOS workspace found.")
        raise typer.Exit(1)

    manifest: RunManifest | None = None
    rm: RunManager | None = None
    try:
        ws = Workspace(ws_root)
        rm = RunManager(ws)
        cm = CheckpointManager(ws_root)

        resolved = run_id or _latest_paused_run_id(ws_root)
        if resolved is None:
            raise WorkspaceError(
                ErrorCode.E4001,
                "No paused run found. Start a run with `designos run <skill>` first.",
            )

        manifest = _load_run_manifest(ws_root, resolved)
        if manifest.status is not RunStatus.PAUSED:
            raise WorkspaceError(
                ErrorCode.E4001,
                f"run '{resolved}' is not paused",
                context={"run_id": resolved, "status": manifest.status.value},
            )

        snap = cm.load(resolved)
        if snap is None:
            raise WorkspaceError(
                ErrorCode.E4001,
                f"No checkpoint found for run '{resolved}'.",
                context={"run_id": resolved},
            )
        if snap.skill != manifest.skill:
            raise WorkspaceError(
                ErrorCode.E4001,
                f"checkpoint skill mismatch for run '{resolved}'",
                context={"run_id": resolved, "snapshot_skill": snap.skill, "manifest_skill": manifest.skill},
            )

        loaded_skill, ctx, _cfg = _prepare_skill_runtime(
            ws_root=ws_root,
            skill=manifest.skill,
            run_id=resolved,
            mode=manifest.mode,
            skill_version=manifest.version,
            model=manifest.model,
        )

        manifest = rm.resume_manifest(manifest)
        rm.write_manifest(manifest)
        _info(f"Resuming run '{resolved}' (skill={snap.skill}, stage={snap.current_stage_index}) …")
        result = _drive_skill(loaded_skill, ctx, auto_confirm=auto_confirm)
        _write_terminal_manifest(rm, manifest, result)
        _emit_terminal_status(result)
        raise typer.Exit(_exit_code_for_status(result.status))
    except DesignOSError as exc:
        if manifest is not None and rm is not None and manifest.status is RunStatus.RUNNING:
            failed_manifest = rm.finish_manifest(manifest, status=RunStatus.FAILED)
            rm.write_manifest(failed_manifest)
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

    manifests: list[RunManifest] = []
    for entry in entries:
        manifest_path = entry / "run.yaml"
        if not manifest_path.exists():
            continue
        try:
            data: dict[str, Any] = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
            manifests.append(RunManifest.model_validate(data))
        except Exception:
            continue

    if not manifests:
        _info("No runs yet.")
        return

    _info(typer.style(f"{'RUN ID':<30} {'SKILL':<20} {'STATUS':<12} STARTED", bold=True))
    _info("-" * 80)
    for manifest in manifests:
        started_col = str(manifest.started_at)[:19]
        _info(f"{manifest.id:<30} {manifest.skill:<20} {manifest.status.value:<12} {started_col}")


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
        cfg = load_config(workspace=ws_root, skill_config=loaded_skill.config)  # type: ignore[attr-defined]
        ctx = SkillContext(
            run_id="preflight",
            workspace=ws_root,
            skill_name=skill,
            skill_version=getattr(loaded_skill, "version", "0.0.0"),
            mode=mode,  # type: ignore[arg-type]
            config=cfg,
            state={},
        )
        checker = PreflightChecker(repo_root=_detect_repo_root())
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

    data: dict[str, Any] = yaml.safe_load(project_yaml.read_text(encoding="utf-8")) or {}
    skills: dict[str, Any] = data.get("skills", {})
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
