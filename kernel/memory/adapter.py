"""Composite memory adapter implementing :class:`IMemoryAdapter`.

Wraps :class:`SessionMemory`, :class:`ProjectMemory` and
:class:`OrganizationMemory` to satisfy the kernel contract.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from kernel.contracts.interfaces import IMemoryAdapter

from .organization_memory import OrganizationMemory
from .project_memory import ProjectMemory
from .sanitizer import Sanitizer
from .session_memory import SessionMemory


class MemoryAdapter(IMemoryAdapter):
    """Three-tier memory facade used throughout the kernel."""

    def __init__(
        self,
        workspace: Path,
        *,
        session: SessionMemory | None = None,
        project: ProjectMemory | None = None,
        organization: OrganizationMemory | None = None,
    ) -> None:
        sanitizer = Sanitizer()
        self._session: SessionMemory = session or SessionMemory()
        self._project: ProjectMemory = project or ProjectMemory(workspace)
        self._organization: OrganizationMemory = organization or OrganizationMemory(
            workspace, sanitizer=sanitizer
        )

    # --- session ------------------------------------------------------------

    def read_session(self, key: str) -> Any:
        return self._session.read(key)

    def write_session(self, key: str, value: Any) -> None:
        self._session.write(key, value)

    # --- project ------------------------------------------------------------

    def read_project(self, key: str) -> Any:
        return self._project.read(key)

    def write_project(self, key: str, value: Any) -> None:
        self._project.write(key, value)

    # --- organisation -------------------------------------------------------

    def search_organization(self, query: str, k: int = 5) -> list[Any]:
        return self._organization.search(query, k)

    def propose_to_organization(self, category: str, payload: Any) -> str:
        return self._organization.propose(category, payload)


__all__ = ["MemoryAdapter"]
