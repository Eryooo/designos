# S2-H5 — Input Quality Gate

> **本报告性质**:输入质量门(执行前自检层),与 S2-H4 输出质量门对偶。**引用层,非新标准层**——不新增通用质量标准、不新增 shared knowledge 真源、不改 runtime/pipeline/factory/release。
> **核心信念**:**先 PRD/需求 → 深度拆解 → 业务/产品/用户目标对齐 → 才能进入产出**。S2-H5 把这条纪律变成执行前的可对账判定门。
> **日期**:2026-06-12

---

## 1. 目标与边界

### 1.1 目标
在 skill **正式执行前**判断:
1. 输入是否足够支撑目标产出
2. 哪些缺失会导致输出降级 / 必须阻断 / 可标 gap 推断
3. 防止 AI 静默脑补、伪造证据、基于弱输入产出强结论

### 1.2 边界(硬约束)
| 允许 | 禁止 |
|---|---|
| 引用 H1 rubric / H1.1 KR | ❌ 新增质量标准 / KR |
| 引用 H2 golden template 必填字段 | ❌ 新增 golden 结构 |
| 引用 H3/H3.1 failure mode 输入相关风险 | ❌ 新增 failure mode / 复制 FM 正文 |
| 引用 H4 self review gate(对偶关系) | ❌ 改 H4 已固化的 4 枚举 |
| 引用 `knowledge/design-work-paradigm/01-input-diagnosis.md` 等已有真源 | ❌ 新增 shared knowledge 真源 |
| 引用各 skill constitution / PILOT-BOUNDARY / knowledge-manifest | ❌ 改 runtime/pipeline/factory/release |

---

## 2. H4 与 H5 的差异

| 维度 | S2-H4 Self Review Gate | S2-H5 Input Quality Gate(本批) |
|---|---|---|
| 检查对象 | **输出**是否合格 | **输入**是否足够支撑输出 |
| 时机 | 执行后(产出已生成),交付前 | **执行前**(产出未生成) |
| 失败处置 | block / degrade_with_gaps / pass_with_minor_warnings / pass | blocked_insufficient_input / needs_user_clarification / ready_with_assumptions / ready |
| 引用源 | H1~H3.1 + skill constitution / golden / failure-modes | H1~H4 + 各 skill input-diagnosis 方法论 + 已有 quality 资产 |
| 不可混淆 | 输出对不对 | 输入够不够 |

**两个 gate 独立判定**:一份产出可以"输入足够(H5 ready)但输出不合格(H4 block)",反之亦然。

---

## 3. 引用源清单

| 类别 | 文件 | 引用内容 |
|---|---|---|
| 输入诊断方法论 | `knowledge/design-work-paradigm/01-input-diagnosis.md` | 完整性 4 维评估 + 5 项核心原则 |
| 输入相关失败模式 | `knowledge/design-work-paradigm/18-failure-modes.md` §FM-I001~I003 | 输入缺失 / 输入质量低 / 格式不支持 |
| UX 证据充分性标准 | `knowledge/ux/evidence-quality.md`(`ux.evidence-quality`) | 证据充分性三属性 + 交付四态 |
| 数据完整度标尺 | `knowledge/research/`(数据完整度相关 asset,如 `research.data-completeness-rubric`) | coverage ≥ 0.70 阈值 + dimensions |
| OKR/KR | S2-H1.1 全局 KR3.2 / 各 skill KR-X1~X5 输入项 | gap/assumption/confidence 标注覆盖 |
| Golden template 必填字段 | S2-H2 各 skill template "输入前提" / "必填章节" | 倒推所需输入 |
| H3 输入相关 FM | 各 skill `eval/failure/failure-modes.md` blocker FM 中输入风险类 | 输入缺失触发的 blocker |
| H4 对偶 | `docs/audits/S2-H4-SELF-REVIEW-GATE.md` | 输出端 4 枚举 + 8 步 |

---

## 4. 统一执行顺序(8 步)

| Step | 名称 | 引用源 | 输出 |
|---|---|---|---|
| **1** | 识别 skill 与目标交付物 | skill SKILL.md outputs | skill id + 目标产出类型 |
| **2** | 收集用户输入与附件 | 用户提交 | input source inventory |
| **3** | 对照 skill input contract | constitution + SKILL.md inputs + knowledge-manifest | required input check 表 |
| **4** | 对照 golden template 必需信息 | H2 各 skill template "输入前提" / "必填章节" | golden input readiness 表 |
| **5** | 对照 failure mode 输入相关风险 | skill failure-modes.md(blocker FM 输入风险类) | failure mode input risk 表 |
| **6** | 识别 missing / ambiguous / inferred / unsupported | input-diagnosis 4 维评估 | gap ledger + assumption ledger |
| **7** | 判断 input_decision | §5 规则 | 4 枚举之一 |
| **8** | 输出 required_user_followup 或 assumption ledger | clarification questions | handoff to execution |

---

## 5. input_decision 规则

### 5.1 唯一枚举(只允许这 4 个)
```
ready
ready_with_assumptions
needs_user_clarification
blocked_insufficient_input
```

### 5.2 判定逻辑(优先级从高到低)

| 优先级 | 条件 | input_decision |
|---|---|---|
| 1(最高) | 缺少**产出必需输入**且无法合理推断 | **blocked_insufficient_input** |
| 2 | 缺少关键判断依据但可通过**少量追问补齐** | **needs_user_clarification** |
| 3 | 输入基本足够但有**推断项**(可标 inferred + assumption) | **ready_with_assumptions** |
| 4 | 输入完整、证据充分、边界清楚 | **ready** |

> 注:任何不确定按"风险未排除"处理——blocker 类输入缺失 + 无法推断 → 不得直接 ready,必须降级为 needs_user_clarification 或 blocked_insufficient_input。

### 5.3 与 H4 对偶映射

| H5 input_decision | 对 H4 输出端的影响 |
|---|---|
| `ready` | 输出端可正常自检,无前置降级 |
| `ready_with_assumptions` | 输出必须显式标注 inferred_fields + assumptions,H4 §7 检查这些标注覆盖率 |
| `needs_user_clarification` | 不得跳过追问直接执行;若强行执行,H4 极可能 degrade_with_gaps |
| `blocked_insufficient_input` | 不允许进入执行;强行执行后 H4 必然 block |

---

## 6. 5 个 Skill 的输入质量重点

### 6.1 prd2proto
**核心输入**:
- PRD 文件(完整度评分基线 ≥ 0.65 才能 proceed)
- 业务目标(必填,KR-A2 同款约束:target_audience / business_goal 非空)
- 用户角色(primary / secondary,带权限)
- 页面范围 / 模块清单
- 交互状态边界(loading / empty / error / 权限态等)
- 设计系统 / 组件约束(antd-pro / linear / coze 等模板选择)
- 技术边界(框架 / 浏览器兼容 / 性能基线)

**典型 blocker 场景**:PRD 缺业务目标或用户角色 → 18 stage 全链路无锚点。

### 6.2 uxeval
**核心输入**:
- 评估目标(可用性 / 完整性 / 合规)
- 关键页面 / 流程 / 任务清单
- 截图(client 模式)或 web URL(web 模式,且必须是 sanitized demo,严禁真实生产 URL)
- PRD / 功能说明(用于"功能在不在"vs"功能好不好用"区分)
- 证据覆盖(`ux.evidence-quality` 三属性:数量 / 多样性 / 时效)
- 评估模式(client / web)
- 可信度边界(已知不可评估的部分)

**典型 blocker 场景**:截图或 URL 缺失 → 无证据 = FM-UXEVAL-001 触发。

### 6.3 ai-analytics
**核心输入**:
- 分析目标(竞品对比 / 市场定位 / 用户画像)
- 行业 / 产品背景
- 竞品范围(≥ 3 个,若不足需明确)
- 数据来源(各 finding 必须有 evidence_refs)
- 用户 / 市场假设(明确标 inferred)
- 不可验证信息标注(已知数据缺口)

**典型 blocker 场景**:竞品资料缺关键维度且无替代来源 → coverage < 0.70 触发 QG1 + FM-AIANALYTICS-003。

### 6.4 ip-design
**核心输入**:
- 品牌 / 业务背景
- 目标人群(职业 / 场景 / 痛点)
- IP 角色定位(吉祥物 / 虚拟代言 / 服务化身)
- 品牌约束(既有色彩 / logo / 字体)
- 视觉风格边界(写实 / 卡通 / 极简等)
- 使用场景(线上 / 线下 / 衍生品)
- 禁忌项(文化禁忌 / 法务禁忌 / 品牌禁忌)

**典型 blocker 场景**:无品牌策略输入即开始视觉 → FM-IPDESIGN-004 视觉先行触发。

### 6.5 brand-creative
**核心输入**:
- 品牌目标(B 端 / C 端 / 政企)
- 竞品 / 市场上下文
- 品牌策略输入(若已有,如 brand-strategy 子 skill 上游产物)
- 子技能依赖(logo / color / typography / VI / voice 选哪几个)
- 应用场景(数字 / 印刷 / 包装 / 空间)
- 约束与禁区(法务 / 商标 / 文化)

**典型 blocker 场景**:策略输入仅有形容词无定位 → FM-BRANDCREATIVE-001 策略空心化触发。

---

## 7. 不可行为(防输入端 Honesty 失守)

执行前不得:
- ❌ 因输入不足而**直接产出强结论**(应降级为 ready_with_assumptions 或 needs_clarification)
- ❌ 把 **assumption 当 fact**(必须显式标 [inferred] 并附 risk_if_wrong)
- ❌ 把 **inferred 当 verified**(verified 需有 evidence_refs 指向真实采集数据)
- ❌ **用缺失证据支撑高置信结论**(confidence 必须反映 evidence 充分性)
- ❌ **跳过 gap ledger**(任何缺失/模糊都必须显式登记)
- ❌ **用真实业务数据/真实客户/真实截图**做输入示例(本模板及示例必须 synthetic / sanitized)

---

## 8. H5 / H4 / H6 关系

```
执行前              执行中           执行后              跨 skill
─────────          ────────        ─────────           ──────────
S2-H5            (skill            S2-H4               S2-H6(候选)
Input Quality →   runtime    →    Self Review     →    Cross-Skill
Gate              prompts)         Gate                 Consistency
                                                         Contract

输入对不对         产出过程         输出对不对           skills 之间一致性
ready/...         (不在本系列      pass/block/...       (skill A 输出 ↔
                   范围)                                  skill B 输入)
```

| 阶段 | 责任范围 |
|---|---|
| **H5(本批)** | 产出 `input quality report`(含 gap ledger / assumption ledger / clarification questions) |
| **H4** | 消费 H5 的 gaps / assumptions / inferred_fields,并在 §7 检查这些是否被标注覆盖 |
| **H6(候选,留作下一批评估)** | 跨 skill 一致性契约:如 ai-analytics 输出 design_strategy → prd2proto 输入,H6 校验上游 H4 通过的产出 = 下游 H5 的合法 input |

---

## 9. 5 个 Skill 审查入口表

| skill | input quality template | golden template | failure modes | input contract 来源 |
|---|---|---|---|---|
| prd2proto | `skills/prd2proto/templates/input-quality-gate.md` | `skills/prd2proto/templates/golden-prd2proto-output.md` | `skills/prd2proto/eval/failure/failure-modes.md` | `constitution.md` + `PILOT-BOUNDARY.md` + `pipeline.yaml` upstream_refs |
| uxeval | `skills/uxeval/templates/input-quality-gate.md` | `skills/uxeval/templates/golden-evaluation-report.md` | `skills/uxeval/eval/failure/failure-modes.md` | `constitution.md`(8 条)+ `INPUT.md` |
| ai-analytics | `skills/ai-analytics/templates/input-quality-gate.md` | `skills/ai-analytics/templates/golden-analysis-output.md` | `skills/ai-analytics/eval/failure/failure-modes.md` | `constitution.md`(4 条) |
| ip-design | `skills/ip-design/templates/input-quality-gate.md` | `skills/ip-design/templates/golden-ip-design-output.md` | `skills/ip-design/eval/failure/failure-modes.md` | `constitution.md`(8 条) |
| brand-creative | `skills/brand-creative/templates/input-quality-gate.md` | `skills/brand-creative/templates/golden-brand-creative-output.md` | `skills/brand-creative/eval/failure/failure-modes.md` | `GROUP.md` + `knowledge/design/quality/brand-creative-failure-modes.md` |

---

## 10. 本批文件清单

| 文件 | 类型 |
|---|---|
| `docs/audits/S2-H5-INPUT-QUALITY-GATE.md` | 总控报告(本文件) |
| `skills/prd2proto/templates/input-quality-gate.md` | skill 模板 |
| `skills/uxeval/templates/input-quality-gate.md` | skill 模板 |
| `skills/ai-analytics/templates/input-quality-gate.md` | skill 模板 |
| `skills/ip-design/templates/input-quality-gate.md` | skill 模板 |
| `skills/brand-creative/templates/input-quality-gate.md` | skill 模板 |
| `scripts/validate_input_quality_templates.py` | 只读校验脚本 |

**未碰**:runtime / pipeline / .factory/archetypes / release/npm/tag/workflow / version / install / `knowledge/manifest.yaml` / 禁止文件。

---

## 11. 状态

本批完成后,DesignOS senior-output 体系七件套齐全:
- ✅ rubric(H1)→ ✅ OKR/KR(H1.1)→ ✅ golden template(H2)→ ✅ knowledge guardrails(H2.2)→ ✅ failure modes(H3/H3.1)→ ✅ self review gate(H4)→ ✅ **input quality gate(本批 H5)**
- ⏭ 候选下一步:S2-H6 Cross-Skill Consistency Contract(跨 skill 上下游契约)
