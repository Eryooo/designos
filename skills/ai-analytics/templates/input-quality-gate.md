# Input Quality Gate — ai-analytics

> **🚫 SYNTHETIC / SANITIZED ONLY** — 本模板及示例不含真实业务/客户/竞品价格/市场数据。
> **本模板性质**:执行前输入质量门(引用层,非新标准)。引用 S2-H1/H1.1 KR、S2-H2 golden、S2-H3 failure modes、S2-H4 self review gate;输入诊断引 `knowledge/design-work-paradigm/01-input-diagnosis.md`;数据完整度引 `knowledge/research/`(`research.data-completeness-rubric` 等已有资产);skill 约束引 `skills/ai-analytics/constitution.md`(4 条)。
> **执行顺序**:见 `docs/audits/S2-H5-INPUT-QUALITY-GATE.md` §4(8 步)。
> **当前状态**:ai-analytics = pilot,prompt-grade,无 runtime;pilot 仅稳产 design_strategy + user_persona。本 gate 通过 ≠ 输入完美。

---

## 1. Metadata

| 字段 | 值(填写时替换) |
|---|---|
| skill | ai-analytics |
| run_id | `run-synth-XXXX` |
| reviewer | `<reviewer-id>` |
| date | `YYYY-MM-DD` |
| requested_output | `<填:目标产出,如 design_strategy + user_persona + competitive_matrix>` |
| input_sources | `<填:竞品资料/PRD/用户访谈 等清单>` |
| input_decision | `<填 §9 结论>` |

---

## 2. Input Source Inventory

| source_id | source_type | path_or_description | available | reliability | notes |
|---|---|---|---|---|---|
| S-001 | text_brief | `<填:分析目标 / 行业背景>` | yes / no | high / medium / low / unknown | `<填>` |
| S-002 | data_table | `<填:竞品资料 / 比较表>` | yes / no | high / medium / low / unknown | `<填:数量 + 可信度>` |
| S-003 | text_brief | `<填:用户访谈/问卷(synthetic)>` | yes / no | high / medium / low / unknown | `<填>` |
| S-004 | existing_artifact | `<填:PRD 上游(若与 prd2proto 同步)>` | yes / no | high / medium / low / unknown | `<填>` |

---

## 3. Required Input Check

| input_item | required | present | evidence | gap_if_missing | decision_impact |
|---|---|---|---|---|---|
| 分析目标(竞品/市场/persona) | yes | yes / no | `<填>` | 无目标无法 methodology-selection | block 或 needs_clarification |
| 行业 / 产品背景 | yes | yes / no | `<填>` | strategy-synthesis 无上下文 | needs_clarification |
| 竞品范围(≥ 3 个) | yes | yes / no | `<填:已有 N 个>` | comparison_matrix 不足 | needs_clarification 或 ready_with_assumptions |
| 数据来源(各 finding 必有) | yes | yes / no | `<填:S-002>` | FM-AIANALYTICS-001 编造数据触发 | block |
| 用户/市场假设标注 | yes | yes / no | `<填>` | 无法标 [inferred] | needs_clarification |
| 不可验证信息明示 | partial | yes / no | `<填>` | 数据缺口未声明 | ready_with_assumptions |
| 期望产出类型清单 | yes | yes / no | `<填:design_strategy / user_persona>` | 无法限定输出范围 | block |

---

## 4. Golden Template Input Readiness

> 引用 `skills/ai-analytics/templates/golden-analysis-output.md` "输入前提" + "必填章节"。

| golden_section | required_input | input_available | can_infer | risk_if_inferred |
|---|---|---|---|---|
| collected_data | 竞品资料 + 用户访谈 + 行业数据 | yes / no / partial | no | 无数据无法启动 |
| competitive_matrix | 竞品 ≥ 3 个 + 维度 ≥ 4 | yes / no / partial | partial | 维度推断风险中 |
| design_strategy.target_audience | 用户群体描述 | yes / no / partial | partial | 推断风险中 |
| design_strategy.business_goal | 业务目标 | yes / no / partial | no | 必填,缺失需 block |
| user_persona.goals/pain_points | 用户访谈/调研 | yes / no / partial | partial | 仅口号风险高 |
| data_completeness_assessment | coverage 真实评估 | yes / no / partial | no | coverage 必须真实 |

---

## 5. Failure Mode Input Risk Check

> 从 `skills/ai-analytics/eval/failure/failure-modes.md` 抽取输入相关 FM。

| fm_id | severity | input_risk | trigger_if_missing | prevention_action |
|---|---|---|---|---|
| FM-AIANALYTICS-001 | blocker | 数据来源缺 → 编造数据(constitution 1) | finding 无 evidence_refs | 不允许执行,要求补来源 |
| FM-AIANALYTICS-002 | blocker | 必填字段无输入支撑 | target_audience / business_goal 推断不出 | 追问业务目标 + 用户群 |
| FM-AIANALYTICS-003 | blocker | 输入量明显不足却被误标 coverage ≥ 0.70 | 资料 < 阈值 | 严格按 collected_data 真实计算 |
| FM-AIANALYTICS-007 | major | 竞品维度 < 4 | comparison_matrix 过浅 | 追问关键维度 |
| FM-AIANALYTICS-008 | minor | methodology 选择缺数据支撑 | 选 KANO/JTBD 但无对应输入 | 改选 SWOT 等低数据要求方法 |

---

## 6. Gap Ledger

| gap_id | missing_or_ambiguous_input | affected_output | severity | user_followup_needed | proposed_question | fallback_if_unanswered |
|---|---|---|---|---|---|---|
| GAP-001 | `<填:示例 — 竞品 < 3 个>` | competitive_matrix | blocker | yes | "[synthetic] 是否能再补 1-2 个核心竞品资料?" | 不允许执行 |
| GAP-002 | `<填:示例 — 用户访谈缺 pain_points>` | user_persona | major | yes | "[synthetic] 是否有用户访谈/问卷数据可补充?" | 标 [inferred] 并降级 confidence |
| GAP-003 | `<填:示例 — 行业平均无来源>` | design_strategy | minor | no | — | 标 [inferred] + risk_if_wrong |

---

## 7. Assumption / Inference Ledger

| assumption_id | inferred_value | basis | confidence | risk_if_wrong | must_label_in_output |
|---|---|---|---|---|---|
| ASM-001 | `<填:示例 — 假设竞品 A 主打中端市场>` | `<填:基于资料中价格区间推断>` | medium | medium | yes |
| ASM-002 | `<填:示例 — 假设目标人群有支付意愿>` | `<填:基于行业普遍假设>` | low | high | yes |
| ASM-003 | `<填:示例 — 假设无法律合规风险>` | `<填:无相关数据,默认>` | low | medium | yes |

---

## 8. Clarification Questions

| question_id | question | why_needed | blocking_level | answer_format_hint |
|---|---|---|---|---|
| Q-001 | `<填:示例 — 本次分析的核心业务目标?>` | design_strategy.business_goal 必填 | blocker | 一句话目标 + 量化 KPI |
| Q-002 | `<填:示例 — 主要竞品名单(≥ 3)?>` | competitive_matrix 基础 | blocker | 竞品名 + 简介 + 资料链接 |
| Q-003 | `<填:示例 — 是否有用户访谈/问卷数据?>` | user_persona 质量 | major | yes/no + 数据来源 |
| Q-004 | `<填:示例 — 期望优先 methodology?>` | methodology-selection | minor | SWOT / JTBD / PEST / 自动 |

---

## 9. Input Decision

```
input_decision: <ready | ready_with_assumptions | needs_user_clarification | blocked_insufficient_input>
```

| 字段 | 内容 |
|---|---|
| decision | `<填 §5 规则结论>` |
| rationale | `<填:数据来源缺/必填字段缺 → blocked;竞品<3 → needs_clarification;含 inferred → ready_with_assumptions;完整 → ready>` |
| required_before_execution | `<填:需答 Q-001/002 等>` |
| allowed_to_proceed | yes / no |
| conditions_if_proceed | `<填:如"必须在 design_strategy 标 ASM-001~003 + data_completeness_assessment.coverage 真实计算">` |

---

## 10. Handoff To Execution

| 字段 | 内容 |
|---|---|
| approved_inputs | `<填:确认可用的输入清单>` |
| gaps_to_carry_forward | `<填:GAP-X 影响 design_strategy 的项>` |
| assumptions_to_label | `<填:ASM-X 必须在输出 [inferred] 标注>` |
| confidence_boundary | `<填:整体置信度上限 + coverage 真实值>` |
| traceability_requirements | `<填:每个 finding 必须 evidence_refs → collected_data 真实条目>` |
