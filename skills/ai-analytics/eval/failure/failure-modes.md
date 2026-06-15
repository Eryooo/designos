# ai-analytics Failure Mode Library (skill-specific)

> Skill: ai-analytics · Layer: skill-specific failure library · Status: pilot
> 本文件是 S2-H1 rubric / S2-H1.1 OKR / S2-H2 golden template 的**配套失败层**。
> 通用失败模式真源是 `knowledge/design-work-paradigm/18-failure-modes.md`，本文件
> **不复制其全文**，只定义 ai-analytics 专属失败模式。所有示例均为 synthetic / sanitized。
> 注意：ai-analytics 当前为 prompt-grade（无 runtime/quality_gates）。

## 放置规则一致性（S2-H2.2）

- skill-specific 配套层，引用通用真源而非复制。
- 覆盖：ai-analytics 4 个一票否决项 + KR-A1~A5 未达标 + 数据真实性/coverage/越界 失败 + golden template 低阶信号。

---

## FM-AIANALYTICS-001

- **id**: FM-AIANALYTICS-001
- **name**: 编造数据（结论无证据来源）
- **applies_to**: data-collection / strategy-synthesis / report-generation stage
- **related_kr**: KR-A1（编造数据=0）, KR1.2（一票否决命中数）
- **related_golden_template_section**: §字段级要求 / §traceability 规范
- **source_reference**: ai-analytics constitution 规则 1（不得编造数据）; S2-H1 §2 ai-analytics 一票否决 #1
- **severity**: blocker
- **detection_signal**: 任一 finding/comparison 条目无 evidence_refs，或 evidence_refs 指向不存在的 collected_data 条目
- **trigger_condition**: 资料缺失但产出具体数据/价格/份额
- **examples_synthetic_only**: 竞品资料未提价格，却写"竞品 A 定价 ¥99/月"
- **remediation**: 删除该结论或显式标 [inferred] 并说明依据；缺数据写入 gaps
- **delivery_decision**: block
- **not_allowed_claims**: 不得把推断包装为已验证事实
- **traceability_requirement**: 每条结论可追溯到 collected_data 具体条目
- **self_review_question**: 每条 finding/数据是否有 evidence_refs 指向真实存在的 collected_data 条目，无来源的具体数据是否已删除或标 [inferred] 并阻断交付？

---

## FM-AIANALYTICS-002

- **id**: FM-AIANALYTICS-002
- **name**: 下游必需字段缺失（design_strategy/user_persona schema 不合规）
- **applies_to**: strategy-synthesis stage
- **related_kr**: KR-A2（schema 必填字段非空率）
- **related_golden_template_section**: §字段级要求（schema 强约束）
- **source_reference**: ai-analytics constitution 规则 2; design-strategy.schema.json; user-persona.schema.json
- **severity**: blocker
- **detection_signal**: design_strategy.target_audience / business_goal 为空；user_persona[].role / goals / pain_points 为空
- **trigger_condition**: prd2proto 注入需要的核心字段缺失
- **examples_synthetic_only**: design_strategy 仅有"科技感、年轻化"形容词，无 target_audience
- **remediation**: 按 schema 补齐必填字段；无足够数据的标 inferred + gap
- **delivery_decision**: block
- **not_allowed_claims**: 不得在 schema 不合规时声称"上游产出已交付"
- **traceability_requirement**: 必填字段值可追溯到 collected_data 或 inferred 依据
- **self_review_question**: design_strategy.target_audience/business_goal 与 user_persona 的 role/goals/pain_points 是否全部非空且符合 schema，缺失是否已阻断交付（下游注入会失效）？

---

## FM-AIANALYTICS-003

- **id**: FM-AIANALYTICS-003
- **name**: Coverage 虚高（数据完整度评估不诚实）
- **applies_to**: strategy-synthesis stage 的 data_completeness_assessment
- **related_kr**: KR-A3（coverage 评估准确性）
- **related_golden_template_section**: §字段级要求（data_completeness_assessment）
- **source_reference**: ai-analytics constitution 规则 3; research.data-completeness-rubric
- **severity**: blocker
- **detection_signal**: coverage ≥ 0.70 但 collected_data 仅 1-2 个来源 / 大量维度 TBD；coverage 与实际资料不匹配
- **trigger_condition**: 为了过 QG1 gate 把 coverage 标高
- **examples_synthetic_only**: 只采集了 1 个竞品资料就标 coverage=0.85
- **remediation**: 按 data-completeness-rubric 重评 coverage；< 0.70 触发 QG1 硬停
- **delivery_decision**: block
- **not_allowed_claims**: 不得把虚高 coverage 当通过判据
- **traceability_requirement**: coverage 计算过程可审计
- **self_review_question**: data_completeness_assessment.coverage 是否真实反映已采集资料量，coverage<0.70 是否已触发 QG1 硬停而非被虚标过线？

---

## FM-AIANALYTICS-004

- **id**: FM-AIANALYTICS-004
- **name**: 越界产出下游职责（产出代码/问题清单）
- **applies_to**: 全部 stage 输出
- **related_kr**: KR-A4（越界产出=0）, KR1.2
- **related_golden_template_section**: §禁止声明 / §字段级要求（输出范围）
- **source_reference**: ai-analytics constitution 规则 4; SKILL.md（analysis 型 skill 边界）
- **severity**: blocker
- **detection_signal**: 输出含代码片段 / 原型 / 问题清单+严重度
- **trigger_condition**: ai-analytics 越界做 prd2proto / uxeval 的事
- **examples_synthetic_only**: 在 design_strategy 里写出"建议代码这样实现…"
- **remediation**: 删除越界内容，转为 design_strategy 的约束建议供下游消费
- **delivery_decision**: block
- **not_allowed_claims**: 不得声称 ai-analytics 可产出代码或评估结论
- **traceability_requirement**: 输出类型须与 SKILL.md outputs 声明一致
- **self_review_question**: 输出是否仅含分析与上游策略，未越界产出代码/原型/问题清单+严重度（下游 prd2proto/uxeval 职责）？若越界是否已阻断？

---

## FM-AIANALYTICS-005

- **id**: FM-AIANALYTICS-005
- **name**: 推断未标 [inferred]（assumption 无依据说明）
- **applies_to**: 全部 LLM stage
- **related_kr**: KR-A5（[inferred] 标注覆盖率）, KR3.2（标注覆盖率）
- **related_golden_template_section**: §gap / assumption / confidence 规范
- **source_reference**: ai-analytics constitution 规则 1（minor 等级）
- **severity**: major
- **detection_signal**: 含推断内容但未在文中标 [inferred] 或说明依据
- **trigger_condition**: 把推断写成确定陈述
- **examples_synthetic_only**: 写"用户主要关注价格"但未标 inferred 与依据
- **remediation**: 推断字段加 [inferred] 标注 + 依据描述
- **delivery_decision**: degrade
- **not_allowed_claims**: 不得把推断当事实
- **traceability_requirement**: 推断可追溯到推断依据（行业数据/类比/用户访谈）
- **self_review_question**: 所有推断内容是否已标 [inferred] 并附依据，把推断写成确定陈述的是否需 degrade？

---

## FM-AIANALYTICS-006

- **id**: FM-AIANALYTICS-006
- **name**: 用户画像质量不达标（goals/pain_points 空泛或脱离场景）
- **applies_to**: strategy-synthesis stage 的 user_persona
- **related_kr**: KR-A2; KR1.1（最低交付线）
- **related_golden_template_section**: §必填章节（user_persona）
- **source_reference**: research.user-persona-quality
- **severity**: major
- **detection_signal**: user_persona 的 goals/pain_points 为单句口号、无具体场景、无证据来源
- **trigger_condition**: 画像写成"想要好用的产品"等通用陈述
- **examples_synthetic_only**: pain_points = ["效率低", "体验差"] 无具体场景
- **remediation**: 按 user-persona-quality rubric 补充场景化描述与证据
- **delivery_decision**: degrade
- **not_allowed_claims**: 不得把空泛画像当用户研究产物
- **traceability_requirement**: 每条 pain_point 可追溯到 collected_data
- **self_review_question**: user_persona 的 goals/pain_points 是否场景化且有证据来源，仅有"效率低/体验差"类口号的是否需 degrade 并补充？

---

## FM-AIANALYTICS-007

- **id**: FM-AIANALYTICS-007
- **name**: 竞品矩阵过浅（comparison_matrix 维度不足）
- **applies_to**: competitor-analysis stage
- **related_kr**: KR-A1; KR1.1
- **related_golden_template_section**: §必填章节（comparison_matrix）
- **source_reference**: research.competitor-analysis
- **severity**: major
- **detection_signal**: comparison_matrix 仅含名称/定位，缺关键维度（定价/功能/视觉/传播）
- **trigger_condition**: 竞品分析维度 < 4 或大量单元格 TBD
- **examples_synthetic_only**: 矩阵只有 [竞品名, 简介] 两列
- **remediation**: 按 competitor-analysis 方法论补维度；缺数据的维度标 gap
- **delivery_decision**: degrade
- **not_allowed_claims**: 不得把单维度对比当深度竞品分析
- **traceability_requirement**: 每个 cell 可追溯到 collected_data
- **self_review_question**: comparison_matrix 是否覆盖 ≥4 个关键维度（定价/功能/视觉/传播），维度过少或大量 TBD 是否需 degrade 并标 gap？

---

## FM-AIANALYTICS-008

- **id**: FM-AIANALYTICS-008
- **name**: Methodology 滥选（选了不被数据支撑的方法）
- **applies_to**: methodology-selection stage
- **related_kr**: KR-A3; KR1.1
- **related_golden_template_section**: §必填章节（methodology）
- **source_reference**: research.methodology-selection
- **severity**: minor
- **detection_signal**: 选了 KANO/JTBD 但缺对应输入数据
- **trigger_condition**: methodology 选择不基于数据可得性
- **examples_synthetic_only**: 标榜用 KANO 模型但没有用户分级问卷数据
- **remediation**: 改选 SWOT 等数据要求较低的方法；或采集相应数据后再用
- **delivery_decision**: warn
- **not_allowed_claims**: 不得使用数据不足以支撑的方法论结论
- **traceability_requirement**: methodology 选择有 why+applies_to 记录
- **self_review_question**: 所选 methodology（如 KANO/JTBD）是否有对应输入数据支撑，数据不足以支撑的是否已 warn 并改选低数据要求方法？

---

## 汇总

| severity | 数量 | FM id |
|---|---|---|
| blocker | 4 | 001, 002, 003, 004 |
| major | 3 | 005, 006, 007 |
| minor | 1 | 008 |
| **合计** | **8** | |

**一票否决覆盖**：4 个 ai-analytics 一票否决项（编造数据/必填字段缺失/Coverage虚高/越界）= FM-001~004 全覆盖。
**KR 未达标覆盖**：KR-A1(001/007) · KR-A2(002/006) · KR-A3(003/008) · KR-A4(004) · KR-A5(005) · KR3.2(005)。
