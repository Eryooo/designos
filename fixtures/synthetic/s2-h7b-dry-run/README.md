# S2-H7B Dry-Run Synthetic Fixtures

**状态**: SYNTHETIC / SANITIZED

## 用途

本批 synthetic fixtures 用于 S2-H7B offline dry-run execution，验证 H1-H7A 质量机制链路的可执行性。

不含真实业务数据、真实 PRD、真实截图、真实 URL、真实客户信息。

## 故意制造的 synthetic 问题

为验证质量门机制，本批 fixtures 故意制造 3 类 synthetic 问题：

1. **输入缺口问题**:
   - `synthetic-prd.md` 缺少明确成功指标
   - 用于触发 input gate: `ready_with_assumptions` 或 `needs_user_clarification`

2. **过程降级问题**:
   - `synthetic-screenshot-notes.md` 缺少关键页面状态描述
   - 用于触发 checkpoint: `continue_with_gaps` 或 `degrade_scope`

3. **跨 skill 一致性问题**:
   - `synthetic-product-brief.md` 的 target audience 与 `synthetic-prd.md` 的 user role 出现轻微不一致
   - 用于触发 consistency: `needs_reconciliation` 或 `blocked_inconsistent`

## Fixtures 清单

- `synthetic-product-brief.md` — 用于 ai-analytics / ip-design / brand-creative
- `synthetic-prd.md` — 用于 prd2proto
- `synthetic-brand-brief.md` — 用于 brand-creative
- `synthetic-screenshot-notes.md` — 用于 uxeval

## 不包含

- 真实项目材料
- 真实业务文案
- 真实客户信息
- 真实 URL / email / token
- 真实本地路径
- 敏感数据
