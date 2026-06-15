# Input Quality Gate — brand-creative

> **🚫 SYNTHETIC / SANITIZED ONLY** — 本模板及示例不含真实品牌/客户/商标/logo。
> **本模板性质**:执行前输入质量门(引用层,非新标准)。引用 S2-H1/H1.1 KR、S2-H2 golden、S2-H3 failure modes、S2-H4 self review gate;输入诊断引 `knowledge/design-work-paradigm/01-input-diagnosis.md`;约束引 `skills/brand-creative/GROUP.md` + `knowledge/design/quality/brand-creative-failure-modes.md`(group skill 无 root constitution)。
> **执行顺序**:见 `docs/audits/S2-H5-INPUT-QUALITY-GATE.md` §4(8 步)。
> **当前状态**:brand-creative = alpha,group skill,13 sub-skill 仅 6 有 pipeline(46%,未达 KR-B1 最低线 50%)。本 gate 通过 ≠ 输入完美。

---

## 1. Metadata

| 字段 | 值(填写时替换) |
|---|---|
| skill | brand-creative |
| run_id | `run-synth-XXXX` |
| reviewer | `<reviewer-id>` |
| date | `YYYY-MM-DD` |
| requested_output | `<填:目标产出 + 涉及的 sub-skill(brand-strategy/logo/color/...)>` |
| input_sources | `<填:品牌目标/竞品/策略输入 等清单>` |
| input_decision | `<填 §9 结论>` |

---

## 2. Input Source Inventory

| source_id | source_type | path_or_description | available | reliability | notes |
|---|---|---|---|---|---|
| S-001 | text_brief | `<填:品牌目标 / 业务背景>` | yes / no | high / medium / low / unknown | `<填>` |
| S-002 | data_table | `<填:竞品 / 市场信息(≥3)>` | yes / no | high / medium / low / unknown | `<填>` |
| S-003 | existing_artifact | `<填:已有 brand-strategy 上游产物(可选)>` | yes / no | high / medium / low / unknown | `<填>` |
| S-004 | design_file | `<填:既有品牌资产(brand-refresh 流程)>` | yes / no | high / medium / low / unknown | `<填>` |

---

## 3. Required Input Check

| input_item | required | present | evidence | gap_if_missing | decision_impact |
|---|---|---|---|---|---|
| 品牌目标(B/C/政企) | yes | yes / no | `<填>` | brand-strategy 无方向 | block 或 needs_clarification |
| 竞品 / 市场上下文 | yes | yes / no | `<填:≥3 竞品>` | 差异化无依据 = FM-BRANDCREATIVE-001 风险 | needs_clarification |
| 品牌策略输入(若已有) | partial | yes / no | `<填:S-003>` | 视觉子技能无策略锚点 | ready_with_assumptions 或 needs_clarification |
| 子技能依赖清单 | yes | yes / no | `<填:logo/color/type/VI/voice 选哪些>` | 无法确定执行范围 | block |
| 应用场景 | partial | yes / no | `<填:数字/印刷/包装/空间>` | brand-collateral 需推断 | ready_with_assumptions |
| 约束与禁区(法务/商标/文化) | yes | yes / no | `<填>` | 商标风险无来源 = FM-BRANDCREATIVE-002 | needs_clarification |

> **特别提示**:若所选 sub-skill 当前**无 pipeline**(13 中 7 个无),input gate 必须在 §9 标注该限制(KR-B1 未达最低线)。

---

## 4. Golden Template Input Readiness

> 引用 `skills/brand-creative/templates/golden-brand-creative-output.md` "输入前提" + "必填章节"。

| golden_section | required_input | input_available | can_infer | risk_if_inferred |
|---|---|---|---|---|
| brand_brief(brand-strategy) | 品牌目标 + 竞品 + 用户 | yes / no / partial | partial | 定位推断风险高(策略空心化) |
| competitive_matrix(competitive-analysis) | 竞品 ≥ 3 + 维度 ≥ 4 | yes / no / partial | partial | 维度推断风险中 |
| logo_spec(logo-design) | 品牌策略 + 风格边界 | yes / no / partial | partial | 视觉先行风险(需先策略) |
| color_palette(color-system) | 品牌人格 + WCAG 要求 | yes / no / partial | yes | 对比度需校验 |
| vi_manual(visual-identity) | 上游 logo/color/type | yes / no / partial | no | 缺上游则 VI 不完整 |
| cross_subskill_consistency | 全 sub-skill 关键词 | yes / no / partial | no | 跨 skill 不一致风险 |

---

## 5. Failure Mode Input Risk Check

> 从 `skills/brand-creative/eval/failure/failure-modes.md` 抽取输入相关 FM。

| fm_id | severity | input_risk | trigger_if_missing | prevention_action |
|---|---|---|---|---|
| FM-BRANDCREATIVE-001 | blocker | 品牌目标/竞品缺 → 策略空心化 | 仅有形容词无定位 | 追问差异化定位 + 目标人群 |
| FM-BRANDCREATIVE-002 | blocker | 商标/法务约束缺 → 风险未标 | 无禁区输入 | 追问商标/法务/文化禁区 |
| FM-BRANDCREATIVE-003 | blocker | 跨 sub-skill 关键词无统一来源 | 各子技能各说各话 | 强制 brand-strategy 先行作为锚点 |
| FM-BRANDCREATIVE-004 | major | 所选 sub-skill 无 pipeline | KR-B1 < 50% | degrade 声明,标 production_blocker |
| FM-BRANDCREATIVE-005 | major | 竞品维度 < 4 | comparison_matrix 过浅 | 追问关键维度 |

---

## 6. Gap Ledger

| gap_id | missing_or_ambiguous_input | affected_output | severity | user_followup_needed | proposed_question | fallback_if_unanswered |
|---|---|---|---|---|---|---|
| GAP-001 | `<填:示例 — 品牌定位仅形容词>` | brand_brief | blocker | yes | "[synthetic] 品牌的差异化定位是?(不是'年轻/科技'这类形容词,而是'为谁解决什么、与谁不同')" | 不允许执行 |
| GAP-002 | `<填:示例 — 商标禁区未提供>` | logo_spec.legal_check | blocker | yes | "[synthetic] 是否有需规避的商标/竞品视觉/文化禁区?" | 标 [待法务确认],高风险阻断 |
| GAP-003 | `<填:示例 — 所选 sub-skill 无 pipeline>` | 对应 phase 产出 | major | no | — | degrade,标"该 sub-skill alpha 未实装" |

---

## 7. Assumption / Inference Ledger

| assumption_id | inferred_value | basis | confidence | risk_if_wrong | must_label_in_output |
|---|---|---|---|---|---|
| ASM-001 | `<填:示例 — 假设主用于数字渠道>` | `<填:无印刷/包装场景描述>` | medium | low | yes |
| ASM-002 | `<填:示例 — 假设品牌调性偏专业稳重>` | `<填:基于 B 端目标推断>` | medium | medium | yes |
| ASM-003 | `<填:示例 — 假设无现有品牌资产>` | `<填:未提供既有资产>` | high | low | yes |

---

## 8. Clarification Questions

| question_id | question | why_needed | blocking_level | answer_format_hint |
|---|---|---|---|---|
| Q-001 | `<填:示例 — 品牌差异化定位?>` | 防策略空心化(FM-001) | blocker | "为谁解决什么 + 与谁不同"(非形容词) |
| Q-002 | `<填:示例 — 涉及哪些 sub-skill?>` | 确定执行范围 + 是否有 pipeline | blocker | 列表(logo/color/type/VI/voice/...) |
| Q-003 | `<填:示例 — 商标/法务/文化禁区?>` | logo legal_check(FM-002) | blocker | 禁区清单 |
| Q-004 | `<填:示例 — 至少 3 个竞品信息?>` | 差异化依据 | major | 竞品名 + 视觉/定位 |

---

## 9. Input Decision

```
input_decision: <ready | ready_with_assumptions | needs_user_clarification | blocked_insufficient_input>
```

| 字段 | 内容 |
|---|---|
| decision | `<填 §5 规则结论>` |
| rationale | `<填:策略空心/商标禁区缺 → blocked 或 needs_clarification;所选 sub-skill 无 pipeline → degrade 声明;含推断 → ready_with_assumptions;完整 → ready>` |
| required_before_execution | `<填:需答 Q-001~003>` |
| allowed_to_proceed | yes / no |
| conditions_if_proceed | `<填:如"必须先 brand-strategy 锚点 + 标 ASM-001~003 + 声明所选 sub-skill 的 alpha 限制">` |

---

## 10. Handoff To Execution

| 字段 | 内容 |
|---|---|
| approved_inputs | `<填:确认可用的输入清单>` |
| gaps_to_carry_forward | `<填:影响策略/法务/跨 skill 一致性的 gap>` |
| assumptions_to_label | `<填:ASM-X 必须在输出标注>` |
| confidence_boundary | `<填:整体可靠性上限;alpha 阶段须声明 sub-skill pipeline 覆盖现状>` |
| traceability_requirements | `<填:每个 sub-skill 产出 keyword_lineage 链接 brand-strategy>` |
