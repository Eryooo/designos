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

### 2a. Evidence Type Classification (S2-H9 FB-02)

> **目的**:显式识别证据类型,区分产品 UI 截图 / web capture / 文档位图 / PRD 文本,确保 uxeval 只在有真实界面证据时启动评估。文档截图/PDF 位图/PRD 文本可用于需求理解,但不可作为 UX 问题的证据。

| 字段 | 取值(枚举) | 说明 |
|---|---|---|
| evidence_type | product_ui_screenshot | 产品真实界面截图(client 模式:桌面/移动端/Web 应用) |
|  | web_capture | Web 模式实时采集(浏览器 DOM / 页面截图) |
|  | prototype_capture | 原型工具/Figma 高保真原型截图 |
|  | document_screenshot | 文档页面截图(需求文档/PPT/Word) |
|  | pdf_page_image | PDF 分页位图(文档插图) |
|  | prd_text | PRD / 需求说明纯文本 |
|  | mixed | 混合(部分 UI 截图 + 部分文档位图) |
|  | unknown | 无法判定 |
| evidence_type_confidence | high / medium / low | 判定置信度 |
| evidence_type_reason | `<填:为何判定为此类型,关键特征(如截图含应用 chrome/浏览器地址栏 vs 文档页眉页脚)>` | 推理依据 |
| can_support_ux_evaluation | yes | 可支持完整 UX 启发式评估(有真实界面+状态) |
|  | partial | 可用于需求理解/评估准备,但不可作为 UX 问题证据 |
|  | no | 当前证据不足以启动任何 UX 评估 |
| missing_ui_evidence | `<填:需补哪些页面/状态截图,如核心流程关键页+空/错/加载态>` | 与 uxeval 必需证据比对 |

### 规则(Trial-001 FB-02 护栏)

- 若 `evidence_type ∈ {product_ui_screenshot, web_capture, prototype_capture}` 且含关键页状态 → `can_support_ux_evaluation = yes`。
- 若 `evidence_type ∈ {document_screenshot, pdf_page_image, prd_text}` → `can_support_ux_evaluation = partial`(仅需求理解,不可作 UX 问题证据)。
- 若 `evidence_type = mixed`,必须在 `evidence_type_reason` 列出"哪部分是 UI 截图(可评估),哪部分只是文档位图(不可评估)"。
- 若 `can_support_ux_evaluation = partial | no`,必须填写 `missing_ui_evidence`(对齐 §7 Gap Ledger 与 §8 Recommended Missing Fields)。
- **守门规则**(关联 §9 input_decision / FM-UXEVAL-001 / FM-UXEVAL-003):
  - `evidence_type ∈ {product_ui_screenshot, web_capture, prototype_capture}` 且含状态 → 允许 `input_decision = ready | ready_with_assumptions`。
  - `evidence_type ∈ {document_screenshot, pdf_page_image, prd_text}` → `input_decision` 不得为 `ready`;至多 `needs_user_clarification`;若无其他 UI 证据 → `blocked_insufficient_input`(输出 `delivery_state = supplement_required`)。
  - `can_support_ux_evaluation = no` → `input_decision = blocked_insufficient_input`(FM-UXEVAL-001 预防,禁止产出无证据 issue)。
  - **禁止**:把 PRD 推断/文档位图当作界面证据产出 UX issue(FM-UXEVAL-003 守门)。

### 示例(synthetic only)

```
evidence_type: pdf_page_image
evidence_type_confidence: high
evidence_type_reason: 现有图像为 PDF 分页位图(文档页眉页脚/文档排版样式),无应用 chrome/UI 控件,判定为文档截图而非产品界面。
can_support_ux_evaluation: no
missing_ui_evidence: 核心流程(如统一待办处理/出差报销/全局搜索)关键页截图;关键页空态/错误态/加载态/无权限态截图;至少 1 条核心流程的端到端截图序列。
```

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

### Recommended Missing Fields (S2-H7.1)

> 针对本次 run 的输入缺口，推荐用户补充的字段（按质量影响排序）。

| field_category | recommended_field | why_important | minimum_needed_to_continue | can_continue_without |
|---|---|---|---|---|
| `<填:示例 — demo_access>` | 可访问的 demo URL 或截图 | 证据采集基础 | 至少主要页面截图 | no |
| `<填:示例 — page_states>` | 关键页面状态描述(空/加载/错误) | 完整性评估 | 至少主流程页面 | yes (降级覆盖范围) |
| `<填:示例 — screen_description>` | 截图文字描述(OCR 失败时) | 问题归因准确性 | 可从截图推断 | yes (标 [inferred]) |
| `<填:示例 — main_tasks>` | 主任务清单 | task-generation 准确性 | 可从页面推断 | yes (标 [inferred]) |

### Recommended User Questions (S2-H7.1)

> 可以直接问用户的问题，帮助用户快速补充关键输入。

| question_id | question | expected_answer_format | blocking_level | linked_gap |
|---|---|---|---|---|
| RQ-001 | `<填:示例 — 本次评估模式(client/web)?web 请提供 demo URL>` | client/web + URL | blocker | GAP-001 |
| RQ-002 | `<填:示例 — 关键截图能否补充文字描述?>` | 页面名 + 描述 | major | GAP-002 |
| RQ-003 | `<填:示例 — 主要用户任务有哪些?>` | 任务清单 | minor | GAP-003 |

### Minimum Needed to Continue (S2-H7.1)

> 如果用户无法补全所有字段，继续执行的最低要求。

- **blocker 级 gap 必须解决**: GAP-001 (demo_access) — 至少主要页面截图
- **major 级 gap 可带 assumption**: GAP-002 (screen_description) — 标 [证据不足]
- **minor 级 gap 可降级 scope**: 可减少边界场景覆盖或降低问题密度

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
