---
name: prd2proto
version: 0.3.0-capability-pilot
type: pipeline
status: capability-pilot
runtime_reliability: llm_assisted
enterprise_ready: false
description: |
  PRD → 设计推理资产 → 受约束的原型代码。基于 Senior Designer Work Paradigm Engine。
  
  Pipeline v2 (17 stages):
  - Stage 01-12: 设计推理资产生成 (design objectives, user tasks, journey, IA, page flow, component strategy, state matrix, interaction rules, etc.)
  - Stage 13: 设计规范生成 (design-spec.md)
  - Stage 14: Token提取 (框架级占位)
  - Stage 15: 约束代码生成 (框架级占位)
  - Stage 16: 可追溯性生成 (traceability map)
  - Stage 17: 专业差距评估 (professional gap report)
  
  当前状态 (2026-06-10):
  - ✅ Pipeline架构: v2主线 (pipeline.yaml), v1保留 (pipeline.v1.yaml)
  - 🔄 Prompts: 框架完成, 资深设计师逻辑补全中
  - 🔄 LLM Execution: 从mock向真实执行迁移中
  - 🔄 Schema Gates: 接入中
  - ❌ Code Generation: 框架级占位 (非本轮P0)
  - ❌ Production Ready: 否
  
  本版本不支持 designer-dsl 模式,仅保留 pm / designer-spec。
requires:
  kernel: ">=1.0.0,<2.0.0"
  mcp_servers:
    - name: pdf-parser
      builtin: true
    - name: frontend-codegen
      builtin: true
      required_when: 'mode == "designer-dsl"'   # 仅 dsl-fetch stage 用；pm/designer-spec 的 token/code 由 LLM 手写，不依赖它
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
  - id: designer-dsl
    label: "设计师生产模式（DSL + design-spec.md + 组件库 → 生产代码）"
    requires:
      file: [inputs/design-spec.md, inputs/component-lib.yaml]
      env: [DSL_SOURCE]
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
    required: false   # spec-generation stage 会按需生成
  - name: dsl_file
    type: file
    formats: [json]
    required: false   # required runtime when mode == designer-dsl
  - name: component_lib_ref
    type: file
    formats: [yaml]
    required: false   # required runtime when mode == designer-dsl
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

- 自然语言：「PRD 转原型」「PRD 转代码」「生成原型代码」「我想把 PRD 变成可运行的前端」
- 快捷命令：`/prd2proto`、`/prd2proto pm`、`/prd2proto designer-spec`、`/prd2proto designer-dsl`

## Progress Contract（强制约束）

LLM 在执行 prd2proto pipeline 时必须遵守：

1. 每个 stage 开始前发一行：

   `⏳ Stage N: <name> — <一句话说在做什么>`

2. 每个 stage 完成后发一行：

   `✅ Stage N: <name> → <产物路径或摘要>`

3. 长操作（npm install / build / 写 5+ 文件）开始前：

   `⏳ <动作>（预计 X 秒，后台跑，不阻塞）`

4. 写 5+ 文件时中间插入：

   `📝 正在写 <文件名>...（N/M）`

5. 两行 progress 之间不允许超过 60 秒沉默。

6. 每完成一个 stage，给用户一个"打断锚点"提示：

   `如要改 [上一步产物] 现在喊停最低成本`

违反 Progress Contract 视为 skill 实施错误。

## Checkpoint Behavior

prd2proto 默认运行环境是聊天模式（Claude Code / Trae / Cursor 等）。

**聊天模式（默认）**：
- C1/C2/C3：用 ≤3 行摘要展示决策点 + 1 行默认决定 + 继续往下跑
  示例：

  > 信息架构 5 页 + 12 组件已建好。我把组件库默认为 antd@5（理由：React 后台首选）。
  > 如要换 element-plus / radix，现在告诉我。

- C4：始终展示生成代码 + 4 条宪法审查报告。`violations.count == 0` → 默认 continue；`> 0` → 真停下让用户决策
- QG_REVIEW：仅 `violations.count > 0` 时触发，强制停下

**有 orchestrator 模式（未来 IDE 集成）**：
- 按 pipeline.yaml 的 checkpoint 弹选项 UI

不允许在 C1/C2/C3 死等用户输入。用户已经看见摘要，没有反应就是默认同意。

## design-spec.md 获取策略

design-spec.md 不是必填项。按优先级：

1. **用户提供**（在 inputs/ 下放了 design-spec.md）：
   → 跳过 spec-generation stage 的模板匹配，直接读用户的

2. **用户没提供**（默认）：
   → 进 spec-generation stage：
     a. 分析 PRD 产品定位（ToB/ToC、行业、用户画像、气质关键词）
     b. 从 `reference/design-templates/` 模板库匹配最合适的（见 `prompts/03a-spec-generation.md`）
     c. 基于选中的模板 + PRD 特征微调
     d. 输出 design-spec.md 并告知用户："我选了 [linear] 风格，因为 ..."

3. **用户看了不满意**：
   → 重新匹配，可参考用户提到的 URL（如 coze.cn）或主动选另一个模板

## Loading Discipline

不要预先加载所有 prompt + reference。按需加载：

- 进入 stage N 前才 Read `prompts/N-*.md`
- 进入 stage N 前才 Read 对应的 `reference/mN-*.md`
- `design-templates/` 仅在 spec-generation stage 才扫描
- `prompts/05-code-generation.md` 仅在 stage 5 才加载

启动阶段（mode 确认 + preflight）只读这份 SKILL.md + constitution.md。

## Output Path Convention

```
output_root = <cwd>/prd2proto-out/<YYYYMMDD>-<short-product-slug>/

prd2proto-out/<run_id>/
├── stages/                          # 各 stage 中间产物
│   ├── 01-prd-understanding.json
│   ├── 02-information-architecture.md
│   ├── 02-component-spec.md
│   ├── 03a-design-spec.md
│   ├── 04-design-tokens.json
│   ├── 04-tokens.css
│   └── 06-review-report.md
├── prototype/                       # 可运行项目
│   └── (package.json + src/...)
└── reports/
    ├── review-report.md
    └── constitution-violations.json
```

`run_id` 格式：`YYYYMMDD-<slug>`，slug 来自 PRD 产品名小写连字符化（如 `xiaofeigun` / `task-platform`）。

## Step 0：模式与输入识别

- 用户消息已含模式（如 `/prd2proto designer-spec`）+ PRD 路径 → 直接进 preflight，不重复打印模板。
- 缺信息时一句话问缺什么（如："我跑哪种保真度？PRD 文件路径？"）。
- 不要把 mode 选择菜单完整复述给用户 —— command-message 已经展示过了。

## Step 0.5：Preflight（模式驱动）

按当前 mode 决定要查什么：

| mode | 必查 | 可选 |
|---|---|---|
| pm | node ≥ 18，包管理器（pnpm / yarn / npm 任一） | — |
| designer-spec | 同上 | — |
| designer-dsl | 同上 + figma-mcp 或 mastergo-mcp 任一 | component-lib.yaml |
| PRD 是 .pdf | 同上 + pdf-parser 可用 | — |

全部就绪 → 静默通过，进 Stage 1。
有缺失 → 提醒安装 + 等用户确认 + 复检。

## 实装现状

| Stage | 类型 | 实装 |
|---|---|---|
| 1 prd-understanding | LLM | ✅ 真业务 prompt |
| 2 design-analysis | LLM | ✅ 真业务 prompt |
| 3a spec-generation | LLM | ✅ 从模板库选 + 微调 |
| 3b dsl-fetch | tool | ❌ 仅 designer-dsl，需外部 figma-mcp / mastergo-mcp |
| 4 token-extraction | LLM | ✅ 真业务 prompt（W3C DTCG 格式） |
| 5 code-generation | LLM | ✅ 真业务 prompt（钉死项目结构 / 状态管理 / mock） |
| 6 review-gate | LLM | ✅ 4 条代码宪法软审查 |
| 7 liveness-check | LLM | ⚠️ LLM 引导用户跑 npm install/dev（frontend-codegen Mock 没有 launch_preview tool；待真 MCP 实装后改 tool） |

注意：旧版 yaml 把 stage 3b/4/5 标 `type: tool` 是误导性表述（依赖的 MCP 是 mock，实际靠 LLM 手写），本版已修正。

## 4 条代码宪法（来自 ADR-003）

⚠️ designer-dsl 模式必须满足。pm 模式放宽前 3 条但保留状态覆盖。

1. ❌ **不得硬编码颜色 / 字号 / 间距** → 必须用 Token 变量
2. ❌ **不得自行编写基础组件** → 必须复用本地组件库（AntDesign / Element Plus / 自定义库）
3. ❌ **不得跳过状态覆盖** → 默认 / 悬停 / 按下 / 聚焦 / 禁用 / 加载 / 错误 七种状态
4. ❌ **不得忽略 Design.md 约束** → 团队约定优先级最高

详细规则与白名单见 `constitution.md`。

## Pipeline 概览

8 个 stage，每种模式实际跑 7 个：

```
Stage 1  prd-understanding         (LLM)
Stage 2  design-analysis           (LLM, Checkpoint C1)
Stage 3a spec-generation           (LLM, only_when: mode != "designer-dsl", Checkpoint C2)
Stage 3b dsl-fetch                 (Tool, only_when: mode == "designer-dsl")
Stage 4  token-extraction          (LLM, Checkpoint C3)
Stage 5  code-generation           (LLM)
Stage 6  review-gate               (LLM, Checkpoint C4 + Gate QG_REVIEW)
Stage 7  liveness-check            (LLM, dev server 起来才算闭环)
```

详见 `pipeline.yaml`。

## 已知边界

1. **frontend-codegen 当前是 Mock**：MCP 仅做 fetch_dsl / extract_tokens / map_components / generate_code 的 mock skeleton。本版 stage 4/5 改为 LLM 主导（不再调 mock 工具）。
2. **liveness-check 没有 launch_preview tool**：本版 stage 7 用 LLM 引导用户在终端跑 `npm run dev`，回报 URL。待 frontend-codegen 真 MCP 实装后可改 `type: tool`。
3. **designer-dsl 模式依赖外部 MCP**：figma-mcp 或 mastergo-mcp 必须先装，preflight 会拦。
4. **review-gate 当前是 LLM 软审查**：4 条代码宪法用 prompt 自我检查。P3 完成后可加静态扫描硬约束。

## 参考

- Constitution: `constitution.md`
- Pipeline: `pipeline.yaml`
- Templates: `templates/`
- Reference: `reference/`
- Design templates library: `reference/design-templates/`
