"""Deterministic rule engine for heuristic detection.

Each rule is a pure function operating on the request payload (screenshot
ref + optional DOM snapshot) and producing zero or more :class:`RawIssue`
objects. Rules cover the deterministic heuristics from the reference scripts
in ``trae_projects/design-review/scripts/build_heuristic_*.mjs``:

* missing system-status indicators (H1)
* technical jargon without explanation (H2 / H10)
* form fields missing label / placeholder (H6 / B3)
* missing error messages on failure pages (H9)
* operation-button overload on a single row (H8 / B4)

Adding a rule:

1. Implement a function ``rule_<short_name>(...) -> list[RawIssue]``.
2. Register it in :data:`RULES`.
3. Cover the rule in ``tests/test_rules.py`` with a hit + miss case.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from schemas import (
    DomNode,
    DomSnapshot,
    RawIssue,
    ScreenshotRef,
    SeverityLevel,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


# Technical jargon vocabulary observed in the legacy outputs that should be
# explained to non-technical users. Kept conservative; the LLM judge picks up
# the long tail.
TECHNICAL_TERMS: tuple[str, ...] = (
    "OCR",
    "ASR",
    "Kreuzberg",
    "Embedding",
    "RAG",
    "JSON",
    "JWT",
    "API",
    "SDK",
    "TLS",
    "SSE",
    "Webhook",
    "DSL",
    "URI",
    "URL",
    "regex",
    "Cron",
)

# Action-bearing tag set used by the button-overload rule.
ACTION_TAGS: frozenset[str] = frozenset({"button", "a"})

# Severity defaults — rules can override locally.
DEFAULT_RULE_CONFIDENCE: float = 0.85


def _node_label_text(node: DomNode) -> str:
    """Aggregate every label-bearing field into a single string for matching."""

    return " ".join(
        part
        for part in (node.text, node.aria_label, node.placeholder, node.attrs.get("title", ""))
        if part
    ).strip()


def _has_loading_indicator_node(node: DomNode) -> bool:
    """Return True when a node looks like a loading / progress indicator."""

    role = node.role.lower()
    if role in {"progressbar", "status"}:
        return True
    classes = " ".join(node.classes).lower()
    return any(token in classes for token in ("loading", "spinner", "progress", "skeleton"))


# ---------------------------------------------------------------------------
# Rule implementations
# ---------------------------------------------------------------------------


def rule_missing_status_indicator(
    screenshot: ScreenshotRef,
    snapshot: DomSnapshot | None,
) -> list[RawIssue]:
    """Flag long-running flows that lack a status indicator (H1).

    Triggered when the flow label hints at an async operation
    (``loading``/``submit``/``processing``/``running``) yet the snapshot
    contains neither an explicit loading flag nor any progressbar-like node.
    """

    if snapshot is None:
        return []
    flow_signal = (screenshot.flow + " " + screenshot.region).lower()
    keywords = ("loading", "submit", "processing", "running", "运行", "提交", "扫描", "加载")
    if not any(keyword in flow_signal for keyword in keywords):
        return []
    if snapshot.has_loading_indicator:
        return []
    if any(_has_loading_indicator_node(node) for node in snapshot.nodes):
        return []

    return [
        RawIssue(
            title="状态反馈缺失",
            description=(
                f"{screenshot.flow or screenshot.id} 涉及长耗时操作，但截图与 DOM "
                "中均未发现加载/进度指示器，用户无法判断系统是否在处理。"
            ),
            principle="H1",
            severity="major",
            evidence_refs=[screenshot.id],
            source="rule",
            confidence=DEFAULT_RULE_CONFIDENCE,
            suggestion="为长耗时操作补充加载/进度反馈，运行中状态需要可视化。",
            user_impact="用户无法判断系统是否在响应，可能误以为操作未生效而重复触发。",
        )
    ]


def rule_action_button_overload(
    screenshot: ScreenshotRef,
    snapshot: DomSnapshot | None,
) -> list[RawIssue]:
    """Flag rows / cards that expose too many action buttons at once (H8 / B4).

    Heuristic: if the snapshot shows >= 5 action elements (button/link) and at
    least 3 of them carry distinct action labels, the row likely exceeds a
    healthy operation density.
    """

    if snapshot is None:
        return []
    actions = [
        node
        for node in snapshot.nodes
        if node.tag.lower() in ACTION_TAGS and _node_label_text(node)
    ]
    if len(actions) < 5:
        return []
    distinct = {_node_label_text(node) for node in actions}
    if len(distinct) < 3:
        return []

    return [
        RawIssue(
            title="操作按钮过多",
            description=(
                f"{screenshot.flow or screenshot.id} 单个区域出现 {len(actions)} 个操作入口，"
                "主操作与次操作未拉开层级，容易产生误点和阅读负担。"
            ),
            principle="B4",
            severity="major",
            evidence_refs=[screenshot.id],
            source="rule",
            confidence=DEFAULT_RULE_CONFIDENCE,
            suggestion="保留 1 个主操作 + 1-2 个次操作，其余收纳到“更多”菜单。",
            user_impact="用户难以快速定位主操作，易误触发危险动作。",
        )
    ]


def rule_jargon_without_explanation(
    screenshot: ScreenshotRef,
    snapshot: DomSnapshot | None,
) -> list[RawIssue]:
    """Flag visible technical jargon without nearby help text (H2 / H10)."""

    if snapshot is None:
        return []
    issues: list[RawIssue] = []
    seen: set[str] = set()
    for node in snapshot.nodes:
        label = _node_label_text(node)
        if not label:
            continue
        for term in TECHNICAL_TERMS:
            if term.lower() not in label.lower() or term in seen:
                continue
            has_help = bool(node.attrs.get("title")) or "tooltip" in " ".join(node.classes).lower()
            if has_help:
                continue
            seen.add(term)
            issues.append(
                RawIssue(
                    title=f"技术术语缺乏说明：{term}",
                    description=(
                        f"{screenshot.flow or screenshot.id} 中出现技术术语 “{term}”，"
                        "但未配套提示或解释，非技术背景用户难以理解含义。"
                    ),
                    principle="H10",
                    severity="minor",
                    evidence_refs=[screenshot.id],
                    source="rule",
                    confidence=DEFAULT_RULE_CONFIDENCE,
                    suggestion=f"为 “{term}” 添加 tooltip / 帮助说明，必要时改用业务术语。",
                    user_impact="用户需要靠经验或外部资料理解术语，配置易出错。",
                )
            )
    return issues


def rule_form_field_missing_label(
    screenshot: ScreenshotRef,
    snapshot: DomSnapshot | None,
) -> list[RawIssue]:
    """Flag form inputs that lack both a placeholder and a label (H6 / B3)."""

    if snapshot is None:
        return []
    issues: list[RawIssue] = []
    for node in snapshot.nodes:
        if node.tag.lower() not in {"input", "textarea", "select"}:
            continue
        node_type = node.attrs.get("type", "").lower()
        if node_type in {"hidden", "submit", "button"}:
            continue
        has_label = bool(node.aria_label or node.placeholder or node.attrs.get("name"))
        if has_label:
            continue
        issues.append(
            RawIssue(
                title="表单字段缺少标签",
                description=(
                    f"{screenshot.flow or screenshot.id} 中存在未标注的表单字段（"
                    f"tag={node.tag}, type={node_type or 'text'}），用户必须依靠"
                    "上下文猜测字段含义。"
                ),
                principle="H6",
                severity="major",
                evidence_refs=[screenshot.id],
                source="rule",
                confidence=DEFAULT_RULE_CONFIDENCE,
                suggestion="为字段补充 label / aria-label / placeholder，并满足可访问性。",
                user_impact="屏幕阅读器无法朗读字段含义，普通用户也容易填错。",
            )
        )
    return issues


def rule_missing_error_message(
    screenshot: ScreenshotRef,
    snapshot: DomSnapshot | None,
) -> list[RawIssue]:
    """Flag failure-context flows that show no error message element (H9)."""

    if snapshot is None:
        return []
    flow_signal = (screenshot.flow + " " + screenshot.region).lower()
    failure_keywords = ("error", "fail", "失败", "异常", "错误")
    if not any(keyword in flow_signal for keyword in failure_keywords):
        return []
    if snapshot.has_error_message:
        return []
    has_error_node = any(
        "error" in " ".join(node.classes).lower() or node.role.lower() == "alert"
        for node in snapshot.nodes
    )
    if has_error_node:
        return []

    return [
        RawIssue(
            title="错误消息缺失",
            description=(
                f"{screenshot.flow or screenshot.id} 处于失败/异常上下文，但页面未提供"
                "可见的错误消息或恢复建议，用户无法定位问题。"
            ),
            principle="H9",
            severity="critical",
            evidence_refs=[screenshot.id],
            source="rule",
            confidence=DEFAULT_RULE_CONFIDENCE,
            suggestion="使用普通语言说明错误原因，并给出可执行的恢复路径。",
            user_impact="用户在失败状态下无路可走，信任度急剧下降。",
        )
    ]


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


RuleFn = Callable[[ScreenshotRef, DomSnapshot | None], list[RawIssue]]


@dataclass(frozen=True)
class Rule:
    """Metadata-attached rule entry."""

    name: str
    principle: str
    default_severity: SeverityLevel
    fn: RuleFn


RULES: tuple[Rule, ...] = (
    Rule("missing_status_indicator", "H1", "major", rule_missing_status_indicator),
    Rule("action_button_overload", "B4", "major", rule_action_button_overload),
    Rule("jargon_without_explanation", "H10", "minor", rule_jargon_without_explanation),
    Rule("form_field_missing_label", "H6", "major", rule_form_field_missing_label),
    Rule("missing_error_message", "H9", "critical", rule_missing_error_message),
)


def run_rules(
    screenshots: list[ScreenshotRef],
    dom_data: list[DomSnapshot] | None,
) -> list[RawIssue]:
    """Execute every registered rule across all screenshots.

    Args:
        screenshots: All screenshots in the request.
        dom_data: Optional DOM snapshots (web mode only); each snapshot is
            looked up by ``screenshot_id``.

    Returns:
        Flattened list of issues raised by the rule engine.
    """

    snapshot_by_id: dict[str, DomSnapshot] = (
        {snap.screenshot_id: snap for snap in dom_data} if dom_data else {}
    )
    out: list[RawIssue] = []
    for screenshot in screenshots:
        snapshot = snapshot_by_id.get(screenshot.id)
        for rule in RULES:
            out.extend(rule.fn(screenshot, snapshot))
    return out


__all__ = [
    "ACTION_TAGS",
    "DEFAULT_RULE_CONFIDENCE",
    "RULES",
    "Rule",
    "RuleFn",
    "TECHNICAL_TERMS",
    "rule_action_button_overload",
    "rule_form_field_missing_label",
    "rule_jargon_without_explanation",
    "rule_missing_error_message",
    "rule_missing_status_indicator",
    "run_rules",
]
