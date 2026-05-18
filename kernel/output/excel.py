"""Excel renderer stub for M1.

Real Excel generation lives in the ``excel-builder`` MCP server. The kernel
stub records that the artefact was requested and writes a placeholder JSON
file beside the intended path so traces stay coherent.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from kernel.contracts.enums import ErrorCode
from kernel.errors import WorkspaceError


class ExcelStubRenderer:
    """Writes a JSON stub describing the intended Excel artefact."""

    async def render(
        self,
        artefact_id: str,
        payload: Any,
        *,
        target_path: Path,
    ) -> Path:
        """Persist a stub JSON file alongside ``target_path``.

        Returns:
            Absolute path of the written stub.
        """
        target_path.parent.mkdir(parents=True, exist_ok=True)
        stub: Path = target_path.with_suffix(target_path.suffix + ".stub.json")
        try:
            stub.write_text(
                json.dumps(
                    {"artefact_id": artefact_id, "payload": _jsonable(payload)},
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                ),
                encoding="utf-8",
            )
        except OSError as exc:
            raise WorkspaceError(
                ErrorCode.E4003,
                f"failed to write excel stub: {exc}",
                context={"path": str(stub)},
            ) from exc
        return stub.resolve()


def _jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return value


__all__ = ["ExcelStubRenderer"]
