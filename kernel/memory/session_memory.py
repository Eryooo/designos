"""Process-local session memory backed by an in-memory dict."""

from __future__ import annotations

from typing import Any


class SessionMemory:
    """Volatile key-value store living for the duration of one process."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    def read(self, key: str) -> Any:
        """Return the value for ``key`` or ``None`` when missing."""
        return self._data.get(key)

    def write(self, key: str, value: Any) -> None:
        """Store ``value`` under ``key``."""
        self._data[key] = value

    def keys(self) -> list[str]:
        """Return all known keys (sorted for stability)."""
        return sorted(self._data)


__all__ = ["SessionMemory"]
