# S2-H1 — 全 Skills 资深输出 Rubric 与最低交付线

> **本报告性质**:整合现有 quality 资产,为 5 skill 定义资深输出标准、最低交付线、一票否决项。**不新建第六套 rubric**——优先复用 `knowledge/design/quality/` 与 `knowledge/design-work-paradigm/17-18` 等已有资产。
> **资深输出含义**:输出按资深设计师能力要求定义判断标准。**不等于**实际产出已达资深水准——maturity 状态见 `skills/status.matrix.yaml`。
> **依据**:S1-0B 覆盖审计、`knowledge/manifest.yaml` 51 资产、各 skill `constitution.md` / 现有 rubric / failure modes。
> **日期**:2026-06-12

---

## 0. 关键术语校准(避免重复 S1-0B 已修正过的混淆)

| 概念 | 含义 | 不可被混用为 |
|---|---|---|
| **Senior output rubric** | 用资深设计师能力要求定义的输出判断标准(不是流程检查清单) | "已达资深水准" / "validated" |
| **Prompt-grade skill** | 有 prompts 与方法论,无 runtime 执行体 | runtime-grade |
| **Runtime-grade skill** | 有 runtime + 真接入 kernel/quality-gates(真 blocking) | prompt-grade |
| **`quality_gates:`** (列表) | kernel/quality-gates 真 blocking gate(stop_execution+QualityGateBlocked) | `gate:`(单数,checkpoint 暂停门) |
| **一票否决项** | 任一不合格,整方案不合格,不靠其他维度均分 | "P0 风险"(后者无强制级别) |
| **最低交付线** | "中阶可用"档,资深设计师能在其上做评审/微调而非推倒重来 | "高阶"(高阶=资深愿意接受) / "validated"(后者需多 case 真证据) |

---

## 1. 总体资深输出标准(全 skills 共用底座)

### 1.1 通用 4 档分级(沿用 ip-design 范式,推为全 skills 通用)

| 档位 | 含义 | 是否可作为最低交付线 |
|---|---|---|
| **高阶可评审** | 资深设计师愿意在其上评审 / 微调 | 不强制(超过最低交付线) |
| **中阶可用** | ✅ **最低交付线** — 资深设计师可基于此做评审,而非推倒重来 | ✅ 是 |
| **低阶仅雏形** | 框架对但深度不足,需返工(标注 gap 后可临时放行) | ❌ 否 |
| **不合格** | 框架错或自相矛盾,直接返工 | ❌ 否 |

### 1.2 通用 9 维评估底座

来自 `knowledge/design-work-paradigm/17-quality-rubrics.md`(全 skills 通用):

1. **Strategic Alignment** — 设计 ↔ 业务/用户目标对齐度
2. **User Understanding** — 用户画像/任务/痛点的理解深度
3. **Design Reasoning Depth** — 设计推理资产的完整性
4. **Output Completeness** — 产物是否覆盖最低必需字段
5. **Internal Consistency** — 跨阶段关键决策一致性
6. **Traceability** — 决策可追溯到输入证据
7. **Differentiation** — 与已有方案的真实差异化
8. **Feasibility** — 工程/法务/成本可落地性
9. **Honesty** — 不夸大(gaps/inferred 显式)、不自动认领能力边界外的事

### 1.3 通用一票否决底座(三条)

任一触发,整产物不合格:

| # | 失败模式 | 来源资产 |
|---|---|---|
| **F-Honesty** | 编造数据 / 静默补全缺失 / 推断未标 `[inferred]` | 各 skill constitution + `design.quality.common-failure-modes` |
| **F-Traceability** | 关键决策无依据,无法追溯到输入 | `knowledge/design-work-paradigm/19-traceability.md` |
| **F-OverClaim** | 文档/产物宣称超出 status.matrix maturity 允许的范围 | `docs/STATUS-DEFINITION.md` 五层 readiness + `not_allowed_claims` |

---

## 2. 每个 Skill 的资深输出标准

### 2.1 prd2proto

**资深输出定义**:从 PRD/简报出发,产出**资深交互/产品设计师水准**的设计推理资产链(18 个 stage 产物,从 requirement_inventory 到 professional_gap_report),让资深前端工程师能基于此生成可评审的演示原型代码。

**复用资产**:
- `frontend.code-quality-constitution`(代码宪法)
- `frontend.design-token-rules` / `frontend.component-state-rules` / `frontend.atomic-design`
- `product.interaction-state-coverage` / `product.information-architecture`
- `knowledge/design-work-paradigm/17-quality-rubrics.md`(通用 9 维)
- `skills/prd2proto/constitution.md`(项目级硬约束)

**rubric 缺口**:🔴 prd2proto **无独立的"senior output rubric"资产** — 当前依赖通用 9 维 + 4 个 frontend/product standards。S2-H2 候选:新建 `design.quality.prd2proto-output-rubric` 把 9 维裁剪到 prd2proto 实际 18-stage 输出场景。

**最低交付线(中阶可用)**:
1. 18 个 stage 产物全部产出(允许带 gaps,但 gaps 必须显式)
2. 每阶段输出通过其 schema 校验(对应 `kernel/contracts/artifacts/` 真 blocking)
3. `traceability_map` 完整覆盖核心决策(IA / page-flow / state-matrix → 上游 PRD / 推理资产)
4. `professional_gap_report` 自评 9 维并显式列出"距资深差距"
5. `constrained-code-generation` 通过 `code_constraint_gate`(无硬编码颜色/无非组件库 div)

**一票否决项(共 4 项)**:
| # | 项目 | 触发条件 |
|---|---|---|
| V1 | **Schema 违约** | 任一 stage 产物未通过对应 artifact schema 校验 |
| V2 | **Traceability 断裂** | 任一关键决策(IA/component-strategy/state-matrix)无可追溯依据 |
| V3 | **代码宪法违反** | 生成代码出现:硬编码颜色/字号、绕过 design-tokens、自建非组件库 div、未覆盖 7 状态 |
| V4 | **Honesty 违反** | 推断字段未标 `[inferred]`,或 gaps/warnings 缺失 |

**常见低阶失败信号**:
- design_objectives 与 PRD 业务目标无 1:1 映射
- user_task_map 只有 primary_tasks,无 edge_tasks(异常/权限/网络异常)
- state-matrix 仅 default + loading,缺 empty / error / disabled / forbidden
- `prototype_code` 用 `<div className="btn-primary">` 而非组件库 Button
- `traceability_map` 全为 `derived_from: PRD`(无具体上游 artifact ID)

**可宣称 / 不可宣称**:

| ✅ 可宣称 | ❌ 不可宣称 |
|---|---|
| "prd2proto 是 DesignOS 当前最深的资深化样板,真接入 kernel/quality-gates" | "prd2proto 已达资深交互设计师水平" |
| "pipeline v2 18 stage 中 prd2proto 是唯一 runtime-grade skill" | "可生成可直接用于生产的代码" |
| "schema 真 blocking + traceability 真接入" | "无需人工复核" |
| "可作为资深设计师评审起点" | "可替代资深设计师" |

---

### 2.2 uxeval

**资深输出定义**:从 PRD + 真实截图出发,产出**资深体验评估专家水准**的评估闭环——证据 → 问题 → 根因 → 影响 → 优先级 → 可执行建议。不只是问题清单。

**复用资产**:
- `ux.heuristic-principles`(评估原则)
- `ux.severity-rubric`(严重等级 4 档)
- `ux.evidence-quality`(证据充分性 standard)
- `ux.issue-attribution`(归因方法论)
- `ux.ux-failure-modes`(评估失败模式)
- `ux.journey-modeling` / `product.interaction-state-coverage`
- `skills/uxeval/constitution.md`(8 条硬约束)

**rubric 缺口**:🟡 uxeval 有 `ux.severity-rubric`,但那是**问题严重等级标尺**,不是**评估报告整体资深度** rubric。S2-H2 候选:新建 `ux.evaluation-quality-rubric`(类似 ip-design 的 9 维),衡量整份评估报告是否到资深线。

**最低交付线(中阶可用)**:
1. 每条 issue 必须有 ≥1 条 evidence(constitution 1)
2. 严重等级用 4 档枚举(`critical/major/minor/suggestion`)(constitution 3)
3. 不输出敏感信息(真实账号/真实姓名/内部 URL 全路径)(constitution 2)
4. 不把"功能存在与否"当体验问题(`out_of_scope` 标注)(constitution 4)
5. 建议方案必须可执行(改什么/改成什么/为什么)(constitution 5)
6. coverage 矩阵齐全:旅程阶段 × 角色 × 任务,每个 cell 有 issue 或显式标"无"

**一票否决项(共 4 项)**:
| # | 项目 | 触发条件 |
|---|---|---|
| V1 | **Evidence 缺失** | 任一 issue 的 `evidence_refs` 为空 |
| V2 | **敏感信息泄露** | 真实账号/密码/Token/真实姓名/内部 URL 全路径出现 |
| V3 | **严重等级越界** | 出现 `severity: "P0"` / `"high"` / `"中"` 等非合法枚举 |
| V4 | **建议不可执行** | "这里要改一下"类吐槽,无"改什么/改成什么/为什么" |

**常见低阶失败信号**:
- 问题清单只列现象不归根因
- 根因全是"用户体验差"/"不够直观"(无具体 heuristic 违反)
- 严重等级集中在 minor/suggestion(规避 critical 的责任)
- 同一 heuristic 重复 N 条 issue 但是同一根因(应聚类为 1 条)
- 评估只覆盖 happy path,缺 error/edge

**可宣称 / 不可宣称**:

| ✅ 可宣称 | ❌ 不可宣称 |
|---|---|
| "基于 Nielsen 启发式 + WCAG 部分覆盖的体验评估" | "可替代专业 UX 研究员" |
| "可识别明显可用性问题,生成结构化 issue 报告" | "已经过真实用户测试验证" |
| "证据 → 问题 → 根因 → 建议 闭环" | "可作为合规/法律认证依据" |
| "适合内部 review 起点" | "已接入统一 kernel quality_gates"(实际是 `gate:` 暂停门,无 runtime) |

---

### 2.3 ai-analytics

**资深输出定义**:从竞品/市场/用户资料出发,产出**资深产品/策略分析师水准**的可被下游消费的 design_strategy + user_persona,每条结论可追溯到证据,置信度可量化。

**复用资产**:
- `research.methodology-selection`(JTBD/SWOT/PEST/AIPL/KANO 选择)
- `research.competitor-analysis` / `research.user-persona-quality`
- `research.data-completeness-rubric`(coverage rubric)
- `design.design-strategy` / `design.tone-and-visual-direction`
- `skills/ai-analytics/constitution.md`(4 条硬约束)

**rubric 缺口**:🟡 ai-analytics 有 `research.data-completeness-rubric`(衡量"输入数据是否够"),但**没有"输出 strategy 资深度"rubric**。S2-H2 候选:新建 `research.strategy-quality-rubric` 衡量 design_strategy / user_persona 的资深度。

**最低交付线(中阶可用)**:
1. 不编造数据(constitution 1):所有结论可追溯到 `collected_data` 具体条目
2. design_strategy / user_persona 严格符合 schema(constitution 2):`target_audience` / `business_goal` / `goals` / `pain_points` 必填非空
3. `data_completeness_assessment.coverage` ≥ 0.70,< 0.70 触发 QG1 硬停(constitution 3)
4. 不越界产出问题清单/代码(constitution 4):仅产出分析与上游策略
5. 推断字段标 `[inferred]` 并说明依据
6. 每条 finding 有 `evidence_refs` 指向 `collected_data` 真实来源

**一票否决项(共 4 项)**:
| # | 项目 | 触发条件 |
|---|---|---|
| V1 | **编造数据** | 资料无某竞品价格,却写出"竞品 A 定价 ¥99/月" |
| V2 | **下游必需字段缺失** | `design_strategy.target_audience` / `business_goal` 为空,导致 prd2proto 注入失效 |
| V3 | **Coverage 虚高** | 实际 coverage < 0.70 标成 ≥ 0.70 |
| V4 | **越界产出** | 产出问题清单 + 严重度(uxeval 职责)/ 代码 / 原型(prd2proto 职责) |

**常见低阶失败信号**:
- comparison_matrix 单元格大量 "TBD" / "?" 但 coverage 仍被标 0.85+
- design_strategy 只有形容词(科技感/年轻化),无可消费的 target_audience 字段
- user_persona 只有姓名/年龄,无 goals 与 pain_points
- 推断字段不标 `[inferred]`,如把"猜测的竞品定价"当事实写
- 引用"行业平均"但无具体数据来源

**可宣称 / 不可宣称**:

| ✅ 可宣称 | ❌ 不可宣称 |
|---|---|
| "可消费 PRD 资料 + 竞品资料,产出可被 prd2proto 消费的 design_strategy / user_persona" | "替代真实市场研究 / 用户访谈" |
| "结构化的竞品对比框架,可追溯到来源条目" | "作为产品决策唯一依据" |
| "适合作为 prd2proto 的上游分析输入" | "可用于财务/投资分析" |
| "pilot 阶段:仅稳定产出 design_strategy / user_persona 两个产物" | "已接入 runtime"(实际 prompt-grade,无 runtime) |

---

### 2.4 ip-design

**资深输出定义**:从产品/服务定义 + 目标用户出发,产出**资深 IP 设计师水准**的 6 阶段闭环 IP 系统(brand_brief → worldview → persona_profile → visual_spec → content_plan → brand_material_spec + image_prompt_pack),每个产物可被中阶设计师接手微调。

**复用资产**(已有完整四件套):
- ✅ `design.quality.ip-design-quality-rubric`(9 维 × 4 档) — **已是范式**
- ✅ `design.quality.common-failure-modes`(IP 常见反模式)
- ✅ `design.quality.stage-review-checklists`(6 阶段评审清单)
- ✅ `design.quality.professional-gap-report`(诚实声明书)
- 各阶段方法论:`design.ip.methodology` / `design.ip.worldview-building` / `design.persona.persona-modeling` / `design.visual.visual-translation` 等
- `skills/ip-design/constitution.md`(8 条硬约束)

**rubric 缺口**:✅ **无独立缺口**——ip-design 有最完整的资深 rubric 体系,是其他 skill 应对标的范式。

**最低交付线(中阶可用)**:
1. 6 阶段产物齐全(brand_brief / worldview / persona_profile / visual_spec / content_plan / brand_material_spec)
2. 9 维 rubric 自评全部到 "中阶可用" 或以上(`design.quality.ip-design-quality-rubric`)
3. 一票否决项(D2/D6/D8)无"低阶/不合格"
4. 必附 `professional_gap_report`(`design.quality.professional-gap-report`)
5. `image_prompt_pack` 含四层结构 + 严格禁忌负向提示词(constitution 6)
6. 每个关键决策(北极星/人格关键词/主形选择/色彩配比)给依据链 + 推断标 `[inferred]`(constitution 2)

**一票否决项(共 4 项,直接来自 ip-design rubric)**:
| # | 项目 | 触发条件 |
|---|---|---|
| V1 | **D2 差异化** | 差异化靠贬低/自夸,或与竞品高度重叠 |
| V2 | **D6 法务/合规** | 核心符号有未标注的潜在商标/版权风险,或敏感映射 |
| V3 | **D8 人格立体度** | 仅有 MBTI 标签或口头禅,无行为模式/动机/恐惧/成长弧 |
| V4 | **视觉先行** | 先画图后反推策略(constitution 1) |

**常见低阶失败信号**(来自 `common-failure-modes`):
- 关键词从 M01 到 M06 漂移(品牌一致性 D1 失守)
- 32px 缩略图模糊不可辨(识别度 D4 失守)
- 衍生品工艺脱离量产能力(落地成本 D5 失守)
- 仅 MBTI/口头禅无行为模式(D8 失守)
- 提示词无负向 prompt(`strict_avoidance`)
- 任一维度打"高阶"但 rubric_self_eval.rationale 无依据

**可宣称 / 不可宣称**:

| ✅ 可宣称 | ❌ 不可宣称 |
|---|---|
| "六阶段结构化 IP 设计,产出 7 类资产" | "自动生成商用 Logo" |
| "至少替代中低阶设计师,达高阶可评审基线" | "替代资深设计师终审" |
| "提示词包跨平台 + 含负向控制" | "本产出已完成商标审查" |
| "中阶设计师可接手微调" | "可直接印刷 / 可直接发布" |
| "合成 case 验证(synthetic case)" | "已通过真实商业项目验证"(若无真实 case) |

---

### 2.5 brand-creative

**资深输出定义**:从品牌策略输入出发,产出**资深品牌策略师水准**的品牌策略 → VI → 内容 → 物料 → 品牌手册全链路,13 子 skill 覆盖。

**复用资产**:
- `design.strategy.brand-strategy-methodology`(策略方法论)
- `design.visual.logo-design-methodology` / `color-system-methodology` / `typography-system-methodology` / `visual-identity-integration-methodology`
- `design.strategy.brand-audit-methodology` / `brand-voice-methodology`
- ✅ `design.quality.brand-identity-quality-rubric`(品牌识别 rubric)
- ✅ `design.quality.brand-creative-failure-modes`(品牌创意失败模式)
- `design.quality.professional-gap-report`(通用诚实声明书)

**rubric 缺口**:🟡 brand-creative 有 rubric + failure modes,但**缺 stage-review-checklists**(各 sub-skill 的阶段评审清单,类似 ip-design 的)。考虑到 13 sub-skill 中仅 6 有 pipeline,本批不强建议补,等 sub-skill 主线建完再补。

**最低交付线(中阶可用)**:
1. 品牌策略基线齐全(定位 / 差异化 / 核心价值 / 人格关键词)
2. logo / 色彩 / 字体 / VI 至少有 1 个 sub-skill 跑完产出 brief 与规范(当前 6 sub-skill 有 pipeline)
3. `brand-identity-quality-rubric` 自评全部到 "中阶可用"
4. `brand-creative-failure-modes` 自检无"严重"级失败
5. 必附 `professional_gap_report`

**一票否决项(共 3 项,基于 brand-identity rubric)**:
| # | 项目 | 触发条件 |
|---|---|---|
| V1 | **策略空心化** | 品牌策略全是形容词(年轻 / 科技 / 信任),无可消费的差异化定位 |
| V2 | **法务/商标风险** | 核心 logo / 名称有明显商标冲突,无标注 |
| V3 | **跨子 skill 不一致** | 策略说 "高端简约",logo 用了大量装饰性元素 |

**常见低阶失败信号**(来自 `brand-creative-failure-modes`):
- logo "看起来好看"但无可识别记忆点
- 色彩系统无对比度可访问性验证(WCAG AA)
- 字体系统无授权风险检查
- VI 手册各章节口径互相矛盾
- "competitive-analysis 子 skill" 单纯列竞品 logo,无差异化定位输入

**可宣称 / 不可宣称**:

| ✅ 可宣称 | ❌ 不可宣称 |
|---|---|
| "Skill Group 框架已搭,13 sub-skill 中 6 个有 pipeline 主线" | "13 个 sub-skill 全部可用" |
| "可生成 brand-strategy + VI 框架" | "替代专业品牌咨询" |
| "alpha 阶段:contracts + 部分子 pipeline" | "可直接用于品牌发布 / 商标注册" |
| "适合内部品牌 brief 起点" | "已接入 runtime"(无 runtime) |

---

## 3. 与 status.matrix Maturity 的关系

**核心规则**:rubric 标准定义 ≠ 实际产出已达该标准。

| status.matrix maturity | rubric 角色 | 真实含义 |
|---|---|---|
| `alpha`(brand-creative) | rubric 是**目标**,主线未实现,大量产物为空 | 不能宣称达到任何 rubric 档位 |
| `pilot`(prd2proto/ai-analytics/ip-design) | rubric 是**判断标准**,产出有,但需人工复核 | 可用 rubric 做自评,但不可宣称 senior_level_ready |
| `beta`(uxeval) | rubric 是**评审标尺**,核心功能稳定 | 可用 rubric 做评审,**但 S1-0B 实证 uxeval 无 runtime,beta 偏乐观,需复核** |
| `stable`(目前无) | rubric 是**回归基线**,验证后稳定 | 可宣称按 rubric "中阶可用"稳定产出 |

**禁止跳级推导**(沿用 STATUS-DEFINITION.md 第 5 条):
- 不能因为"rubric 标准已定"声称"已达 senior_level"
- 不能因为"pilot 已通过 1 case rubric 自评"声称"validated"
- 不能因为"runtime 真接入 quality_gates"(prd2proto 是这样)声称"达资深水准"

**当前可声明状态**:
- **DesignOS 全 skills 已建立资深输出标准定义**(本批次产出)
- ✅ **不可声明**"DesignOS 已达资深设计师水平" — maturity 显示 alpha/pilot/beta,validated=false 全空

---

## 4. 是否新增 Knowledge Asset

**本批次决策:不新增**。

**理由**(inventory-before-build):
1. **5 skill 中 ip-design 有完整四件套**(rubric+fm+checklists+gap report),是范式 — 不需要新建
2. **brand-creative 有 rubric + fm**,缺 stage-checklist,但因 13 sub-skill 仅 6 有 pipeline,等主线补完再补 checklist 更合适
3. **uxeval/ai-analytics/prd2proto 缺独立"输出资深度 rubric"**,但通用 9 维(`17-quality-rubrics`)+ 各自的 standards/methodologies 已覆盖最低交付线判断 — S2-H2 决定是否新建专属 rubric

**留给 S2-H2 的候选新增**(仅候选,本批不建):
- `design.quality.prd2proto-output-rubric`(裁剪 9 维到 prd2proto 18-stage 输出场景)
- `ux.evaluation-quality-rubric`(衡量整份评估报告资深度,非问题严重度)
- `research.strategy-quality-rubric`(衡量 design_strategy / user_persona 资深度)
- `design.quality.brand-creative-stage-checklists`(各 sub-skill 阶段评审清单,等主线补完)

---

## 5. 全 skills 资深输出 Rubric 摘要表

| Skill | maturity | 现有 rubric | 一票否决数 | 最低交付线核心 | rubric 缺口 |
|---|---|---|---|---|---|
| prd2proto | pilot | 通用 9 维 + 4 frontend/product standards | **4** | 18 stage 全产 + schema 真 blocking + traceability + code 宪法 | 🔴 缺独立资深输出 rubric |
| uxeval | beta | severity-rubric + evidence-quality + failure-modes | **4** | 证据 → 问题 → 根因 → 建议 闭环 + coverage 全 | 🟡 缺评估报告整体资深度 rubric |
| ai-analytics | pilot | data-completeness-rubric + user-persona-quality | **4** | 不编造 + schema 必填 + coverage≥0.70 + 不越界 | 🟡 缺 strategy 资深度 rubric |
| ip-design | pilot | **完整四件套**(rubric+fm+checklists+gap report) | **4**(D2/D6/D8 + 视觉先行) | 6 阶段全产 + 9 维全到中阶 + gap report | ✅ 无 |
| brand-creative | alpha | rubric + failure-modes | **3** | 策略基线齐全 + 至少 1 sub-skill 跑通 | 🟡 缺 stage checklist(等主线) |

**一票否决项总数**:4+4+4+4+3 = **19** 项(全部基于已有资产或现有 constitution 硬约束)。

---

## 6. 核心原则(本报告内化)

| 原则 | 含义 |
|---|---|
| **判断标准 ≠ 已达水平** | rubric 是"按资深要求定义的判断尺",不是"已达资深"的证书 |
| **复用 > 新建** | 本报告整合现有 16 个 quality 资产,不新建第六套 |
| **缺口指认 ≠ 缺口必补** | 标识 rubric 缺口供 S2-H2 评估,不强制必须新建 |
| **runtime-grade 必须实证** | 仅 prd2proto 是 runtime-grade(真接 kernel/quality-gates);其他 4 个是 prompt-grade |
| **`gate:` ≠ `quality_gates:`** | 沿用 S1-0B/0C 校准:前者是 checkpoint 暂停门,后者是 kernel 真 blocking |
| **maturity 锚定可宣称口径** | 高于 maturity 的宣称都是 not_allowed_claim |

---

## 7. 后续(S2-H2 / S2-H3 候选,不在本批)

**S2-H2(Golden Output Templates)**:
- 为每个 skill 写 1 份"中阶可用"档样板(synthetic golden case),不引入真实业务数据
- 若 H1 指认的 3 个 rubric 缺口经评估后值得补,则在 H2 同步新建

**S2-H3(Senior Review Process)**:
- 定义"资深评审"运作流程:谁评审、按 rubric 哪些维度、产出 review-report
- 落地为 `.claude/skills/` 下的资深评审 skill 或 governance 步骤

---

*报告结束。本批次不新增 knowledge asset、不改 runtime / pipeline / .factory/archetypes / 发布。*
