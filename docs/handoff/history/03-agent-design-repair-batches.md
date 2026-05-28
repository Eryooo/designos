# Agent-design 分批修复方案

## 1. 适用场景

当单个线程额度不足以完成整仓修复时，不做“大一锅端”，改为按批次推进。

目标仓库：

- `/Users/young/Documents/Codex/Agent-design`

原则：

1. 每个 batch 都能独立完成
2. 每个 batch 都有明确验收标准
3. 先修平台语义，再修 skill 能力，再修文档与评测

## 2. 推荐批次顺序

### Batch 1：修运行时真语义

目标：

- 修复失败 skill 被标记为 `COMPLETED`
- 修复 checkpoint / paused / failed 的结果聚合

改动范围：

- `kernel/skill_loader/pipeline_loader.py`
- 必要时补 `kernel/pipeline/engine.py`
- 补对应单元测试 / 集成测试

验收标准：

1. stage 失败时 `SkillResult.status == FAILED`
2. checkpoint 暂停时返回 `PAUSED`
3. 原有成功路径仍返回 `COMPLETED`
4. 新测试覆盖这三类状态

为什么先做：

- 不修这个，后面所有 run、history、workflow、group skill 结果都不可信

### Batch 2：打通 skill frontmatter 与 preflight / MCP 注册

目标：

- 让 `SKILL.md` 真正成为运行时真源

改动范围：

- `skills/uxeval/SKILL.md`
- `kernel/skill_loader/pipeline_loader.py`
- `kernel/preflight/requirements.py`
- `kernel/preflight/checker.py`
- `kernel/mcp/registry.py`

验收标准：

1. `load_pipeline_skill(skills/uxeval)` 后不再是 `version=0.0.0`
2. `supported_modes` 和 `mcp_servers` 正确加载
3. `designos preflight uxeval --mode web/client` 能正确区分依赖
4. 缺依赖时 preflight 必须失败，不再是假阳性

### Batch 3：修 CLI 假闭环

目标：

- `run / resume / history / input check / mcp install` 至少做到“语义真实”

改动范围：

- `designos/cli/main.py`
- `kernel/workspace/run_manager.py`
- checkpoint / manifest 相关测试

验收标准：

1. `run` 会写 `run.yaml`
2. `history` 能读到真实 run manifest
3. `resume` 真恢复，不只是打印提示
4. `input check` 做结构化检查，不只是目录非空
5. `mcp install` 若暂时不实现，也必须明确返回失败而不是 TODO 成功

### Batch 4：对齐 tool output schema

目标：

- 修复 pipeline outputs 与 tool returns 不一致的问题

改动范围：

- `skills/uxeval/pipeline.yaml`
- `mcp-servers/excel-builder/core.py`
- `mcp-servers/excel-builder/server.py`
- 相关 stage/tool 集成测试

验收标准：

1. Stage 7 声明的 outputs 能被真实返回
2. `issue_report / html_report / evidence_pack` 都有稳定键名
3. 下游 stage / manifest 可直接消费

### Batch 5：替换 client 模式 M1 stub

目标：

- 让 `image-analyzer` 不再只是枚举文件

改动范围：

- `mcp-servers/image-analyzer/*`
- `skills/uxeval/pipeline.yaml`
- client 模式集成测试

验收标准：

1. 至少输出结构化页面观察
2. 支持递归扫描截图目录
3. 返回值能支撑冲突分析与问题归因
4. 不再出现 `mode=stub` 作为主路径结果

### Batch 6：收敛测试、版本线、CI

目标：

- 让仓库重新具备“可自证”能力

改动范围：

- `tests/unit/*`
- `tests/e2e/*`
- `pyproject.toml`
- `.github/workflows/*`
- 版本相关文件

验收标准：

1. 测试不再断言旧版本 `0.1.0`
2. placeholder tests 被替换为真实行为测试
3. `ruff` 错误大幅清零或至少降到可控范围
4. `pyright` 在本地和 CI 都可运行
5. Python / npm / skill version 策略明确

### Batch 7：修 skill 产品化

目标：

- 把 `uxeval` 从“可跑 skill”提升到“可共享 skill”

改动范围：

- `SKILL.md`
- `pipeline.yaml`
- `constitution.md`
- `README.md`
- `INPUT.md`
- `eval/`

验收标准：

1. 单一真源建立
2. `strict / semi-auto / autonomous` 正式化
3. `confidence / coverage / evidence_basis` 进入输出 schema
4. web/client 共用证据协议
5. golden / dirty / failure / autonomous case 齐备

## 3. 额度紧张时的最优停点

如果只能做前 2 个 batch，也值得做。

原因：

- Batch 1 修复“结果真假”
- Batch 2 修复“配置真假”

这两步做完，平台至少从“会误导人”变成“可以继续可信迭代”。

## 4. 新线程建议提示词

### 做 Batch 1

```text
请在 /Users/young/Documents/Codex/Agent-design 中只做 Batch 1：修复 runtime 状态聚合问题。基于 /Users/young/Documents/Codex/desigonos/outputs/agent-design-production-audit.md 和 /Users/young/Documents/Codex/desigonos/outputs/agent-design-repair-batches.md，直接改代码、补测试、跑验证。目标是让失败 skill 不再返回 COMPLETED，checkpoint 返回 PAUSED。
```

### 做 Batch 2

```text
请在 /Users/young/Documents/Codex/Agent-design 中只做 Batch 2：打通 SKILL.md frontmatter 到 preflight 和 MCP registry 的运行时链路。基于 /Users/young/Documents/Codex/desigonos/outputs/agent-design-production-audit.md 和 /Users/young/Documents/Codex/desigonos/outputs/agent-design-repair-batches.md，直接修改代码并补验证。
```

## 5. 最后建议

不要在额度紧张时直接要求“把整个 skills 平台修好”。

最省额度的方式是：

1. 一个线程只做一个 batch
2. 每个 batch 完成后把结果落盘
3. 下一线程只读取：
   - 上一批变更结果
   - 本文件
   - 主审计报告
