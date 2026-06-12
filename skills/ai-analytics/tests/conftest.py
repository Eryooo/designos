"""Shared pytest fixtures for ai-analytics."""

from __future__ import annotations

from pathlib import Path

import pytest

SKILL_DIR: Path = Path(__file__).resolve().parent.parent


@pytest.fixture
def skill_dir() -> Path:
    return SKILL_DIR
