"""Unit tests for playwright-driver MCP server.

Layer 1 (`unit`): pure-logic tests that MUST pass in any environment, including
when the optional `playwright` package is not installed. They cover schemas,
evidence formatting, server tool definitions, and the JSON script executor under
a mock browser. None of them launch a real browser, so a missing Playwright
dependency must never turn these red — that is the self-contained baseline this
module guards.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.unit

from schemas import (
    ActionType,
    EvaluationScript,
    ExecutionResult,
    PageState,
    ScriptStep,
    SelectorType,
    SessionInfo,
    StepEvidence,
)


class TestSchemas:
    def test_script_step_creation(self):
        step = ScriptStep(step=1, action=ActionType.NAVIGATE, url="https://example.com")
        assert step.step == 1
        assert step.action == ActionType.NAVIGATE
        assert step.url == "https://example.com"
        assert step.selector_type == SelectorType.CSS

    def test_evaluation_script(self):
        steps = [
            ScriptStep(step=1, action=ActionType.NAVIGATE, url="https://example.com"),
            ScriptStep(step=2, action=ActionType.SCREENSHOT, name="home"),
        ]
        script = EvaluationScript(task_id="T-001", task_title="Test", steps=steps)
        assert script.task_id == "T-001"
        assert len(script.steps) == 2

    def test_page_state(self):
        state = PageState(url="https://example.com", title="Example")
        assert state.url == "https://example.com"
        assert state.dom_text == ""
        assert state.page_count == 1

    def test_step_evidence_ground_truth(self):
        ev = StepEvidence(
            step=1,
            action=ActionType.SCREENSHOT,
            url="https://example.com",
            title="Example",
            screenshot_path="/tmp/test.png",
        )
        assert ev.confidence == "ground_truth"
        assert "url" in ev.evidence_basis
        assert ev.verification_gap == []

    def test_execution_result(self):
        result = ExecutionResult(
            task_id="T-001",
            task_title="Test",
            status="completed",
            steps_total=3,
            steps_succeeded=3,
            steps_failed=0,
        )
        assert result.status == "completed"


class TestEvidenceBuilder:
    def test_build_step_evidence(self):
        from evidence_builder import build_step_evidence

        state = PageState(url="https://example.com/page", title="Page")
        ev = build_step_evidence(
            step=1,
            action=ActionType.SCREENSHOT,
            page_state=state,
            screenshot_path="/tmp/shot.png",
            dom_snapshot={"text": "hello"},
        )
        assert ev.confidence == "ground_truth"
        assert ev.url == "https://example.com/page"
        assert "url" in ev.evidence_basis
        assert "dom" in ev.evidence_basis
        assert "screenshot" in ev.evidence_basis
        assert ev.verification_gap == []

    def test_build_evidence_without_screenshot(self):
        from evidence_builder import build_step_evidence

        state = PageState(url="https://example.com", title="Home")
        ev = build_step_evidence(step=2, action=ActionType.NAVIGATE, page_state=state)
        assert ev.screenshot_path is None
        assert "screenshot" not in ev.evidence_basis
        assert "url" in ev.evidence_basis


class TestServer:
    def test_tool_definitions(self):
        from server import _tool_definitions

        tools = _tool_definitions()
        names = [t["name"] for t in tools]
        assert "browser_launch" in names
        assert "browser_close" in names
        assert "navigate" in names
        assert "click_element" in names
        assert "fill_input" in names
        assert "capture_screenshot" in names
        assert "get_page_state" in names
        assert "execute_script" in names
        assert "switch_page" in names
        assert "switch_frame" in names
        assert "extract_dom" in names

    def test_handle_initialize(self):
        from server import handle_request

        result = handle_request("initialize", None)
        assert result["protocolVersion"] == "2024-11-05"
        assert "playwright-driver" in result["serverInfo"]["name"]

    def test_handle_tools_list(self):
        from server import handle_request

        result = handle_request("tools/list", None)
        assert "tools" in result
        assert len(result["tools"]) == 12

    def test_handle_unknown_method(self):
        from server import handle_request

        result = handle_request("unknown/method", None)
        assert "error" in result


class TestScriptExecutor:
    def test_execute_with_mock_browser(self):
        from script_executor import ScriptExecutor

        mock_browser = MagicMock()
        mock_browser.navigate.return_value = None
        mock_browser.get_page_state.return_value = PageState(
            url="https://example.com", title="Example"
        )
        mock_browser._page = MagicMock()

        executor = ScriptExecutor(mock_browser)
        script = EvaluationScript(
            task_id="T-001",
            task_title="Test Task",
            steps=[
                ScriptStep(step=1, action=ActionType.NAVIGATE, url="https://example.com"),
            ],
        )
        result = executor.execute(script)
        assert result.status == "completed"
        assert result.steps_succeeded == 1
        assert result.steps_failed == 0
        assert len(result.evidence) == 1
        assert result.evidence[0].confidence == "ground_truth"
