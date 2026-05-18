"""Output renderer dispatcher implementing :class:`IOutputRenderer`."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from kernel.contracts.enums import ErrorCode
from kernel.contracts.interfaces import IOutputRenderer
from kernel.errors import WorkspaceError

from .excel import ExcelStubRenderer
from .html import HTMLRenderer
from .markdown import MarkdownRenderer


class OutputRenderer(IOutputRenderer):
    """Dispatches by ``fmt`` to the format-specific renderer."""

    def __init__(
        self,
        *,
        markdown: MarkdownRenderer | None = None,
        excel: ExcelStubRenderer | None = None,
        html: HTMLRenderer | None = None,
    ) -> None:
        self._markdown: MarkdownRenderer = markdown or MarkdownRenderer()
        self._excel: ExcelStubRenderer = excel or ExcelStubRenderer()
        self._html: HTMLRenderer = html or HTMLRenderer()

    async def render(
        self,
        artefact_id: str,
        payload: Any,
        *,
        target_path: Path,
        fmt: str,
    ) -> Path:
        target_path = Path(target_path)
        if fmt == "markdown":
            return await self._markdown.render(artefact_id, payload, target_path=target_path)
        if fmt == "xlsx":
            return await self._excel.render(artefact_id, payload, target_path=target_path)
        if fmt == "html":
            return await self._html.render(artefact_id, payload, target_path=target_path)
        if fmt == "json":
            return _write_json(target_path, payload)
        raise WorkspaceError(
            ErrorCode.E4003,
            f"unsupported output format: {fmt}",
            context={"artefact_id": artefact_id, "fmt": fmt},
        )


def _write_json(target_path: Path, payload: Any) -> Path:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    body: str = json.dumps(_jsonable(payload), ensure_ascii=False, indent=2, default=str)
    target_path.write_text(body, encoding="utf-8")
    return target_path.resolve()


def _jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return value


__all__ = ["OutputRenderer"]
