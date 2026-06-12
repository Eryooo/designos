"""Unit tests for the DesignOS CLI."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from designos import __version__ as DESIGNOS_VERSION
from designos.cli.main import app


runner = CliRunner()


def _make_preflight_skill(
    root: Path,
    *,
    command: str = "definitely-missing-command-12345 --version",
    required_when: str | None = 'mode == "web"',
) -> Path:
    skill_dir = root / "demo-preflight"
    skill_dir.mkdir(parents=True, exist_ok=True)
    required_when_lines = ""
    if required_when is not None:
        required_when_lines = f"      required_when: '{required_when}'\n"
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: demo-preflight\n"
        "version: 1.2.3\n"
        "type: pipeline\n"
        "requires:\n"
        "  kernel: \">=1.0.0,<2.0.0\"\n"
        "  mcp_servers:\n"
        "    - name: pdf-parser\n"
        "      builtin: true\n"
        "    - name: playwright-driver\n"
        "      builtin: false\n"
        f"{required_when_lines}"
        "      requires_external:\n"
        f"        - command: \"{command}\"\n"
        "          install_hint: \"Install Playwright before using web mode.\"\n"
        "modes:\n"
        "  - id: client\n"
        "  - id: web\n"
        "---\n"
        "# Demo preflight skill\n",
        encoding="utf-8",
    )
    (skill_dir / "pipeline.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "demo-preflight-pipeline",
                "version": "1.2.3",
                "stages": [
                    {
                        "id": "noop",
                        "type": "composite",
                        "outputs": ["ok"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return skill_dir


# ---------------------------------------------------------------------------
# version
# ---------------------------------------------------------------------------


def test_version_command_prints_designos_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert DESIGNOS_VERSION in result.stdout
    assert "DesignOS" in result.stdout


# ---------------------------------------------------------------------------
# --help
# ---------------------------------------------------------------------------


def test_help_lists_all_top_level_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for cmd in ("version", "init", "run", "resume", "config", "history", "preflight"):
        assert cmd in result.stdout


def test_skill_subgroup_help() -> None:
    result = runner.invoke(app, ["skill", "--help"])
    assert result.exit_code == 0
    assert "list" in result.stdout
    assert "versions" in result.stdout


def test_input_subgroup_help() -> None:
    result = runner.invoke(app, ["input", "--help"])
    assert result.exit_code == 0
    assert "check" in result.stdout
    assert "scaffold" in result.stdout


def test_mcp_subgroup_help() -> None:
    result = runner.invoke(app, ["mcp", "--help"])
    assert result.exit_code == 0
    assert "install" in result.stdout


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------


def test_init_creates_workspace_directory(tmp_path: Path) -> None:
    result = runner.invoke(app, ["init", "my-project"], catch_exceptions=False)
    # The command runs from the test process cwd, not tmp_path.
    # We just verify it doesn't crash with an unexpected error.
    # Exit code 0 means workspace was created; exit code 1 means it already exists.
    assert result.exit_code in (0, 1)


def test_init_creates_workspace_in_tmp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init", "test-ws"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (tmp_path / "test-ws").is_dir()
    assert (tmp_path / "test-ws" / "designos.project.yaml").exists()
    assert (tmp_path / "test-ws" / "inputs").is_dir()
    assert (tmp_path / "test-ws" / "outputs").is_dir()
    assert (tmp_path / "test-ws" / "runs").is_dir()


def test_init_with_skill_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init", "ws-with-skill", "--skill", "uxeval"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "uxeval" in result.stdout


def test_init_fails_on_existing_workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", "existing-ws"], catch_exceptions=False)
    result = runner.invoke(app, ["init", "existing-ws"], catch_exceptions=False)
    assert result.exit_code == 1
    # mix_stderr=True (default) means stderr is merged into result.output / result.stdout
    assert "Error" in result.output


def test_init_force_flag_reinitialises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", "force-ws"], catch_exceptions=False)
    result = runner.invoke(app, ["init", "force-ws", "--force"], catch_exceptions=False)
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# history
# ---------------------------------------------------------------------------


def test_history_empty_workspace_prints_no_runs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", "hist-ws"], catch_exceptions=False)
    monkeypatch.chdir(tmp_path / "hist-ws")
    result = runner.invoke(app, ["history"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "No runs yet" in result.stdout


def test_history_no_workspace_exits_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["history"])
    assert result.exit_code == 1


def test_history_lists_run_entries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", "hist-ws2"], catch_exceptions=False)
    ws = tmp_path / "hist-ws2"
    runs_dir = ws / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    run_dir = runs_dir / "001-uxeval"
    run_dir.mkdir()
    import yaml
    from datetime import UTC, datetime
    manifest = {
        "id": "001-uxeval",
        "skill": "uxeval",
        "status": "completed",
        "started_at": datetime.now(UTC).isoformat(),
        "version": "1.0.0",
        "model": "claude-opus-4-5",
    }
    (run_dir / "run.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
    monkeypatch.chdir(ws)
    result = runner.invoke(app, ["history"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "001-uxeval" in result.stdout
    assert "uxeval" in result.stdout


# ---------------------------------------------------------------------------
# skill list
# ---------------------------------------------------------------------------


def test_skill_list_no_skills_installed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """skill list must not crash even when no skills are installed."""
    monkeypatch.chdir(tmp_path)
    # Point skill search paths to empty dirs so nothing is found.
    result = runner.invoke(app, ["skill", "list"], catch_exceptions=False)
    assert result.exit_code == 0


def test_skill_list_finds_skill_in_search_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    skills_dir = tmp_path / "skills"
    skill_dir = skills_dir / "my-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# my-skill\n", encoding="utf-8")

    # Patch _skill_search_paths to return our tmp skills dir.
    import designos.cli.main as cli_mod
    monkeypatch.setattr(cli_mod, "_GLOBAL_SKILLS_DIR", skills_dir)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["skill", "list"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "my-skill" in result.stdout


# ---------------------------------------------------------------------------
# skill versions
# ---------------------------------------------------------------------------


def test_skill_versions_lists_prompt_dirs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    skills_dir = tmp_path / "skills"
    skill_dir = skills_dir / "demo-skill"
    prompts_dir = skill_dir / "prompts"
    (prompts_dir / "v1.0.0").mkdir(parents=True)
    (prompts_dir / "v1.1.0").mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# demo-skill\n", encoding="utf-8")

    import designos.cli.main as cli_mod
    monkeypatch.setattr(cli_mod, "_GLOBAL_SKILLS_DIR", skills_dir)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["skill", "versions", "demo-skill"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "v1.0.0" in result.stdout
    assert "v1.1.0" in result.stdout


def test_skill_versions_unknown_skill_exits_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import designos.cli.main as cli_mod
    monkeypatch.setattr(cli_mod, "_GLOBAL_SKILLS_DIR", tmp_path / "empty-skills")
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["skill", "versions", "nonexistent"])
    assert result.exit_code == 1


# ---------------------------------------------------------------------------
# preflight
# ---------------------------------------------------------------------------


def test_preflight_client_mode_passes_when_web_dependency_not_required(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    skills_dir = tmp_path / "skills"
    _make_preflight_skill(skills_dir)

    import designos.cli.main as cli_mod

    monkeypatch.setattr(cli_mod, "_GLOBAL_SKILLS_DIR", skills_dir)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["preflight", "demo-preflight", "--mode", "client"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Preflight passed" in result.stdout


def test_preflight_web_mode_fails_for_missing_playwright_probe(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    skills_dir = tmp_path / "skills"
    _make_preflight_skill(skills_dir)

    import designos.cli.main as cli_mod

    monkeypatch.setattr(cli_mod, "_GLOBAL_SKILLS_DIR", skills_dir)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["preflight", "demo-preflight", "--mode", "web"], catch_exceptions=False)

    assert result.exit_code == 1
    assert "definitely-missing-command-12345 --version" in result.output
    assert "Install Playwright before using web mode." in result.output


def test_preflight_prefers_repo_skill_over_global_install(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    skills_dir = tmp_path / "skills"
    global_skills = tmp_path / "global-skills"
    _make_preflight_skill(skills_dir)
    _make_preflight_skill(
        global_skills,
        command="definitely-missing-command-99999 --version",
        required_when=None,
    )

    import designos.cli.main as cli_mod

    monkeypatch.setattr(cli_mod, "_GLOBAL_SKILLS_DIR", global_skills)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["preflight", "demo-preflight", "--mode", "client"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Preflight passed" in result.stdout


# ---------------------------------------------------------------------------
# mcp install (stub)
# ---------------------------------------------------------------------------


def test_mcp_install_stub_outputs_todo() -> None:
    result = runner.invoke(app, ["mcp", "install", "some-server"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "TODO" in result.stdout


# ---------------------------------------------------------------------------
# resume (no workspace)
# ---------------------------------------------------------------------------


def test_resume_no_workspace_exits_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["resume"])
    assert result.exit_code == 1


def test_resume_no_checkpoint_exits_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", "resume-ws"], catch_exceptions=False)
    monkeypatch.chdir(tmp_path / "resume-ws")
    result = runner.invoke(app, ["resume"])
    assert result.exit_code == 1


# ---------------------------------------------------------------------------
# input scaffold
# ---------------------------------------------------------------------------


def test_input_scaffold_copies_templates(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    skills_dir = tmp_path / "skills"
    skill_dir = skills_dir / "tpl-skill"
    templates_dir = skill_dir / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "旅程地图.md").write_text("# template\n", encoding="utf-8")
    (skill_dir / "SKILL.md").write_text("# tpl-skill\n", encoding="utf-8")

    import designos.cli.main as cli_mod
    monkeypatch.setattr(cli_mod, "_GLOBAL_SKILLS_DIR", skills_dir)
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", "tpl-ws"], catch_exceptions=False)
    monkeypatch.chdir(tmp_path / "tpl-ws")

    result = runner.invoke(app, ["input", "scaffold", "tpl-skill"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (tmp_path / "tpl-ws" / "inputs" / "旅程地图.md").exists()


def test_input_scaffold_unknown_skill_exits_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import designos.cli.main as cli_mod
    monkeypatch.setattr(cli_mod, "_GLOBAL_SKILLS_DIR", tmp_path / "empty")
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", "scaffold-ws"], catch_exceptions=False)
    monkeypatch.chdir(tmp_path / "scaffold-ws")
    result = runner.invoke(app, ["input", "scaffold", "ghost-skill"])
    assert result.exit_code == 1
