# Claude Code Opus Strict Project Instructions

适用项目：
- `/Users/young/Documents/Codex/Agent-design`

用途：
- 作为 Claude Code 的项目级长期约束
- 目标不是省事，而是尽量压低跑偏概率，保持高标准、高质量、按既定路线推进

---

## 1. 绝对优先级

你负责的不是普通代码修复，而是 DesignOS / UXEval 的生产级平台推进。

任何时候，优先级永远是：

1. **不偏离真源**
2. **不破坏已有冻结结论**
3. **不牺牲质量标准换速度**
4. **不重新发散已定方向**

---

## 2. 必读真源文件

开始任何工作前，先读取这些本地文件，不要先凭聊天上下文猜：

### 主控真源
- `/Users/young/Documents/Codex/desigonos/outputs/agent-design-master-repair-charter.md`

### client mode 冻结真源
- `/Users/young/Documents/Codex/Agent-design/docs/releases/client-mode-v1.5-freeze/client_mode_freeze_manifest.json`
- `/Users/young/Documents/Codex/Agent-design/docs/releases/client-mode-v1.5-freeze/client_mode_freeze_notes.md`
- `/Users/young/Documents/Codex/Agent-design/docs/releases/client-mode-v1.5-freeze/client_mode_validation_baseline.md`

### 后续路线真源
- `/Users/young/Documents/Codex/desigonos/outputs/client-mode-90pct-upgrade-roadmap.md`
- `/Users/young/Documents/Codex/desigonos/outputs/client-mode-90pct-metric-tree.md`
- `/Users/young/Documents/Codex/desigonos/outputs/skills-factory-roadmap.md`
- `/Users/young/Documents/Codex/desigonos/outputs/claude-code-opus-handoff-pack.md`

---

## 3. 质量标准

### UXEval 结果标准

- normal mode 进入主结论的内容：接近 `99%-100%` 可信
- fallback 正向断言：至少 `85%+`
- 做不到时：
  - `unknown`
  - `verification_gap`
  - 补资料
  - 调工具/MCP
  - 或阻断

### client mode 当前状态

- `client mode` 已冻结为：`V1.5 pilot baseline`
- 除非明确发现 release blocker，否则不要继续扩展 client mode 新能力

### 交付标准

优先级不是“能跑”，而是：

1. 结果是否可信
2. 边界是否诚实
3. 自动化是否真的替代低价值工作
4. 是否可持续回归和复用

---

## 4. 工作方式

### 一次只做一个 batch

- 不要并行推进多个主题
- 不要顺手扩 scope
- 不要把一个 batch 做成平台大改

### 先仓库真相，后计划

每次开始都先：

1. 读真源文件
2. 看 repo 当前状态
3. 跑最小验证
4. 再定这轮 batch 的边界

### 每轮都要落盘

任何重要推进，至少写入以下之一：

- `docs/plans/...`
- `docs/releases/...`
- `/Users/young/Documents/Codex/desigonos/outputs/...`

不允许只留在会话中。

### 先讲产品影响，再讲技术

每次汇报先回答：

1. 解决了什么产品和用户问题
2. 不解决会怎样
3. 价值大小
4. 为什么必须先修
5. 哪些是长期正确方案
6. 哪些只是过渡方案

---

## 5. 禁止事项

### 禁止重新发散

以下事情不要再重复讨论或重新定义：

- DesignOS 的总目标
- 3 层 / 3+2 分层
- client mode 的 90%+ 路线
- client mode 的 99%-100% / 85%+ 质量线
- client mode 已冻结的事实

### 禁止偷偷放松标准

不允许为了更快通过而：

- 放松 final gate
- 把 provisional/medium 直接当 trusted
- 降低 fallback 可信度要求
- 降低 benchmark 通过线

### 禁止无边界深挖 frozen client mode

如果任务不是明确的 release blocker，不要继续在 client mode 上开新能力战线。

---

## 6. 当前阶段默认顺序

如果用户没有明确改阶段，默认顺序是：

1. 承认并尊重 `client mode freeze`
2. 支持 client mode 的端到端人工验收
3. 转向 `web mode` 封装
4. 再抽 `Skills Factory Template`
5. 再推进剩余 6 个 skills

---

## 7. 工厂化原则

后续 6 个 skills 不能各自重发明一套方法，必须复用这 8 套模板：

1. `Input Contract`
2. `Evidence Contract`
3. `Delivery Contract`
4. `Runtime Skeleton`
5. `Benchmark / Eval Harness`
6. `Release Skeleton`
7. `Skill Archetype Model`
8. `Production Definition of Done`

---

## 8. 默认环境要求

- 工作目录固定为 `/Users/young/Documents/Codex/Agent-design`
- Python 优先使用 repo-local `.venv`
- 验证命令默认使用：
  - `./.venv/bin/python -m pytest ...`
  - `./.venv/bin/python -m ruff check .`
  - `./.venv/bin/python -m pyright`

---

## 9. 当前最重要的执行原则

一句话：

`不要再把时间浪费在重新证明 client mode 是否成熟上，而是把它当成已冻结基线，尽快把后续工作推进到 web mode 和 skills factory。`
