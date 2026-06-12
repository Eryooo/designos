"""Markdown renderer using simple ``{{var}}`` substitution.

We deliberately avoid pulling in ``jinja2`` (not declared in pyproject); the
renderer supports two modes:

1. ``payload`` is a string — written verbatim to ``target_path``.
2. ``payload`` is a Pydantic model or dict — rendered as a YAML-like
   structured Markdown document with section headings.

Skill-specific Markdown templates can be supplied via the ``template`` kwarg
on :func:`render`.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from kernel.contracts.enums import ErrorCode
from kernel.errors import WorkspaceError

_VAR_RE = re.compile(r"\{\{\s*([\w.]+)\s*\}\}")


class MarkdownRenderer:
    """Render Pydantic / dict / str payloads as Markdown."""

    async def render(
        self,
        artefact_id: str,
        payload: Any,
        *,
        target_path: Path,
        template: str | None = None,
    ) -> Path:
        """Render and persist a Markdown artefact.

        Args:
            artefact_id: Stable artefact identifier (used for the H1 heading).
            payload: String, dict or Pydantic model.
            target_path: Destination path.
            template: Optional Markdown template containing ``{{var}}`` placeholders.

        Returns:
            Absolute path of the written file.
        """
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(payload, str):
            content: str = payload
        elif template is not None:
            content = _render_template(template, _to_dict(payload))
        else:
            content = _render_default(artefact_id, _to_dict(payload))
        try:
            target_path.write_text(content, encoding="utf-8")
        except OSError as exc:
            raise WorkspaceError(
                ErrorCode.E4003,
                f"failed to write markdown: {exc}",
                context={"path": str(target_path)},
            ) from exc
        return target_path.resolve()


def _to_dict(payload: Any) -> dict[str, Any]:
    if hasattr(payload, "model_dump"):
        return payload.model_dump(mode="json")  # type: ignore[no-any-return]
    if isinstance(payload, dict):
        return dict(payload)  # type: ignore[arg-type]
    return {"value": payload}


def _render_template(template: str, ctx: dict[str, Any]) -> str:
    def replace(match: re.Match[str]) -> str:
        path: str = match.group(1)
        cur: Any = ctx
        for segment in path.split("."):
            cur = cur.get(segment, "") if isinstance(cur, dict) else getattr(cur, segment, "")
            if cur in (None, ""):
                return ""
        return str(cur)

    return _VAR_RE.sub(replace, template)


def _render_default(title: str, payload: dict[str, Any]) -> str:
    lines: list[str] = [f"# {title}", ""]
    for key, value in payload.items():
        lines.append(f"## {key}")
        lines.append("")
        lines.append(_format_value(value))
        lines.append("")
    return "\n".join(lines)


def _format_value(value: Any) -> str:
    if isinstance(value, list):
        return "\n".join(f"- {_format_inline(item)}" for item in value)  # type: ignore[arg-type]
    if isinstance(value, dict):
        return "\n".join(f"- **{k}**: {_format_inline(v)}" for k, v in value.items())  # type: ignore[arg-type]
    return str(value)


def _format_inline(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return str(value)
    return str(value)


__all__ = ["MarkdownRenderer"]
