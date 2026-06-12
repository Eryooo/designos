# Route B Batch 6 - First-Pass Success Engine Core

日期：2026-05-26

## 目标

在不放松 `final_delivery_ready` 门槛的前提下，把 client mode 的 upstream 成功率收真：

- 输出 `first_pass_success_breakdown`
- 区分“真缺料”与“已有证据没吃懂”
- 让 auto-remediation 优先做高杠杆提分，而不是只会拦截

## 已完成代码

- `mcp-servers/image-analyzer/schemas.py`
  - 为 `EvidenceAssessment` 增加 `first_pass_success_breakdown`
- `mcp-servers/image-analyzer/core.py`
  - 增加 `first_pass_success_breakdown` 生成逻辑
  - 增加 supplement cause 分类：
    - `missing_evidence`
    - `weak_readability`
    - `fusion_insufficient`
    - `mapping_unresolved`
    - `critical_path_not_met`
  - auto-remediation 优先围绕 P0/P1 与 sectioned markdown 做 trusted mapping uplift
  - 输出 pre/post remediation 的 critical-path 与 trusted-mapping 对比
  - 增加最小类型 coercion helper，确保 Batch 6 运行时新增契约通过 `pyright`
- `mcp-servers/image-analyzer/tests/test_core.py`
  - 补齐 first-pass uplift / 真缺料 / fusion 不足三类回归
- `tests/integration/test_kernel_mcp_integration.py`
  - 补齐 runtime 集成断言

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
- `mcp-servers/image-analyzer/tests/test_core.py`：`35 passed`
- `tests/integration/test_kernel_mcp_integration.py`：`21 passed`
- 全量 `pytest -q`：`249 passed in 53.74s`
- `ruff check .`：`All checks passed!`
- `pyright`：`0 errors, 0 warnings, 0 informations`

## 收尾结论

Batch 6 的功能实现已经完成；本次 closeout 唯一补齐的是 `pyright` 类型收尾与批次记录落盘，没有新增能力，也没有改变 final gate。
