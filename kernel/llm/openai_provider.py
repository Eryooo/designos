"""OpenAI-compatible provider (OpenAI / Deepseek)."""

from __future__ import annotations

import os
from typing import Any, Literal

from kernel.contracts.enums import ErrorCode
from kernel.contracts.interfaces import ILLMClient
from kernel.contracts.schemas import LLMResponse
from kernel.errors import ConfigError, DesignOSError
from kernel.trace import get_logger

_log = get_logger("kernel.llm.openai")


class OpenAIProvider(ILLMClient):
    """Async OpenAI / Deepseek-compatible client adapter."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        default_model: str = "gpt-4o-mini",
        api_key_env: str = "OPENAI_API_KEY",
        base_url_env: str = "OPENAI_BASE_URL",
    ) -> None:
        self._api_key: str | None = api_key or os.getenv(api_key_env)
        self._base_url: str | None = base_url or os.getenv(base_url_env)
        self._default_model: str = default_model
        self._client: Any | None = None
        self._api_key_env: str = api_key_env

    @classmethod
    def for_deepseek(cls, *, default_model: str = "deepseek-chat") -> OpenAIProvider:
        """Construct a provider preconfigured for Deepseek's OpenAI-compatible API."""
        return cls(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            default_model=default_model,
            api_key_env="DEEPSEEK_API_KEY",
        )

    def _ensure_client(self) -> Any:
        if self._client is not None:
            return self._client
        if not self._api_key:
            raise ConfigError(
                ErrorCode.E1002,
                f"{self._api_key_env} is not set",
            )
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:  # pragma: no cover
            raise ConfigError(
                ErrorCode.E1003,
                "openai SDK is not installed",
            ) from exc
        kwargs: dict[str, Any] = {"api_key": self._api_key}
        if self._base_url:
            kwargs["base_url"] = self._base_url
        self._client = AsyncOpenAI(**kwargs)
        return self._client

    async def call(
        self,
        prompt: str,
        *,
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        chosen: str = model or self._default_model
        client: Any = self._ensure_client()
        try:
            resp: Any = await client.chat.completions.create(
                model=chosen,
                temperature=temperature,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as exc:
            _log.error("openai.call.failed", error=str(exc))
            raise DesignOSError(
                ErrorCode.E1003,
                f"openai-compatible call failed: {exc}",
                context={"model": chosen},
            ) from exc

        choice: Any = resp.choices[0]
        text: str = (choice.message.content or "") if choice.message else ""
        usage: Any = getattr(resp, "usage", None)
        return LLMResponse(
            text=text,
            model=chosen,
            input_tokens=int(getattr(usage, "prompt_tokens", 0) or 0) if usage else 0,
            output_tokens=int(getattr(usage, "completion_tokens", 0) or 0) if usage else 0,
            finish_reason=_normalise_finish(getattr(choice, "finish_reason", "stop")),
            raw=_to_dict(resp),
        )


def _normalise_finish(value: Any) -> Literal["stop", "length", "tool_use", "error"]:
    if value == "length":
        return "length"
    if value == "tool_calls":
        return "tool_use"
    return "stop"


def _to_dict(resp: Any) -> dict[str, Any]:
    if hasattr(resp, "model_dump"):
        return resp.model_dump()  # type: ignore[no-any-return]
    return {}


__all__ = ["OpenAIProvider"]
