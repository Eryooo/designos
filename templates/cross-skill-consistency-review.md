# Cross-Skill Consistency Review (Global Template)

> **🚫 SYNTHETIC / SANITIZED ONLY** — 本模板及示例不含真实业务/客户/链路数据。
> **本模板性质**:跨 skill 一致性评审通用运行日志(引用层,非新标准)。规范见 `docs/audits/S2-H6-CROSS-SKILL-CONSISTENCY-CONTRACT.md`。
> **用途**:任何跨 skill 串联时,用本日志做字段映射审查、gap 传递检查、冲突记录;结果移交下游 H5 input gate 和 H4 self review。
> **consistency_decision 枚举**(唯一 4 个):`consistent` / `consistent_with_carried_gaps` / `needs_reconciliation` / `blocked_inconsistent`。

---

## 1. Metadata

| 字段 | 值(填写时替换) |
|---|---|
| review_id | `CR-synth-XXXX` |
| upstream_skill | `<填:ai-analytics / brand-creative / ip-design / prd2proto / uxeval>` |
| downstream_skill | `<填>` |
| upstream_run_id | `<填>` |
| downstream_run_id | `<填>` |
| reviewer | `<reviewer-id>` |
| date | `YYYY-MM-DD` |
| consistency_decision | `<填 §9 结论>` |

---

## 2. Skill Chain Summary

| 字段 | 值 |
|---|---|
| chain_type | `<填:inter-skill(跨 skill) / intra-skill(skill 内部链路)>` |
| contract_reference | `<填:docs/contracts/cross-skill/*.md 路径>` |
| upstream_h4_decision | `<填:上游 H4 的 pass / degrade_with_gaps / block>` |
| downstream_h5_input_decision | `<填:下游 H5 的 input_decision>` |
| expected_artifacts | `<填:本次传递的 artifact 清单>` |

---

## 3. Upstream Artifact Inventory

| artifact_id | artifact_type | skill_id | source_stage | maturity | confidence | h4_decision |
|---|---|---|---|---|---|---|
| `<填>` | `<填>` | `<填>` | `<填>` | `<填>` | `<填:0..1>` | `<填>` |

---

## 4. Downstream Input Inventory

| expected_input | artifact_type | provided | mapping_source | reliability |
|---|---|---|---|---|
| `<填>` | `<填>` | yes / no | `<填:artifact_id>` | high / medium / low / unknown |

---

## 5. Field Mapping Matrix

| mapping_id | upstream_artifact.field | downstream_artifact.field | mapping_type | consistency_status | notes |
|---|---|---|---|---|---|
| MAP-001 | `<填:artifact.field_path>` | `<填:artifact.field_path>` | exact / derived / optional / carry_forward | consistent / mismatch / missing | `<填>` |

---

## 6. Gap / Assumption Carry-Forward

| item_id | type | source | value_or_description | carried_to_downstream | downstream_label_required |
|---|---|---|---|---|---|
| GAP-001 | gap / assumption / inferred | `<填:上游 artifact.gap_id>` | `<填>` | yes / no | yes / no |

> **硬约束**:上游所有 gaps / assumptions / inferred_fields 必须传递。下游不得静默丢弃。

---

## 7. Contradiction Log

| contradiction_id | upstream_value | downstream_value | affected_fields | severity | resolution_options |
|---|---|---|---|---|---|
| CON-001 | `<填:上游字段值>` | `<填:下游字段值>` | `<填:字段路径>` | blocker / major / minor | `<填:以上游为准 / 追问用户 / 降级>` |

---

## 8. Reconciliation Questions

| question_id | question | why_needed | blocking_level | answer_format_hint |
|---|---|---|---|---|
| RQ-001 | `<填>` | `<填:冲突点说明>` | blocker / major / minor | `<填>` |

---

## 9. Consistency Decision

```
consistency_decision: <consistent | consistent_with_carried_gaps | needs_reconciliation | blocked_inconsistent>
```

| 字段 | 内容 |
|---|---|
| decision | `<填 §4 规则结论>` |
| rationale | `<填:核心字段改写 → blocked;冲突需裁定 → needs_reconciliation;gap 完整携带 → consistent_with_carried_gaps;全一致 → consistent>` |
| user_action_required | yes / no |
| user_notice | `<填:非 consistent 时的用户说明:冲突在哪 / 影响什么 / 可以怎么做>` |
| allow_downstream_to_proceed | yes / no |

---

## 10. Handoff To H4 / H5.1

| 字段 | 内容 |
|---|---|
| h5_input_gate_for_downstream | `<填:下游 H5 input_decision 是否需基于本审查调整>` |
| h5.1_carry_forward_update | `<填:新增的 cross-skill gap / contradiction 需加入下游 H5.1 checkpoint log>` |
| h4_traceability_note | `<填:下游 H4 在 §7 Traceability Check 时需验证上游 artifact_id 引用真实存在>` |
| consistency_review_log_path | `templates/cross-skill-consistency-review.md`(本 review 实例) |
