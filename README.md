# DesignOS

AI-native 设计能力包，把高级设计专家方法论封装为可共享的 Skill 矩阵，跨 IDE / Agent 统一调用。

## 状态

`v0.1.0` — M0 阶段（接口冻结 + 仓库骨架）。Kernel / MCP Servers / Skills 实现尚在并行开发中，暂未具备端到端运行能力。

## 文档与贡献

- 架构与决策：`docs/architecture/`
- 决策记录（ADR）：`docs/decisions/`
- 数据契约：`docs/schemas/`
- 排期与并行任务：`docs/plans/`

提交规范请遵循 Conventional Commits，所有变更需通过 `uv run ruff check .`、`uv run pyright`、`uv run pytest` 三关。

## License

Apache 2.0，详见 `LICENSE`。
