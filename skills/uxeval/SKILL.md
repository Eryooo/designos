---
name: uxeval
version: 1.0.0
type: pipeline
description: 体验启发式评估 + 可用性测试，支持 Web 自动化与 Client 截图双模式
authors:
  - young@company.com
tags: [ux, evaluation, heuristics, playwright, journey, accessibility]

requires:
  kernel: ">=1.0.0,<2.0.0"
  mcp_servers:
    - name: playwright-driver
      builtin: true
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
    label: "客户端应用（提供截图目录）"
    requires:
      directory: [inputs/screens/]

inputs:
  - name: prd_file
    type: file
    formats: [pdf, docx, md]
    required: true
    path_hint: inputs/prd.pdf
  - name: scope_md
    type: file
    formats: [md]
    required: true
    path_hint: inputs/scope.md
  - name: principles_md
    type: file
    formats: [md]
    required: false
    path_hint: inputs/principles.md
  - name: screenshots_dir
    type: directory
    required: false
    path_hint: inputs/screens/
    required_when: "mode == 'client'"

outputs:
  - id: journey_map
    type: user_journey
    format: markdown
  - id: task_checklist_full
    type: task_checklist
    format: markdown
  - id: task_checklist_lite
    type: task_checklist
    format: markdown
  - id: issue_report
    type: issue_report
    format: xlsx
  - id: html_report
    type: issue_report
    format: html
  - id: evidence_pack
    type: evidence_pack
    format: directory

upstream_refs:
  - skill: ai-analytics
    output_type: design_strategy
    inject_as: competitive_context
    required: false
  - skill: ai-analytics
    output_type: user_persona
    inject_as: existing_personas
    required: false
---

# UXEval Skill

## When to use this skill

启动 `/uxeval` 当你需要：

- 对一个 **Web 后台 / Web 应用** 做体验启发式评估（web 模式：提供 URL + 账号密码，由 Playwright 自动化采集证据）
- 对一个 **客户端 / 移动端应用** 做体验评估（client 模式：人工提交截图集，AI 做视觉分析）
- 把高级体验设计师的评估流程标准化成「需求理解 → 旅程建模 → 任务清单 → 证据采集 → 问题归因 → 报告」的可复用工作流
- 输出可被产品 / 研发评审、可分派、可跟踪的体验问题清单（Excel + Markdown + HTML）

不适合的场景：

- **设计稿还原度验收**：用 `/design-acceptance`
- **PRD → 原型代码**：用 `/prd2proto`
- **品牌创意 / 视觉评估**：用 `/brand-creative:multi-dim-design-evaluator`

## How it works

UXEval 是一个 8 阶段 Pipeline（带 3 个用户确认点）：

```
prd-understanding ──► persona-derivation ──► scenario-derivation ──► principle-mapping
                                                                          │
                                                                          ▼
                                                                  journey-modeling [C1]
                                                                          │
                                                                          ▼
                                                                  task-generation [C2]
                                                                          │
                                              ┌───────────────────────────┴───────────────────────────┐
                                              │ mode == "web"                                          │ mode == "client"
                                              ▼                                                        ▼
                                    task-script-generation ──► web-automation               screenshot-loading
                                              │                                                        │
                                              └───────────────────────────┬───────────────────────────┘
                                                                          ▼
                                                                  heuristic-detection
                                                                          │
                                                                          ▼
                                                                  issue-attribution [C3]
                                                                          │
                                                                          ▼
                                                                  report-generation
```

### 双模式说明

| 模式 | 输入 | 自动化范围 | 适用场景 |
|---|---|---|---|
| `web` | URL + 账号密码 | Playwright 自动登录、采集截图、采集 DOM | 后台 / SaaS / 内部系统 |
| `client` | 截图目录 | LLM 多模态分析截图，无浏览器自动化 | 桌面客户端 / 移动 App / 已下线系统 |

### 三个 Checkpoint

- **C1（旅程确认）**：Agent 输出旅程地图后停下，让你确认「这个旅程是否覆盖关键用户路径」
- **C2（任务清单确认）**：拆出体验任务清单后停下，让你校准「是否偏功能测试，是否漏掉关键体验任务」
- **C3（问题清单确认）**：归因后的问题清单停下，让你确认「严重等级、归因、改进建议是否合理」

### 与上游 Skill 的衔接

如果先跑了 `/competitor-analysis`（ai-analytics），UXEval 会自动询问你是否注入：

- `design_strategy`：竞品体验对标基线
- `user_persona`：竞品分析阶段已沉淀的用户画像

注入后用于「persona-derivation」和「issue-attribution」阶段，让评估有竞品参照。

## What you get

每次跑完 UXEval（约 30-90 分钟，取决于产品复杂度），你会得到：

1. **旅程地图** `01-旅程地图.md`：用户角色 + 阶段 + 任务链路
2. **完整版任务清单** `02-任务清单-完整版.md`：给资深设计师参考
3. **简洁执行版任务清单** `03-任务清单-简洁版.md`：给中低阶设计师顺序执行
4. **问题清单 Excel** `04-问题报告.xlsx`：含截图、原则、严重等级、改进建议
5. **HTML 报告** `04-问题报告.html`：分享用
6. **证据包** `evidence/`：所有截图 + 流程文件 + 自动化 trace（仅 web 模式）

## Inputs you must prepare

放在工作区的 `inputs/` 目录下：

- `prd.pdf` 或 `prd.md`：产品需求文档
- `scope.md`：评估范围（用户提供，模板见 `templates/scope.md`）
- `principles.md`（可选）：自定义启发式原则；不提供则用 Nielsen 10 原则
- `screens/`（仅 client 模式）：截图目录

Web 模式额外需要在 `.env.local` 中：

```
APP_BASE_URL=https://...
APP_USERNAME=...
APP_PASSWORD=...
```

## Constitution

不可违反的 7 条评估宪法见 `constitution.md`。任何违反都会导致 stage 输出被拒。
