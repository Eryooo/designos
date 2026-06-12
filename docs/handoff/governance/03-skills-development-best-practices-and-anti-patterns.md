# DesignOS Skills Development Best Practices and Anti-Patterns

用途：
- 这是基于 `uxeval` 从 runtime 修复到 `client mode V1.5 freeze` 全过程提炼出来的最佳实践和反模式清单
- 目标不是复盘历史，而是让后续 `web mode` 和剩余 6 个 skills 不再重走弯路
- Claude Code Opus 应将本文件视为“工程经验约束”，与主控章程、Factory Template、Governor Spec 共同使用

---

## 1. 先说结论

后续 skill 开发中，最重要的不是“先把功能堆出来”，而是：

1. 先把真源、边界、交付状态说清楚
2. 先修 runtime truth，再修 prompt/文案/表层体验
3. 先提升 first-pass success，再去强化 gate
4. 先抽共性模板，再做 skill-specific 差异

一句话：

`不要做会演示的 skill，要做能真实替代低价值工作的生产级 skill。`

---

## 2. 最佳实践

### 2.1 先修 Runtime Truth

优先级顺序必须是：
- 状态真假
- 配置真假
- 产物真假
- 证据真假
- 再到 prompt 与文案

原因：
- 如果 runtime truth 不成立，后面所有“看起来更强”的分析都建立在假地基上

具体表现：
- status 必须来自 runtime terminal event
- preflight 必须消费真实 config / mode / MCP
- artifacts 必须是运行时真实产物
- evidence 必须 machine-readable，不靠口头声明

### 2.2 先做自动化成功率，再做安全阻断

正确顺序：
1. 提升 ingestion
2. 提升 fusion
3. 提升 critical-path coverage
4. 提升 remediation
5. 最后用 gate 卡最终交付

错误顺序：
- 只会拦，不会做成

### 2.3 优先围绕主链路，不围绕平均质量

评价标准不应是：
- 分析了多少页面
- 输出了多少问题

而应是：
- P0/P1 主链路有没有覆盖
- 关键状态有没有拿到
- 能不能支撑 final delivery

### 2.4 把用户介入压缩成最少量高回报动作

好方案：
- 一次 clarification
- 一次 targeted acquisition
- 一次结构化 supplement request

坏方案：
- 多轮零散确认
- 要求用户批量重命名
- 要求用户手写整套 mapping

### 2.5 所有质量提升都要能被 benchmark 看到

如果一个改动不能在 benchmark / metrics 里体现真实提升，它很可能不是优先级最高的改动。

每次 batch 都应该回答：
- 拉升了哪个指标
- 提升了多少
- 是更会做成了，还是更会拦了

### 2.6 先 Freeze，再切阶段

skill 一旦达到阶段收工线，就应该 Freeze：
- 固化 baseline
- 固化 benchmark
- 固化已知边界
- 转向下一阶段

不要继续在同一条线无限打磨。

---

## 3. 反模式清单

### 3.1 假成功

表现：
- 实际失败/暂停，却显示 completed

后果：
- 破坏所有后续判断

### 3.2 假配置

表现：
- SKILL.md / mode / MCP 配置存在，但 runtime 没真正消费

后果：
- preflight 假阳性
- mode 差异失真

### 3.3 假闭环

表现：
- run/history/resume 看起来有，但 manifest / checkpoint / final status 不真

后果：
- 用户以为系统可恢复、可追溯，实际不成立

### 3.4 假证据

表现：
- screenshot analysis 假装理解页面语义
- 用低证据内容输出高确定性结论

后果：
- 直接误导业务判断

### 3.5 只会拦，不会做

表现：
- gate 非常严格
- final 很难过
- 但前面 ingestion/fusion/remediation 提升不明显

后果：
- 系统很安全，但没法替代工作

### 3.6 只会做，看起来做成了，但质量不够

表现：
- 为了提高通过率，放松 trusted evidence / final gate

后果：
- 看起来可用，实则破坏产品可信度

### 3.7 每个 skill 重发明一套方法

表现：
- 新 skill 重新定义 input/evidence/delivery/benchmark/release

后果：
- 周期爆炸
- 无法工厂化

### 3.8 只在聊天里宣布完成

表现：
- 没有 docs/plans / docs/releases / outputs 落盘

后果：
- 别的模型无法稳定接管
- 回归和发布都不可追溯

---

## 4. 从 `uxeval` 提炼出的关键经验

### 4.1 Naming 是加速器，不是门槛

正确做法：
- OCR / markdown / mapping 优先
- naming 只做 accelerator

### 4.2 Clarification 不是越少越好，而是越少越值钱越好

正确做法：
- 只确认少量歧义
- 且这些歧义要能推进 critical path 或 final delivery

### 4.3 Fallback 不是失败，而是边界清晰的安全交付

前提：
- 不得伪装 final
- 只能输出高确定性内容

### 4.4 Benchmark 不是报告附件，而是迭代驱动器

正确做法：
- 每个 batch 都用 benchmark 定位瓶颈
- 不是“先想功能，再看看有没有提升”

### 4.5 Freeze 不是停止演进，而是防止无限修同一条线

正确做法：
- 达到 freeze line 就冻结
- 然后转到下一阶段

---

## 5. 后续 `web mode` 与 6 个 skills 的使用方式

Claude Code Opus 在开发后续阶段时，应该这样使用本经验文档：

1. 先查这次需求是否命中了已知反模式
2. 先确认是不是需要先补 runtime truth
3. 先确认这次改动主要提升哪个 benchmark 指标
4. 先确认是否能复用 Factory Template，而不是重发明

如果不能明确回答这 4 个问题，就不应该直接动手扩代码。

---

## 6. 一句话总纲

`后续 skill 开发的最佳实践不是“更会生成代码”，而是“更少走弯路、更早对齐真相、更快 Freeze、更多复用模板”。`
