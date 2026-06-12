# Batch 4F - Auto Remediation Before Pause

## Scope

Only Batch 4F:

- upgrade uxeval client-mode evidence flow from "hit gate then pause" to
  "auto-remediate once, pause only if unresolved"
- keep the logic in the existing `mcp-servers/image-analyzer` package and the
  uxeval runtime call chain
- do not add new CLI features, remote services, or broad schema rewrites

## What Changed

### 1. `image-analyzer` now performs one real remediation pass before gates see the result

The existing `load_and_analyze()` flow now:

1. scans the evidence bundle
2. builds baseline OCR / markdown / filename cues
3. computes a baseline `evidence_assessment`
4. if the result is not `final_delivery_ready`, performs one remediation pass:
   - reuses recursive scan results
   - re-matches `screens-description.md` and markdown sections to screenshots
   - generates run-scoped derived evidence notes from OCR + markdown + existing
     cue structure
   - rebuilds per-screenshot linked evidence and text cues
   - recomputes `evidence_assessment`

This lets client mode self-heal common evidence-shape issues before the
pipeline pauses the user.

### 2. Supplement requests are now structured

`evidence_assessment.coverage_summary` now records concrete gap lists such as:

- `low_readability_paths`
- `missing_description_paths`
- `missing_ocr_paths`
- `missing_state_categories`
- `missing_tasks`

`required_actions` also became more specific by referencing the exact screenshots
or gap categories that need follow-up.

### 3. Same unresolved gap only pauses once

The analyzer now persists a run-scoped remediation state under:

- `runs/<run-id>/outputs/evidence-remediation/`

When a paused run is resumed without any evidence change and the unresolved gap
signature is identical, the analyzer fails fast with a clear remediation-loop
message instead of triggering another identical pause.

### 4. Tool failure messages now surface real MCP errors

`kernel/pipeline/stage_runner.py` now propagates the underlying MCP error
message instead of collapsing every tool failure into a generic `tool failed`.

## Validation

Commands:

```bash
cd mcp-servers/image-analyzer && ../../.venv/bin/python -m pytest -q tests/test_core.py
./.venv/bin/python -m pytest -q tests/e2e/test_run_history_closure.py tests/integration/test_kernel_mcp_integration.py
./.venv/bin/python -m pytest -q
./.venv/bin/python -m ruff check .
./.venv/bin/python -m pyright
```

Results:

- `image-analyzer` core tests: `13 passed`
- targeted e2e + integration: `24 passed`
- full repo baseline: `237 passed in 19.71s`
- `ruff check .`: passed
- `pyright`: `0 errors, 0 warnings, 0 informations`
