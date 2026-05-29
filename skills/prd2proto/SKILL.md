---
name: prd2proto
version: 0.1.0
type: pipeline
description: PRD → 可交互前端代码。当用户说 PRD 转原型、原型生成、PRD 转代码、prd2proto 时使用。支持三种保真度档位：pm（PM 演示用低保真）/ designer-spec（设计师高保真原型）/ designer-dsl（DSL + 组件库 + 设计规范，生产级代码）。
requires:
  kernel: ">=1.0.0,<2.0.0"
  mcp_servers:
    - name: pdf-parser
      builtin: true
    - name: frontend-codegen
      builtin: true
    - name: figma-mcp
      builtin: false
      required_when: 'mode == "designer-dsl"'
      requires_external:
        - command: "figma-mcp --version"
          install_hint: "Install figma-mcp from the community MCP marketplace, or provide DSL data via mastergo-mcp instead."
          required_when: 'mode == "designer-dsl"'
    - name: mastergo-mcp
      builtin: false
      required_when: 'mode == "designer-dsl"'
      requires_external:
        - command: "mastergo-mcp --version"
          install_hint: "Install mastergo-mcp from the official MasterGo plugin store, or provide DSL data via figma-mcp instead."
          required_when: 'mode == "designer-dsl"'
modes:
  - id: pm
    label: "PM 模式（PRD → 低保真演示原型）"
  - id: designer-spec
    label: "设计师模式（PRD + design-spec.md → 高保真原型）"
    requires:
      file: [inputs/design-spec.md]
  - id: designer-dsl
    label: "设计师生产模式（DSL + design-spec.md + 组件库 → 生产代码）"
    requires:
      file: [inputs/design-spec.md, inputs/component-lib.yaml]
      env: [DSL_SOURCE]   # "figma" or "mastergo"
inputs:
  - name: prd_file
    type: file
    formats: [pdf, docx, md]
    required: true
  - name: scope_md
    type: file
    formats: [md]
    required: true
  - name: design_spec_md
    type: file
    formats: [md]
    required: false   # required runtime by stage gate when mode == designer-spec/designer-dsl
  - name: dsl_file
    type: file
    formats: [json]
    required: false   # required runtime by stage gate when mode == designer-dsl
  - name: component_lib_ref
    type: file
    formats: [yaml]
    required: false   # required runtime by stage gate when mode == designer-dsl
outputs:
  - id: prototype_code
    type: prototype_code
    format: directory
  - id: frontend_code
    type: frontend_code
    format: directory
  - id: design_tokens
    type: design_tokens
    format: json
  - id: information_architecture
    type: information_architecture
    format: markdown
  - id: component_spec
    type: component_spec
    format: markdown
---

# prd2proto — PRD 转原型代码

## 触发条件

用户说出以下任一意图时立即启动：
- 自然语言：「PRD 转原型」「PRD 转代码」「生成原型代码」「我想把 PRD 变成可运行的前端」
- 快捷命令：`/prd2proto`、`/prd2proto pm`、`/prd2proto designer-spec`、`/prd2proto designer-dsl`

## Step 0：模式选择

回复用户：

```
我将用 prd2proto 把 PRD 转成前端代码。请确认：

1. 哪种保真度？
   - pm：PRD → 演示原型（最快，给 PM 看效果用）
   - designer-spec：PRD + design-spec.md → 高保真原型（设计师能用）
   - designer-dsl：DSL（Figma/MasterGo）+ design-spec.md + 组件库 → 生产代码

2. 必需输入：
   - PRD 文档（.md / .pdf / .docx）
   - 评估范围（几句话：目标产品、核心模块）

3. designer-spec / designer-dsl 模式额外需要：
   - design-spec.md（团队设计约定）
   - DSL 数据（仅 designer-dsl，需要先在 Figma/MasterGo 装对应 MCP 插件）
   - 本地组件库引用（仅 designer-dsl）

4. 目标框架：React 还是 Vue？

准备好了吗？
```

不要跳过模式选择直接开始。

## Step 0.5：环境预检（Preflight）

预检规则跟 uxeval 一样，但 prd2proto 关注的依赖不同：

- **PDF 解析**（必需）：用户提供 PDF PRD 时
- **frontend-codegen MCP**（必需，当前为 Mock 实现）
- **figma-mcp / mastergo-mcp**（仅 designer-dsl 模式）：用户必须自己装好其中一个

预检失败时给出清单，等用户安装后复检。

## 输入要求

### 必需（所有模式）
- PRD 文件（pdf/docx/md）
- scope.md（目标产品 + 核心模块说明）

### 仅 designer-spec / designer-dsl
- design-spec.md（团队设计约定。若没有，spec-generation stage 会帮用户生成首版）

### 仅 designer-dsl
- DSL 文件（从 figma-mcp / mastergo-mcp 拉取）
- 本地组件库引用（component-lib.yaml，列出可复用组件）
- Design.md（团队约定，优先级高于上述所有）

## 输出产物

### 主要产物
1. **prototype_code**（目录）：可运行的前端项目骨架
2. **frontend_code**（目录，仅 designer-dsl）：生产可用代码
3. **design_tokens**（json，仅 designer-spec/dsl）：颜色 / 字号 / 间距 token
4. **information_architecture**（markdown）：信息架构 + 页面拓扑
5. **component_spec**（markdown）：组件规格说明

## 4 条代码宪法（来自 ADR-003）

⚠️ designer-dsl 模式必须满足。pm 模式放宽前 3 条但保留状态覆盖。

1. ❌ **不得硬编码颜色 / 字号 / 间距** → 必须用 Token 变量
2. ❌ **不得自行编写基础组件** → 必须复用本地组件库（AntDesign Vue / Element Plus / 自定义库）
3. ❌ **不得跳过状态覆盖** → 默认 / 悬停 / 按下 / 聚焦 / 禁用 / 加载 / 错误 七种状态
4. ❌ **不得忽略 Design.md 约束** → 团队约定优先级最高

constitution.md 详细规则见配套文件。

## Pipeline 概览

7 个 stage（按 archetype generation）：

```
Stage 1  prd-understanding         (LLM)
Stage 2  design-analysis           (LLM, Checkpoint C1)
Stage 3a spec-generation           (LLM, only_when: designer-spec)
Stage 3b dsl-fetch                 (Tool, only_when: designer-dsl)
Stage 4  token-extraction          (Tool, only_when: designer-spec/designer-dsl)
Stage 5  code-generation           (Tool)
Stage 6  review-gate               (LLM, Checkpoint C4 + Gate QG_REVIEW)
```

详见 pipeline.yaml。

## 当前实装阶段

- ✅ pm 模式（端到端跑通 = P1 batch 当前）
- ⏳ designer-spec 模式（P2 batch）
- ⏳ designer-dsl 模式（P3 完成 frontend-codegen 真 MCP 后才跑得起来）

详见 `docs/plans/2026-05-29-prd2proto-implementation-plan.md`。

## 已知边界

1. **frontend-codegen 当前是 Mock**：generate_code 返回固定 React/Vue 项目骨架，不真做 DSL 解析。P3 batch 实装真逻辑。
2. **designer-dsl 模式依赖外部 MCP**：figma-mcp 或 mastergo-mcp 必须先装。不装的话 Preflight 会拦。
3. **review-gate 当前是 LLM 软审查**：4 条代码宪法用 prompt 自我检查。P3 完成后改静态扫描硬约束。

## 参考

- Constitution: `constitution.md`
- Pipeline: `pipeline.yaml`
- Templates: `templates/`
- Reference: `reference/`
