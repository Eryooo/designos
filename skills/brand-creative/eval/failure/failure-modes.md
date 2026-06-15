# brand-creative Failure Mode Library (skill-specific)

> Skill: brand-creative · Layer: skill-specific failure library · Status: alpha
> 本文件是 S2-H1 rubric / S2-H1.1 OKR / S2-H2 golden template 的**配套失败层**。
> 通用失败模式真源是 `knowledge/design/quality/brand-creative-failure-modes.md`
> （`design.quality.brand-creative-failure-modes`）与 `knowledge/design-work-paradigm/18-failure-modes.md`，
> 本文件**不复制其全文**，只定义 brand-creative skill group 专属失败模式。
> 所有示例均为 synthetic / sanitized。注意：brand-creative 当前为 alpha
> （13 sub-skill 中仅 6 有 pipeline，主线未成型）。

## 放置规则一致性（S2-H2.2）

- skill-specific 配套层，引用通用真源 `design.quality.brand-creative-failure-modes` 不复制。
- 覆盖：brand-creative 3 个一票否决项 + KR-B1~B5 未达标 + 跨 sub-skill 一致性失败 + golden template 低阶信号。

---

## FM-BRANDCREATIVE-001

- **id**: FM-BRANDCREATIVE-001
- **name**: 策略空心化（品牌策略全是形容词，无可消费定位）
- **applies_to**: brand-strategy sub-skill 输出
- **related_kr**: KR-B2（rubric 中阶以上）, KR-B3（一票否决=0）, KR1.2
- **related_golden_template_section**: §必填章节（brand_brief）/ §一票否决检查
- **source_reference**: design.quality.brand-identity-quality-rubric; brand-creative-failure-modes F-BS1; S2-H1 §2 brand-creative 一票否决 #1
- **severity**: blocker
- **detection_signal**: brand_brief 仅含"年轻化、科技感、信任、专业"等形容词，无差异化定位、无目标人群细分、无品牌承诺
- **trigger_condition**: 策略输出无下游可消费的具体字段
- **examples_synthetic_only**: brand_brief: `tone: "现代、专业"`（仅形容词）
- **remediation**: 按 brand-strategy 方法论补差异化定位 + 目标人群 + 品牌承诺；空心策略不放行
- **delivery_decision**: block
- **not_allowed_claims**: 不得把形容词堆砌当品牌策略
- **traceability_requirement**: 策略字段链接到 competitive-analysis 与用户洞察

---

## FM-BRANDCREATIVE-002

- **id**: FM-BRANDCREATIVE-002
- **name**: 法务/商标风险（核心 logo/名称冲突未标注）
- **applies_to**: logo-design / visual-identity sub-skill
- **related_kr**: KR-B3, KR1.2
- **related_golden_template_section**: §一票否决检查 / §禁止声明
- **source_reference**: design.quality.brand-identity-quality-rubric; brand-creative-failure-modes（法务类）; S2-H1 §2 brand-creative 一票否决 #2
- **severity**: blocker
- **detection_signal**: logo 与既有品牌视觉高度相似 / 名称音形义与已注册商标重叠 / 缺 [待法务确认] 标注
- **trigger_condition**: 视觉/名称风险信号未在产出中显式
- **examples_synthetic_only**: logo 与某知名品牌主形高度相似但报告未提
- **remediation**: 标注潜在风险信号 + [待法务确认]；高风险方案重新发想
- **delivery_decision**: block
- **not_allowed_claims**: 不得声称"已通过商标审查"或"无法务风险"
- **traceability_requirement**: 风险信号链接到具体竞品/已注册商标参考

---

## FM-BRANDCREATIVE-003

- **id**: FM-BRANDCREATIVE-003
- **name**: 跨 sub-skill 不一致（策略/视觉/内容关键词链路断裂）
- **applies_to**: 跨 sub-skill 一致性审查
- **related_kr**: KR-B4（跨 sub-skill 关键词链路一致 ≥ 70%）, KR1.2
- **related_golden_template_section**: §一票否决检查 / §traceability 规范
- **source_reference**: design.quality.brand-creative-failure-modes（跨子技能断链类）; S2-H1 §2 brand-creative 一票否决 #3
- **severity**: blocker
- **detection_signal**: brand-strategy 关键词在 logo-design / brand-voice 中未体现；color-system 与 typography 调性矛盾
- **trigger_condition**: 关键词跨 sub-skill 漂移 ≥ 30%
- **examples_synthetic_only**: brand-strategy 强调"高端简约"，logo-design 出大量装饰性元素
- **remediation**: 跨 sub-skill 一致性审查；漂移点回 brand-strategy 重新对齐
- **delivery_decision**: block
- **not_allowed_claims**: 不得在跨 sub-skill 不一致时声称"完整品牌系统"
- **traceability_requirement**: 每个 sub-skill 产出含 keyword_lineage 引用 brand-strategy

---

## FM-BRANDCREATIVE-004

- **id**: FM-BRANDCREATIVE-004
- **name**: Sub-skill pipeline 覆盖不足（KR-B1 最低线 50% 未达）
- **applies_to**: skill group 主线建设
- **related_kr**: KR-B1（sub-skill 有 pipeline 比例 ≥ 50%）, KR1.1
- **related_golden_template_section**: §当前主线状态
- **source_reference**: GROUP.md sub_skills 列表; status.matrix maturity=alpha
- **severity**: major
- **detection_signal**: `skills/brand-creative/sub-skills/*/pipeline.yaml` 存在比例 < 50%（当前 6/13 = 46%）
- **trigger_condition**: 13 sub-skill 中有 pipeline 的 < 7 个
- **examples_synthetic_only**: brand-voice / content-strategy 等 7 个 sub-skill 仅有 README 无 pipeline
- **remediation**: 优先补关键 sub-skill 的 pipeline；alpha 阶段不冒充更高 maturity
- **delivery_decision**: degrade
- **not_allowed_claims**: 不得声称"brand-creative 全链路可用"或"13 sub-skill 全部 pipeline-ready"
- **traceability_requirement**: status.matrix 与实际 pipeline 数一致

---

## FM-BRANDCREATIVE-005

- **id**: FM-BRANDCREATIVE-005
- **name**: 竞品分析过浅（competitive-analysis 维度不足以支撑差异化）
- **applies_to**: competitive-analysis sub-skill
- **related_kr**: KR-B2, KR1.1
- **related_golden_template_section**: §必填章节（competitive_matrix）
- **source_reference**: brand-creative-failure-modes F-CA1（竞品矩阵过浅）
- **severity**: major
- **detection_signal**: competitor_matrix 仅有 [name, summary]，缺 visual_style / tone / positioning / pricing
- **trigger_condition**: 维度 < 4 或大量 cell 为 TBD
- **examples_synthetic_only**: 竞品仅写名字，无视觉风格/传播口径维度
- **remediation**: 按 competitive-analysis 方法论补维度；缺数据的标 gap
- **delivery_decision**: degrade
- **not_allowed_claims**: 不得用浅竞品分析支撑"差异化已验证"
- **traceability_requirement**: differentiation 必须链接 ≥ 4 维 competitive_matrix

---

## FM-BRANDCREATIVE-006

- **id**: FM-BRANDCREATIVE-006
- **name**: 推断未标 [inferred]（assumption 无依据）
- **applies_to**: 全部 sub-skill 输出
- **related_kr**: KR3.2（标注覆盖率）
- **related_golden_template_section**: §gap / assumption / confidence 规范
- **source_reference**: brand-creative-failure-modes F-BS2（伪装竞品对标）; design-work-paradigm/18-failure-modes
- **severity**: major
- **detection_signal**: 含推断但未标 [inferred] / `differentiation.basis=competitor_matrix` 但无矩阵输入
- **trigger_condition**: 推断字段 ≥ 30% 但 inferences[] 列表项 < 真实推断数
- **examples_synthetic_only**: 写"竞品 A 主打高端"但 collected_data 无该结论
- **remediation**: 推断字段标 [inferred] + basis 改 inferred 并声明未验证
- **delivery_decision**: degrade
- **not_allowed_claims**: 不得把推断当已验证结论
- **traceability_requirement**: 推断可追溯到推断依据

---

## FM-BRANDCREATIVE-007

- **id**: FM-BRANDCREATIVE-007
- **name**: VI 完整性不足（visual-identity 缺关键模块）
- **applies_to**: visual-identity sub-skill
- **related_kr**: KR-B2, KR1.1
- **related_golden_template_section**: §必填章节（vi_manual）
- **source_reference**: brand-creative-failure-modes（VI 类）; design.visual.visual-identity-integration-methodology
- **severity**: major
- **detection_signal**: vi_manual 缺 logo 使用规范 / 颜色应用 / 字体层级 / 辅助图形 / 场景应用
- **trigger_condition**: VI 模块完整度 < 80%
- **examples_synthetic_only**: 仅有 logo，无颜色与字体规范
- **remediation**: 按 vi 方法论补全模块；缺失的标 gap
- **delivery_decision**: degrade
- **not_allowed_claims**: 不得把不完整 VI 当"品牌识别系统"
- **traceability_requirement**: vi_manual 各模块链接到上游 sub-skill 产出

---

## FM-BRANDCREATIVE-008

- **id**: FM-BRANDCREATIVE-008
- **name**: failure-modes 自检命中（KR-B5 严重级触发）
- **applies_to**: 全 sub-skill 自检
- **related_kr**: KR-B5（failure-modes 自检命中=0）
- **related_golden_template_section**: §一票否决检查 / §gap 规范
- **source_reference**: design.quality.brand-creative-failure-modes; KR-B5
- **severity**: minor
- **detection_signal**: brand-creative-failure-modes 自检中触发严重级 FM 但无标注
- **trigger_condition**: 严重级 FM 自检命中 ≥ 1 但未记入 gaps
- **examples_synthetic_only**: F-CA1 命中但 brand_brief 未标 gap
- **remediation**: 自检命中的 FM 全部记入 gaps；严重级触发时考虑降级 maturity 声明
- **delivery_decision**: warn
- **not_allowed_claims**: 不得在 FM 自检命中时声称"无失败模式"
- **traceability_requirement**: 自检结果可审计

---

## 汇总

| severity | 数量 | FM id |
|---|---|---|
| blocker | 3 | 001, 002, 003 |
| major | 4 | 004, 005, 006, 007 |
| minor | 1 | 008 |
| **合计** | **8** | |

**一票否决覆盖**：3 个 brand-creative 一票否决项（策略空心化/法务/跨子skill不一致）= FM-001~003 全覆盖。
**KR 未达标覆盖**：KR-B1(004) · KR-B2(001/005/007) · KR-B3(001/002/003) · KR-B4(003) · KR-B5(008) · KR3.2(006)。
