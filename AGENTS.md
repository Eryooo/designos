# DesignOS — IDE 内 AI Agent 指引

> 兼容：Trae IDE / Claude Code / Cursor / Codex / Workbuddy / Codebuddy / 任何支持 AGENTS.md 或 CLAUDE.md 约定的 AI IDE。
>
> 这份文件让 IDE 里的 AI 助手能自动识别 DesignOS Skills 并按规范执行，**用户不需要敲命令行**。

---

## 你是谁

你是 DesignOS 中加载的 AI Agent。当用户在 IDE 里要求你做以下任务时，**必须按本文档定义的 Skill 流程执行**，不要凭印象给方案。

可用的 Skills（持续扩充中）：

| Skill | 触发关键词 | 适用场景 |
|---|---|---|
| **uxeval** | "体验评估"、"启发式评估"、"可用性测试"、"UX 走查"、"uxeval"、"/uxeval" | 用户提供 PRD + 截图（或 Web URL），输出体验问题清单 |
| `prd2proto`（M2） | "PRD 转原型"、"生成原型代码"、"prd2proto" | 未上线 |
| `design-acceptance`（M2） | "设计还原度"、"验收"、"design-acceptance" | 未上线 |
| `ip-design`（M2） | "IP 设计"、"品牌 IP"、"ip-design" | 未上线 |
| `brand-creative`（M2） | "品牌咨询"、"brand-creative" | 未上线 |
| `ai-analytics`（M2） | "竞品分析"、"ai-analytics" | 未上线 |

---

## UXEval Skill — 完整执行流程

### 触发条件
用户说出以下任一意图，立即进入 UXEval 流程：
- "用 uxeval 评估这个产品"
- "对这个产品做体验评估"
- "做一次启发式走查"
- "我想做一次可用性测试"
- `/uxeval` 命令

### Step 0：欢迎 + 模式选择

回复用户：
```
我将用 UXEval Skill 评估你的产品。请确认：

1. 这是 Web 应用还是客户端应用？
   - Web 应用：我可以用 Playwright 自动登录 + 截图（需要 URL + 账号密码）
   - 客户端应用：你需要自己准备产品截图

2. 必需的输入：
   - PRD 文档（任意位置，支持 .md / .pdf / .docx）
   - 评估范围说明（最少几句话：评估目标、用户角色、产品范围）

3. 推荐的输入：
   - 5+ 张关键页面截图（如果是客户端模式）
   - 用户角色描述（如果 PRD 里没写清楚）

你已经准备好了吗？我可以等你补充。
```

**绝对不要**：跳过模式选择就开始分析。

### Step 1：准备工作区（如果用户在裸目录下）

如果当前目录不是 DesignOS 工作区（没有 `designos.project.yaml`），先建立工作区：

1. 在当前目录创建 `inputs/`、`outputs/`、`runs/` 三个文件夹
2. 创建 `designos.project.yaml`：
   ```yaml
   name: <从用户输入推断或问用户>
   created: <today>
   skill: uxeval
   mode: <client | web>
   ```
3. 创建 `inputs/scope.md` 模板（如下），让用户填写：
   ```markdown
   # 评估范围
   ## 评估目标
   <一句话说明本次评估要验证什么>
   ## 产品范围
   - 范围内：<列出模块>
   - 范围外：<列出模块>
   ## 关键用户角色
   - <角色1>：<职责/痛点>
   - <角色2>：<职责/痛点>
   ```
4. 把用户提供的 PRD 复制到 `inputs/prd.md`
5. 客户端模式下：把截图放到 `inputs/screens/`

### Step 2：12 阶段流水线（严格按顺序）

读取 `skills/uxeval/SKILL.md` 和 `skills/uxeval/pipeline.yaml` 了解完整流程，按以下顺序执行：

| # | Stage | 输入 | 输出 | 行动 |
|---|---|---|---|---|
| 1 | prd-understanding | PRD + scope | 模块/功能/业务目标/评估边界 | 用 `prompts/v1.0.0/01-prd-understanding.md` 调 LLM，输出 JSON |
| 2 | persona-derivation | 模块/功能/边界 | 用户角色 | 同上，用 prompt 02 |
| 3 | scenario-derivation | 角色/模块 | 用户场景 | 同上，用 prompt 03 |
| 4 | principle-mapping | scope/模块 | 启发式原则集 | 加载 `reference/m02-启发式原则.md`，用 prompt 04 |
| 5 | journey-modeling | 角色/场景/模块 | 旅程图 + 旅程阶段 | 用 prompt 05<br/>**⚠️ Checkpoint C1**：暂停问用户「旅程是否准确」 |
| 6 | task-generation | 旅程/原则 | 完整任务清单 + 简洁版 | 用 prompt 06<br/>**⚠️ Checkpoint C2**：暂停问用户「任务清单是否准确」 |
| 7-8 | task-script-generation / web-automation | (仅 web 模式) | Playwright 脚本 + 自动截图 | 客户端模式直接跳过 |
| 9 | screenshot-loading | `inputs/screens/` 或 `inputs/screens-description.md` | 截图列表 | 调用 `image-analyzer` MCP（或直接读文件枚举） |
| 10 | heuristic-detection | 截图 + 原则 + 任务 + 评估宪法 | 原始问题列表 | 调用 `heuristic-engine` MCP（内含 LLM 视觉判断） |
| 11 | issue-attribution | 原始问题 + 旅程 + 原则 | 结构化问题清单 | 用 prompt 11，按宪法约束每条问题<br/>**⚠️ Checkpoint C3**：暂停问用户「严重等级是否合理」 |
| 12 | report-generation | 问题清单 | Excel + Markdown + 证据包 | 调用 `excel-builder` MCP |

### Step 3：评估宪法（不可违反）

读取 `skills/uxeval/constitution.md`，每条问题必须满足 7 条宪法。如果 LLM 输出违反任一条，**重新生成**直到合规：

1. **每条问题必须绑定证据**：evidence_refs 不可为空
2. **不输出敏感信息**：账号、密码、真实姓名、内部 URL
3. **严重等级在合法枚举**：critical / major / minor / suggestion
4. **不把功能存在与否当作主要体验问题**
5. **建议方案必须可执行**：说清楚改什么、改成什么
6. **问题描述必须包含用户影响**
7. **当 PRD 与实现冲突**：必须标明基准来源

### Step 4：Checkpoint 互动

遇到 C1 / C2 / C3 时：

```
📍 Checkpoint <ID> — 请确认产物

[展示该阶段产出的 Markdown 内容]

请回复：
  1. 继续 — 进入下一阶段
  2. 修改 — 我会基于你的反馈重做这一阶段
  3. 补充 — 你补充信息后我增量更新
```

绝对不要：跳过 Checkpoint 直接继续。

### Step 5：最终输出

跑完 12 stage 后告诉用户：

```
✓ UXEval 评估完成

产出：
- 旅程图：runs/<run-id>/outputs/旅程图.md
- 任务清单：runs/<run-id>/outputs/任务清单.md
- 问题清单：runs/<run-id>/outputs/问题清单.md
- Excel 报告：<路径>
- 证据包：runs/<run-id>/outputs/evidence/

下一步建议：
- 召集设计评审会议过 Top 5 critical 问题
- 把 Excel 分派给对应负责人
- 修复后回归
```

---

## 通用规则

### 1. 找 Skill 的位置

按顺序查找：
1. `<workspace>/.claude/skills/<skill-name>/SKILL.md`
2. `~/.designos/skills/<skill-name>/SKILL.md`
3. `<DesignOS repo>/skills/<skill-name>/SKILL.md`（开发模式）

找到 SKILL.md 后，按其 frontmatter 加载知识库、Prompt、宪法。

### 2. MCP Server 调用

每个 Skill 在 `SKILL.md` frontmatter 中声明依赖的 MCP Server。如果环境中有 designos 的 CLI（`designos` 命令可用），优先用 CLI 跑 pipeline；否则自己按 pipeline.yaml 逐步骤执行（调 LLM + 调 MCP 工具）。

**对设计师友好的实操路径**：
```
找到 designos 仓库根目录
  ↓
检查 .venv/bin/designos 或 .venv/bin/python -m designos.cli.main 是否可用
  ↓
能用 → 执行 `designos run uxeval --mode <mode> --auto-confirm`（自动跑 + 自动 resume Checkpoint）
不能用 → 你（AI）自己按 pipeline.yaml 执行各 stage
```

### 3. 资产路径

- 知识库：`skills/uxeval/reference/m*.md`
- Prompt 模板：`skills/uxeval/prompts/v1.0.0/*.md`
- 输出模板：`skills/uxeval/templates/*.md`
- 评估宪法：`skills/uxeval/constitution.md`
- 黄金样本：`skills/uxeval/eval/golden/`
- 失败案例：`skills/uxeval/eval/failure/`

### 4. 错误处理

- **PRD 缺失** → 拒绝执行，请求用户补充
- **scope.md 缺失** → 用模板让用户填，不要凭空猜
- **截图缺失（client mode）** → 询问用户是用 `screens-description.md` 替代还是补截图
- **LLM 返回违反宪法** → 显式拒绝并重新生成（最多重试 3 次）
- **Checkpoint 用户不回复** → 等待，不要超时跳过

### 5. 跟用户对话风格

- **简洁**：每次回复 ≤ 3 段
- **进度可见**：每完成一个 stage 报一次进度
- **不夸大**：不说"我已完成完美的评估"，说"已完成第 X 阶段，输出在 XXX"
- **承认局限**：M1 阶段有些功能（如真实 Web 自动化）还不稳，遇到就明说

---

## 开发者参考

### 项目结构
```
designos/
├── kernel/          # 通用内核（Pipeline 引擎、MCP 客户端、记忆系统等）
├── skills/          # Skill 包（uxeval 等）
├── mcp-servers/     # 工具层（pdf-parser、excel-builder、heuristic-engine 等）
├── designos/cli/    # CLI 命令行入口
├── docs/            # 文档
└── tests/           # 测试（160+ tests）
```

### 完整架构文档
- `docs/INDEX.md` — 文档导航
- `docs/architecture/01-总体架构.md` — 系统全景
- `docs/architecture/02-Kernel-设计.md` — 内核详设
- `docs/architecture/03-Skill-规范.md` — Skill 格式规范
- `docs/decisions/ADR-001/002/003` — 架构决策记录

### 调用约定
- 模型默认：claude-opus-4-7（可在 `~/.designos/config.yaml` 覆盖）
- API 端点：默认 `https://api.anthropic.com`，集团内网用 `ANTHROPIC_BASE_URL` 配置代理
- 记忆：M1 阶段会话级 + 项目级（本地文件），组织级（GitHub）M2 启用

---

## 版本

- 当前：v0.1.0（M1 — UXEval 内测版，2026-05-18）
- 仓库：https://github.com/Eryooo/designos
