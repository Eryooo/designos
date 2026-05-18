"""Integration tests: Kernel directly calls MCP server core modules.

These tests import the MCP server core.py functions directly (no stdio),
verifying that the Kernel can consume their outputs via the shared contracts.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Path helpers — MCP servers are standalone uv projects; add their dirs to
# sys.path so we can import core.py and schemas.py directly.
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).parent.parent.parent
_PDF_PARSER_DIR = _REPO_ROOT / "mcp-servers" / "pdf-parser"
_EXCEL_BUILDER_DIR = _REPO_ROOT / "mcp-servers" / "excel-builder"
_HEURISTIC_ENGINE_DIR = _REPO_ROOT / "mcp-servers" / "heuristic-engine"


def _add_mcp_path(p: Path) -> None:
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)


def _isolate_mcp_path(p: Path) -> None:
    """Switch sys.path to a single MCP dir and evict cached core/schemas modules.

    Each MCP server has its own ``core.py`` / ``schemas.py``; without isolation
    the second test class would get the first one's cached modules.
    """
    # Remove any other mcp-servers/* dir from sys.path
    other_mcp_dirs = [
        str(d)
        for d in (_PDF_PARSER_DIR, _EXCEL_BUILDER_DIR, _HEURISTIC_ENGINE_DIR)
        if d != p
    ]
    sys.path[:] = [s for s in sys.path if s not in other_mcp_dirs]
    _add_mcp_path(p)
    # Evict cached modules so importlib re-imports from the new sys.path
    for name in ("core", "schemas", "server", "rules", "principles_library", "llm_judge"):
        sys.modules.pop(name, None)


@pytest.fixture
def pdf_parser_env() -> None:
    """Test fixture: isolate sys.path to pdf-parser MCP."""
    _isolate_mcp_path(_PDF_PARSER_DIR)


@pytest.fixture
def excel_builder_env() -> None:
    """Test fixture: isolate sys.path to excel-builder MCP."""
    _isolate_mcp_path(_EXCEL_BUILDER_DIR)


@pytest.fixture
def heuristic_engine_env() -> None:
    """Test fixture: isolate sys.path to heuristic-engine MCP."""
    _isolate_mcp_path(_HEURISTIC_ENGINE_DIR)


# ---------------------------------------------------------------------------
# pdf-parser integration
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestPdfParserIntegration:
    """Kernel MCPClient can call pdf-parser core.py directly."""

    def test_pdf_parser_core_importable(self) -> None:
        """pdf-parser core module is importable from the MCP server directory."""
        _isolate_mcp_path(_PDF_PARSER_DIR)
        import importlib

        core = importlib.import_module("core")
        assert hasattr(core, "parse_pdf"), "parse_pdf function must exist in core"
        assert hasattr(core, "PdfParseError"), "PdfParseError must exist in core"

    def test_pdf_parser_schemas_importable(self) -> None:
        """pdf-parser schemas module is importable and contains expected models."""
        _isolate_mcp_path(_PDF_PARSER_DIR)
        import importlib

        schemas = importlib.import_module("schemas")
        assert hasattr(schemas, "PdfContent")
        assert hasattr(schemas, "PdfMetadata")
        assert hasattr(schemas, "Section")

    def test_pdf_parser_missing_file_raises(self) -> None:
        """parse_pdf raises FileNotFoundError for a non-existent path."""
        _isolate_mcp_path(_PDF_PARSER_DIR)
        import importlib

        core = importlib.import_module("core")
        with pytest.raises(FileNotFoundError):
            core.parse_pdf(Path("/nonexistent/file.pdf"))

    def test_pdf_parser_section_heading_detection(self) -> None:
        """_is_section_heading correctly identifies numbered headings."""
        _isolate_mcp_path(_PDF_PARSER_DIR)
        import importlib

        core = importlib.import_module("core")
        assert core._is_section_heading("1. 需求背景") is True
        assert core._is_section_heading("1.1. 功能描述") is True
        assert core._is_section_heading("第一章 概述") is True
        assert core._is_section_heading("普通正文内容") is False

    @pytest.mark.asyncio
    async def test_kernel_mcp_client_calls_pdf_parser(self) -> None:
        """MCPClient.call_tool routes to pdf-parser and returns ToolResult."""
        from kernel.contracts.schemas import MCPServerConfig, ToolResult
        from kernel.contracts.enums import MCPTransport

        mock_transport = AsyncMock()
        mock_transport.call = AsyncMock(
            return_value=ToolResult(
                server="pdf-parser",
                tool="parse_pdf",
                ok=True,
                data={
                    "sections": [{"title": "1. 需求背景", "content": "...", "page": 1}],
                    "metadata": {"page_count": 5, "title": None, "author": None},
                    "raw_text": "1. 需求背景\n内容",
                },
            )
        )

        from kernel.mcp.client import MCPClient
        from kernel.mcp.registry import MCPRegistry

        config = MCPServerConfig(
            name="pdf-parser",
            transport=MCPTransport.STDIO,
            command=["uv", "run", "python", "server.py"],
        )
        registry = MCPRegistry()
        registry.register(config)
        client = MCPClient(registry)
        client._transports["pdf-parser"] = mock_transport

        result: ToolResult = await client.call_tool(
            "pdf-parser", "parse_pdf", {"path": "/tmp/test.pdf"}
        )

        assert result.ok is True
        assert "sections" in result.data
        mock_transport.call.assert_called_once_with(
            "parse_pdf", {"path": "/tmp/test.pdf"}
        )


# ---------------------------------------------------------------------------
# excel-builder integration
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestExcelBuilderIntegration:
    """Kernel MCPClient can call excel-builder core.py directly."""

    def test_excel_builder_core_importable(self) -> None:
        """excel-builder core module is importable."""
        _isolate_mcp_path(_EXCEL_BUILDER_DIR)
        import importlib

        core = importlib.import_module("core")
        assert hasattr(core, "build_issue_report")
        assert hasattr(core, "ExcelBuilderError")

    def test_build_issue_report_uxeval_template(self, tmp_path: Path) -> None:
        """build_issue_report creates a valid Excel file with uxeval template."""
        _isolate_mcp_path(_EXCEL_BUILDER_DIR)
        import importlib

        core = importlib.import_module("core")

        issues: list[dict[str, Any]] = [
            {
                "id": "I-001",
                "title": "登录按钮对比度不足",
                "severity": "critical",
                "principle_ids": ["H4"],
                "description": "对比度低于 WCAG AA",
                "evidence_refs": ["E-001"],
                "suggestion": "调整颜色",
            }
        ]
        output_path = str(tmp_path / "report.xlsx")
        result = core.build_issue_report(issues, output_path, "uxeval")

        assert result["path"] == output_path
        assert result["sheet_count"] == 3
        assert Path(output_path).exists()

    def test_build_issue_report_unknown_template_raises(self, tmp_path: Path) -> None:
        """build_issue_report raises ExcelBuilderError for unknown template."""
        _isolate_mcp_path(_EXCEL_BUILDER_DIR)
        import importlib

        core = importlib.import_module("core")

        with pytest.raises(core.ExcelBuilderError, match="Unknown template"):
            core.build_issue_report([], str(tmp_path / "out.xlsx"), "unknown-template")

    @pytest.mark.asyncio
    async def test_kernel_mcp_client_calls_excel_builder(self) -> None:
        """MCPClient.call_tool routes to excel-builder and returns ToolResult."""
        from kernel.contracts.schemas import MCPServerConfig, ToolResult
        from kernel.contracts.enums import MCPTransport

        mock_transport = AsyncMock()
        mock_transport.call = AsyncMock(
            return_value=ToolResult(
                server="excel-builder",
                tool="build_issue_report",
                ok=True,
                data={"path": "/tmp/report.xlsx", "sheet_count": 3},
            )
        )

        from kernel.mcp.client import MCPClient
        from kernel.mcp.registry import MCPRegistry

        config = MCPServerConfig(
            name="excel-builder",
            transport=MCPTransport.STDIO,
            command=["uv", "run", "python", "server.py"],
        )
        registry = MCPRegistry()
        registry.register(config)
        client = MCPClient(registry)
        client._transports["excel-builder"] = mock_transport

        result: ToolResult = await client.call_tool(
            "excel-builder",
            "build_issue_report",
            {"issues": [], "output_path": "/tmp/r.xlsx", "template": "uxeval"},
        )

        assert result.ok is True
        assert result.data["sheet_count"] == 3


# ---------------------------------------------------------------------------
# heuristic-engine integration
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestHeuristicEngineIntegration:
    """Kernel MCPClient can call heuristic-engine core.py directly."""

    def test_heuristic_engine_core_importable(self) -> None:
        """heuristic-engine core module is importable."""
        _isolate_mcp_path(_HEURISTIC_ENGINE_DIR)
        import importlib

        core = importlib.import_module("core")
        assert hasattr(core, "detect")

    def test_heuristic_engine_schemas_importable(self) -> None:
        """heuristic-engine schemas module contains expected models."""
        _isolate_mcp_path(_HEURISTIC_ENGINE_DIR)
        import importlib

        schemas = importlib.import_module("schemas")
        assert hasattr(schemas, "DetectionRequest")
        assert hasattr(schemas, "DetectionResult")
        assert hasattr(schemas, "RawIssue")
        assert hasattr(schemas, "ScreenshotRef")
        assert hasattr(schemas, "HeuristicPrinciple")

    def test_detect_with_mock_judge(self, tmp_path: Path) -> None:
        """detect() returns DetectionResult with mocked LLM judge."""
        _isolate_mcp_path(_HEURISTIC_ENGINE_DIR)
        import importlib

        schemas = importlib.import_module("schemas")
        core = importlib.import_module("core")

        # Create a fake screenshot file
        screenshot = tmp_path / "s001.png"
        screenshot.write_bytes(b"\x89PNG\r\n")

        request = schemas.DetectionRequest(
            screenshots=[
                schemas.ScreenshotRef(id="S-001", path=screenshot, flow="login")
            ],
            principles=[
                schemas.HeuristicPrinciple(
                    id="H1",
                    name="系统状态可见性",
                    description="系统应始终让用户了解正在发生的事情",
                )
            ],
            constitution="每条问题必须有 evidence_refs",
            mode="client",
        )

        mock_judge = MagicMock()
        mock_judge.evaluate = MagicMock(
            return_value=[
                schemas.RawIssue(
                    title="缺少加载状态",
                    description="提交后无反馈",
                    principle="H1",
                    severity="minor",
                    evidence_refs=["S-001"],
                    source="llm_judge",
                    confidence=0.85,
                    suggestion="添加 spinner",
                    user_impact="用户不知道操作是否成功",
                )
            ]
        )

        # Patch run_rules inside the already-loaded core module to return no rule issues
        with patch.object(core, "run_rules", return_value=[]):
            result = core.detect(request, judge=mock_judge)

        assert isinstance(result, schemas.DetectionResult)
        assert result.summary.total_issues == 1
        assert result.raw_issues[0].principle == "H1"

    @pytest.mark.asyncio
    async def test_kernel_mcp_client_calls_heuristic_engine(self) -> None:
        """MCPClient.call_tool routes to heuristic-engine and returns ToolResult."""
        from kernel.contracts.schemas import MCPServerConfig, ToolResult
        from kernel.contracts.enums import MCPTransport

        mock_transport = AsyncMock()
        mock_transport.call = AsyncMock(
            return_value=ToolResult(
                server="heuristic-engine",
                tool="detect",
                ok=True,
                data={
                    "raw_issues": [
                        {
                            "title": "缺少加载状态",
                            "description": "提交后无反馈",
                            "principle": "H1",
                            "severity": "minor",
                            "evidence_refs": ["S-001"],
                            "source": "llm_judge",
                            "confidence": 0.85,
                        }
                    ],
                    "summary": {
                        "total_issues": 1,
                        "by_severity": {"minor": 1},
                        "by_principle": {"H1": 1},
                        "rule_hits": 0,
                        "llm_hits": 1,
                    },
                },
            )
        )

        from kernel.mcp.client import MCPClient
        from kernel.mcp.registry import MCPRegistry

        config = MCPServerConfig(
            name="heuristic-engine",
            transport=MCPTransport.STDIO,
            command=["uv", "run", "python", "server.py"],
        )
        registry = MCPRegistry()
        registry.register(config)
        client = MCPClient(registry)
        client._transports["heuristic-engine"] = mock_transport

        result: ToolResult = await client.call_tool(
            "heuristic-engine", "detect", {"screenshots": [], "principles": []}
        )

        assert result.ok is True
        assert result.data["summary"]["total_issues"] == 1
