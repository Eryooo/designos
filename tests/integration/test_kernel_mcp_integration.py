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
from PIL import Image

# ---------------------------------------------------------------------------
# Path helpers — MCP servers are standalone uv projects; add their dirs to
# sys.path so we can import core.py and schemas.py directly.
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).parent.parent.parent
_PDF_PARSER_DIR = _REPO_ROOT / "mcp-servers" / "pdf-parser"
_EXCEL_BUILDER_DIR = _REPO_ROOT / "mcp-servers" / "excel-builder"
_IMAGE_ANALYZER_DIR = _REPO_ROOT / "mcp-servers" / "image-analyzer"
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
        for d in (_PDF_PARSER_DIR, _EXCEL_BUILDER_DIR, _IMAGE_ANALYZER_DIR, _HEURISTIC_ENGINE_DIR)
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


@pytest.fixture
def image_analyzer_env() -> None:
    """Test fixture: isolate sys.path to image-analyzer MCP."""
    _isolate_mcp_path(_IMAGE_ANALYZER_DIR)


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
        assert hasattr(core, "audit_delivery_readiness")
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
        output_dir = tmp_path / "outputs"
        output_dir.mkdir()
        result = core.build_issue_report(issues, output_dir=str(output_dir), template="uxeval")

        assert result["issue_report"]["id"] == "issue_report"
        assert result["issue_report"]["sheet_count"] == 3
        assert Path(result["issue_report"]["path"]).exists()
        assert Path(result["html_report"]["path"]).exists()
        assert Path(result["evidence_pack"]["path"]).is_dir()
        assert (Path(result["evidence_pack"]["path"]) / "manifest.json").exists()

    def test_build_issue_report_unknown_template_raises(self, tmp_path: Path) -> None:
        """build_issue_report raises ExcelBuilderError for unknown template."""
        _isolate_mcp_path(_EXCEL_BUILDER_DIR)
        import importlib

        core = importlib.import_module("core")

        with pytest.raises(core.ExcelBuilderError, match="Unknown template"):
            core.build_issue_report([], str(tmp_path / "out.xlsx"), "unknown-template")

    def test_audit_delivery_readiness_returns_bounded_package(self, tmp_path: Path) -> None:
        """audit_delivery_readiness creates a deterministic audit bundle."""
        _isolate_mcp_path(_EXCEL_BUILDER_DIR)
        import importlib

        core = importlib.import_module("core")

        result = core.audit_delivery_readiness(
            issues=[
                {
                    "id": "I-001",
                    "title": "CTA hidden below the fold",
                    "severity": "major",
                    "description": "CTA is below the fold.",
                    "user_impact": "Users miss the primary action.",
                    "suggestion": "Move CTA above the fold.",
                    "evidence_refs": ["E-001"],
                    "evidence_basis": ["ocr CTA cue"],
                    "verification_status": "verified",
                }
            ],
            unverified_issues=[
                {
                    "id": "I-099",
                    "title": "Export feedback may be missing",
                    "severity": "major",
                    "blocked_by": ["missing success-state screenshot"],
                }
            ],
            evidence_assessment={
                "delivery_status": "fallback_safe",
                "required_actions": ["补导出成功状态截图"],
                "missing_coverage": ["关键状态覆盖不足"],
                "verification_gaps": ["导出成功状态未覆盖"],
                "fusion_summary": {
                    "trusted_page_mappings": [{"relative_path": "screen-01.png"}],
                    "provisional_mappings": [{"relative_path": "screen-02.png"}],
                    "conflicting_evidence_groups": [{"relative_path": "screen-03.png"}],
                    "unresolved_ambiguities": [{"relative_path": "screen-04.png"}],
                },
                "coverage_summary": {
                    "capture_mission_version": "2026-05-25",
                    "missing_state_categories": ["success"],
                    "missing_tasks": ["导出成功"],
                    "fusion_conflicting_paths": ["screen-03.png"],
                    "fusion_unresolved_paths": ["screen-04.png"],
                },
            },
            delivery_assessment={"delivery_status": "fallback_safe"},
            capture_mission={
                "mission_version": "2026-05-25",
                "critical_flows": ["导出报表"],
                "capture_order": ["导出入口", "导出成功反馈"],
                "final_delivery_pass_line": ["must_capture_states 覆盖率 >= 80%。"],
                "fallback_pass_line": ["must_capture_states 覆盖率 >= 40%。"],
            },
            output_dir=str(tmp_path / "outputs"),
        )

        assert result["audited_delivery_assessment"]["delivery_status"] == "fallback_safe"
        assert result["audited_delivery_assessment"]["capture_mission_version"] == "2026-05-25"
        assert result["audited_delivery_assessment"]["fallback_pass_line"] == ["must_capture_states 覆盖率 >= 40%。"]
        assert result["audited_delivery_assessment"]["fusion_summary"]["conflict_count"] == 1
        assert result["audited_delivery_assessment"]["delivery_readiness_breakdown"]["fallback_gate_pass"] is True
        assert "trusted_evidence_sufficiency" in result["audited_delivery_assessment"]["delivery_readiness_breakdown"]["failing_final_gates"]
        bundle_path = Path(result["delivery_audit_bundle"]["path"])
        assert bundle_path.is_dir()
        assert (bundle_path / "bounded_issue_pass.md").exists()
        assert (bundle_path / "unverified_issues.json").exists()
        assert (bundle_path / "supplement_request.md").exists()
        assert "Capture Mission pass lines" in (bundle_path / "supplement_request.md").read_text(encoding="utf-8")

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
                data={
                    "issue_report": {
                        "id": "issue_report",
                        "type": "issue_report",
                        "path": "/tmp/report.xlsx",
                        "format": "xlsx",
                        "summary": "Excel report",
                        "sheet_count": 3,
                    },
                    "html_report": {
                        "id": "html_report",
                        "type": "html_report",
                        "path": "/tmp/report.html",
                        "format": "html",
                        "summary": "HTML report",
                    },
                    "evidence_pack": {
                        "id": "evidence_pack",
                        "type": "evidence_pack",
                        "path": "/tmp/evidence_pack",
                        "format": "directory",
                        "summary": "Evidence pack",
                    },
                },
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
            {"issues": [], "output_dir": "/tmp/out", "template": "uxeval"},
        )

        assert result.ok is True
        assert result.data["issue_report"]["sheet_count"] == 3
        assert result.data["html_report"]["type"] == "html_report"


# ---------------------------------------------------------------------------
# heuristic-engine integration
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestImageAnalyzerIntegration:
    """Kernel MCPClient can call image-analyzer core.py directly."""

    def test_image_analyzer_core_importable(self) -> None:
        _isolate_mcp_path(_IMAGE_ANALYZER_DIR)
        import importlib

        core = importlib.import_module("core")
        assert hasattr(core, "load_and_analyze")
        assert hasattr(core, "plan_required_evidence")

    def test_image_analyzer_planning_returns_structured_pre_run_guidance(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _isolate_mcp_path(_IMAGE_ANALYZER_DIR)
        import importlib

        core = importlib.import_module("core")
        ocr_runtime = importlib.import_module("ocr_runtime")

        screens = tmp_path / "screens"
        screens.mkdir()
        Image.new("RGB", (1440, 900), "white").save(screens / "login-default.png")
        Image.new("RGB", (1440, 900), "white").save(screens / "dashboard-default.png")
        (screens / "screens-description.md").write_text(
            "# 登录页\n\n登录页默认态。\n\n# 工作台首页\n\n工作台首页默认态。",
            encoding="utf-8",
        )
        monkeypatch.setattr(
            core,
            "probe_ocr_backend",
            lambda: ocr_runtime.OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
        )

        result = core.plan_required_evidence(
            modules=[{"name": "登录"}, {"name": "工作台首页"}, {"name": "设置页"}],
            key_features=[{"name": "登录"}, {"name": "查看工作台"}, {"name": "进入设置"}],
            task_checklist_lite="- 登录\n- 工作台首页\n- 设置页",
            journey_stages=["进入登录", "进入工作台", "进入设置"],
            screenshots_dir=screens,
        )

        assert result.capture_mission.must_capture_pages
        assert result.required_evidence_plan.critical_page_count >= 3
        assert result.evidence_input_guidance.pre_run_status == "supplement_required"
        assert "设置页" in "；".join(result.evidence_input_guidance.missing_pages)

    def test_image_analyzer_returns_text_evidence_contract(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _isolate_mcp_path(_IMAGE_ANALYZER_DIR)
        import importlib

        core = importlib.import_module("core")
        ocr_runtime = importlib.import_module("ocr_runtime")

        nested = tmp_path / "screens" / "nested"
        nested.mkdir(parents=True)
        Image.new("RGB", (1440, 900), "white").save(nested / "screen-01.png")
        (tmp_path / "screens" / "screens-description.md").write_text(
            "# Login Screen\n\nContains 登录 button and error state tips.",
            encoding="utf-8",
        )
        monkeypatch.setattr(
            core,
            "probe_ocr_backend",
            lambda: ocr_runtime.OCRProbeResult(available=True, backend="tesseract"),
        )
        monkeypatch.setattr(
            core,
            "run_ocr",
            lambda path, preferred_backend=None: ocr_runtime.OCRResult(
                backend="tesseract",
                lines=(
                    ocr_runtime.OCRLine(text="登录", confidence=0.92),
                    ocr_runtime.OCRLine(text="重试", confidence=0.88),
                ),
                raw_text="登录\n重试",
            ),
        )

        result = core.load_and_analyze(tmp_path / "screens")

        assert result.image_analysis.analyzer_kind == "text_evidence_inventory"
        assert result.image_analysis.ocr_available is True
        assert result.image_analysis.semantic_analysis_available is False
        assert result.image_analysis.summary["total_files"] == 2
        assert result.evidence_assessment.verdict == "sufficient"
        assert result.evidence_assessment.delivery_status == "fallback_safe"
        assert result.evidence_assessment.final_delivery_ready is False
        assert result.screenshots[0].relative_path == "nested/screen-01.png"
        assert result.screenshots[0].resolution == "1440x900"
        assert result.screenshots[0].button_text_candidates[0].source_channel == "ocr"

    def test_image_analyzer_plan_flows_into_runtime_coverage(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _isolate_mcp_path(_IMAGE_ANALYZER_DIR)
        import importlib

        core = importlib.import_module("core")
        ocr_runtime = importlib.import_module("ocr_runtime")

        screens = tmp_path / "screens"
        screens.mkdir()
        for name in ("login-default.png", "dashboard-default.png", "settings-default.png"):
            Image.new("RGB", (1440, 900), "white").save(screens / name)
        (screens / "screens-description.md").write_text(
            "# 登录页\n\n登录默认态。\n\n# 工作台首页\n\n工作台首页默认态。\n\n# 设置页\n\n设置页默认态。",
            encoding="utf-8",
        )
        monkeypatch.setattr(
            core,
            "probe_ocr_backend",
            lambda: ocr_runtime.OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
        )

        plan = core.plan_required_evidence(
            modules=[{"name": "登录"}, {"name": "工作台首页"}, {"name": "设置页"}],
            key_features=[{"name": "登录"}, {"name": "查看工作台"}, {"name": "进入设置"}],
            task_checklist_lite="- 登录\n- 工作台首页\n- 设置页",
            journey_stages=["进入登录", "进入工作台", "进入设置"],
            screenshots_dir=screens,
        )

        result = core.load_and_analyze(
            screens,
            task_checklist_lite="- 登录\n- 工作台首页\n- 设置页",
            required_evidence_plan=plan.required_evidence_plan,
        )

        summary = result.evidence_assessment.coverage_summary
        assert summary["required_evidence_plan_version"] == "2026-05-25"
        assert summary["capture_mission_version"] == "2026-05-25"
        assert summary["planned_page_count"] >= 3
        assert summary["final_delivery_pass_line"] == plan.capture_mission.final_delivery_pass_line
        assert "missing_critical_pages" in summary

    def test_image_analyzer_critical_path_summary_blocks_final_when_p0_missing(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _isolate_mcp_path(_IMAGE_ANALYZER_DIR)
        import importlib

        core = importlib.import_module("core")
        ocr_runtime = importlib.import_module("ocr_runtime")

        screens = tmp_path / "screens"
        screens.mkdir()
        for name in (
            "dashboard-home.png",
            "settings-page.png",
            "report-list.png",
            "export-center.png",
            "notice-center.png",
        ):
            Image.new("RGB", (1440, 900), "white").save(screens / name)
        (screens / "screens-description.md").write_text(
            "\n".join(
                [
                    "# 关键页面说明",
                    "",
                    "## dashboard-home.png",
                    "这是工作台首页加载态。",
                    "",
                    "## settings-page.png",
                    "这是设置页保存成功态。",
                    "",
                    "## report-list.png",
                    "这是报表列表空状态。",
                    "",
                    "## export-center.png",
                    "这是导出中心成功态。",
                    "",
                    "## notice-center.png",
                    "这是通知中心默认态。",
                ]
            ),
            encoding="utf-8",
        )
        monkeypatch.setattr(
            core,
            "probe_ocr_backend",
            lambda: ocr_runtime.OCRProbeResult(available=True, backend="tesseract"),
        )
        ocr_lines = {
            "dashboard-home.png": ("工作台首页", "加载中"),
            "settings-page.png": ("设置页", "保存成功"),
            "report-list.png": ("报表列表", "暂无数据"),
            "export-center.png": ("导出中心", "导出成功"),
            "notice-center.png": ("通知中心", "消息中心"),
        }
        monkeypatch.setattr(
            core,
            "run_ocr",
            lambda path, preferred_backend=None: ocr_runtime.OCRResult(
                backend="tesseract",
                lines=tuple(
                    ocr_runtime.OCRLine(text=text, confidence=0.93)
                    for text in ocr_lines[path.name]
                ),
                raw_text="\n".join(ocr_lines[path.name]),
            ),
        )

        plan = core.plan_required_evidence(
            modules=[{"name": name} for name in ("登录", "工作台首页", "设置页", "报表列表", "导出中心", "通知中心")],
            key_features=[{"name": name} for name in ("登录", "查看工作台", "保存设置", "查看报表", "导出中心", "通知中心")],
            task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 导出中心\n- 通知中心",
            journey_stages=["登录", "工作台首页", "设置页", "报表列表", "导出中心", "通知中心"],
            screenshots_dir=screens,
        )

        result = core.load_and_analyze(
            screens,
            task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 导出中心\n- 通知中心",
            required_evidence_plan=plan.required_evidence_plan,
        )

        assert result.evidence_assessment.delivery_status == "supplement_required"
        assert result.evidence_assessment.first_pass_success_breakdown is not None
        assert "missing_evidence" in result.evidence_assessment.first_pass_success_breakdown["supplement_cause_classification"]
        assert result.evidence_assessment.critical_path_coverage_summary is not None
        assert "[P0] 登录" in result.evidence_assessment.critical_path_coverage_summary.failing_final_paths
        assert result.evidence_assessment.coverage_summary["planned_page_coverage_ratio"] == 0.833
        assert result.evidence_assessment.targeted_acquisition_plan is not None
        assert result.evidence_assessment.targeted_acquisition_plan.highest_value_next_captures
        assert result.evidence_assessment.targeted_acquisition_plan.highest_value_next_captures[0].target_page == "登录"
        assert result.evidence_assessment.targeted_acquisition_plan.highest_value_next_captures[0].suggested_input_form == "screenshot"
        assert result.evidence_assessment.client_mode_metrics is not None
        assert result.evidence_assessment.client_mode_metrics.success_metrics.supplement_required_rate == 1.0
        assert result.evidence_assessment.benchmark_summary is not None
        assert result.evidence_assessment.benchmark_summary.delivery_status == "supplement_required"
        assert result.evidence_assessment.benchmark_summary.root_cause == "input_truly_insufficient"

    def test_image_analyzer_auto_drafts_mapping_for_messy_names(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _isolate_mcp_path(_IMAGE_ANALYZER_DIR)
        import importlib

        core = importlib.import_module("core")
        ocr_runtime = importlib.import_module("ocr_runtime")

        screens = tmp_path / "screens"
        screens.mkdir()
        for name in ("IMG3001.png", "IMG3002.png", "IMG3003.png", "IMG3004.png", "IMG3005.png"):
            Image.new("RGB", (1440, 900), "white").save(screens / name)
        (screens / "screens-description.md").write_text(
            "\n".join(
                [
                    "# 关键页面说明",
                    "",
                    "## IMG3001.png",
                    "这是登录页加载态。",
                    "",
                    "## IMG3002.png",
                    "这是登录页错误态。",
                    "",
                    "## IMG3003.png",
                    "这是工作台首页默认态。",
                    "",
                    "## IMG3004.png",
                    "这是设置页保存成功态。",
                    "",
                    "## IMG3005.png",
                    "这是报表列表空状态。",
                ]
            ),
            encoding="utf-8",
        )
        monkeypatch.setattr(
            core,
            "probe_ocr_backend",
            lambda: ocr_runtime.OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
        )

        plan = core.plan_required_evidence(
            modules=[{"name": "登录"}, {"name": "工作台首页"}, {"name": "设置页"}, {"name": "报表列表"}],
            key_features=[{"name": "登录"}, {"name": "查看工作台"}, {"name": "保存设置"}, {"name": "查看报表"}],
            task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表",
            journey_stages=["进入登录", "进入工作台", "保存设置", "查看报表"],
            screenshots_dir=screens,
        )

        result = core.load_and_analyze(
            screens,
            task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表",
            required_evidence_plan=plan.required_evidence_plan,
        )

        image_refs = [ref for ref in result.screenshots if ref.kind == "image"]
        assert result.evidence_assessment.coverage_summary["draft_mapping_count"] == len(image_refs)
        assert result.evidence_assessment.coverage_summary["clarification_needed_count"] == 0
        assert result.evidence_assessment.coverage_summary["naming_issues"]
        assert result.evidence_assessment.fusion_summary is not None
        assert len(result.evidence_assessment.fusion_summary.trusted_page_mappings) >= 4
        assert all(ref.draft_mapping is not None for ref in image_refs)
        assert all(
            ref.draft_mapping is not None and ref.draft_mapping.page_name is not None
            for ref in image_refs
        )

    def test_image_analyzer_clarification_mapping_file_promotes_final_delivery(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _isolate_mcp_path(_IMAGE_ANALYZER_DIR)
        import importlib

        core = importlib.import_module("core")
        ocr_runtime = importlib.import_module("ocr_runtime")

        screens = tmp_path / "screens"
        screens.mkdir()
        for name in ("IMG4001.png", "IMG4002.png", "IMG4003.png", "IMG4004.png", "IMG4005.png"):
            Image.new("RGB", (1440, 900), "white").save(screens / name)
        (screens / "screens-description.md").write_text(
            "\n".join(
                [
                    "# 关键页面说明",
                    "",
                    "## IMG4001.png",
                    "这是登录页成功态。",
                    "",
                    "## IMG4002.png",
                    "这是工作台首页默认态。",
                    "",
                    "## IMG4003.png",
                    "这个页面可能是设置页或报表列表，当前只看到列表区域和一个保存入口。",
                    "",
                    "## IMG4004.png",
                    "这是报表列表空状态。",
                    "",
                    "## IMG4005.png",
                    "这是通知中心默认态。",
                ]
            ),
            encoding="utf-8",
        )
        monkeypatch.setattr(
            core,
            "probe_ocr_backend",
            lambda: ocr_runtime.OCRProbeResult(available=True, backend="tesseract"),
        )
        ocr_lines = {
            "IMG4001.png": ("登录", "登录成功"),
            "IMG4002.png": ("工作台首页", "首页"),
            "IMG4003.png": ("保存", "列表"),
            "IMG4004.png": ("报表列表", "暂无数据"),
            "IMG4005.png": ("通知中心", "消息中心"),
        }
        monkeypatch.setattr(
            core,
            "run_ocr",
            lambda path, preferred_backend=None: ocr_runtime.OCRResult(
                backend="tesseract",
                lines=tuple(
                    ocr_runtime.OCRLine(text=text, confidence=0.93)
                    for text in ocr_lines[path.name]
                ),
                raw_text="\n".join(ocr_lines[path.name]),
            ),
        )

        plan = core.plan_required_evidence(
            modules=[{"name": name} for name in ("登录", "工作台首页", "设置页", "报表列表", "通知中心")],
            key_features=[{"name": name} for name in ("登录", "查看工作台", "保存设置", "查看报表", "通知中心")],
            task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心",
            journey_stages=["登录", "工作台首页", "设置页", "报表列表", "通知中心"],
            screenshots_dir=screens,
        )

        before = core.load_and_analyze(
            screens,
            task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心",
            required_evidence_plan=plan.required_evidence_plan,
        )
        assert before.evidence_assessment.delivery_status == "fallback_safe"
        assert before.evidence_assessment.clarification_items
        assert before.evidence_assessment.targeted_acquisition_plan is not None
        assert before.evidence_assessment.targeted_acquisition_plan.highest_value_next_captures[0].suggested_input_form == "clarification"

        (screens / "screens-map.md").write_text(
            "- IMG4003.png -> page=设置页; states=success\n",
            encoding="utf-8",
        )
        after = core.load_and_analyze(
            screens,
            task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心",
            required_evidence_plan=plan.required_evidence_plan,
        )

        assert after.evidence_assessment.delivery_status == "final_delivery_ready"
        assert after.evidence_assessment.clarification_items == []
        assert after.evidence_assessment.targeted_acquisition_plan is not None
        assert after.evidence_assessment.targeted_acquisition_plan.highest_value_next_captures == []
        assert before.evidence_assessment.benchmark_summary is not None
        assert before.evidence_assessment.benchmark_summary.delivery_status == "fallback_safe"
        assert after.evidence_assessment.client_mode_metrics is not None
        assert after.evidence_assessment.client_mode_metrics.success_metrics.final_delivery_ready_rate == 1.0
        assert after.evidence_assessment.benchmark_summary is not None
        assert after.evidence_assessment.benchmark_summary.delivery_status == "final_delivery_ready"


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
