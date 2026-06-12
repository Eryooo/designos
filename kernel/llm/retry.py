"""Exponential-backoff retry helper for LLM / MCP client calls.

The kernel's contract is "retry up to 3 attempts with exponential backoff".
This decorator wraps an async callable and retries on any
:class:`DesignOSError` whose ``error_code`` matches the configured filter, or
on any unhandled exception when no filter is supplied.
"""

from __future__ import annotations

import asyncio
import functools
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar

from kernel.contracts.enums import ErrorCode
from kernel.contracts.schemas import RetryConfig
from kernel.errors import DesignOSError
from kernel.trace import get_logger

_log = get_logger("kernel.llm.retry")

T = TypeVar("T")


def with_retry(
    config: RetryConfig | None = None,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Decorate an async callable with exponential-backoff retry.

    Args:
        config: Retry policy; defaults to :class:`RetryConfig` defaults
            (max_attempts=2, backoff=1.0, retry on any error).
    """
    cfg = config or RetryConfig()

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: object, **kwargs: object) -> T:
            attempt: int = 0
            while True:
                attempt += 1
                try:
                    return await func(*args, **kwargs)
                except DesignOSError as exc:
                    if not _should_retry(cfg, exc.error_code, attempt):
                        raise
                    delay: float = _backoff(cfg, attempt)
                    _log.warning(
                        "retry.scheduled",
                        attempt=attempt,
                        delay=delay,
                        code=exc.error_code.value,
                    )
                    await asyncio.sleep(delay)
                except Exception:
                    if attempt >= cfg.max_attempts or cfg.retry_on:
                        raise
                    delay = _backoff(cfg, attempt)
                    _log.warning("retry.scheduled", attempt=attempt, delay=delay)
                    await asyncio.sleep(delay)

        return wrapper

    return decorator


def _should_retry(cfg: RetryConfig, code: ErrorCode, attempt: int) -> bool:
    if attempt >= cfg.max_attempts:
        return False
    return not (cfg.retry_on and code not in cfg.retry_on)


def _backoff(cfg: RetryConfig, attempt: int) -> float:
    base: float = cfg.backoff_seconds * (2 ** (attempt - 1))
    jitter: float = random.uniform(0.0, cfg.backoff_seconds * 0.1)
    return base + jitter


__all__ = ["with_retry"]
