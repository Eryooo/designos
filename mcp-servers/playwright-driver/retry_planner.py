"""Retry planner: analyze execution failures and generate corrected scripts."""

from __future__ import annotations

from typing import Any

from schemas import (
    ActionType,
    EvaluationScript,
    ExecutionResult,
    ScriptStep,
    SelectorType,
)


class RetryPlanner:
    """Analyzes failed steps and produces corrected execution scripts."""

    def needs_retry(self, result: ExecutionResult) -> bool:
        return result.steps_failed > 0

    def plan_retry(
        self,
        original_script: EvaluationScript,
        result: ExecutionResult,
        page_state: dict[str, Any] | None = None,
    ) -> EvaluationScript | None:
        """Generate a corrected script for failed steps.

        Args:
            original_script: The script that was executed.
            result: The execution result with errors.
            page_state: Current page state (if available) for context.

        Returns:
            A new EvaluationScript with corrected steps, or None if no retry possible.
        """
        if not self.needs_retry(result):
            return None

        failed_steps = {e["step"] for e in result.errors}
        corrected_steps = []
        step_counter = 0

        for original_step in original_script.steps:
            if original_step.step not in failed_steps:
                continue

            error = next(
                (e for e in result.errors if e["step"] == original_step.step),
                None,
            )
            if error is None:
                continue

            correction = self._correct_step(original_step, error, page_state)
            if correction:
                step_counter += 1
                corrected_steps.append(correction.model_copy(update={"step": step_counter}))

        if not corrected_steps:
            return None

        return EvaluationScript(
            task_id=f"{original_script.task_id}-retry",
            task_title=f"{original_script.task_title} (retry)",
            steps=corrected_steps,
        )

    def _correct_step(
        self,
        step: ScriptStep,
        error: dict[str, Any],
        page_state: dict[str, Any] | None,
    ) -> ScriptStep | None:
        """Attempt to correct a failed step based on error type."""
        error_msg = error.get("error", "").lower()

        if step.action == ActionType.CLICK:
            return self._correct_click(step, error_msg, page_state)
        elif step.action == ActionType.NAVIGATE:
            return self._correct_navigate(step, error_msg)
        elif step.action == ActionType.FILL:
            return self._correct_fill(step, error_msg, page_state)
        elif step.action == ActionType.SWITCH_PAGE:
            return step.model_copy(update={"wait_after_ms": 2000})
        elif step.action == ActionType.SWITCH_FRAME:
            return step.model_copy(update={"wait_after_ms": 2000})

        return None

    def _correct_click(
        self, step: ScriptStep, error_msg: str, page_state: dict | None
    ) -> ScriptStep | None:
        if "timeout" in error_msg or "not found" in error_msg:
            if step.selector_type == SelectorType.CSS:
                return step.model_copy(update={
                    "selector_type": SelectorType.TEXT,
                    "selector": step.selector.split("#")[-1].split(".")[-1].replace("-", " "),
                    "wait_after_ms": max(step.wait_after_ms, 1000),
                })
            elif step.selector_type == SelectorType.TEXT:
                return step.model_copy(update={
                    "selector_type": SelectorType.ROLE,
                    "wait_after_ms": max(step.wait_after_ms, 1000),
                })
        return None

    def _correct_navigate(self, step: ScriptStep, error_msg: str) -> ScriptStep | None:
        if "timeout" in error_msg:
            return step.model_copy(update={"wait_after_ms": 3000})
        return None

    def _correct_fill(
        self, step: ScriptStep, error_msg: str, page_state: dict | None
    ) -> ScriptStep | None:
        if "timeout" in error_msg or "not found" in error_msg:
            return step.model_copy(update={"wait_after_ms": max(step.wait_after_ms, 1000)})
        return None
