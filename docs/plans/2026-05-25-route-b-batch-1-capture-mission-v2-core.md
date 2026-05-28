Title: Route B Batch 1 - Capture Mission V2 Core
Date: 2026-05-25
Status: done

Summary
- Upgraded client-mode pre-run planning from a generic required-evidence plan into a runtime-consumable `capture_mission`.
- Added a user-facing `capture_mission.md` artifact under `runs/<run-id>/outputs/evidence-planning/`.
- Wired later runtime stages to the same mission semantics:
  - `load_and_analyze` now carries mission version, pass lines, capture order, and rationale into `coverage_summary`.
  - `evidence_assessment` now derives final/fallback thresholds from mission policy instead of hardcoded numbers alone.
  - `delivery-audit` now consumes `capture_mission` and echoes the same pass lines in the bounded package.

Runtime changes
- `plan_required_evidence` now returns `capture_mission` alongside `required_evidence_plan`.
- `skills/uxeval/pipeline.yaml` now exposes `capture_mission` from `evidence-planning` and passes it into `delivery-audit`.
- Missing-page / missing-state / missing-description messages were tightened to talk in Capture Mission terms instead of a vague plan.
- The same missing category is still surfaced once per unresolved run via planning/remediation state signatures; this batch keeps that behavior and makes the surfaced gap trace back to mission pass lines.

Validation
- `./.venv/bin/python -m pytest -q mcp-servers/image-analyzer/tests/test_core.py`
- `./.venv/bin/python -m pytest -q mcp-servers/excel-builder/tests/test_core.py`
- `./.venv/bin/python -m pytest -q skills/uxeval/tests/test_pipeline_integration.py tests/integration/test_kernel_mcp_integration.py`
- `./.venv/bin/python -m pytest -q`
- `./.venv/bin/python -m ruff check .`
- `./.venv/bin/python -m pyright`
- `./.venv/bin/python -m compileall mcp-servers/image-analyzer/core.py mcp-servers/image-analyzer/schemas.py mcp-servers/excel-builder/core.py mcp-servers/image-analyzer/tests/test_core.py tests/integration/test_kernel_mcp_integration.py skills/uxeval/tests/test_pipeline_integration.py tests/e2e/test_run_history_closure.py`

Observed results
- image-analyzer core: 23 passed
- excel-builder core: 13 passed
- pipeline + MCP integration: 55 passed
- full pytest: 247 passed
- ruff: passed
- pyright: 0 errors, 0 warnings

Product outcome
- Users now get a minimal critical capture task list before heavy analysis, not a late-stage generic “please add more screenshots”.
- Final / fallback / supplement outcomes can be traced back to the same mission pass lines across planning, analysis, remediation, evidence assessment, and delivery audit.
- The bounded fallback package now carries the same mission language as pre-run planning, reducing the need to translate raw runtime state by hand.
