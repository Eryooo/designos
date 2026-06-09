# Route B Batch 10 - Golden Benchmark Sweep

## Goal

不再继续点状修能力，而是用固定 golden benchmark cases 对当前 client mode 做一次统一 sweep，判断：

- 哪些场景已经接近或达到 V1.5 线
- 哪些场景仍明显不达标
- 当前最大的剩余瓶颈是什么
- 是否建议进入 Freeze，还是还需要最后一批质量拉升

## Scope

只做 Route B Batch 10：

- 固定 golden benchmark cases
- 运行 sweep
- 生成 machine-readable + human-readable 汇总
- 如果 sweep 暴露 release blocker，只做最小修正

不扩到：

- web mode
- 新 CLI
- OCR 新能力
- report 大改
- 泛化平台化重构

## Changed Files

- `mcp-servers/image-analyzer/benchmark_harness.py`
- `mcp-servers/image-analyzer/core.py`
- `mcp-servers/image-analyzer/tests/test_core.py`

## Golden Cases

本批固定 5 类 cases：

1. `case-final-mainline`
   - 高质量输入、主链路覆盖充分

2. `case-hq-no-description`
   - 高质量截图，但说明不足

3. `case-salvageable`
   - 输入可挽救，目标是验证 system ingestion / remediation 是否足够把已有输入吃成结果

4. `case-missing-evidence`
   - 真缺关键证据

5. `case-complex-multi-module`
   - 复杂多模块、多状态的高复杂度 final 场景

## Sweep Artifacts

Golden sweep 会写：

- `golden_benchmark_sweep.json`
- `golden_benchmark_sweep.md`

实际样例已生成到：

- `/private/tmp/route-b-batch10-sweep/golden_benchmark_sweep.json`
- `/private/tmp/route-b-batch10-sweep/golden_benchmark_sweep.md`

## Release Blocker Found and Fixed

Sweep 首轮暴露了一个明确 blocker：

- `case-complex-multi-module` 的 `trusted_mapping_rate` 出现 `2.0`

原因不是 final gate 放松，而是 benchmark 指标计算没有把 rate 上界收敛到 `[0, 1]`。

本批做的最小修正：

- `core._trusted_mapping_rate_snapshot()` 改成复用 `_bounded_rate(...)`

修正后：

- `trusted_mapping_rate` 恢复为 `1.0`
- 重新跑 sweep 后，case 结果稳定

## Sweep Result Snapshot

当前 sweep 聚合结果：

- `case_count = 5`
- `v1_5_target_met_count = 4`
- `v1_5_target_met_rate = 0.800`
- `final_delivery_ready_case_count = 3`
- `supplement_required_case_count = 1`
- `blocked_case_count = 1`
- `final_capable_pass_rate = 0.667`
- `bounded_safety_pass_rate = 1.000`

当前结论：

- strongest case: `case-final-mainline`
- weakest case: `case-hq-no-description`
- largest remaining bottleneck metric: `trusted_mapping_rate`
- freeze recommendation:
  - `Do one more quality-lift batch before Freeze: at least one final-capable golden case still fails the V1.5 line.`

## Interpretation

最关键的发现不是“系统会不会拦”，而是：

- `case-salvageable` 已经能到 `final_delivery_ready`
- 但它的 `trusted_mapping_rate` 仍然只有 `0.8`
- 所以它还没过 V1.5 线

这说明当前剩余最大问题不是：

- 真缺料
- clarification 太多
- P0/P1 主链路没命中

而是：

- 已有输入在 salvageable 场景下，仍没有被足够稳定地提升成 `90%+ trusted coverage`

## Validation

执行命令：

```bash
./.venv/bin/python -m compileall \
  mcp-servers/image-analyzer/benchmark_harness.py \
  mcp-servers/image-analyzer/core.py \
  mcp-servers/image-analyzer/tests/test_core.py

./.venv/bin/python -m pytest -q mcp-servers/image-analyzer/tests/test_core.py -k golden_benchmark_sweep_generates_stable_case_compare
./.venv/bin/python -m pytest -q mcp-servers/image-analyzer/tests/test_core.py
./.venv/bin/python -m pytest -q tests/integration/test_kernel_mcp_integration.py
./.venv/bin/python -m pytest -q
./.venv/bin/python -m ruff check .
./.venv/bin/python -m pyright
```

结果：

- `compileall` 通过
- golden sweep targeted test -> `1 passed, 39 deselected in 0.79s`
- `mcp-servers/image-analyzer/tests/test_core.py` -> `40 passed in 5.08s`
- `tests/integration/test_kernel_mcp_integration.py` -> `21 passed in 2.58s`
- 全量 `pytest -q` -> `249 passed in 33.26s`
- `ruff check .` -> 通过
- `pyright` -> 通过

## Closeout

Batch 10 的产出不是新能力，而是一条固定的验收基线：

- client mode 在哪些场景已经接近 V1.5
- 哪些场景现在仍然只是 bounded-safe
- 哪些差距仍是系统能力问题，而不是输入客观不足

当前最重要的剩余瓶颈已经被 sweep 明确定位到：

- `trusted_mapping_rate`

如果继续做 Batch 11，应该围绕这个指标做最后一轮质量拉升，而不是再泛化加功能。
