# Route B Batch 8 - Metrics Instrumentation + Benchmark Harness Core

## Goal

把 client mode 从“功能修复链路”收成“指标驱动系统”：

- 在 runtime 里产出统一 `client_mode_metrics`
- 在同一条 client-mode 运行链里产出 `benchmark_summary`
- 把 coverage / trust / success / human burden 四类指标固定成 machine-readable contract
- 生成稳定 benchmark artifact：
  - `outputs/benchmark/client_mode_benchmark_summary.json`
  - `outputs/benchmark/client_mode_benchmark_summary.md`

## Scope

只做 Route B Batch 8，不扩到：

- OCR 新能力
- web mode
- 新 CLI
- 前端 dashboard
- report 大改

## Changed Files

- `mcp-servers/image-analyzer/schemas.py`
- `mcp-servers/image-analyzer/core.py`
- `mcp-servers/image-analyzer/tests/test_core.py`
- `mcp-servers/excel-builder/core.py`
- `mcp-servers/excel-builder/tests/test_core.py`
- `tests/integration/test_kernel_mcp_integration.py`

## Runtime Contract

新增：

- `EvidenceAssessment.client_mode_metrics`
- `EvidenceAssessment.benchmark_summary`

其中 `client_mode_metrics` 至少覆盖：

- coverage metrics
- trust metrics
- success / throughput metrics
- human burden metrics

`benchmark_summary` 会明确说明：

- 当前 `delivery_status`
- 哪些指标达标
- 哪些指标未达标
- 离 90%+ 还差什么
- 当前更像“输入真不足”还是“系统还没把已有输入吃干净”

## Benchmark Artifacts

Image-analyzer runtime 会写：

- `outputs/benchmark/client_mode_benchmark_summary.json`
- `outputs/benchmark/client_mode_benchmark_summary.md`

Delivery audit 如果继续执行，会用 audited status 和 actual issue leakage 覆盖同一路径，保证 run-level benchmark 与最终交付语义一致。

## Validation

执行命令：

```bash
./.venv/bin/python -m compileall \
  mcp-servers/image-analyzer/core.py \
  mcp-servers/image-analyzer/schemas.py \
  mcp-servers/image-analyzer/tests/test_core.py \
  mcp-servers/excel-builder/core.py \
  mcp-servers/excel-builder/tests/test_core.py \
  tests/integration/test_kernel_mcp_integration.py

./.venv/bin/python -m pytest -q mcp-servers/image-analyzer/tests/test_core.py
./.venv/bin/python -m pytest -q mcp-servers/excel-builder/tests/test_core.py
./.venv/bin/python -m pytest -q tests/integration/test_kernel_mcp_integration.py
./.venv/bin/python -m pytest -q
./.venv/bin/python -m ruff check .
./.venv/bin/python -m pyright
```

结果：

- `compileall` 通过
- `mcp-servers/image-analyzer/tests/test_core.py` -> `37 passed in 5.12s`
- `mcp-servers/excel-builder/tests/test_core.py` -> `16 passed in 0.88s`
- `tests/integration/test_kernel_mcp_integration.py` -> `21 passed in 3.20s`
- 全量 `pytest -q` -> `249 passed in 50.80s`
- `ruff check .` -> `All checks passed!`
- `pyright` -> `0 errors, 0 warnings, 0 informations`

补充：

- `mcp-servers/image-analyzer/tests` 和 repo 根 `tests/` 不能放在同一条 pytest 命令里混跑，否则会触发现有的 `ImportPathMismatchError`。本批验证按真实可运行方式拆开执行，最终全量 `pytest -q` 也已通过。

## Sample

本批生成过一个真实 supplement case 样例：

- `/private/tmp/route-b-batch8-sample/outputs/benchmark/client_mode_benchmark_summary.json`
- `/private/tmp/route-b-batch8-sample/outputs/benchmark/client_mode_benchmark_summary.md`

这个样例会明确显示：

- `delivery_status = supplement_required`
- `input_quality_class = missing_evidence`
- `critical_path_page_hit_rate / critical_path_state_hit_rate / trusted_mapping_rate`
- `auto_remediation_lift`
- `clarification_item_count`
- `distance_to_90_plus`
- `targeted_acquisition_plan_path`

## Closeout

Batch 8 把 Route B 从“只会解释为什么没过线”推进到了“每一轮 run 都能稳定产出可比较的 runtime benchmark snapshot”。后续批次不需要再猜“到底更会做成了，还是只是更会拦了”，可以直接横向比指标。
