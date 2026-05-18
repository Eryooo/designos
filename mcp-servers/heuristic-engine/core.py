"""Core detection orchestrator (pure functions, no MCP dependencies).

Combines the deterministic rule engine with the LLM vision judge, enforces
the constitution invariants (non-empty evidence, valid severity, sensitive-
data redaction) and assembles the aggregate :class:`DetectionSummary`.

Constitution invariants enforced here:

1. Every issue's ``evidence_refs`` is non-empty and references a known
   ``ScreenshotRef.id`` from the request.
2. ``severity`` belongs to the allowed enum.
3. ``principle`` belongs to the requested principle catalogue.
4. ``description`` / ``title`` / ``suggestion`` are stripped of obvious
   sensitive markers (account names, password mentions, internal URLs).
5. Web-mode requests with declared ``dom_data`` only see DOM snapshots that
   match a known screenshot id.
"""

from __future__ import annotations

import re

from llm_judge import LLMJudge
from rules import run_rules
from schemas import (
    DetectionRequest,
    DetectionResult,
    DetectionSummary,
    DomSnapshot,
    RawIssue,
    SeverityLevel,
)

# ---------------------------------------------------------------------------
# Sensitive-data redaction
# ---------------------------------------------------------------------------


_VALID_SEVERITIES: frozenset[SeverityLevel] = frozenset(
    {"critical", "major", "minor", "suggestion"}
)

# Patterns kept conservative to avoid over-eager scrubbing of legitimate
# product copy. Escalation should happen in Sanitiser, not here.
_SENSITIVE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"password\s*[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"密码\s*[:：]\s*\S+"),
    re.compile(r"\b(?:10|172|192)\.(?:\d{1,3}\.){2}\d{1,3}\b"),
    re.compile(r"https?://(?:[\w-]+\.)*(?:internal|intranet|local)(?:[/?\s]|$)", re.IGNORECASE),
    re.compile(r"\b[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\.)*(?:internal|intranet|local)\b", re.IGNORECASE),
)


def _redact(text: str) -> str:
    """Replace sensitive substrings with ``[REDACTED]``.

    Args:
        text: Source text emitted by a rule or LLM.

    Returns:
        Text with conservative redactions applied; empty input is returned
        unchanged.
    """

    if not text:
        return text
    redacted = text
    for pattern in _SENSITIVE_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def _scrub_issue(issue: RawIssue) -> RawIssue:
    """Apply :func:`_redact` to every free-form field on an issue."""

    return issue.model_copy(
        update={
            "title": _redact(issue.title),
            "description": _redact(issue.description),
            "suggestion": _redact(issue.suggestion),
            "user_impact": _redact(issue.user_impact),
        }
    )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _filter_dom_data(
    dom_data: list[DomSnapshot] | None,
    valid_screenshot_ids: set[str],
) -> list[DomSnapshot] | None:
    """Drop DOM snapshots that do not match any screenshot id."""

    if dom_data is None:
        return None
    return [snap for snap in dom_data if snap.screenshot_id in valid_screenshot_ids]


def _validate_issue(
    issue: RawIssue,
    valid_screenshot_ids: set[str],
    valid_principle_ids: set[str],
) -> RawIssue | None:
    """Return ``issue`` when it satisfies the constitution, else ``None``."""

    if not issue.evidence_refs:
        return None
    if not all(ref in valid_screenshot_ids for ref in issue.evidence_refs):
        return None
    if issue.severity not in _VALID_SEVERITIES:
        return None
    if issue.principle not in valid_principle_ids:
        return None
    return issue


def _summarise(issues: list[RawIssue]) -> DetectionSummary:
    """Build a :class:`DetectionSummary` from a flattened issue list."""

    by_severity: dict[str, int] = {}
    by_principle: dict[str, int] = {}
    rule_hits = 0
    llm_hits = 0
    for issue in issues:
        by_severity[issue.severity] = by_severity.get(issue.severity, 0) + 1
        by_principle[issue.principle] = by_principle.get(issue.principle, 0) + 1
        if issue.source == "rule":
            rule_hits += 1
        else:
            llm_hits += 1
    return DetectionSummary(
        total_issues=len(issues),
        by_severity=by_severity,
        by_principle=by_principle,
        rule_hits=rule_hits,
        llm_hits=llm_hits,
    )


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------


def detect(
    request: DetectionRequest,
    *,
    judge: LLMJudge | None = None,
) -> DetectionResult:
    """Run the rule engine + LLM judge over a detection request.

    Args:
        request: Validated detection request payload.
        judge: Optional :class:`LLMJudge`; when omitted a default instance is
            constructed (which respects ``HEURISTIC_ENGINE_MOCK``).

    Returns:
        :class:`DetectionResult` with sanitised issues and aggregate summary.
    """

    valid_screenshot_ids = {s.id for s in request.screenshots}
    valid_principle_ids = {p.id for p in request.principles}
    dom_data = (
        _filter_dom_data(request.dom_data, valid_screenshot_ids)
        if request.mode == "web"
        else None
    )

    rule_issues = run_rules(request.screenshots, dom_data)

    judge_impl = judge if judge is not None else LLMJudge()
    llm_issues = judge_impl.evaluate(request)

    combined: list[RawIssue] = []
    for issue in (*rule_issues, *llm_issues):
        validated = _validate_issue(issue, valid_screenshot_ids, valid_principle_ids)
        if validated is None:
            continue
        combined.append(_scrub_issue(validated))

    summary = _summarise(combined)
    return DetectionResult(raw_issues=combined, summary=summary)


__all__ = [
    "detect",
]
