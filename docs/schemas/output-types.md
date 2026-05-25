# DesignOS 数据结构定义

> 版本：v1.0-draft
> 日期：2026-05-15
> 用途：所有模块间传递数据的 Schema 定义，开发时的唯一参考

---

## 1. OutputType 枚举

Skill 产物的标准类型，用于 Skill 间自动匹配和注入。

| 类型 ID | 含义 | 产出 Skill | 消费 Skill |
|---|---|---|---|
| `analysis_report` | 分析报告 | ai-analytics | prd2proto, uxeval |
| `design_strategy` | 设计策略建议 | ai-analytics | prd2proto, ip-design |
| `comparison_matrix` | 竞品对比矩阵 | ai-analytics | — |
| `user_persona` | 用户画像 | uxeval, ai-analytics | prd2proto, uxeval |
| `user_journey` | 用户旅程图 | uxeval | prd2proto |
| `task_checklist` | 任务清单 | uxeval | — |
| `issue_report` | 问题报告 | uxeval | — |
| `html_report` | HTML 版问题报告 | uxeval | — |
| `prototype_code` | 原型代码 | prd2proto | design-system, uxeval |
| `design_tokens` | Design Token | prd2proto, design-system | — |
| `information_architecture` | 信息架构 | prd2proto | uxeval |
| `component_spec` | 组件规范 | design-system | — |
| `style_guide` | 样式指南 | design-system | — |
| `brand_brief` | 品牌 Brief | ip-design, brand-creative | — |
| `brand_persona` | 品牌人格档案 | ip-design | brand-creative |
| `visual_spec` | 视觉规范 | ip-design, design-system | — |
| `content_plan` | 内容计划 | ip-design, brand-creative | — |
| `heuristic_checklist` | 启发式检查清单 | uxeval | — |
| `evidence_pack` | 证据包 | uxeval, design-acceptance | — |
| `delivery_audit_bundle` | 最终交付资格审计包（含 bounded fallback package） | uxeval | — |
| `evaluation_script` | Playwright 评估脚本 | uxeval | — |
| `automated_eval_trace` | 自动化执行 trace | uxeval, design-acceptance | — |
| `visual_diff_report` | 视觉差异报告 | design-acceptance | — |
| `acceptance_report` | 设计验收报告 | design-acceptance | — |
| `page_mapping` | 页面映射表 | (用户输入) | design-acceptance 消费 |
| `frontend_code` | 前端代码 | prd2proto, design-system | — |
| `design_token_spec` | Design Token 规范 | design-system | prd2proto, design-acceptance |

**扩展规则**：新 Skill 可在自己的 `SKILL.md` 中声明新的 OutputType，Kernel 动态注册。

---

## 2. 核心 Schema

### 2.1 Pipeline 配置

```yaml
# pipeline.yaml 的完整 Schema
name: string                    # Pipeline 名称
version: string                 # semver

upstream_refs:                  # 可选：上游 Skill 产物引用
  - skill: string               # 上游 Skill 名
    output_type: string         # OutputType 枚举值
    inject_as: string           # 注入到 Pipeline 的变量名
    required: boolean           # 是否必须（false=没有也能跑）

stages:                         # Stage 列表（顺序执行）
  - id: string                  # 唯一标识
    type: enum[llm, tool, composite]
    prompt: string | null       # type=llm 时的 prompt 文件路径
    mcp_server: string | null   # type=tool 时的 MCP Server 名
    mcp_tool: string | null     # type=tool 时的工具名
    inputs: list[string]        # 输入变量名（从前序 stage 或 upstream）
    outputs: list[string]       # 输出变量名
    knowledge: list[string]     # 按需加载的知识库文件路径
    checkpoint: false | CheckpointConfig

CheckpointConfig:
  id: string                    # 如 "C1"
  message: string               # 展示给用户的确认提示
  allow: list[enum[continue, modify, supplement]]

memory:
  read: list[string]            # 读取的记忆 key pattern
  write: list[string]           # 写入的记忆 key pattern

constitution: string            # 评估宪法文件路径
```

### 2.2 Run Manifest

```yaml
# runs/001-uxeval/run.yaml
id: string                      # run 序号
skill: string                   # Skill 名
version: string                 # Skill 版本
status: enum[running, paused, completed, failed]
started_at: datetime
completed_at: datetime | null
model: string                   # 使用的模型
depends_on: list[string]        # 依赖的上游 run id

inputs_used:
  - path: string
    type: string                # 输入类型描述

outputs:
  - id: string                  # 产物 ID
    type: string                # OutputType
    path: string                # 相对路径
    format: enum[markdown, xlsx, html, json, directory]
    summary: string             # 一句话描述

checkpoints_decisions:
  - checkpoint: string          # Checkpoint ID
    decision: string            # 用户决策描述
    timestamp: datetime
```

### 2.3 项目配置

```yaml
# designos.project.yaml
name: string
created: date
owner: string
business_unit: string
tags: list[string]

skills:                         # 锁定的 Skill 版本
  uxeval: string                # semver range
  prd2proto: string

runs:                           # 执行历史
  - id: string
    skill: string
    status: string
    depends_on: list[string]
    completed_at: datetime | null
```

### 2.4 全局配置

```yaml
# ~/.designos/config.yaml
primary_model: string           # 如 "claude-opus-4-7"
fallback_model: string          # 如 "deepseek-v3"
memory_repo: string             # 组织记忆 Git URL
default_output_formats: list[string]  # [markdown, xlsx, html]
auto_upstream_inject: boolean   # true=自动提示引用上游（默认 true）
```

### 2.5 Checkpoint 持久化

```yaml
# .designos/checkpoints/session-{run_id}.yaml
run_id: string
skill: string
current_stage: integer          # 当前执行到第几个 stage（0-indexed）
completed_stages:
  - id: string
    output_hash: string         # SHA256，用于验证完整性
    checkpoint_decision: string | null
pending_stages: list[string]    # 待执行的 stage id
state_snapshot: dict            # Pipeline 当前状态（所有变量）
last_updated: datetime
```

---

## 3. 错误码枚举

| 错误码 | 含义 | 触发场景 |
|---|---|---|
| `E1001` | 配置文件缺失 | .env.local 或 config.yaml 不存在 |
| `E1002` | API Key 无效 | LLM 返回 401 |
| `E1003` | 模型不可用 | LLM 返回 503 |
| `E2001` | Pipeline 配置解析失败 | pipeline.yaml 格式错误 |
| `E2002` | Stage 输入缺失 | 前序 stage 未产出所需变量 |
| `E2003` | Stage 输出 Schema 校验失败 | LLM 输出不符合预期格式 |
| `E2004` | Checkpoint 恢复失败 | checkpoint 文件损坏 |
| `E3001` | MCP Server 启动失败 | 依赖未安装 |
| `E3002` | MCP 工具调用超时 | 30s 无响应 |
| `E3003` | MCP 工具返回错误 | 工具内部异常 |
| `E4001` | 工作区结构异常 | inputs/ 不存在 |
| `E4002` | 输入文件不存在 | PRD 路径无效 |
| `E4003` | 磁盘空间不足 | 写入前检测 |
| `E5001` | 组织记忆仓库不可达 | git pull 失败 |
| `E5002` | 脱敏检查未通过 | propose 时检测到敏感信息 |

---

## 4. 文件命名约定

| 场景 | 约定 | 示例 |
|---|---|---|
| Pipeline stage 输出 | `{序号}-{中文名}.{ext}` | `01-需求理解.md` |
| 证据截图 | `问题-{ID}-{简述}.png` | `问题-001-登录页.png` |
| Run 目录 | `{三位序号}-{skill名}/` | `001-uxeval/` |
| Prompt 版本 | `prompts/v{semver}/` | `prompts/v1.0.0/` |
| 黄金样本 | `eval/golden/case-{序号}-{简述}/` | `eval/golden/case-001-工作台/` |
| 失败案例 | `eval/failure/F{序号}-{简述}/` | `eval/failure/F001-功能测试偏移/` |
