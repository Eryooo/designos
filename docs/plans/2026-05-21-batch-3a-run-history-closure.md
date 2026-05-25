# Batch 3A — run/history real closure

## Scope

Only fix the `designos run/history` manifest loop for M1:

- write `runs/<id>/run.yaml` as `running` when `designos run` starts
- write terminal status from real `SkillResult.status`
- map exit codes to `completed=0`, `failed=1`, `paused=2`
- persist `completed_at`, skill version, model, outputs
- make `designos history` read only real `run.yaml` files
- add unit and e2e coverage for completed / failed / paused

Explicitly not included:

- resume execution
- report schema
- `image-analyzer`
- new skill features

## Code changes

- `designos/cli/main.py`
  - add `RUNNING -> terminal` manifest lifecycle for `designos run`
  - switch terminal exit code to follow `SkillResult.status`
  - persist manifest outputs from `SkillResult.artifacts`
  - make `history` ignore stray run folders and invalid manifests
- `kernel/workspace/run_manager.py`
  - add `finish_manifest(...)` helper for terminal manifest writes
- `tests/unit/test_cli_run_history.py`
  - verify startup manifest is `running`
  - verify final manifest status/version/model/outputs
  - verify `history` only lists real manifests
- `tests/e2e/test_run_history_closure.py`
  - verify real CLI exit codes and terminal manifests for completed / failed / paused

## Validation

Commands:

```bash
./.venv/bin/python -m pytest -q tests/unit/test_cli_run_history.py
./.venv/bin/python -m pytest -q tests/e2e/test_run_history_closure.py
./.venv/bin/python -m compileall designos/cli/main.py kernel/workspace/run_manager.py tests/unit/test_cli_run_history.py tests/e2e/test_run_history_closure.py
./.venv/bin/python -m pytest -q tests/unit/test_kernel_workspace.py tests/unit/test_cli.py::test_history_empty_workspace_prints_no_runs tests/unit/test_cli.py::test_history_lists_run_entries
```

Results:

- `tests/unit/test_cli_run_history.py` → `4 passed in 0.65s`
- `tests/e2e/test_run_history_closure.py` → `3 passed in 1.73s`
- related regression checks → `7 passed in 0.31s`
- `compileall` passed

## Sample run.yaml

Generated from a real local CLI run in `/private/tmp/designos-batch3a-sample-ws`:

```yaml
id: 001-demo-completed
skill: demo-completed
version: 3.1.4
status: completed
started_at: '2026-05-21T10:09:26.467203Z'
completed_at: '2026-05-21T10:09:26.469488Z'
model: claude-opus-4-7
depends_on: []
inputs_used: []
outputs: []
checkpoint_decisions: []
```
