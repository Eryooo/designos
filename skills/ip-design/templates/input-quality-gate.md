# Input Quality Gate — ip-design

> **🚫 SYNTHETIC / SANITIZED ONLY** — 本模板及示例不含真实品牌/IP/客户/商标。
> **本模板性质**:执行前输入质量门(引用层,非新标准)。引用 S2-H1/H1.1 KR、S2-H2 golden、S2-H3 failure modes、S2-H4 self review gate;输入诊断引 `knowledge/design-work-paradigm/01-input-diagnosis.md`;skill 约束引 `skills/ip-design/constitution.md`(8 条)+ 9 维 rubric + `common-failure-modes`。
> **执行顺序**:见 `docs/audits/S2-H5-INPUT-QUALITY-GATE.md` §4(8 步)。
> **当前状态**:ip-design = pilot,prompt-grade,无 runtime。本 gate 通过 ≠ 输入完美。

---

## 1. Metadata

| 字段 | 值(填写时替换) |
|---|---|
| skill | ip-design |
| run_id | `run-synth-XXXX` |
| reviewer | `<reviewer-id>` |
| date | `YYYY-MM-DD` |
| requested_output | `<填:目标产出,如 6 阶段 IP 资产 + image_prompt_pack + professional_gap_report>` |
| input_sources | `<填:品牌背景/目标人群/竞品 IP 等清单>` |
| input_decision | `<填 §9 结论>` |

---

## 2. Input Source Inventory

| source_id | source_type | path_or_description | available | reliability | notes |
|---|---|---|---|---|---|
| S-001 | text_brief | `<填:品牌/业务背景>` | yes / no | high / medium / low / unknown | `<填>` |
| S-002 | text_brief | `<填:目标人群描述>` | yes / no | high / medium / low / unknown | `<填>` |
| S-003 | data_table | `<填:竞品 IP 信息(≥3)>` | yes / no | high / medium / low / unknown | `<填>` |
| S-004 | design_file | `<填:既有品牌资产(色彩/logo/字体,可选)>` | yes / no | high / medium / low / unknown | `<填:新品牌则 N/A>` |

---

## 3. Required Input Check

| input_item | required | present | evidence | gap_if_missing | decision_impact |
|---|---|---|---|---|---|
| 品牌 / 业务背景 | yes | yes / no | `<填>` | 无法 strategy-alignment | block 或 needs_clarification |
| 目标人群(职业/场景/痛点) | yes | yes / no | `<填>` | persona-modeling 无主体 | needs_clarification |
| IP 角色定位 | yes | yes / no | `<填:吉祥物/虚拟代言/...>` | 北极星推导无方向 | needs_clarification |
| 竞品 IP 信息(≥ 3) | yes | yes / no | `<填:S-003>` | 差异化无依据 = FM-IPDESIGN-001 风险 | needs_clarification |
| 品牌约束(既有资产) | partial | yes / no | `<填:S-004>` | 基因继承缺;新品牌跳过 | ready_with_assumptions |
| 视觉风格边界 | partial | yes / no | `<填:写实/卡通/极简>` | visual-translation 需推断 | ready_with_assumptions |
| 使用场景 | partial | yes / no | `<填:线上/线下/衍生品>` | brand-material-spec 需推断 | ready_with_assumptions |
| 禁忌项(文化/法务/品牌) | yes | yes / no | `<填>` | strict_avoidance 无来源 | needs_clarification |

---

## 4. Golden Template Input Readiness

> 引用 `skills/ip-design/templates/golden-ip-design-output.md` "输入前提" + "必填章节"。

| golden_section | required_input | input_available | can_infer | risk_if_inferred |
|---|---|---|---|---|
| brand_brief(M01) | 业务背景 + 目标人群 + 竞品 | yes / no / partial | partial | 北极星推断风险中 |
| worldview(M02) | 品牌价值 + 角色定位 | yes / no / partial | yes | 世界观推断需标 inferred |
| persona_profile(M03) | 目标人群 + 角色定位 | yes / no / partial | partial | 人格五要素推断风险高 |
| visual_spec(M04) | 视觉风格边界 + 品牌约束 | yes / no / partial | partial | **视觉先行风险**(必须先有 M01-M03) |
| image_prompt_pack | visual_spec + 禁忌项 | yes / no / partial | no | 无禁忌则 negative_prompt 缺 |
| content_plan(M05) | 使用场景 + 传播渠道 | yes / no / partial | yes | 推断需标 inferred |
| brand_material_spec(M06) | 使用场景 + 成本约束 | yes / no / partial | yes | 落地成本推断风险中 |

---

## 5. Failure Mode Input Risk Check

> 从 `skills/ip-design/eval/failure/failure-modes.md` 抽取输入相关 FM。

| fm_id | severity | input_risk | trigger_if_missing | prevention_action |
|---|---|---|---|---|
| FM-IPDESIGN-001 | blocker | 竞品 IP 缺 → 差异化无依据(D2 不合格) | 无竞品空白分析 | 追问竞品 IP(≥3) |
| FM-IPDESIGN-002 | blocker | 禁忌/法务输入缺 → D6 风险未标 | 无禁忌项来源 | 追问文化/法务禁忌 |
| FM-IPDESIGN-003 | blocker | 目标人群缺 → 人格扁平(D8 不合格) | 无用户洞察 | 追问目标人群痛点 |
| FM-IPDESIGN-004 | blocker | 无策略输入即要视觉 → 视觉先行 | 跳过 M01-M03 | 强制先建策略再视觉 |
| FM-IPDESIGN-007 | major | 输入不足处大量推断未标 | inferences[] 缺 | 强制标 [inferred] + 依据 |

---

## 6. Gap Ledger

| gap_id | missing_or_ambiguous_input | affected_output | severity | user_followup_needed | proposed_question | fallback_if_unanswered |
|---|---|---|---|---|---|---|
| GAP-001 | `<填:示例 — 竞品 IP < 3>` | brand_brief.differentiation | blocker | yes | "[synthetic] 能否补充至少 3 个竞品 IP 的视觉/定位信息?" | 差异化标 [inferred] 并降级,或阻断 |
| GAP-002 | `<填:示例 — 禁忌项未提供>` | visual_spec.strict_avoidance | blocker | yes | "[synthetic] 是否有文化/法务/品牌禁忌需规避?" | 用通用禁忌占位并标 [待确认] |
| GAP-003 | `<填:示例 — 视觉风格未指定>` | visual-translation | minor | no | — | 按北极星推断风格,标 [inferred] |

### Recommended Missing Fields (S2-H7.1)

> 针对本次 run 的输入缺口，推荐用户补充的字段（按质量影响排序）。

| field_category | recommended_field | why_important | minimum_needed_to_continue | can_continue_without |
|---|---|---|---|---|
| `<填:示例 — competitor_ips>` | 3-5 个竞品 IP 视觉/定位 | differentiation 基础 | 至少 3 个竞品 | no |
| `<填:示例 — brand_taboos>` | 文化/法务/品牌禁忌清单 | strict_avoidance 合规性 | 至少通用禁忌 | yes (标 [待确认]) |
| `<填:示例 — visual_style>` | 期望视觉风格描述 | visual-translation 准确性 | 可从北极星推断 | yes (标 [inferred]) |
| `<填:示例 — target_emotion>` | 目标情感调性 | emotional_quality 决策 | 可从品牌基因推断 | yes (标 [inferred]) |

### Recommended User Questions (S2-H7.1)

> 可以直接问用户的问题，帮助用户快速补充关键输入。

| question_id | question | expected_answer_format | blocking_level | linked_gap |
|---|---|---|---|---|
| RQ-001 | `<填:示例 — 主要竞品 IP 有哪些(至少 3 个)?>` | 竞品名 + 视觉风格 | blocker | GAP-001 |
| RQ-002 | `<填:示例 — 是否有文化/法务/品牌禁忌需规避?>` | yes/no + 禁忌清单 | blocker | GAP-002 |
| RQ-003 | `<填:示例 — 期望的视觉风格(简约/热闹/科技/...)?>` | 风格关键词 | minor | GAP-003 |

### Minimum Needed to Continue (S2-H7.1)

> 如果用户无法补全所有字段，继续执行的最低要求。

- **blocker 级 gap 必须解决**: GAP-001 (competitor_ips), GAP-002 (brand_taboos)
- **major 级 gap 可带 assumption**: 可从品牌基因推断部分属性
- **minor 级 gap 可降级 scope**: 可降低视觉方案数量或减少变体

---

## 7. Assumption / Inference Ledger

| assumption_id | inferred_value | basis | confidence | risk_if_wrong | must_label_in_output |
|---|---|---|---|---|---|
| ASM-001 | `<填:示例 — 假设暖色调更契合"亲和"人格>` | `<填:基于北极星推断>` | medium | medium | yes |
| ASM-002 | `<填:示例 — 假设主要线上使用>` | `<填:无线下场景描述>` | medium | low | yes |
| ASM-003 | `<填:示例 — 假设无现有品牌资产(新品牌)>` | `<填:未提供既有资产>` | high | low | yes |

---

## 8. Clarification Questions

| question_id | question | why_needed | blocking_level | answer_format_hint |
|---|---|---|---|---|
| Q-001 | `<填:示例 — IP 角色定位是?>` | 北极星 + 人格推导方向 | blocker | 吉祥物/虚拟代言/服务化身 + 一句话定位 |
| Q-002 | `<填:示例 — 至少 3 个竞品 IP?>` | 差异化(D2)必需 | blocker | 竞品 IP 名 + 视觉/定位描述 |
| Q-003 | `<填:示例 — 目标人群痛点?>` | 人格立体度(D8) | blocker | 职业 + 场景 + ≥3 痛点 |
| Q-004 | `<填:示例 — 文化/法务禁忌?>` | strict_avoidance(D6) | major | 禁忌清单 |

---

## 9. Input Decision

```
input_decision: <ready | ready_with_assumptions | needs_user_clarification | blocked_insufficient_input>
```

| 字段 | 内容 |
|---|---|
| decision | `<填 §5 规则结论>` |
| rationale | `<填:竞品/人群/禁忌缺 → needs_clarification 或 blocked;含推断 → ready_with_assumptions;完整 → ready>` |
| required_before_execution | `<填:需答 Q-001~003>` |
| allowed_to_proceed | yes / no |
| conditions_if_proceed | `<填:如"必须先建 M01-M03 策略链再进 M04 视觉 + 标 ASM-001~003">` |

---

## 10. Handoff To Execution

| 字段 | 内容 |
|---|---|
| approved_inputs | `<填:确认可用的输入清单>` |
| gaps_to_carry_forward | `<填:影响差异化/人格/视觉的 gap>` |
| assumptions_to_label | `<填:ASM-X 必须在 inferences[] 标注>` |
| confidence_boundary | `<填:9 维 rubric 自评置信度上限;D6 不确定打"中阶(待法务确认)">` |
| traceability_requirements | `<填:每阶段决策链接上阶段 + 方法论 id(design.ip.*)+ 输入条目>` |
