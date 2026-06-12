# Agent-design 产品方案与技术方案

> 编写日期：2026-05-15
> 版本：v0.1（待评审）
> 上游依据：`00-项目认知`（对话内）+ `01-竞品调研-Agent与Skills封装与自主进化.md`
> 用途：把 7 个设计领域 Agent 原型封装为「自主进化 + 带记忆的可共享 Skill 矩阵」，开源到 GitHub 并向集团内分发

---

## 0. TL;DR

**做什么**：把现有 6 个设计领域 Agent + 1 个 AI-native 治理底盘，重构为一套统一架构下的 Skill 矩阵，命名为 **DesignOS**（暂名，可改）。

**核心架构**：
```
DesignOS = Kernel（通用内核）+ 6 个 Domain Skills + N 个 MCP Servers
        + Eval-driven 进化飞轮 + 三级记忆系统 + GitHub Monorepo 分发
```

**封装标准**：Anthropic Agent Skills（`SKILL.md` + 目录约定）

**技术栈**：
- Skill 格式：Anthropic Skills（Markdown + Frontmatter）
- 工具协议：MCP（Model Context Protocol）
- 评估：Promptfoo + 自定义 LLM judge
- 记忆：mem0（情景）+ 文件系统（语义/程序）
- 编排：Skill 内部 YAML Pipeline（不引入 LangGraph）
- CI：GitHub Actions（含 eval 回归）
- 模型：Claude（主）+ Deepseek（兼容备份）

**分阶段交付**：
- M1（4 周）：Kernel + UXEval Pilot Skill 跑通
- M2（8 周）：6 个 Skill 全量上线 + Eval 飞轮 v1
- M3（12 周）：开源、集团推广、私有 Registry 雏形

---

## 1. 产品方案

### 1.1 产品定位

**一句话定位**：
> DesignOS 是一套面向集团内体验/产品/品牌/创意工作者的「AI-native 设计能力包」——把高级设计专家的方法论封装成可调用、可演进、可共享的 Skill 矩阵。

**它不是什么**：
- 不是又一个 ChatGPT 套壳
- 不是 Figma/MasterGo 的替代
- 不是一个一次性的项目交付物
- 不是只能在某一个 IDE 里用的工具

**它是什么**：
- 是设计专家经验的「可执行版本」
- 是组织级的设计质量基础设施
- 是一套跨工具（Claude Code / Trae IDE / Cursor / 未来其他）通用的能力包
- 是一个能持续学习、版本演进的知识系统

---

### 1.2 目标用户与场景

| 用户角色 | 主要场景 | 价值 |
|---|---|---|
| **高级体验设计师** | 用 Skill 加速自己的工作 + 培养中阶设计师 | 把自己的判断力沉淀为团队资产 |
| **中阶体验设计师** | 用 Skill 独立完成评估、原型、走查 | 不依赖专家也能产出标准质量 |
| **产品经理** | 用 PRD2Proto Skill 快速验证想法 | 需求阶段就能看到原型 |
| **品牌/创意人员** | 用 BrandCreative / IP-Design Skill | 系统化创意生产 |
| **新入职设计师** | Skill 当作教材使用 | 边用边学 |
| **跨业务复用** | 集团其他部门复用同一套 Skill | 降低重复建设 |

---

### 1.3 产品矩阵（6 + 1）

```
┌─────────────────────────────────────────────────────────┐
│              AI-Native 治理底盘 (Skill 0)                │
│  Issue 驱动 / PR 承载 / 契约锁定 / 六大门禁 / 灰度放量    │
└─────────────────────────────────────────────────────────┘
        ↑（嵌入到下面 6 个 Skill 的产物交付环节）
┌──────────────┬──────────────┬──────────────┐
│  UXEval      │  PRD2Proto   │  DesignSystem│
│  体验评估     │  PRD→原型    │  设计交付    │
├──────────────┼──────────────┼──────────────┤
│  IPDesign    │  BrandCreative│ AIAnalytics │
│  IP 设计     │  品牌咨询    │  竞品分析    │
└──────────────┴──────────────┴──────────────┘
```

**每个 Skill 的能力边界**（基于你已有文档的总结）：

| Skill | 输入 | 输出 | 核心子流程 |
|---|---|---|---|
| **uxeval** | PRD + 截图 + 启发式原则 | 旅程图 + 任务清单 + 问题报告 | 6 段：理解→原则→旅程→任务→证据→归因 |
| **prd2proto** | PRD + 设计草图 | 设计分析文档 + Vue3 可交互原型 | 6 段 + C1-C4 |
| **design-system** | 设计稿 DSL（MasterGo） | 符合规范的 Vue 代码 | 7 步：解析→映射→确认→生成→检查 |
| **ip-design** | PRD + 竞品 + 用户画像 | IP Brief + 世界观 + 视觉规范 | 6 段：策略→世界观→人格→视觉→叙事→落地 |
| **brand-creative** | PRD + 市场数据 | 策略→创意→设计→交付全套 | 8-9 段 + C1-C5 |
| **ai-analytics** | 竞品 URL/截图 | 多维度分析报告 + 策略建议 | 5 段：需求→采集→分析→策略→报告 |

---

### 1.4 核心产品原则

1. **Skill 即资产**：每个 Skill 是组织资产，要有 owner、版本、变更日志
2. **专家放行**：自动化只到「评估集筛选」为止，最终合入必须人工 review
3. **证据闭环**：所有结论强制绑定证据（截图/文档/链接），无证据=无效
4. **渐进式披露**：SKILL.md 主体精炼，详细方法论按需 load
5. **跨平台优先**：选格式、协议、工具时优先选「不绑死单一厂商」的方案
6. **可复用产物**：每次使用都要沉淀可复用模板，而不是一次性文档
7. **失败可追溯**：所有运行有 trace，失败案例可被 audit 和 learn

---

### 1.5 与现有资产的映射关系

| 现有资产 | 在新架构中的位置 | 改造动作 |
|---|---|---|
| 6 个 `*-agent.html` | 转为 Skill 主页 README + 营销页 | 提炼骨架，HTML 保留作为分享物料 |
| `ai-native.html` | 转为 Skill 0（治理底盘） + 集成进 CI/CD | 拆解为 Issue/PR 模板、门禁规则文件 |
| 11 份 Markdown 知识库 ×6 = ~70 份 | 各 Skill 的 `reference/` 目录 | 加 frontmatter、按渐进披露重组 |
| `Agent自主进化方案.md` | 实现为 `eval/` + `prompts/v*` + GitHub Actions | 工程化落地 |
| `分享材料维度.md` | 转为「六大能力对齐表」放各 Skill README | 简化为模板 |
| `体验评估分享内容.md` | UXEval Skill 的「方法论分享」章节 | 直接挪用 |
| 现有 `.mjs` 脚本 | 拆为 MCP Server | 标准化协议 |

---

### 1.6 商业化与开源策略

**开源范围**：
- **完全开源**：Kernel、Skill 模板、MCP Server、文档
- **可选开源**：6 个 Domain Skill 的方法论部分
- **保留私有**：评估宪法的高级版、专家级 few-shot 库、集团真实案例数据

**License**：建议 Apache 2.0（兼容性最好，适合企业引用）

**集团内分发**：先用集团 GitHub Enterprise 私有仓库，开源时镜像到公网

---

## 2. 技术方案

### 2.1 整体架构

```
                    ┌─────────────────────────────────┐
                    │       用户（设计师 / PM ）       │
                    └────────────┬────────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
        ┌─────────┐         ┌─────────┐        ┌─────────┐
        │ Claude  │         │ Trae /  │        │ Cursor  │
        │  Code   │         │ Cursor  │        │  Rules  │
        └────┬────┘         └────┬────┘        └────┬────┘
             │                   │                  │
             └───────┬───────────┴──────────────────┘
                     │ Skills 加载
                     ▼
        ┌────────────────────────────────────────────┐
        │              DesignOS Skills               │
        │  ┌──────────────────────────────────────┐  │
        │  │           Kernel (内核)              │  │
        │  │  Pipeline / Checkpoint / Evidence /  │  │
        │  │  Output / Memory / Trace             │  │
        │  └──────────────────────────────────────┘  │
        │           ↑     ↑     ↑     ↑              │
        │  ┌────────┴─────┴─────┴─────┴──────────┐  │
        │  │  6 个 Domain Skills (Skill Pack)     │  │
        │  │  uxeval / prd2proto / design-system  │  │
        │  │  ip-design / brand-creative / ai-    │  │
        │  │  analytics                           │  │
        │  └──────────────────────────────────────┘  │
        └────────────────┬───────────────────────────┘
                         │ MCP 协议
                         ▼
        ┌────────────────────────────────────────────┐
        │            MCP Servers (工具层)             │
        │  pdf-parser / browser-capture /            │
        │  excel-builder / mastergo-dsl /            │
        │  image-gen / ...                           │
        └────────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────────┐
        │         记忆与评估基础设施                  │
        │  mem0 / Markdown KB / Promptfoo / DSPy /   │
        │  GitHub Actions / Trace Storage            │
        └────────────────────────────────────────────┘
```

---

### 2.2 仓库结构（GitHub Monorepo）

```
designos/                                  # 仓库名
├── README.md                              # 项目主页
├── LICENSE                                # Apache 2.0
├── CHANGELOG.md
├── CONTRIBUTING.md
├── docs/
│   ├── 00-项目认知.md
│   ├── 01-竞品调研.md                    # ← 已存在
│   ├── 02-产品与技术方案.md              # ← 本文档
│   ├── 03-Kernel-spec.md                 # 待写
│   ├── 04-Skill-author-guide.md          # 待写
│   ├── 05-MCP-server-guide.md            # 待写
│   ├── 06-Eval-framework.md              # 待写
│   ├── 07-Memory-architecture.md         # 待写
│   └── 08-Governance-and-release.md      # 待写
│
├── kernel/                                # 通用内核
│   ├── pipeline/
│   │   ├── pipeline.yaml.schema          # Pipeline 配置规范
│   │   └── runner.py                     # Pipeline 执行引擎
│   ├── checkpoint/
│   │   ├── checkpoint.md.schema          # Checkpoint 描述规范
│   │   └── interrupt.py                  # 暂停 / 恢复机制
│   ├── evidence/
│   │   ├── evidence.json.schema          # 证据数据结构
│   │   └── collector.py                  # 收集与索引
│   ├── output/
│   │   └── templates/                    # md / xlsx / html 模板
│   ├── memory/
│   │   └── adapter.py                    # 三级记忆抽象
│   └── trace/
│       └── otel-config.yaml              # OpenTelemetry 配置
│
├── skills/                                # 6 个领域 Skill
│   ├── uxeval/
│   │   ├── SKILL.md                      # ★ 入口文件
│   │   ├── pipeline.yaml                 # Pipeline 配置
│   │   ├── constitution.md               # 评估宪法
│   │   ├── reference/                    # 方法论知识库
│   │   │   ├── index.json
│   │   │   ├── m01-需求理解.md
│   │   │   ├── m02-启发式原则.md
│   │   │   ├── m03-旅程建模.md
│   │   │   ├── m04-任务生成.md
│   │   │   ├── m05-证据采集.md
│   │   │   └── m06-问题归因.md
│   │   ├── templates/                    # 输出模板
│   │   │   ├── 旅程地图.md
│   │   │   ├── 任务清单-完整版.md
│   │   │   ├── 任务清单-简洁版.md
│   │   │   └── 问题报告.xlsx
│   │   ├── examples/
│   │   │   ├── 黄金样本-1/
│   │   │   └── 黄金样本-2/
│   │   ├── eval/
│   │   │   ├── golden/                   # 黄金评估集
│   │   │   ├── failure/                  # 失败案例集
│   │   │   ├── judges/                   # 自定义评估器
│   │   │   └── promptfoo.yaml            # Promptfoo 配置
│   │   ├── prompts/
│   │   │   └── v1.0.0/                   # 带版本的 Prompt
│   │   │       ├── 01-prd-understanding.md
│   │   │       ├── 02-principle-mapping.md
│   │   │       ├── ...
│   │   │       └── CHANGELOG.md
│   │   └── README.md                     # Skill 自身文档
│   ├── prd2proto/
│   ├── design-system/
│   ├── ip-design/
│   ├── brand-creative/
│   └── ai-analytics/
│
├── mcp-servers/                           # MCP 工具
│   ├── pdf-parser/
│   │   ├── server.py
│   │   ├── package.json / pyproject.toml
│   │   └── README.md
│   ├── browser-capture/
│   ├── excel-builder/
│   ├── mastergo-dsl/
│   └── image-prompt-gen/
│
├── shared/                                # 跨 Skill 共享资产
│   ├── personas/                          # 用户画像库
│   ├── design-tokens/                     # 通用 Token
│   └── component-libs/                    # 组件库索引
│
├── tools/                                 # 开发工具
│   ├── skill-creator/                    # 新 Skill 脚手架
│   ├── kb-validator/                     # 知识库 lint
│   └── eval-runner/                      # 本地跑 eval
│
└── .github/
    ├── workflows/
    │   ├── eval.yml                      # PR 跑 eval 回归
    │   ├── lint.yml                      # 知识库 + Skill 格式 lint
    │   └── release.yml                   # 自动 changelog + tag
    ├── ISSUE_TEMPLATE/
    └── PULL_REQUEST_TEMPLATE.md
```

---

### 2.3 核心组件详细设计

#### 2.3.1 Kernel — 通用内核

**职责**：抽出 6 个 Skill 的共同骨架，让每个 Skill 只配置差异。

**6 大组件**：

**(1) Pipeline 引擎**
- 输入：`pipeline.yaml`（声明式配置）
- 执行：按 stage 顺序调用，stage 间传递 state
- 支持：暂停（在 checkpoint）、恢复、重跑、回滚

**`pipeline.yaml` 示例（UXEval）**：
```yaml
name: uxeval-pipeline
version: 1.0.0
stages:
  - id: prd-understanding
    type: llm
    prompt: prompts/v1.0.0/01-prd-understanding.md
    inputs: [prd_file, business_context]
    outputs: [modules, roles, key_tasks, eval_boundary]
    knowledge: [reference/m01-需求理解.md]
    checkpoint: false

  - id: principle-mapping
    type: llm
    prompt: prompts/v1.0.0/02-principle-mapping.md
    inputs: [eval_boundary]
    outputs: [principle_checklist]
    knowledge: [reference/m02-启发式原则.md]
    checkpoint: false

  - id: journey-modeling
    type: llm
    prompt: prompts/v1.0.0/03-journey-modeling.md
    inputs: [modules, roles, key_tasks]
    outputs: [journey_map, journey_stages]
    checkpoint:
      id: C1
      message: 请确认用户旅程是否准确
      allow: [continue, modify, supplement]

  # ... 后续 stage

memory:
  read: [organization.uxeval.golden, organization.uxeval.failure]
  write: [project.uxeval.{project_id}]

constitution: constitution.md
```

**(2) Checkpoint 系统**
- 每个 Checkpoint 是一个「断点」，含：唯一 id、提示信息、允许的用户动作（continue/modify/supplement）
- 状态持久化为 JSON，支持中断后恢复
- 与 LangGraph 的 interrupt 机制思路一致，但实现更轻

**(3) Evidence 系统**
- 每条 Agent 结论必须绑定 `evidence_refs: [...]`
- 证据类型：截图（路径 + 区域）、文档（文件 + 锚点）、链接（URL + 时间戳）
- 内核提供 `evidence.attach()` API，Skill 调用

**(4) Output 模板**
- 三种格式：Markdown（阅读）、Excel（分派）、HTML（分享）
- 模板用 Jinja2 / Handlebars
- Skill 提供数据，Kernel 渲染

**(5) Memory Adapter**
- 三级抽象：`session.*` / `project.*` / `organization.*`
- Backend 可换：mem0、本地文件、Postgres
- 默认实现：`session` 用进程内、`project` 用项目目录、`organization` 用 mem0

**(6) Trace**
- OpenTelemetry 兼容，导出到 LangSmith / Phoenix / 本地文件
- 记录：每次 stage 调用、Prompt 版本、模型版本、输入输出、耗时

---

#### 2.3.2 Skill 包格式

**SKILL.md 格式**（以 UXEval 为例）：
```markdown
---
name: uxeval
version: 1.0.0
description: 把高级体验设计师的评估经验封装为 6 段式评估 Pipeline，输出绑定证据的问题报告
authors:
  - young@company.com
tags: [ux, evaluation, heuristics]
requires:
  kernel: ">=1.0.0"
  mcp_servers:
    - pdf-parser
    - browser-capture
    - excel-builder
  models:
    primary: claude-opus-4-7
    fallback: deepseek-v3
inputs:
  - name: prd_file
    type: file
    formats: [pdf, docx, md]
    required: true
  - name: screenshots_dir
    type: directory
    required: false
  - name: heuristic_principles
    type: file
    formats: [md, xlsx]
    default: reference/m02-启发式原则.md
outputs:
  - name: journey_map
    type: markdown
  - name: task_checklist_full
    type: markdown
  - name: task_checklist_lite
    type: markdown
  - name: issue_report
    type: xlsx
  - name: html_report
    type: html
---

# UXEval Skill

## When to use this skill

当需要对某个产品/功能做体验评估走查时调用本 Skill。典型场景：
- 新功能上线前的体验校验
- 历史功能的体验债务盘点
- 跨业务的体验质量基线对齐

## How it works

本 Skill 按 6 段流水线执行（见 `pipeline.yaml`）：

1. **需求理解**：解析 PRD，提取模块/角色/任务
2. **原则映射**：将启发式原则结构化为可执行检查点
3. **旅程建模**：构建用户旅程图（Checkpoint C1）
4. **任务生成**：产出完整版 + 简洁执行版双任务清单（Checkpoint C2）
5. **证据采集**：截图 + 浏览器采集，绑定问题
6. **问题归因**：输出问题清单 + 严重等级 + 解决方案（Checkpoint C3）

## Constitution（评估宪法）

详见 `constitution.md`。核心 7 条不可违反。

## Knowledge base

详细方法论按需加载：
- 需求理解 → `@reference/m01-需求理解.md`
- 启发式原则 → `@reference/m02-启发式原则.md`
- 旅程建模 → `@reference/m03-旅程建模.md`
- 任务生成 → `@reference/m04-任务生成.md`
- 证据采集 → `@reference/m05-证据采集.md`
- 问题归因 → `@reference/m06-问题归因.md`

## Examples

参考 `examples/` 下的两个黄金样本。

## Memory usage

本 Skill 会读取组织级记忆中的：
- `organization.uxeval.golden_samples`（黄金问题样例）
- `organization.uxeval.failure_cases`（典型失败案例）

会写入项目级记忆：
- `project.uxeval.{project_id}.judgements`（设计师对每条问题的判断）

不会写入组织级记忆（需专家审批后另行合入）。
```

---

#### 2.3.3 MCP Server 列表

将你现有 `.mjs` 脚本 + 新需求拆解为以下 MCP Server：

| Server | 工具 | 来源 |
|---|---|---|
| **pdf-parser** | parse_pdf, extract_sections | 新建（Python + pdfplumber） |
| **browser-capture** | capture_url, capture_flow | 来自 `capture_experience_eval.mjs` |
| **excel-builder** | build_issue_report, build_task_list | 来自 `build_heuristic_issue_report.mjs` |
| **mastergo-dsl** | parse_design, extract_tokens | design-system 用 |
| **image-prompt-gen** | gen_prompt_from_brief | ip-design / brand-creative 用 |
| **competitor-scraper** | scrape_site, analyze_layout | ai-analytics 用 |
| **vue-codegen** | gen_vue_component | prd2proto / design-system 用 |
| **figma-export**（可选） | export_design | 可选 |

每个 MCP Server 独立目录，独立 README，独立测试，可独立发布到 Smithery。

---

#### 2.3.4 评估框架（自主进化飞轮的工程化）

**评估集结构**：
```
skills/uxeval/eval/
├── golden/                          # 黄金样本
│   ├── case-001-classify-grade/
│   │   ├── input/                  # 输入：脱敏的 PRD + 截图
│   │   ├── expected/               # 期望产物
│   │   │   ├── journey-map.md
│   │   │   ├── task-checklist.md
│   │   │   └── issue-report.xlsx
│   │   └── annotations.yaml        # 专家标注：哪些是 must-have
│   └── ...
├── failure/                         # 失败案例
│   ├── fail-001-bias-to-functional-test/
│   │   ├── input/
│   │   ├── bad_output/             # 错误产物
│   │   └── why.md                  # 为什么失败 + 修正方向
│   └── ...
├── judges/                          # 评估器
│   ├── rule-evidence-bound.py      # 规则：每条问题必须有证据
│   ├── rule-severity-enum.py       # 规则：严重等级在合法枚举
│   ├── rule-no-leak.py             # 规则：不泄露敏感信息
│   ├── llm-experience-oriented.md  # LLM judge：是否体验导向
│   ├── llm-actionable.md           # LLM judge：建议是否可执行
│   └── llm-faithful.md             # LLM judge：忠实于截图和 PRD
├── promptfoo.yaml                   # Promptfoo 主配置
└── benchmarks/                      # 历史 benchmark 结果
    ├── v1.0.0.json
    ├── v1.0.1.json
    └── ...
```

**Promptfoo 配置示例**：
```yaml
description: UXEval Skill 回归评估
prompts:
  - file://prompts/v1.0.0/03-journey-modeling.md
providers:
  - id: claude-opus-4-7
  - id: deepseek-v3
tests:
  - description: 黄金样本 1
    vars:
      prd_file: golden/case-001/input/prd.md
      screenshots: golden/case-001/input/screens/
    assert:
      - type: javascript
        value: file://judges/rule-evidence-bound.py
      - type: llm-rubric
        value: file://judges/llm-experience-oriented.md
        threshold: 0.85
```

**CI 集成**：
- 每个 PR 触发 `eval.yml`
- 跑全量评估集，输出 benchmark.json
- 与上一个版本对比，关键指标（覆盖率、证据完整率、严重等级一致性）任何一个退步则 PR block
- 报告作为 PR comment 自动贴

---

#### 2.3.5 三级记忆系统

**Session 记忆**（会话内）：
- 实现：进程内变量 + Kernel Checkpointer 的本地 JSON 持久化
- 内容：当前 Pipeline 的 state、中间产物
- 生命周期：会话结束（或用户 abort）即清除

**Project 记忆**（项目级）：
- 实现：项目目录下 `.designos/project-memory/` Markdown + JSON
- 内容：当前项目的旅程图、任务、问题、决策、设计师批注
- 生命周期：项目内永久，可手动归档
- 写入方：Agent 自动写中间产物，设计师可手动批注

**Organization 记忆**（组织级，最关键）：
- 实现：mem0（情景记忆）+ Markdown 知识库（语义/程序记忆）
- 内容：
  - 黄金样本（成功的判断模式）
  - 失败案例（曾犯过的错）
  - 设计师偏好（特定专家的风格）
  - 跨项目模式（行业/产品类型的共性）
- 生命周期：长期
- **写入纪律（不可妥协）**：
  - Agent 只能写到 `organization.staging.*`（暂存区）
  - 必须设计专家在 GitHub PR 中 review 通过才合入 `organization.*`
  - 合入后打 tag、记录到 CHANGELOG
  - 自动评估器只能筛选候选，不能自动合入

**记忆 API（Kernel 提供）**：
```python
# Session
state.set("current_journey", journey_map)
state.get("current_journey")

# Project
project_memory.append("decisions", decision_obj)
project_memory.query("past_journey_for_module", module="...")

# Organization (read-only for Agent in production)
org_memory.search("similar_issue", query="...", k=5)
# 写入只能通过专门的 staging API
org_memory.propose("golden_sample", payload, requires_review=True)
```

---

#### 2.3.6 进化飞轮的工程实现

完整对应你方案文档的 7 步循环：

| 步骤 | 工程实现 | 文件位置 |
|---|---|---|
| 1. 运行任务 | Pipeline 执行 | `kernel/pipeline/runner.py` |
| 2. 记录全过程 | OpenTelemetry trace 输出到 trace store | `traces/` |
| 3. 自动评估 | Promptfoo + judges | `eval/` |
| 4. 人工校准 | GitHub Issue + 专家标注 | `.github/ISSUE_TEMPLATE/calibration.md` |
| 5. 归因问题 | 失败案例分类标签 | `eval/failure/*/why.md` |
| 6. 优化 Agent | DSPy 离线优化 + 专家审批 | `tools/dspy-optimizer/` |
| 7. 回归测试 | GitHub Actions | `.github/workflows/eval.yml` |
| 8. 发布新版本 | release.yml 自动 changelog + tag | `.github/workflows/release.yml` |

---

### 2.4 关键技术决策的取舍

| 决策点 | 选项 | 选择 | 理由 |
|---|---|---|---|
| **Skill 格式** | Anthropic Skills / 自创 | Anthropic Skills | 标准、Markdown 友好、与现有知识库契合 |
| **工具协议** | MCP / OpenAPI / 自创 | MCP | 已是事实标准 |
| **编排框架** | LangGraph / CrewAI / Skill 内 Pipeline | Skill 内 Pipeline | 你的场景顺序流水线足够，避免过度工程 |
| **记忆框架** | mem0 / Letta / 自建 | mem0 + 自建 | mem0 做情景，Markdown 做语义 |
| **评估框架** | Promptfoo / LangSmith / 自建 | Promptfoo（起步） | 轻量、CI 友好；规模化后可加 LangSmith |
| **Prompt 优化** | DSPy / TextGrad / 手工 | DSPy（阶段 3） | 学术成熟、社区活跃 |
| **主模型** | Claude / GPT / Deepseek | Claude（主）+ Deepseek（备） | 你已有 Deepseek，Claude Skills 是首发平台 |
| **仓库形态** | Monorepo / 多仓 | Monorepo（短期）→ 多仓（长期） | 起步简单，演进可拆 |
| **License** | Apache 2.0 / MIT / GPL | Apache 2.0 | 企业友好 + 专利保护 |
| **CI** | GitHub Actions / GitLab CI | GitHub Actions | 标配、生态成熟 |
| **Trace 存储** | LangSmith / Phoenix / 本地 | 起步本地 + Phoenix（自托管） | 数据不出集团 |

---

### 2.5 数据流与时序

**典型场景：设计师跑一次 UXEval**

```
1. 设计师在 Claude Code 中输入：
   "请用 uxeval skill 评估 ~/projects/foo 这个产品的体验"
   提供 PRD 路径 + 启发式原则 + 截图目录

2. Claude 加载 Skill：
   - 读取 SKILL.md（系统指令）
   - 读取 pipeline.yaml（流程）
   - 读取 constitution.md（约束）

3. Kernel.Pipeline 执行：
   Stage 1: PRD 解析（调用 pdf-parser MCP）
       → 输出模块/角色/任务
       → 写 session.modules
       → trace 记录
   Stage 2: 原则映射（LLM 调用）
       → 输出原则检查点
       → 写 session.principles
   Stage 3: 旅程建模（LLM 调用）
       → 输出旅程图
       → 写 session.journey_map
       → ★ 触发 Checkpoint C1：暂停等设计师确认
   ... 设计师在 IDE 中确认/修改 ...
   Stage 4: 任务生成
   Stage 5: 证据采集（调用 browser-capture MCP）
       → 输出截图 + 流程证据
   Stage 6: 问题归因
       → 输出问题清单
       → ★ Checkpoint C3：设计师校准严重等级
   Stage 7: 报告生成（调用 excel-builder MCP）
       → 输出 .md / .xlsx / .html

4. 项目级记忆写入：
   - project.uxeval.foo.journey_map
   - project.uxeval.foo.issues
   - project.uxeval.foo.decisions（设计师批注）

5. 设计师在 PR 中提交「这个项目里我新发现的某条经验值得加入组织记忆」：
   → 提交到 organization.staging.uxeval.golden
   → 走 GitHub PR review → 专家审批 → 合入

6. 下次类似项目使用 UXEval 时：
   → 自动读取 organization.uxeval.golden 中相关样本作为 few-shot
```

---

### 2.6 安全与合规

| 关注点 | 措施 |
|---|---|
| **敏感数据隔离** | 评估集脱敏 + 私有仓库；`.env.local` 不入 Git |
| **Prompt Injection** | Pipeline 内对用户输入加 `<user_input>` 隔离标签 |
| **凭证管理** | 1Password / Doppler；Skill 中只引用变量名 |
| **审计日志** | trace 保留 6 个月 + 关键决策入审计库 |
| **License 合规** | CI 中加 `license-checker`，禁 GPL 传染 |
| **数据出境** | 默认所有模型走集团内代理 / 私有部署 |
| **专家放行** | 任何 organization 记忆变更必走 PR review |

---

### 2.7 性能与成本

| 维度 | 估算 | 备注 |
|---|---|---|
| **单次 UXEval 跑完** | 15-30 分钟（含人工 Checkpoint） | LLM 调用约 6-10 次 |
| **单次 Token 消耗** | 50K-150K input / 20K-40K output | 取决于 PRD 大小 |
| **单次成本（Opus）** | $1-5 | 接受范围内 |
| **单次成本（Deepseek）** | $0.05-0.2 | 备份/降本可选 |
| **CI eval 全量跑** | 10-30 分钟 | 取决于评估集大小 |
| **CI 单次成本** | $5-20 | 优化方向：缓存 + 并行 |

---

## 3. 分阶段交付计划

### 3.1 里程碑

```
M1 (4 周)：Kernel + UXEval Pilot
├─ Week 1: Kernel 骨架 + Skill 模板
├─ Week 2: UXEval Skill 落地 + 3 个 MCP Server
├─ Week 3: Eval 框架 v1（Promptfoo + 5 个黄金样本）
└─ Week 4: 端到端跑通 + 内部 demo

M2 (5-12 周)：6 个 Skill 全量
├─ Week 5-6: prd2proto + design-system
├─ Week 7-8: ip-design + brand-creative
├─ Week 9: ai-analytics
├─ Week 10: 跨 Skill 共享资产抽取
├─ Week 11: Eval 飞轮 v2（DSPy 集成）
└─ Week 12: 集团内 5 个种子用户灰度

M3 (13-24 周)：开源 + 平台化
├─ Week 13-16: 文档完善 + 安全 review
├─ Week 17-20: 开源准备 + GitHub 发布
├─ Week 21-24: 集团 Skill Registry MVP
```

---

### 3.2 M1 详细任务（Pilot 期）

| 任务 | 产出 | 负责人 | 工时 |
|---|---|---|---|
| 设计 Kernel Pipeline schema | `pipeline.yaml.schema` | 待定 | 3d |
| 实现 Pipeline runner | `runner.py` | 待定 | 5d |
| 实现 Checkpoint 暂停/恢复 | `interrupt.py` | 待定 | 3d |
| 实现 Memory adapter（mem0 接入） | `adapter.py` | 待定 | 3d |
| pdf-parser MCP Server | `mcp-servers/pdf-parser/` | 待定 | 2d |
| browser-capture MCP Server | 复用 + 标准化 | 待定 | 2d |
| excel-builder MCP Server | 复用 + 标准化 | 待定 | 2d |
| UXEval SKILL.md + pipeline.yaml | Skill 入口 | 设计师 | 2d |
| UXEval reference/ 重构 | 6 份方法论文档 | 设计师 | 5d |
| UXEval constitution.md | 7 条评估宪法 | 设计师 | 2d |
| UXEval prompts v1.0.0 | 6 个 stage prompts | 设计师 + AI | 5d |
| UXEval golden 5 个样本 | 脱敏的真实案例 | 设计师 | 5d |
| UXEval failure 3 个案例 | 失败案例 | 设计师 | 2d |
| Promptfoo 配置 + 3 个 judge | `eval/promptfoo.yaml` | 待定 | 3d |
| GitHub Actions eval.yml | CI 工作流 | 待定 | 2d |
| 端到端 demo | 跑通完整流程 | 全员 | 3d |

**约 50 人天**，2 人全力推 4 周可完成。

---

### 3.3 风险预案

| 风险 | 概率 | 影响 | 预案 |
|---|---|---|---|
| Anthropic Skills 格式后续大改 | 中 | 高 | 抽象层兼容，Skill 迁移工具 |
| MCP 生态停滞 | 低 | 中 | 工具层抽象不绑死 MCP，可降级 |
| Eval 集质量差 | 中 | 高 | 专家强投入，定期 review |
| 设计师不愿用 | 中 | 高 | 早期种子用户绑定 + 案例驱动 |
| 集团合规阻塞 | 中 | 高 | 提前 1 月启动法务/安全 review |
| 模型成本超预算 | 低 | 中 | Deepseek 降级路径常备 |
| 自主进化跑偏 | 中 | 高 | 严格人类放行，禁止全自动合入 |

---

## 4. 待你评审决策的 8 个问题

为了让方案更具体、更可执行，需要你在评审时确认以下 8 个关键决策：

1. **命名**：项目最终命名 `DesignOS` / `Agent-design` / 其他？
2. **License**：Apache 2.0 是否可接受？（推荐）
3. **开源时机**：M1 跑通就开源 vs M3 才开源？
4. **集团内试点范围**：从你部门开始 vs 联合 2-3 个兄弟部门？
5. **Pilot 选择**：UXEval 作为 Pilot vs 选另一个 Skill？
6. **模型策略**：主推 Claude，还是与 Deepseek 双主？
7. **记忆边界**：组织记忆是按部门隔离 vs 集团统一？
8. **维护团队**：你 1 人 + 1 个工程，还是争取建 3-5 人小团队？

---

## 5. 下一步动作（建议）

如果方案通过评审：

1. **本周内**：拍板上述 8 个决策点，确定 M1 团队配置
2. **下周开始**：启动 M1 Pilot
3. **同步进行**：法务/安全/合规预审；准备集团内 sponsor

如果需要调整方案：

- 可对 6 个 Skill 的优先级排序提供建议
- 可针对某个具体技术决策深入讨论
- 可准备一份 30 分钟的内部宣讲材料（基于本文档）

---

## 附录 A：术语表

| 术语 | 定义 |
|---|---|
| **Skill** | 一个能力包，含 SKILL.md + 知识库 + Pipeline + 评估集 |
| **Kernel** | 跨 Skill 共享的内核，提供 Pipeline / Checkpoint / Memory 等基础能力 |
| **MCP Server** | 通过 Model Context Protocol 暴露工具的服务 |
| **Pipeline** | Skill 内的顺序执行流程，由若干 stage 组成 |
| **Checkpoint** | Pipeline 中的人机协同断点 |
| **Constitution** | Skill 的评估宪法，定义不可违反的硬约束 |
| **Evidence** | 绑定到 Agent 结论的证据（截图/文档/链接） |
| **Golden Sample** | 高质量的标杆样例，用于 few-shot 和评估 |
| **Failure Case** | 已知的失败模式，用于 anti-pattern 检测 |

---

## 附录 B：与现有项目文档的对照

| 现有文档 | 在新方案中的对应 |
|---|---|
| `Agent自主进化方案.md` 阶段 1 | M1 完成 |
| `Agent自主进化方案.md` 阶段 2 | M2 完成 |
| `Agent自主进化方案.md` 阶段 3 | M3 + 后续 |
| `分享材料维度.md` 六大能力 | 各 Skill README 的「价值映射」章节 |
| `体验评估分享内容.md` | UXEval Skill README 主体 |
| 6 个 `*-agent.html` | 各 Skill 的对外宣传页 + 方法论参考 |
| `ai-native.html` | Skill 0（治理底盘）+ CI/CD 配置 |

---

**方案版本**：v0.1
**期待评审反馈**：方案整体方向 / 8 个决策点 / 阶段拆分合理性 / 资源可行性
