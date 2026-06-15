# Input Quality Gate — prd2proto

> **🚫 SYNTHETIC / SANITIZED ONLY** — 本模板及示例不含真实业务/客户/PRD/设计资产。
> **本模板性质**:执行前输入质量门(引用层,非新标准)。引用 S2-H1/H1.1 KR、S2-H2 golden、S2-H3 failure modes、S2-H4 self review gate(对偶);输入诊断方法论引 `knowledge/design-work-paradigm/01-input-diagnosis.md`;skill 约束引 `skills/prd2proto/constitution.md` + `PILOT-BOUNDARY.md` + `pipeline.yaml` upstream_refs。
> **执行顺序**:见 `docs/audits/S2-H5-INPUT-QUALITY-GATE.md` §4(8 步)。
> **当前状态**:prd2proto = pilot,runtime-grade。本 gate 通过 ≠ 输入完美——只是输入足够支撑下游产出。

---

## 1. Metadata

| 字段 | 值(填写时替换) |
|---|---|
| skill | prd2proto |
| run_id | `run-synth-XXXX` |
| reviewer | `<reviewer-id>` |
| date | `YYYY-MM-DD` |
| requested_output | `<填:目标产出,如 18 stage 推理资产链 + prototype_code(pm 模式)>` |
| input_sources | `<填:用户提交的 PRD / 截图 / brief 等清单>` |
| input_decision | `<填 §9 结论>` |

---

## 2. Input Source Inventory

| source_id | source_type | path_or_description | available | reliability | notes |
|---|---|---|---|---|---|
| S-001 | prd | `<填:PRD 文件路径>` | yes / no | high / medium / low / unknown | `<填>` |
| S-002 | text_brief | `<填:scope_md 或简报>` | yes / no | high / medium / low / unknown | `<填>` |
| S-003 | existing_artifact | `<填:ai-analytics 上游 design_strategy(可选)>` | yes / no | high / medium / low / unknown | `<填>` |
| S-004 | design_file | `<填:Figma/MasterGo DSL(designer-dsl 模式必需)>` | yes / no | high / medium / low / unknown | `<填>` |

---

## 3. Required Input Check

| input_item | required | present | evidence | gap_if_missing | decision_impact |
|---|---|---|---|---|---|
| PRD 文件 + 内容 | yes | yes / no | `<填:S-001>` | 无法 input-diagnosis,直接 blocker | block |
| 业务目标(business_goal) | yes | yes / no | `<填:PRD 章节路径>` | design-objectives 缺锚点 | block 或 needs_clarification |
| 用户角色(target_audience) | yes | yes / no | `<填>` | user-task-modeling 无主体 | needs_clarification |
| 页面范围 / 模块清单 | yes | yes / no | `<填>` | IA / page-flow 无范围 | needs_clarification |
| 交互状态边界 | partial | yes / no | `<填:loading/empty/error 等>` | state-matrix 不完整 | ready_with_assumptions(标 inferred) |
| 设计系统 / 组件约束 | partial | yes / no | `<填:antd-pro/linear/...>` | spec-generation 模板需推断 | ready_with_assumptions |
| 技术边界(框架/兼容) | partial | yes / no | `<填>` | code-generation 默认 React+antd | ready_with_assumptions |
| mode 选择(pm/spec/dsl) | yes | yes / no | `<填>` | 无法分支执行 | block |
| Figma/MasterGo DSL | required_when="designer-dsl" | yes / no | `<填>` | dsl 模式必需(已在 v2 中删除,N/A) | not_applicable |

---

## 4. Golden Template Input Readiness

> 引用 `skills/prd2proto/templates/golden-prd2proto-output.md` "输入前提" + "必填章节"。

| golden_section | required_input | input_available | can_infer | risk_if_inferred |
|---|---|---|---|---|
| input-diagnosis(requirement_inventory) | PRD 全文 + scope_md | yes / no / partial | no | 无法启动 |
| design-objectives | 业务目标 / 用户目标 | yes / no / partial | partial | 推断业务目标风险高 |
| product-archetype | 产品类型 / 用户群 | yes / no / partial | yes | 推断需标 [inferred] |
| user-task-modeling | 用户角色 + 主任务 | yes / no / partial | partial | 推断 edge tasks 风险中 |
| business-flow-modeling | 业务规则 / 状态机说明 | yes / no / partial | no | 推断业务流程风险极高 |
| information-architecture | 模块清单 / 信息层级 | yes / no / partial | partial | 默认 antd-pro 三段导航 |
| component-strategy | 设计系统约束 | yes / no / partial | yes | 默认 antd-pro 组件库 |
| state-matrix | 交互状态边界 | yes / no / partial | partial | 默认 7 状态枚举 |
| design-spec-generation | 视觉风格偏好 | yes / no / partial | yes | 默认模板库选 |
| token-extraction | design tokens 来源 | yes / no / partial | yes | 默认从 spec 提取 |

---

## 5. Failure Mode Input Risk Check

> 从 `skills/prd2proto/eval/failure/failure-modes.md` 抽取与输入相关的 blocker / major FM。

| fm_id | severity | input_risk | trigger_if_missing | prevention_action |
|---|---|---|---|---|
| FM-PRD2PROTO-001 | blocker | PRD/scope 缺导致 schema 校验无法启动 | 任一必需字段无来源 | 不允许进入执行,阻断 |
| FM-PRD2PROTO-002 | blocker | 业务目标/用户角色缺导致 traceability 无锚点 | decision_trace 无 upstream | 追问业务目标 + 用户角色 |
| FM-PRD2PROTO-004 | blocker | 输入声称"已生产就绪"却含 pilot 边界 | not_allowed_claims 命中 | 修正输入端口径声明 |
| FM-PRD2PROTO-005 | major | PRD 缺业务目标导致静默脑补 | gaps[] 为空但 PRD 缺信息 | 强制记入 gap ledger |
| FM-PRD2PROTO-007 | major | 模式选择不明导致 18 stage 链断 | mode 字段缺失 | 追问 mode |

---

## 6. Gap Ledger

| gap_id | missing_or_ambiguous_input | affected_output | severity | user_followup_needed | proposed_question | fallback_if_unanswered |
|---|---|---|---|---|---|---|
| GAP-001 | `<填:示例 — 业务目标未量化>` | design-objectives | blocker | yes | "[synthetic] 本次目标的核心 KPI 是什么(转化率/留存/GMV/...)?" | 不允许执行 |
| GAP-002 | `<填:示例 — edge tasks 未列>` | user-task-modeling | major | yes | "[synthetic] 是否需要覆盖错误/权限/网络异常路径?" | 标 [inferred] 标准 7 状态 |
| GAP-003 | `<填:示例 — 设计系统未指定>` | component-strategy | minor | no | — | 默认 antd-pro,标 inferred |

---

## 7. Assumption / Inference Ledger

| assumption_id | inferred_value | basis | confidence | risk_if_wrong | must_label_in_output |
|---|---|---|---|---|---|
| ASM-001 | `<填:示例 — 假设用户主要使用桌面端>` | `<填:基于 PRD 提到 "管理后台">` | high / medium / low | medium | yes |
| ASM-002 | `<填:示例 — 假设非高并发场景>` | `<填:无性能要求描述,默认>` | medium | low | yes |
| ASM-003 | `<填:示例 — 假设无国际化需求>` | `<填:PRD 仅含中文示例>` | low | medium | yes |

---

## 8. Clarification Questions

| question_id | question | why_needed | blocking_level | answer_format_hint |
|---|---|---|---|---|
| Q-001 | `<填:示例 — 本次目标的核心 KPI 是?>` | 无业务目标无法 design-objectives | blocker | 一句话 KPI(如"3 个月内试用转化 ≥ 20%") |
| Q-002 | `<填:示例 — 主用户角色?>` | user-task-modeling 必需 | blocker | 角色名 + 主要任务 |
| Q-003 | `<填:示例 — 选择 pm / designer-spec / designer-dsl?>` | 决定执行分支 | blocker | 三选一 |
| Q-004 | `<填:示例 — 是否需要覆盖 edge tasks?>` | state-matrix 完整度 | major | yes/no + 关键异常清单 |

---

## 9. Input Decision

```
input_decision: <ready | ready_with_assumptions | needs_user_clarification | blocked_insufficient_input>
```

| 字段 | 内容 |
|---|---|
| decision | `<填 §5 规则结论>` |
| rationale | `<填:命中的 blocker/必需缺失 → blocked;少量追问可补 → needs_clarification;含推断 → ready_with_assumptions;完整 → ready>` |
| required_before_execution | `<填:需用户答 Q-001/Q-002 等>` |
| allowed_to_proceed | yes / no |
| conditions_if_proceed | `<填:如"必须在输出标注 ASM-001~003 + GAP-002">` |

---

## 10. Handoff To Execution

| 字段 | 内容 |
|---|---|
| approved_inputs | `<填:确认可用的输入清单(S-001 等)>` |
| gaps_to_carry_forward | `<填:GAP-001~003 中将被带入执行的>` |
| assumptions_to_label | `<填:ASM-001~003 必须在输出 inferred_fields 标注>` |
| confidence_boundary | `<填:整体置信度上限,如 ≤ 0.75 因业务目标推断>` |
| traceability_requirements | `<填:每个推断决策必须在 decision_trace 链接到对应 ASM 编号>` |
