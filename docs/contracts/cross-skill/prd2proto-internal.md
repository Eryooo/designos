# Cross-Skill Contract: prd2proto Internal

> **🚫 SYNTHETIC / SANITIZED ONLY** — 示例不含真实业务/PRD。
> **契约性质**:prd2proto 18 stage 内部链路一致性契约(引用层,非新标准)。规范见 `docs/audits/S2-H6-CROSS-SKILL-CONSISTENCY-CONTRACT.md`。

---

## 1. Contract Metadata

| 字段 | 值 |
|---|---|
| contract_id | CC-005 |
| upstream_skill | prd2proto(内部 stage 链) |
| downstream_skill | prd2proto(内部 stage 链) |
| contract_version | 1.0.0-pilot |
| consistency_decision_enum | consistent / consistent_with_carried_gaps / needs_reconciliation / blocked_inconsistent |
| core_invariant | business_goal + target_audience 全链路不变 |

---

## 2. Upstream Artifacts

内部 18 stage 链路:

```
requirement_inventory → design_objectives → user_task_map → business_flow → user_journey → 
information_architecture → page_flow → page_structure → component_strategy → state_matrix → 
interaction_rules → design_spec → design_tokens → prototype_code → 
traceability_map → professional_gap_report → liveness_check
```

核心不变量流转:

| 阶段 | 关键产物 | 下游消费 |
|---|---|---|
| input-diagnosis | requirement_inventory(business_goal / user_goals / gaps) | 全链路 |
| design-objectives | design_objectives(goal mapping) | user_task_map + 后续全部 |
| user-task-modeling | user_task_map(actor / primary_tasks / edge_tasks) | business_flow / journey / IA / page_flow |
| state-matrix | state_matrix(7 状态) | component_strategy / interaction_rules / prototype_code |
| traceability-generation | traceability_map(decision_trace) | H4 self-review §7 |

---

## 3. Downstream Inputs

| stage | 必需上游字段 | mandatory |
|---|---|---|
| design-objectives | requirement_inventory.business_goal + user_goals | yes |
| user-task-modeling | design_objectives.goal_mapping | yes |
| information-architecture | user_task_map.primary_tasks | yes |
| state-matrix | page_structure + user_task_map.edge_tasks | yes |
| prototype-code | design_spec + design_tokens + state_matrix | yes |
| traceability-generation | 全链路 artifact_id | yes |

---

## 4. Required Field Mapping

| mapping_id | upstream_field | downstream_field | mapping_type | conflict_rule | gap_rule | confidence_rule |
|---|---|---|---|---|---|---|
| MAP-001 | requirement_inventory.business_goal | design_objectives.business_goals | exact | 不允许在 design_objectives 改写 | 缺则 gap_transparency_gate 触发 | 置信度≤上游 |
| MAP-002 | design_objectives.goal_mapping | user_task_map.task_goal_refs | carry_forward | 每个任务须服务至少 1 个目标 | 无 goal_ref 的任务标 gap | 同上 |
| MAP-003 | user_task_map.edge_tasks | state_matrix.edge_states | carry_forward | edge_tasks 须体现在 state_matrix | 缺则 FM-PRD2PROTO-008 | 同上 |
| MAP-004 | state_matrix.states | component_strategy.state_variants | carry_forward | 组件须覆盖 state_matrix 定义的所有状态 | 缺则 FM-PRD2PROTO-008 | 同上 |
| MAP-005 | design_tokens.{color,spacing,typography} | prototype_code(style 引用) | exact | 代码必须引用 token;硬编码 → FM-PRD2PROTO-003 | 缺则 code_constraint_gate 触发 | 同上 |

---

## 5. Gap / Assumption / Confidence Carry-Forward

| 传递项 | 规则 |
|---|---|
| requirement_inventory.gaps | 全链路携带;final output professional_gap_report 汇总 |
| requirement_inventory.ambiguities | 携带到 design_objectives + user_task_map |
| 推断字段([inferred]) | 在 inferred_fields 中全链路维护 |
| confidence 值 | 只降不升 |

---

## 6. Conflict Rules

| 冲突类型 | 处理方式 | consistency_decision |
|---|---|---|
| design_objectives 改写 business_goal | FM-PRD2PROTO-002 + 立即 blocked | blocked_inconsistent |
| prototype_code 硬编码样式值 | FM-PRD2PROTO-003 + code_constraint_gate | blocked_inconsistent |
| state_matrix 未覆盖 user_task_map.edge_tasks | FM-PRD2PROTO-008 | needs_reconciliation |
| traceability_map 引用不存在的 artifact_id | FM-PRD2PROTO-002 traceability 断裂 | blocked_inconsistent |

---

## 7. Consistency Decision Rules

- **consistent**:全链路 business_goal/target_audience 不变,traceability 完整,token 全引用
- **consistent_with_carried_gaps**:有 gap 携带但核心不变量保持
- **needs_reconciliation**:edge_tasks 覆盖不完整但可补充
- **blocked_inconsistent**:business_goal 被改写 / 硬编码 / traceability 断裂

---

## 8. User Reconciliation Prompts

| prompt_id | 场景 | 说明给用户 | 建议操作 |
|---|---|---|---|
| RP-001 | design_objectives 与 PRD 业务目标不符 | "[synthetic] PRD 的核心 KPI 是'转化率 ≥ 20%',design_objectives 未引用此目标 — traceability 将断裂" | 在 design_objectives 显式引用 PRD 业务目标 |
| RP-002 | prototype_code 含硬编码 | "[synthetic] 代码出现 `color: #1677ff` 而非引用 design token — 违反代码宪法" | 替换为 `var(--color-brand-primary)` 或对应 token |

---

## 9. Synthetic Example

```yaml
# requirement_inventory(synthetic)
business_goal: "3 个月试用转化 ≥ 20%"
target_audience: "小型企业 IT 管理员"

# design_objectives 正确继承:
design_objectives:
  business_goals:
    - goal_id: BG-001
      description: "3 个月试用转化 ≥ 20%"  # 原样引用
      source_artifact_id: "req-inventory-20260612-synth001"

# prototype_code 正确引用 token:
# color: var(--color-brand-primary)       # ✅

# 错误:
# color: #1677ff                          # ❌ blocked_inconsistent
```

---

## 10. Related Gates

| Gate | 关系 |
|---|---|
| prd2proto H5.1 CP-P1~CP-P5 | 每个 checkpoint 检查不变量是否被篡改 |
| prd2proto H4 §4 | V1-V4 一票否决(Schema/Traceability/代码宪法/Honesty) |
| prd2proto H4 §7 | traceability 规范检查:traceability_map 引用必须真实 |
