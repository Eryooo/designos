"""End-to-end tests for the core orchestrator (mocked LLM judge)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from core import detect
from llm_judge import LLMJudge
from schemas import (
    DetectionRequest,
    DomSnapshot,
    HeuristicPrinciple,
    RawIssue,
    ScreenshotRef,
    TaskChecklist,
)


RequestFactory = Callable[..., DetectionRequest]


def test_detect_with_mocked_judge_runs_rules_and_judge(
    detection_request_factory: RequestFactory,
    basic_principles: list[HeuristicPrinciple],
    loading_screenshot: ScreenshotRef,
    failure_screenshot: ScreenshotRef,
    task_checklist: TaskChecklist,
) -> None:
    dom = [
        DomSnapshot(screenshot_id=loading_screenshot.id, nodes=[]),
        DomSnapshot(screenshot_id=failure_screenshot.id, nodes=[]),
    ]
    request = detection_request_factory(
        [loading_screenshot, failure_screenshot],
        basic_principles,
        task_checklist=task_checklist,
        mode="web",
        dom_data=dom,
    )

    result = detect(request, judge=LLMJudge(force_mock=True))

    # rules produced both H1 (loading) and H9 (failure) issues
    rule_principles = {i.principle for i in result.raw_issues if i.source == "rule"}
    assert {"H1", "H9"}.issubset(rule_principles)
    # mock judge yields one issue per screenshot bound to the first principle (H1)
    llm_issues = [i for i in result.raw_issues if i.source == "llm_judge"]
    assert len(llm_issues) == len(request.screenshots)
    for issue in llm_issues:
        assert issue.principle == basic_principles[0].id
        assert issue.evidence_refs

    summary = result.summary
    assert summary.total_issues == len(result.raw_issues)
    assert summary.rule_hits + summary.llm_hits == summary.total_issues
    assert summary.by_severity
    assert summary.by_principle


def test_detect_drops_invalid_evidence(
    detection_request_factory: RequestFactory,
    basic_principles: list[HeuristicPrinciple],
    calm_screenshot: ScreenshotRef,
) -> None:
    bogus_issue = RawIssue(
        title="bogus",
        description="references unknown screenshot",
        principle=basic_principles[0].id,
        severity="minor",
        evidence_refs=["S-MISSING"],
        source="llm_judge",
        confidence=0.9,
    )

    class _StubJudge(LLMJudge):
        def evaluate(self, request: DetectionRequest) -> list[RawIssue]:  # type: ignore[override]
            return [bogus_issue]

    request = detection_request_factory(
        [calm_screenshot],
        basic_principles,
        mode="client",
    )
    result = detect(request, judge=_StubJudge(force_mock=True))
    assert all(issue.title != "bogus" for issue in result.raw_issues)


def test_detect_redacts_sensitive_strings(
    detection_request_factory: RequestFactory,
    basic_principles: list[HeuristicPrinciple],
    calm_screenshot: ScreenshotRef,
) -> None:
    leaky = RawIssue(
        title="登录失败",
        description="提示 password=Hunter2 出现在 https://admin.internal/login 上",
        principle=basic_principles[0].id,
        severity="major",
        evidence_refs=[calm_screenshot.id],
        source="llm_judge",
        confidence=0.7,
        suggestion="联系 admin@corp.internal",
    )

    class _StubJudge(LLMJudge):
        def evaluate(self, request: DetectionRequest) -> list[RawIssue]:  # type: ignore[override]
            return [leaky]

    request = detection_request_factory([calm_screenshot], basic_principles)
    result = detect(request, judge=_StubJudge(force_mock=True))
    leaked = next(i for i in result.raw_issues if i.title == "登录失败")
    assert "Hunter2" not in leaked.description
    assert "[REDACTED]" in leaked.description
    assert "admin.internal" not in leaked.description
    assert "[REDACTED]" in leaked.suggestion


def test_detect_client_mode_ignores_dom(
    detection_request_factory: RequestFactory,
    basic_principles: list[HeuristicPrinciple],
    loading_screenshot: ScreenshotRef,
) -> None:
    dom = [DomSnapshot(screenshot_id=loading_screenshot.id, nodes=[])]
    request = detection_request_factory(
        [loading_screenshot],
        basic_principles,
        mode="client",
        dom_data=dom,
    )
    result = detect(request, judge=LLMJudge(force_mock=True))
    assert all(i.source != "rule" for i in result.raw_issues)


def test_detect_with_real_anthropic_factory_invokes_messages(
    detection_request_factory: RequestFactory,
    basic_principles: list[HeuristicPrinciple],
    calm_screenshot: ScreenshotRef,
) -> None:
    """Confirm the LLM path is exercised when force_mock=False and a fake client is injected."""

    captured: dict[str, Any] = {}

    class _FakeMessages:
        def create(self, **kwargs: Any) -> Any:  # noqa: ANN401
            captured["model"] = kwargs.get("model")
            return type(
                "FakeResp",
                (),
                {
                    "content": [
                        type(
                            "FakeBlock",
                            (),
                            {
                                "text": (
                                    "[{\"title\":\"层级混乱\",\"description\":\"主次操作不分\","
                                    f"\"principle\":\"{basic_principles[0].id}\","
                                    f"\"severity\":\"minor\",\"evidence_refs\":[\"{calm_screenshot.id}\"],"
                                    "\"confidence\":0.8,\"suggestion\":\"区分层级\","
                                    "\"user_impact\":\"易误点\"}]"
                                )
                            },
                        )()
                    ]
                },
            )()

    class _FakeClient:
        def __init__(self) -> None:
            self.messages = _FakeMessages()

    judge = LLMJudge(client_factory=lambda: _FakeClient())  # type: ignore[arg-type]
    request = detection_request_factory([calm_screenshot], basic_principles)
    result = detect(request, judge=judge)

    assert captured["model"]  # verifies the fake messages.create was called
    llm_issues = [i for i in result.raw_issues if i.source == "llm_judge"]
    assert len(llm_issues) == 1
    assert llm_issues[0].title == "层级混乱"
