"""JSON script interpreter for playwright-driver MCP server."""

from __future__ import annotations

from typing import Any

from core import BrowserManager
from evidence_builder import build_step_evidence
from schemas import (
    ActionType,
    EvaluationScript,
    ExecutionResult,
    StepEvidence,
    StepResult,
)


class ScriptExecutor:
    """Executes a JSON evaluation script against a live browser."""

    def __init__(self, browser: BrowserManager, output_dir: str | None = None) -> None:
        self._browser = browser
        self._output_dir = output_dir

    def execute(self, script: EvaluationScript) -> ExecutionResult:
        results: list[StepResult] = []
        evidence: list[StepEvidence] = []
        errors: list[dict[str, Any]] = []

        for step_def in script.steps:
            result = self._execute_step(step_def)
            results.append(result)
            if result.success and result.evidence:
                evidence.append(result.evidence)
            elif not result.success:
                errors.append({
                    "step": step_def.step,
                    "action": step_def.action.value,
                    "error": result.error,
                })

        succeeded = sum(1 for r in results if r.success)
        failed = len(results) - succeeded
        status = "completed" if failed == 0 else ("partial" if succeeded > 0 else "failed")

        return ExecutionResult(
            task_id=script.task_id,
            task_title=script.task_title,
            status=status,
            steps_total=len(results),
            steps_succeeded=succeeded,
            steps_failed=failed,
            evidence=evidence,
            errors=errors,
        )

    def _execute_step(self, step) -> StepResult:
        try:
            action = step.action
            screenshot_path = None
            dom_snapshot = None

            if action == ActionType.NAVIGATE:
                self._browser.navigate(step.url)
            elif action == ActionType.CLICK:
                self._browser.click(
                    step.selector,
                    selector_type=step.selector_type.value,
                )
            elif action == ActionType.FILL:
                self._browser.fill(step.selector, step.value or "")
            elif action == ActionType.SCREENSHOT:
                screenshot_path = self._browser.screenshot(
                    step.name or f"step-{step.step}",
                    full_page=step.full_page,
                    output_dir=self._output_dir,
                )
            elif action == ActionType.GET_STATE:
                pass
            elif action == ActionType.WAIT:
                self._browser._page.wait_for_timeout(step.wait_after_ms or 1000)
            elif action == ActionType.SWITCH_PAGE:
                self._browser.switch_page(step.page_index or "last")
            elif action == ActionType.SWITCH_FRAME:
                self._browser.switch_frame(frame_selector=step.frame_selector)
            elif action == ActionType.EXTRACT_DOM:
                dom_snapshot = self._browser.extract_dom(step.selector or "body")

            if step.wait_after_ms and action != ActionType.WAIT:
                self._browser._page.wait_for_timeout(step.wait_after_ms)

            page_state = self._browser.get_page_state()
            ev = build_step_evidence(
                step=step.step,
                action=action,
                page_state=page_state,
                screenshot_path=screenshot_path,
                dom_snapshot=dom_snapshot,
            )
            return StepResult(step=step.step, action=action, success=True, evidence=ev)

        except Exception as exc:
            return StepResult(
                step=step.step,
                action=step.action,
                success=False,
                error=str(exc),
            )
