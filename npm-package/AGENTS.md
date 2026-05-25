# DesignOS — IDE 内 AI Agent 指引

> 兼容：Trae IDE / Claude Code / Cursor / Codex / Workbuddy / Codebuddy / 任何支持 AGENTS.md 或 CLAUDE.md 约定的 AI IDE。
>
> 这份文件让 IDE 里的 AI 助手能自动识别 DesignOS Skills 并按规范执行，**用户不需要敲命令行，不需要单独配 API Key**。

---

## 执行原则（重要）

**只有一套执行流程**，无论用户从 IDE 对话框还是 terminal 触发，做的事情完全一样：你（AI）是执行主体，按本文档定义的流水线分步执行；需要工具时（PDF 解析、浏览器自动化、Excel 生成等）就调用对应工具或 MCP。

**关键约束**：

- 用户在对话框说 `/uxeval`，你**直接用当前配置的模型**（Claude / GPT / DeepSeek 等）按 `skills/uxeval/pipeline.yaml` 逐 stage 执行。
- 你需要的所有 prompt 模板、知识库、评估宪法都在 skills/uxeval/ 全局位置（用户已通过 install 注入），直接读文件即可。
- **不要要求用户重复配 API Key**（IDE/CLI 已经配过了）。
- **不要要求用户手动 mkdir / 填空模板 / 跑 designos init**——所有目录、配置、scope 推断都由你自动完成。
- 需要外部工具时（如 Web 模式的 Playwright）才提示用户安装；客户端模式（M1 主路径）不需要任何额外依赖。

---

## 快捷命令

不需要长指令。用户输入以下任意命令立即触发对应 Skill：

| 命令 | 等价于 |
|---|---|
| `/uxeval` 或 `/uxeval client` | 用 UXEval 客户端模式评估当前目录的产品 |
| `/uxeval web <URL>` | 用 UXEval Web 模式评估指定 URL |
| `/uxeval resume` | 恢复中断的评估 |
| `/uxeval --help` | 显示 UXEval 帮助 |
| `/skills` | 列出所有可用 Skills |
| `/designos init` | 在当前目录初始化 DesignOS 工作区 |

**识别规则**（适用于 Trae/Codex/Workbuddy/Codebuddy 等）：
- 用户消息**以 `/` 开头**时，按命令解析
- 否则按自然语言意图匹配（见下方 Skills 表）

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
- 自然语言：「用 uxeval 评估这个产品」「对这个产品做体验评估」「做一次启发式走查」「我想做一次可用性测试」
- 快捷命令：`/uxeval`、`/uxeval client`、`/uxeval web <URL>`

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

### Step 1：自动初始化工作区（AI 全自动）

**核心原则**：用户只需要丢一个 PRD（或粘贴 PRD 内容），AI 自动完成所有目录创建、文件搬运、配置生成、scope 推断。**绝对不要让用户从空模板填表，绝对不要预先要求用户建目录**。

#### 1.1 检测是否已是工作区

检查当前目录是否存在 `designos.project.yaml`：

- **存在** → 已是 DesignOS 工作区，跳过初始化，直接进入 Step 2。但仍做 1.5（环境检查）和 1.6（模式确认）。
- **不存在** → 进入 1.2 寻找 PRD。

告诉用户：「检测到当前目录不是 DesignOS 工作区，我将为你自动初始化。」

#### 1.2 智能定位 PRD 文件

按优先级搜索 PRD 输入源：

1. **用户消息中的文件路径**：扫描用户消息，如果包含 `.md / .pdf / .docx` 路径，优先使用。
2. **用户拖入的文件**：如果消息附件含文件，直接采用。
3. **用户粘贴的 PRD 正文**：如果用户消息很长（>500 字）且含「功能/需求/用户/页面」等关键词，识别为粘贴的 PRD 内容。
4. **当前目录自动扫描**（按顺序）：
   - 根目录：`prd.md` / `PRD.md` / `需求文档.*` / `*PRD*.{md,pdf,docx}` / `*需求*.{md,pdf,docx}`
   - `./inputs/`：同上模式
   - `./docs/`：同上模式

**找到** → 进入 1.3。告诉用户：「✓ 已找到 PRD：`<路径>`」

**没找到** → 友好询问：

```
我没找到 PRD 文件。你可以选择以下任一方式：
  1. 告诉我 PRD 文件的路径（例如：./my-prd.pdf）
  2. 把 PRD 内容直接粘贴在对话里
  3. 把 PRD 文件拖到对话窗口

准备好后告诉我，我会自动建好工作区。
```

不要假装继续，必须等用户回应。

#### 1.3 自动创建工作区目录与配置

在**当前工作目录**直接创建（不要问用户「建在哪里」）：

```bash
mkdir -p inputs outputs runs
```

**搬运 PRD**：
- `.md` 文件 → 复制为 `inputs/prd.md`
- `.pdf / .docx` 文件 → 复制为 `inputs/prd.<ext>`，并在 `inputs/prd.md` 写一行：`> 原文件：inputs/prd.pdf（需 pdf-parser MCP 解析，安装后会自动转 md）`
- 用户粘贴的正文 → 直接写入 `inputs/prd.md`

**生成 `designos.project.yaml`**（name 从 PRD 标题或首段推断，推断不出就用当前目录名）：

```yaml
name: <从 PRD 第一行标题或文件名推断>
created: <today YYYY-MM-DD>
skill: uxeval
mode: <暂留空，1.6 决定>
```

**生成 `.gitignore`**：

```
.env.local
.env
runs/
.designos/
outputs/*/evidence/
*.DS_Store
```

报告：「✓ 已建工作区于 `./`，目录：`inputs/` `outputs/` `runs/`。」

#### 1.4 AI 自动推断 scope.md（不要让用户从空模板写）

**严禁**给用户一份空模板让他填。**必须**调 LLM 读 PRD 内容，生成一份**已经填好初稿**的 `inputs/scope.md`。

推断逻辑：
- **评估目标**：从 PRD 的「业务目标 / 项目背景 / 立项原因」段落抽取，凝练成 1-2 句。
- **产品范围**：从 PRD 的「功能清单 / 模块结构 / 信息架构」抽取，列出范围内模块；范围外标注「本次评估不覆盖」。
- **关键用户角色**：从 PRD 的「目标用户 / 用户画像 / 使用场景」抽取，每个角色给出职责和典型痛点。
- 找不到的字段 → 写「（PRD 未明确，建议补充）」占位，**不要**留空。

写入 `inputs/scope.md`，然后告诉用户：

```
✓ 我已读完 PRD，自动推断出评估范围（写入 inputs/scope.md）：

【评估目标】
<生成内容摘要>

【产品范围】
- 范围内：<...>
- 范围外：<...>

【关键用户角色】
- <角色1>：<...>
- <角色2>：<...>

请审阅。回复：
  - 「继续」→ 进入下一步
  - 「修改 <具体内容>」→ 我会调整对应字段
  - 「重做」→ 重新推断
```

必须等到用户明确回复才继续。

#### 1.5 模型可用性检查

确认你（AI）当前能调用 LLM。如果 IDE 已配置好 Claude / GPT / DeepSeek 等模型，直接进入下一步——**不要让用户去配 API Key**。

只有当 IDE 完全没配置任何模型时（极少见）才提示：
```
当前 IDE 似乎未配置 LLM 模型。请在 IDE 设置里配置任意一个：
  - Claude (推荐，prompt 都针对它调优)
  - GPT-4o / DeepSeek 等
配置完成后回复「继续」。
```

**绝对不要**：让用户运行 `designos init`、写 `.env.local`、配 `ANTHROPIC_API_KEY`——这些都不是必需步骤。IDE/CLI 已经配过模型，你直接用即可。

#### 1.6 自动判定模式（客户端 vs Web）

判定优先级：

1. 用户原始指令含 `web <URL>` 或 `https://` → **Web 模式**，记录 URL 到 yaml。
2. `inputs/screens/` 目录存在 或 `inputs/screens-description.md` 存在 → **客户端模式**。
3. PRD 内容含「H5 / Web / 网页 / 网站 / 后台管理 / Dashboard / SaaS」 → 倾向 Web，但需确认。
4. PRD 内容含「App / 客户端 / iOS / Android / 小程序 / 桌面端」 → 倾向客户端，但需确认。
5. 都不明确 → 询问：

```
这是 Web 应用还是客户端应用？
  - Web 应用：我会用 Playwright 自动登录 + 截图（需 URL + 账号）
  - 客户端应用：你只需准备 5+ 张关键页面截图放到 inputs/screens/
回复「web <URL>」或「client」。
```

确认后写回 `designos.project.yaml` 的 `mode` 字段。

客户端模式下，若 `inputs/screens/` 为空，提示：「请在 `inputs/screens/` 放入 5+ 张关键页面截图（命名建议：01-登录.png、02-首页.png）。完成后回复「继续」。」

#### 1.7 完成初始化，进入 Step 2

输出汇总：

```
✓ 工作区初始化完成
  - 目录：./inputs ./outputs ./runs
  - PRD：inputs/prd.md
  - 范围：inputs/scope.md（已审阅）
  - 模式：<client | web>
  - API Key：✓

即将进入 12 阶段评估流水线。回复「开始」启动。
```

---

#### 示例对话（一次完整的自动初始化）

```
用户：/uxeval

AI：检测到当前目录不是 DesignOS 工作区，我将为你自动初始化。
    正在扫描 PRD 文件...
    ✓ 找到 PRD：./需求文档-V2.docx

    ✓ 已建工作区于 ./
      - inputs/  outputs/  runs/
      - inputs/prd.docx（原文件已复制）
      - designos.project.yaml
      - .gitignore

    正在阅读 PRD 并推断评估范围...

AI：✓ 我已读完 PRD，自动推断出评估范围（写入 inputs/scope.md）：

    【评估目标】
    验证「智能工单系统 V2」是否能让一线客服在 30 秒内完成工单分派，
    并确保新员工无需培训即可上手。

    【产品范围】
    - 范围内：工单列表、工单详情、分派流程、客户档案
    - 范围外：管理后台数据看板、系统设置

    【关键用户角色】
    - 一线客服小李：日均处理 80+ 工单，痛点是分派慢、找不到历史记录
    - 客服主管王姐：负责工单复核与团队 KPI 监控

    请审阅。回复「继续」/「修改 <内容>」/「重做」。

用户：修改 评估目标 加上重点关注新员工 5 分钟内完成首次分派

AI：✓ 已更新 inputs/scope.md。新版评估目标：
    「验证新员工能否在 5 分钟内完成首次工单分派，且一线客服日常分派 < 30 秒。」
    回复「继续」进入下一步。

用户：继续

AI：✓ 检测到 .env.local 含 ANTHROPIC_API_KEY。
    根据 PRD 提及「移动客服 App」，判定为客户端模式。
    检测到 inputs/screens/ 为空，请放入 5+ 张关键页面截图，命名建议：
      01-工单列表.png  02-工单详情.png  03-分派弹窗.png ...
    放好后回复「开始」。

用户：（放好截图后）开始

AI：（进入 Step 2 流水线）
```

---

#### 关键约束（不要违反）

- 不要让用户手动 `mkdir`
- 不要给用户空白模板让他填字段
- 不要在没找到 PRD 时假装继续
- 不要不告诉用户做了什么就改文件
- 每一步都要明确报告「做了什么 / 在哪里」
- 每个自动推断都要给用户「继续 / 修改 / 重做」干预入口
- 失败时给具体可执行命令，不丢「Error」

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

### Slash command 解析规则

当用户输入以 `/` 开头的命令：
1. 优先在 `.claude/commands/<cmd>.md` 找匹配的命令定义
2. 找不到 → 在本 AGENTS.md 的「快捷命令」表中查找
3. 仍找不到 → 按自然语言意图匹配 Skill
4. 都找不到 → 告诉用户「未识别命令：/xxx，输入 /skills 查看可用列表」

### 2. 执行方式

你（AI）按 `skills/uxeval/pipeline.yaml` 逐 stage 执行：读对应 prompt 文件 + reference 知识库，用当前模型推理，把产物写到用户当前项目的 `outputs/`。

**遇到需要工具的 stage**：
- **PRD 是 .pdf / .docx**：调用 `pdf-parser` 工具解析为文本（IDE 多模态可读 PDF 时也可直接读）。
- **Web 模式生成评估脚本**：自己写 Playwright `.spec.mjs` 文件，然后通过 terminal 跑 `node ...spec.mjs` 自动登录 + 截图。
- **Excel 报告**：调用 `excel-builder` 工具或自己用 openpyxl 临时脚本生成 .xlsx。
- **批量启发式检测**：调用 `heuristic-engine` MCP 跑结构化检测（含 LLM judge + 宪法校验）。
- **MCP / 工具未安装**：降级——能 AI 自己做的就自己做，必须工具支持的就提示用户安装。

### 3. 资产路径

- 知识库：`skills/uxeval/reference/m*.md`
- Prompt 模板：`skills/uxeval/prompts/v1.0.0/*.md`
- 输出模板：`skills/uxeval/templates/*.md`
- 评估宪法：`skills/uxeval/constitution.md`
- 黄金样本：`skills/uxeval/eval/golden/`
- 失败案例：`skills/uxeval/eval/failure/`

### 4. 错误处理

- **PRD 缺失** → 拒绝执行，请求用户补充
- **scope.md 缺失** → 从 PRD 自动推断生成初版，让用户审阅确认
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

- 当前：v0.4.0（V1 Candidate，2026-05-25）
- 仓库：https://github.com/Eryooo/designos
