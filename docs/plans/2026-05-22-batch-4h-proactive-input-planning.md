# Batch 4H — Client Proactive Input Planning

## Scope

Only Batch 4H:

- add client-mode proactive input planning before screenshot analysis
- make planning outputs runtime-consumable by `screenshot-loading`
- surface one-shot pre-run supplement guidance for obvious critical input gaps
- keep the same basic gap from re-pausing forever on resume

Out of scope:

- new CLI commands
- new remote services
- OCR capability expansion
- large schema or architecture rewrites

## What Changed

### 1. `image-analyzer` gained deterministic planning

- Added `plan_required_evidence(...)` in `mcp-servers/image-analyzer/core.py`
- Added planning result models in `mcp-servers/image-analyzer/schemas.py`
- Added MCP exposure in `mcp-servers/image-analyzer/server.py`

Runtime outputs:

- `required_evidence_plan`
- `critical_page_requirements`
- `critical_state_requirements`
- `evidence_input_guidance`

Planning behavior:

- derive critical pages from `task_checklist_lite` + modules
- derive page-level critical states
- inspect current screenshot bundle before heavy OCR/runtime analysis
- give one-shot structured supplement actions when obvious critical pages/states/descriptions are missing
- persist a pre-run planning gap signature and fail fast on unchanged repeat resume instead of looping on the same pause

### 2. `uxeval` pipeline now plans before screenshot analysis

Updated `skills/uxeval/pipeline.yaml`:

- inserted `evidence-planning` tool stage for client mode
- added a `QG0` gate before `screenshot-loading`
- `screenshot-loading` now consumes `required_evidence_plan`

Effect:

- obvious base input gaps are surfaced once before the run sinks time into later stages
- later `evidence_assessment` is plan-aware instead of relying only on generic after-the-fact coverage heuristics

### 3. Downstream runtime now follows the same plan

- `load_and_analyze(...)` now accepts `required_evidence_plan`
- `coverage_summary` now includes plan-derived fields such as:
  - `planned_page_count`
  - `matched_planned_page_count`
  - `missing_critical_pages`
  - `missing_planned_states`
  - `missing_required_description_pages`
- `excel-builder` delivery-audit bundle now preserves these plan-derived gaps inside supplement artifacts

## Validation

### Targeted

```bash
cd /Users/young/Documents/Codex/Agent-design/mcp-servers/image-analyzer
../../.venv/bin/python -m pytest -q tests/test_core.py

cd /Users/young/Documents/Codex/Agent-design
./.venv/bin/python -m pytest -q \
  skills/uxeval/tests/test_frontmatter_runtime.py \
  skills/uxeval/tests/test_pipeline_integration.py \
  tests/integration/test_kernel_mcp_integration.py \
  tests/e2e/test_run_history_closure.py
```

Results:

- `image-analyzer/tests/test_core.py` → `17 passed in 0.61s`
- runtime / pipeline / integration / e2e set → `74 passed in 21.97s`

### Full baseline

```bash
./.venv/bin/python -m pytest -q
./.venv/bin/python -m ruff check .
./.venv/bin/python -m pyright
./.venv/bin/python -m compileall \
  mcp-servers/image-analyzer/core.py \
  mcp-servers/image-analyzer/schemas.py \
  mcp-servers/image-analyzer/server.py \
  mcp-servers/excel-builder/core.py \
  skills/uxeval/pipeline.yaml \
  skills/uxeval/SKILL.md \
  skills/uxeval/prompts/05b-screenshot-analysis.md \
  skills/uxeval/reference/m05-证据采集.md \
  tests/e2e/test_run_history_closure.py \
  skills/uxeval/tests/test_pipeline_integration.py \
  skills/uxeval/tests/test_frontmatter_runtime.py \
  tests/integration/test_kernel_mcp_integration.py
```

Results:

- `pytest -q` → `246 passed in 36.99s`
- `ruff check .` → `All checks passed!`
- `pyright` → `0 errors, 0 warnings, 0 informations`
- `compileall` → passed
