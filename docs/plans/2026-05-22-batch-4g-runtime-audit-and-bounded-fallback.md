# Batch 4G - Runtime Audit And Bounded Fallback

## Scope

Only Batch 4G:

- add a deterministic `delivery-audit` stage between Stage 6 and Stage 7
- stop trusting Stage 6 `delivery_assessment` for final report release
- productize `fallback_safe` into a bounded, directly usable intermediate package
- keep the implementation in existing tool/runtime layers without new CLI commands

## What Changed

### 1. Final report release now depends on runtime audit, not LLM self-report

`skills/uxeval/pipeline.yaml` now inserts a `delivery-audit` tool stage after
`issue-attribution`:

- inputs: `issues`, `unverified_issues`, `evidence_assessment`, `delivery_assessment`
- outputs: `audited_delivery_assessment`, `delivery_audit_bundle`

Stage 7 now gates on:

- `audited_delivery_assessment.delivery_status`

instead of trusting Stage 6 `delivery_assessment`.

### 2. Deterministic audit rules are enforced in `excel-builder`

The new `audit_delivery_readiness()` tool in `mcp-servers/excel-builder/core.py`
enforces hard rules such as:

- any main-list issue with `verification_status != verified` disqualifies final delivery
- any main-list issue missing `evidence_refs` or `evidence_basis` disqualifies final delivery
- key `unverified_issues` prevent `final_delivery_ready`
- unresolved evidence coverage gaps prevent `final_delivery_ready`

### 3. `fallback_safe` now generates a real bounded package

The runtime always writes a deterministic `delivery_audit_bundle/` containing:

- `bounded_issue_pass.md`
- `unverified_issues.json`
- `supplement_request.md`
- `audited_delivery_assessment.json`
- `manifest.json`

For `fallback_safe`, this becomes the user-facing bounded delivery package.
For `final_delivery_ready`, it remains the audit trail proving why final report
release is allowed.

### 4. Runtime outputs and docs were aligned

- new output type: `delivery_audit_bundle`
- `skills/uxeval/SKILL.md` now declares the audit bundle output and the new 6.5 audit stage
- constitution and prompt text now refer to `audited_delivery_assessment` as the final release authority

## Validation

Commands:

```bash
cd mcp-servers/excel-builder && ../../.venv/bin/python -m pytest -q tests/test_core.py
./.venv/bin/python -m pytest -q skills/uxeval/tests/test_frontmatter_runtime.py skills/uxeval/tests/test_pipeline_integration.py tests/integration/test_kernel_mcp_integration.py tests/e2e/test_run_history_closure.py
./.venv/bin/python -m pytest -q
./.venv/bin/python -m ruff check .
./.venv/bin/python -m pyright
```

Results:

- excel-builder core tests: `13 passed`
- targeted uxeval/integration/e2e: `69 passed`
- full repo baseline: `241 passed in 29.43s`
- `ruff check .`: passed
- `pyright`: `0 errors, 0 warnings, 0 informations`
