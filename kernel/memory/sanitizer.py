"""Sanitiser used before any organisation-memory propose.

Detects common PII patterns (phone numbers, emails, internal URLs, API keys)
and returns the list of violations. Callers must reject the payload when the
list is non-empty.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

from kernel.contracts.enums import ErrorCode
from kernel.errors import SanitizerError

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

_PHONE_CN = re.compile(r"(?<!\d)(?:\+?86[\s-]?)?1[3-9]\d{9}(?!\d)")
_PHONE_INTL = re.compile(r"\+\d{1,3}[\s-]?\d{6,14}")
_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_INTERNAL_URL = re.compile(
    r"https?://(?:[A-Za-z0-9.-]+\.)*"
    r"(?:internal|local|corp|intra|staging|dev)"
    r"(?:[:/][\w./-]*)?",
    re.IGNORECASE,
)
_API_KEYS: list[tuple[str, re.Pattern[str]]] = [
    ("anthropic_key", re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}")),
    ("openai_key", re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}")),
    ("deepseek_key", re.compile(r"sk-[A-Za-z0-9]{32,}")),
    ("aws_secret", re.compile(r"(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])")),
    ("github_token", re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}")),
]

_DETECTORS: list[tuple[str, re.Pattern[str]]] = [
    ("phone_cn", _PHONE_CN),
    ("phone_intl", _PHONE_INTL),
    ("email", _EMAIL),
    ("internal_url", _INTERNAL_URL),
    *_API_KEYS,
]


class Sanitizer:
    """Runs a pre-defined regex battery over JSON-serialisable payloads."""

    def scan(self, payload: Any) -> list[str]:
        """Return human-readable hits; empty list means clean."""
        text: str = _flatten(payload)
        hits: list[str] = []
        for label, pattern in _DETECTORS:
            for match in pattern.findall(text):
                hits.append(f"{label}: {_truncate(str(match))}")
        return hits

    def assert_clean(self, payload: Any) -> None:
        """Raise :class:`SanitizerError` when any hit is found."""
        hits: list[str] = self.scan(payload)
        if hits:
            raise SanitizerError(
                ErrorCode.E5002,
                f"sanitiser blocked propose: {len(hits)} hit(s)",
                context={"hits": hits},
            )


def _flatten(payload: Any) -> str:
    if payload is None:
        return ""
    if isinstance(payload, str):
        return payload
    if isinstance(payload, (int, float, bool)):
        return str(payload)
    if isinstance(payload, dict):
        items: Iterable[Any] = payload.values()  # type: ignore[assignment]
        return "\n".join(_flatten(v) for v in items)
    if isinstance(payload, (list, tuple, set)):
        return "\n".join(_flatten(v) for v in payload)  # type: ignore[arg-type]
    if hasattr(payload, "model_dump"):
        return _flatten(payload.model_dump(mode="json"))
    return str(payload)


def _truncate(value: str, *, limit: int = 80) -> str:
    return value if len(value) <= limit else value[:limit] + "…"


__all__ = ["Sanitizer"]
