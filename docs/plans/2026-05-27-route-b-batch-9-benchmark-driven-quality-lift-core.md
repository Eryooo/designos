# Route B Batch 9 - Benchmark-Driven Quality Lift Core

## Goal

基于 Batch 8 已经落地的 `client_mode_metrics` 和 `benchmark_summary`，不再泛化加功能，而是围绕当前最卡住 client mode 的 2-3 个指标做最小、高杠杆的质量拉升。

这批不放松 final gate，不扩到 web mode / CLI / dashboard。目标是让系统更会把“已有基本合格输入”吃成结果，而不只是更会拦。

## Bottlenecks

本批主攻 3 个指标：

1. `trusted_mapping_rate`
   - 卡点：已有 OCR / markdown / remediation 线索没有稳定转成 trusted mapping，导致 final gate 仍被 `trusted_evidence_sufficiency` 拦住。

2. `critical_path_state_hit_rate`
   - 卡点：P0/P1 页面虽然可能命中了，但关键状态没有被同一份证据可靠吸收，导致主链路 state coverage 不足。

3. `auto_remediation_lift`
   - 卡点：系统能诊断“已有输入可救”，但 remediation 还不够会把同一份输入自动抬到 final-ready。

没有主攻的指标也做了明确归因：

- `first_pass_final_rate`
  - 这批不是靠放松门槛把更多 run 伪装成 first-pass final。
  - 当前提升主要体现在 `auto_remediation_lift`，因为很多场景的问题是“已有输入没吃懂”，不是“真正一开始就已经 final-ready”。

## Scope

只做 Route B Batch 9，不扩到：

- web mode
- 新 CLI
- 前端 dashboard
- 大范围 schema 重构
- 与当前瓶颈指标无关的泛化优化

## Changed Files

- `mcp-servers/image-analyzer/core.py`
- `mcp-servers/image-analyzer/tests/test_core.py`
- `tests/integration/test_kernel_mcp_integration.py`

## Quality Lift Strategy

本批做的是上游质量拉升，不是继续加阻断条件。

### 1. 更强的 OCR / markdown / remediation 互证

- `_mapping_candidate_details()` 现在把 `mixed` cue 纳入 page/state 计分
- state-specific OCR / markdown evidence 会显式参与 page disambiguation
- remediation 派生的页面 cue 不再只是 fallback hint，而是能在强证据下把 mapping 推进到 trusted

### 2. 更严格但更会做成的 fusion 判定

- OCR 和 markdown 状态冲突时，明确打回 `conflicting`
- 多个 markdown/derived cues 同时显式指向不同页面时，打回 `ambiguous`
- 只有在 state evidence 足够强、且 page cue 被独立证据验证后，才允许 trusted

### 3. 修掉 description / remediation 污染导致的“没吃懂”

- 多 section 的 `screens-description.md` 不再把第一段粗暴 fallback 给所有截图
- remediation 候选页会优先围绕 trusted/final-eligible mapping 和 priority missing pages 收敛
- `plan_required_evidence()` 的 pre-run 路径改成和 `load_and_analyze()` 一致：先 draft mapping，再 remediation，再重新应用 mapping

## Expected Metric Impact

这批预期直接拉升：

- `trusted_mapping_rate`
- `critical_path_state_hit_rate`
- `critical_path_page_hit_rate`
- `auto_remediation_lift`

并间接推动：

- `final_delivery_ready_rate`
- `clarification_item_count` 维持不升或下降
- `supplement_request_precision` 更少把“没吃懂”误报成“真缺料”

## Benchmark Compare Sample

真实对比样例已生成：

- `/private/tmp/route-b-batch9-sample/benchmark-compare/benchmark_compare.json`
- `/private/tmp/route-b-batch9-sample/benchmark-compare/benchmark_compare.md`

样例结论：

- 场景：`state_specific_evidence_uplift_without_gate_relaxation`
- 同一份输入在旧 ingestion 逻辑下：`fallback_safe`
- 在本批质量拉升后：`final_delivery_ready`

核心指标变化：

- `trusted_mapping_rate`: `0.600 -> 1.000` (`+0.400`)
- `critical_path_state_hit_rate`: `0.500 -> 1.000` (`+0.500`)
- `critical_path_page_hit_rate`: `0.500 -> 1.000` (`+0.500`)
- `auto_remediation_lift`: `0.000 -> 0.400` (`+0.400`)
- `clarification_item_count`: `0 -> 0`

这说明提升来自“更会吃已有输入”，而不是“要求更多人工补充”或“放松 final gate”。

## Validation

执行命令：

```bash
./.venv/bin/python -m compileall \
  mcp-servers/image-analyzer/core.py \
  mcp-servers/image-analyzer/schemas.py \
  mcp-servers/image-analyzer/tests/test_core.py \
  tests/integration/test_kernel_mcp_integration.py

./.venv/bin/python -m pytest -q mcp-servers/image-analyzer/tests/test_core.py
./.venv/bin/python -m pytest -q tests/integration/test_kernel_mcp_integration.py
./.venv/bin/python -m pytest -q
./.venv/bin/python -m ruff check .
./.venv/bin/python -m pyright
```

结果：

- `compileall` 通过
- `mcp-servers/image-analyzer/tests/test_core.py` -> `39 passed in 6.03s`
- `tests/integration/test_kernel_mcp_integration.py` -> `21 passed in 3.23s`
- 全量 `pytest -q` -> `249 passed in 47.78s`
- `ruff check .` -> `All checks passed!`
- `pyright` -> `0 errors, 0 warnings, 0 informations`

补充：

- `mcp-servers/image-analyzer/tests` 和 repo 根 `tests/` 不能混在同一条 pytest 命令里跑，否则会触发现有的 `ImportPathMismatchError`。本批验证按真实可运行方式拆开执行，最终全量 `pytest -q` 已通过。

## Closeout

Batch 9 不是再加新 gate，而是把 Batch 8 暴露出来的 ingestion/fusion 瓶颈直接做掉。结果是：

- system ingestion gap 能被 benchmark 明确观察到
- 同一份输入更容易被自动吃成 trusted coverage
- final gate 仍维持原标准
- client mode 更接近“更会做成”，而不是只会更早给出 supplement/fallback
