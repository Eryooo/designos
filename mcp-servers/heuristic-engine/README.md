# heuristic-engine MCP Server

DesignOS UXEval 启发式检测引擎。把"启发式原则 + 任务清单 + 截图（可选 DOM）"作为输入，输出结构化的体验问题清单。

## 能力

- **规则引擎**（`rules.py`）：基于 DOM/截图元数据的纯函数硬规则。涵盖系统状态可见性、操作密度、术语解释、表单标签、错误反馈等启发式硬规约。
- **LLM 视觉评审**（`llm_judge.py`）：调用 Anthropic 视觉模型（默认 `claude-opus-4-7`），按照 Skill 注入的评估宪法对每张截图给出主观判断。
- **原则库**（`principles_library.py`）：内置尼尔森 10 + DesignOS 业务扩展 5 条；Skill 可覆写。
- **宪法强制**（`core.py`）：每条 issue 必须 `evidence_refs` 非空、`severity` 合法、`principle` 在原则集中；自动剔除账号 / 密码 / 内网地址等敏感信息。

## MCP 工具

```jsonc
// tool: detect
// input
{
  "screenshots": [{ "id": "S-001", "path": "...", "flow": "登录" }],
  "principles": [{ "id": "H1", "name": "...", "description": "..." }],
  "task_checklist": { "tasks": [{ "id": "T-1", "title": "..." }], "journey_summary": "..." },
  "constitution": "...",
  "mode": "client",
  "dom_data": null
}
// output
{
  "raw_issues": [
    {
      "title": "...",
      "description": "...",
      "principle": "H1",
      "severity": "major",
      "evidence_refs": ["S-001"],
      "source": "rule",
      "confidence": 0.85,
      "suggestion": "...",
      "user_impact": "..."
    }
  ],
  "summary": {
    "total_issues": 1,
    "by_severity": {"major": 1},
    "by_principle": {"H1": 1},
    "rule_hits": 1,
    "llm_hits": 0
  }
}
```

`principles` 留空时自动加载 `principles_library.default_principles()`（尼尔森 10 + 业务扩展 5）。

## Mock 模式

开发或单测无真实 API Key 时设置环境变量：

```bash
export HEURISTIC_ENGINE_MOCK=1
```

LLM judge 会跳过实际请求，返回每张截图一条占位 issue（principle 为输入清单第一条），便于跑通端到端流程。

## 运行

```bash
uv pip install -e ".[dev]"
uv run designos-heuristic-engine   # MCP stdio
uv run pytest tests/ -v
```

## 目录

```
heuristic-engine/
├── pyproject.toml
├── server.py              # MCP stdio 入口
├── core.py                # 检测编排 + 宪法强制
├── rules.py               # 规则引擎（5 条硬规则）
├── llm_judge.py           # LLM 视觉判断器
├── schemas.py             # Pydantic 输入输出
├── principles_library.py  # 原则库（10+5）
└── tests/
    ├── conftest.py
    ├── fixtures/          # 测试用 DOM/截图元数据
    ├── test_rules.py
    └── test_core.py
```
