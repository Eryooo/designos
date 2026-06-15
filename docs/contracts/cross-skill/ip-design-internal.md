# Cross-Skill Contract: ip-design Internal

> **🚫 SYNTHETIC / SANITIZED ONLY** — 示例不含真实品牌/IP。
> **契约性质**:ip-design 6 阶段内部一致性契约(引用层,非新标准)。规范见 `docs/audits/S2-H6-CROSS-SKILL-CONSISTENCY-CONTRACT.md`。

---

## 1. Contract Metadata

| 字段 | 值 |
|---|---|
| contract_id | CC-004 |
| upstream_skill | ip-design(内部阶段链) |
| downstream_skill | ip-design(内部阶段链) |
| contract_version | 1.0.0-pilot |
| consistency_decision_enum | consistent / consistent_with_carried_gaps / needs_reconciliation / blocked_inconsistent |
| core_violation | FM-IPDESIGN-004(视觉先行)= 视觉阶段出现在策略链之前 |

---

## 2. Upstream Artifacts

内部链路:

```
M01 brand_brief → M02 worldview → M03 persona_profile → M04 visual_spec + image_prompt_pack → M05 content_plan → M06 brand_material_spec
```

| 阶段 | 关键产物 | 下游消费 |
|---|---|---|
| M01 strategy-alignment | brand_brief(北极星/人格/差异化) | M02/M03/M04/M05/M06 全部 |
| M02 worldview-building | worldview(时空/规则/关系/文化原型) | M03/M04/M05 |
| M03 persona-modeling | persona_profile(行为/动机/恐惧/成长/声音) | M04/M05/M06 |
| M04 visual-translation | visual_spec + image_prompt_pack | M06 |
| M05 narrative-planning | content_plan | M06 |

---

## 3. Downstream Inputs

| 阶段 | 必需上游输入 | mandatory |
|---|---|---|
| M02 | brand_brief.north_star + personality_keywords | yes |
| M03 | brand_brief + worldview | yes |
| M04 | brand_brief + worldview + persona_profile | yes(**先策略后视觉**) |
| M05 | brand_brief + persona_profile | yes |
| M06 | visual_spec + content_plan + brand_brief | yes |

---

## 4. Required Field Mapping

| mapping_id | upstream_field | downstream_field | mapping_type | conflict_rule | gap_rule | confidence_rule |
|---|---|---|---|---|---|---|
| MAP-001 | brand_brief.north_star | visual_spec.style_quadrant | derived | 视觉调性须服务北极星;冲突 → FM-IPDESIGN-004 风险 | 缺则推断标 [inferred] | 置信度≤上游 |
| MAP-002 | brand_brief.personality_keywords | visual_spec.color_system.primary | derived | 主色须契合人格;冲突 → needs_reconciliation | 同上 | 同上 |
| MAP-003 | brand_brief.differentiation | visual_spec.strict_avoidance | carry_forward | 差异化禁忌须在视觉禁忌中体现 | 缺则 FM-IPDESIGN-005 风险 | 同上 |
| MAP-004 | persona_profile.behavior_model | content_plan.voice_style | derived | 内容声音须服务人格 | 同上 | 同上 |
| MAP-005 | brand_brief.north_star | image_prompt_pack.layer_2 | exact | 提示词设计概念层须引用北极星 | 缺则 FM-IPDESIGN-005 | 同上 |

---

## 5. Gap / Assumption / Confidence Carry-Forward

| 传递项 | 规则 |
|---|---|
| brand_brief [inferred] 人格推断 | M03/M04 必须保留 [inferred] 标注 |
| 差异化缺乏竞品依据(D2 gap) | 携带到 visual_spec 的 gaps |
| 法务/商标待确认(D6 gap) | 从 M04 携带到 M06 brand_material_spec |
| D8 人格立体度不足 | 携带 gap 直到 professional_gap_report |

---

## 6. Conflict Rules

| 冲突类型 | 处理方式 | consistency_decision |
|---|---|---|
| 视觉调性与北极星矛盾 | 回 M01 对齐;用户确认 | blocked_inconsistent |
| M04 在 M03 之前产出(视觉先行) | FM-IPDESIGN-004 一票否决 | blocked_inconsistent |
| content_plan 语调与 persona_profile 声音边界冲突 | needs_reconciliation | needs_reconciliation |
| 跨阶段关键词漂移 | FM-IPDESIGN-006 触发 | blocked_inconsistent |

---

## 7. Consistency Decision Rules

- **consistent**:全链路关键词无漂移,traceability 完整,视觉严格后于策略
- **consistent_with_carried_gaps**:字段对齐但 D6/D2 gap 显式携带
- **needs_reconciliation**:内容声音与人格有可协商差异
- **blocked_inconsistent**:视觉先行 / 北极星矛盾 / 关键词跨阶段漂移

---

## 8. User Reconciliation Prompts

| prompt_id | 场景 | 说明给用户 | 建议操作 |
|---|---|---|---|
| RP-001 | M04 未完成 M03 即开始 | "[synthetic] 人格建模(M03)尚未完成即进行视觉转化(M04) — 这将触发'视觉先行'一票否决" | 先完成 M03 再进 M04 |
| RP-002 | visual_spec 色彩与北极星矛盾 | "[synthetic] 北极星强调'稳重可靠',视觉规范出现大量鲜艳跳色 — D1 品牌一致性失守" | 回 M04 调整主色方向 |

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
# M01 brand_brief(synthetic)
north_star: "让 IT 管理员感到'有个可靠伙伴在帮我看着'"
personality_keywords: ["稳重", "细心", "略带技术感"]

# M04 visual_spec 正确接入:
visual_spec:
  style_quadrant: "专业稳重"  # 服务北极星
  color_system:
    primary: "#2C5282"      # 深蓝 = 稳重
  keyword_lineage: brand_brief.personality_keywords

# M04 错误接入(blocked_inconsistent):
visual_spec:
  style_quadrant: "活泼可爱"   # 与北极星矛盾
  color_system:
    primary: "#FF6B6B"         # 与稳重矛盾
  # 无 keyword_lineage 引用      # traceability 断裂
```

---

## 10. Related Gates

| Gate | 关系 |
|---|---|
| ip-design H5.1 CP-I3 | 视觉先行检查点:M04 前必须确认 M01-M03 完成 |
| ip-design H4 §4 | V1-V4 一票否决检查(含视觉先行) |
| ip-design H4 §6 | golden template 跨阶段 traceability 检查 |
