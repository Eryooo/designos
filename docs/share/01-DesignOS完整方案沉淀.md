# DesignOS — Agent Skills 开发完整方案沉淀

> 集团内部分享版 · 2026-05-19
> 作者：young
> 版本：v0.1.2

---

## 目录

1. [项目背景与目标](#一项目背景与目标)
2. [产品方案设计](#二产品方案设计)
3. [技术方案设计](#三技术方案设计)
4. [核心设计思路](#四核心设计思路)
5. [关键决策点与权衡](#五关键决策点与权衡)
6. [开发过程关键节点](#六开发过程关键节点)
7. [经验总结](#七经验总结)
8. [最佳实践](#八最佳实践)
9. [踩坑记录](#九踩坑记录)
10. [未来规划（M2+）](#十未来规划)

---

## 一、项目背景与目标

### 1.1 起点：7 个设计类 Agent 原型

我作为高级体验设计师，已经在工作中沉淀了 7 个设计能力的 AI Agent 原型：

| Agent | 用途 |
|---|---|
| 体验评估（UXEval） | 启发式评估、可用性测试 |
| PRD → 原型 | 从需求文档生成可交互原型 |
| 设计系统 | Token 体系、组件规范生成 |
| IP 设计 | 品牌 IP 形象设计 |
| 品牌咨询 | 品牌策略、视觉创意 |
| 竞品分析 | AI Analytics 能力 |
| AI-native 治理底盘 | 跨 Agent 的能力调度、记忆管理 |

### 1.2 核心问题

这些原型分散在各处，**只有我会用**。设计师团队 100+ 人，要把这套能力沉淀成**可共享、可演进**的工具包，让每个设计师都能：

- 一键调用专家级方法论
- 不需要懂 prompt engineering
- 在自己日常用的 IDE 里直接触发
- 输出质量稳定可控

### 1.3 项目目标

```
做一个 AI-native 设计能力包，封装高级设计专家方法论为可共享 Skill 矩阵
```

衡量标准：
- ✅ 设计师不写 prompt，对 IDE 说一句话就能跑完整流程
- ✅ 输出符合宪法（可证据化、可执行、不跑偏）
- ✅ 跨 IDE（Trae / Cursor / Claude Code / Codex / Workbuddy）通用
- ✅ 通过 GitHub + PyPI 在集团内分发

---

## 二、产品方案设计

### 2.1 产品定位：DesignOS

**Design** + **Operating System** = 设计师的操作系统层。

不是一个 App，不是一个网站，是一组**装到设计师工作流里**的能力包。

### 2.2 三层架构

```
┌─────────────────────────────────────────────────┐
│  Skills 层（设计师视角）                          │
│  • UXEval / PRD→Proto / Design System / ...    │
│  每个 Skill 是一套完整的方法论 + Prompt + 流水线   │
├─────────────────────────────────────────────────┤
│  Kernel 层（基础设施）                            │
│  • Pipeline 引擎 / MCP 客户端 / 记忆系统 / LLM 路由│
├─────────────────────────────────────────────────┤
│  MCP Servers 层（工具）                           │
│  • PDF 解析 / Excel 生成 / 启发式判断 / 视觉分析   │
└─────────────────────────────────────────────────┘
```

### 2.3 Skill 规范

每个 Skill 是一个目录，遵循统一规范：

```
skills/uxeval/
├── SKILL.md              # 入口文件（含 frontmatter）
├── constitution.md       # 评估宪法（不可违反的硬约束）
├── pipeline.yaml         # 流水线定义（12 stages）
├── prompts/v1.0.0/       # 版本化的 Prompt 模板
│   ├── 01-prd-understanding.md
│   ├── 02-persona-derivation.md
│   └── ...
├── reference/            # 知识库（启发式原则、证据采集等）
├── templates/            # 输出模板
└── eval/
    ├── golden/           # 黄金样本
    └── failure/          # 失败案例
```

**关键设计**：
- **版本化 Prompt**：每个改动有 commit 记录，回归测试可追溯
- **宪法（Constitution）**：硬约束放在独立文件，每次输出后校验，违反则重新生成
- **流水线（Pipeline）**：声明式 YAML 定义阶段、依赖、Checkpoint

### 2.4 Skill 类型

| 类型 | 特征 | 例子 |
|---|---|---|
| Pipeline Skill | 固定阶段、串行执行、产物可预测 | UXEval（12 stages） |
| Skill Group | 包含多个子 Skill + workflow 编排 | brand-creative（13+ 子能力） |

### 2.5 Pipeline 设计（以 UXEval 为例）

12 个阶段，每个阶段类型为 `llm` 或 `tool`：

```
1. PRD 理解         → 模块 / 功能 / 业务目标
2. 角色推导         → 用户角色
3. 场景推导         → 关键场景
4. 启发式映射       → 适用原则
5. 旅程建模         → 用户旅程图        ⚠ Checkpoint C1
6. 任务生成         → 体验任务清单      ⚠ Checkpoint C2
7. (Web 模式)       → Playwright 自动化（M2）
8. 截图加载         → 截图列表
9. 启发式检测       → 原始问题清单
10. 问题归因        → 结构化问题清单    ⚠ Checkpoint C3
11. 报告生成        → Excel + Markdown
```

**Checkpoint 机制**：在关键产物点暂停、展示给用户、等回复「继续 / 修改 / 补充」，避免 AI 自嗨跑偏。

### 2.6 双模式（客户端 vs Web）

UXEval 支持两种证据采集模式，核心流程一致，区别在于截图从哪来：

| 模式 | 证据采集方式 | 适用场景 |
|---|---|---|
| **客户端模式** | 用户提供界面截图，AI 直接读取分析 | 移动 App / 桌面客户端 / 小程序 / 无法自动化的系统 |
| **Web 模式** | AI 生成 Playwright 脚本，自动登录 + 导航 + 截图 | Web 后台 / SaaS / 内部管理系统 |

**触发入口统一**：无论从 IDE 对话框还是 terminal 触发，做的事情完全一样——AI 是执行主体，按 pipeline.yaml 逐 stage 执行，需要工具时就调用工具。`designos run` 只是另一个触发入口（适合 CI / 批量场景），不是另一条路径。

**关键洞察**：设计师在 IDE/CLI 里已经配过 LLM 模型（Claude / GPT / DeepSeek），DesignOS **不需要重复要求他们配 API Key**。

---

## 三、技术方案设计

### 3.1 技术栈

| 层 | 选型 | 为什么 |
|---|---|---|
| 语言 | Python 3.11+ | 设计师会用，AI 生态最完善 |
| 包管理 | uv | 比 pip 快 10x，比 poetry 简单 |
| 构建 | hatchling | 标准 PEP 621，PyPI 友好 |
| 模型 | Pydantic v2 | 严格类型 + 序列化 |
| CLI | Typer | 类型驱动的 CLI 框架 |
| 日志 | structlog | 结构化日志，可上 OpenTelemetry |
| HTTP | httpx | async / sync 统一 |
| LLM SDK | anthropic + openai | 多 Provider 支持 |
| 协议 | MCP (Model Context Protocol) | Anthropic 推的工具调用标准 |

### 3.2 Kernel 内核设计

```
kernel/
├── pipeline/         # 流水线引擎
│   ├── engine.py     # 编排器
│   └── stage_runner.py # 单 stage 执行器
├── mcp/              # MCP 客户端
│   ├── client.py     # 标准 stdio 客户端
│   ├── inprocess_transport.py # 进程内调用（开发优化）
│   └── registry.py   # MCP Server 注册表
├── llm/              # LLM 客户端
│   ├── client.py     # 路由分发
│   ├── anthropic_provider.py
│   └── openai_provider.py
├── memory/           # 三级记忆
│   ├── session.py    # 会话级（内存）
│   ├── project.py    # 项目级（本地文件）
│   └── organization.py # 组织级（GitHub）
├── workspace/        # 工作区管理
├── checkpoint/       # Checkpoint 状态机
├── contracts/        # 全局接口与 Schema
└── trace/            # OpenTelemetry 追踪
```

### 3.3 MCP Server 设计

每个 MCP Server 是一个独立 Python 包，暴露工具给 Kernel 调用：

| Server | 工具 | 用途 |
|---|---|---|
| pdf-parser | parse_pdf | PRD PDF → Markdown |
| excel-builder | build_issue_report | 问题清单 → Excel |
| heuristic-engine | detect_issues | 截图 + 原则 → 问题列表 |
| image-analyzer | load_and_analyze | 截图加载 + 多模态分析 |
| playwright-driver | run_evaluation | Web 自动化（M2） |
| visual-diff | compare | 设计稿 vs 实现还原度（M2） |
| frontend-codegen | generate | PRD → 前端代码（M2） |
| competitor-scraper | scrape | 竞品抓取（M2） |
| image-prompt-gen | generate | IP / 品牌图片 prompt（M2） |
| methodology-advisor | advise | 跨 Skill 方法论咨询（M2） |

### 3.4 InProcessTransport：开发期的关键优化

**问题**：标准 MCP 用 stdio 通信，每个 Server 是独立子进程。开发期反复改代码 → 反复重启 Server → 调试痛苦。

**解决**：写了一个 `InProcessTransport`，在开发模式下**直接 import 工具函数调用**，绕过子进程。生产环境仍走 stdio。

```python
# kernel/mcp/inprocess_transport.py
class InProcessTransport(ITransport):
    """开发期内联调用，省掉子进程开销"""
    async def call_tool(self, name: str, args: dict) -> Any:
        fn = self._registry[name]
        # 1. 类型注解解析（处理 from __future__ import annotations）
        hints = typing.get_type_hints(fn)
        # 2. 字段映射（pipeline 输出 → tool 输入）
        normalized = self._apply_aliases(args)
        # 3. Pydantic 校验
        ...
```

这个看起来小，但**让开发效率提升 5x**。

### 3.5 三级记忆系统

```
Session Memory（会话级，内存）
    ↑ 跑完一个 run 后归档
Project Memory（项目级，本地 .designos/memory/）
    ↑ 用户认为有价值，提交到组织
Organization Memory（组织级，GitHub repo）
    ↑ 专家审核 + golden sample 沉淀
```

**关键设计**：
- 写入是"自下而上"的（Session → Project → Org）
- 每一级都有人工 gate（防止脏数据污染）
- 组织级记忆驱动 Skill 自演进（见 3.7）

### 3.6 Checkpoint 机制

避免 AI 跑偏的核心。三个 Checkpoint：

| ID | 时机 | 提问 |
|---|---|---|
| C1 | 旅程图生成后 | 这个旅程是否准确？ |
| C2 | 任务清单生成后 | 任务粒度是否合理？是否覆盖关键场景？ |
| C3 | 问题严重等级标注后 | 严重等级是否合理？ |

每个 Checkpoint：
1. **暂停**流水线
2. **展示**该阶段产物
3. **等待**用户回复（继续 / 修改 / 补充）
4. **`auto_confirm` 模式**可以自动 resume，跳过等待

### 3.7 Eval-driven 自演进

```
跑评估 → 收集失败案例 → 加入 failure/
                              ↓
                      DSPy 自动 prompt 优化
                              ↓
                      在 golden samples 上回归测试
                              ↓
                      通过 → PR 提案 → 专家审核
                              ↓
                      合并 → 新版本 prompt
```

工具链：
- **promptfoo**：A/B 测试不同版本 prompt
- **DSPy**：自动 prompt engineering
- **golden samples**：每个 Skill 必备 5+ 黄金样本
- **失败案例库**：跑出来的 bad case 自动归档

### 3.8 分发：PyPI + GitHub

- **PyPI**：`pip install <YOUR_INTERNAL_PACKAGE>`，版本化分发
- **GitHub**：源码 + Skill 包 + AGENTS.md
- **GitHub Actions**：tag 触发自动发版（OIDC trusted publishing，免 token）

### 3.9 IDE 集成层

让 AI 在 IDE 里"知道"DesignOS 的能力：

| IDE | 配置文件 |
|---|---|
| Claude Code | `.claude/commands/uxeval.md` + `AGENTS.md` |
| Cursor | `.cursor/rules/*.mdc` + `.cursorrules` |
| Trae / Workbuddy / Codebuddy | `AGENTS.md`（通用约定） |

**通用 AGENTS.md** 是核心 — 它是给 AI 看的"使用手册"，告诉它：
- DesignOS 有哪些 Skill
- 每个 Skill 的触发条件
- 完整执行流程（步骤 / Checkpoint / 错误处理）
- 文件位置约定
- 对话风格要求

---

## 四、核心设计思路

### 4.1 哲学层：AI-native，不是 AI-feature

❌ 错的思路：做一个网页/App，里面塞一些 AI 功能
✅ 对的思路：让 AI 成为执行主体，工具/数据/Prompt 围绕它编排

体现在：
- 没有 GUI，所有交互在 IDE 对话框
- 流程驱动而非按钮驱动
- AI 调 MCP 工具，不是用户点工具按钮

### 4.2 知识层：让方法论可执行

设计专家的经验通常在脑子里、PPT 里、Notion 里 —— 这些 AI 看不懂。

**做法**：把方法论拆成三个文件：
- `constitution.md`：硬约束（什么绝对不能做）
- `prompts/`：软指导（推理过程）
- `reference/`：知识库（领域知识）

**好处**：可版本化、可 diff、可回归测试。

### 4.3 流程层：流水线 + Checkpoint

❌ 一次性大 prompt（20 页）让 AI 跑完所有事 —— 容易跑偏，无法干预
✅ 拆成 12 个 stage，每个 stage 一个明确产物，关键节点 Checkpoint

### 4.4 工具层：MCP 协议解耦

工具不是写在 prompt 里的「请你帮我处理 PDF」，而是真实的代码 —— 通过 MCP 协议暴露给 LLM。

**好处**：
- 工具可独立测试
- 工具可被多个 Skill 共用
- 工具可热替换（PDF 解析器用 pdfplumber 还是 unstructured，对 Skill 透明）

### 4.5 演进层：自下而上的进化

每次跑出来的 run，无论好坏都是养料：
- 好的 → 进 golden samples
- 坏的 → 进 failure cases
- 累积一定量 → 触发 prompt 自动优化

**专家不在闭环里反复改 prompt**，而是给 Skill 灌数据，让它自己长。

---

## 五、关键决策点与权衡

### 5.1 决策表

| 决策点 | 选择 | 替代方案 | 为什么 |
|---|---|---|---|
| 主语言 | Python | TypeScript / Go | 设计师生态、AI/ML 库丰富、MCP 官方 SDK |
| 包格式 | PyPI | npm / 自托管 | 集团内已有 PyPI 镜像，零额外基础设施 |
| 模型协议 | MCP | OpenAI Function Calling | MCP 跨厂商、标准化、未来兼容性好 |
| 默认模型 | Claude Opus 4.7 | GPT-4o / DeepSeek | 长上下文 + 多模态视觉 + Anthropic 调优最稳 |
| Skill 格式 | Markdown + YAML | JSON Schema / 自定义 DSL | 设计师能读能写，git diff 友好 |
| 执行模式 | 统一流程，CLI 只是另一个触发入口 | IDE 和 CLI 是两条路径 | 本质上做的事一样，不应区分 |
| 记忆存储 | 本地文件 → GitHub | 数据库 / 向量库 | 透明、可审计、零运维 |
| License | Apache 2.0 | MIT / 私有 | 集团内分享，可商用，专利保护 |

### 5.2 走过弯路的决策

#### 弯路 1：把 IDE 和 CLI 当成两条路径（已纠正）

**初版**：要求设计师 `pip install <YOUR_INTERNAL_PACKAGE>` → `<YOUR_INTERNAL_PACKAGE> init` → 配 API Key → `<YOUR_INTERNAL_PACKAGE> run uxeval`，把这叫"CLI 模式"；IDE 里说 `/uxeval` 叫"IDE 模式"。

**问题**：本质上做的事完全一样——AI 按 pipeline 逐 stage 执行，需要工具时调工具。区分两条路径是多余的，还让设计师以为必须装 Python 才能用。

**纠正**：只有一套执行流程。`/uxeval`（IDE 对话框）和 `<YOUR_INTERNAL_PACKAGE> run uxeval`（terminal）是同一件事的两个触发入口。设计师用前者，CI/批量用后者。

#### 弯路 2：让设计师 git clone 整个仓库（待纠正）

**当前**：设计师 `git clone designos` 仓库，把它当作工作目录。

**问题**：开发者视角，不是用户视角。设计师的工作目录应该是「他正在评估的产品」。

**下一步**：实现 `designos install` 命令，在用户当前目录注入 Skill。

---

## 六、开发过程关键节点

### Day 1：架构定型

- 确认统一执行流程（AI 按 pipeline 执行 + client/web 双模式证据采集）
- 选定技术栈（Python + uv + hatch + Pydantic）
- 7 个 Agent → 6 个 Skill（PRD→Proto 合并 design-system）
- 10 个 MCP Server 初始清单

### Day 2：UXEval Pipeline 跑通

- 12 stages 全部实现
- 真实 LLM 调用（Claude Opus）
- Checkpoint 机制工作
- 端到端跑通 6-8 分钟

**踩坑**：
- LLM 输出的 JSON 没有规范分隔，pipeline 拿不到 → 写 `_parse_llm_outputs()`
- 缺失上游输入直接崩溃 → 改为缺失默认空字符串
- Pydantic frozen 模型不接受 `None` → 写 `_drop_none_recursive()`

### Day 3：测试 + 内测准备

- 148 个单元测试通过，160 总测试
- 写设计师内测手册
- 写通用 AGENTS.md（覆盖 Trae / Cursor / Claude Code / Codex / Workbuddy / Codebuddy）
- 自动初始化工作区（用户只需丢 PRD，AI 自动建目录、推断 scope）

### Day 4：PyPI 发版

- GitHub Actions + OIDC trusted publishing 配通
- v0.1.0 发布到 PyPI
- 试装到 Trae IDE → 遇到沙箱权限问题
- 修复（DESIGNOS_HOME 环境变量 + 项目级降级），v0.1.1 发布
- 永久 PATH 修复（__main__.py + 自动写 .zshrc），v0.1.2 发布

### Day 5：方向调整

- 发现：让设计师 `pip install` + 配 API Key 是过度设计
- 调整：统一为一套执行流程，`designos run` 只是 CI/批量场景的触发入口
- 重写设计师内测手册：从 6 步降到 3 步
- 改 AGENTS.md，明确告诉 AI「不要让用户重复配 API Key」

### Day 6（明天）：install 命令

- 实现 `designos install`，一行命令把 skills 安装到全局
- 让设计师不需要 git clone 整个仓库
- 对标 oh-my-zsh / husky 的安装体验

---

## 七、经验总结

### 7.1 关于 Agent Skill 设计

#### ✅ 做对的事

1. **把宪法独立**：constitution.md 让硬约束可审计
2. **流水线显式化**：YAML 比"一个大 prompt"可控 100 倍
3. **Checkpoint 机制**：让人类有干预入口，不被 AI 牵着走
4. **MCP 协议解耦工具**：工具可独立演进
5. **版本化 prompt**：能 git diff、能回归测试

#### ❌ 别犯的错

1. **不要追求"一个 prompt 解决所有"**：拆成 stage 才能稳定
2. **不要让 AI 决定流程顺序**：声明式 pipeline 更可靠
3. **不要在 prompt 里硬编码工具调用**：用 MCP 解耦
4. **不要忽略错误处理**：LLM 会返回不合规输出，必须 retry + 校验
5. **不要把所有上下文塞进一次调用**：分阶段更省 token

### 7.2 关于工程实现

#### ✅ 做对的事

1. **Pydantic v2 严格 schema**：错误在边界就暴露
2. **InProcessTransport**：开发体验提升 5x
3. **structlog + OpenTelemetry**：复杂流水线必须可观测
4. **黄金样本 + 失败案例**：自演进的基础数据集

#### ❌ 别犯的错

1. **`from __future__ import annotations` 注意 Pydantic 兼容性**：用 `typing.get_type_hints()` 才能解析字符串注解
2. **不要用 `data.get(name, data)` 做兜底**：会把整个字典塞进单个字段，难调试
3. **MCP 子进程的标准输入输出会被各种东西污染**：日志、warning 都要重定向到 stderr
4. **不要重复造 LLM client**：用官方 SDK，自己只做 routing

### 7.3 关于产品设计

#### ✅ 做对的事

1. **从 IDE 视角设计**：设计师在哪、AI 在哪、就在哪交互
2. **零配置优先**：能从 IDE 拿到的，不要再问用户
3. **简洁的 Slash Command**：`/uxeval` 比 `<YOUR_INTERNAL_PACKAGE> run uxeval --mode client --auto-confirm` 好 10 倍

#### ❌ 别犯的错

1. **不要让用户重复配 API Key**：IDE 已有的就别要了
2. **不要让用户「先去配置好环境」**：这是开发者思维
3. **不要在文档里堆「先 git clone → 再 cd → 再 pip install ...」**：每多一步就流失 30% 用户

### 7.4 关于团队协作

DesignOS 一个人不够 —— 一旦上规模，需要：
- **设计专家**：定义 Skill 内容、宪法、黄金样本
- **工程师**：维护 Kernel、MCP Server、CI/CD
- **领域 PM**：组织级记忆策展、反馈回路
- **AI 工程师**：自演进流水线、prompt 优化

---

## 八、最佳实践

### 8.1 Skill 设计

**模板**：

```markdown
---
name: <skill-name>
version: 1.0.0
mcp_servers: [<list>]
default_mode: client
---

# <Skill 名> — 一句话定位

## 触发条件
- 自然语言：「...」「...」
- Slash command：/<name>

## 输入要求
- 必需：<...>
- 推荐：<...>
- 可选：<...>

## 输出
- <产物 1>：路径 + 格式
- <产物 2>：...

## 流水线（pipeline.yaml 引用）

## 宪法（constitution.md 引用）

## Checkpoint（在哪些点暂停）
```

### 8.2 Prompt 编写

**结构**：

```
1. 角色定义（你是谁）
2. 输入说明（你会拿到什么）
3. 任务目标（你要产出什么）
4. 约束（不能做什么）
5. 输出格式（严格的 JSON schema）
6. Few-shot examples（黄金样本）
7. 自检清单（输出前自己核对）
```

**避坑**：
- 不要写「请尽量...」「最好...」 → 改成「必须...」
- 不要让 LLM 自由发挥结构 → 给 JSON schema
- 不要相信单次输出 → 加宪法校验 + retry

### 8.3 Pipeline 编写

```yaml
- id: <stage-id>
  type: llm | tool
  only_when: <condition>           # 条件执行
  prompt: prompts/v1.0.0/01-x.md   # LLM stage 必填
  mcp_server: <name>                # tool stage 必填
  mcp_tool: <name>                  # tool stage 必填
  inputs: [<state-keys>]            # 上游产物
  outputs: [<state-keys>]           # 本阶段产物
  checkpoint:                       # 可选
    id: C1
    message: "请确认..."
  retry:
    max_attempts: 3
    backoff_seconds: 2.0
```

### 8.4 Checkpoint 编写

```python
{
  "id": "C2",
  "message": "请确认任务清单是否合理",
  "preview": "<前 500 字符的产物预览>",
  "options": ["继续", "修改", "补充"],
  "auto_confirm": false
}
```

### 8.5 黄金样本管理

每个 Skill 至少 5 个黄金样本：
- 涵盖典型场景（移动端 App / Web 后台 / 小程序 / SaaS）
- 包含完整输入 + 期望输出
- 用于回归测试 + Few-shot
- 每次 prompt 改动后必跑

### 8.6 失败案例归档

```
skills/uxeval/eval/failure/
├── 2026-05-18-旅程图跑偏.json
│   ├── input/
│   ├── output/
│   ├── expected/
│   └── analysis.md   # 为什么错、怎么改
```

---

## 九、踩坑记录

### 9.1 LLM 相关

| 坑 | 表现 | 解法 |
|---|---|---|
| LLM 返回带 markdown 代码块的 JSON | `JSONDecodeError` | 写 JSON 提取器（去 ```json ... ``` 包裹） |
| LLM 输出多个产物时只填了第一个 | 后续 stage 拿不到上游数据 | 在 prompt 里要求严格 schema + 解析时拆分 |
| `temperature=0` 仍有不一致 | 同样输入跑两次结果不同 | 不依赖完全确定性，加 retry + 宪法校验 |
| 长文档塞进 prompt 超 token 限制 | 报 `context_length_exceeded` | 用 Claude 长上下文（200k）或先做 summary stage |
| 多模态 .md 被当成图片 | base64 编码失败 | 显式判断后缀，文本走 text block |

### 9.2 MCP / 工具相关

| 坑 | 表现 | 解法 |
|---|---|---|
| stdio MCP server 启动慢 | 每次 stage 切换 200ms 开销 | 开发期用 InProcessTransport |
| MCP server 的 print() 污染 stdio | client 解析失败 | 重定向到 stderr 或用 logging |
| Pipeline 字段名 ≠ Tool 参数名 | Pydantic 校验失败 | 写字段映射表 `_ARG_ALIASES` |
| Frozen 模型不接受 `None` | `validation error` | 写 `_drop_none_recursive()` |

### 9.3 打包 / 分发相关

| 坑 | 表现 | 解法 |
|---|---|---|
| `pip install --user` 后 binary 不在 PATH | `command not found: designos` | __main__.py 兜底 + 自动改 .zshrc |
| Trae 沙箱不能写 `~/.designos` | `PermissionError` | DESIGNOS_HOME env + 项目级降级 |
| GitHub Actions 推 PyPI 卡住 | environment 没批准 | 第一次推手动批一次，后续自动 |
| 集团镜像源同步慢 | `pip install <YOUR_INTERNAL_PACKAGE>` 找不到 | 临时用 `-i https://pypi.org/simple/` 强制官方源 |

### 9.4 IDE 集成相关

| 坑 | 表现 | 解法 |
|---|---|---|
| Claude Code 不识别 Slash Command | 输入 `/uxeval` 没反应 | 必须放 `.claude/commands/uxeval.md`，不能在子目录 |
| AGENTS.md 在子目录被忽略 | AI 不知道 Skill | 复制一份到子目录或用 IDE 全局配置 |
| Cursor 的 .mdc 格式和 Claude 不通用 | 配置要写两份 | 分别维护 `.cursor/rules/` 和 `.claude/commands/` |

---

## 十、未来规划

### 10.1 M2（下一阶段）

| 项目 | 内容 |
|---|---|
| Web 自动化 | 实现 playwright-driver MCP，支持 Web 模式自动登录 + 截图 |
| 5 个 Skill | prd2proto / design-system（合并） / ip-design / brand-creative / ai-analytics |
| `designos install` 命令 | 一键注入 Skill 到当前目录 |
| 组织级记忆 | GitHub repo 作为团队记忆库 + 专家审核流 |
| Eval 自演进 | DSPy + promptfoo 接入 |

### 10.2 M3（中期）

- 多模态视觉强化（不只截图，支持视频 / 操作录制）
- 跨 Skill 编排（如 PRD → 原型 → 评估 → 报告 一条龙）
- 设计师 SaaS 版（不愿装本地的用户用 Web）
- 集团内 Skill 市场（用户自发贡献 + 排行）

### 10.3 远期愿景

```
DesignOS 不只是工具
它是设计师集体智慧的载体
每个新加入的设计师，
都能站在前 100 个设计师的肩膀上
```

---

## 附录

### A. 项目地址
- GitHub：<YOUR_INTERNAL_PRIVATE_REPO>
- PyPI：https://<YOUR_INTERNAL_REGISTRY>/
- 当前版本：v0.1.2（M1 — UXEval 内测版）

### B. 关键文件索引

```
Agent-design/
├── AGENTS.md                          # IDE 通用指引（必读）
├── pyproject.toml                     # 包配置
├── kernel/                            # 内核
│   ├── pipeline/                      # 流水线引擎
│   ├── mcp/                           # MCP 客户端
│   ├── llm/                           # LLM 路由
│   └── memory/                        # 记忆系统
├── skills/uxeval/                     # 第一个 Skill
│   ├── SKILL.md
│   ├── constitution.md
│   ├── pipeline.yaml
│   ├── prompts/v1.0.0/
│   ├── reference/
│   └── eval/golden|failure/
├── mcp-servers/                       # 工具层
│   ├── pdf-parser/
│   ├── excel-builder/
│   ├── heuristic-engine/
│   └── image-analyzer/
├── designos/cli/                      # CLI 入口
│   ├── main.py
│   ├── installer.py
│   └── ide_detector.py
├── docs/                              # 文档
│   ├── 内测操作手册.md
│   ├── architecture/
│   └── decisions/
└── tests/                             # 160+ 测试
```

### C. 命令速查

```bash
# 安装（一次性）
curl -fsSL https://designos.dev/install.sh | bash
# 安装后在任何项目目录说 /uxeval 即可

# 批量 / CI 场景（同一套流程，另一个触发入口）
pip install <YOUR_INTERNAL_PACKAGE>
<YOUR_INTERNAL_PACKAGE> run uxeval --mode client --auto-confirm
designos --help

# 开发者
git clone <repo>
uv sync
uv run pytest                    # 跑测试
uv build                         # 本地构建
```

### D. 联系方式

- 维护：young
- 反馈：GitHub Issues / 团队群
- 协作：欢迎 PR，每个 Skill 都需要专家审核

---

> 文档版本：v1.0
> 更新时间：2026-05-19
> 下次更新：M2 阶段开始时
