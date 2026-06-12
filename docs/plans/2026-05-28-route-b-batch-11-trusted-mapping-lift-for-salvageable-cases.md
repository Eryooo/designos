# Route B Batch 11 - Trusted Mapping Lift for Salvageable Cases

## Goal

只针对 salvageable case 的 `trusted_mapping_rate` 瓶颈做最后一轮高杠杆质量拉升。

这批不放松 final gate，不扩到 web mode / OCR 新能力 / CLI / dashboard。目标是把：

- salvageable case 的 `trusted_mapping_rate`
- 从 `0.8`
- 拉到 `0.9+`

并让它真正跨过 V1.5 freeze 线。

## Bottleneck Diagnosis

Batch 10 golden sweep 已经明确：

- salvageable case 已经能到 `final_delivery_ready`
- `critical_path_page_hit_rate = 1.0`
- `critical_path_state_hit_rate = 1.0`
- `clarification_item_count = 0`
- 但 `trusted_mapping_rate = 0.8`

实际卡点只剩一张图：

- `shot-05.png`

根因不是：

- P0/P1 主链路没覆盖
- clarification 不足
- 真缺料

而是：

- markdown section 标题是 `通知中心`
- 说明正文里给出的强 cue 是 `消息中心`
- OCR 也只识别到 `消息中心`
- 旧的 section 绑定规则主要依赖 title overlap / exact filename / 粗 token overlap
- 结果这张图没有被稳定绑到 `通知中心`
- 最终停在 `4/5 trusted = 0.8`

## Scope

只做 Route B Batch 11，不扩到：

- web mode
- OCR 新能力
- 新 CLI
- dashboard
- 大范围 schema 重构

## Changed Files

- `mcp-servers/image-analyzer/core.py`
- `mcp-servers/image-analyzer/benchmark_harness.py`
- `mcp-servers/image-analyzer/tests/test_core.py`

## Quality Lift

### 1. 更强的 markdown section -> screenshot 精确绑定

`core._select_description_sections()` 现在不再只依赖：

- title token overlap
- exact filename match
- 粗粒度 token overlap

而是新增：

- `title_substring_hits`
- `body_substring_hits`

但只接受 **3 字及以上** 的高信息量片段，避免把 `首页` 这种短通用词误扩散到错误 section。

这让：

- `通知中心`
- `页面标题为消息中心`
- `OCR=消息中心`

这种 salvageable 证据能被稳定绑定到同一页。

### 2. 不放松 trusted 标准

这次没有做：

- 把 `medium` / `provisional` 直接算成 trusted
- 放松 final gate
- 弱化 verification discipline

提升来自：

- 更精准地把已有 markdown section 绑定给正确截图
- 让 OCR / markdown / remediation 的互证真正落到同一页

## Benchmark Compare

真实前后对比样例：

- `/private/tmp/route-b-batch11-salvageable-compare/salvageable_benchmark_compare.json`
- `/private/tmp/route-b-batch11-salvageable-compare/salvageable_benchmark_compare.md`

核心变化：

- `delivery_status`: `final_delivery_ready -> final_delivery_ready`
- `trusted_mapping_rate`: `0.800 -> 1.000`
- `critical_path_page_hit_rate`: `1.000 -> 1.000`
- `critical_path_state_hit_rate`: `1.000 -> 1.000`
- `auto_remediation_lift`: `0.400 -> 0.600`
- `clarification_item_count`: `0 -> 0`
- `v1_5_target_met`: `false -> true`

这说明：

- final gate 没变
- bounded / blocked 边界没变
- 变化只来自“系统更会把 salvageable 输入吃成 trusted coverage”

## Golden Sweep Update

重新跑 sweep 后：

- `/private/tmp/route-b-batch11-sweep/golden_benchmark_sweep.json`
- `/private/tmp/route-b-batch11-sweep/golden_benchmark_sweep.md`

聚合结果变成：

- `v1_5_target_met_rate = 1.0`
- `final_capable_pass_rate = 1.0`
- `bounded_safety_pass_rate = 1.0`
- `largest_remaining_bottleneck_metric = objective_input_insufficiency`
- `freeze_recommendation = Recommend Freeze`

也就是说：

- final-capable golden cases 全部过线
- 剩余 bounded cases 的失败来自客观输入不足，而不是系统质量缺口

## Validation

执行命令：

```bash
./.venv/bin/python -m compileall \
  mcp-servers/image-analyzer/core.py \
  mcp-servers/image-analyzer/benchmark_harness.py \
  mcp-servers/image-analyzer/tests/test_core.py

./.venv/bin/python -m pytest -q mcp-servers/image-analyzer/tests/test_core.py -k "sectioned_markdown_remediation_improves_first_pass_success_without_lowering_final_gate or golden_benchmark_sweep_generates_stable_case_compare or benchmark_metrics_distinguish_salvageable_input_from_true_missing_evidence"
./.venv/bin/python -m pytest -q mcp-servers/image-analyzer/tests/test_core.py
./.venv/bin/python -m pytest -q tests/integration/test_kernel_mcp_integration.py
./.venv/bin/python -m pytest -q
./.venv/bin/python -m ruff check .
./.venv/bin/python -m pyright
```

结果：

- `compileall` 通过
- targeted salvageable regressions -> `3 passed, 37 deselected in 1.35s`
- `mcp-servers/image-analyzer/tests/test_core.py` -> `40 passed in 6.41s`
- `tests/integration/test_kernel_mcp_integration.py` -> `21 passed in 3.97s`
- 全量 `pytest -q` -> `249 passed in 46.86s`
- `ruff check .` -> `All checks passed!`
- `pyright` -> `0 errors, 0 warnings, 0 informations`

## Closeout

Batch 11 的本质不是“让 final 更容易过”，而是：

- 把 salvageable case 中最后一张没被 trusted 的图吃进来
- 让 trusted coverage 从 `0.8` 抬到 `1.0`
- 让 V1.5 freeze 线从“差最后 0.1”变成“已过线”

如果后续要继续做 Route B，重点就不再是 salvageable trusted mapping，而是：

- 是否还要继续降低对客观缺料场景的用户负担
- 或转去 web mode / 其他 skill 的工厂化
