# ip-design Failure Mode Library (skill-specific)

> Skill: ip-design · Layer: skill-specific failure library · Status: pilot
> 本文件是 S2-H1 rubric / S2-H1.1 OKR / S2-H2 golden template 的**配套失败层**。
> 通用失败模式真源是 `knowledge/design/quality/common-failure-modes.md`
> （`design.quality.common-failure-modes`）与 `knowledge/design-work-paradigm/18-failure-modes.md`，
> 本文件**不复制其全文**，只定义 ip-design 专属、可对账的 failure modes。
> 已有具体 failure case 见 `eval/failure/f-s1-*`、`f-p1-*`、`f-v2-*` 等单独文件。
> 所有示例均为 synthetic / sanitized。注意：ip-design 当前为 prompt-grade（无 runtime）。

## 放置规则一致性（S2-H2.2）

- skill-specific 配套层，引用通用真源 `design.quality.common-failure-modes` 与现有 case 文件，不复制。
- 覆盖：ip-design 4 个一票否决项（D2/D6/D8 + 视觉先行）+ KR-I1~I5 未达标 + 跨阶段一致性失败。

---

## FM-IPDESIGN-001

- **id**: FM-IPDESIGN-001
- **name**: 差异化失守（D2 不合格，差异化靠贬低或与竞品高度重叠）
- **applies_to**: strategy-alignment / brand-brief 输出
- **related_kr**: KR-I1（9 维 rubric 中阶以上）, KR-I2（一票否决=0）, KR1.2
- **related_golden_template_section**: §必填章节（differentiation）/ §一票否决检查
- **source_reference**: ip-design 9 维 rubric D2; common-failure-modes F-S3（差异化靠贬低）; S2-H1 §2 ip-design 一票否决 #1
- **severity**: blocker
- **detection_signal**: differentiation 含贬损语 / 与竞品高度重叠 / 无具体空白点说明
- **trigger_condition**: D2 评分 = 不合格
- **examples_synthetic_only**: "我们比竞品 A 更专业，比竞品 B 更现代"（贬低式）
- **remediation**: 重写差异化基于竞品空白；不做贬损；找不到真正差异化的标 gap
- **delivery_decision**: block
- **not_allowed_claims**: 不得声称 IP 方案"具有差异化定位"当 D2 不合格
- **traceability_requirement**: differentiation 须链接竞品分析证据

---

## FM-IPDESIGN-002

- **id**: FM-IPDESIGN-002
- **name**: 法务/合规风险未标注（D6 不合格）
- **applies_to**: visual-translation / landing-spec 输出
- **related_kr**: KR-I1, KR-I2, KR1.2
- **related_golden_template_section**: §一票否决检查 / §禁止声明
- **source_reference**: ip-design constitution #5（不承诺法务/版权/最终商用资产）; 9 维 rubric D6; S2-H1 §2 ip-design 一票否决 #2
- **severity**: blocker
- **detection_signal**: 核心符号与既有商标形似但 visual_spec 无 [待法务确认] 标注；世界观含敏感映射
- **trigger_condition**: D6 评分 = 不合格 / 风险信号未标
- **examples_synthetic_only**: 核心符号与某知名 IP 视觉高度相似但报告未标
- **remediation**: 标注潜在风险信号 + [待法务确认]；D6 打"中阶可用"档而非"高阶"
- **delivery_decision**: block
- **not_allowed_claims**: 不得声称"已通过商标审查"或"无版权风险"
- **traceability_requirement**: 风险信号链接到具体竞品/商标参考

---

## FM-IPDESIGN-003

- **id**: FM-IPDESIGN-003
- **name**: 人格立体度不足（D8 不合格，仅 MBTI 标签或口头禅）
- **applies_to**: persona-modeling stage
- **related_kr**: KR-I1, KR-I2, KR1.2
- **related_golden_template_section**: §必填章节（persona_profile）
- **source_reference**: 9 维 rubric D8; common-failure-modes F-P1（仅 MBTI 标签）; eval/failure/f-p1-mbti-only.md; S2-H1 §2 ip-design 一票否决 #3
- **severity**: blocker
- **detection_signal**: persona_profile 仅有 MBTI 标签 / 口头禅，缺行为模式 / 动机 / 恐惧/缺陷 / 成长弧 / 关系网
- **trigger_condition**: D8 评分 = 不合格
- **examples_synthetic_only**: persona_profile 仅 `MBTI: ENTJ, 口头禅: "搞起来"`
- **remediation**: 按 persona-modeling 方法论补全五要素（行为/动机/恐惧/成长/关系）
- **delivery_decision**: block
- **not_allowed_claims**: 不得声称"已建立完整 IP 人格"
- **traceability_requirement**: 每个人格要素链接到品牌策略或用户洞察

---

## FM-IPDESIGN-004

- **id**: FM-IPDESIGN-004
- **name**: 视觉先行（先画图后反推策略）
- **applies_to**: 全 pipeline 流程顺序
- **related_kr**: KR-I2, KR1.1（最低交付线）
- **related_golden_template_section**: §禁止声明
- **source_reference**: ip-design constitution #1（品牌策略先于视觉表达）; S2-H1 §2 ip-design 一票否决 #4
- **severity**: blocker
- **detection_signal**: 视觉产出无法追溯到 brand_brief 与 persona；策略与视觉时间戳倒置
- **trigger_condition**: visual_spec 在 brand_brief / persona_profile 之前生成
- **examples_synthetic_only**: 先有 logo 草图，再反向写"我们的品牌人格是…"
- **remediation**: 重走 M01-M03 策略链；视觉决策必须从策略推导
- **delivery_decision**: block
- **not_allowed_claims**: 不得把"先画图"包装为创意流程
- **traceability_requirement**: 视觉决策须可追溯到上游策略 artifact

---

## FM-IPDESIGN-005

- **id**: FM-IPDESIGN-005
- **name**: 视觉禁忌缺失（image_prompt_pack 无负向 prompt）
- **applies_to**: visual-translation / image-prompt-pack stage
- **related_kr**: KR-I3（image_prompt_pack 含负向 prompt 率=100%）, KR1.1
- **related_golden_template_section**: §必填章节（image_prompt_pack）
- **source_reference**: ip-design constitution #6; eval/failure/f-v2-32px-blur.md
- **severity**: major
- **detection_signal**: image_prompt_pack 无 negative_prompt / `--no` / 严格避免清单；visual_spec.strict_avoidance < 5 条
- **trigger_condition**: 提示词包只含正向描述
- **examples_synthetic_only**: prompt 只写"科技感、年轻化、可爱"，无任何避免清单
- **remediation**: 补 ≥ 5 条严格禁忌；同步到提示词 negative 字段
- **delivery_decision**: degrade
- **not_allowed_claims**: 不得声称"提示词包可控"
- **traceability_requirement**: 禁忌清单链接到 visual_spec.strict_avoidance

---

## FM-IPDESIGN-006

- **id**: FM-IPDESIGN-006
- **name**: 跨阶段关键词漂移（M01-M06 一致性断裂）
- **applies_to**: 跨阶段一致性审查
- **related_kr**: KR-I4（professional gap report 完整生成率）, KR3.3
- **related_golden_template_section**: §traceability 规范
- **source_reference**: 9 维 rubric D9（跨阶段证据）; common-failure-modes 跨阶段类
- **severity**: major
- **detection_signal**: M01 北极星关键词在 M04 视觉规范中未体现；M03 人格关键词在 M05 内容规划中漂移
- **trigger_condition**: 关键词链路（北极星 → 人格 → 视觉 → 内容）某一节断
- **examples_synthetic_only**: M01 强调"专业稳重"，M04 出"萌系卡通"风格
- **remediation**: 补关键词传导链；跨阶段不一致的标 gap，专业 gap report 中显式
- **delivery_decision**: gap
- **not_allowed_claims**: 不得在跨阶段不一致时声称"完整 IP 系统"
- **traceability_requirement**: 每阶段产出含 keyword_lineage 链接前一阶段

---

## FM-IPDESIGN-007

- **id**: FM-IPDESIGN-007
- **name**: 推断未显式（[inferred] 标注覆盖率不足）
- **applies_to**: 全部 stage（缺真实用户研究/竞品深度分析时）
- **related_kr**: KR-I5（[inferred] 标注覆盖率 ≥ 90%）, KR3.2
- **related_golden_template_section**: §gap / assumption / confidence 规范
- **source_reference**: ip-design constitution #2（每个判断可追溯）; common-failure-modes F-S2（用户画像臆造）
- **severity**: major
- **detection_signal**: 关键决策（北极星/人格关键词/主形选择/色彩配比）含推断但未标 [inferred] 或未记入 inferences[]
- **trigger_condition**: 推断比例 ≥ 30% 但 inferences[] 列表项 < 真实推断数
- **examples_synthetic_only**: 推断"用户偏好暖色"未标 [inferred]
- **remediation**: 所有推断字段标 [inferred]，记入 inferences[]，给依据
- **delivery_decision**: degrade
- **not_allowed_claims**: 不得把推断当确定结论
- **traceability_requirement**: 每个推断有依据来源（用户研究/竞品/品牌资产/参考案例）

---

## FM-IPDESIGN-008

- **id**: FM-IPDESIGN-008
- **name**: 识别度不达标（D4 低阶，32px 不可辨）
- **applies_to**: visual-translation / image-prompt-pack stage
- **related_kr**: KR-I1, KR1.1
- **related_golden_template_section**: §必填章节（visual_spec 识别度测试）
- **source_reference**: 9 维 rubric D4; eval/failure/f-v2-32px-blur.md
- **severity**: minor
- **detection_signal**: visual_spec 缺 32px 识别度测试 / 缺四级简化 / 远观轮廓与竞品撞车
- **trigger_condition**: D4 评分 = 低阶仅雏形
- **examples_synthetic_only**: 形象细节过多，32px 下成色块
- **remediation**: 补四级简化；远观轮廓差异化测试；不达标的标 gap
- **delivery_decision**: warn
- **not_allowed_claims**: 不得在识别度不达标时声称"可商用"
- **traceability_requirement**: 识别度测试结果记入 visual_spec.recognition_test

---

## 汇总

| severity | 数量 | FM id |
|---|---|---|
| blocker | 4 | 001, 002, 003, 004 |
| major | 3 | 005, 006, 007 |
| minor | 1 | 008 |
| **合计** | **8** | |

**一票否决覆盖**：4 个 ip-design 一票否决项（D2 差异化/D6 法务/D8 人格立体度/视觉先行）= FM-001~004 全覆盖。
**KR 未达标覆盖**：KR-I1(001/002/003/008) · KR-I2(001/002/003/004) · KR-I3(005) · KR-I4(006) · KR-I5(007) · KR3.2(007) · KR3.3(006)。
