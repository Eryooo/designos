# DesignOS

AI-native 设计能力包，把高级设计专家方法论封装为可共享的 Skill 矩阵，跨 IDE / Agent 统一调用。

## 安装

```bash
npx designos
```

一行命令，自动检测并配置所有已安装的 IDE（Claude Code / Cursor / Trae / Codex / Qoder / WorkBuddy）。

安装完成后，在任意项目目录的 AI 对话框输入 `/uxeval` 即可启动体验评估。

## 升级

```bash
npx designos@latest
```

## 文档与贡献

- 架构与决策：`docs/architecture/`
- 决策记录（ADR）：`docs/decisions/`
- 数据契约：`docs/schemas/`
- 排期与并行任务：`docs/plans/`

提交规范请遵循 Conventional Commits，所有变更需通过 `uv run ruff check .`、`uv run pyright`、`uv run pytest` 三关。

## License

Apache 2.0，详见 `LICENSE`。
