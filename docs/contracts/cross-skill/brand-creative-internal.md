# Cross-Skill Contract: brand-creative Internal

> **🚫 SYNTHETIC / SANITIZED ONLY** — 示例不含真实品牌。
> **契约性质**:brand-creative 13 个子技能之间的内部一致性契约(引用层,非新标准)。规范见 `docs/audits/S2-H6-CROSS-SKILL-CONSISTENCY-CONTRACT.md`。

---

## 1. Contract Metadata

| 字段 | 值 |
|---|---|
| contract_id | CC-003 |
| upstream_skill | brand-creative(内部子技能链) |
| downstream_skill | brand-creative(内部子技能链) |
| contract_version | 1.0.0-pilot |
| consistency_decision_enum | consistent / consistent_with_carried_gaps / needs_reconciliation / blocked_inconsistent |
| current_status | alpha(13 sub-skill 仅 6 有 pipeline — 46%,未达 KR-B1 最低线 50%) |

---

## 2. Upstream Artifacts

内部链路顺序:

```
competitive-analysis → brand-strategy → {logo-design, color-system, typography-system} → visual-identity
```

| 子技能 | 关键产物 | 下游消费者 |
|---|---|---|
| competitive-analysis | competitor_matrix | brand-strategy |
| brand-strategy | brand_brief(定位/差异化/人格) | logo-design / color-system / typography-system / brand-voice / content-strategy |
| logo-design | logo_spec | visual-identity |
| color-system | color_palette | visual-identity |
| typography-system | typography_spec | visual-identity |
| visual-identity | vi_manual | brand-guidelines / collateral |

---

## 3. Downstream Inputs

| 子技能 | 依赖的上游产物 | mandatory |
|---|---|---|
| brand-strategy | competitor_matrix.differentiation_basis | yes |
| logo-design | brand_brief.personality_keywords + differentiation | yes |
| color-system | brand_brief.personality_keywords + brand_brief.target_audience | yes |
| typography-system | brand_brief.personality_keywords | yes |
| visual-identity | logo_spec + color_palette + typography_spec | yes |
| brand-guidelines | vi_manual + brand_voice_guide + content_plan | yes |

---

## 4. Required Field Mapping

| mapping_id | upstream | downstream | mapping_type | conflict_rule | gap_rule | confidence_rule |
|---|---|---|---|---|---|---|
| MAP-001 | brand_brief.personality_keywords | logo_spec.form_principle | derived | logo 形态须服务于人格关键词;冲突 → blocked_inconsistent | 缺则推断标 [inferred] | 置信度≤上游 |
| MAP-002 | brand_brief.personality_keywords | color_palette.primary | derived | 主色须契合人格调性;冲突 → needs_reconciliation | 同上 | 同上 |
| MAP-003 | brand_brief.personality_keywords | typography_spec.main_font | derived | 字体须服务于调性 | 同上 | 同上 |
| MAP-004 | brand_brief.differentiation | visual-identity.cross_consistency | carry_forward | 视觉不可推翻差异化定位 | 标 gap | 同上 |
| MAP-005 | {logo_spec + color_palette + typography_spec} | vi_manual | exact | 三件套必须全部纳入 vi_manual | 缺一则 FM-BRANDCREATIVE-007 触发 | 同上 |

---

## 5. Gap / Assumption / Confidence Carry-Forward

| 传递项 | 规则 |
|---|---|
| brand_brief [inferred] 字段 | 所有下游子技能必须保留 [inferred] 标注 |
| competitive-analysis.gaps | 携带到 brand-strategy 的 gaps |
| 上游子技能的 confidence | 下游不可升,只可降 |
| trademark_signal 待确认项 | 必须在 vi_manual 和 brand-guidelines 中持续标注 |

---

## 6. Conflict Rules

| 冲突类型 | 处理方式 | consistency_decision |
|---|---|---|
| logo 风格与 brand_brief.personality_keywords 明显矛盾 | 回 brand-strategy 对齐;用户确认 | blocked_inconsistent |
| color 主调与 brand_brief 调性冲突 | 追问用户 | needs_reconciliation |
| vi_manual 缺 logo / color / typography 任一件套 | FM-BRANDCREATIVE-007 触发 | blocked_inconsistent(若缺件套) |
| 各子技能 keyword_lineage 漂移 | FM-BRANDCREATIVE-003 触发 | blocked_inconsistent |

---

## 7. Consistency Decision Rules

- **consistent**:三件套全部与 brand_brief 对齐,vi_manual 完整,traceability 完整
- **consistent_with_carried_gaps**:字段对齐但有 trademark/法务 gap 携带
- **needs_reconciliation**:某子技能风格与人格有可协商差异
- **blocked_inconsistent**:logo/color/type 推翻 brand_brief / 视觉先行 / vi_manual 缺件套

---

## 8. User Reconciliation Prompts

| prompt_id | 场景 | 说明给用户 | 建议操作 |
|---|---|---|---|
| RP-001 | logo 风格与策略矛盾 | "[synthetic] brand_brief 强调'稳重专业',logo 设计出现大量装饰性元素 — 品牌一致性(D1)失守" | 回 logo-design 调整形态方向 |
| RP-002 | vi_manual 缺 typography | "[synthetic] visual-identity 缺 typography_spec — 品牌手册不完整" | 补充 typography-system 子技能或标 gap |

### Reconciliation Options (S2-H7.1)

> 当 consistency_decision = needs_reconciliation 或 blocked_inconsistent 时，提供至少 2 个可选裁定方案。

#### 通用裁定方案

| option_id | resolution_approach | pros | cons | user_action_needed |
|---|---|---|---|---|
| OPT-1 | 以上游为准 | 保持上游一致性 | 下游需修改已推断字段 | no (自动修正) |
| OPT-2 | 以下游为准 | 保持下游已有逻辑 | 可能与上游设计意图不一致 | yes (需用户确认偏离) |
| OPT-3 | 追问用户裁定 | 由用户明确决策 | 需要用户介入 | yes |

**推荐方案**: 根据具体冲突类型选择，一般优先 OPT-1 (以上游为准)

**理由**: 上游 skill 产出应作为下游输入的权威来源，除非用户明确要求偏离。

---

---

## 9. Synthetic Example

```yaml
# brand-strategy 定义(synthetic)
brand_brief:
  personality_keywords: ["稳重", "专业", "略带技术感"]

# logo-design 正确接入:
logo_spec:
  form_principle: "[synthetic] 简约几何形,无过多装饰,传达稳重专业感"
  keyword_lineage: brand_brief.personality_keywords  # 引用上游

# logo-design 错误接入(blocked_inconsistent):
logo_spec:
  form_principle: "[synthetic] 活泼卡通形态,鲜艳装饰"  # 与 personality_keywords 矛盾
```

---

## 10. Related Gates

| Gate | 关系 |
|---|---|
| brand-creative H5 CP-B2/CP-B3 | checkpoint 在策略后和三件套后检查一致性 |
| brand-creative H4 §4 | FM-BRANDCREATIVE-003 一票否决:跨子技能不一致 |
| brand-creative H4 §6 | golden template cross_subskill_consistency 节 |
| brand-creative H4 §8 | Not Allowed Claims:不得在不一致时声称"完整品牌系统" |
