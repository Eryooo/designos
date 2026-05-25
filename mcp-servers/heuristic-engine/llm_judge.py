"""LLM vision-judge for heuristic detection.

Wraps the Anthropic SDK to send each screenshot together with the principle
catalogue, task context, and the skill's evaluation constitution; expects a
JSON list of :class:`RawIssue`-shaped dicts back.

The client is fully mockable:

* Setting ``HEURISTIC_ENGINE_MOCK=1`` skips the API entirely and returns a
  deterministic, principle-aware fixture issue per screenshot.
* The :class:`LLMJudge` constructor accepts an injected ``client_factory``
  callable used by the unit tests to swap in a fake Anthropic client without
  monkey-patching modules.

Wire format the LLM is asked to honour:

```
[
  {
    "title": "...",
    "description": "...",
    "principle": "H1",
    "severity": "major",
    "evidence_refs": ["S-001"],
    "confidence": 0.7,
    "suggestion": "...",
    "user_impact": "..."
  }
]
```
"""

from __future__ import annotations

import base64
import json
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any, Protocol, cast

from pydantic import ValidationError
from schemas import (
    DetectionRequest,
    HeuristicPrinciple,
    RawIssue,
    ScreenshotRef,
    SeverityLevel,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


MOCK_ENV_VAR: str = "HEURISTIC_ENGINE_MOCK"
DEFAULT_MODEL: str = "claude-opus-4-7"
SYSTEM_PROMPT_TEMPLATE: str = """你是 DesignOS UXEval 的启发式视觉评审引擎。

你必须严格遵守如下评估宪法：
{constitution}

附加铁律：
1. 每条 issue 的 evidence_refs 必须从给定 screenshots 的 id 中选取，且不能为空。
2. severity 必须是 critical / major / minor / suggestion 之一。
3. principle 必须是给定 principles 中的 id。
4. 不要把功能存在与否当作主要体验问题，关注体验、交互、信息架构和反馈。
5. 不要输出 PRD 没要求且明显属于推断的功能缺失。
6. 不要输出账号、密码、内部 URL、内网 IP 等敏感信息。

输出严格的 JSON 数组（不要 markdown，不要解释文字），每个元素结构：
[
  {
    "title": "短摘要",
    "description": "用户视角的具体描述",
    "principle": "对应原则 id",
    "severity": "critical|major|minor|suggestion",
    "evidence_refs": ["screenshot id"],
    "confidence": 0.0-1.0 浮点,
    "suggestion": "可执行修复建议",
    "user_impact": "用户层面的影响"
  }
]
"""


def _render_system_prompt(constitution: str) -> str:
    """Render the system prompt without leaning on ``str.format`` (avoids brace
    collisions in user-provided constitutions).
    """

    payload = constitution.strip() or "（未提供宪法，按默认体验评估口径执行。）"
    return SYSTEM_PROMPT_TEMPLATE.replace("{constitution}", payload)


# ---------------------------------------------------------------------------
# Anthropic client protocol (kept narrow so tests can inject doubles)
# ---------------------------------------------------------------------------


class _MessagesAPI(Protocol):
    """Subset of the Anthropic ``messages`` API surface we depend on."""

    def create(self, **kwargs: Any) -> Any:
        """Invoke the messages.create endpoint."""


class _AnthropicLike(Protocol):
    """Minimal Anthropic client protocol used by :class:`LLMJudge`."""

    messages: _MessagesAPI


ClientFactory = Callable[[], _AnthropicLike]


# ---------------------------------------------------------------------------
# Public errors
# ---------------------------------------------------------------------------


class LLMJudgeError(RuntimeError):
    """Raised when the LLM judge cannot produce a parsable response."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _is_mock_enabled() -> bool:
    """Return True when the env var requests mock mode."""

    return os.environ.get(MOCK_ENV_VAR, "").strip() in {"1", "true", "TRUE", "yes"}


def _encode_image(path: Path) -> tuple[str, str]:
    """Read ``path`` and return ``(media_type, base64_data)``.

    Falls back to ``image/png`` when the suffix is unknown.
    """

    suffix = path.suffix.lower().lstrip(".")
    media_type = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
        "gif": "image/gif",
    }.get(suffix, "image/png")
    data = base64.standard_b64encode(path.read_bytes()).decode("ascii")
    return media_type, data


def _format_principles(principles: list[HeuristicPrinciple]) -> str:
    """Render principles as compact bullet list for the LLM."""

    return "\n".join(f"- {p.id}: {p.name} — {p.description}" for p in principles)


def _format_tasks(request: DetectionRequest) -> str:
    """Render task checklist as compact context string."""

    if not request.task_checklist.tasks:
        return "（未提供任务清单）"
    lines = []
    if request.task_checklist.journey_summary:
        lines.append(f"旅程概要：{request.task_checklist.journey_summary}")
    for task in request.task_checklist.tasks:
        lines.append(f"- {task.id} [{task.journey_stage}] {task.title}：{task.description}")
    return "\n".join(lines)


def _format_screenshots(screenshots: list[ScreenshotRef]) -> str:
    """Render screenshot manifest for the LLM prompt."""

    return "\n".join(
        f"- {s.id} flow={s.flow or '-'} region={s.region or '-'} url={s.page_url or '-'}"
        for s in screenshots
    )


def _coerce_severity(raw: object) -> SeverityLevel:
    """Coerce arbitrary values from the LLM into a valid severity."""

    if isinstance(raw, str) and raw in ("critical", "major", "minor", "suggestion"):
        return cast(SeverityLevel, raw)
    return "minor"


def _validate_issue_dict(
    payload: dict[str, Any],
    valid_screenshot_ids: set[str],
    valid_principle_ids: set[str],
) -> RawIssue | None:
    """Validate one LLM-emitted dict and produce a :class:`RawIssue`.

    Returns ``None`` when the payload is unsalvageable; the caller decides
    whether to log + skip or raise.
    """

    evidence_raw = payload.get("evidence_refs") or []
    if not isinstance(evidence_raw, list):
        return None
    evidence = [ref for ref in evidence_raw if isinstance(ref, str) and ref in valid_screenshot_ids]
    if not evidence:
        return None
    principle = payload.get("principle")
    if not isinstance(principle, str) or principle not in valid_principle_ids:
        return None
    try:
        confidence_raw = float(payload.get("confidence", 0.5))
    except (TypeError, ValueError):
        confidence_raw = 0.5
    try:
        return RawIssue(
            title=str(payload.get("title", "")).strip() or "未命名启发式问题",
            description=str(payload.get("description", "")).strip(),
            principle=principle,
            severity=_coerce_severity(payload.get("severity")),
            evidence_refs=evidence,
            source="llm_judge",
            confidence=max(0.0, min(1.0, confidence_raw)),
            suggestion=str(payload.get("suggestion", "")),
            user_impact=str(payload.get("user_impact", "")),
        )
    except ValidationError:
        return None


def _extract_text(response: Any) -> str:
    """Pull the first text block out of an Anthropic messages response."""

    content = getattr(response, "content", None)
    if isinstance(content, list):
        for block in content:
            text = getattr(block, "text", None)
            if isinstance(text, str):
                return text
            if isinstance(block, dict) and isinstance(block.get("text"), str):
                return cast(str, block["text"])
    if isinstance(response, dict):
        blocks = response.get("content", [])
        if isinstance(blocks, list):
            for block in blocks:
                if isinstance(block, dict) and isinstance(block.get("text"), str):
                    return cast(str, block["text"])
    raise LLMJudgeError("LLM response missing text content")


# ---------------------------------------------------------------------------
# Mock judge — deterministic, principle-aware fixture for offline tests
# ---------------------------------------------------------------------------


def _mock_issues_for(screenshot: ScreenshotRef, principles: list[HeuristicPrinciple]) -> list[RawIssue]:
    """Return a deterministic fixture issue per screenshot.

    Picks the first principle in scope and produces a single low-severity
    issue. Stable enough for snapshot tests; explicit so the contract with the
    real LLM is mirrored 1:1.
    """

    if not principles:
        return []
    principle = principles[0]
    return [
        RawIssue(
            title=f"[mock] {principle.name} 待复核",
            description=(
                f"Mock LLM judge：在截图 {screenshot.id} 上观察到 {principle.name} 相关风险，"
                "请人工复核后再决定是否纳入正式报告。"
            ),
            principle=principle.id,
            severity="suggestion",
            evidence_refs=[screenshot.id],
            source="llm_judge",
            confidence=0.4,
            suggestion="切换到真实 LLM judge 后复核此条建议。",
            user_impact="Mock 模式下的占位条目，仅用于流程联调。",
        )
    ]


# ---------------------------------------------------------------------------
# LLM judge implementation
# ---------------------------------------------------------------------------


class LLMJudge:
    """Visual heuristic judge backed by an Anthropic vision model.

    Args:
        model: Anthropic model id (defaults to ``claude-opus-4-7``).
        client_factory: Optional callable returning an Anthropic-like client;
            primarily used by tests. When omitted, the real ``anthropic.Anthropic``
            client is built lazily.
        force_mock: When True, always returns deterministic mock issues
            regardless of env vars. Useful for unit tests.
        max_tokens: Output cap forwarded to ``messages.create``.
    """

    def __init__(
        self,
        *,
        model: str = DEFAULT_MODEL,
        client_factory: ClientFactory | None = None,
        force_mock: bool = False,
        max_tokens: int = 2048,
    ) -> None:
        self._model = model
        self._client_factory = client_factory
        self._force_mock = force_mock
        self._max_tokens = max_tokens

    # -- public API ---------------------------------------------------------

    def evaluate(self, request: DetectionRequest) -> list[RawIssue]:
        """Score every screenshot against the principle catalogue.

        Args:
            request: Validated detection request.

        Returns:
            All :class:`RawIssue` objects emitted by the judge, validated and
            constitution-compliant.
        """

        if self._force_mock or _is_mock_enabled():
            return [
                issue
                for screenshot in request.screenshots
                for issue in _mock_issues_for(screenshot, request.principles)
            ]

        client = self._client()
        valid_screenshot_ids = {s.id for s in request.screenshots}
        valid_principle_ids = {p.id for p in request.principles}
        out: list[RawIssue] = []
        for screenshot in request.screenshots:
            try:
                response = self._invoke(client, request, screenshot)
                text = _extract_text(response)
                payloads = self._parse_json(text)
                for payload in payloads:
                    issue = _validate_issue_dict(payload, valid_screenshot_ids, valid_principle_ids)
                    if issue is not None:
                        out.append(issue)
            except (LLMJudgeError, Exception) as exc:
                import logging
                logging.getLogger(__name__).warning(
                    "LLM judge failed for %s: %s", screenshot.id, str(exc)[:200]
                )
                continue
        return out

    # -- internals ----------------------------------------------------------

    def _client(self) -> _AnthropicLike:
        """Lazy-build the Anthropic client using the injected factory."""

        if self._client_factory is not None:
            return self._client_factory()
        try:
            from anthropic import Anthropic  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - covered by mock path
            raise LLMJudgeError(
                "anthropic SDK is required when HEURISTIC_ENGINE_MOCK is unset"
            ) from exc
        return cast(_AnthropicLike, Anthropic())

    def _invoke(
        self,
        client: _AnthropicLike,
        request: DetectionRequest,
        screenshot: ScreenshotRef,
    ) -> Any:
        """Send a single screenshot evaluation request to the LLM."""

        system = _render_system_prompt(request.constitution)
        user_text = (
            "Principles in scope:\n"
            f"{_format_principles(request.principles)}\n\n"
            "Screenshots manifest (id is what you cite in evidence_refs):\n"
            f"{_format_screenshots(request.screenshots)}\n\n"
            "Task context:\n"
            f"{_format_tasks(request)}\n\n"
            f"Now evaluate screenshot id={screenshot.id} (flow={screenshot.flow or '-'},"
            f" region={screenshot.region or '-'}). Output JSON array only."
        )

        # Build content blocks: use image for real screenshots, text for .md descriptions.
        screenshot_path = Path(screenshot.path)
        content_blocks: list[dict[str, Any]] = []
        if screenshot_path.suffix.lower() in (".md", ".txt"):
            try:
                text_content = screenshot_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                text_content = "(unable to read file)"
            content_blocks.append({
                "type": "text",
                "text": f"[Screenshot {screenshot.id} — text description]:\n{text_content[:2000]}",
            })
        else:
            media_type, data = _encode_image(screenshot_path)
            content_blocks.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": data,
                },
            })
        content_blocks.append({"type": "text", "text": user_text})

        return client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=system,
            messages=[
                {
                    "role": "user",
                    "content": content_blocks,
                }
            ],
        )

    @staticmethod
    def _parse_json(text: str) -> list[dict[str, Any]]:
        """Parse the LLM text payload as a JSON array of issue dicts."""

        cleaned = text.strip()
        if cleaned.startswith("```"):
            # strip optional ```json fences
            cleaned = cleaned.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise LLMJudgeError(f"LLM judge returned invalid JSON: {exc}") from exc
        if not isinstance(data, list):
            raise LLMJudgeError("LLM judge response must be a JSON array")
        return [item for item in data if isinstance(item, dict)]


__all__ = [
    "DEFAULT_MODEL",
    "LLMJudge",
    "LLMJudgeError",
    "MOCK_ENV_VAR",
    "SYSTEM_PROMPT_TEMPLATE",
]
