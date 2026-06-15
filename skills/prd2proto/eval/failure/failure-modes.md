# prd2proto Failure Mode Library (skill-specific)

> Skill: prd2proto · Layer: skill-specific failure library · Status: pilot
> 本文件是 S2-H1 rubric / S2-H1.1 OKR / S2-H2 golden template 的**配套失败层**。
> 通用失败模式真源仍是 `knowledge/design-work-paradigm/18-failure-modes.md`，本文件
> **不复制其全文**，只定义 prd2proto 专属的、可检测可对账的 failure modes。
> 所有示例均为 synthetic / sanitized，不含真实业务数据。

## 放置规则一致性（S2-H2.2）

- 本文件是 skill-specific 配套层，引用通用真源而非复制。
- 通用真源：`design-work-paradigm/18-failure-modes.md`（输入/输出/追溯类通用 FM）。
- 本文件覆盖：prd2proto 4 个一票否决项 + KR-P1~P5 未达标 + gap/assumption/confidence/traceability 失败 + golden template 低阶信号。

---

## FM-PRD2PROTO-001

- **id**: FM-PRD2PROTO-001
- **name**: Schema 违约交付（artifact 不符合 schema 仍标完成）
- **applies_to**: 全部 18 stage 的 artifact 输出
- **related_kr**: KR-P2（schema 真 blocking 通过率）, KR1.2（一票否决命中数）
- **related_golden_template_section**: §输出 artifact 列表 / §字段级要求
- **source_reference**: prd2proto constitution（schema_gate）; S2-H1 §2 prd2proto 一票否决 #1; design-work-paradigm/18-failure-modes.md
- **severity**: blocker
- **detection_signal**: artifact JSON 无法通过对应 `*.schema.json` 校验；required 字段缺失；枚举值越界
- **trigger_condition**: 任一 stage 输出未过 schema 校验但 pipeline 继续到下一 stage
- **examples_synthetic_only**: `requirement_inventory` 缺 `readiness_decision` 字段，却进入 design-objectives stage
- **remediation**: 在该 stage 停下，补齐 required 字段 / 修正枚举值，重跑 schema 校验通过后再继续
- **delivery_decision**: block
- **not_allowed_claims**: 不得声称"已生成完整推理资产链"
- **traceability_requirement**: schema 校验结果须记入 stage run-report，失败 stage id 可追溯
- **self_review_question**: 当前 stage 的 artifact 是否通过对应 `*.schema.json` 校验，且校验失败时已阻断进入下一 stage？

---

## FM-PRD2PROTO-002

- **id**: FM-PRD2PROTO-002
- **name**: Traceability 断裂（最终产物无法回溯到上游推理资产）
- **applies_to**: traceability-generation stage 及最终 prototype/design-spec
- **related_kr**: KR-P4（traceability 关键决策追溯率）, KR3.3（全局 traceability）
- **related_golden_template_section**: §traceability 规范
- **source_reference**: prd2proto constitution（traceability_gate）; S2-H1 §2 prd2proto 一票否决 #2; design-work-paradigm/19-traceability.md
- **severity**: blocker
- **detection_signal**: `traceability_map` 中关键设计决策无 upstream_artifacts 链接；decision_trace 为空
- **trigger_condition**: 最终代码/设计规范元素无法追溯到 design_objectives / user_task_map
- **examples_synthetic_only**: 生成了"结算页快捷支付"组件，但 traceability_map 无对应 business_goal 链接
- **remediation**: 补全 decision_trace，每个关键决策链接到上游 artifact_id；无法链接的标 gap
- **delivery_decision**: block
- **not_allowed_claims**: 不得声称"每个设计决策都可追溯"
- **traceability_requirement**: traceability_map 必须覆盖全部 P0 决策点
- **self_review_question**: 每个关键设计决策（IA/页面/组件/状态）是否在 traceability_map 中链接到上游 artifact_id，而非孤立存在？

---

## FM-PRD2PROTO-003

- **id**: FM-PRD2PROTO-003
- **name**: 代码宪法违反（生成代码违反 code-quality-constitution）
- **applies_to**: constrained-code-generation stage
- **related_kr**: KR-P3（code-constraint-gate 触发后修正率）
- **related_golden_template_section**: §字段级要求（代码约束）
- **source_reference**: prd2proto constitution（code_constraint_gate）; frontend.code-quality-constitution; S2-H1 §2 prd2proto 一票否决 #3
- **severity**: blocker
- **detection_signal**: 硬编码颜色/尺寸（未用 design token）；未用组件库；状态覆盖缺失
- **trigger_condition**: 生成代码含硬编码样式值或绕过 design_tokens.json
- **examples_synthetic_only**: 生成 `<div style="color:#1677ff">` 而非引用 `--color-brand-primary` token
- **remediation**: code-constraint-gate 拦截 → 重新生成，强制引用 design token 与组件库
- **delivery_decision**: block
- **not_allowed_claims**: 不得声称"生成生产级代码"
- **traceability_requirement**: 每处样式值可追溯到 design_tokens.json 条目
- **self_review_question**: 生成代码是否全部引用 design token 与组件库，无任何硬编码颜色/尺寸或非组件库 div？若有则是否已被 code-constraint-gate 阻断？

---

## FM-PRD2PROTO-004

- **id**: FM-PRD2PROTO-004
- **name**: Honesty 违反（把 mock/未验证产物标为已完成/可生产）
- **applies_to**: 全部 stage 的产出声明 + PILOT-BOUNDARY 边界
- **related_kr**: KR3.1（不可宣称项命中数）, KR1.1（最低交付线覆盖率）
- **related_golden_template_section**: §禁止声明
- **source_reference**: 全局底座 F-OverClaim; S2-H1 §1.3 通用一票否决底座; PILOT-BOUNDARY.md
- **severity**: blocker
- **detection_signal**: 文档/输出含"完全自动化/生产就绪/已达资深水准"；mock 路径标"已跑通"
- **trigger_condition**: 任一产出声明超出 prompt-grade / pilot 真实能力
- **examples_synthetic_only**: README 写"prd2proto 全自动生成可上线原型"
- **remediation**: 改为诚实边界表述（pilot / 需人工复核 / prompt-grade）
- **delivery_decision**: block
- **not_allowed_claims**: 见 detection_signal 全部禁词
- **traceability_requirement**: 能力声明须与 status.matrix maturity 一致
- **self_review_question**: 当前文档/输出是否命中任一 not_allowed_claims（完全自动化/生产就绪/已达资深），若命中是否已改为诚实边界表述并阻断发布？

---

## FM-PRD2PROTO-005

- **id**: FM-PRD2PROTO-005
- **name**: 静默补全缺失输入（gap 未显式标注）
- **applies_to**: input-diagnosis stage
- **related_kr**: KR3.2（gap/assumption 标注覆盖率）
- **related_golden_template_section**: §gap / assumption / confidence / traceability 规范
- **source_reference**: prd2proto constitution（gap_transparency_gate）; design-work-paradigm/01-input-diagnosis.md
- **severity**: major
- **detection_signal**: requirement_inventory 的 `gaps` 数组为空，但 PRD 明显缺业务目标/用户定义
- **trigger_condition**: 输入缺失被 LLM 静默脑补而非记入 gaps
- **examples_synthetic_only**: PRD 无成功指标，却直接假设"目标转化率 5%"未标 [inferred]
- **remediation**: 缺失信息全部记入 gaps；推断值标 [inferred] + 风险
- **delivery_decision**: gap
- **not_allowed_claims**: 不得声称"输入完整"
- **traceability_requirement**: 每个 gap 链接到受影响的下游 stage
- **self_review_question**: PRD 缺失的信息是否已全部记入 requirement_inventory 的 gaps，而不是被静默脑补？若有脑补是否需 gap/rework？

---

## FM-PRD2PROTO-006

- **id**: FM-PRD2PROTO-006
- **name**: 推断未标注 confidence（assumption 无风险等级）
- **applies_to**: 全部 LLM stage
- **related_kr**: KR-P1（stage 产出完整性）, KR3.2（标注覆盖率）
- **related_golden_template_section**: §gap / assumption / confidence 规范
- **source_reference**: artifact-base schema（assumptions/inferred_fields 字段）; S2-H2 golden template
- **severity**: major
- **detection_signal**: artifact 含推断内容但 `inferred_fields` 为空 / `assumptions` 无 risk_if_wrong
- **trigger_condition**: 推断字段未进入 inferred_fields 列表
- **examples_synthetic_only**: 推断"用户主要用移动端"但未标 inferred、未给 confidence
- **remediation**: 所有推断字段加入 inferred_fields；assumption 补 risk_if_wrong
- **delivery_decision**: degrade
- **not_allowed_claims**: 不得把推断当事实陈述
- **traceability_requirement**: 推断字段可追溯到推断依据
- **self_review_question**: 所有推断内容是否已进入 inferred_fields 列表、assumptions 是否带 risk_if_wrong，而非以确定语气陈述？若缺标注是否需 degrade？

---

## FM-PRD2PROTO-007

- **id**: FM-PRD2PROTO-007
- **name**: Stage 链断裂（18 stage 未完整产出即声称交付）
- **applies_to**: pipeline 全链
- **related_kr**: KR-P1（18 stage 全产出率）
- **related_golden_template_section**: §输出目录结构 / artifact 列表
- **source_reference**: pipeline.yaml; S2-H1.1 KR-P1; S1-0B（prd2proto runtime 仅通跑前 5+）
- **severity**: major
- **detection_signal**: 输出目录缺中间 stage artifact；run-report 显示 stage 提前终止
- **trigger_condition**: 18 stage（designer-dsl 17）未全部产出却标完成
- **examples_synthetic_only**: 只产出前 7 个推理资产就生成代码，跳过 state-matrix
- **remediation**: 补齐缺失 stage；无法补的标 gap 并降级声明
- **delivery_decision**: degrade
- **not_allowed_claims**: 不得声称"完整 18-stage 推理链"（除非真跑完）
- **traceability_requirement**: run-report 记录每个 stage 完成状态
- **self_review_question**: 18 stage（designer-dsl 17）是否全部产出对应 artifact，若有跳过/提前终止的 stage 是否已标 gap 并降级"完整推理链"声明？

---

## FM-PRD2PROTO-008

- **id**: FM-PRD2PROTO-008
- **name**: 状态矩阵覆盖不全（边缘/异常状态缺失）
- **applies_to**: state-matrix stage
- **related_kr**: KR-P1; KR1.1（最低交付线）
- **related_golden_template_section**: §必填章节（状态矩阵）
- **source_reference**: product.interaction-state-coverage; frontend.component-state-rules
- **severity**: minor
- **detection_signal**: state_matrix 仅覆盖正常态，缺 loading/empty/error/权限态
- **trigger_condition**: 关键页面/组件状态枚举不全
- **examples_synthetic_only**: 列表页只设计了"有数据"态，缺空态与加载失败态
- **remediation**: 按 7 状态规则补全；缺业务态的标 gap
- **delivery_decision**: warn
- **not_allowed_claims**: 不得声称"状态全覆盖"
- **traceability_requirement**: 每个状态可追溯到 interaction-state-coverage 规则
- **self_review_question**: 关键页面/组件的状态矩阵是否覆盖 loading/empty/error/权限态等边缘态，缺失的是否已标 gap 并 warn？

---

## 汇总

| severity | 数量 | FM id |
|---|---|---|
| blocker | 4 | 001, 002, 003, 004 |
| major | 3 | 005, 006, 007 |
| minor | 1 | 008 |
| **合计** | **8** | |

**一票否决覆盖**：4 个 prd2proto 一票否决项（Schema/Traceability/代码宪法/Honesty）= FM-001~004 全覆盖。
**KR 未达标覆盖**：KR-P1(007/008) · KR-P2(001) · KR-P3(003) · KR-P4(002) · KR3.1(004) · KR3.2(005/006)。
