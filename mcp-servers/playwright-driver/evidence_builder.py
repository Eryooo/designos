"""Evidence formatting for web mode, aligned with DesignOS Evidence Contract."""

from __future__ import annotations

from datetime import datetime

from schemas import ActionType, PageState, StepEvidence


def build_step_evidence(
    step: int,
    action: ActionType,
    page_state: PageState,
    screenshot_path: str | None = None,
    dom_snapshot: dict | None = None,
) -> StepEvidence:
    return StepEvidence(
        step=step,
        action=action,
        url=page_state.url,
        title=page_state.title,
        screenshot_path=screenshot_path,
        dom_snapshot=dom_snapshot,
        page_state=page_state,
        timestamp=datetime.now().isoformat(),
        confidence="ground_truth",
        evidence_basis=_build_basis(screenshot_path, dom_snapshot),
        verification_gap=[],
    )


def _build_basis(screenshot_path: str | None, dom_snapshot: dict | None) -> list[str]:
    basis = ["url"]
    if dom_snapshot:
        basis.append("dom")
    if screenshot_path:
        basis.append("screenshot")
    return basis
