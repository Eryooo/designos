# Batch 4E - final delivery readiness for uxeval client mode

Date: 2026-05-22

## Goal

Turn `uxeval` client mode from a coarse “can continue / cannot continue” flow into a productized delivery-qualification flow:

- only allow final report delivery when evidence and issue quality meet the final-delivery bar
- allow bounded fallback output only when it is safe enough to share as a limited intermediate result
- keep low-confidence or insufficiently evidenced issues out of the main issue list

## Changes

- Extended `evidence_assessment` with explicit delivery qualification:
  - `delivery_status`: `final_delivery_ready | fallback_safe | supplement_required | blocked`
  - `final_delivery_ready`
  - `fallback_safe`
  - `missing_coverage`
  - `coverage_summary`
- The image-analyzer now uses real local signals to decide delivery readiness:
  - screenshot count
  - readability ratio
  - OCR / description-backed text coverage
  - key-task coverage inferred from `task_checklist_lite`
- Preserved the old coarse `verdict` as a compatibility layer:
  - `final_delivery_ready` and `fallback_safe` both map to `verdict=sufficient`
  - `supplement_required` maps to `verdict=supplement_needed`
  - `blocked` stays `blocked`
- Added minimal issue-level delivery metadata in `Issue`:
  - `confidence`
  - `evidence_basis`
  - `verification_status`
- Updated the `uxeval` pipeline:
  - Stage 5.5 only blocks on `delivery_status == blocked`
  - Stage 6 blocks on `delivery_status in [blocked, supplement_required]`
  - Stage 6 now outputs `issues`, `unverified_issues`, and `delivery_assessment`
  - Stage 7 only runs when `delivery_assessment.delivery_status == final_delivery_ready`
- Updated prompts / docs so client mode now distinguishes:
  - final deliverable
  - bounded fallback result
  - supplement-required state
  - blocked state

## Validation

Commands run:

```bash
cd /Users/young/Documents/Codex/Agent-design/mcp-servers/image-analyzer
../../.venv/bin/python -m pytest -q tests/test_core.py

cd /Users/young/Documents/Codex/Agent-design
./.venv/bin/python -m pytest -q \
  skills/uxeval/tests/test_frontmatter_runtime.py \
  skills/uxeval/tests/test_pipeline_integration.py \
  tests/integration/test_kernel_mcp_integration.py \
  tests/e2e/test_run_history_closure.py \
  tests/unit/test_contracts.py

./.venv/bin/python -m pytest -q
./.venv/bin/python -m ruff check .
./.venv/bin/python -m pyright
```

Results:

- `image-analyzer` targeted suite: `10 passed`
- uxeval + runtime targeted suite: `126 passed`
- full repo baseline: `234 passed in 19.18s`
- `ruff check .`: passed
- `pyright`: `0 errors, 0 warnings, 0 informations`

## Product outcome

- Final reports now require `final_delivery_ready` rather than just “not obviously blocked”.
- `fallback_safe` can still produce a bounded issue pass, but runtime will not let it masquerade as a final report.
- `supplement_required` and `blocked` stop the run earlier and carry structured coverage gaps plus required actions.
- Stage 6 now has a formal split between:
  - `issues` for verified main-list items
  - `unverified_issues` for low-confidence or under-evidenced findings
