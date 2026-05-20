"""Shared pytest fixtures for UXEval Skill integration tests."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from kernel.contracts.schemas import LLMResponse, ToolResult


SKILL_DIR: Path = Path(__file__).resolve().parent.parent
FIXTURES_DIR: Path = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def uxeval_skill_dir() -> Path:
    """Absolute path to the uxeval skill directory."""
    return SKILL_DIR


@pytest.fixture
def sample_prd_path() -> Path:
    """Sample PRD used by tests."""
    return FIXTURES_DIR / "sample-prd.md"


@pytest.fixture
def sample_scope_path() -> Path:
    """Sample scope.md used by tests."""
    return FIXTURES_DIR / "sample-scope.md"


@pytest.fixture
def mock_llm_client() -> AsyncMock:
    """Mock ILLMClient that returns staged responses keyed by stage."""
    client = AsyncMock()
    client.call = AsyncMock(
        return_value=LLMResponse(
            text='{"modules": [{"id": "M-001", "name": "登录"}]}',
            model="mock-claude-opus",
            input_tokens=200,
            output_tokens=80,
        )
    )
    return client


@pytest.fixture
def mock_mcp_client() -> AsyncMock:
    """Mock IMCPClient for heuristic-engine / pdf-parser / excel-builder."""
    client = AsyncMock()
    client.call_tool = AsyncMock(
        return_value=ToolResult(
            server="mock-server",
            tool="mock-tool",
            ok=True,
            data={"raw_issues": []},
        )
    )
    return client
