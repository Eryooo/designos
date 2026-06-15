# uxeval Failure Mode Library (skill-specific)

> Skill: uxeval · Layer: skill-specific failure library · Status: pilot (beta maturity)
> 本文件是 S2-H1 rubric / S2-H1.1 OKR / S2-H2 golden template 的**配套失败层**。
> 通用失败模式真源是 `knowledge/ux/ux-failure-modes.md` 与
> `knowledge/design-work-paradigm/18-failure-modes.md`，本文件**不复制其全文**，
> 只定义 uxeval 专属失败模式。所有示例均为 synthetic / sanitized。
> 注意：uxeval 当前为 prompt-grade（无 runtime），pipeline 中 `gate:` 是**暂停门
> (checkpoint)**，不是 kernel quality_gates，本文件不混称。

## 放置规则一致性（S2-H2.2）

- skill-specific 配套层，引用通用真源而非复制。
- 覆盖：uxeval 4 个一票否决项 + KR-U1~U5 未达标 + evidence/severity/建议 失败 + golden template 低阶信号。

---

## FM-UXEVAL-001

- **id**: FM-UXEVAL-001
- **name**: Issue 无证据（evidence_refs 为空）
- **applies_to**: issue-attribution stage 全部 issue
- **related_kr**: KR-U1（evidence_refs 非空率）, KR1.2（一票否决命中数）
- **related_golden_template_section**: §必填章节（问题清单）/ §字段级要求
- **source_reference**: uxeval constitution #1; S2-H1 §2 uxeval 一票否决 #1
- **severity**: blocker
- **detection_signal**: 任一 issue 的 `evidence_refs` 数组为空
- **trigger_condition**: 输出 issue 但无截图/DOM/trace 证据绑定
- **examples_synthetic_only**: "登录页加载慢"无任何 screenshot 证据引用
- **remediation**: 每条 issue 至少绑定 1 条 evidence；无证据的移到 unverified_issues 附录
- **delivery_decision**: block
- **not_allowed_claims**: 不得把无证据主观判断当作正式 issue
- **traceability_requirement**: evidence path 必须实际存在于 evidence/ 目录

---

## FM-UXEVAL-002

- **id**: FM-UXEVAL-002
- **name**: 敏感信息泄露（真实账号/PII/内部 URL 进入报告）
- **applies_to**: 全部 stage 输出 + 截图证据
- **related_kr**: KR-U4（敏感信息泄露=0）, KR3.1（不可宣称项）
- **related_golden_template_section**: §禁止声明 / §traceability 规范
- **source_reference**: uxeval constitution #2; 全局底座 F-Honesty
- **severity**: blocker
- **detection_signal**: scan-sensitive 命中；报告含真实账号/手机号/身份证/完整内部 URL
- **trigger_condition**: 截图或文本含未打码敏感信息
- **examples_synthetic_only**: 报告截图含真实测试账号 `user@realcorp.internal`（应打码）
- **remediation**: 打码或脱敏；evidence 路径不含真实用户名
- **delivery_decision**: block
- **not_allowed_claims**: —
- **traceability_requirement**: 敏感信息打码记录可审计

---

## FM-UXEVAL-003

- **id**: FM-UXEVAL-003
- **name**: 严重等级越界（用非法枚举值）
- **applies_to**: issue-attribution stage
- **related_kr**: KR-U2（严重等级 4 档枚举率）
- **related_golden_template_section**: §字段级要求（severity）
- **source_reference**: uxeval constitution #3; ux.severity-rubric
- **severity**: blocker
- **detection_signal**: severity 值不在 `critical/major/minor/suggestion` 内
- **trigger_condition**: 用"高/中/低"或"P0/P1"等非法等级
- **examples_synthetic_only**: `severity: "高"` 或 `severity: "P0"`
- **remediation**: 改为 4 档合法枚举，依据 severity-rubric 重判
- **delivery_decision**: block
- **not_allowed_claims**: 不得自定义严重等级体系
- **traceability_requirement**: 每个 severity 可追溯到 severity-rubric 判定依据

---

## FM-UXEVAL-004

- **id**: FM-UXEVAL-004
- **name**: 建议不可执行（缺改什么/改成什么/为什么）
- **applies_to**: issue-attribution stage 的 recommendation
- **related_kr**: KR-U3（建议可执行三要素覆盖率）
- **related_golden_template_section**: §必填章节（改进建议）
- **source_reference**: uxeval constitution #5; S2-H1 §2 uxeval 一票否决 #4
- **severity**: blocker
- **detection_signal**: 建议只有"这里要改一下/优化体验"类空泛表述
- **trigger_condition**: recommendation 缺三要素（改什么/改成什么/为什么）
- **examples_synthetic_only**: "导航需要优化"（无具体方案）
- **remediation**: 补全三要素；无法给出的标 gap
- **delivery_decision**: block
- **not_allowed_claims**: 不得把吐槽当建议
- **traceability_requirement**: 建议链接到对应 issue 与 heuristic 原则

---

## FM-UXEVAL-005

- **id**: FM-UXEVAL-005
- **name**: 功能测试偏移（把功能缺失当体验问题）
- **applies_to**: task-generation / issue-attribution stage
- **related_kr**: KR-U5（评估范围纪律）, KR1.1（最低交付线）
- **related_golden_template_section**: §必填章节（评估范围）
- **source_reference**: uxeval constitution #4; uxeval eval/failure/F001-功能测试偏移; ux.ux-failure-modes
- **severity**: major
- **detection_signal**: issue 描述"PRD 要求的 X 功能未实现"类需求覆盖问题
- **trigger_condition**: 把"功能在不在"当体验问题（应交 design-acceptance）
- **examples_synthetic_only**: "PRD 要求的搜索功能未实现" 被列为可用性 issue
- **remediation**: 标 out_of_scope；只保留"功能好不好用"类体验问题
- **delivery_decision**: degrade
- **not_allowed_claims**: 不得把需求覆盖度当体验评估结论
- **traceability_requirement**: 每条 issue 链接到 heuristic principle_id

---

## FM-UXEVAL-006

- **id**: FM-UXEVAL-006
- **name**: 证据-场景不匹配（issue 场景与截图内容不符）
- **applies_to**: issue-attribution stage（场景-证据校验）
- **related_kr**: KR-U1; KR3.2（标注覆盖率）
- **related_golden_template_section**: §traceability 规范
- **source_reference**: uxeval 06-issue-attribution Step 2.5（场景-证据匹配校验）
- **severity**: major
- **detection_signal**: issue 描述场景与 evidence 截图 OCR/说明不一致
- **trigger_condition**: 问题描述"配置数据源节点"但截图实为"空间详情页"
- **examples_synthetic_only**: issue 写"在结算页"，证据截图却是商品列表页
- **remediation**: 删除不匹配 issue 或标 [需现场验证] 移入 unverified_issues
- **delivery_decision**: gap
- **not_allowed_claims**: 不得把场景错配的 issue 当确认问题
- **traceability_requirement**: 场景-证据匹配结果记入 scene_evidence_validation

---

## FM-UXEVAL-007

- **id**: FM-UXEVAL-007
- **name**: 证据不足却声明完整交付（delivery 状态虚高）
- **applies_to**: delivery-audit / evidence-quality 判定
- **related_kr**: KR-U1; KR3.2
- **related_golden_template_section**: §gap / assumption / confidence 规范
- **source_reference**: ux.evidence-quality（交付四态）; S2-H2 golden template
- **severity**: major
- **detection_signal**: 证据覆盖不足却标 final_delivery_ready
- **trigger_condition**: coverage 不足但未降级为 fallback_safe / supplement_required
- **examples_synthetic_only**: 仅 3 张截图覆盖 10 个关键流程，仍标"评估完整"
- **remediation**: 按证据充分性降级交付状态，列 supplement_required
- **delivery_decision**: degrade
- **not_allowed_claims**: 不得在证据不足时声称"评估完整"
- **traceability_requirement**: 交付状态可追溯到 evidence coverage 计算

---

## FM-UXEVAL-008

- **id**: FM-UXEVAL-008
- **name**: 无原则映射的 issue（principle_ids 为空）
- **applies_to**: issue-attribution stage
- **related_kr**: KR-U5; KR1.1
- **related_golden_template_section**: §字段级要求（principle 映射）
- **source_reference**: ux.heuristic-principles; ux.issue-attribution
- **severity**: minor
- **detection_signal**: issue 的 principle_ids 数组为空
- **trigger_condition**: issue 未映射到任一启发式原则
- **examples_synthetic_only**: "这个按钮颜色不好看"无 principle_id 支撑
- **remediation**: 映射到具体 heuristic 原则；无法映射的复核是否为有效 issue
- **delivery_decision**: warn
- **not_allowed_claims**: 不得把无原则依据的主观偏好当 issue
- **traceability_requirement**: 每条 issue ≥1 个 principle_id

---

## 汇总

| severity | 数量 | FM id |
|---|---|---|
| blocker | 4 | 001, 002, 003, 004 |
| major | 3 | 005, 006, 007 |
| minor | 1 | 008 |
| **合计** | **8** | |

**一票否决覆盖**：4 个 uxeval 一票否决项（Evidence缺失/敏感信息/严重等级越界/建议不可执行）= FM-001~004 全覆盖。
**KR 未达标覆盖**：KR-U1(001/006/007) · KR-U2(003) · KR-U3(004) · KR-U4(002) · KR-U5(005/008) · KR3.2(006/007)。
