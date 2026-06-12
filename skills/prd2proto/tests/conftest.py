"""Shared pytest fixtures for the scaffolded skill."""

from __future__ import annotations

from pathlib import Path

import pytest

SKILL_DIR: Path = Path(__file__).resolve().parent.parent
FIXTURES_DIR: Path = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def skill_dir() -> Path:
    """Absolute path to this skill directory."""
    return SKILL_DIR


@pytest.fixture
def sample_prd_path() -> Path:
    return FIXTURES_DIR / "sample-prd.md"


@pytest.fixture
def sample_scope_path() -> Path:
    return FIXTURES_DIR / "sample-scope.md"
