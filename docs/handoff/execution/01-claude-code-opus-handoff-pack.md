# Claude Code Opus 接管包

目标：让 Claude Code Opus 在接手 `/Users/young/Documents/Codex/Agent-design` 后，尽量保持当前这条线程已经建立的质量标准、交付标准、路线规划和收口节奏，而不是重新发散。

---

## 1. 先说结论

如果你希望 Claude Code Opus 接手后也能达到当前这条线的交付质量，关键不是“模型更强”这一个因素，而是同时做到这 5 件事：

1. 给它稳定的本地环境和固定工具链
2. 给它明确的主控真源文档
3. 给它固定的质量验收标准
4. 给它固定的工作顺序
5. 给它一段足够强的主提示词，防止重新发散

一句话：

`模型能力只是 1/5，真正决定质量的是环境、真源、标准、流程、提示词。`

---

## 2. Claude Code 里必须先满足的配置

### 2.1 工作目录

Claude Code 必须工作在：

- `/Users/young/Documents/Codex/Agent-design`

不要让它在旧路径、复制仓库、镜像仓库或 UI stale cwd 里工作。

### 2.2 Python 环境

必须优先使用 repo-local `.venv`：

- `/Users/young/Documents/Codex/Agent-design/.venv`

后续所有验证命令，默认都走：

```bash
./.venv/bin/python -m pytest ...
./.venv/bin/python -m ruff check .
./.venv/bin/python -m pyright
```

### 2.3 基础命令能力

Claude Code 至少要能稳定执行这些命令：

- `rg`
- `git`
- `pytest`
- `ruff`
- `pyright`
- `compileall`

如果这些命令路径不稳，要优先修环境，不要先修代码。

### 2.4 本地文件读写权限

必须确保 Claude Code 能稳定读取这些目录：

- `/Users/young/Documents/Codex/Agent-design`
- `/Users/young/Documents/Codex/desigonos/outputs`
- `/private/tmp`

因为当前很多 benchmark / freeze / sweep 样例都落在这几个位置。

---

## 3. Claude Code 里必须能读取的真源文件

Claude Code 接手时，不要让它重新从聊天里理解世界观，先读这些本地文件。

### 3.1 主控真源

- [`/Users/young/Documents/Codex/desigonos/outputs/agent-design-master-repair-charter.md`](/Users/young/Documents/Codex/desigonos/outputs/agent-design-master-repair-charter.md)

这是总章程。

### 3.2 client mode 冻结结论

- [`/Users/young/Documents/Codex/Agent-design/docs/releases/client-mode-v1.5-freeze/client_mode_freeze_manifest.json`](/Users/young/Documents/Codex/Agent-design/docs/releases/client-mode-v1.5-freeze/client_mode_freeze_manifest.json)
- [`/Users/young/Documents/Codex/Agent-design/docs/releases/client-mode-v1.5-freeze/client_mode_freeze_notes.md`](/Users/young/Documents/Codex/Agent-design/docs/releases/client-mode-v1.5-freeze/client_mode_freeze_notes.md)
- [`/Users/young/Documents/Codex/Agent-design/docs/releases/client-mode-v1.5-freeze/client_mode_validation_baseline.md`](/Users/young/Documents/Codex/Agent-design/docs/releases/client-mode-v1.5-freeze/client_mode_validation_baseline.md)

这 3 个文件是当前 client mode 的冻结边界。

### 3.3 后续路线真源

- [`/Users/young/Documents/Codex/desigonos/outputs/client-mode-90pct-upgrade-roadmap.md`](/Users/young/Documents/Codex/desigonos/outputs/client-mode-90pct-upgrade-roadmap.md)
- [`/Users/young/Documents/Codex/desigonos/outputs/client-mode-90pct-metric-tree.md`](/Users/young/Documents/Codex/desigonos/outputs/client-mode-90pct-metric-tree.md)
- [`/Users/young/Documents/Codex/desigonos/outputs/skills-factory-roadmap.md`](/Users/young/Documents/Codex/desigonos/outputs/skills-factory-roadmap.md)
- [`/Users/young/Documents/Codex/desigonos/outputs/designos-phase-order-and-stop-conditions.md`](/Users/young/Documents/Codex/desigonos/outputs/designos-phase-order-and-stop-conditions.md)
- [`/Users/young/Documents/Codex/desigonos/outputs/skills-factory-template-master-spec.md`](/Users/young/Documents/Codex/desigonos/outputs/skills-factory-template-master-spec.md)
- [`/Users/young/Documents/Codex/desigonos/outputs/claude-code-opus-governor-spec.md`](/Users/young/Documents/Codex/desigonos/outputs/claude-code-opus-governor-spec.md)
- [`/Users/young/Documents/Codex/desigonos/outputs/skills-development-best-practices-and-anti-patterns.md`](/Users/young/Documents/Codex/desigonos/outputs/skills-development-best-practices-and-anti-patterns.md)

这些文件共同构成：
- 阶段顺序真源
- 工厂模板真源
- Claude 执行约束真源
- 开发经验 / 反模式真源
- 指标理论依据真源

---

## 4. Claude Code 必须遵守的质量标准

这部分最重要，不能丢。

### 4.1 `uxeval` 输出标准

- normal mode 主结论：接近 `99%-100%` 可信
- fallback 正向断言：至少 `85%+`
- 做不到时：
  - `unknown`
  - `verification_gap`
  - 补资料
  - 调工具/MCP
  - 或阻断

### 4.2 client mode 目标线

- 目标不是“能跑”
- 目标不是“会 fallback”
- 目标是：`在适用边界内逼近 90%+ 覆盖和可信度`

### 4.3 当前 client mode 冻结结论

当前已经是：

- `client mode V1.5 freeze candidate / frozen_for_pilot`

所以 Claude Code 后续**不应继续无限修 client mode**。  
默认应该：

1. 先承认 client mode 已冻结
2. 做你的端到端验收支持
3. 转向 web mode
4. 再做 skills factory template

### 4.4 指标体系是理论依据，不是附属文档

[`/Users/young/Documents/Codex/desigonos/outputs/client-mode-90pct-metric-tree.md`](/Users/young/Documents/Codex/desigonos/outputs/client-mode-90pct-metric-tree.md) 不只是参考材料，而是后续判断“为什么这个 batch 值得做、为什么这次提升是真的”的理论依据。

Claude Code 后续每一批都必须明确回答：
- 当前主攻哪些关键指标
- 为什么先攻这些指标
- 这次是让系统更会做成，还是只是更会拦
- 对 90%+ 目标的直接贡献是什么

---

## 5. Claude Code 必须遵守的工作方法

### 5.1 一次只做一个 batch

不要发散，不要一次做很多方向。

### 5.2 先看仓库真相，再说计划

优先顺序：

1. 读本地文件
2. 看 git/workspace 当前状态
3. 跑最小验证
4. 再决定下一步

### 5.3 产品语言优先

每次汇报都先说：

1. 解决了什么产品/用户问题
2. 不解决会怎样
3. 价值大小
4. 为什么必须先修
5. 哪些是长期正确方案
6. 哪些只是当前过渡方案

### 5.4 不允许继续“会拦不会做”

任何后续改动都必须同时回答：

- 是不是提升了自动做成率
- 还是只是让 gate 更严格了

### 5.5 所有结论都要落盘

不能只留在会话里。  
每轮重要结论至少要写到：

- `docs/plans/...`
- 或 `docs/releases/...`
- 或 `/Users/young/Documents/Codex/desigonos/outputs/...`

### 5.6 必须继承已有工程经验，不允许重复踩坑

Claude Code 必须阅读并遵守：
- [`/Users/young/Documents/Codex/desigonos/outputs/skills-development-best-practices-and-anti-patterns.md`](/Users/young/Documents/Codex/desigonos/outputs/skills-development-best-practices-and-anti-patterns.md)

它的作用是避免：
- 重新出现假成功 / 假配置 / 假闭环 / 假证据
- 重新把 naming 变成门槛
- 重新变成“只会拦不会做”
- 重新让每个 skill 重发明一套方法

---

## 6. Claude Code 接手时建议启用/安装的能力

### 6.1 必要能力

不是指模型插件，而是最少必须具备的工作能力：

- 稳定 shell 执行
- 稳定读写本地文件
- 稳定跑 Python / pytest / ruff / pyright
- 稳定读 markdown / json / yaml

### 6.2 如果 Claude Code 支持本地技能/规则文件

建议至少放进 3 类约束：

1. `DesignOS 平台章程`
- 强制它先读主控章程

2. `UXEval 质量标准`
- 强制它遵守 `99%-100% / 85%+ / 90%+` 这三条线

3. `Batch 工作法`
- 强制它一次只做一个 batch，不得发散

如果 Claude Code 支持 Project Instructions，优先把这些写进去。

---

## 7. Claude Code 推荐的最小 Project Instructions

可以放一版类似下面的项目级规则：

```text
你当前负责的不是普通代码修复，而是 DesignOS/UXEval 的生产级平台演进。

必须遵守：
1. 先读本地真源文件，再行动：
   - /Users/young/Documents/Codex/desigonos/outputs/agent-design-master-repair-charter.md
   - /Users/young/Documents/Codex/Agent-design/docs/releases/client-mode-v1.5-freeze/client_mode_freeze_manifest.json
   - /Users/young/Documents/Codex/Agent-design/docs/releases/client-mode-v1.5-freeze/client_mode_freeze_notes.md
   - /Users/young/Documents/Codex/Agent-design/docs/releases/client-mode-v1.5-freeze/client_mode_validation_baseline.md
2. normal mode 主结论必须接近 99%-100% 可信；fallback 正向断言也必须 >= 85%
3. client mode 当前已冻结为 V1.5 pilot baseline，不要继续无边界深挖 client mode
4. 后续重点转向 web mode 封装，再转向 Skills Factory Template
5. 一次只做一个 batch，不要扩 scope
6. 先给产品/用户影响，再讲技术实现
7. 每次重要变更都要落盘，不允许只留在聊天里
```

---

## 8. Claude Code 高质量接管主提示词

这是你最应该直接给 Claude Code Opus 的主提示词：

```text
请接管 /Users/young/Documents/Codex/Agent-design 的后续工作，但不要重新发散分析，也不要从头定义方向。先读取这些本地真源文件：

- /Users/young/Documents/Codex/desigonos/outputs/agent-design-master-repair-charter.md
- /Users/young/Documents/Codex/Agent-design/docs/releases/client-mode-v1.5-freeze/client_mode_freeze_manifest.json
- /Users/young/Documents/Codex/Agent-design/docs/releases/client-mode-v1.5-freeze/client_mode_freeze_notes.md
- /Users/young/Documents/Codex/Agent-design/docs/releases/client-mode-v1.5-freeze/client_mode_validation_baseline.md
- /Users/young/Documents/Codex/desigonos/outputs/client-mode-90pct-upgrade-roadmap.md
- /Users/young/Documents/Codex/desigonos/outputs/client-mode-90pct-metric-tree.md
- /Users/young/Documents/Codex/desigonos/outputs/skills-factory-roadmap.md

然后遵守以下工作规则：

1. 不要重新发散产品方向。以本地文件为单一真源。
2. normal mode 主结论必须接近 99%-100% 可信；fallback 正向断言也必须 >= 85%。
3. client mode 当前已经冻结为 V1.5 pilot baseline。不要继续无限修 client mode，除非我明确要求。
4. 当前优先级应转向：
   - 支持 client mode 的端到端人工验收
   - web mode 封装
   - 然后抽 Skills Factory Template
5. 一次只做一个 batch，不要扩 scope。
6. 先用产品/用户语言说明问题，再讲技术实现。
7. 任何重要结论都要落盘到仓库或 /Users/young/Documents/Codex/desigonos/outputs。

如果当前任务没有明确指定，请默认从“web mode 封装”的最小可执行 batch 开始，并先做仓库真相检查、最小验证、再给出一个单批次推进方案。
```

---

## 9. Claude Code 接手后第一步该做什么

最优顺序：

1. 读取真源文件
2. 跑 client mode freeze baseline 最小验证
3. 明确承认 client mode 已冻结
4. 开始规划 `web mode` 的第一批

也就是：

`不要让 Claude Code 再花很多额度重新证明 client mode 是否成熟，而是让它先接过 Freeze 结论，再切下一阶段。`

---

## 10. 一句话收口

`为了让 Claude Code Opus 也达到当前这条线的交付质量，最重要的不是多装几个工具，而是给它：稳定本地环境 + 单一真源 + 固定质量标准 + 固定批次工作法 + 强约束主提示词。`
