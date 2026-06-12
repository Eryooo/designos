# Kernel 设计

> 版本：v1.0-draft
> 日期：2026-05-15
> 关联：[01-总体架构](01-总体架构.md), [03-Skill-规范](03-Skill-规范.md), [ADR-003](../decisions/ADR-003-Skill矩阵收敛与SkillGroup形态.md)

---

## 1. Kernel 职责

Kernel 是 DesignOS 的通用内核，所有 Skill 共享。Kernel **不感知具体业务**，只提供：

1. **Skill 加载与发现**（Pipeline + Skill Group 双形态）
2. **Pipeline 执行引擎**（顺序 / 条件分支 / 并行）
3. **Checkpoint 系统**（暂停 / 恢复 / 中断 / 重跑）
4. **Memory 适配器**（三级记忆抽象）
5. **LLM / MCP 客户端**（多 provider 抽象）
6. **配置加载**（环境变量 + YAML + 项目级 + 用户级）
7. **错误处理**（统一异常 + 错误码）
8. **Trace / 日志**（structlog + OpenTelemetry）
9. **预检机制**（外部依赖检测）
10. **输出渲染**（Markdown / Excel / HTML）

---

## 2. 模块结构

```
kernel/
├── __init__.py
├── contracts/                  # ★ 接口定义（Day 1 必出，所有线依赖）
│   ├── interfaces.py           # 抽象类（ILLMClient / IMCPClient / IMemoryAdapter）
│   ├── schemas.py              # Pydantic Models（StageResult / PipelineContext / RunManifest）
│   ├── enums.py                # OutputType / SkillType / Mode
│   └── errors.py               # DesignOSError + ErrorCode
│
├── skill_loader/               # Skill 加载与发现
│   ├── loader.py               # 通用入口（识别 Pipeline / Skill Group）
│   ├── pipeline_loader.py      # Pipeline Skill 加载
│   └── group_loader.py         # Skill Group 加载
│
├── pipeline/                   # Pipeline 执行引擎
│   ├── engine.py               # 顺序执行
│   ├── orchestrator.py         # 工作流编排（含并行）
│   ├── stage_runner.py         # 单 Stage 执行（LLM / MCP / 复合）
│   └── parallel_executor.py    # 并行子任务执行 + 结果聚合
│
├── checkpoint/                 # Checkpoint 系统
│   ├── manager.py              # 暂停 / 恢复 / 持久化
│   ├── state_serializer.py     # 状态序列化
│   └── interrupt.py            # 中断处理
│
├── memory/                     # 记忆系统
│   ├── adapter.py              # 抽象基类
│   ├── session_memory.py       # 会话级（进程内）
│   ├── project_memory.py       # 项目级（本地文件）
│   ├── organization_memory.py  # 组织级（Git 仓库）
│   └── sanitizer.py            # 脱敏检查
│
├── llm/                        # LLM 客户端
│   ├── client.py               # 抽象接口
│   ├── anthropic_provider.py   # Claude
│   ├── openai_provider.py      # OpenAI 兼容（含 Deepseek）
│   └── retry.py                # 重试 / 超时
│
├── mcp/                        # MCP 客户端
│   ├── client.py               # 调用 MCP Server 的统一入口
│   ├── stdio_transport.py      # stdio 模式
│   ├── sse_transport.py        # SSE 模式
│   └── registry.py             # MCP Server 发现与注册
│
├── config/                     # 配置加载
│   ├── loader.py               # 多层配置合并
│   ├── env_loader.py           # .env.local
│   └── schemas.py              # DesignOSConfig / SkillConfig / ProjectConfig
│
├── errors/                     # 异常体系
│   ├── __init__.py             # DesignOSError + 全部异常类
│   └── codes.py                # ErrorCode 枚举（E1001 / E2001 / ...）
│
├── trace/                      # 追溯日志
│   ├── logger.py               # structlog 配置
│   ├── recorder.py             # 写 trace.jsonl
│   └── otel_exporter.py        # OpenTelemetry（M2 启用）
│
├── preflight/                  # 预检机制
│   ├── checker.py              # 通用检测器
│   └── requirements.py         # 解析 SKILL.md 的 requires_external
│
├── output/                     # 输出渲染
│   ├── renderer.py             # 统一入口
│   ├── markdown.py             # Markdown 渲染
│   ├── excel.py                # Excel 渲染
│   └── html.py                 # HTML 渲染
│
└── workspace/                  # 项目工作区管理
    ├── initializer.py          # designos init 实现
    ├── workspace.py            # 工作区抽象
    └── run_manager.py          # runs/ 目录管理
```

---

## 3. 核心接口（Day 1 必须冻结）

### 3.1 Skill 抽象

```python
# kernel/contracts/interfaces.py
from abc import ABC, abstractmethod
from pydantic import BaseModel
from pathlib import Path
from typing import AsyncIterator

class ISkill(ABC):
    """所有 Skill 的统一接口"""
    name: str
    version: str
    skill_type: SkillType  # PIPELINE | GROUP

    @abstractmethod
    async def run(self, ctx: SkillContext) -> SkillResult: ...

class IPipelineSkill(ISkill):
    """Pipeline 形态 Skill"""
    @abstractmethod
    def get_stages(self) -> list[StageConfig]: ...

class ISkillGroup(ISkill):
    """Skill Group 形态"""
    @abstractmethod
    def list_sub_skills(self) -> list[str]: ...
    @abstractmethod
    def get_workflow(self, name: str) -> WorkflowConfig | None: ...
    @abstractmethod
    async def run_sub_skill(self, name: str, ctx: SkillContext) -> SkillResult: ...
```

### 3.2 Pipeline 引擎接口

```python
class IPipelineEngine(ABC):
    @abstractmethod
    async def execute(
        self,
        skill: IPipelineSkill,
        ctx: SkillContext,
    ) -> AsyncIterator[StageEvent]:
        """流式产出 stage 完成 / checkpoint / error 事件"""
```

### 3.3 工作流编排器（Skill Group 用）

```python
class IWorkflowOrchestrator(ABC):
    @abstractmethod
    async def execute(
        self,
        group: ISkillGroup,
        workflow: WorkflowConfig,
        ctx: SkillContext,
    ) -> AsyncIterator[WorkflowEvent]: ...

    @abstractmethod
    async def execute_parallel(
        self,
        group: ISkillGroup,
        sub_skill_names: list[str],
        ctx: SkillContext,
    ) -> dict[str, SkillResult]:
        """并行执行多个子 Skill，结果聚合"""
```

### 3.4 客户端抽象

```python
class ILLMClient(ABC):
    @abstractmethod
    async def call(
        self,
        prompt: str,
        *,
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> LLMResponse: ...

class IMCPClient(ABC):
    @abstractmethod
    async def call_tool(
        self,
        server: str,
        tool: str,
        args: dict,
    ) -> ToolResult: ...

class IMemoryAdapter(ABC):
    @abstractmethod
    def read_session(self, key: str) -> Any: ...
    @abstractmethod
    def write_session(self, key: str, value: Any) -> None: ...
    @abstractmethod
    def read_project(self, key: str) -> Any: ...
    @abstractmethod
    def write_project(self, key: str, value: Any) -> None: ...
    @abstractmethod
    def search_organization(self, query: str, k: int = 5) -> list[Any]: ...
    @abstractmethod
    def propose_to_organization(
        self, category: str, payload: Any
    ) -> str:
        """返回 staging PR URL"""
```

---

## 4. 关键数据结构

```python
# kernel/contracts/schemas.py

class SkillType(str, Enum):
    PIPELINE = "pipeline"
    GROUP = "group"

class StageType(str, Enum):
    LLM = "llm"
    TOOL = "tool"
    COMPOSITE = "composite"

class StageConfig(BaseModel):
    id: str
    type: StageType
    prompt: Path | None = None
    mcp_server: str | None = None
    mcp_tool: str | None = None
    inputs: list[str] = []
    outputs: list[str] = []
    knowledge: list[Path] = []
    only_when: str | None = None     # mode 条件分支
    checkpoint: CheckpointConfig | None = None
    retry: RetryConfig = RetryConfig()

class CheckpointConfig(BaseModel):
    id: str                          # 如 "C1"
    message: str
    allow: list[Literal["continue", "modify", "supplement"]]

class WorkflowStep(BaseModel):
    type: Literal["sequential", "parallel"]
    sub_skills: list[str]            # 引用 group 内的子 Skill 名
    on_failure: Literal["abort", "continue", "skip"] = "abort"

class WorkflowConfig(BaseModel):
    name: str
    description: str
    steps: list[WorkflowStep]

class SkillContext(BaseModel):
    workspace: Path
    skill_name: str
    skill_version: str
    mode: str | None = None
    config: DesignOSConfig
    upstream_data: dict[str, Any] = {}
    state: dict[str, Any] = {}        # 跨 stage 共享状态

class StageResult(BaseModel):
    stage_id: str
    status: Literal["completed", "failed", "skipped"]
    outputs: dict[str, Any] = {}
    error: ErrorInfo | None = None
    duration_ms: int

class SkillResult(BaseModel):
    skill_name: str
    status: Literal["completed", "paused", "failed"]
    stages: list[StageResult]
    artifacts: list[ArtifactRef]      # 产物文件引用
    paused_at_checkpoint: str | None = None
```

---

## 5. Pipeline 执行流程

```
┌────────────────────────────────────────────────────┐
│ 1. SkillLoader.load(skill_name)                    │
│    → IPipelineSkill 实例                            │
└────────────────────────┬───────────────────────────┘
                         ▼
┌────────────────────────────────────────────────────┐
│ 2. PipelineEngine.execute(skill, ctx)              │
│    for stage in skill.get_stages():                │
│      ├── 检查 stage.only_when 条件                  │
│      ├── 解析 stage.inputs（从 ctx.state）          │
│      ├── 执行（LLM / Tool / Composite）            │
│      ├── 校验 stage.outputs（Pydantic）            │
│      ├── 写入 ctx.state                             │
│      ├── 记录 trace                                 │
│      └── 如果有 checkpoint：                        │
│            ├── 持久化状态                           │
│            ├── 暂停，等用户                          │
│            └── 恢复时从这里继续                      │
└────────────────────────────────────────────────────┘
```

---

## 6. Skill Group 执行流程（brand-creative 用）

```
┌────────────────────────────────────────────────────┐
│ 1. SkillLoader.load(skill_name)                    │
│    → ISkillGroup 实例                              │
└────────────────────────┬───────────────────────────┘
                         ▼
┌────────────────────────────────────────────────────┐
│ 2a. 单技能模式                                      │
│   group.run_sub_skill("competitor-spectrum", ctx)  │
└────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────┐
│ 2b. 工作流模式                                      │
│   workflow = group.get_workflow("full-T1-to-T8")  │
│   for step in workflow.steps:                      │
│     if step.type == "sequential":                  │
│       for name in step.sub_skills:                 │
│         await group.run_sub_skill(name, ctx)       │
│     elif step.type == "parallel":                  │
│       results = await asyncio.gather(*[            │
│         group.run_sub_skill(n, ctx)                │
│         for n in step.sub_skills                   │
│       ])                                           │
└────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────┐
│ 2c. 并行模式（用户显式指定）                         │
│   results = await orchestrator.execute_parallel(   │
│     group, ["sub1", "sub2", "sub3"], ctx          │
│   )                                                │
└────────────────────────────────────────────────────┘
```

---

## 7. 配置层级（合并优先级从高到低）

```
1. 命令行参数
2. 项目级 designos.project.yaml
3. 用户级 ~/.designos/config.yaml
4. .env.local（API Key 等敏感信息）
5. Skill 级默认值
6. Kernel 内置默认值
```

---

## 8. 错误处理

所有异常继承 `DesignOSError`，带 `ErrorCode`：

```python
class DesignOSError(Exception):
    error_code: ErrorCode
    message: str
    context: dict[str, Any] = {}

class ConfigError(DesignOSError): ...   # E1xxx
class PipelineError(DesignOSError): ...  # E2xxx
class MCPError(DesignOSError): ...       # E3xxx
class WorkspaceError(DesignOSError): ... # E4xxx
class MemoryError(DesignOSError): ...    # E5xxx
```

完整错误码表：见 [schemas/output-types.md](../schemas/output-types.md#3-错误码枚举)。

---

## 9. 与 Skill 的契约

Kernel 对 Skill 的承诺：
- 提供 `SkillContext`（含 workspace / config / upstream / state）
- 提供 LLM / MCP / Memory / Output 客户端
- 处理 Checkpoint 暂停 / 恢复
- 处理错误重试 / 超时

Skill 对 Kernel 的承诺：
- 实现 `IPipelineSkill` 或 `ISkillGroup` 接口
- Stage outputs 必须符合 Pydantic Schema
- 不直接操作文件系统（通过 Kernel 提供的 Output renderer）
- 不直接调用 LLM / MCP（通过 ctx 注入的客户端）
