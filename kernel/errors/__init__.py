"""Re-export of the frozen error classes from ``kernel.contracts``.

This package exists so kernel internals can ``from kernel.errors import ...``
without reaching into ``contracts`` directly. Concrete exception classes are
defined in :mod:`kernel.contracts.errors` and must not be redefined here.
"""

from __future__ import annotations

from kernel.contracts.errors import (
    ConfigError,
    DesignOSError,
    MCPError,
    OrgMemoryError,
    PipelineError,
    PreflightError,
    SanitizerError,
    WorkspaceError,
)

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
