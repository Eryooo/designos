"""Unit tests for the deterministic rule engine."""

from __future__ import annotations

from schemas import DomNode, DomSnapshot, ScreenshotRef
from rules import (
    rule_action_button_overload,
    rule_form_field_missing_label,
    rule_jargon_without_explanation,
    rule_missing_error_message,
    rule_missing_status_indicator,
    run_rules,
)


# ---------------------------------------------------------------------------
# rule_missing_status_indicator
# ---------------------------------------------------------------------------


def test_missing_status_indicator_hits(loading_screenshot: ScreenshotRef) -> None:
    snapshot = DomSnapshot(screenshot_id=loading_screenshot.id, nodes=[])
    issues = rule_missing_status_indicator(loading_screenshot, snapshot)
    assert len(issues) == 1
    assert issues[0].principle == "H1"
    assert issues[0].evidence_refs == [loading_screenshot.id]


def test_missing_status_indicator_misses_when_indicator_present(
    loading_screenshot: ScreenshotRef,
) -> None:
    snapshot = DomSnapshot(
        screenshot_id=loading_screenshot.id,
        nodes=[],
        has_loading_indicator=True,
    )
    assert rule_missing_status_indicator(loading_screenshot, snapshot) == []


def test_missing_status_indicator_skips_unrelated_flow(
    calm_screenshot: ScreenshotRef,
) -> None:
    snapshot = DomSnapshot(screenshot_id=calm_screenshot.id, nodes=[])
    assert rule_missing_status_indicator(calm_screenshot, snapshot) == []


# ---------------------------------------------------------------------------
# rule_action_button_overload
# ---------------------------------------------------------------------------


def test_action_button_overload_hits(
    calm_screenshot: ScreenshotRef,
    overload_snapshot: DomSnapshot,
) -> None:
    issues = rule_action_button_overload(calm_screenshot, overload_snapshot)
    assert len(issues) == 1
    assert issues[0].principle == "B4"


def test_action_button_overload_misses_below_threshold(
    calm_screenshot: ScreenshotRef,
) -> None:
    snapshot = DomSnapshot(
        screenshot_id=calm_screenshot.id,
        nodes=[
            DomNode(tag="button", text="详情"),
            DomNode(tag="button", text="编辑"),
        ],
    )
    assert rule_action_button_overload(calm_screenshot, snapshot) == []


# ---------------------------------------------------------------------------
# rule_jargon_without_explanation
# ---------------------------------------------------------------------------


def test_jargon_without_explanation_hits(
    calm_screenshot: ScreenshotRef,
    jargon_snapshot: DomSnapshot,
) -> None:
    issues = rule_jargon_without_explanation(calm_screenshot, jargon_snapshot)
    titles = {issue.title for issue in issues}
    assert any("OCR" in t for t in titles)
    assert any("ASR" in t for t in titles)
    for issue in issues:
        assert issue.principle == "H10"
        assert issue.evidence_refs == [calm_screenshot.id]


def test_jargon_skips_when_tooltip_provided(calm_screenshot: ScreenshotRef) -> None:
    snapshot = DomSnapshot(
        screenshot_id=calm_screenshot.id,
        nodes=[DomNode(tag="span", text="OCR 解析", attrs={"title": "光学字符识别"})],
    )
    assert rule_jargon_without_explanation(calm_screenshot, snapshot) == []


# ---------------------------------------------------------------------------
# rule_form_field_missing_label
# ---------------------------------------------------------------------------


def test_form_field_missing_label_hits(
    calm_screenshot: ScreenshotRef,
    naked_form_snapshot: DomSnapshot,
) -> None:
    issues = rule_form_field_missing_label(calm_screenshot, naked_form_snapshot)
    assert len(issues) == 2
    assert all(issue.principle == "H6" for issue in issues)


def test_form_field_with_label_passes(calm_screenshot: ScreenshotRef) -> None:
    snapshot = DomSnapshot(
        screenshot_id=calm_screenshot.id,
        nodes=[DomNode(tag="input", placeholder="请输入用户名")],
    )
    assert rule_form_field_missing_label(calm_screenshot, snapshot) == []


# ---------------------------------------------------------------------------
# rule_missing_error_message
# ---------------------------------------------------------------------------


def test_missing_error_message_hits(failure_screenshot: ScreenshotRef) -> None:
    snapshot = DomSnapshot(screenshot_id=failure_screenshot.id, nodes=[])
    issues = rule_missing_error_message(failure_screenshot, snapshot)
    assert len(issues) == 1
    assert issues[0].principle == "H9"
    assert issues[0].severity == "critical"


def test_missing_error_message_misses_when_alert_present(
    failure_screenshot: ScreenshotRef,
) -> None:
    snapshot = DomSnapshot(
        screenshot_id=failure_screenshot.id,
        nodes=[DomNode(tag="div", role="alert", text="导入失败：列名缺失")],
    )
    assert rule_missing_error_message(failure_screenshot, snapshot) == []


# ---------------------------------------------------------------------------
# run_rules — integration across rules
# ---------------------------------------------------------------------------


def test_run_rules_aggregates_across_screenshots(
    loading_screenshot: ScreenshotRef,
    failure_screenshot: ScreenshotRef,
) -> None:
    dom = [
        DomSnapshot(screenshot_id=loading_screenshot.id, nodes=[]),
        DomSnapshot(screenshot_id=failure_screenshot.id, nodes=[]),
    ]
    issues = run_rules([loading_screenshot, failure_screenshot], dom)
    principles = {issue.principle for issue in issues}
    assert {"H1", "H9"}.issubset(principles)


def test_run_rules_returns_empty_without_dom(
    calm_screenshot: ScreenshotRef,
) -> None:
    assert run_rules([calm_screenshot], None) == []
