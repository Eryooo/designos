"""Run-id allocator and ``run.yaml`` manifest writer."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import yaml

from kernel.contracts.enums import Mode, RunStatus
from kernel.contracts.schemas import OutputManifest, RunManifest

from .workspace import Workspace


class RunManager:
    """Allocates run ids and persists :class:`RunManifest` documents."""

    def __init__(self, workspace: Workspace) -> None:
        self._workspace: Workspace = workspace

    def allocate(self, skill_name: str) -> str:
        """Assign the next ``NNN-<skill>`` run id."""
        runs_dir: Path = self._workspace.runs_dir
        runs_dir.mkdir(parents=True, exist_ok=True)
        existing: list[int] = []
        for entry in runs_dir.iterdir():
            if not entry.is_dir():
                continue
            head: str = entry.name.split("-", 1)[0]
            if head.isdigit():
                existing.append(int(head))
        next_idx: int = (max(existing) + 1) if existing else 1
        return f"{next_idx:03d}-{skill_name}"

    def run_dir(self, run_id: str, *, create: bool = True) -> Path:
        """Return the directory for ``run_id`` (creating it when requested)."""
        target: Path = self._workspace.runs_dir / run_id
        if create:
            target.mkdir(parents=True, exist_ok=True)
        return target

    def write_manifest(self, manifest: RunManifest) -> Path:
        """Persist the manifest to ``runs/<id>/run.yaml``."""
        target: Path = self.run_dir(manifest.id) / "run.yaml"
        target.write_text(
            yaml.safe_dump(
                manifest.model_dump(mode="json"),
                allow_unicode=True,
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        return target

    def start_manifest(
        self,
        run_id: str,
        skill: str,
        version: str,
        model: str,
        *,
        mode: Mode | None = None,
    ) -> RunManifest:
        """Build a fresh ``RUNNING`` manifest with the right timestamps."""
        return RunManifest(
            id=run_id,
            skill=skill,
            version=version,
            status=RunStatus.RUNNING,
            started_at=datetime.now(UTC),
            model=model,
            mode=mode,
        )

    def resume_manifest(self, manifest: RunManifest) -> RunManifest:
        """Return a paused manifest switched back to ``RUNNING`` for resume."""
        return manifest.model_copy(
            update={
                "status": RunStatus.RUNNING,
                "completed_at": None,
                "status_reason": None,
                "required_actions": [],
            }
        )

    def finish_manifest(
        self,
        manifest: RunManifest,
        *,
        status: RunStatus,
        outputs: list[OutputManifest] | None = None,
        status_reason: str | None = None,
        required_actions: list[str] | None = None,
    ) -> RunManifest:
        """Return a terminal manifest updated with final status and timestamp."""
        completed_at = datetime.now(UTC) if status in {RunStatus.COMPLETED, RunStatus.FAILED} else None
        return manifest.model_copy(
            update={
                "status": status,
                "completed_at": completed_at,
                "outputs": list(outputs or []),
                "status_reason": status_reason,
                "required_actions": list(required_actions or []),
            }
        )


__all__ = ["RunManager"]
