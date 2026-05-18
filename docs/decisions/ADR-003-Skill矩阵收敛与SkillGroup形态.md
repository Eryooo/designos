# ADR-003：Skill 矩阵收敛 + Skill Group 形态 + 共享 MCP

> 日期：2026-05-15
> 状态：已批准
> 决策人：young
> 触发：研读 6 个 trae_projects 参考项目（prototype_agent / ipdesign / brand-skill / analysis_agent / system_agent / design-token），第二轮认知修正

---

## 决策概要

ADR-002 之后又发现：
- **prd2proto 与 design-system 实质边界重合**——都是「设计意图 → 代码」，差别仅在保真度
- **brand-creative 不是 Pipeline 形态**——是 13+ 个可独立调用的技能函数
- **methodology_advisor 是跨 Skill 共享能力**——多个 Skill 都需要"按场景选方法论"

---

## R7 决策汇总

| # | 决策 | 结论 |
|---|---|---|
| 7.1 | prd2proto + design-system 合并 | 融合为 `prd2proto`，三模式（PM / Designer-Spec / Designer-DSL） |
| 7.2 | 生产级代码生成路径 | **本地组件库 + Design Token + Design.md** 三件套（业界最佳实践） |
| 7.3 | ip-design 视觉转化 | 仅生成多家生图工具的提示词，不调用生图 API |
| 7.4 | brand-creative 形态 | 升级为 **Skill Group**（13+ 子技能 + 工作流编排 + 并行执行能力） |
| 7.5 | methodology-advisor | 提为共享 MCP Server |
| 7.6 | image-analyzer | 提为共享 MCP Server（多 Skill 都需要多模态图像分析） |
| 7.7 | Skill 总数 | 6 个（uxeval / design-acceptance / prd2proto / ip-design / brand-creative / ai-analytics） |
| 7.8 | Kernel 必须支持的 Skill 形态 | **Pipeline Skill** + **Skill Group**（双形态） |

---

## 7.1 prd2proto 三模式设计

```yaml
# skills/prd2proto/pipeline.yaml
name: prd2proto

mode_prompt:
  question: "你是哪类用户？这决定原型保真度和工作流。"
  options:
    - id: pm
      label: "产品经理（快速原型，演示用）"
      requires: [PRD]
      defaults:
        component_lib: "通用 Element Plus / AntDesign Vue"
        design_tokens: "默认中性主题"
        fidelity: low
    - id: designer-spec
      label: "设计师（高保真原型，无 Figma 稿）"
      requires:
        - PRD
        - design-spec.md (Skill 可帮用户生成)
      defaults:
        fidelity: medium
    - id: designer-dsl
      label: "设计师（生产级，有 Figma/MasterGo 稿）"
      requires:
        - DSL
        - design-spec.md
        - 本地组件库引用
      defaults:
        fidelity: high

stages:
  # 共享阶段（所有模式都跑）
  - id: prd-understanding
  - id: design-analysis             # 输出 design-analysis.md
    checkpoint: C1                  # 用户确认设计分析

  # 模式分支阶段
  - id: design-spec-generation
    only_when: mode == "designer-spec"  # 帮用户生成 design.md

  - id: dsl-fetch
    only_when: mode == "designer-dsl"
    mcp_server: figma-mcp / mastergo-mcp

  - id: token-extraction
    only_when: mode == "designer-dsl"
    mcp_server: frontend-codegen    # 子模块

  # 共享后期
  - id: code-generation
    mcp_server: frontend-codegen
  - id: preview-launch
```

---

## 7.2 生产级代码最佳实践（写入项目宪法）

每次 prd2proto 在 `designer-dsl` 模式下生成代码，必须：

1. **不得硬编码颜色 / 字号 / 间距**——必须用 Token 变量
2. **不得自行编写基础组件**——必须复用本地组件库（AntDesign Vue / Element Plus / 内部库）
3. **不得跳过状态覆盖**——所有交互组件必须覆盖 默认/悬停/按下/聚焦/禁用/加载/错误 七种状态
4. **不得忽略 Design.md 约束**——团队约定优先级最高

PM 模式下放宽前 3 条，但保留状态覆盖要求。

---

## 7.3 brand-creative 升级为 Skill Group

### 目录结构

```
skills/brand-creative/                  # ★ Skill Group
├── GROUP.md                            # 技能组说明 + 子技能注册表
├── workflows/                          # 预定义工作流
│   ├── full-T1-to-T8.yaml             # 全流程（13 子技能顺序）
│   ├── quick-audit.yaml                # T1+T2 快速审计
│   └── creative-only.yaml              # T5+T6 仅创意
└── skills/                             # 子 Skill 列表（每个独立可调）
    ├── deep-demand-exploration/
    ├── brand-asset-audit/
    ├── competitor-spectrum-analyzer/
    ├── cis-auditor/
    ├── brand-house-deconstructor/
    ├── social-content-analyzer/
    ├── opportunity-gap-analyzer/
    ├── aipl-strategy-mapper/
    ├── market-positioning-map/
    ├── uso-creative-directions/
    ├── three-step-reference/
    ├── visual-consistency-checker/
    ├── variant-generator/
    ├── multi-dim-design-evaluator/
    └── deliverable-generator/
```

### 三种调用方式

```bash
# 单技能调用
designos run brand-creative:competitor-spectrum-analyzer

# 工作流调用
designos run brand-creative --workflow full-T1-to-T8

# 并行调用（高级）
designos run brand-creative --parallel \
  competitor-spectrum-analyzer cis-auditor brand-house-deconstructor
```

### Kernel 必须新增的能力

- **Group 加载器**：识别 GROUP.md，注册子 Skill
- **工作流编排器**：解析 workflow YAML（顺序 / 并行 / 条件分支）
- **并行执行器**：多个独立子 Skill 并发跑，结果聚合
- **统一上下文**：子 Skill 可共享 group 级状态

---

## 7.4 共享 MCP Server 矩阵

### 自建 MCP Servers（DesignOS 维护）

| Server | 用途 | 使用方 |
|---|---|---|
| pdf-parser | PRD 解析 | uxeval, prd2proto |
| excel-builder | Excel 报告生成 | 全部需要表格输出的 Skill |
| playwright-driver | Web/Electron 自动化 | uxeval, design-acceptance |
| heuristic-engine | 启发式检测引擎 | uxeval |
| visual-diff | 设计稿 vs 实现视觉对比 | design-acceptance |
| frontend-codegen | 代码生成（含 DSL 解析、Token 提取、组件映射、状态覆盖） | prd2proto |
| competitor-scraper | 竞品网站抓取 | ai-analytics |
| **image-prompt-gen** | AI 图像提示词生成（多平台） | ip-design, brand-creative |
| **methodology-advisor** ★ | 方法论推荐 + 模板提供 | ai-analytics, brand-creative, ip-design |
| **image-analyzer** ★ | 多模态图像分析 | uxeval(client mode), ip-design, brand-creative, ai-analytics |

### 外部 MCP Servers（用户自装）

| Server | 安装 | 使用方 |
|---|---|---|
| mastergo-mcp | 用户从社区/官方安装 | prd2proto, design-acceptance |
| figma-mcp | 用户从社区安装 | prd2proto, design-acceptance |

---

## 7.5 methodology-advisor 边界

| 维度 | 是 | 不是 |
|---|---|---|
| 核心职责 | 根据 `{scenario, goal, domain, constraints}` 推荐方法论组合 + 提供模板 | 不执行方法论本身 |
| 输入 | 场景描述 | 不接受真实业务数据 |
| 输出 | 推荐列表 + 应用模板 + 选择理由 + 跳过理由 + 预估时间 | 不输出最终分析报告 |
| 维护内容 | 方法论库（PEST / SWOT / KANO / AIPL / USO / CIS / 双钻 / 五层模型 / 华为五步法 / 启发式十原则 / Gap 分析 / 价值主张画布 / 战略路线图 等 ~20 种） | 不维护项目数据、用户偏好 |

---

## 7.6 最终 Skill 矩阵

| Skill | 形态 | 触发 | 模式 | 关键 MCP |
|---|---|---|---|---|
| **uxeval** | Pipeline | `/uxeval` | web / client | playwright-driver, heuristic-engine, image-analyzer, pdf-parser, excel-builder |
| **design-acceptance** | Pipeline | `/design-acceptance` | web / client | playwright-driver, visual-diff, mastergo-mcp/figma-mcp |
| **prd2proto** | Pipeline | `/prd2proto` | pm / designer-spec / designer-dsl | pdf-parser, frontend-codegen, mastergo-mcp/figma-mcp |
| **ip-design** | Pipeline | `/ip-design` | — | image-analyzer, image-prompt-gen, methodology-advisor, competitor-scraper |
| **brand-creative** | **Skill Group** | `/brand-creative[:子技能]` | 单技能/工作流/并行 | image-analyzer, image-prompt-gen, methodology-advisor, competitor-scraper |
| **ai-analytics** | Pipeline | `/competitor-analysis` | — | competitor-scraper, image-analyzer, methodology-advisor, excel-builder |

---

## 影响

需同步更新：
- [x] `docs/INDEX.md` — Skill 数量降为 6，新增 ADR-003 引用
- [x] `docs/decisions/ADR-002.md` — 在末尾标记被 ADR-003 部分覆盖
- [x] `docs/architecture/01-总体架构.md` — Skill 列表 + MCP 矩阵
- [x] `docs/architecture/02-Kernel-设计.md` — 新增（含 Skill Group 支持）
- [x] `docs/architecture/03-Skill-规范.md` — 新增（Pipeline + Skill Group 双形态）
- [x] `docs/schemas/output-types.md` — 调整
- [x] `docs/plans/01-项目排期.md` — Skill 顺序调整
- [x] `docs/plans/02-并行执行任务.md` — MCP 列表更新
- [x] `docs/plans/03-Sub-agent-分工.md` — 新增（M0+M1 并行 sub-agent 任务）
