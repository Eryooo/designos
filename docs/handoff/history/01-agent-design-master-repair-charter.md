# Agent-design 主控修复章程

## 1. 这份文件的作用

这不是普通报告，而是后续所有修复线程的 `单一真源`。

目标：

1. 把今天这次会话里形成的产品判断、架构判断、修复优先级固化下来
2. 避免后续线程重复理解、重复争论、重复走偏
3. 让 Codex 在新线程里可以直接按本章程推进，而不是重新分析一遍

适用项目：

- `/Users/young/Documents/Codex/Agent-design`

## 2. 最终目标

DesignOS 不是做一个“会写报告的 skill 集合”，而是做一个：

`可替代低阶设计师、可替代低阶重复设计工作、可在集团内部共享、可持续自主进化的 Skills OS`

这里的“替代”必须精确定义为：

- 替代低阶、重复、可标准化、可证据化的设计工作单元
- 不追求一开始替代高级设计师的判断力
- 先替代“流程性劳动”，再逐步逼近“分析性劳动”

## 3. 产品定义冻结

### 3.1 对外产品定义

DesignOS 是：

- 装到设计师工作流里的能力包
- 以 IDE 对话为主入口的 Skills OS
- 面向集团内共享的设计生产力基础设施

DesignOS 不是：

- 独立 Web App
- 单次项目交付物
- 只会写 Prompt 的模板库
- 一开始就试图替代所有设计工作的大而全 AI

### 3.2 v1 黄金路径

必须优先确保下面这条路径极稳：

`设计师在 IDE 中输入 /uxeval，提供 PRD + 截图或 URL，10 分钟内拿到可分享的结构化评估结果，零额外配置，零手工建目录。`

任何不直接增强这条黄金路径的能力，在 v1 都不是最高优先级。

## 4. 架构定义冻结

### 4.1 用户心智模型：坚持三层

对设计师、业务方、集团内部传播，统一使用三层心智模型：

1. `Skills Layer`
2. `Kernel / Runtime Layer`
3. `MCP Capability Layer`

不要再向用户暴露更多层级。

### 4.2 工程真实分层：采用 3+2

工程上按 `3+2` 理解：

1. `Skill Experience Layer`
   - skill 定义、methodology、prompt、constitution、templates、modes

2. `Runtime Layer`
   - pipeline、checkpoint、state machine、artifact、tool broker

3. `Capability Layer`
   - 共享 MCP / shared tools

4. `Evolution Plane`
   - eval、golden/failure、自动优化、回放、质量回归

5. `Governance Plane`
   - 三级记忆晋升、脱敏、审批、版本、发布、灰度、回滚

原则：

- 前 3 层属于 `执行面`
- 后 2 层属于 `控制面`
- 控制面不能压垮执行面

## 5. 必须保留的核心设计

以下方向全部保留，不推翻：

1. `IDE-first`
   - 设计师主入口应始终是 IDE 对话，不是命令行

2. `一套执行流程`
   - IDE slash command 和 CLI 只是两个触发入口，不是两套产品

3. `共享 MCP 解耦`
   - 任意会被两个及以上 skill 复用的能力，优先做成共享 capability

4. `三级记忆`
   - Session -> Project -> Organization 的方向保留
   - 但必须是“晋升制”，不能是“任意写入共享记忆”

5. `Eval 飞轮`
   - golden / failure / 回放 / 回归 / prompt 优化 是长期必须能力

6. `Skill 双形态`
   - Pipeline Skill 保留
   - Skill Group 形态保留，但先冻结接口，不急着做满能力

## 6. 必须修正的核心偏差

### 6.1 先修“平台语义”，再修“技能效果”

当前最危险的问题不是 prompt 弱，而是平台会误报成功。

必须先修：

1. runtime 状态聚合
2. frontmatter -> preflight -> MCP registry 链路
3. CLI 真闭环
4. tool output schema
5. image-analyzer stub

### 6.2 schema-first 优先于 skill-count-first

当前比新增 skill 更重要的是先冻结共享数据契约。

至少冻结这些对象：

1. `InputManifest`
2. `Evidence`
3. `Observation`
4. `Finding`
5. `Conflict`
6. `ArtifactManifest`
7. `RunManifest`
8. `MemoryRecord`
9. `EvalCase`

没有这一层，skills OS 不会真正成立。

### 6.3 执行面和控制面分离

`memory / eval / governance` 都需要，但不要把它们塞进一次 run 的主执行路径里。

执行面追求：

- 短
- 稳
- 易验证

控制面追求：

- 可晋升
- 可审计
- 可回归

## 7. Skill Group 的处理原则

判断：

- 现在完全不考虑 Skill Group，后续确实可能融不进去
- 但现在就做满 Group workflow / parallel / group state，会拖垮 v1

因此采用：

`协议先冻，能力后开`

现在必须冻结：

1. `GROUP.md`
2. `WorkflowConfig`
3. `WorkflowStep`
4. group artifact merge 规则
5. group state namespace 约定

现在暂时不做满：

1. 复杂并行调度
2. group 级恢复
3. 跨子技能共享可变状态
4. brand-creative 全量 workflow

## 8. 阶段规划冻结

### P0：Freeze the OS Contract

先冻结：

- runtime 状态语义
- shared schema
- skill manifest
- tool return contract
- memory promotion contract

目标：

- 以后所有 skill 都按这一套长

### P1：Evaluation OS v1

只优先做评估线平台：

1. `uxeval`
2. `design-acceptance`
3. `ai-analytics`

原因：

- 三者最共享证据链
- 最容易替代低阶劳动
- 最适合在集团内部放量

### P2：Evolution OS

把这些做实：

- golden/failure 回归
- 失败样本晋升
- 自动评测
- prompt 优化
- 三级记忆晋升

### P3：Multi-skill OS

最后再开：

- Skill Group
- workflow orchestration
- parallel sub-skills
- cross-skill artifact composition

## 9. 生产级 Definition of Done

DesignOS 要宣称“生产级可替代低阶工作”，至少满足：

1. `结果真实`
   - 失败不会被标成功

2. `配置真实`
   - preflight 不是假阳性

3. `输出可消费`
   - artifact / evidence / finding schema 稳定

4. `可分享`
   - 默认脱敏
   - 默认适合业务分享

5. `可回归`
   - golden / failure / dirty / autonomous cases 齐备

6. `可进化`
   - run 结果能进入评测与晋升链路

7. `设计师零低阶配置`
   - 不要求重复配 key
   - 不要求先学 CLI
   - 不要求先建目录

## 10. 接下来新线程必须优先读取的文件

按顺序：

1. `/Users/young/Documents/Codex/desigonos/outputs/agent-design-master-repair-charter.md`
2. `/Users/young/Documents/Codex/desigonos/outputs/agent-design-production-audit.md`
3. `/Users/young/Documents/Codex/desigonos/outputs/uxeval-production-readiness-audit.md`
4. `/Users/young/Documents/Codex/desigonos/outputs/agent-design-repair-batches.md`
5. `/Users/young/Documents/Codex/desigonos/outputs/agent-design-optimization-handoff.md`

## 11. 新线程执行原则

1. 不要先优化 prompt 文案
2. 不要先新增 skill 数量
3. 不要先扩展 Skill Group 能力
4. 先修平台 P0，再修 skill P1
5. 每个线程只做一个 batch，做完立即落盘验证结果

## 12. 你在 Agent-design 新线程里要说的话

见：

- `/Users/young/Documents/Codex/desigonos/outputs/agent-design-next-thread-prompt.md`
