"""Tiny HTML renderer for run reports.

Builds a minimal HTML document with the artefact id as title and the payload
serialised as a ``<pre>`` block. Skills can later supply richer templates.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from kernel.contracts.enums import ErrorCode
from kernel.errors import WorkspaceError

_BASE_TEMPLATE: str = (
    "<!DOCTYPE html>\n"
    "<html lang=\"en\">\n"
    "<head>\n"
    "<meta charset=\"utf-8\" />\n"
    "<title>{title}</title>\n"
    "<style>body{{font-family:system-ui,sans-serif;margin:2rem;}}"
    "pre{{background:#f5f5f5;padding:1rem;overflow:auto;}}</style>\n"
    "</head>\n"
    "<body>\n"
    "<h1>{title}</h1>\n"
    "<pre>{body}</pre>\n"
    "</body>\n"
    "</html>\n"
)


class HTMLRenderer:
    """Minimal HTML artefact writer."""

    async def render(
        self,
        artefact_id: str,
        payload: Any,
        *,
        target_path: Path,
        template: str | None = None,
    ) -> Path:
        """Persist an HTML artefact.

        Args:
            artefact_id: Used as the page title.
            payload: Anything JSON-serialisable.
            target_path: Destination ``.html`` path.
            template: Optional override of the default template.

        Returns:
            Absolute path of the written file.
        """
        target_path.parent.mkdir(parents=True, exist_ok=True)
        body: str = json.dumps(_jsonable(payload), ensure_ascii=False, indent=2, default=str)
        document: str = (template or _BASE_TEMPLATE).format(
            title=html.escape(artefact_id),
            body=html.escape(body),
        )
        try:
            target_path.write_text(document, encoding="utf-8")
        except OSError as exc:
            raise WorkspaceError(
                ErrorCode.E4003,
                f"failed to write html: {exc}",
                context={"path": str(target_path)},
            ) from exc
        return target_path.resolve()


def _jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return value


__all__ = ["HTMLRenderer"]
