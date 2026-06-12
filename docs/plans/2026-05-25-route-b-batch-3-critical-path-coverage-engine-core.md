# Route B Batch 3: Critical Path Coverage Engine Core

- Date: 2026-05-25
- Status: done
- Scope: only client-mode critical-path-first coverage and its runtime/audit tests

## Summary

This batch upgrades `uxeval` client mode from generic page coverage to critical-business-path-first coverage.

Key result:

- `final_delivery_ready` is now explicitly constrained by P0/P1 critical-path coverage
- `fallback_safe` is now explicitly constrained by P0 critical-path coverage
- secondary page coverage can no longer mask a missing P0 path
- missing P2 coverage no longer blocks final delivery when P0/P1 pass lines are met

## Runtime changes

### image-analyzer

- Added critical-path runtime schema:
  - `CriticalPathDefinition`
  - `CriticalPathCoverageRecord`
  - `CriticalPathCoverageSummary`
- Capture mission now emits path-level coverage requirements and pass-line rationale.
- Screenshot analysis now computes deterministic `critical_path_coverage_summary`.
- Evidence assessment now:
  - blocks final delivery on failing P0/P1 paths
  - blocks fallback on failing P0 paths
  - explains supplement/fallback at the critical-path layer
- Final/fallback gating no longer treats P2 gaps as automatic blockers.
- OCR-available state coverage now uses the same runtime semantics in generic coverage and critical-path coverage, avoiding false fallback downgrades.

### delivery audit

- `excel-builder.audit_delivery_readiness()` now consumes critical-path coverage directly.
- A claimed `final_delivery_ready` run is downgraded if critical-path final gates still fail.

## Validation

Commands run:

```bash
./.venv/bin/python -m pytest -q mcp-servers/image-analyzer/tests/test_core.py
./.venv/bin/python -m pytest -q mcp-servers/excel-builder/tests/test_core.py
./.venv/bin/python -m pytest -q tests/integration/test_kernel_mcp_integration.py
./.venv/bin/python -m pytest -q
./.venv/bin/python -m ruff check .
./.venv/bin/python -m pyright
```

Results:

- `mcp-servers/image-analyzer/tests/test_core.py` -> `31 passed`
- `mcp-servers/excel-builder/tests/test_core.py` -> `14 passed`
- `tests/integration/test_kernel_mcp_integration.py` -> `20 passed`
- full `pytest -q` -> `248 passed in 37.74s`
- `ruff check .` -> `All checks passed!`
- `pyright` -> `0 errors, 0 warnings, 0 informations`

## Product outcome

- A run with many screenshots but missing a P0 path now fails deterministically, even when average coverage is high.
- A run with strong P0/P1 coverage can now pass final delivery even if a P2 page is still absent.
- Fallback and supplement outputs now explain *which* critical path is below the pass line, instead of only reporting generic average coverage gaps.
