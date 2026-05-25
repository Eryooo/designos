# Batch 3B — resume real closure

## Scope

Only fix real checkpoint resume execution for M1:

- `designos resume` really loads checkpoint state and continues execution
- support `--run-id <id>` and default latest paused run
- persist `mode` into `run.yaml` and reuse saved run metadata during resume
- select the latest paused run from checkpoint recency instead of paused-manifest completion timestamps
- rebuild `SkillContext`, `SkillLoader`, config, MCP, and engine from saved run metadata
- write terminal manifest after resume using real `SkillResult.status`
- map exit codes to `completed=0`, `failed=1`, `paused=2`
- allow resume to pause again on a later checkpoint
- add unit and e2e coverage

Explicitly not included:

- report schema
- `image-analyzer`
- `input check`
- `mcp install`
- new skill features

## Code changes

- `designos/cli/main.py`
  - add shared runtime helpers for `run` and `resume`
  - load real paused run manifests and resume from latest paused run when `--run-id` is omitted
  - pick the default paused run by checkpoint `last_updated`
  - validate checkpoint presence before switching the run back to `running`
  - rebuild runtime using saved `skill`, `run_id`, `mode`, and `model`
  - write terminal `run.yaml` after resumed execution using real `SkillResult.status`
- `kernel/contracts/schemas.py`
  - add `mode` to `RunManifest`
- `kernel/workspace/run_manager.py`
  - persist `mode` when a run starts
  - add `resume_manifest(...)` helper to switch paused manifests back to `running`
  - keep `completed_at = null` when the run is only paused
- `tests/unit/test_cli_run_history.py`
  - tighten run manifest assertions so `mode` is covered
- `tests/unit/test_cli_resume.py`
  - cover latest paused run selection
  - cover paused -> resume -> completed
  - cover paused -> resume -> paused again
  - cover missing / corrupt checkpoint failures
- `tests/e2e/test_resume_closure.py`
  - cover real CLI paused -> resume -> completed
  - cover real CLI paused -> resume -> paused again
  - cover real CLI missing / corrupt checkpoint failures

## Validation

Commands:

```bash
./.venv/bin/python -m pytest -q tests/unit/test_cli_resume.py tests/unit/test_cli_run_history.py
./.venv/bin/python -m pytest -q tests/e2e/test_resume_closure.py tests/e2e/test_run_history_closure.py
./.venv/bin/python -m pytest -q tests/unit/test_kernel_checkpoint.py tests/integration/test_skill_pipeline_integration.py tests/unit/test_kernel_workspace.py tests/unit/test_cli.py::test_history_empty_workspace_prints_no_runs tests/unit/test_cli.py::test_history_lists_run_entries
./.venv/bin/python -m compileall designos/cli/main.py kernel/contracts/schemas.py kernel/workspace/run_manager.py tests/unit/test_cli_resume.py tests/e2e/test_resume_closure.py
```

Results:

- `tests/unit/test_cli_resume.py tests/unit/test_cli_run_history.py` -> `8 passed in 0.55s`
- `tests/e2e/test_resume_closure.py tests/e2e/test_run_history_closure.py` -> `7 passed in 4.31s`
- related checkpoint / manifest regressions -> `16 passed in 0.52s`
- `compileall` passed

## Sample paused run.yaml

Generated from a real local CLI run before resume:

```yaml
id: 001-demo-resume-sample
skill: demo-resume-sample
version: 4.2.0
status: paused
started_at: '2026-05-21T11:34:38.205009Z'
completed_at: null
model: claude-opus-4-7
mode: web
depends_on: []
inputs_used: []
outputs: []
checkpoint_decisions: []
```

## Sample resumed run.yaml

Same run after `designos resume`:

```yaml
id: 001-demo-resume-sample
skill: demo-resume-sample
version: 4.2.0
status: completed
started_at: '2026-05-21T11:34:38.205009Z'
completed_at: '2026-05-21T11:34:38.740615Z'
model: claude-opus-4-7
mode: web
depends_on: []
inputs_used: []
outputs: []
checkpoint_decisions: []
```
