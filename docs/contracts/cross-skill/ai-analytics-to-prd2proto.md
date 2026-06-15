# Cross-Skill Contract: ai-analytics → prd2proto

> **🚫 SYNTHETIC / SANITIZED ONLY** — 示例不含真实业务。
> **契约性质**:ai-analytics 输出 → prd2proto 输入的字段映射与一致性规则(引用层,非新标准)。
> **规范引用**:`docs/audits/S2-H6-CROSS-SKILL-CONSISTENCY-CONTRACT.md`;字段引用 `kernel/contracts/artifacts/{design-strategy.schema.json, user-persona.schema.json}` 和各 skill golden template。

---

## 1. Contract Metadata

| 字段 | 值 |
|---|---|
| contract_id | CC-001 |
| upstream_skill | ai-analytics |
| downstream_skill | prd2proto |
| contract_version | 1.0.0-pilot |
| upstream_h4_required | pass 或 degrade_with_gaps(blocked 时下游不允许启动) |
| consistency_decision_enum | consistent / consistent_with_carried_gaps / needs_reconciliation / blocked_inconsistent |

---

## 2. Upstream Artifacts

ai-analytics 传入 prd2proto 的产物:

| artifact | schema | key_fields | mandatory |
|---|---|---|---|
| `design_strategy` | `kernel/contracts/artifacts/design-strategy.schema.json` | target_audience / business_goal / design_principles / differentiation_statement | **yes**(prd2proto `upstream_refs` 注入) |
| `user_persona[]` | `kernel/contracts/artifacts/user-persona.schema.json` | role / goals / pain_points | **yes** |
| `analysis_report` | — | competitive_matrix / market_findings | optional |

---

## 3. Downstream Inputs

prd2proto 的 `pipeline.yaml` upstream_refs:

| prd2proto input | 对应 ai-analytics artifact | inject_as | required |
|---|---|---|---|
| `design_strategy` | `design_strategy` | `design_strategy` | false(optional) |
| `existing_personas` | `user_persona[]` | `existing_personas` | false(optional) |

> **注**:optional 指 prd2proto 可无上游输入独立运行,但若有上游产物则**必须使用且不可改写**。

---

## 4. Required Field Mapping

| mapping_id | upstream_artifact.field | downstream_artifact.field | mapping_type | conflict_rule | gap_rule | confidence_rule |
|---|---|---|---|---|---|---|
| MAP-001 | design_strategy.target_audience | design_objectives.target_audience | exact | 下游不允许改写;如不同 → blocked_inconsistent | 上游缺则下游推断须标 [inferred] | 置信度≤上游;不可上升 |
| MAP-002 | design_strategy.business_goal | design_objectives.business_goal | exact | 同上 | 缺则追问用户 | 同上 |
| MAP-003 | design_strategy.design_principles | design_objectives.design_principles | derived | 可扩展但不可推翻 | 缺则用默认原则并标 [inferred] | 同上 |
| MAP-004 | user_persona[].role | user_task_map.actor | exact | 角色名必须对应;冲突 → needs_reconciliation | 缺则推断 + 标 [inferred] | 同上 |
| MAP-005 | user_persona[].goals | user_task_map.primary_tasks | derived | 任务须服务 goals;不可与 goals 矛盾 | 缺则按产品类型推断 | 降级不可升 |
| MAP-006 | user_persona[].pain_points | user_task_map.pain_points | carry_forward | 下游须显式携带 | 缺则标 gap | 同上 |

---

## 5. Gap / Assumption / Confidence Carry-Forward

| 传递项 | 规则 |
|---|---|
| ai-analytics 的 data_completeness_assessment.gaps | 必须进入 prd2proto requirement_inventory.gaps |
| ai-analytics 的 [inferred] 字段 | 下游 artifact 中继续标 [inferred];不得去掉标注 |
| ai-analytics 的 confidence 值 | prd2proto 的对应字段 confidence 不得高于上游 ai-analytics 的 confidence |
| ai-analytics 的 assumptions | 进入 prd2proto 的 assumptions 列表 |

---

## 6. Conflict Rules

| 冲突类型 | 处理方式 | consistency_decision |
|---|---|---|
| prd2proto 的目标人群与 design_strategy.target_audience 不同 | 追问用户,以上游为准或显式降级 | needs_reconciliation |
| prd2proto 的 user_task_map actor 与 user_persona.role 不一致 | 以上游为准;若有充分理由改变须用户确认 | needs_reconciliation |
| prd2proto 把 ai-analytics 的 [inferred] 当 verified fact | 立即标 blocked_inconsistent | blocked_inconsistent |
| prd2proto 的 design_objectives 与 design_strategy.business_goal 矛盾 | 立即标 blocked_inconsistent | blocked_inconsistent |

---

## 7. Consistency Decision Rules

- **consistent**:design_strategy + user_persona 全部 exact 字段对齐,gaps 完整携带,traceability 完整
- **consistent_with_carried_gaps**:字段对齐但上游 gaps/assumptions 被显式携带
- **needs_reconciliation**:字段存在可协商差异(如任务扩展),需用户确认
- **blocked_inconsistent**:任一 exact 字段被改写 / [inferred] 被去标注 / 业务目标/用户矛盾

---

## 8. User Reconciliation Prompts

| prompt_id | 场景 | 说明给用户的内容 | 建议用户操作 |
|---|---|---|---|
| RP-001 | 用户角色不一致 | "[synthetic] ai-analytics 定义目标人群为 IT 管理员,prd2proto 即将按运营人员做页面 — 这会导致任务建模全部偏移" | 以上游 IT 管理员为准 / 提供新的角色输入 |
| RP-002 | [inferred] 被去掉 | "[synthetic] ai-analytics 把'行业转化率 12%'标为推断,prd2proto 当成事实使用 — 会造成置信度虚高" | 在 design_objectives 保留 [inferred] 标注 |

---

## 9. Synthetic Example

> [synthetic] Acme Demo SaaS — ai-analytics 产出 → prd2proto 使用

```yaml
# ai-analytics 上游输出(synthetic)
design_strategy:
  target_audience: "小型企业 IT 管理员 [inferred: 基于 5 条访谈推断]"
  business_goal: "3 个月试用转化 ≥ 20%"
  confidence: 0.70

# prd2proto 正确接入(consistency=consistent_with_carried_gaps):
design_objectives:
  target_audience: "小型企业 IT 管理员 [inferred: 承接 ai-analytics 推断]"
  business_goal: "3 个月试用转化 ≥ 20%"
  source_artifact_id: "design-strategy-20260612-synth001"
  confidence: 0.70  # ≤ 上游

# prd2proto 错误接入(consistency=blocked_inconsistent):
design_objectives:
  target_audience: "运营人员"        # 改写了目标人群
  business_goal: "提升用户体验"      # 改写了业务目标
  # [inferred] 标注被去掉             # Honesty violation
```

---

## 10. Related Gates

| Gate | 关系 |
|---|---|
| ai-analytics H4 self-review | 上游必须 pass 或 degrade_with_gaps 才允许传入 prd2proto |
| prd2proto H5 input-quality-gate | 本契约审查结果决定 H5 的 input_decision |
| prd2proto H5.1 CP-P1/CP-P2 | upstream_artifacts 携带的 gaps 必须在 CP-P1 起持续 carry-forward |
| prd2proto H4 self-review §7 | 须验证 design_objectives.source_artifact_id 指向真实 ai-analytics run |
