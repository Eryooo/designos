# prd2proto 试点边界说明（Pilot Boundary）

> 版本：P1.1 Reality Hardening ｜ 日期：2026-06-01 ｜ 适用：内部试点
> 真源输入（两份真实端到端试跑报告）：
> - Trae / Kimi 运行：`/Users/young/Documents/trae_projects/xfg-ui/prd2proto_skill_report.md`
> - Claude Code 运行：`/Users/young/Documents/claude-code/designos/prd2proto-run/REPORT-skill-iteration.md`

本文件回答一个问题：**prd2proto 现在能信到哪、不能信到哪。**
它是"真实试跑可解释、可见、不断点、不过度假装自动化"的内部试点基线，
不是"已生产可用"声明。

## 1. 这批（P1.1）修掉了哪些真实试跑痛点

| 真实试跑痛点（原话） | 根因 | 本批收口 |
|---|---|---|
| "你在干啥怎么卡半天不动" | 无进度纪律，长写阶段连续静默 | Progress Contract 前置为**强制**执行纪律：每 stage 进/出各一行、长操作前预告、≤60 秒不得静默；测试锁死 |
| Checkpoint 在纯聊天里像停机 | checkpoint 模型抄自有 orchestrator 的场景 | Checkpoint Behavior：聊天模式 C1/C2/C3 **默认继续 + ≤3 行摘要 + 可打断**，只有 QG_REVIEW（真违规）硬停；测试锁死 |
| "mock MCP 永远通过但没价值" | frontend-codegen 被声明为**无条件** builtin 依赖 | frontmatter 加 `required_when: mode == "designer-dsl"`；pm / designer-spec 不再触发它；preflight 行为测试锁死 |
| build 过了但看不见原型（ERR_CONNECTION_REFUSED） | pipeline 终点错位在 review-gate | liveness-check 为**最后一个 stage**，必须产出 `dev_url` 并告诉用户打开哪个地址；测试锁死 |
| "代码有了不知道去哪看" | 输出路径无约定 | Output Path Convention（`prd2proto-out/<run_id>/`）稳定落盘；测试锁死 |
| pipeline 看着像 tool 实际是 LLM | `type: tool` 误导 | 实装现状表 + pipeline 把 token/code 标 `type: llm`，仅 dsl-fetch 是真 tool；测试锁死禁止把 mock 路径夸大成"已全部自动"的措辞 |

## 2. 哪些问题已经不再会让用户抓狂

- **不会再"卡半天没反应"**：Progress Contract 是强制纪律且测试保证它在 SKILL.md 前部、含 60 秒静默上限。
- **不会再在 checkpoint 处停机**：聊天模式默认继续，用户随时打断；只有真实宪法违规才停。
- **不会再 build 完看不见东西**：liveness-check 收尾必给 dev_url。
- **不会再不知道产物在哪**：输出路径固定。
- **不会再被假"工具自动化"误导**：实装现状表写明每个 stage 是真 tool 还是 LLM 手写。

## 3. 哪些自动化仍然不是真自动化（试点必须知道）

| Stage | 名义 | 真相 |
|---|---|---|
| 3b dsl-fetch | tool | 仅 designer-dsl；依赖**外部** figma-mcp / mastergo-mcp，未在本基线真实跑通 |
| 4 token-extraction | "工具" | **LLM 手写** W3C DTCG，不是工具产物 |
| 5 code-generation | "工具" | **LLM 手写**，prompt 钉死结构/状态管理/mock，但仍是 LLM 合成 |
| 7 liveness-check | tool（理想） | **LLM 引导用户在终端跑 npm**；frontend-codegen mock 没有 launch_preview，未真自动化 |
| 6 review-gate | 质量门 | **LLM 软审查** 4 条宪法，非静态扫描硬约束 |

frontend-codegen 本体是 **mock**：只返回固定骨架，不真做 DSL→代码。designer-dsl 真跑通不在本批范围。

## 4. 测试覆盖（本批锁住的契约）

- 结构 smoke 仍绿（skill 可加载、三模式过滤、8 stage 拓扑、factory validate 通过）
- Progress Contract / Checkpoint 行为有明确、可回归的约束
- preflight 按 mode 真实收敛（frontend-codegen 不在 pm/designer-spec 被探测）
- liveness / 输出路径 / 打开哪个 URL 的交付信息可验证
- 文档 / SKILL.md / pipeline 对"自动化真相"表述一致（禁止把 mock 路径夸大成"已全部自动"的措辞）

## 5. 这批不做（Scope 红线）

- 不扩 frontend-codegen 真能力 ／ 不做 designer-dsl 真 Figma 跑通
- 不重做 factory ／ 不开发其余 skills ／ 不做大范围 UI 美学调优
