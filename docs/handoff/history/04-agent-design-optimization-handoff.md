# Agent-design 优化交接包

## 1. 这份文件是给哪个项目用的

目标项目：

- `/Users/young/Documents/Codex/Agent-design`

用途：

- 在该项目的新线程里，直接引用本文件和相关审计报告
- 让 Codex 基于已经完成的排查结果，继续系统性优化 `uxeval` skill 及其平台底座

## 2. 为什么当前 skill 明明有很多问题，却依然产出了完整报告

这是本次排查里最容易误解的一点。

结论：

`成功产出完整体验评估报告，并不等于 Agent-design 仓库里的 runtime 已经生产级可用。`

原因有两层：

1. 本次成功运行主要依赖的是：
   - 当前对话里的模型执行能力
   - 本地文件读取、PDF 解析、截图分析、结构化写作能力
   - 我对 `SKILL.md` 工作流的人工补全与兜底执行

2. 不是完全依赖 Agent-design 仓库内部那套 `designos runtime`
   - `preflight` 在 repo 内仍是假阳性
   - `PipelineSkill.run()` 仍会把失败结果洗成 `COMPLETED`
   - `image-analyzer` 仍是 stub
   - `report-generation` 的 tool output 与 pipeline outputs 仍未对齐

所以，`单次 run 成功` 证明的是：

- `uxeval` 方法论和产出结构是有价值的

而不是：

- `Agent-design` 平台已经达到了生产级自治执行

## 3. 在 Agent-design 项目里必须引用的文件

### 核心审计文件

- [agent-design-production-audit.md](/Users/young/Documents/Codex/desigonos/outputs/agent-design-production-audit.md)
- [uxeval-production-readiness-audit.md](/Users/young/Documents/Codex/desigonos/outputs/uxeval-production-readiness-audit.md)
- [unified-uxeval-skill-blueprint.md](/Users/young/Documents/Codex/desigonos/outputs/unified-uxeval-skill-blueprint.md)

### 运行结果与评审清单

- [for-skill-review-manifest.json](/Users/young/Documents/Codex/desigonos/outputs/for-skill-review-manifest.json)
- [auto-run-quality-review.md](/Users/young/Documents/Codex/desigonos/outputs/auto-run-quality-review.md)
- [judge_me.md](/Users/young/Documents/Codex/desigonos/outputs/judge_me.md)

### 真实产物样本

- [07-问题报告.md](/Users/young/Documents/Codex/desigonos/runs/20260521-uxeval-client-01/07-问题报告.md)
- [07-问题报告.xlsx](/Users/young/Documents/Codex/desigonos/runs/20260521-uxeval-client-01/07-问题报告.xlsx)
- [06-问题清单.json](/Users/young/Documents/Codex/desigonos/runs/20260521-uxeval-client-01/06-问题清单.json)

## 4. 在 Agent-design 项目里优先修什么

第一优先级不是调 prompt，而是先修平台底座：

1. 修 `PipelineSkill.run()` 状态聚合
   - 失败不能再返回 `COMPLETED`
   - checkpoint 需要返回 `PAUSED`

2. 打通 `SKILL.md frontmatter -> skill config -> preflight -> MCP registry`
   - 让 skill 定义变成真正的运行时真源

3. 修复 CLI 假闭环
   - `run` 写 manifest
   - `resume` 真恢复
   - `mcp install` 去掉 TODO stub
   - `input check` 改成结构化校验

4. 对齐 tool output schema
   - Stage 7 pipeline outputs 与 `excel-builder` 的真实返回值一一对应

5. 替换 M1 stub
   - 至少把 `image-analyzer` 从“枚举文件”升级为“可产生结构化视觉观察”

第二优先级才是 skill 级优化：

1. 收敛 `SKILL.md / README / constitution / tests / pipeline`
2. 产品化 `strict / semi-auto / autonomous`
3. 增加 `confidence / coverage / evidence_basis / unresolved_conflicts`
4. 建立 web/client 共用证据 schema

## 5. 在 Agent-design 新线程里建议直接使用的启动提示词

可直接复制下面这句到 `/Users/young/Documents/Codex/Agent-design` 的新线程：

```text
请基于 /Users/young/Documents/Codex/desigonos/outputs/agent-design-optimization-handoff.md、/Users/young/Documents/Codex/desigonos/outputs/agent-design-production-audit.md、/Users/young/Documents/Codex/desigonos/outputs/uxeval-production-readiness-audit.md，对当前 Agent-design 仓库进行系统性整改。目标不是修补单次 demo，而是把 uxeval 和底层 runtime 一起提升到生产级可用。先从 P0 平台问题开始，直接修改代码、补测试、跑验证。
```

## 6. 对新线程的执行建议

在 `Agent-design` 新线程里，优先采用下面顺序：

1. 先修 runtime 与 CLI 语义错误
2. 再修 skill 定义与 preflight / MCP 接线
3. 再修 tests / lint / typecheck 漂移
4. 最后再收敛 prompt、README、评测集和自动化模式

否则会出现“prompt 越改越强，但平台仍然误报成功”的假进展。
