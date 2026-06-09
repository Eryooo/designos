# DesignOS Skills Factory Template Master Spec

用途：
- 这是 DesignOS 后续 `web mode` 与剩余 6 个 skills 的最高优先级工厂模板规范
- 它不是建议清单，而是后续开发必须遵守的主控规范
- 目标不是“更快做 skill”，而是“在不牺牲质量的前提下，把 skill 开发从周级压到天级”

---

## 1. 适用范围

本规范适用于：
- `uxeval web mode` 封装
- 后续剩余 6 个 skills 的设计、开发、测试、发布、验收
- 所有需要进入 DesignOS 统一技能体系的 skill

本规范不允许被下游 skill 自行覆盖，只允许：
- 在 archetype 层扩展
- 在 skill-specific 层补充
- 不允许绕开基础契约

---

## 2. 总目标

DesignOS 不是做“能跑的 prompt skill 集合”，而是做“可替代一部分低价值工作的生产级 Skills OS”。

因此后续每个 skill 的目标必须同时满足：

1. `结果质量`
- 主结论必须达到产品可用标准
- 不允许“看起来完整，但质量不足”

2. `自动化程度`
- 系统优先自动完成
- 用户只补系统客观拿不到的信息

3. `边界诚实`
- 达不到交付标准时，不允许冒充完成
- 但也不能变成只会阻断、不提升自动成功率的系统

4. `工厂化复用`
- 不允许每个新 skill 从零重发明输入、证据、交付、benchmark、发布方式

---

## 3. 全局不可违背规则

### 3.1 质量阈值

- normal / final mode 主结论：接近 `99%-100%` 可信
- fallback 正向断言：至少 `85%+`
- 对 `uxeval client mode`：在适用边界内，目标是 `90%+` 覆盖和可信度

### 3.2 自动化优先

顺序必须是：

1. 先提升 AI / tool / MCP / runtime 自动能力
2. 再做 auto-remediation
3. 最后才让用户补最少量信息

不允许把低价值整理劳动重新甩回给用户。

### 3.3 Runtime Truth

不允许：
- 假成功
- 假配置
- 假闭环
- 假产物
- 假证据

所有状态、产物、coverage、confidence、delivery_status 都必须来自 runtime 真相，而不是 prompt 自报。

### 3.4 Batch Discipline

- 一次只允许做一个 batch
- 不扩 scope
- 先看仓库真相，再改代码
- 改完必须：
  - 补测试
  - 跑验证
  - 落盘记录

---

## 4. Skills Factory 八大模板

所有新 skill 必须先对齐这 8 套模板。

### 4.1 Input Contract

必须统一：
- 支持哪些输入对象
- 必填输入
- 可选输入
- scope 定义方式
- preflight 检查逻辑
- 输入不足时的结构化反馈

最低要求：
- 有 machine-readable input schema
- 有最小可运行输入集合
- 有 preflight
- 有 structured supplement actions

### 4.2 Evidence Contract

必须统一：
- inventory
- coverage
- confidence
- evidence_basis
- verification_gap
- trusted / provisional / conflicting / ambiguous

最低要求：
- evidence 必须 machine-readable
- 不同 skill 不得各自发明“证据”结构
- downstream 必须消费统一 evidence 语义

### 4.3 Delivery Contract

必须统一：
- `final_delivery_ready`
- `fallback_safe`
- `supplement_required`
- `blocked`

最低要求：
- 只有 final 才能进入最终主交付
- fallback 不得伪装 final
- supplement 和 blocked 必须可解释、可执行

### 4.4 Runtime Skeleton

必须统一骨架：
- preflight
- planning
- evidence collection
- analysis
- audit
- fallback / bounded package
- artifact packaging
- checkpoint / resume

最低要求：
- 不允许每个 skill 重写执行骨架
- 只允许在骨架内替换 skill-specific stage

### 4.5 Benchmark / Eval Harness

必须统一：
- benchmark summary
- golden cases
- regression baseline
- 指标快照

最低要求：
- 每个 skill 都要能回答“更会做成了还是更会拦了”
- 不允许只说“感觉变强了”

### 4.6 Release Skeleton

必须统一：
- versioning
- install 口径
- release checklist
- validation baseline
- 安全发布链

最低要求：
- 发版前必须有固定验证命令
- release blocker 必须为 0 才能发

### 4.7 Skill Archetype Model

所有 skill 先归类，再开发：

1. `Evaluation 型`
- 复用 evidence / audit / fallback / report

2. `Generation 型`
- 复用 input adapter / artifact packaging / review gate

3. `Workflow / Group 型`
- 复用 orchestration / sub-skill merge / checkpoint / resume

不允许按“skill 名称”直接从零开始。

### 4.8 Production Definition of Done

每个新 skill 必须有统一 DoD：
- 结果质量门槛
- fallback 边界
- 人工介入上限
- benchmark 通过线
- release blocker 为 0

DoD 必须落盘成文档，不允许只存在于聊天里。

---

## 5. Claude Code 的执行约束

Claude Code 接手后，必须把本规范当作上位约束。

必须遵守：
- 先读真源文件，再开始
- 一次只做一个 batch
- 优先用产品语言解释“解决了什么问题”
- 不允许顺手做相邻但未授权的优化
- 不允许为了通过 benchmark 放松 final gate
- 不允许因为模型习惯而重写既有架构方向

Claude Code 不应做的事：
- 重新定义总体路线
- 把 frozen client mode 拉回无限修
- 跳过 benchmark / validation / docs 落盘
- 按单个 skill 喜好重发明契约

---

## 6. 每个新 Skill 的标准开发流程

所有后续 skills 必须按以下顺序：

1. 先归 archetype
2. 绑定八大模板
3. 定义 skill-specific contract
4. 定义 golden cases
5. 只做一个 batch
6. 跑 benchmark / validation
7. 落盘结果
8. 再做下一个 batch
9. 达到 DoD 后 Freeze
10. 才允许进入 release

---

## 7. Freeze 与 Release 条件

一个 skill 只有同时满足这些条件，才允许进入 Freeze / Release：

- final-capable case 全部过线
- bounded-safety case 全部守住边界
- release blocker 为 0
- golden benchmark 可重复
- validation baseline 固化
- 已知边界明确
- 安装口径明确

---

## 8. 反跑偏规则

如果后续任何模型开始出现以下行为，视为跑偏：

- 继续无边界深挖已冻结 skill
- 不断新增功能，但不提升关键指标
- 放松 final gate 来制造“成功率”
- 每个新 skill 重新定义 evidence / delivery / benchmark
- 不落盘、不验证、只在聊天里宣布完成

一旦出现，正确动作是：
- 停止发散
- 回到本规范
- 重建当前 batch 边界

---

## 9. 当前阶段顺序

当前顺序固定为：

1. `client mode` 冻结后人工验收支持
2. `web mode` 封装
3. `Skills Factory Template` 实装化
4. 剩余 6 个 skills 按 archetype 开发

不得跳回去重新长期深挖 frozen client mode，除非出现 release blocker。

---

## 10. 一句话总纲

`后续 6 个 skills 的正确姿势，不是再做 6 次 uxeval，而是以 uxeval 为样板，按统一工厂模板、统一质量标准、统一验证与发布方式，批量复制生产级 skills。`
