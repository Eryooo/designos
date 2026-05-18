"""Unit tests for the Typer CLI shell."""

from __future__ import annotations

from typer.testing import CliRunner

from designos.cli.main import app


def test_version_command_prints_designos_version() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout
    assert "DesignOS" in result.stdout


def test_help_lists_placeholder_commands() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for cmd in ("version", "init", "run", "resume", "config", "history", "preflight"):
        assert cmd in result.stdout


def test_run_placeholder_echoes_skill_name() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["run", "uxeval"])
    assert result.exit_code == 0
    assert "uxeval" in result.stdout
