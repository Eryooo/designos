# Sub-agent 分工清单（M0 + M1）

> 版本：v1.0
> 日期：2026-05-15
> 用途：把 M0 + M1 的工作拆成可被独立 Sub-agent 并行执行的任务包

---

## 1. 总策略

```
T0 (Day 1, 串行): 单 Agent 出接口定义 + M0 仓库骨架
                   │
                   ▼
T1 (Day 2-7, 并行): 4 个 Agent 并行
   ├── A1: Kernel 实现
   ├── A2: pdf-parser MCP Server
   ├── A3: excel-builder MCP Server
   └── A4: heuristic-engine MCP Server
                   │
                   ▼
T2 (Week 2, 并行 + 串行): 3 个 Agent
   ├── A5: UXEval Skill 内容（reference / prompts / constitution）
   ├── A6: CLI + 工作区管理
   └── A7: 集成测试 + E2E
                   │
                   ▼
T3 (Week 3-4, 单 Agent): 联调 + Bug 修复 + Demo
```

---

## 2. T0 — 接口冻结 + M0 setup（单 Agent，1 天）

### 任务包 T0

**Sub-agent 名称**：`bootstrap-architect`
**模型推荐**：Claude Opus（决策密度高）
**预估 Token**：50K input / 30K output

**目标**：
1. 初始化仓库（git + pyproject.toml + uv 配置）
2. 配置开发工具（ruff / pyright / pytest）
3. 配置 CI（GitHub Actions：lint / type / unit）
4. 创建项目骨架目录
5. **写完整的 `kernel/contracts/` 接口定义**——后续所有线依赖

**必须读的文档**：
- `docs/decisions/ADR-001` + `ADR-002` + `ADR-003`
- `docs/architecture/01-总体架构.md`
- `docs/architecture/02-Kernel-设计.md`
- `docs/architecture/03-Skill-规范.md`
- `docs/schemas/output-types.md`

**产出**（按目录）：
```
Agent-design/
├── pyproject.toml
├── uv.lock
├── ruff.toml
├── pyrightconfig.json
├── .gitignore
├── .env.example
├── README.md
├── LICENSE                       # Apache 2.0
├── CHANGELOG.md
├── .github/
│   └── workflows/
│       ├── ci.yml                # lint + type + unit
│       └── release.yml
├── kernel/
│   ├── __init__.py
│   └── contracts/                # ★ 完整实现
│       ├── __init__.py
│       ├── enums.py              # SkillType / StageType / OutputType / ErrorCode
│       ├── schemas.py            # 所有 Pydantic Models
│       ├── interfaces.py         # ISkill / IPipelineSkill / ISkillGroup / ILLMClient / IMCPClient / IMemoryAdapter
│       └── errors.py             # DesignOSError 体系
├── kernel/pipeline/__init__.py   # 占位（A1 实现）
├── kernel/checkpoint/__init__.py # 占位
├── kernel/memory/__init__.py     # 占位
├── kernel/llm/__init__.py        # 占位
├── kernel/mcp/__init__.py        # 占位
├── kernel/config/__init__.py     # 占位
├── kernel/errors/__init__.py     # 占位
├── kernel/output/__init__.py     # 占位
├── kernel/preflight/__init__.py  # 占位
├── kernel/trace/__init__.py      # 占位
├── kernel/workspace/__init__.py  # 占位
├── kernel/skill_loader/__init__.py
├── designos/
│   ├── __init__.py
│   └── cli/
│       ├── __init__.py
│       └── main.py               # Typer 入口（占位）
├── skills/                       # 空目录
├── mcp-servers/                  # 空目录
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── __init__.py
│   │   └── test_contracts.py     # ★ 验证 Schema / Enum 定义合理
│   ├── integration/
│   │   └── __init__.py
│   └── e2e/
│       └── __init__.py
└── tools/                        # 空目录
```

**验收标准**：
- [ ] `uv sync` 成功
- [ ] `uv run ruff check .` 全过
- [ ] `uv run pyright` 全过（contracts 完整类型标注）
- [ ] `uv run pytest tests/unit/test_contracts.py` 全过（Schema 实例化测试）
- [ ] `.github/workflows/ci.yml` 在 PR 中能跑通（fork 仓库验证）
- [ ] git log 干净（首个 commit + Conventional Commits）

**强制规约**：
- 类型标注 100%
- Pydantic v2 语法（不用 v1）
- 用 uv 管理依赖（不用 pip / poetry）
- 接口定义里的所有字段必须有 docstring

---

## 3. T1 — 4 Agent 并行（M1 Week 2-3）

### 任务包 A1：Kernel 实现

**Sub-agent 名称**：`kernel-engineer`
**模型推荐**：Claude Opus
**预估 Token**：120K input / 60K output

**目标**：实现 Kernel 的所有非接口模块

**前置依赖**：T0 的 `kernel/contracts/` 完成

**只能修改**：
- `kernel/pipeline/`
- `kernel/checkpoint/`
- `kernel/memory/` (本地实现 + 接口 stub)
- `kernel/llm/`
- `kernel/mcp/`
- `kernel/config/`
- `kernel/errors/` (实现具体异常类)
- `kernel/output/`
- `kernel/preflight/`
- `kernel/trace/`
- `kernel/workspace/`
- `kernel/skill_loader/`
- `tests/unit/test_kernel_*.py`

**禁止修改**：
- `kernel/contracts/` （接口已冻结）
- `mcp-servers/` （A2/A3/A4 负责）
- `skills/` （A5 负责）

**关键交付**：
- `PipelineEngine` 能按 YAML 顺序执行（mock LLM/MCP）
- `WorkflowOrchestrator` 能跑顺序 + 并行工作流
- `CheckpointManager` 能暂停 / 持久化 / 恢复
- `MemoryAdapter` 本地文件实现 + 组织记忆 Git stub
- `LLMClient` 支持 Anthropic + OpenAI 兼容（含 Deepseek）
- `MCPClient` 支持 stdio + SSE 两种 transport
- `ConfigLoader` 支持 4 层合并
- `Sanitizer` 脱敏检查规则
- `WorkspaceInitializer` 能创建项目工作区
- 所有模块有 README.md（接口 + 示例）

**验收标准**：
- [ ] 单元测试覆盖率核心路径 >= 80%
- [ ] pyright strict 全过
- [ ] ruff check 全过
- [ ] 用一个 fixture pipeline.yaml 能跑通完整流程（mock）

---

### 任务包 A2：pdf-parser MCP Server

**Sub-agent 名称**：`mcp-pdf-parser`
**模型推荐**：Claude Sonnet（Token 便宜，工程简单）
**预估 Token**：30K input / 15K output

**目标**：实现 PDF 解析 MCP Server

**前置依赖**：T0 完成

**只能修改**：`mcp-servers/pdf-parser/`

**目录结构**：
```
mcp-servers/pdf-parser/
├── pyproject.toml          # 独立依赖：mcp + pdfplumber
├── server.py               # MCP stdio Server 入口
├── core.py                 # 核心解析逻辑（纯函数）
├── schemas.py              # Pydantic Models（PdfContent / Section）
├── README.md
└── tests/
    ├── conftest.py
    ├── test_core.py
    ├── test_server.py
    └── fixtures/
        ├── sample-prd.pdf
        ├── scanned.pdf
        └── empty.pdf
```

**接口契约**：
```python
# tool: parse_pdf
# input: {path: str}
# output: PdfContent {
#   sections: list[Section],   # title + content + page
#   metadata: PdfMetadata,
#   page_count: int,
# }
```

**验收标准**：
- [ ] 标准 PRD PDF 提取章节正确（用真实分类分级 PRD 测试）
- [ ] 扫描件 PDF 返回 PdfParseError（不崩溃）
- [ ] 空 PDF 返回空 sections
- [ ] 100 页 PDF 在 30s 内完成
- [ ] MCP Inspector 手动连通成功
- [ ] 单测全过

---

### 任务包 A3：excel-builder MCP Server

**Sub-agent 名称**：`mcp-excel-builder`
**模型推荐**：Claude Sonnet
**预估 Token**：30K input / 15K output

**目标**：实现 Excel 报告生成 MCP Server

**只能修改**：`mcp-servers/excel-builder/`

**接口契约**：
```python
# tool: build_issue_report
# input: {
#   issues: list[Issue],
#   output_path: str,
#   template: "uxeval" | "design-acceptance" | "competitor"
# }
# output: {path: str, sheet_count: int}
```

**验收标准**：
- [ ] Excel 含正确 sheet（问题清单 + 摘要 + 启发式原则）
- [ ] 中文不乱码
- [ ] 严重等级用颜色标记（critical=红 / major=橙 / minor=黄 / suggestion=灰）
- [ ] 列宽自适应
- [ ] 单测全过

---

### 任务包 A4：heuristic-engine MCP Server

**Sub-agent 名称**：`mcp-heuristic-engine`
**模型推荐**：Claude Opus（涉及 LLM 视觉判断）
**预估 Token**：50K input / 25K output

**目标**：实现启发式检测引擎 MCP Server

**只能修改**：`mcp-servers/heuristic-engine/`

**接口契约**：
```python
# tool: detect
# input: {
#   screenshots: list[ScreenshotRef],
#   principles: list[HeuristicPrinciple],
#   task_checklist: TaskChecklist,
#   constitution: str,           # 注入 Skill 的评估宪法
# }
# output: {
#   raw_issues: list[RawIssue],   # 含问题描述 + 原则 + 严重等级 + evidence_refs
#   summary: DetectionSummary,
# }
```

**实现策略**：
- 内部 LLM 调用（视觉模型分析截图）+ 规则引擎（DOM 数据规则匹配）
- 参考 `/Users/young/Documents/trae_projects/design-review/scripts/build_heuristic_*.mjs` 现有逻辑

**验收标准**：
- [ ] 给定 5 张截图 + 10 条原则，能输出结构化问题清单
- [ ] 每条问题强制绑 evidence_refs（违反宪法直接拒绝）
- [ ] 严重等级在合法枚举内
- [ ] 单测覆盖核心规则

---

## 4. T2 — 3 Agent 并行（M1 Week 3-4）

### 任务包 A5：UXEval Skill 内容

**Sub-agent 名称**：`skill-author-uxeval`
**模型推荐**：Claude Opus（方法论密度高）
**预估 Token**：80K input / 40K output

**目标**：把 UXEval 的方法论 + Prompt + 评估宪法 + Pipeline 配置写完

**前置依赖**：T0 完成（接口已定）

**只能修改**：`skills/uxeval/`

**目录产出**：
```
skills/uxeval/
├── SKILL.md
├── pipeline.yaml
├── constitution.md
├── reference/
│   ├── index.json
│   ├── m01-需求理解.md
│   ├── m02-启发式原则.md
│   ├── m03-旅程建模.md
│   ├── m04-任务生成.md
│   ├── m05-证据采集.md
│   └── m06-问题归因.md
├── prompts/
│   └── v1.0.0/
│       ├── 01-prd-understanding.md
│       ├── 02-principle-mapping.md
│       ├── 03-journey-modeling.md
│       ├── 04-task-generation.md
│       ├── 05a-script-generation.md   # web mode（M1 client 优先，可先占位）
│       ├── 06-issue-attribution.md
│       └── CHANGELOG.md
├── templates/
│   ├── 旅程地图.md
│   ├── 任务清单.md
│   └── 问题报告.md
├── examples/
│   └── case-001-分类分级/
├── eval/
│   ├── golden/
│   ├── failure/
│   └── promptfoo.yaml
├── tests/
│   ├── conftest.py
│   ├── fixtures/
│   └── test_pipeline_integration.py
└── README.md
```

**素材来源**：
- `legacy/agent-prototypes/uxeval-agent.html` 提取方法论框架
- `legacy/sharing-materials/体验评估分享内容.md` 提取宪法和评估口径
- `/Users/young/Documents/trae_projects/design-review/outputs/` 真实评估产物作 golden 样本

**验收标准**：
- [ ] SKILL.md 通过 Skill 加载器校验
- [ ] pipeline.yaml 能被 Kernel 解析
- [ ] 6 个 prompt 通过专家（你）review
- [ ] 至少 2 个黄金样本 + 1 个失败案例
- [ ] 集成测试用 mock LLM 跑通

---

### 任务包 A6：CLI + 工作区管理

**Sub-agent 名称**：`cli-engineer`
**模型推荐**：Claude Sonnet
**预估 Token**：40K input / 20K output

**目标**：实现 designos CLI 命令

**前置依赖**：A1 完成（依赖 Kernel）

**只能修改**：
- `designos/cli/`
- `tests/unit/test_cli_*.py`

**核心命令**：
```bash
designos init <name> [--skill <skill>]   # 创建工作区
designos config                           # 交互式配置 API Key + 模型
designos run <skill> [--mode <mode>]      # 执行 Skill
designos resume                           # 恢复中断的 Pipeline
designos history                          # 查看历史 run
designos input check                      # 检查输入合规性
designos input scaffold <skill>           # 复制输入模板
designos skill list                       # 列出可用 Skill
designos skill versions <skill>           # 查看 Skill 版本
designos preflight <skill>                # 单独跑预检
designos --version
designos --help
```

**验收标准**：
- [ ] 所有命令有 `--help`
- [ ] `designos init test-project --skill uxeval` 能创建合规工作区
- [ ] `designos config` 交互式向导能写 .env.local
- [ ] CLI 单测全过

---

### 任务包 A7：集成测试 + E2E 冒烟

**Sub-agent 名称**：`qa-engineer`
**模型推荐**：Claude Sonnet
**预估 Token**：40K input / 20K output

**目标**：写集成测试和 E2E 冒烟

**前置依赖**：A1 + A2 + A3 + A4 + A5 + A6 完成

**只能修改**：
- `tests/integration/`
- `tests/e2e/`
- `tests/conftest.py`（共享 fixtures）

**测试覆盖**：
- Kernel + MCP Server 集成（pdf-parser / excel-builder / heuristic-engine 各 1 个）
- UXEval Skill + Kernel + 3 个 MCP 集成（用 recorded LLM 回放）
- E2E：`designos init` → `designos run uxeval --mode client` → 验证产物

**验收标准**：
- [ ] 集成测试用 mock LLM 跑通
- [ ] E2E 冒烟在 CI 中能跑
- [ ] 测试覆盖 Checkpoint 暂停/恢复

---

## 5. T3 — 联调 + Demo（W4-W5）

由 main agent（你 + 我对接）负责，不分 sub-agent。

包括：
- 跨任务包接口对齐
- Bug 修复
- 你 review
- 端到端 demo（用真实 PRD + 截图）
- M1 完成确认

---

## 6. Sub-agent 通用规约（每个 Agent prompt 都注入）

```markdown
你是 DesignOS 项目的 Sub-agent，负责一个独立任务包。

## 你必须遵守的铁律

1. **只动你被分配的目录**——禁止修改其他目录文件
2. **先读文档再写代码**：必读 `docs/decisions/ADR-001/002/003`、`docs/architecture/01-02-03`
3. **接口冻结**：`kernel/contracts/` 是只读的，不许改
4. **TDD 优先**：先写 test_*.py 再写实现
5. **类型标注 100%**：pyright strict 必须全过
6. **接口用 Pydantic**：跨模块传递只用 Pydantic Model，禁止 dict
7. **日志用 structlog**：禁止 print 和 logging
8. **错误用 DesignOSError**：所有异常继承基类，带 ErrorCode
9. **配置走 YAML/env**：禁止硬编码
10. **单文件 < 300 行，单函数 < 30 行**
11. **commit 用 Conventional Commits**：feat / fix / docs / test / refactor / chore

## 提交前必须自检

- [ ] `uv run ruff check .` 全过
- [ ] `uv run pyright` 全过
- [ ] `uv run pytest <你的测试>` 全过
- [ ] 模块有 README.md

## 不要做的事

- 不要装新依赖（除了任务允许的）
- 不要改 `kernel/contracts/`
- 不要改其他 Agent 的代码
- 不要写「未来可能会用到」的代码
- 不要为不存在的需求写防御性代码
```

---

## 7. 启动顺序

```
Day 1: 启动 T0 (bootstrap-architect)
       ↓ 完成后
Day 2: 同时启动 A1 / A2 / A3 / A4 (4 Agent 并行)
       ↓ A1 + A2/3/4 完成后
Week 3-4: 同时启动 A5 / A6 / A7 (3 Agent 并行)
       ↓ 全部完成后
Week 5: T3 联调
```

我会按这个顺序逐个 dispatch sub-agent。
