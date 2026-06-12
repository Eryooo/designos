# 6 个 Skills 深度需求排查（基于底层真源文档）

> 日期：2026-05-28
> 目的：在抽 Factory Template 之前，先把每个 skill 的真实需求摸清楚，找真正的共性，不臆想抽象。

---

## 真源文档（已通读）

| 文档 | 作用 |
|---|---|
| `legacy/Agent自主进化方案.md` | 项目最初的进化飞轮思想（评估宪法 / golden / failure / DSPy） |
| `legacy/sharing-materials/体验评估分享内容.md` | uxeval 的最初产品定位（6 段评估流水线） |
| `legacy/sharing-materials/分享材料维度.md` | ip-design / brand-creative 的最初业务背景（六大能力） |
| `docs/01-竞品调研.md` | 行业 benchmark |
| `docs/02-产品方案-v0.1.md` | 6+1 矩阵的最初设计 + 各 skill 输入输出 |
| `docs/分享/01-DesignOS完整方案沉淀.md` | 集团内分享版的产品定位 |
| `docs/decisions/ADR-001` | 五轮架构决策（运行时 / 数据契约 / 质量 / 治理 / 安全） |
| `docs/decisions/ADR-002` | Skill 矩阵 6→7（新增 design-acceptance）+ Playwright 共享 + 双模式 |
| `docs/decisions/ADR-003` | Skill 矩阵 7→6（design-system 并入 prd2proto）+ brand-creative 升 Skill Group |
| `docs/architecture/01-总体架构.md` | 系统全景 |
| `docs/architecture/03-Skill-规范.md` | Pipeline + Skill Group 双形态规范 |
| `docs/schemas/output-types.md` | OutputType 枚举（Skill 间数据契约） |
| `docs/plans/01-项目排期.md` | M0/M1/M2/M3 阶段拆分 |

---

## 6 个 Skills 逐个深度排查

### 1. UXEval（已实现，client + web 双模式）

**核心目标：** 把高级体验设计师的评估方法论封装成可复用工作流

**输入：**
- PRD（pdf/docx/md，必需）
- scope.md（必需）
- 截图（client mode）或 URL + 登录态（web mode）
- 启发式原则（默认 Nielsen 10 + 业务 5）

**输出（OutputType 真源）：**
- `user_journey`（用户旅程图）
- `task_checklist`（任务清单）
- `issue_report`（Excel 问题报告）
- `html_report`（HTML 报告）
- `evidence_pack`（证据包目录）
- `delivery_audit_bundle`（交付审计包）
- `heuristic_checklist`（启发式检查清单）
- `user_persona`（用户画像，可选）

**6 段方法论（底层真源）：** 需求理解 → 原则映射 → 旅程建模 → 任务生成 → 证据采集 → 问题归因

**模式：** web / client（不同的证据采集方式）

**MCP 依赖：** playwright-driver（web）/ image-analyzer（client）/ heuristic-engine / pdf-parser / excel-builder

**8 条评估宪法（不可违反）：**
1. 每条问题必须绑定证据
2. 不输出敏感信息
3. 严重等级在合法枚举内
4. 不把功能存在与否当作主要体验问题
5. 建议方案必须可执行
6. 问题描述必须包含用户影响
7. PRD 与实现冲突时标明基准来源
8. 证据截图必须与问题场景匹配

**质量目标：**
- normal mode: 99-100%
- fallback: 85%+
- web mode: final 100% / fallback 95%+

**特征：**
- ⭐ 评估型 skill
- ⭐ 需要 Checkpoint（C1/C2/C3）人工干预
- ⭐ 输出必须证据闭环
- ⭐ 有评估宪法（硬约束）
- ⭐ 跨 mode 共享 Stage 1-4

---

### 2. Design-Acceptance（设计还原度验收，未实现）

**核心目标：** 检查"功能在不在 / 像不像"，对比设计稿 vs 实现

**与 uxeval 的边界（来自宪法第 4 条）：**
- uxeval = "功能好不好用"
- design-acceptance = "功能在不在 / 还原度对不对"

**输入（推断自 ADR-002 + output-types）：**
- 设计稿 DSL（来自 mastergo-mcp / figma-mcp，外部 MCP）
- 实现端：URL（web mode）或 截图（client mode）
- `page_mapping`（页面映射表，用户输入）

**输出（OutputType 真源）：**
- `acceptance_report`（验收报告）
- `visual_diff_report`（视觉差异报告）
- `automated_eval_trace`（自动化执行 trace）
- `evidence_pack`（证据包）

**模式：** web / client（与 uxeval 完全对称）

**MCP 依赖：** playwright-driver（web）/ visual-diff / mastergo-mcp（外部）/ figma-mcp（外部）

**特征：**
- ⭐ 评估型 skill
- ⭐ 与 uxeval 共享 playwright-driver（双模式同结构）
- ⭐ 但核心检测逻辑不同：uxeval 用 heuristic-engine，design-acceptance 用 visual-diff
- ⭐ 需要外部 MCP（DSL 来源）
- ⭐ 输出仍是问题清单（"哪里没还原"）

---

### 3. PRD2Proto（PRD 转原型，未实现）

**核心目标：** PRD → 可交互前端代码（含生产级 100% 还原）

**三模式（关键，来自 ADR-003，与 uxeval 的 web/client 完全不同）：**

| 模式 | 输入 | 保真度 | 用户 |
|---|---|---|---|
| `pm` | PRD | low | PM 快速演示 |
| `designer-spec` | PRD + design-spec.md（Skill 可帮生成） | medium | 设计师高保真原型 |
| `designer-dsl` | DSL + design-spec.md + 本地组件库引用 | high | 设计师生产级代码 |

**designer-dsl 模式的"三件套"（生产级关键）：**
1. **MasterGo/Figma DSL**（设计稿数据）
2. **本地组件库引用**（AntDesign Vue / Element Plus / 内部库）
3. **Design.md**（团队约定，优先级最高）

**生产级宪法（4 条强约束）：**
1. 不得硬编码颜色 / 字号 / 间距 → 必须用 Token 变量
2. 不得自行编写基础组件 → 必须复用本地组件库
3. 不得跳过状态覆盖 → 默认/悬停/按下/聚焦/禁用/加载/错误 七种状态
4. 不得忽略 Design.md 约束

**输出（OutputType 真源）：**
- `prototype_code`（原型代码）
- `frontend_code`（前端代码，正式版）
- `design_tokens` / `design_token_spec`
- `information_architecture`
- `component_spec`

**MCP 依赖：** pdf-parser / **frontend-codegen**（核心，含 DSL 解析、Token 提取、组件映射、状态覆盖） / mastergo-mcp / figma-mcp

**Pipeline 阶段（推断，含 C1-C4）：**
1. PRD 理解
2. 设计分析（design-analysis.md）⚠️ Checkpoint C1
3. 模式分支：spec 生成 / DSL 抓取
4. Token 提取
5. 代码生成
6. 还原度自检（pm 模式跳过部分）
7. 预览启动

**特征：**
- ⭐ 生成型 skill（不是评估型）
- ⭐ 三模式语义和 uxeval 的 web/client 完全不同（不是证据采集差异，是保真度差异）
- ⭐ 输出 = 可执行代码（不是问题清单）
- ⭐ 需要外部 MCP（DSL 来源）
- ⭐ 生产级有"代码宪法"

---

### 4. IP-Design（IP 设计，未实现）

**核心目标：** IP 形象设计的方法论 Pipeline

**6 段方法论（来自 02-产品方案）：** 策略 → 世界观 → 人格 → 视觉 → 叙事 → 落地

**输入：**
- PRD（品牌 brief）
- 竞品（参考）
- 用户画像（可选，可从 ai-analytics 上游引用）

**输出（OutputType 真源）：**
- `brand_brief`（品牌 Brief）
- `brand_persona`（品牌人格档案）
- `visual_spec`（视觉规范）
- `content_plan`（内容计划）

**MCP 依赖：** **image-analyzer**（分析竞品/参考图）/ **image-prompt-gen**（生成多平台图像 prompt） / **methodology-advisor**（推荐方法论）/ competitor-scraper

**关键决策（ADR-003 决策 7.3）：**
- 视觉转化阶段**仅生成多家生图工具的提示词**，不调用生图 API
- 即不直接生成图片，输出的是"给 Midjourney/Stable Diffusion 用的 prompt"

**特征：**
- ⭐ 生成型 skill（生成 Brief / 人格 / 视觉规范 / 图像 prompt）
- ⭐ 不需要 web/client mode（输入是文档/参考图，不是产品本身）
- ⭐ 需要多模态分析（看竞品图片）
- ⭐ 需要方法论库（11+ 文档：MBTI / 双钻 / 五层模型 等）
- ⭐ 输出是文档 + prompt，不是代码也不是问题清单

---

### 5. Brand-Creative（品牌咨询，Skill Group 形态，未实现）

**核心目标：** 品牌创意全流程，包含 13+ 子技能

**为什么是 Skill Group（不是 Pipeline）：**
- 每个子技能可独立调用（"我只想做竞品光谱分析"）
- 子技能间有复杂编排（顺序 / 并行 / 条件分支）
- 一次完整流程要跑 13+ 子技能（T1-T8）

**13+ 子技能（按 Tier 分组）：**

| Tier | 子技能 | 类型 |
|---|---|---|
| T1 | deep-demand-exploration | 需求勘探（输入分析型） |
| T1 | brand-asset-audit | 品牌资产审计（评估型） |
| T2 | competitor-spectrum-analyzer | 竞品三层梯度划分（分析型） |
| T2 | cis-auditor | CIS 审计（评估型） |
| T2 | brand-house-deconstructor | 品牌屋拆解（分析型） |
| T2 | social-content-analyzer | 社交内容分析（分析型） |
| T2 | opportunity-gap-analyzer | 机会缺口分析（分析型） |
| T3 | aipl-strategy-mapper | AIPL 策略映射 |
| T3 | market-positioning-map | 市场定位图 |
| T5 | uso-creative-directions | USO 创意方向（生成型） |
| T5 | three-step-reference | 三步参考（生成型） |
| T6 | variant-generator | 多版本生成（生成型） |
| T7 | visual-consistency-checker | 视觉一致性检查（评估型） |
| T7 | multi-dim-design-evaluator | 多维设计评估（评估型） |
| T8 | deliverable-generator | 交付物生成 |

**3 种调用方式：**
1. **单技能调用** — `designos run brand-creative:competitor-spectrum-analyzer`
2. **工作流调用** — `designos run brand-creative --workflow full-T1-to-T8`
3. **并行调用** — `designos run brand-creative --parallel <multi-skills>`

**预定义工作流：**
- `full-T1-to-T8`：全流程（13 子技能）
- `quick-audit`：T1+T2 快速审计
- `creative-only`：T5+T6 仅创意

**Kernel 新需求（ADR-003 决策 7.8）：**
- Group 加载器（识别 GROUP.md）
- 工作流编排器（解析 workflow YAML，支持顺序/并行/条件分支）
- 并行执行器
- 统一上下文（子 Skill 共享 group 级状态）

**MCP 依赖：** image-analyzer / image-prompt-gen / methodology-advisor / competitor-scraper / excel-builder

**特征：**
- ⭐ Skill Group 形态（13+ 子 Skill）
- ⭐ 子 Skill 类型混杂（评估型 + 分析型 + 生成型）
- ⭐ 不需要 web/client mode
- ⭐ 需要工作流编排（kernel 必须支持）
- ⭐ 包含一个 multi-dim-design-evaluator 子技能（视觉/品牌评估，与 uxeval 互补）

---

### 6. AI-Analytics（竞品分析，未实现）

**核心目标：** 多维度竞品分析 + 输出策略建议

**5 段方法论（来自 02-产品方案）：** 需求 → 采集 → 分析 → 策略 → 报告

**输入：**
- 竞品 URL / 截图
- 行业关键词

**输出（OutputType 真源）：**
- `analysis_report`（分析报告）
- `design_strategy`（设计策略，**uxeval/prd2proto 的上游产物**）
- `comparison_matrix`（竞品对比矩阵）
- `user_persona`（用户画像，**uxeval 的上游产物**）

**MCP 依赖：** **competitor-scraper**（核心）/ image-analyzer / methodology-advisor / excel-builder

**特征：**
- ⭐ 分析型 skill（介于评估和生成之间）
- ⭐ 输入：竞品（URL or 截图）→ 是否需要 web/client mode？**有这个潜在需求**（ADR-003 没明确）
- ⭐ 输出 = 上游产物，喂给 uxeval / prd2proto / ip-design / brand-creative
- ⭐ 需要方法论库（PEST / SWOT / KANO / AIPL / USO 等 ~20 种）

---

## 真正的共性分析

### 共性 1：Skill 定义结构（强共性，所有 skill 都要）

| 元素 | 来源 | uxeval | design-acc | prd2proto | ip-design | brand-creative | ai-analytics |
|---|---|---|---|---|---|---|---|
| `SKILL.md` frontmatter | 规范 | ✅ | ✅ | ✅ | ✅ | GROUP.md | ✅ |
| `pipeline.yaml` | 规范 | ✅ | ✅ | ✅ | ✅ | workflow.yaml | ✅ |
| `constitution.md` | 规范 | ✅（8 条） | ✅（推断有） | ✅（4 条生产级） | ? | ? | ? |
| `reference/m*.md`（方法论） | 规范 | ✅（6 份） | ✅ | ✅ | ✅（11 份） | ✅（13+） | ✅（~20） |
| `prompts/v*/` | 规范 | ✅ | ✅ | ✅ | ✅ | 每子技能 1 份 | ✅ |
| `templates/` | 规范 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `eval/golden/` | 规范 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `eval/failure/` | 规范 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### 共性 2：Pipeline Stage 类型（强共性）

所有 Skill 的 stage 都是 `llm` / `tool` / `composite` 三种类型之一（已统一在 kernel 中）。

### 共性 3：Checkpoint 机制（中度共性）

- uxeval：C1/C2/C3
- design-acceptance：推断 C1/C2
- prd2proto：C1/C2/C3/C4（4 个）
- ip-design：6 段每段都有 checkpoint（推断）
- brand-creative：每个子技能内部有自己的 checkpoint
- ai-analytics：5 段（推断 C1/C2）

→ Checkpoint 机制是通用的，kernel 已支持。

### 共性 4：Evidence 概念（弱共性，仅评估型 skill 有）

| Skill | 有 evidence 概念 | 形式 |
|---|---|---|
| uxeval | ✅ | 截图 / DOM / trace 锚定问题 |
| design-acceptance | ✅ | 设计稿 vs 实现的视觉差异图 |
| prd2proto | ❌ | 输出是代码，不是问题 |
| ip-design | ❌ | 输出是 Brief/规范，不是问题 |
| brand-creative | 部分 ✅ | 仅 cis-auditor / multi-dim-design-evaluator 等评估型子技能 |
| ai-analytics | 部分 ✅ | 竞品采集结果作为分析依据 |

**结论：Evidence Contract 不是全局共性，只是评估型 skill 的需要。**

### 共性 5：Delivery Status（弱共性）

| Skill | 适用 final/fallback/blocked 模型 |
|---|---|
| uxeval | ✅ 完全适用（已实现） |
| design-acceptance | ✅ 完全适用 |
| prd2proto | ⚠️ 适用但语义不同（pm/designer-spec/designer-dsl 是保真度，不是质量门槛） |
| ip-design | ⚠️ 弱适用（生成型，每段输出有完整度） |
| brand-creative | 子技能各异 |
| ai-analytics | ⚠️ 适用（数据完整度可分级） |

**结论：Delivery Status 不是简单复用，需要按 archetype 分别定义。**

### 共性 6：MCP Server 共享（强共性）

| MCP Server | 使用方 | 共享度 |
|---|---|---|
| pdf-parser | uxeval, prd2proto | 中（2 个） |
| excel-builder | uxeval, ai-analytics, brand-creative | 中（3 个） |
| **playwright-driver** | uxeval, design-acceptance | 中（2 个） |
| **image-analyzer** | uxeval, ip-design, brand-creative, ai-analytics | **高（4 个）** |
| **methodology-advisor** | ai-analytics, brand-creative, ip-design | 中（3 个） |
| competitor-scraper | ai-analytics, brand-creative | 中（2 个） |
| image-prompt-gen | ip-design, brand-creative | 中（2 个） |
| heuristic-engine | uxeval | 低（1 个，专用） |
| visual-diff | design-acceptance | 低（1 个，专用） |
| frontend-codegen | prd2proto | 低（1 个，专用） |

**结论：MCP 共享是真共性，是 kernel 支持的核心能力。**

### 共性 7：Mode 概念（弱共性，语义不同）

| Skill | 有 mode 吗 | mode 的语义 |
|---|---|---|
| uxeval | ✅ | web / client（**证据采集方式**） |
| design-acceptance | ✅ | web / client（**证据采集方式**，与 uxeval 对称） |
| prd2proto | ✅ | pm / designer-spec / designer-dsl（**保真度档位**） |
| ip-design | ❌ | 无 mode |
| brand-creative | ❌ | 无 mode（但有 workflow 选择） |
| ai-analytics | 推测可能有 | web / client（竞品来源） |

**结论：mode 不是单一抽象。同样叫 mode，uxeval 是"证据采集差异"，prd2proto 是"保真度差异"。不能强行统一。**

### 共性 8：上下游产物消费（强共性）

OutputType 枚举已经定义清楚：
- ai-analytics → uxeval / prd2proto / ip-design 的上游
- uxeval → prd2proto 的上游
- prd2proto → 可被 design-acceptance 消费验证

**这是真共性，已通过 OutputType + upstream_refs 机制统一。**

### 共性 9：Constitution 机制（强共性）

每个 skill 都有自己的 constitution.md，约束输出质量：
- uxeval：8 条评估宪法
- prd2proto：4 条代码生产宪法
- 其他 skill 推断也有

**结论：Constitution 是机制级共性，但内容是 skill-specific 的。**

### 共性 10：自演进飞轮（强共性，全局机制）

所有 skill 都有：
- `eval/golden/`（黄金样本）
- `eval/failure/`（失败案例）
- Promptfoo 配置
- DSPy 优化（M3+）

**这是 kernel + GitHub Actions 层的共性，每个 skill 都共用同一套基础设施。**

---

## 关键洞察

### 1. 真正的强共性只有 5 个

1. **Skill 定义结构**（SKILL.md / pipeline.yaml / constitution.md / reference / prompts / templates / eval）
2. **Pipeline Stage 类型**（llm / tool / composite）
3. **Checkpoint 机制**
4. **MCP Server 共享**
5. **Constitution 机制**（每 skill 独立内容，但机制统一）
6. **自演进飞轮**（eval/golden + failure + Promptfoo）
7. **OutputType + upstream_refs**（Skill 间通信）

### 2. 弱共性不要硬抽

- **Evidence Contract**：只有评估型 skill 需要（uxeval / design-acceptance / 部分 brand-creative 子技能）
- **Delivery Status**：每个 archetype 语义不同
- **Mode**：uxeval/design-acceptance/prd2proto 三个有 mode 的语义都不同，不能统一
- **质量阈值**：每个 skill 的"100%"含义不同（uxeval 是证据可信度，prd2proto 是代码还原度，ip-design 是方法论完整度）

### 3. 三种 archetype 是真实存在的，但不能粗暴对应抽象

按"输出语义"分：

| Archetype | Skill | 输出本质 |
|---|---|---|
| 评估型 | uxeval, design-acceptance, brand-creative.evaluators | 问题清单（带证据） |
| 生成型 | prd2proto, ip-design, brand-creative.generators | 文档 / 代码 / prompt |
| 分析型 | ai-analytics, brand-creative.analyzers | 分析报告 / 上游产物 |

但 brand-creative 一个 skill 内同时存在三种 archetype 的子技能。

### 4. Kernel 已经做到了什么

当前 kernel 已经实现：
- ✅ Pipeline 引擎（stage 调度）
- ✅ Checkpoint 系统
- ✅ MCP Registry / 三种 transport（stdio / inprocess / sse）
- ✅ Preflight 机制（required_when）
- ✅ Memory adapter（三级）
- ✅ State management（state dict 流转）
- ✅ Error handling

**但没做：**
- ❌ Skill Group 加载器（brand-creative 必需）
- ❌ Workflow 编排器（顺序 / 并行 / 条件）
- ❌ 并行执行器
- ❌ Group 级状态共享
- ❌ Sub-skill 注册机制

### 5. M2 阶段的关键阻塞点

要做 M2 的 5 个 skills，最先要补的是：
1. **Skill Group 形态支持**（brand-creative 阻塞点，需要 kernel 升级）
2. **mode 系统的差异化处理**（prd2proto 的 mode 与 uxeval 不同）
3. **frontend-codegen MCP**（prd2proto 核心）
4. **methodology-advisor MCP**（ip-design / brand-creative / ai-analytics 共用）
5. **image-analyzer 的多 skill 适配**（当前只为 uxeval client mode 服务）

---

## 下一步建议

不要急着抽 Factory Template。应该先：

1. **先做 design-acceptance**（与 uxeval 双胞胎，最大化复用 playwright-driver，验证"评估型 skill"的共性）
2. **再做 ai-analytics**（验证"分析型 skill"的共性，且产出 design_strategy / user_persona 喂给其他 skill）
3. **再做 ip-design**（验证"生成型 skill"的共性，且只需 image-prompt-gen / methodology-advisor）
4. **再补 frontend-codegen MCP，做 prd2proto**（验证三模式系统）
5. **最后做 brand-creative**（最复杂，需要 kernel 升级 Skill Group 支持）

按这个顺序做完前 3 个，才有足够的真实数据去抽 Factory Template，否则只是基于 uxeval 一个样本的过度泛化。
