"""Unit tests for IDE detection, installer, and init global flow."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from designos.cli.ide_detector import IDE, detect_ide, ide_config_path
from designos.cli.installer import (
    ask_api_key,
    check_api_connectivity,
    install_ide_configs,
)
from designos.cli.main import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# IDE Detector
# ---------------------------------------------------------------------------


class TestDetectIDE:
    """Tests for detect_ide()."""

    def test_returns_valid_enum(self) -> None:
        result = detect_ide()
        assert isinstance(result, IDE)
        assert result.value in [e.value for e in IDE]

    def test_detects_claude_code_from_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("CLAUDE_CODE_ENTRYPOINT", "1")
        # Clear others that might interfere
        for var in ("CURSOR_TRACE_ID", "CURSOR", "TRAE_IDE", "CODEX_CLI"):
            monkeypatch.delenv(var, raising=False)
        assert detect_ide() == IDE.CLAUDE_CODE

    def test_detects_cursor_from_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("CLAUDE_CODE_ENTRYPOINT", raising=False)
        monkeypatch.setenv("CURSOR_TRACE_ID", "abc123")
        assert detect_ide() == IDE.CURSOR

    def test_detects_trae_from_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("CLAUDE_CODE_ENTRYPOINT", raising=False)
        monkeypatch.delenv("CURSOR_TRACE_ID", raising=False)
        monkeypatch.delenv("CURSOR", raising=False)
        monkeypatch.setenv("TRAE_IDE", "1")
        assert detect_ide() == IDE.TRAE

    def test_detects_codex_from_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("CLAUDE_CODE_ENTRYPOINT", raising=False)
        monkeypatch.delenv("CURSOR_TRACE_ID", raising=False)
        monkeypatch.delenv("CURSOR", raising=False)
        monkeypatch.delenv("TRAE_IDE", raising=False)
        monkeypatch.setenv("CODEX_CLI", "1")
        assert detect_ide() == IDE.CODEX

    def test_returns_unknown_when_no_signals(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Clear all known env vars
        for var in (
            "CLAUDE_CODE_ENTRYPOINT",
            "CURSOR_TRACE_ID",
            "CURSOR",
            "TRAE_IDE",
            "CODEX_CLI",
            "WORKBUDDY_ENV",
            "CODEBUDDY_ENV",
        ):
            monkeypatch.delenv(var, raising=False)
        # Patch shutil.which to return None for all known binaries
        monkeypatch.setattr("shutil.which", lambda _: None)
        assert detect_ide() == IDE.UNKNOWN

    def test_env_takes_priority_over_path(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("CLAUDE_CODE_ENTRYPOINT", raising=False)
        monkeypatch.delenv("CURSOR_TRACE_ID", raising=False)
        monkeypatch.delenv("CURSOR", raising=False)
        monkeypatch.setenv("TRAE_IDE", "1")
        # Even if 'claude' is on PATH, env wins
        monkeypatch.setattr("shutil.which", lambda x: "/usr/bin/claude" if x == "claude" else None)
        assert detect_ide() == IDE.TRAE


class TestIDEConfigPath:
    """Tests for ide_config_path()."""

    def test_claude_code_paths(self, tmp_path: Path) -> None:
        paths = ide_config_path(IDE.CLAUDE_CODE, tmp_path)
        assert "agents" in paths
        assert paths["agents"] == tmp_path / "AGENTS.md"
        assert "commands" in paths
        assert paths["commands"] == tmp_path / ".claude" / "commands"

    def test_cursor_paths(self, tmp_path: Path) -> None:
        paths = ide_config_path(IDE.CURSOR, tmp_path)
        assert "rules" in paths
        assert paths["rules"] == tmp_path / ".cursor" / "rules"
        assert "cursorrules" in paths
        assert paths["cursorrules"] == tmp_path / ".cursorrules"

    def test_trae_paths(self, tmp_path: Path) -> None:
        paths = ide_config_path(IDE.TRAE, tmp_path)
        assert "agents" in paths
        assert paths["agents"] == tmp_path / "AGENTS.md"

    def test_unknown_fallback(self, tmp_path: Path) -> None:
        paths = ide_config_path(IDE.UNKNOWN, tmp_path)
        assert "agents" in paths
        assert paths["agents"] == tmp_path / "AGENTS.md"

    def test_all_ides_return_non_empty(self, tmp_path: Path) -> None:
        for ide in IDE:
            paths = ide_config_path(ide, tmp_path)
            assert len(paths) > 0


# ---------------------------------------------------------------------------
# Installer
# ---------------------------------------------------------------------------


class TestInstallIDEConfigs:
    """Tests for install_ide_configs()."""

    def test_copies_agents_md(self, tmp_path: Path) -> None:
        source = tmp_path / "repo"
        source.mkdir()
        (source / "AGENTS.md").write_text("# Test AGENTS", encoding="utf-8")
        (source / "kernel").mkdir()

        target = tmp_path / "project"
        target.mkdir()

        written = install_ide_configs(IDE.CLAUDE_CODE, target, source)
        assert (target / "AGENTS.md").exists()
        assert (target / "AGENTS.md").read_text() == "# Test AGENTS"
        assert any("AGENTS.md" in str(p) for p in written)

    def test_creates_commands_dir_for_claude_code(self, tmp_path: Path) -> None:
        source = tmp_path / "repo"
        source.mkdir()
        (source / "AGENTS.md").write_text("# Agents", encoding="utf-8")
        (source / "kernel").mkdir()

        target = tmp_path / "project"
        target.mkdir()

        install_ide_configs(IDE.CLAUDE_CODE, target, source)
        assert (target / ".claude" / "commands").is_dir()

    def test_cursor_creates_rules_and_cursorrules(self, tmp_path: Path) -> None:
        source = tmp_path / "repo"
        source.mkdir()
        (source / "AGENTS.md").write_text("# Cursor rules", encoding="utf-8")
        (source / "kernel").mkdir()

        target = tmp_path / "project"
        target.mkdir()

        written = install_ide_configs(IDE.CURSOR, target, source)
        assert (target / ".cursor" / "rules" / "designos.md").exists()
        assert (target / ".cursorrules").exists()
        assert len(written) >= 2

    def test_no_source_agents_md_skips_gracefully(self, tmp_path: Path) -> None:
        source = tmp_path / "empty-repo"
        source.mkdir()

        target = tmp_path / "project"
        target.mkdir()

        written = install_ide_configs(IDE.UNKNOWN, target, source)
        assert written == []


class TestAskAPIKey:
    """Tests for ask_api_key() with mocked input."""

    def test_returns_new_key_when_no_existing(self) -> None:
        with patch("typer.prompt", return_value="sk-ant-test123"):
            key = ask_api_key(existing=None)
        assert key == "sk-ant-test123"

    def test_keeps_existing_key_when_user_declines(self) -> None:
        with patch("typer.confirm", return_value=False):
            with patch("typer.echo"):
                key = ask_api_key(existing="sk-ant-old-key-1234")
        assert key == "sk-ant-old-key-1234"

    def test_replaces_existing_key_when_user_confirms(self) -> None:
        with patch("typer.confirm", return_value=True):
            with patch("typer.echo"):
                with patch("typer.prompt", return_value="sk-ant-new-key"):
                    key = ask_api_key(existing="sk-ant-old-key-1234")
        assert key == "sk-ant-new-key"


class TestAPIConnectivity:
    """Tests for check_api_connectivity() with mocked HTTP."""

    def test_success_on_200(self) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        with patch("httpx.post", return_value=mock_resp):
            success, err = check_api_connectivity("sk-ant-test")
        assert success is True
        assert err == ""

    def test_failure_on_401(self) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized"
        with patch("httpx.post", return_value=mock_resp):
            success, err = check_api_connectivity("sk-bad-key")
        assert success is False
        assert "Authentication" in err

    def test_failure_on_timeout(self) -> None:
        import httpx

        with patch("httpx.post", side_effect=httpx.TimeoutException("timeout")):
            success, err = check_api_connectivity("sk-ant-test")
        assert success is False
        assert "timed out" in err

    def test_failure_on_connect_error(self) -> None:
        import httpx

        with patch("httpx.post", side_effect=httpx.ConnectError("refused")):
            success, err = check_api_connectivity("sk-ant-test")
        assert success is False
        assert "Connection error" in err

    def test_custom_base_url(self) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        with patch("httpx.post", return_value=mock_resp) as mock_post:
            check_api_connectivity("sk-ant-test", base_url="https://proxy.example.com")
        call_args = mock_post.call_args
        assert "proxy.example.com" in call_args[0][0]


# ---------------------------------------------------------------------------
# CLI init command integration
# ---------------------------------------------------------------------------


class TestInitCommand:
    """Tests for the unified init command."""

    def test_init_help_shows_both_modes(self) -> None:
        result = runner.invoke(app, ["init", "--help"])
        assert result.exit_code == 0
        assert "global setup" in result.stdout.lower() or "Global" in result.stdout

    def test_init_with_name_creates_workspace(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["init", "my-ws"], catch_exceptions=False)
        assert result.exit_code == 0
        assert (tmp_path / "my-ws" / "designos.project.yaml").exists()

    def test_init_no_args_triggers_global_install(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """init without name should call run_global_install."""
        monkeypatch.chdir(tmp_path)
        with patch("designos.cli.installer.run_global_install") as mock_install:
            result = runner.invoke(app, ["init"], catch_exceptions=False)
        assert result.exit_code == 0
        mock_install.assert_called_once_with(force=False)

    def test_init_force_flag_passed_to_global_install(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.chdir(tmp_path)
        with patch("designos.cli.installer.run_global_install") as mock_install:
            result = runner.invoke(app, ["init", "--force"], catch_exceptions=False)
        assert result.exit_code == 0
        mock_install.assert_called_once_with(force=True)
