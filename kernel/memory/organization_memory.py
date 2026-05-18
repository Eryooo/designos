"""Organisation memory stub for M1.

The full implementation will sync with an external git repository in M2.
For M1 we only support the ``propose`` path: payloads pass through the
sanitiser and are written to a staging directory for human review.
``search_organization`` returns an empty list.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from kernel.contracts.enums import ErrorCode
from kernel.errors import OrgMemoryError

from .sanitizer import Sanitizer


class OrganizationMemory:
    """Stub backed by a local staging directory."""

    def __init__(self, workspace: Path, *, sanitizer: Sanitizer | None = None) -> None:
        self._staging: Path = workspace / ".designos" / "memory" / "staging"
        self._sanitizer: Sanitizer = sanitizer or Sanitizer()

    def search(self, query: str, k: int = 5) -> list[Any]:
        """Return an empty list — semantic search is M2 work."""
        del query, k
        return []

    def propose(self, category: str, payload: Any) -> str:
        """Run sanitiser, persist to staging, return the local path as URL.

        Args:
            category: Memory bucket (e.g. ``uxeval/golden_samples``).
            payload: Document to publish (dict or pydantic-compatible).

        Returns:
            ``file://`` URL of the staged document.

        Raises:
            SanitizerError: When the sanitiser detects sensitive data.
            OrgMemoryError: When writing to staging fails.
        """
        self._sanitizer.assert_clean(payload)
        if not category or ("/" in category and category.startswith("/")):
            raise OrgMemoryError(
                ErrorCode.E5001,
                f"invalid category: {category!r}",
            )
        target_dir: Path = self._staging / category.strip("/")
        target_dir.mkdir(parents=True, exist_ok=True)
        stamp: str = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        target: Path = target_dir / f"propose-{stamp}.json"
        try:
            target.write_text(
                json.dumps(_to_jsonable(payload), ensure_ascii=False, indent=2, default=str),
                encoding="utf-8",
            )
        except OSError as exc:  # pragma: no cover - filesystem failure
            raise OrgMemoryError(
                ErrorCode.E5001,
                f"failed to write organisation propose: {exc}",
                context={"path": str(target)},
            ) from exc
        return target.resolve().as_uri()


def _to_jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return value


__all__ = ["OrganizationMemory"]
