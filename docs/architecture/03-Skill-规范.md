# Skill 规范

> 版本：v1.0-draft
> 日期：2026-05-15
> 关联：[02-Kernel-设计](02-Kernel-设计.md), [ADR-003](../decisions/ADR-003-Skill矩阵收敛与SkillGroup形态.md)

---

## 1. 两种 Skill 形态

DesignOS 支持两种 Skill 形态，通过 `SKILL.md` / `GROUP.md` 文件名区分：

| 形态 | 标识文件 | 特点 | 典型代表 |
|---|---|---|---|
| **Pipeline Skill** | `SKILL.md` | 阶段固定、顺序执行、可有条件分支 | uxeval / prd2proto / ip-design / ai-analytics / design-acceptance |
| **Skill Group** | `GROUP.md` | 子技能集合、可独立调用、支持工作流编排 + 并行 | brand-creative |

---

## 2. Pipeline Skill 规范

### 2.1 目录结构

```
skills/<skill-name>/
├── SKILL.md                    # ★ 入口文件（必需）
├── pipeline.yaml               # ★ Pipeline 配置（必需）
├── constitution.md             # ★ 评估宪法（必需，Skill 不可违反的规则）
├── reference/                  # 方法论知识库
│   ├── index.json              # 索引
│   └── m*.md                   # 方法论文档（按需加载）
├── prompts/
│   └── v<semver>/              # 带版本号的 prompts
│       └── *.md
├── templates/                  # 输出模板（Markdown / Excel）
│   └── *.md
├── examples/                   # 示例（可选）
├── eval/                       # 评估集
│   ├── golden/                 # 黄金样本
│   ├── failure/                # 失败案例
│   ├── judges/                 # 自定义评估器
│   └── promptfoo.yaml
├── tests/                      # 集成测试
│   ├── conftest.py
│   ├── fixtures/
│   └── test_*.py
└── README.md                   # Skill 文档
```

### 2.2 SKILL.md 格式

`SKILL.md` frontmatter 是 Skill 的运行时元数据真源，尤其是 `version`。loader、preflight、MCP registry 只应消费这里的版本声明。

```markdown
---
name: uxeval
version: 1.0.0
type: pipeline                  # ← 标识形态
description: 体验启发式评估 + 可用性测试，支持 Web 自动化与 Client 截图双模式
authors:
  - young@company.com
tags: [ux, evaluation, heuristics, playwright]

requires:
  kernel: ">=1.0.0,<2.0.0"
  mcp_servers:
    - name: playwright-driver
      builtin: true             # 内置（DesignOS 维护）
      requires_external:
        - command: "playwright --version"
          install_hint: "pip install playwright && playwright install chromium"
          required_when: "mode == 'web'"
    - name: heuristic-engine
      builtin: true
    - name: pdf-parser
      builtin: true
    - name: excel-builder
      builtin: true
    - name: image-analyzer
      builtin: true

  models:
    primary: claude-opus-4-7
    fallback: deepseek-v3

modes:
  - id: web
    label: "Web 应用（提供 URL + 账号密码）"
    requires:
      env: [APP_BASE_URL, APP_USERNAME, APP_PASSWORD]
  - id: client
    label: "客户端应用（提供截图）"
    requires:
      directory: [inputs/screens/]

inputs:
  - name: prd_file
    type: file
    formats: [pdf, docx, md]
    required: true
  - name: scope_md
    type: file
    formats: [md]
    required: true

outputs:
  - id: journey_map
    type: user_journey
    format: markdown
  - id: task_checklist_full
    type: task_checklist
    format: markdown
  - id: issue_report
    type: issue_report
    format: xlsx
  - id: html_report
    type: html_report
    format: html
  - id: evidence_pack
    type: evidence_pack
    format: directory

upstream_refs:                  # 可选：消费上游 Skill 产物
  - skill: ai-analytics
    output_type: design_strategy
    inject_as: competitive_context
    required: false
---

# UXEval Skill

## When to use this skill
（Markdown 正文，模型/用户阅读）

## How it works
...
```

### 2.3 pipeline.yaml 格式

`pipeline.yaml` 只描述 stage graph，不应再声明独立运行时 `version`；否则会和 `SKILL.md` 形成多真源。

```yaml
name: uxeval-pipeline

stages:
  - id: prd-understanding
    type: llm
    prompt: prompts/v1.0.0/01-prd-understanding.md
    inputs: [prd_file, scope_md]
    outputs: [modules, roles, key_tasks]
    knowledge: [reference/m01-需求理解.md]

  - id: principle-mapping
    type: llm
    prompt: prompts/v1.0.0/02-principle-mapping.md
    inputs: [scope_md]
    outputs: [principles]
    knowledge: [reference/m02-启发式原则.md]

  - id: journey-modeling
    type: llm
    prompt: prompts/v1.0.0/03-journey-modeling.md
    inputs: [modules, roles, key_tasks]
    outputs: [journey_map, journey_stages]
    checkpoint:
      id: C1
      message: "请确认用户旅程是否准确"
      allow: [continue, modify, supplement]

  - id: task-generation
    type: llm
    prompt: prompts/v1.0.0/04-task-generation.md
    inputs: [journey_map, principles]
    outputs: [task_checklist_full, task_checklist_lite]
    checkpoint:
      id: C2

  # ★ 模式分支：仅 web 模式执行
  - id: script-generation
    type: llm
    only_when: mode == "web"
    prompt: prompts/v1.0.0/05a-script-generation.md
    inputs: [task_checklist_lite]
    outputs: [evaluation_script]

  - id: web-automation
    type: tool
    only_when: mode == "web"
    mcp_server: playwright-driver
    mcp_tool: run_evaluation
    inputs: [evaluation_script]
    outputs: [screenshots, dom_data, automated_eval_trace]

  # ★ 模式分支：仅 client 模式执行
  - id: screenshot-loading
    type: tool
    only_when: mode == "client"
    mcp_server: image-analyzer
    mcp_tool: load_and_analyze
    inputs: [screenshots_dir]
    outputs: [screenshots, image_analysis]

  # ★ 后续共用
  - id: heuristic-detection
    type: tool
    mcp_server: heuristic-engine
    mcp_tool: detect
    inputs: [screenshots, principles, task_checklist_lite]
    outputs: [raw_issues]

  - id: issue-attribution
    type: llm
    prompt: prompts/v1.0.0/06-issue-attribution.md
    inputs: [raw_issues, journey_map, principles]
    outputs: [issues]
    checkpoint:
      id: C3

  - id: report-generation
    type: tool
    mcp_server: excel-builder
    mcp_tool: build_issue_report
    inputs: [issues, journey_map, principles]
    outputs: [issue_report, html_report, evidence_pack]

memory:
  read:
    - "organization.uxeval.golden_samples"
    - "organization.uxeval.failure_cases"
  write:
    - "project.uxeval.{run_id}"

constitution: constitution.md
```

### 2.4 constitution.md 格式

```markdown
# UXEval 评估宪法

以下 7 条规则是不可违反的硬约束。任何违反都会导致 stage 输出被拒。

1. **每条问题必须绑定证据**：evidence_refs 不可为空
2. **不输出敏感信息**：账号、密码、真实姓名、内部 URL
3. **严重等级必须在合法枚举内**：critical / major / minor / suggestion
4. **不把功能存在与否当作主要体验问题**：功能缺失记为产品问题不是体验问题
5. **建议方案必须可执行**：说清楚改什么、改成什么、为什么
6. **问题描述必须包含用户影响**：不只是"按钮丑"，要写"用户找不到下一步操作"
7. **当 PRD 与实现冲突时**：必须标明基准来源（PRD / 截图 / 推断）
```

---

## 3. Skill Group 规范（brand-creative 专用）

### 3.1 目录结构

```
skills/<group-name>/
├── GROUP.md                    # ★ 技能组说明（必需）
├── workflows/                  # 预定义工作流
│   └── *.yaml
├── skills/                     # 子 Skill 列表
│   └── <sub-skill>/
│       ├── SKILL.md            # 子 Skill 入口（每个子 Skill 是迷你 Pipeline）
│       ├── prompt.md
│       └── ...
├── shared/                     # Group 内共享资源
│   ├── reference/
│   └── templates/
├── eval/
└── README.md
```

### 3.2 GROUP.md 格式

```markdown
---
name: brand-creative
version: 1.0.0
type: group                     # ← 标识为 Skill Group
description: 品牌创意全流程，13+ 子技能，可独立调用 / 工作流 / 并行
authors:
  - young@company.com

requires:
  kernel: ">=1.0.0,<2.0.0"
  mcp_servers:
    - name: image-analyzer
    - name: image-prompt-gen
    - name: methodology-advisor
    - name: competitor-scraper
    - name: excel-builder

sub_skills:                     # ★ 子 Skill 注册表
  - id: deep-demand-exploration
    path: skills/deep-demand-exploration/SKILL.md
    tier: T1
  - id: brand-asset-audit
    path: skills/brand-asset-audit/SKILL.md
    tier: T1
  - id: competitor-spectrum-analyzer
    path: skills/competitor-spectrum-analyzer/SKILL.md
    tier: T2
  - id: cis-auditor
    path: skills/cis-auditor/SKILL.md
    tier: T2
  # ... 共 13+ 子 Skill

workflows:
  - id: full-T1-to-T8
    file: workflows/full-T1-to-T8.yaml
    description: 全流程（13 子技能顺序）
  - id: quick-audit
    file: workflows/quick-audit.yaml
    description: T1+T2 快速审计
  - id: creative-only
    file: workflows/creative-only.yaml
    description: T5+T6 仅创意输出
---

# Brand Creative Skill Group

调用方式：

```bash
# 单技能
designos run brand-creative:competitor-spectrum-analyzer

# 工作流
designos run brand-creative --workflow full-T1-to-T8

# 并行
designos run brand-creative --parallel \
  competitor-spectrum-analyzer cis-auditor brand-house-deconstructor
```
```

### 3.3 workflow.yaml 格式

```yaml
# skills/brand-creative/workflows/full-T1-to-T8.yaml
name: full-T1-to-T8
description: 全流程：T1 需求勘探 → T8 物料交付

steps:
  # T1: 顺序执行两个子技能
  - type: sequential
    sub_skills:
      - deep-demand-exploration
      - brand-asset-audit
    on_failure: abort

  # T2: 5 个分析任务并行（互不依赖，可并发跑省时间）
  - type: parallel
    sub_skills:
      - competitor-spectrum-analyzer
      - cis-auditor
      - brand-house-deconstructor
      - social-content-analyzer
      - opportunity-gap-analyzer
    on_failure: continue          # 单个失败不影响其他

  # T3: 顺序
  - type: sequential
    sub_skills:
      - aipl-strategy-mapper
      - market-positioning-map

  # T4-A
  - type: sequential
    sub_skills:
      - opportunity-gap-analyzer  # 复用 T2 的结果

  # T5: 创意概念
  - type: sequential
    sub_skills:
      - uso-creative-directions
      - three-step-reference

  # T4-B
  - type: sequential
    sub_skills:
      - visual-consistency-checker
      - three-step-reference

  # T6: 多版本输出
  - type: sequential
    sub_skills:
      - variant-generator

  # T7: 评估
  - type: sequential
    sub_skills:
      - multi-dim-design-evaluator
      - visual-consistency-checker

  # T8: 交付
  - type: sequential
    sub_skills:
      - deliverable-generator
```

---

## 4. 子 Skill 规范（Skill Group 内）

每个子 Skill 是一个迷你 Pipeline Skill，目录结构与普通 Pipeline Skill 一致，但通常只有 1-2 个 stage：

```
skills/brand-creative/skills/competitor-spectrum-analyzer/
├── SKILL.md                    # 子 Skill 入口
├── prompt.md                   # 单 Prompt 即可
├── templates/                  # 可选
└── examples/                   # 可选
```

子 Skill 的 SKILL.md 简化版：

```markdown
---
name: competitor-spectrum-analyzer
parent: brand-creative          # ★ 标识属于哪个 Group
version: 1.0.0
type: pipeline
description: 竞品三层梯度自动划分与维度定义

inputs:
  - name: competitor_list
    type: list[string]
    required: true
  - name: industry
    type: string
    required: true

outputs:
  - id: spectrum
    type: comparison_matrix
    format: markdown
---

# Competitor Spectrum Analyzer

按竞品的核心、相关、跨界三层划分...
```

---

## 5. Skill 扩展（新增 Skill 流程）

### 5.1 用脚手架创建

```bash
# 创建 Pipeline Skill
designos skill create my-skill --type pipeline

# 创建 Skill Group
designos skill create my-group --type group

# 在已有 Group 中创建子 Skill
designos skill create my-sub --parent my-group
```

### 5.2 上线 checklist

参见 [04-MCP-Server-规范.md](04-MCP-Server-规范.md) 后续会链接的 Skill 上线 checklist。

核心要求：
- [ ] SKILL.md 含完整 frontmatter
- [ ] pipeline.yaml 或 GROUP.md 完整
- [ ] constitution.md 至少 3 条不可违反规则
- [ ] reference/ 至少 1 份方法论文档
- [ ] prompts/v0.1.0/ 所有 stage prompt 就绪
- [ ] eval/golden/ 至少 2 个样本
- [ ] tests/ 集成测试通过
- [ ] README.md 含使用示例

---

## 6. Skill 间通信契约

详见 [05-数据契约.md](05-数据契约.md)（待写）和 [schemas/output-types.md](../schemas/output-types.md)。

核心规则：
- 上游 Skill 通过 OutputType 声明产物类型
- 下游 Skill 通过 `upstream_refs` 声明可消费的类型
- Kernel 自动匹配并询问用户是否注入
