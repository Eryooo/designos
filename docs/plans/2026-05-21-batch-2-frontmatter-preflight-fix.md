# Batch 2 Frontmatter to Preflight Fix

Date: 2026-05-21

## Scope

Single source of truth used for this batch:

- `/Users/young/Documents/Codex/desigonos/outputs/agent-design-master-repair-charter.md`
- `/Users/young/Documents/Codex/desigonos/outputs/agent-design-production-audit.md`
- `/Users/young/Documents/Codex/desigonos/outputs/agent-design-repair-batches.md`

Batch target:

- Make `skills/uxeval/SKILL.md` the runtime truth source for version, type, modes, and MCP dependencies
- Wire `SKILL.md frontmatter -> skill config -> preflight -> MCP registry`
- Eliminate `version=0.0.0`, empty `supported_modes`, empty `mcp_servers`, and preflight false positives

Out of scope for this batch:

- CLI fake-closure fixes beyond preflight
- report schema redesign
- `image-analyzer` implementation changes

## Code Changes

Changed files:

- `skills/uxeval/SKILL.md`
- `kernel/contracts/schemas.py`
- `kernel/skill_loader/pipeline_loader.py`
- `kernel/preflight/requirements.py`
- `kernel/preflight/checker.py`
- `designos/cli/main.py`
- `tests/unit/test_kernel_preflight.py`
- `tests/unit/test_kernel_config.py`
- `tests/unit/test_cli.py`
- `skills/uxeval/tests/test_frontmatter_runtime.py`

Implemented:

1. Added real `uxeval` frontmatter: `version`, `type`, `requires.mcp_servers`, `modes`, `inputs`, and `outputs`.
2. Extended runtime MCP config to carry `required_when` and `requires_external`.
3. Updated pipeline loading so MCP dependency declarations are parsed from SKILL frontmatter into `skill.config`.
4. Switched preflight to consume parsed `skill.config.mcp_servers` instead of only a legacy `skill.preflight` attribute.
5. Added builtin MCP availability checks in preflight when a repo-root builtin server is declared.
6. Passed `skill_config` through `load_config()` so `cfg.skill_config` and `cfg.mcp_servers` carry real frontmatter-derived data.
7. Changed CLI MCP wiring to build its registry from `cfg.mcp_servers`.
8. Changed skill search precedence so the current project `skills/` overrides stale global installs, with global skills as fallback.

## Validation

Commands run:

```bash
./.venv/bin/python -m compileall kernel/contracts/schemas.py kernel/skill_loader/pipeline_loader.py kernel/preflight/requirements.py kernel/preflight/checker.py designos/cli/main.py tests/unit/test_kernel_preflight.py tests/unit/test_cli.py skills/uxeval/tests/test_frontmatter_runtime.py
./.venv/bin/python -m pytest tests/unit/test_kernel_preflight.py tests/unit/test_kernel_skill_loader.py tests/unit/test_kernel_config.py tests/unit/test_cli.py::test_preflight_client_mode_passes_when_web_dependency_not_required tests/unit/test_cli.py::test_preflight_web_mode_fails_for_missing_playwright_probe tests/unit/test_cli.py::test_preflight_prefers_repo_skill_over_global_install skills/uxeval/tests/test_frontmatter_runtime.py
./.venv/bin/python -m designos.cli.main preflight uxeval --mode client
./.venv/bin/python -m designos.cli.main preflight uxeval --mode web
./.venv/bin/python - <<'PY'
from kernel.skill_loader.pipeline_loader import load_pipeline_skill
from pathlib import Path
skill = load_pipeline_skill(Path('skills/uxeval'))
print({'version': skill.config.version, 'supported_modes': skill.config.supported_modes, 'mcp_servers': [s.name for s in skill.config.mcp_servers]})
PY
```

Results:

- compile step passed
- targeted tests: `20 passed in 0.57s`
- `load_pipeline_skill(skills/uxeval)` now returns:
  - `version == 1.0.0`
  - `supported_modes == ['web', 'client']`
  - `mcp_servers == ['pdf-parser', 'excel-builder', 'image-analyzer', 'heuristic-engine', 'playwright-driver']`
- `designos preflight uxeval --mode client`: passed
- `designos preflight uxeval --mode web`: failed correctly
  - missing builtin MCP server `playwright-driver`
  - missing external dependency probe `playwright --version`

## Acceptance Check

- `skill.config.version` correct: passed
- `skill.config.supported_modes` correct: passed
- `skill.config.mcp_servers` includes real dependencies: passed
- preflight behavior differs between `client` and `web`: passed
- web-mode missing Playwright fails instead of false-positive passing: passed
- unit and integration coverage added: passed

## Notes

- An unrelated baseline test still expects CLI version `0.1.0` while the current CLI prints `0.1.2`. That mismatch was excluded from the Batch 2 targeted validation because it is not part of the frontmatter/preflight chain.

## Next Batch

Per the repair charter ordering, the next platform batch should address the CLI false-closure path only after the frontmatter/preflight chain is stable.
