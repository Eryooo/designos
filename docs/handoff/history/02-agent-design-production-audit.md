# Agent-design 平台级生产审计报告

## 1. 审计目标

本次审计不是继续评价单个 `uxeval` 报告写得像不像设计师，而是下钻到 skills 开发仓库 `/Users/young/Documents/claude-code/Agent-design`，判断：

1. 这套平台是否已经具备把 DesignOS skills 做成生产级产品的内核条件
2. 还有哪些遗漏和未察觉的问题，会阻断“比中高级设计师更稳、更高效”的终极目标
3. 哪些问题属于 `uxeval`，哪些已经上升为 `DesignOS 全技能平台` 的系统性缺陷

## 2. 总结结论

当前评级：`L1：原型可演示，不可作为生产级技能平台对外承诺`

原因不是启发式评估思路差，而是平台底座还存在 5 个硬阻断：

1. 运行时会把失败 skill 洗成 `COMPLETED`
2. preflight / frontmatter / MCP 注册这条契约链路是断的
3. CLI 的 `run / resume / history / mcp install` 里有多处“看起来存在，实际上没闭环”
4. MCP 工具输出协议和 pipeline 输出协议没有真正对齐
5. 测试、lint、类型检查、版本线已经漂移，当前仓库不能可靠自证

这意味着：`单次 demo 可以跑通，不等于平台可信。`

## 3. 本次证据

审计方式分为四层：

1. 读平台契约：`README`、架构规范、skill 规范
2. 读关键实现：loader、pipeline engine、stage runner、preflight、MCP transport、CLI
3. 动态验证：实际跑 `pytest`、`ruff`、`pyright`、`designos preflight uxeval`
4. 结果对照：把这次 `uxeval` 自动运行成功经验反向映射到平台底座，找出“成功是靠产品能力，还是靠执行者兜底”

关键动态结果：

- `pytest tests/unit tests/integration -q -p no:cacheprovider`：`1 failed, 169 passed`
- `ruff check . --no-cache`：`189 errors`
- `./.venv/bin/pyright`：本地入口损坏，指向旧路径 `/Users/young/Documents/claude code/Agent-design/.venv/bin/python3`
- `designos preflight uxeval`：输出 `Preflight passed for 'uxeval'.`，但实际加载到的 skill config 为空
- 复现实验：当 tool stage 失败时，`PipelineSkill.run()` 仍返回 `completed`

## 4. P0 级问题

### P0-1：失败状态被洗成 `COMPLETED`，平台最上层结果语义不可信

证据：

- [`PipelineSkill.run()`](/Users/young/Documents/claude-code/Agent-design/kernel/skill_loader/pipeline_loader.py:83) 只是消费 engine 事件流，最后无条件返回 [`RunStatus.COMPLETED`](/Users/young/Documents/claude-code/Agent-design/kernel/skill_loader/pipeline_loader.py:96)
- 但 [`PipelineEngine`](/Users/young/Documents/claude-code/Agent-design/kernel/pipeline/engine.py:111) 在 stage 失败时会直接发出 `stage_failed` 并 `return`
- [`SkillGroup.run_sub_skill()`](/Users/young/Documents/claude-code/Agent-design/kernel/skill_loader/group_loader.py:59) 又直接依赖 `skill.run(ctx)`，所以这个错误会污染 skill group 场景

动态复现：

- 我构造了一个只有一个 tool stage、且 MCP 必然缺失的临时 skill
- engine 日志明确输出了两次 `stage.failed`
- 但最外层 `skill.run(ctx)` 最终打印结果仍是 `completed`

这不是“边角 bug”，而是平台级语义错误。只要上层依赖 `SkillResult.status` 做编排、统计、回归、自动重试或质量门禁，就会被误导。

### P0-2：preflight 是假阳性，skill 规范与运行时未接通

证据链是完整的：

- skill 规范要求 `SKILL.md` frontmatter 提供 `version`、`type`、`requires.mcp_servers`、`modes` 等字段，[规范](/Users/young/Documents/claude-code/Agent-design/docs/architecture/03-Skill-规范.md:50)
- 实际 [`skills/uxeval/SKILL.md`](/Users/young/Documents/claude-code/Agent-design/skills/uxeval/SKILL.md:1) 只有 `name` 和 `description`
- 因此 [`_config_from_frontmatter()`](/Users/young/Documents/claude-code/Agent-design/kernel/skill_loader/pipeline_loader.py:119) 会把 `version` 退回到 `0.0.0`，`supported_modes` 变成空，`mcp_servers` 变成空
- 我直接加载 repo 内 skill，得到的结果是：`{'version': '0.0.0', 'supported_modes': [], 'mcp_servers': []}`
- [`PreflightChecker`](/Users/young/Documents/claude-code/Agent-design/kernel/preflight/checker.py:22) 只调用 [`requirements_from_skill()`](/Users/young/Documents/claude-code/Agent-design/kernel/preflight/requirements.py:25)
- 但 `requirements_from_skill()` 只读 skill 实例上的 `preflight` 属性；[`requirements_from_frontmatter()`](/Users/young/Documents/claude-code/Agent-design/kernel/preflight/requirements.py:39) 虽然存在，却没有被 CLI/loader 接上
- [`MCPRegistry.from_skill_config()`](/Users/young/Documents/claude-code/Agent-design/kernel/mcp/registry.py:22) 也只相信 `skill.config.mcp_servers`
- 结果就是 `designos preflight uxeval` 在 repo 内实际输出“通过”，见 [`preflight()`](/Users/young/Documents/claude-code/Agent-design/designos/cli/main.py:467)

这意味着当前 preflight 不是在判断“依赖是否齐”，而是在判断“空配置有没有报错”。这会制造最危险的一类产品错觉：`看起来安全，其实没检查。`

### P0-3：CLI 有多处伪闭环能力，会误导团队以为平台已可用

#### 1. `run` 不写 manifest

- [`run()`](/Users/young/Documents/claude-code/Agent-design/designos/cli/main.py:211) 只分配 `run_id` 和创建 run 目录，[`RunManager`](/Users/young/Documents/claude-code/Agent-design/kernel/workspace/run_manager.py:22)
- 但全仓搜索可见，[`start_manifest()`](/Users/young/Documents/claude-code/Agent-design/kernel/workspace/run_manager.py:56) 和 [`write_manifest()`](/Users/young/Documents/claude-code/Agent-design/kernel/workspace/run_manager.py:43) 只在测试里被调用，不在真实 CLI 路径里被调用
- 同时 [`history()`](/Users/young/Documents/claude-code/Agent-design/designos/cli/main.py:421) 又依赖 `runs/<id>/run.yaml`

结果：平台提供了 run history 能力的界面，但默认 run 根本不产生 history 所需真数据。

#### 2. `resume` 不是恢复执行，只是打印提示

- [`resume()`](/Users/young/Documents/claude-code/Agent-design/designos/cli/main.py:309) 最终只输出“Use `designos run <skill> --run-id <id>` to re-execute from the checkpoint.”，[关键行](/Users/young/Documents/claude-code/Agent-design/designos/cli/main.py:346)

这不是 resume，而是“告诉用户手动重跑”。

#### 3. `mcp install` 仍是 TODO stub

- [`mcp install`](/Users/young/Documents/claude-code/Agent-design/designos/cli/main.py:670) 只打印 `TODO: mcp install`
- 单元测试还把这个 placeholder 当成预期行为，[测试](/Users/young/Documents/claude-code/Agent-design/tests/unit/test_cli.py:218)

#### 4. `input check` 不是校验输入，只是检查目录非空

- [`input_check()`](/Users/young/Documents/claude-code/Agent-design/designos/cli/main.py:512) 会打印 `INPUT.md`
- 最终真正的判定条件只有 `inputs/` 是否非空，[关键逻辑](/Users/young/Documents/claude-code/Agent-design/designos/cli/main.py:553)

对于一个想要替代低阶设计劳动的平台，这类“命令存在但没有兑现语义”的能力必须被视为 P0，不是 P2。

### P0-4：pipeline 输出契约与 MCP 工具输出契约没有对齐

证据：

- `uxeval` Stage 7 声明输出 `[issue_report, html_report, evidence_pack]`，[pipeline](/Users/young/Documents/claude-code/Agent-design/skills/uxeval/pipeline.yaml:141)
- [`StageRunner._run_tool()`](/Users/young/Documents/claude-code/Agent-design/kernel/pipeline/stage_runner.py:99) 是按 `stage.outputs` 名字直接从 `ToolResult.data` 里逐个取 key，[关键行](/Users/young/Documents/claude-code/Agent-design/kernel/pipeline/stage_runner.py:121)
- 但 [`excel-builder.build_issue_report()`](/Users/young/Documents/claude-code/Agent-design/mcp-servers/excel-builder/core.py:214) 返回只有 `path` 和 `sheet_count`
- [`excel-builder` server](/Users/young/Documents/claude-code/Agent-design/mcp-servers/excel-builder/server.py:51) 只是把这个 dict JSON 化返回

结论非常直接：当前 Stage 7 即使“成功”，也拿不到 skill 声明中的 `issue_report`、`html_report`、`evidence_pack` 三个结构输出。它最多得到一份不知道该挂到哪个 output id 上的通用路径。

这会直接破坏：

- report artifact 索引
- 下游 skill 消费
- manifest 编排
- 自动回归对比

### P0-5：client 证据采集工具仍是 M1 stub，不具备生产级视觉审计能力

证据：

- [`image-analyzer/core.py`](/Users/young/Documents/claude-code/Agent-design/mcp-servers/image-analyzer/core.py:1) 文件头明确写着 `M1 stub implementation`
- 文档说明“`No actual vision analysis is performed`”，[关键行](/Users/young/Documents/claude-code/Agent-design/mcp-servers/image-analyzer/core.py:3)
- 只扫描当前目录，不递归，[关键逻辑](/Users/young/Documents/claude-code/Agent-design/mcp-servers/image-analyzer/core.py:29)
- 最终 `image_analysis` 只返回 `found_count / paths / mode=stub`，[返回值](/Users/young/Documents/claude-code/Agent-design/mcp-servers/image-analyzer/core.py:117)

这与 `uxeval` 在外部承诺的“逐张截图分析、结构化观察、冲突识别、问题归因”存在本质断层。当前成功案例里真正做这些事的，是执行者和通用模型能力，不是 repo 内声明的 client 证据工具链。

## 5. P1 级问题

### P1-1：MCP 协议实现分叉，真实 stdio 路径与 M1 直连捷径不是同一套系统

证据：

- [`StdioTransport`](/Users/young/Documents/claude-code/Agent-design/kernel/mcp/stdio_transport.py:24) 期待 MCP 风格的 `result.content` / `structuredContent`，[关键逻辑](/Users/young/Documents/claude-code/Agent-design/kernel/mcp/stdio_transport.py:146)
- 但 [`pdf-parser/server.py`](/Users/young/Documents/claude-code/Agent-design/mcp-servers/pdf-parser/server.py:56) 和 [`image-analyzer/server.py`](/Users/young/Documents/claude-code/Agent-design/mcp-servers/image-analyzer/server.py:64) 实现的是 repo 自定义 JSON-RPC handler，直接返回 `{"result": result.model_dump()}`
- 同时 [`InProcessTransport`](/Users/young/Documents/claude-code/Agent-design/kernel/mcp/inprocess_transport.py:1) 明确承认自己是 `M1 pragmatic shortcut`，[说明](/Users/young/Documents/claude-code/Agent-design/kernel/mcp/inprocess_transport.py:6)

短期内 repo 之所以还能跑一些内置工具，是因为 in-process 直调绕开了完整协议一致性问题。只要未来切回真实 stdio、多进程打包或跨环境分发，这个分叉会开始集中爆炸。

### P1-2：版本线已经分叉，发布系统没有平台级一致性约束

证据：

- Python 包版本是 `0.1.2`，[`pyproject.toml`](/Users/young/Documents/claude-code/Agent-design/pyproject.toml:1) 与 [`designos/__init__.py`](/Users/young/Documents/claude-code/Agent-design/designos/__init__.py:1)
- npm 包版本是 `0.3.1`，[`npm-package/package.json`](/Users/young/Documents/claude-code/Agent-design/npm-package/package.json:1)
- 单元测试和 e2e 仍在断言 `0.1.0`，[unit](/Users/young/Documents/claude-code/Agent-design/tests/unit/test_cli.py:21) / [e2e](/Users/young/Documents/claude-code/Agent-design/tests/e2e/test_smoke.py:65)
- npm 发布工作流只检查 npm 包和 `install.sh` 版本一致，[workflow](/Users/young/Documents/claude-code/Agent-design/.github/workflows/npm-publish.yml:25)，并不校验 Python 包版本线

这解释了为什么测试会失败，也说明目前 repo 里其实同时存在多条“产品真相”。

### P1-3：测试体系在给 placeholder 背书，而不是给产品能力背书

证据：

- e2e 里明确写着 `init produces some output (TODO placeholder or real output)`，[测试](/Users/young/Documents/claude-code/Agent-design/tests/e2e/test_smoke.py:111)
- `preflight` 测试直接把“placeholder 通过”当成正常结果，[测试](/Users/young/Documents/claude-code/Agent-design/tests/e2e/test_smoke.py:169)
- 导入 smoke test 仍断言 `designos.__version__ == "0.1.0"`，[测试](/Users/young/Documents/claude-code/Agent-design/tests/e2e/test_smoke.py:184)

这类测试不是在防回归，而是在把“未完成实现”制度化。久而久之，团队会默认“只要 CI 绿了就算完成”，但 CI 绿的其实是 placeholder。

### P1-4：仓库健康度链路已经明显失真

证据：

- README 写明所有变更都需要通过 `uv run ruff check .`、`uv run pyright`、`uv run pytest` 三关，[README](/Users/young/Documents/claude-code/Agent-design/README.md:21)
- CI 也确实配置了 `ruff -> pyright -> pytest` 三段门禁，[CI](/Users/young/Documents/claude-code/Agent-design/.github/workflows/ci.yml:12)
- 但当前本地现实是：
  - `pytest`：`1 failed, 169 passed`
  - `ruff`：`189 errors`
  - `pyright`：入口脚本损坏，路径仍指向旧目录 `claude code`

这说明仓库已经从“标准存在”滑向“标准陈列”。一旦进入多人并行维护阶段，质量只会继续失控。

### P1-5：repo 结构复制会持续制造 drift

证据：

- 主 skill 在 `skills/`
- npm 发布又维护一份 `npm-package/skills/`
- 同步脚本直接 `rm -rf` 再 `cp -r`，[脚本](/Users/young/Documents/claude-code/Agent-design/scripts/sync-skills.sh:1)
- npm 发布 workflow 也内联了相同复制逻辑，[workflow](/Users/young/Documents/claude-code/Agent-design/.github/workflows/npm-publish.yml:19)

当前两份内容虽然还能对齐，但这种“双目录复制 + 脚本同步”的结构不是长期生产方案，尤其不适合未来出现多个技能、多版本、多渠道发布时继续扩张。

### P1-6：示例 workspace 无法证明“一个新设计师拿来就能用”

证据：

- 示例工程 [`my-project/designos.project.yaml`](/Users/young/Documents/claude-code/Agent-design/my-project/designos.project.yaml:1) 的 `skills` 是空 dict

这说明 sample workspace 只能证明目录结构存在，不能证明“一个新 workspace 已正确绑定 skill，并可按平台默认路径跑起来”。

## 6. 为什么这些问题会阻断终极目标

终极目标不是“让 skill 偶尔写出一份漂亮报告”，而是：

`让 DesignOS 所有 Skills 稳定替代设计师的低阶重复劳动，并且在组织内被大规模复用。`

上面的 P0/P1 问题会分别卡死四件事：

1. `可信执行`
   - 失败被标成功，组织无法信任自动结果

2. `可信扩散`
   - preflight 是假阳性，换个团队、换个环境就会爆

3. `可信回归`
   - 测试和版本线漂移，无法证明新版本更好

4. `可信消费`
   - 输出 schema 不稳，后续 skill、报表系统、评审流程都接不住

只要这四件事没闭环，平台再多做几个 skill，本质上也只是把 demo 数量变多，不会把生产能力变强。

## 7. 修复优先级

### 第一阶段：两周内必须完成

1. 修复 `PipelineSkill.run()` 聚合逻辑
   - 失败时返回 `FAILED`
   - checkpoint 时返回 `PAUSED`
   - 把 engine 的最终状态正式汇总到 `SkillResult`

2. 打通 frontmatter -> skill config -> preflight -> MCP registry
   - 让 `SKILL.md` 成为真实运行入口，不再只是触发元数据

3. 补齐 CLI 真闭环
   - `run` 写 manifest
   - `resume` 真恢复
   - `mcp install` 不再是 stub
   - `input check` 改成结构化校验

4. 对齐 report tool schema
   - tool 输出必须与 stage `outputs` 一一对应

### 第二阶段：一到两个迭代内完成

1. 去掉 M1 stub，补真实 image analysis / artifact export 契约
2. 统一 stdio MCP 协议，不再依赖 in-process shortcut 掩盖问题
3. 把 Python / npm / skill version 收敛成单一发布线
4. 清理 placeholder tests，重建 production smoke suite

### 第三阶段：平台化门槛

1. 每个 skill 必须有：
   - golden cases
   - dirty cases
   - failure cases
   - autonomous cases

2. 每次发布必须产出：
   - run manifest
   - artifact manifest
   - confidence / coverage / unresolved assumptions

3. 每个共享 skill 默认提供：
   - strict 模式
   - semi-auto 模式
   - autonomous 模式

## 8. 最终判断

如果问题是：

`Agent-design 这套平台现在能不能支撑 DesignOS skills 进入生产级分发？`

答案是：

`不能。当前更像“已有几个成功案例的 alpha 平台”，还不是“可组织化放量的生产平台”。`

如果问题换成：

`这套平台值不值得继续投入？`

答案是：

`值得，而且必须继续投入。`

因为这次深潜得到的结论并不是“方向错了”，而是：

- 方法论层已经有价值
- 单次自动 run 已能证明高价值输出
- 真正缺的是平台工程化、协议收敛、验证基础设施

也就是说，距离“比中高级设计师更稳、更高效”的差距，已经不主要在启发式评估本身，而在平台是否能把这些能力变成可信、可重复、可回归、可共享的产品。
