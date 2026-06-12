Title: Route B Batch 2 - Evidence Fusion V2 Core
Date: 2026-05-25
Status: done

Summary
- Added a unified evidence-fusion layer in `image-analyzer` so client mode now resolves page/state mappings from the same runtime synthesis of OCR, markdown, directory structure, filename, and draft mapping signals.
- Tightened `trusted` semantics: only mappings that remain `final_delivery_eligible` are counted as trusted for final delivery coverage.
- Stopped derived remediation notes from laundering OCR text into fake independent markdown support.

Runtime changes
- `load_and_analyze` now extracts markdown cues from screenshot-matched sections instead of coarse whole-file fallback whenever `screens-description.md` or per-image `.md` files are present.
- Draft mappings now carry fusion verdict, supporting channels, fusion score, and conflicting candidates; `fusion_summary` aggregates trusted page/state mappings, provisional mappings, conflicts, and unresolved ambiguities.
- `auto_remediation` now preserves original markdown cues and only appends mixed-source derived note cues, so remediation can help fallback and clarification without inflating trusted coverage.
- `delivery-audit` consumes the same fusion outputs and echoes conflict / ambiguity paths into the bounded package.

Validation
- `./.venv/bin/python -m compileall mcp-servers/image-analyzer/core.py mcp-servers/image-analyzer/schemas.py mcp-servers/image-analyzer/tests/test_core.py mcp-servers/excel-builder/core.py mcp-servers/excel-builder/tests/test_core.py tests/integration/test_kernel_mcp_integration.py tests/e2e/test_run_history_closure.py`
- `./.venv/bin/python -m pytest -q mcp-servers/image-analyzer/tests/test_core.py`
- `./.venv/bin/python -m pytest -q mcp-servers/excel-builder/tests/test_core.py`
- `./.venv/bin/python -m pytest -q tests/integration/test_kernel_mcp_integration.py`
- `./.venv/bin/python -m pytest -q tests/e2e/test_run_history_closure.py::test_client_auto_remediation_can_complete_without_user_pause`
- `./.venv/bin/python -m pytest -q`
- `./.venv/bin/python -m ruff check .`
- `./.venv/bin/python -m pyright`

Observed results
- image-analyzer core: 25 passed
- excel-builder core: 13 passed
- kernel MCP integration: 19 passed
- targeted e2e regression: 1 passed
- full pytest: 247 passed
- ruff: passed
- pyright: 0 errors, 0 warnings

Product outcome
- Client mode now eats more of the evidence users already provided instead of asking them to explain or map the same screenshots again.
- OCR + markdown agreement now increases trusted mapping strength; source conflicts stay provisional/conflicting and are minimized into clarification only when truly ambiguous.
- Final delivery coverage and bounded fallback both read from the same fusion summary, so page/state coverage no longer drifts between screenshot analysis, remediation, evidence assessment, and delivery audit.
