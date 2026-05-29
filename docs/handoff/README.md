# Claude Code Handoff Pack (Self-contained in worktree)

用途：
- 这是 `Agent-design-webmode` 的本地化交接包。
- Claude Code 应优先只读取本目录与 `../releases/client-mode-v1.5-freeze/` 下的文件，不再依赖外部 `desigonos/outputs` 路径。

## 建议阅读顺序

1. `governance/01-claude-code-opus-governor-spec.md`
2. `governance/02-skills-factory-template-master-spec.md`
3. `governance/03-skills-development-best-practices-and-anti-patterns.md`
4. `theory/01-client-mode-90pct-metric-tree.md`
5. `governance/04-designos-phase-order-and-stop-conditions.md`
6. `history/01-agent-design-master-repair-charter.md`
7. `../releases/client-mode-v1.5-freeze/client_mode_freeze_manifest.json`
8. `../releases/client-mode-v1.5-freeze/client_mode_freeze_notes.md`
9. `../releases/client-mode-v1.5-freeze/client_mode_validation_baseline.md`
10. `next-skills/01-six-skills-deep-analysis.md`
11. `next-skills/02-ADR-003-skill-matrix-convergence-and-groups.md`
12. `next-skills/04-output-types.md`
13. `/Users/young/Documents/Codex/Agent-design-webmode/CLAUDE_HANDOFF_START.md`

## 目录说明

- `governance/`：上位执行规范、工厂模板、经验反模式、阶段顺序
- `theory/`：90%+ 目标的指标树与升级路线理论依据
- `history/`：项目修复总章程、审计、修复批次历史
- `evaluation/`：现有 client mode / benchmark / 审计结论
- `execution/`：Claude 交接包、严格说明、主启动提示词
- `next-skills/`：后续 6 个 skills 的矩阵、边界、产物契约、prd2proto 关键语义

## 使用原则

- `client mode` 已冻结为 `V1.5 pilot baseline`。
- 当前主线不是继续深挖 frozen client mode，而是转 `web mode` 封装。
- 后续 6 个 skills 必须按 Factory Template 开发，不能重新发明方法。
