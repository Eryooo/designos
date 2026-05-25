# Batch 4D - evidence_assessment runtime quality gate

Date: 2026-05-22

## Goal

Turn `evidence_assessment` from a prompt-only hint into a real runtime gate for `uxeval` client mode so blocked or insufficient evidence cannot silently flow into final issue attribution or report generation.

## Changes

- Added generic `StageGateConfig` to pipeline stage schema.
- Extended the runtime condition DSL to read dotted paths from pipeline state, such as `evidence_assessment.verdict`.
- Added engine-level gate handling before stage execution:
  - `pause` gates emit checkpoint events with `pause_kind=gate`
  - gate pauses persist `status_reason` and `required_actions`
  - gate checkpoints can rewind resume to an earlier stage via `resume_from_stage`
- Changed checkpoint restore order so current workspace inputs override stale snapshot state on resume. This allows user-supplemented evidence to take effect after a gated pause.
- Added paused-run manifest fields:
  - `status_reason`
  - `required_actions`
- Prevented `--auto-confirm` from auto-bypassing gate pauses. Only normal review checkpoints auto-continue.
- Wired `skills/uxeval/pipeline.yaml` gates:
  - `QG1`: block before `prd-screenshot-conflict` when verdict is `blocked`
  - `QG2`: pause before `issue-attribution` when verdict is `blocked` or `supplement_needed`
  - `QG3`: defensive pause before `report-generation` when verdict is `blocked` or `supplement_needed`
  - all three rewind to `screenshot-loading`

## Validation

Commands run:

```bash
./.venv/bin/python -m compileall \
  kernel/contracts/schemas.py \
  kernel/pipeline/condition.py \
  kernel/pipeline/engine.py \
  kernel/skill_loader/pipeline_loader.py \
  kernel/workspace/run_manager.py \
  designos/cli/main.py

./.venv/bin/python -m pytest -q \
  tests/unit/test_kernel_pipeline.py \
  tests/unit/test_kernel_skill_loader.py \
  tests/unit/test_cli_run_history.py \
  tests/e2e/test_resume_closure.py \
  skills/uxeval/tests/test_pipeline_integration.py \
  tests/unit/test_contracts.py

./.venv/bin/python -m pytest -q \
  tests/unit/test_cli_resume.py \
  tests/e2e/test_run_history_closure.py \
  tests/integration/test_skill_pipeline_integration.py

./.venv/bin/python -m pytest -q
```

Results:

- targeted gate suite: `132 passed`
- related CLI/integration suite: `12 passed`
- full repo baseline: `231 passed in 18.61s`

## Product outcome

- `blocked` evidence no longer reaches conflict analysis / issue attribution / report generation as if it were valid.
- `supplement_needed` evidence no longer silently produces final issue lists or reports.
- paused runs now tell the user what to fix and can be resumed after supplementing evidence, with the evidence stages re-run instead of reusing stale snapshot state.
