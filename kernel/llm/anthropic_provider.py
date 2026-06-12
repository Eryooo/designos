"""Anthropic provider for :class:`ILLMClient`.

Uses the official ``anthropic`` SDK in async mode; honours
``ANTHROPIC_API_KEY`` and optional ``ANTHROPIC_BASE_URL``.
"""

from __future__ import annotations

import os
from typing import Any

from kernel.contracts.enums import ErrorCode
from kernel.contracts.interfaces import ILLMClient
from kernel.contracts.schemas import LLMResponse
from kernel.errors import ConfigError, DesignOSError
from kernel.trace import get_logger

_log = get_logger("kernel.llm.anthropic")


class AnthropicProvider(ILLMClient):
    """Async Anthropic client adapter."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        default_model: str = "claude-opus-4-7",
    ) -> None:
        self._api_key: str | None = api_key or os.getenv("ANTHROPIC_API_KEY")
        self._base_url: str | None = base_url or os.getenv("ANTHROPIC_BASE_URL")
        self._default_model: str = default_model
        self._client: Any | None = None

    def _ensure_client(self) -> Any:
        if self._client is not None:
            return self._client
        if not self._api_key:
            raise ConfigError(
                ErrorCode.E1002,
                "ANTHROPIC_API_KEY is not set",
            )
        try:
            from anthropic import AsyncAnthropic
        except ImportError as exc:  # pragma: no cover - dependency declared
            raise ConfigError(
                ErrorCode.E1003,
                "anthropic SDK is not installed",
            ) from exc
        kwargs: dict[str, Any] = {"api_key": self._api_key}
        if self._base_url:
            kwargs["base_url"] = self._base_url
        self._client = AsyncAnthropic(**kwargs)
        return self._client

    async def call(
        self,
        prompt: str,
        *,
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Send a single prompt to Anthropic and normalise the response."""
        chosen: str = model or self._default_model
        client: Any = self._ensure_client()
        try:
            resp: Any = await client.messages.create(
                model=chosen,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as exc:
            _log.error("anthropic.call.failed", error=str(exc))
            raise DesignOSError(
                ErrorCode.E1003,
                f"anthropic call failed: {exc}",
                context={"model": chosen},
            ) from exc

        text: str = _extract_text(resp)
        usage: dict[str, int] = _extract_usage(resp)
        finish: str = _normalise_stop_reason(getattr(resp, "stop_reason", None))
        return LLMResponse(
            text=text,
            model=chosen,
            input_tokens=usage.get("input_tokens", 0),
            output_tokens=usage.get("output_tokens", 0),
            finish_reason=finish,  # type: ignore[arg-type]
            raw=_to_dict(resp),
        )


def _extract_text(resp: Any) -> str:
    blocks: Any = getattr(resp, "content", None)
    if blocks is None:
        return ""
    parts: list[str] = []
    for block in blocks:  # type: ignore[assignment]
        text: Any = getattr(block, "text", None)
        if isinstance(text, str):
            parts.append(text)
    return "".join(parts)


def _extract_usage(resp: Any) -> dict[str, int]:
    usage: Any = getattr(resp, "usage", None)
    if usage is None:
        return {}
    return {
        "input_tokens": int(getattr(usage, "input_tokens", 0) or 0),
        "output_tokens": int(getattr(usage, "output_tokens", 0) or 0),
    }


def _normalise_stop_reason(value: Any) -> str:
    if value in {"end_turn", "stop_sequence"}:
        return "stop"
    if value == "max_tokens":
        return "length"
    if value == "tool_use":
        return "tool_use"
    return "stop"


def _to_dict(resp: Any) -> dict[str, Any]:
    if hasattr(resp, "model_dump"):
        return resp.model_dump()  # type: ignore[no-any-return]
    return {}


__all__ = ["AnthropicProvider"]
