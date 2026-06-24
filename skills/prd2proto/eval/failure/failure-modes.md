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
- **detection_signal**: 文档/输出含全自动无人值守/生产就绪/已达资深水准等过度声明；mock 路径标"已跑通"
- **trigger_condition**: 任一产出声明超出 prompt-grade / pilot 真实能力
- **examples_synthetic_only**: README 写"prd2proto 全自动生成可上线原型"
- **remediation**: 改为诚实边界表述（pilot / 需人工复核 / prompt-grade）
- **delivery_decision**: block
- **not_allowed_claims**: 见 detection_signal 全部禁词
- **traceability_requirement**: 能力声明须与 status.matrix maturity 一致
- **self_review_question**: 当前文档/输出是否命中任一 not_allowed_claims（全自动无人值守/生产就绪/已达资深等过度声明），若命中是否已改为诚实边界表述并阻断发布？

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
| blocker | 7 | 001, 002, 003, 004, 009, 011, 015 |
| major | 6 | 005, 006, 007, 010, 013, 016 |
| minor | 3 | 008, 012, 014 |
| **合计** | **16** | |

**一票否决覆盖**：4 个原有 prd2proto 一票否决项（Schema/Traceability/代码宪法/Honesty）= FM-001~004。
**S2-H11 资深设计执行一票否决**：PRD直转页面(009)、缺Problem Framing(011)、Verdict Inflation(015)。
**KR 未达标覆盖**：KR-P1(007/008) · KR-P2(001) · KR-P3(003) · KR-P4(002) · KR3.1(004) · KR3.2(005/006)。

---

## FM-PRD2PROTO-009

- **id**: FM-PRD2PROTO-009
- **name**: PRD直转页面（跳过问题定义与设计推导）
- **applies_to**: design-objectives, product-archetype, information-architecture, page-structure
- **related_kr**: KR-P1; S2-H11-0 Domain 1/3/5/7
- **related_golden_template_section**: §必填章节（problem_statement, goal_tree, product_foundation_map, ia_rationale）
- **source_reference**: knowledge/product/senior-design-execution.md Domain 1/3/5/7; skills/prd2proto/reference/senior-design-execution-adaptation.md §2.2
- **severity**: blocker
- **detection_signal**: design_objectives缺problem_statement; product_archetype缺foundation/core_module区分; information_architecture无rationale直接输出flat功能页面清单
- **trigger_condition**: 任一中间推理资产(problem/goal/product model/IA rationale)缺失或直接从PRD功能清单生成页面
- **examples_synthetic_only**: PRD含10个功能点,直接生成10个flat sidebar页面,无IA rationale/product foundation/goal tree
- **remediation**: 补problem framing/goal decomposition/product model/IA rationale; 若PRD不支持则标gap并降级
- **delivery_decision**: block
- **not_allowed_claims**: 不得声称"资深产品设计推导""完整设计推理链"
- **traceability_requirement**: IA → product model → goal → problem 可追溯
- **self_review_question**: 是否从PRD直接生成页面,跳过problem framing/goal decomposition/product model/IA rationale? 若跳过则block。

---

## FM-PRD2PROTO-010

- **id**: FM-PRD2PROTO-010
- **name**: Example Flow Dominance（详细示例流程主导整个产品架构）
- **applies_to**: product-archetype, information-architecture, page-flow
- **related_kr**: KR-P1; S2-H11-0 Domain 5/7
- **related_golden_template_section**: §product_foundation_map, §information_architecture.experience_surfaces
- **source_reference**: knowledge/product/senior-design-execution.md Domain 5; skills/prd2proto/reference/senior-design-execution-adaptation.md §2.2 Trigger 1
- **severity**: major
- **detection_signal**: PRD含1个详细example + N个产品基础能力,但IA/导航/首页围绕example设计,基础能力被边缘化或缺失
- **trigger_condition**: representative_scenario因描述详细而被错误提升为product_foundation或main navigation
- **examples_synthetic_only**: 企业AI助理PRD含"费用申请详细流程"示例,系统把费用申请作为主导航和首页,压过对话/技能/记忆等产品基础能力
- **remediation**: 区分product_foundation/core_module/representative_scenario; example用于验证能力,不主导架构; 标注example_dominance_risk
- **delivery_decision**: degrade
- **not_allowed_claims**: 不得声称"完整产品架构""主导航准确"
- **traceability_requirement**: IA → product_foundation_map, representative_scenario标注为proof-of-flow
- **self_review_question**: 是否因某个流程描述详细就让它主导IA/导航/首页? 产品基础能力是否被example压倒? 若是则degrade并标example_dominance_risk。

---

## FM-PRD2PROTO-011

- **id**: FM-PRD2PROTO-011
- **name**: Missing Problem Framing（缺业务问题/用户问题定义）
- **applies_to**: input-diagnosis, design-objectives
- **related_kr**: KR-P1; S2-H11-0 Domain 1
- **related_golden_template_section**: §design_objectives.problem_statement
- **source_reference**: knowledge/product/senior-design-execution.md Domain 1; skills/prd2proto/reference/senior-design-execution-adaptation.md §1 Domain 1
- **severity**: blocker
- **detection_signal**: design_objectives缺problem_statement或只有功能清单无问题定义
- **trigger_condition**: PRD缺业务问题/用户问题/成功指标,且未标注inferred_problem并降低confidence
- **examples_synthetic_only**: PRD直接列功能清单,无"要解决什么业务问题""用户痛点是什么""成功指标是什么",输出也无problem_statement
- **remediation**: 补problem_statement(业务问题/用户问题/成功指标); PRD不支持时标inferred+assumption+low confidence
- **delivery_decision**: block(若完全缺失); degrade(若inferred但未标注)
- **not_allowed_claims**: 不得声称"基于明确问题定义的设计"
- **traceability_requirement**: goal_tree → problem_statement 可追溯
- **self_review_question**: design_objectives是否含problem_statement(业务问题/用户问题/成功指标)? PRD缺失时是否标inferred+assumption? 若无则block。

---

## FM-PRD2PROTO-012

- **id**: FM-PRD2PROTO-012
- **name**: Missing Product/Domain Model（缺产品对象模型与模块边界）
- **applies_to**: product-archetype, information-architecture
- **related_kr**: KR-P1; S2-H11-0 Domain 5
- **related_golden_template_section**: §product_archetype.product_foundation_map, §product_archetype.domain_objects
- **source_reference**: knowledge/product/senior-design-execution.md Domain 5; skills/prd2proto/reference/senior-design-execution-adaptation.md §1 Domain 5
- **severity**: minor
- **detection_signal**: product_archetype缺product_foundation/core_module/domain_objects,或IA无法追溯到product model
- **trigger_condition**: PRD缺业务对象/权限/状态描述,product_archetype未建模或IA直接从功能清单生成
- **examples_synthetic_only**: CRM PRD缺"客户/线索/商机对象关系",product_archetype未建模,IA直接平铺功能页面
- **remediation**: 补product_foundation_map/domain_objects/module_boundaries; PRD不支持时标inferred并在IA中标ia_inferred_from_features
- **delivery_decision**: warn(可推断); degrade(若IA unsupported)
- **not_allowed_claims**: 不得声称"基于产品模型的IA"
- **traceability_requirement**: IA → product model → domain objects 可追溯
- **self_review_question**: product_archetype是否含product_foundation_map/domain_objects? IA是否可追溯到product model? 若无则warn并标inferred。

---

## FM-PRD2PROTO-013

- **id**: FM-PRD2PROTO-013
- **name**: IA Unsupported By Evidence（IA无rationale或flat功能映射）
- **applies_to**: information-architecture, page-flow
- **related_kr**: KR-P1; S2-H11-0 Domain 7
- **related_golden_template_section**: §information_architecture.ia_rationale, §information_architecture.experience_surfaces
- **source_reference**: knowledge/product/senior-design-execution.md Domain 7; skills/prd2proto/reference/senior-design-execution-adaptation.md §1 Domain 7
- **severity**: major
- **detection_signal**: information_architecture缺ia_rationale; 功能域1:1映射为页面; 单层sidebar覆盖所有功能; 缺experience_surfaces/shell/context/history区分
- **trigger_condition**: IA直接从PRD功能清单生成,无product model/task priority/user journey支撑
- **examples_synthetic_only**: 多体验表面产品(宿主平台+产品导航+历史上下文+工作区)被压平成单层sidebar
- **remediation**: 补ia_rationale(为何这样组织?); 识别experience_surfaces/shell/context; 区分product foundation/management/scenarios; 标ia_inferred_from_features
- **delivery_decision**: degrade
- **not_allowed_claims**: 不得声称"资深IA决策""经过架构推导"
- **traceability_requirement**: IA → product model → user tasks → journey
- **self_review_question**: IA是否有rationale? 是否识别experience_surfaces? 是否flat功能1:1页面? 若flat则degrade并标ia_inferred_from_features。

---

## FM-PRD2PROTO-014

- **id**: FM-PRD2PROTO-014
- **name**: State Coverage Illusion（状态覆盖不全却宣称完整）
- **applies_to**: state-matrix, page-structure, interaction-rules
- **related_kr**: KR-P1; S2-H11-0 Domain 6/8
- **related_golden_template_section**: §state_matrix.states, §page_structure.state_coverage
- **source_reference**: knowledge/product/senior-design-execution.md Domain 6/8; skills/prd2proto/reference/senior-design-execution-adaptation.md §1 Domain 6/8
- **severity**: minor
- **detection_signal**: state_matrix只有happy path; page_structure缺loading/empty/error/permission描述
- **trigger_condition**: PRD缺异常流程/权限流程/中断状态,state_matrix未标gap却宣称"状态完整"
- **examples_synthetic_only**: 列表页只设计"有数据"态,缺空态/加载失败/无权限态,未标gap
- **remediation**: 补loading/empty/error/permission/retry/interruption; PRD不支持时标state_coverage_gaps
- **delivery_decision**: warn
- **not_allowed_claims**: 不得声称"状态全覆盖""交互完整"
- **traceability_requirement**: state_matrix → business_flow → user_journey
- **self_review_question**: state_matrix是否覆盖loading/empty/error/permission等边缘态? 缺失的是否标gap? 若只有happy path则warn并标state_coverage_gaps。

---

## FM-PRD2PROTO-015

- **id**: FM-PRD2PROTO-015
- **name**: Clickable Prototype Verdict Inflation（可点击≠资深可评审）
- **applies_to**: professional-gap-assessment, self-review-gate
- **related_kr**: KR-P1; S2-H11-0 Domain 10
- **related_golden_template_section**: §self_review_gate.delivery_decision, §professional_gap_report.verdict
- **source_reference**: knowledge/product/senior-design-execution.md Domain 10; skills/prd2proto/reference/senior-design-execution-adaptation.md §3 Absolute Rules
- **severity**: blocker
- **detection_signal**: liveness/smoke pass被当作design quality证明; coverage<80%或critical gaps>0时判定review-ready; 缺visual evidence时判定visual_review_ready
- **trigger_condition**: verdict与evidence/coverage/gap不匹配,过度声明prototype质量
- **examples_synthetic_only**: PRD-only输入,prototype可点击且smoke pass,但缺IA rationale/状态覆盖/visual evidence,判定为"senior_review_ready"
- **remediation**: 校准verdict: liveness≠quality; clickable≠senior-reviewable; 按coverage/gap/visual evidence判定; 降级为partial_clickable_prototype或clickable_prototype_ready_with_gaps
- **delivery_decision**: block
- **not_allowed_claims**: 不得声称"资深可评审""visual review ready""production candidate"(除非evidence支持)
- **traceability_requirement**: verdict → coverage → gap → evidence 可追溯
- **self_review_question**: verdict是否与coverage/gap/visual evidence匹配? liveness pass是否被当作design quality? coverage<80%或critical gaps>0时是否仍判review-ready? 若是则block并降级verdict。

---

## FM-PRD2PROTO-016

- **id**: FM-PRD2PROTO-016
- **name**: Visual Polish Overclaim（无视觉证据却宣称视觉可评审）
- **applies_to**: design-spec-generation, token-extraction, professional-gap-assessment
- **related_kr**: KR-P1; S2-H11-0 Domain 9
- **related_golden_template_section**: §design_spec.visual_source_status, §design_tokens.extraction_method
- **source_reference**: knowledge/product/senior-design-execution.md Domain 9; skills/prd2proto/reference/senior-design-execution-adaptation.md §1 Domain 9
- **severity**: major
- **detection_signal**: 无screenshots/design system/brand tokens/reference UI,但design_spec声称"视觉已确立"或token_extraction输出"品牌token"; component library default被当成visual direction
- **trigger_condition**: visual_source_status=none,但visual_fidelity_mode≠structural_only或verdict=visual_review_ready
- **examples_synthetic_only**: PRD-only输入,选择Ant Design默认主题,输出token并声称"已提取品牌设计语言"
- **remediation**: 标visual_source_status=none, visual_fidelity_mode=structural_only; component library标为implementation_constraint而非visual direction; 降级verdict; 请求screenshots/design system/tokens
- **delivery_decision**: degrade
- **not_allowed_claims**: 不得声称"视觉可评审""品牌语言已确立""design tokens extracted"(除非有visual source)
- **traceability_requirement**: design_tokens → visual_source(screenshots/design system/brand assets)
- **self_review_question**: 是否有visual source(screenshots/design system/tokens/brand assets)? 若无,visual_fidelity_mode是否为structural_only? component library是否被误认为visual direction? 若overclaim则degrade。
