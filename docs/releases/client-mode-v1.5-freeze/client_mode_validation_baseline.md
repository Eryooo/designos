# Client Mode Validation Baseline

这是一份冻结版本的最小回归命令集合。后续每次 release candidate 或试点前，至少跑下面这些命令。

## Required Commands

### 1. Golden benchmark sweep

```bash
./.venv/bin/python - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, str(Path('mcp-servers/image-analyzer').resolve()))
import benchmark_harness
benchmark_harness.run_golden_benchmark_sweep(Path('/private/tmp/client-mode-freeze-sweep'))
PY
```

通过标准：

- 生成 `golden_benchmark_sweep.json`
- 生成 `golden_benchmark_sweep.md`
- `final_capable_pass_rate == 1.0`
- `bounded_safety_pass_rate == 1.0`
- `release_blocker_count == 0`

### 2. image-analyzer core

```bash
./.venv/bin/python -m pytest -q mcp-servers/image-analyzer/tests/test_core.py
```

### 3. excel-builder core

```bash
./.venv/bin/python -m pytest -q mcp-servers/excel-builder/tests/test_core.py
```

### 4. integration

```bash
./.venv/bin/python -m pytest -q tests/integration/test_kernel_mcp_integration.py
```

### 5. e2e

```bash
./.venv/bin/python -m pytest -q tests/e2e/test_run_history_closure.py
```

### 6. full pytest

```bash
./.venv/bin/python -m pytest -q
```

### 7. lint

```bash
./.venv/bin/python -m ruff check .
```

### 8. typecheck

```bash
./.venv/bin/python -m pyright
```

## Current Known-Good Results

本次冻结校验的已知通过结果：

- golden benchmark sweep -> `case_count=5`, `final_capable_pass_rate=1.0`, `bounded_safety_pass_rate=1.0`
- `mcp-servers/image-analyzer/tests/test_core.py` -> `40 passed in 7.67s`
- `mcp-servers/excel-builder/tests/test_core.py` -> `16 passed in 1.18s`
- `tests/integration/test_kernel_mcp_integration.py` -> `21 passed in 4.55s`
- `tests/e2e/test_run_history_closure.py` -> `15 passed in 28.83s`
- full `pytest -q` -> `249 passed in 47.57s`
- `ruff check .` -> `All checks passed!`
- `pyright` -> `0 errors, 0 warnings, 0 informations`

## Notes

- `mcp-servers/image-analyzer/tests` 和 repo 根 `tests/` 仍建议分开定向跑；最终再用 full `pytest -q` 做整仓确认。
- 当前如果回归失败，先判定是：
  - `objective input insufficiency` 的边界变化
  - 还是 trusted mapping / critical-path coverage / remediation ingestion 真回退

只有后一类才视为 release blocker。
