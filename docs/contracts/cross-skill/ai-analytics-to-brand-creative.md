# Cross-Skill Contract: ai-analytics → brand-creative

> **🚫 SYNTHETIC / SANITIZED ONLY** — 示例不含真实业务。
> **契约性质**:ai-analytics 输出 → brand-creative 输入的字段映射与一致性规则(引用层,非新标准)。规范见 `docs/audits/S2-H6-CROSS-SKILL-CONSISTENCY-CONTRACT.md`。

---

## 1. Contract Metadata

| 字段 | 值 |
|---|---|
| contract_id | CC-002 |
| upstream_skill | ai-analytics |
| downstream_skill | brand-creative |
| contract_version | 1.0.0-pilot |
| upstream_h4_required | pass 或 degrade_with_gaps |
| consistency_decision_enum | consistent / consistent_with_carried_gaps / needs_reconciliation / blocked_inconsistent |

---

## 2. Upstream Artifacts

| artifact | key_fields | mandatory |
|---|---|---|
| `competitor_matrix` | 竞品 × 维度矩阵(visual_style / positioning / pricing 等) | yes(competitive-analysis 子技能的基础) |
| `design_strategy` | target_audience / differentiation_statement | optional(提升策略质量) |
| `user_persona[]` | role / goals / pain_points | optional |

---

## 3. Downstream Inputs

| brand-creative sub-skill | 对应 ai-analytics artifact | inject_as |
|---|---|---|
| competitive-analysis | competitor_matrix | 竞品数据来源 |
| brand-strategy | design_strategy.target_audience + differentiation | 策略基础 |

---

## 4. Required Field Mapping

| mapping_id | upstream_artifact.field | downstream_artifact.field | mapping_type | conflict_rule | gap_rule | confidence_rule |
|---|---|---|---|---|---|---|
| MAP-001 | competitor_matrix.competitors[] | competitive-analysis.competitor_matrix | carry_forward | brand-creative 只可扩展不可删除上游竞品 | 上游缺则 brand-creative 自采,标 [inferred] | 置信度≤上游 |
| MAP-002 | design_strategy.target_audience | brand-strategy.target_audience | exact | 不允许改写;冲突 → needs_reconciliation | 缺则推断标 [inferred] | 同上 |
| MAP-003 | design_strategy.differentiation_statement | brand-strategy.differentiation | derived | 可扩展但不可推翻上游差异化方向 | 缺则 brand-creative 独立分析 | 同上 |

---

## 5. Gap / Assumption / Confidence Carry-Forward

| 传递项 | 规则 |
|---|---|
| ai-analytics 竞品资料缺口 | 进入 brand-creative competitive-analysis 的 gaps |
| ai-analytics [inferred] 的差异化描述 | brand-strategy 必须保留 [inferred] 标注 |
| coverage < 1.0 的 competitor_matrix | brand-creative 须在 cross_subskill_consistency 中标注数据来源限制 |

---

## 6. Conflict Rules

| 冲突类型 | 处理方式 | consistency_decision |
|---|---|---|
| brand-strategy 目标人群与 ai-analytics.design_strategy.target_audience 不同 | 追问用户,以上游为准或显式说明 | needs_reconciliation |
| brand-creative 删除上游 competitor_matrix 的竞品 | 立即标 blocked_inconsistent | blocked_inconsistent |
| brand-creative 把 ai-analytics [inferred] 差异化当 verified fact | 立即标 blocked_inconsistent | blocked_inconsistent |

---

## 7. Consistency Decision Rules

- **consistent**:竞品矩阵全部携带,target_audience 对齐,traceability 完整
- **consistent_with_carried_gaps**:字段对齐但上游 gaps 显式携带
- **needs_reconciliation**:策略有合理扩展但需用户确认
- **blocked_inconsistent**:竞品删除/目标人群改写/[inferred]去标注

---

## 8. User Reconciliation Prompts

| prompt_id | 场景 | 说明给用户 | 建议操作 |
|---|---|---|---|
| RP-001 | brand-strategy 人群与 ai-analytics 不一致 | "[synthetic] ai-analytics 确定目标人群为 IT 管理员,brand-creative 即将改为'年轻用户' — 策略链将断裂" | 以 ai-analytics 为准 / 提供新人群说明 |
| RP-002 | 竞品维度不足 | "[synthetic] ai-analytics 竞品矩阵缺 visual_style 维度,brand-creative 差异化无视觉参照" | 补充竞品视觉风格信息 |

---

## 9. Synthetic Example

```yaml
# ai-analytics 上游(synthetic)
competitor_matrix:
  - competitor: "synthetic-A"
    positioning: "高端企业级"
    visual_style: "深蓝 + 极简"
    
# brand-creative 正确接入(consistent_with_carried_gaps):
competitive_analysis:
  source_artifact_id: "analysis-20260612-synth001"
  competitors:
    - name: "synthetic-A"     # 原样携带
      positioning: "高端企业级"
      visual_style: "深蓝 + 极简"
```

---

## 10. Related Gates

| Gate | 关系 |
|---|---|
| ai-analytics H4 | 上游必须 pass 才允许传入 brand-creative |
| brand-creative H5 input-quality-gate | 本契约审查决定 H5 input_decision |
| brand-creative H5.1 CP-B1/CP-B2 | 上游 gaps 从 CP-B1 起持续 carry-forward |
| brand-creative H4 §5 | FM-BRANDCREATIVE-001 检查策略是否引用上游 |
