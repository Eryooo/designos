# Route B Batch 4: Bounded Clarification UX Core

Date: 2026-05-26
Status: completed

## Goal

Compress still-necessary human confirmation in `uxeval` client mode into a single, small, high-return clarification package instead of repeated, low-value interruptions.

## Runtime changes

- Unified clarification schema now includes:
  - `screenshot_ref`
  - `candidate_pages`
  - `candidate_states`
  - `ambiguity_reason`
  - `affected_critical_paths`
  - `unlocks_final_delivery`
  - `confirmation_prompt`
- Clarification generation is now bounded:
  - only emitted for a small number of high-impact ambiguities
  - suppressed when the real problem is broad evidence shortage rather than a few ambiguous screenshots
- Clarification is prioritized by critical-path and final-gate impact.
- Same-run clarification is surfaced only once via shared state under `outputs/clarification/state.json`.
- Lightweight confirmation via `screens-map.md` / `screens-index.md` now feeds back into:
  - trusted mapping
  - critical-path coverage
  - final / fallback / supplement status

## Validation

Commands run:

```bash
./.venv/bin/python -m compileall \
  mcp-servers/image-analyzer/core.py \
  mcp-servers/image-analyzer/schemas.py \
  mcp-servers/image-analyzer/tests/test_core.py \
  tests/integration/test_kernel_mcp_integration.py

./.venv/bin/python -m pytest -q mcp-servers/image-analyzer/tests/test_core.py
./.venv/bin/python -m pytest -q tests/integration/test_kernel_mcp_integration.py
./.venv/bin/python -m pytest -q
./.venv/bin/python -m ruff check .
./.venv/bin/python -m pyright
```

Expected focus of validation:

- small ambiguity produces a minimal clarification package
- same run does not resurface the same clarification
- broad missing evidence does not misroute to clarification
- lightweight clarification confirmation can unlock critical-path coverage and final delivery
- clarification never lowers normal-mode confidence thresholds or lets fallback masquerade as final

## Product outcome

- Users are interrupted fewer times because the system now groups only the highest-return ambiguities into a single clarification package.
- Clarification is no longer a fallback for broad missing evidence; it is reserved for a few screenshots whose confirmation materially unlocks trusted coverage.
- The confirmation artifact is lightweight and local: users can confirm only the ambiguous screenshots instead of rewriting a full mapping table or bulk-renaming files.
