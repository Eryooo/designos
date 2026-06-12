> ⚠️ **ARCHIVED / OUTDATED — DO NOT USE FOR CURRENT STATUS.**
> 本文件是历史过程记录，不代表当前状态。当前权威状态见仓库根
> `INTERNAL-PILOT-README.md` / `REVIEW-MANIFEST.md` / `skills/status.matrix.yaml`。

# Claude Code Start Prompt

把下面整段作为 Claude Code 新会话的第一条消息：

```text
请在 /Users/young/Documents/Codex/Agent-design-webmode 中接管后续工作，但不要重新发散分析，也不要从头定义方向。你当前接手的是一个已经完成 client mode V1.5 冻结的 DesignOS/UXEval 平台项目。

先读取这些本地真源文件：
- /Users/young/Documents/Codex/Agent-design-webmode/docs/handoff/governance/01-claude-code-opus-governor-spec.md
- /Users/young/Documents/Codex/Agent-design-webmode/docs/handoff/governance/02-skills-factory-template-master-spec.md
- /Users/young/Documents/Codex/Agent-design-webmode/docs/handoff/governance/03-skills-development-best-practices-and-anti-patterns.md
- /Users/young/Documents/Codex/Agent-design-webmode/docs/handoff/theory/01-client-mode-90pct-metric-tree.md
- /Users/young/Documents/Codex/Agent-design-webmode/docs/handoff/governance/04-designos-phase-order-and-stop-conditions.md
- /Users/young/Documents/Codex/Agent-design-webmode/docs/handoff/theory/03-skills-factory-roadmap.md
- /Users/young/Documents/Codex/Agent-design-webmode/docs/handoff/history/01-agent-design-master-repair-charter.md
- /Users/young/Documents/Codex/Agent-design-webmode/docs/handoff/next-skills/01-six-skills-deep-analysis.md
- /Users/young/Documents/Codex/Agent-design-webmode/docs/handoff/next-skills/02-ADR-003-skill-matrix-convergence-and-groups.md
- /Users/young/Documents/Codex/Agent-design-webmode/docs/handoff/next-skills/03-ADR-002-skill-matrix-playwright-sharing.md
- /Users/young/Documents/Codex/Agent-design-webmode/docs/handoff/next-skills/04-output-types.md
- /Users/young/Documents/Codex/Agent-design-webmode/docs/releases/client-mode-v1.5-freeze/client_mode_freeze_manifest.json
- /Users/young/Documents/Codex/Agent-design-webmode/docs/releases/client-mode-v1.5-freeze/client_mode_freeze_notes.md
- /Users/young/Documents/Codex/Agent-design-webmode/docs/releases/client-mode-v1.5-freeze/client_mode_validation_baseline.md

然后遵守以下规则：
1. 不要重新发散产品方向。以上本地文件是单一真源。
2. normal mode 主结论必须接近 99%-100% 可信；fallback 正向断言也必须 >= 85%。
3. client mode 当前已经冻结为 V1.5 pilot baseline。除非发现 release blocker，不要继续无限修 client mode。
4. 在理解后续 6 个 skills 时，必须特别注意：`prd2proto` 的 mode 语义与 `uxeval` 不同。`uxeval` 的 mode 是证据采集差异，`prd2proto` 的 mode 是保真度档位；不得把两者强行套成同一类 mode 逻辑。
5. 后续默认优先级是：
   - 支持 client mode 端到端人工验收
   - 开始 web mode 封装
   - 再抽 Skills Factory Template
   - 再按 archetype 推进剩余 6 个 skills
6. `governance/02-skills-factory-template-master-spec.md` 是后续所有 skill 的统一工厂模板主规范；`governance/03-skills-development-best-practices-and-anti-patterns.md` 是工程经验与反模式约束。不得绕开它们自定义一套新方法。
7. `theory/01-client-mode-90pct-metric-tree.md` 是后续质量拉升、冻结判断和 benchmark 解释的理论依据与指标真源。每一批都必须明确映射到指标树，而不是只做泛化优化。
8. 对 `prd2proto`、`design-acceptance`、`ai-analytics`、`brand-creative` 等后续 skills，必须先根据 archetype 和输出契约理解业务边界，再写 pipeline；不允许先拍脑袋生成 skill 骨架。
9. 一次只做一个 batch，不要扩 scope。
10. 每次汇报先用产品/用户语言说明问题、风险、价值，再讲技术。
11. 每次重要结论都要落盘到仓库。
12. 如果你不确定下一步做什么，默认先做仓库真相检查和最小验证，再给出单 batch 推进方案。

如果用户当前没有指定具体任务，请默认从“web mode 封装”的最小可执行第一批开始，并先回答：
1. 当前 client mode freeze 基线是否完整
2. web mode 当前仓库真相是什么
3. 最小可执行的 web mode Batch 1 应该做什么
4. 为什么这一步是当前最高优先级
5. 当前 batch 主攻哪些关键指标，以及如何判断这是“更会做成”而不是“更会拦”
```
