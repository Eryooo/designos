# Input Quality Gate — uxeval

> **🚫 SYNTHETIC / SANITIZED ONLY** — 本模板及示例不含真实业务/客户/截图/账号/内部 URL。
> **本模板性质**:执行前输入质量门(引用层,非新标准)。引用 S2-H1/H1.1 KR、S2-H2 golden、S2-H3 failure modes、S2-H4 self review gate;输入诊断引 `knowledge/design-work-paradigm/01-input-diagnosis.md`;证据充分性引 `knowledge/ux/evidence-quality.md`(`ux.evidence-quality`);skill 约束引 `skills/uxeval/constitution.md`(8 条) + `skills/uxeval/INPUT.md`。
> **执行顺序**:见 `docs/audits/S2-H5-INPUT-QUALITY-GATE.md` §4(8 步)。
> **当前状态**:uxeval = beta,prompt-grade,无 runtime;`gate:` 是暂停门非 kernel quality_gates。本 gate 通过 ≠ 输入完美。

---

## 1. Metadata

| 字段 | 值(填写时替换) |
|---|---|
| skill | uxeval |
| run_id | `run-synth-XXXX` |
| reviewer | `<reviewer-id>` |
| date | `YYYY-MM-DD` |
| requested_output | `<填:目标产出,如完整 issue 报告 + 旅程地图 + delivery_assessment>` |
| input_sources | `<填:截图/URL/PRD/范围说明 等清单>` |
| input_decision | `<填 §9 结论>` |

---

## 2. Input Source Inventory

| source_id | source_type | path_or_description | available | reliability | notes |
|---|---|---|---|---|---|
| S-001 | prd | `<填:PRD 或 feature_spec 路径>` | yes / no | high / medium / low / unknown | `<填>` |
| S-002 | screenshot | `<填:client 模式截图目录>` | yes / no | high / medium / low / unknown | `<填:数量 + 是否 sanitized>` |
| S-003 | url | `<填:web 模式 sanitized demo URL>` | yes / no | high / medium / low / unknown | `<填:严禁真实生产 URL>` |
| S-004 | text_brief | `<填:scope_md / screens-description.md>` | yes / no | high / medium / low / unknown | `<填>` |

---

## 3. Required Input Check

| input_item | required | present | evidence | gap_if_missing | decision_impact |
|---|---|---|---|---|---|
| 评估目标(可用性/合规/...) | yes | yes / no | `<填>` | 无目标无法 principle-mapping | block 或 needs_clarification |
| 评估模式(client / web) | yes | yes / no | `<填>` | 无法分支(需求不同输入) | block |
| 关键页面/流程清单 | yes | yes / no | `<填>` | task-generation 无范围 | needs_clarification |
| 截图(client 模式) | required_when="client" | yes / no | `<填:S-002>` | 无证据 = FM-UXEVAL-001 触发 | block |
| Web URL(web 模式) | required_when="web" | yes / no | `<填:S-003,sanitized>` | 无法采集证据 | block |
| PRD / 功能说明 | yes | yes / no | `<填>` | 无法区分"功能在不在"vs"功能好不好用" | needs_clarification |
| 用户角色 | yes | yes / no | `<填>` | 旅程角色无主体 | needs_clarification |
| 已知敏感数据范围 | partial | yes / no | `<填:哪些字段需打码>` | 防止泄露真实账号/PII | block(若涉真实数据) |

---

## 4. Golden Template Input Readiness

> 引用 `skills/uxeval/templates/golden-evaluation-report.md` "输入前提" + "必填章节"。

| golden_section | required_input | input_available | can_infer | risk_if_inferred |
|---|---|---|---|---|
| 需求理解 | PRD + scope | yes / no / partial | partial | 推断业务目标风险中 |
| 启发式映射 | 关键页面 + 评估目标 | yes / no / partial | partial | 推断适用 heuristic 风险中 |
| 旅程地图 | 用户角色 + 任务清单 | yes / no / partial | partial | 推断旅程阶段风险中 |
| 任务清单 | 旅程 + 状态边界 | yes / no / partial | partial | 推断 edge tasks 风险高 |
| 证据采集 | 截图 / Web 可达 | yes / no / partial | no | 无证据则 V1 触发 |
| 问题归因 | 证据 + 启发式映射 | yes / no / partial | no | 无证据无法归因 |
| 交付状态评估 | 证据覆盖度 | yes / no / partial | partial | 推断需降级为 fallback_safe |

---

## 5. Failure Mode Input Risk Check

> 从 `skills/uxeval/eval/failure/failure-modes.md` 抽取输入相关 FM。

| fm_id | severity | input_risk | trigger_if_missing | prevention_action |
|---|---|---|---|---|
| FM-UXEVAL-001 | blocker | 截图/URL 缺 → evidence_refs 必空 | 任一 issue 无证据来源 | 不允许执行,要求补证据 |
| FM-UXEVAL-002 | blocker | 真实账号/PII/内部 URL 进入截图 | 输入含未打码敏感信息 | 阻断,要求脱敏 |
| FM-UXEVAL-005 | major | PRD 缺 → 无法区分功能 vs 体验 | 把功能缺失当体验问题 | 追问 PRD 范围 |
| FM-UXEVAL-006 | major | 截图与场景描述不匹配 | scene_evidence_validation 失败 | 追问场景对应关系 |
| FM-UXEVAL-007 | major | 证据覆盖不足却声明完整交付 | coverage 三属性不达标 | 强制降级 delivery_assessment |

---

## 6. Gap Ledger

| gap_id | missing_or_ambiguous_input | affected_output | severity | user_followup_needed | proposed_question | fallback_if_unanswered |
|---|---|---|---|---|---|---|
| GAP-001 | `<填:示例 — 缺 web 模式 demo URL>` | 证据采集 | blocker | yes | "[synthetic] 本次评估是 client 还是 web 模式?web 模式请提供 sanitized demo URL" | 不允许执行 |
| GAP-002 | `<填:示例 — 截图无 OCR 识别失败>` | 问题归因 | major | yes | "[synthetic] 关键截图能否补 screens-description.md?" | 标 [证据不足] 移 unverified_issues |
| GAP-003 | `<填:示例 — 缺主任务清单>` | task-generation | minor | no | — | 推断主任务,标 [inferred] |

---

## 7. Assumption / Inference Ledger

| assumption_id | inferred_value | basis | confidence | risk_if_wrong | must_label_in_output |
|---|---|---|---|---|---|
| ASM-001 | `<填:示例 — 假设默认所有用户已登录>` | `<填:PRD 未提注册流程>` | medium | medium | yes |
| ASM-002 | `<填:示例 — 假设主旅程为「查询 → 筛选 → 下单」>` | `<填:截图 OCR 推断>` | low | high | yes |
| ASM-003 | `<填:示例 — 假设 WCAG AA 是合规基线>` | `<填:行业惯例>` | high | low | yes |

---

## 8. Clarification Questions

| question_id | question | why_needed | blocking_level | answer_format_hint |
|---|---|---|---|---|
| Q-001 | `<填:示例 — 本次评估模式 client / web?>` | 决定证据采集方式 | blocker | 二选一 |
| Q-002 | `<填:示例 — 关键评估页面/流程清单?>` | task-generation 必需 | blocker | 列表(每项含页面名 + 任务) |
| Q-003 | `<填:示例 — 截图是否含真实账号/PII 需打码?>` | 防止 FM-UXEVAL-002 | blocker | yes/no + 待打码字段清单 |
| Q-004 | `<填:示例 — 是否覆盖 error / 权限态评估?>` | 任务清单完整度 | major | yes/no |

---

## 9. Input Decision

```
input_decision: <ready | ready_with_assumptions | needs_user_clarification | blocked_insufficient_input>
```

| 字段 | 内容 |
|---|---|
| decision | `<填 §5 规则结论>` |
| rationale | `<填:无截图/URL → blocked;模式不明 → needs_clarification;含推断 → ready_with_assumptions;完整 → ready>` |
| required_before_execution | `<填:需用户答 Q-001~003>` |
| allowed_to_proceed | yes / no |
| conditions_if_proceed | `<填:如"必须在 issue 报告标 ASM-001~003 + delivery_assessment 降级">` |

---

## 10. Handoff To Execution

| 字段 | 内容 |
|---|---|
| approved_inputs | `<填:确认可用的输入清单>` |
| gaps_to_carry_forward | `<填:将影响 issue 归因 / coverage 的 gap>` |
| assumptions_to_label | `<填:必须在 issue 报告标的 ASM 列表>` |
| confidence_boundary | `<填:整体可信度上限,如 fallback_safe / supplement_required>` |
| traceability_requirements | `<填:每条 issue 必须 4 维链接(heuristic + 旅程 + 任务 + evidence)>` |
