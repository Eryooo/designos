# Route B Batch 7 - Targeted Evidence Acquisition Core

日期：2026-05-26

## 目标

把 client mode 从“知道缺什么”升级成“知道下一步先补哪一个最值钱”，并用指标收益来排序补料动作。

本批只做：

- targeted acquisition contract
- deterministic acquisition scoring
- critical-path-first supplement prioritization
- clarification / screenshot / markdown description 三类动作分流
- 对应测试与验证

不做：

- OCR 新能力扩展
- web mode
- 新 CLI
- report 大改

## 已完成实现

### 1. Runtime contract

在 `mcp-servers/image-analyzer/schemas.py` 新增：

- `TargetedMetricLift`
- `TargetedAcquisitionItem`
- `TargetedAcquisitionPlan`
- `EvidenceAssessment.targeted_acquisition_plan`

每个 acquisition item 现在包含：

- `target_page`
- `target_state`
- `priority`
- `affected_critical_paths`
- `expected_unlocks_final_delivery`
- `expected_metric_lift`
- `why_this_first`
- `suggested_input_form`

### 2. Targeted acquisition engine

在 `mcp-servers/image-analyzer/core.py` 增加 deterministic builder：

- 优先补能闭合 `P0/P1` critical path 的页面 / 状态
- 优先把 `provisional -> trusted`
- clarification 只在“已有证据足够、只差少量确认”时排前
- 大面积缺料不会误走 clarification
- `nice_to_have_later` 不再混入 feature label，只保留真实 page 目标

### 3. Runtime feedback loop

targeted acquisition 结果已经回流到：

- `EvidenceAssessment.targeted_acquisition_plan`
- `required_actions`
- `coverage_summary`
- `image_analysis.summary`

并显式映射到：

- `critical_path_coverage`
- `first_pass_success_breakdown`
- `final / fallback / supplement` 判定

### 4. User-facing artifact

当提供 `output_dir` 时，会生成：

- `outputs/targeted-acquisition/targeted_acquisition_plan.md`
- `outputs/targeted-acquisition/targeted_acquisition_plan.json`

## 验证命令

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

## 验证结果

- `compileall`：通过
- `mcp-servers/image-analyzer/tests/test_core.py`：`36 passed in 4.68s`
- `tests/integration/test_kernel_mcp_integration.py`：`21 passed in 2.90s`
- 全量 `pytest -q`：`249 passed in 41.98s`
- `ruff check .`：`All checks passed!`
- `pyright`：`0 errors, 0 warnings, 0 informations`

## 本批收口

Batch 7 已把“补料建议”收成 runtime 可执行能力：

- 不再泛泛建议“再补几张关键截图”
- 明确给出最高收益的下一步动作
- 同时解释它会抬升哪些指标，以及是否有望推动 final gate
