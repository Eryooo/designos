# S2-H7B Offline Dry-Run Execution

**批次**: S2-H7B
**时间**: 2026-06-15
**状态**: COMPLETED

---

## 1. 本批目标与边界

### 目标

用 synthetic / sanitized fixture 跑一轮完整 offline dry-run，验证 H1-H7A 质量机制链路是否可执行。

### 不是目标

- 不追求漂亮结论
- 不验证模型生成质量
- 不使用真实 PRD / 截图 / 业务数据

### 边界

- 仅用 synthetic / sanitized fixture
- 外部 workspace raw outputs 不提交到仓库
- 仓库只回灌脱敏总结和机制问题

---

## 2. Workspace 创建说明

外部 workspace 路径（占位符）：
```
<DESIGNOS_WORKSPACE_ROOT>/
  runs/
  evidence/
  batches/
  exports/
```

本批创建了 5 个 run 目录：
- `<DESIGNOS_WORKSPACE_ROOT>/runs/RUN-20260615-001-ai-analytics`
- `<DESIGNOS_WORKSPACE_ROOT>/runs/RUN-20260615-002-prd2proto`
- `<DESIGNOS_WORKSPACE_ROOT>/runs/RUN-20260615-003-uxeval`
- `<DESIGNOS_WORKSPACE_ROOT>/runs/RUN-20260615-004-ip-design`
- `<DESIGNOS_WORKSPACE_ROOT>/runs/RUN-20260615-005-brand-creative`

每个 run 目录包含：
- `run-manifest.yaml`
- `inputs/`
- `outputs/`
- `logs/`
- `gates/` (input-quality.json / progressive-checkpoints.json / cross-skill-consistency.json / self-review.json)
- `diagnostic-summary.md`
- `diagnostic-summary.json`
- `sanitized-issue-candidate.md`

这些 raw outputs 不提交到仓库。

---

## 3. Synthetic Fixture 清单

仓库内 synthetic fixtures（已提交）：
- `fixtures/synthetic/s2-h7b-dry-run/README.md`
- `fixtures/synthetic/s2-h7b-dry-run/synthetic-product-brief.md`
- `fixtures/synthetic/s2-h7b-dry-run/synthetic-prd.md`
- `fixtures/synthetic/s2-h7b-dry-run/synthetic-brand-brief.md`
- `fixtures/synthetic/s2-h7b-dry-run/synthetic-screenshot-notes.md`

故意制造的 3 类 synthetic 问题：
1. **输入缺口** — PRD 缺少成功指标
2. **过程降级** — screenshot notes 缺少空状态/错误状态/加载状态
3. **跨 skill 一致性** — target audience 描述不一致（5-20 vs 10-50 人）

---

## 4. 五个 Run 摘要表

| run_id | skill | input_decision | checkpoint_decisions | consistency_decision | delivery_decision | triggered_fm_count | gap_count | assumption_count | result |
|--------|-------|----------------|----------------------|----------------------|-------------------|--------------------|-----------|--------------------|--------|
| RUN-001 | ai-analytics | ready_with_assumptions | [nominal, gaps, nominal, nominal, delivered] | needs_reconciliation | delivered_with_limitations | 1 | 2 | 2 | ✅ |
| RUN-002 | prd2proto | ready_with_assumptions | [nominal, nominal, gaps, nominal, delivered] | needs_reconciliation | delivered_with_limitations | 1 | 2 | 1 | ✅ |
| RUN-003 | uxeval | needs_user_clarification | [nominal, degrade, gaps, nominal, delivered_degraded] | nominal | delivered_with_limitations | 2 | 3 | 0 | ✅ |
| RUN-004 | ip-design | ready_nominal | [nominal, nominal, nominal, nominal, delivered] | nominal | delivered | 0 | 0 | 0 | ✅ |
| RUN-005 | brand-creative | ready_with_assumptions | [nominal, nominal, gaps, nominal, delivered] | nominal | delivered_with_limitations | 1 | 1 | 1 | ✅ |

---

## 5. 三类 Synthetic 问题验证结果

### 5.1 输入缺口问题

**设计**:
- synthetic PRD 缺少明确成功指标

**验证结果**:
- ✅ RUN-001 (ai-analytics): input gate 触发 `ready_with_assumptions`
- ✅ RUN-002 (prd2proto): input gate 触发 `ready_with_assumptions`

**结论**: Input quality gate 成功捕获输入缺口。

### 5.2 过程降级问题

**设计**:
- synthetic screenshot notes 缺少空状态/错误状态/加载状态

**验证结果**:
- ✅ RUN-003 (uxeval): input gate 触发 `needs_user_clarification`
- ✅ RUN-003 (uxeval): CP2 触发 `degrade_scope`

**结论**: Progressive checkpoint 成功捕获过程缺口并触发降级。

### 5.3 跨 Skill 一致性问题

**设计**:
- product brief 说"5-20 人"，PRD 说"10-50 人"

**验证结果**:
- ✅ RUN-001 (ai-analytics): consistency gate 触发 `needs_reconciliation`
- ✅ RUN-002 (prd2proto): consistency gate 触发 `needs_reconciliation`

**结论**: Cross-skill consistency contract 成功捕获一致性冲突。

---

## 6. H5/H5.1/H6/H4 串联可执行性

| 机制 | 文档 | 验证结果 |
|------|------|----------|
| H5: Input Quality Gate | `templates/input-quality-template.md` | ✅ 可执行 |
| H5.1: Progressive Checkpoint | `templates/progressive-checkpoint-template.md` | ✅ 可执行 |
| H6: Cross-Skill Consistency | `templates/cross-skill-consistency-template.md` | ✅ 可执行 |
| H4: Self-Review | `templates/self-review-template.md` | ✅ 可执行 |

**结论**: 四大质量门机制串联可执行，能生成 diagnostic-summary.md/json。

---

## 7. Sanitized Issue Registry 摘要

仓库内脱敏问题登记：
- `docs/audits/sanitized-issues/S2-H7B-sanitized-issue-registry.md`

登记问题数：6

问题类型分布：
- input_gap: 2
- consistency_gap: 2
- template_gap: 1
- docs_gap: 1

所有问题均已脱敏，不含真实路径、真实业务内容、真实 URL。

---

## 8. Synthetic Replay Case 摘要

仓库内 synthetic replay case：
- `fixtures/synthetic/s2-h7b-dry-run/synthetic-replay-case.md`

用途：
- 复现 input gate: ready_with_assumptions
- 复现 checkpoint: degrade_scope
- 复现 consistency: needs_reconciliation

已标 SYNTHETIC / SANITIZED，不含真实数据。

---

## 9. 发现的机制问题

### 9.1 输入缺口捕获能力

**发现**: Input gate 能捕获缺少成功指标的问题，但未明确推荐"补充哪些字段"。

**建议**: 在 input-quality template 中增加"推荐补充字段清单"。

### 9.2 降级决策透明度

**发现**: Progressive checkpoint 能触发 `degrade_scope`，但未记录"具体降级了哪些范围"。

**建议**: 在 checkpoint template 中增加"降级范围明细"字段。

### 9.3 跨 Skill 一致性自动 reconcile

**发现**: Consistency gate 能识别冲突，但未自动建议 reconcile 方案。

**建议**: 在 consistency template 中增加"推荐 reconcile 方案"字段。

### 9.4 Diagnostic Summary 结构化输出

**发现**: diagnostic-summary.json 能汇总，但缺少"linked KR"的聚合视图。

**建议**: 增加 KR 聚合视图，方便追溯。

---

## 10. 不进入仓库的 Raw Outputs 清单

外部 workspace 下的 raw outputs（不提交）：
- `<DESIGNOS_WORKSPACE_ROOT>/runs/RUN-*/run-manifest.yaml`
- `<DESIGNOS_WORKSPACE_ROOT>/runs/RUN-*/inputs/*`
- `<DESIGNOS_WORKSPACE_ROOT>/runs/RUN-*/outputs/*`
- `<DESIGNOS_WORKSPACE_ROOT>/runs/RUN-*/logs/*`
- `<DESIGNOS_WORKSPACE_ROOT>/runs/RUN-*/gates/*.json`
- `<DESIGNOS_WORKSPACE_ROOT>/runs/RUN-*/diagnostic-summary.md`
- `<DESIGNOS_WORKSPACE_ROOT>/runs/RUN-*/diagnostic-summary.json`
- `<DESIGNOS_WORKSPACE_ROOT>/runs/RUN-*/sanitized-issue-candidate.md`

这些文件只存在本机，不进入 git。

---

## 11. 是否可以进入 S2-H7.1 Gap Fix

✅ **可以进入 S2-H7.1**

条件：
- 外部 workspace 机制可执行
- 四大质量门串联可执行
- Diagnostic summary 能生成
- Sanitized issue registry 能生成
- 没有 raw outputs 进入 git
- 所有校验脚本通过

下一批 (S2-H7.1) 可基于本批发现的 4 个机制问题进行 gap fix。
