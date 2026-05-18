"""Structlog configuration for the kernel.

Every kernel module must obtain its logger via :func:`get_logger`.
``print`` is forbidden by project convention.
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Any

import structlog
from structlog.stdlib import BoundLogger

_configured: bool = False


def configure(
    *,
    level: str | None = None,
    json_output: bool | None = None,
) -> None:
    """Configure structlog once for the whole process.

    Args:
        level: Log level name (e.g. ``"INFO"``); defaults to ``DESIGNOS_LOG_LEVEL``
            env var or ``INFO``.
        json_output: Force JSON renderer when True; defaults to env var
            ``DESIGNOS_LOG_JSON`` truthy or non-tty stdout.
    """
    global _configured
    if _configured:
        return

    resolved_level: str = (level or os.getenv("DESIGNOS_LOG_LEVEL", "INFO")).upper()
    if json_output is None:
        json_output = bool(os.getenv("DESIGNOS_LOG_JSON")) or not sys.stdout.isatty()

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=getattr(logging, resolved_level, logging.INFO),
    )

    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    processors.append(
        structlog.processors.JSONRenderer()
        if json_output
        else structlog.dev.ConsoleRenderer(colors=sys.stderr.isatty())
    )

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, resolved_level, logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )
    _configured = True


def get_logger(name: str | None = None, **initial: Any) -> BoundLogger:
    """Return a configured structlog logger bound with optional context."""
    if not _configured:
        configure()
    logger: BoundLogger = structlog.get_logger(name)
    if initial:
        logger = logger.bind(**initial)
    return logger


__all__ = ["configure", "get_logger"]
