"""E2E smoke tests: CLI invocation via subprocess.

Tests that the designos CLI binary can be invoked, returns expected output,
and creates correct workspace structures. No real LLM calls are made.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from designos import __version__ as DESIGNOS_VERSION


_REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Run the repository CLI via the current Python environment."""
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    pythonpath_parts = [str(_REPO_ROOT)]
    if existing_pythonpath:
        pythonpath_parts.append(existing_pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)

    return subprocess.run(
        [sys.executable, "-m", "designos.cli.main", *args],
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else str(_REPO_ROOT),
        env=env,
        timeout=30,
    )


def _run_designos(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Run the repository CLI, never the globally installed `designos`."""
    return _run_cli(*args, cwd=cwd)


# ---------------------------------------------------------------------------
# Version smoke test
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestVersionCommand:
    """designos --version / version command returns expected output."""

    def test_version_command_exits_zero(self) -> None:
        """designos version exits with code 0."""
        result = _run_designos("version")
        assert result.returncode == 0, (
            f"Expected exit 0, got {result.returncode}\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_version_output_contains_version_string(self) -> None:
        """designos version output contains the package version."""
        result = _run_designos("version")
        combined = result.stdout + result.stderr
        assert DESIGNOS_VERSION in combined, (
            f"Expected '{DESIGNOS_VERSION}' in output, got:\n{combined}"
        )

    def test_version_output_contains_designos(self) -> None:
        """designos version output contains 'DesignOS'."""
        result = _run_designos("version")
        combined = result.stdout + result.stderr
        assert "DesignOS" in combined, (
            f"Expected 'DesignOS' in output, got:\n{combined}"
        )

    def test_help_flag_exits_zero(self) -> None:
        """designos --help exits with code 0."""
        result = _run_designos("--help")
        assert result.returncode == 0

    def test_help_output_contains_commands(self) -> None:
        """designos --help lists core commands."""
        result = _run_designos("--help")
        combined = result.stdout + result.stderr
        for cmd in ["init", "run", "version"]:
            assert cmd in combined, f"Expected '{cmd}' in help output"


# ---------------------------------------------------------------------------
# Init command smoke test
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestInitCommand:
    """designos init creates a workspace directory."""

    def test_init_exits_zero(self, tmp_path: Path) -> None:
        """designos init test-project exits with code 0."""
        result = _run_designos("init", "test-project", cwd=tmp_path)
        assert result.returncode == 0, (
            f"Expected exit 0, got {result.returncode}\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_init_produces_output(self, tmp_path: Path) -> None:
        """designos init produces some output (TODO placeholder or real output)."""
        result = _run_designos("init", "test-project", cwd=tmp_path)
        combined = result.stdout + result.stderr
        assert len(combined.strip()) > 0, "Expected non-empty output from init"

    def test_init_with_skill_flag_exits_zero(self, tmp_path: Path) -> None:
        """designos init test-project --skill uxeval exits with code 0.

        Note: In M1 the init command is a placeholder (A6 not yet complete),
        so we only verify the CLI accepts the arguments without crashing.
        """
        result = _run_designos("init", "test-project", "--skill", "uxeval", cwd=tmp_path)
        # CLI must not crash with an unhandled exception
        assert result.returncode == 0, (
            f"CLI crashed with exit {result.returncode}\n"
            f"stderr: {result.stderr}"
        )

    def test_init_help_available(self) -> None:
        """designos init --help exits with code 0."""
        result = _run_designos("init", "--help")
        assert result.returncode == 0


# ---------------------------------------------------------------------------
# Other command smoke tests
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestOtherCommands:
    """Smoke tests for remaining CLI commands."""

    def test_run_help_available(self) -> None:
        """designos run --help exits with code 0."""
        result = _run_designos("run", "--help")
        assert result.returncode == 0

    def test_resume_exits_with_error_outside_workspace(self) -> None:
        """designos resume returns non-zero outside a workspace (correct behavior)."""
        result = _run_designos("resume")
        assert result.returncode != 0
        assert "workspace" in result.stderr.lower() or "workspace" in result.stdout.lower()

    def test_config_runs_or_prompts(self) -> None:
        """designos config either prompts (and times out via empty stdin) or completes."""
        # config is interactive; in non-interactive mode it should fail gracefully (not crash)
        result = _run_designos("config")
        # Accept either successful no-op or graceful exit; just ensure no traceback
        assert "Traceback" not in result.stderr

    def test_history_exits_with_error_outside_workspace(self) -> None:
        """designos history returns non-zero outside a workspace (correct behavior)."""
        result = _run_designos("history")
        assert result.returncode != 0
        assert "workspace" in result.stderr.lower() or "workspace" in result.stdout.lower()

    def test_preflight_exits_zero(self) -> None:
        """designos preflight uxeval exits with code 0 (placeholder)."""
        result = _run_designos("preflight", "uxeval")
        assert result.returncode == 0


# ---------------------------------------------------------------------------
# Module-level import smoke test
# ---------------------------------------------------------------------------


@pytest.mark.e2e
class TestImportSmoke:
    """Verify top-level package imports succeed without side effects."""

    def test_designos_package_importable(self) -> None:
        """designos package imports cleanly."""
        import importlib

        mod = importlib.import_module("designos")
        assert hasattr(mod, "__version__")
        assert mod.__version__ == DESIGNOS_VERSION

    def test_kernel_contracts_importable(self) -> None:
        """kernel.contracts package imports cleanly."""
        import importlib

        schemas = importlib.import_module("kernel.contracts.schemas")
        enums = importlib.import_module("kernel.contracts.enums")
        interfaces = importlib.import_module("kernel.contracts.interfaces")

        assert hasattr(schemas, "Issue")
        assert hasattr(enums, "SeverityLevel")
        assert hasattr(interfaces, "IPipelineEngine")

    def test_pipeline_engine_importable(self) -> None:
        """kernel.pipeline.engine imports cleanly."""
        import importlib

        mod = importlib.import_module("kernel.pipeline.engine")
        assert hasattr(mod, "PipelineEngine")

    def test_checkpoint_manager_importable(self) -> None:
        """kernel.checkpoint.manager imports cleanly."""
        import importlib

        mod = importlib.import_module("kernel.checkpoint.manager")
        assert hasattr(mod, "CheckpointManager")
