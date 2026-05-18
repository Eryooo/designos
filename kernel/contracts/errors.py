"""DesignOS exception hierarchy.

All exceptions raised inside the kernel, MCP servers, or skills must inherit
from :class:`DesignOSError` and carry an :class:`~kernel.contracts.enums.ErrorCode`
so that callers can branch on the canonical code rather than substring-matching
messages.

Note: Python ships a built-in ``MemoryError``; the DesignOS organisation-memory
exception is therefore exposed as :class:`OrgMemoryError` to avoid shadowing.
"""

from __future__ import annotations

from typing import Any

from .enums import ErrorCode


class DesignOSError(Exception):
    """Base exception for every DesignOS subsystem.

    Attributes:
        error_code: Canonical :class:`ErrorCode` identifying the failure family.
        message: Human-readable description shown in CLI output and logs.
        context: Free-form structured payload (file paths, stage ids, etc.)
            attached for debugging; must be JSON-serialisable.
    """

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        *,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.error_code: ErrorCode = error_code
        self.message: str = message
        self.context: dict[str, Any] = context if context is not None else {}

    def __str__(self) -> str:  # pragma: no cover - trivial formatting
        return f"[{self.error_code.value}] {self.message}"


class ConfigError(DesignOSError):
    """Raised when configuration loading or validation fails (E1xxx)."""


class PreflightError(DesignOSError):
    """Raised when an external dependency precondition is not satisfied.

    Reuses the E1xxx code space (config / environment family).
    """


class PipelineError(DesignOSError):
    """Raised by the pipeline engine for stage / checkpoint failures (E2xxx)."""


class MCPError(DesignOSError):
    """Raised when an MCP server fails to start or respond (E3xxx)."""


class WorkspaceError(DesignOSError):
    """Raised for workspace / filesystem issues (E4xxx)."""


class OrgMemoryError(DesignOSError):
    """Raised when the organisation memory git repository is unreachable.

    Named ``OrgMemoryError`` (not ``MemoryError``) to avoid shadowing the
    built-in ``MemoryError`` from the Python standard library. Maps to E5001.
    """


class SanitizerError(DesignOSError):
    """Raised when sanitiser detects sensitive data on memory propose (E5002)."""


__all__ = [
    "ConfigError",
    "DesignOSError",
    "MCPError",
    "OrgMemoryError",
    "PipelineError",
    "PreflightError",
    "SanitizerError",
    "WorkspaceError",
]
