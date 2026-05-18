"""LLM client dispatcher.

Provides a thin :class:`LLMClient` that routes to a concrete provider
(Anthropic / OpenAI / Deepseek) based on ``GlobalConfig.primary_model`` or
explicit construction.
"""

from __future__ import annotations

from typing import Any

from kernel.contracts.interfaces import ILLMClient
from kernel.contracts.schemas import GlobalConfig, LLMResponse
from kernel.trace import get_logger

from .anthropic_provider import AnthropicProvider
from .openai_provider import OpenAIProvider

_log = get_logger("kernel.llm.client")


class LLMClient(ILLMClient):
    """Routes calls to the configured primary provider with optional fallback."""

    def __init__(
        self,
        *,
        primary: ILLMClient,
        fallback: ILLMClient | None = None,
        default_model: str | None = None,
    ) -> None:
        self._primary: ILLMClient = primary
        self._fallback: ILLMClient | None = fallback
        self._default_model: str | None = default_model

    @classmethod
    def from_global_config(cls, cfg: GlobalConfig) -> LLMClient:
        """Build a client from :class:`GlobalConfig` defaults."""
        primary: ILLMClient = _build_provider(cfg.primary_model, anthropic_base_url=cfg.anthropic_base_url)
        fallback: ILLMClient | None = None
        if cfg.fallback_model and cfg.fallback_model != cfg.primary_model:
            fallback = _build_provider(cfg.fallback_model, anthropic_base_url=cfg.anthropic_base_url)
        return cls(primary=primary, fallback=fallback, default_model=cfg.primary_model)

    async def call(
        self,
        prompt: str,
        *,
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        chosen: str | None = model or self._default_model
        try:
            return await self._primary.call(
                prompt,
                model=chosen,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as exc:
            if self._fallback is None:
                raise
            _log.warning("llm.fallback.engaged", error=str(exc))
            return await self._fallback.call(
                prompt,
                model=None,
                temperature=temperature,
                max_tokens=max_tokens,
            )


def _build_provider(model: str, *, anthropic_base_url: str | None) -> ILLMClient:
    lowered: str = model.lower()
    if lowered.startswith(("claude", "anthropic")):
        kwargs: dict[str, Any] = {"default_model": model}
        if anthropic_base_url:
            kwargs["base_url"] = anthropic_base_url
        return AnthropicProvider(**kwargs)
    if lowered.startswith("deepseek"):
        return OpenAIProvider.for_deepseek(default_model=model)
    return OpenAIProvider(default_model=model)


__all__ = ["LLMClient"]
