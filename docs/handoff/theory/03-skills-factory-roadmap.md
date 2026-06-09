# DesignOS Skills Factory 路线

日期：2026-05-25

## 一句话结论

第一支生产级 skill 做得慢是正常的。  
如果第 2 到第 7 支 skill 还和今天一样慢，那就说明不是 skill 难，而是平台没有被工厂化。

## GitHub 上那些“看起来很牛”的 skills，通常分两类

### 第一类：看起来很快，其实是 prompt 包装

特点：
- 很快能发出来
- 演示效果漂亮
- 依赖人工补上下文
- 边界控制弱
- 很少做 runtime gate / audit / fallback / eval

优点：
- 上线快
- 适合 demo 和传播

缺点：
- 很难稳定替代真实工作
- 一旦输入复杂就失真

### 第二类：真正能复用、能规模化的 skill system

特点：
- 不只是 prompt
- 有输入契约、工具契约、产物契约
- 有 preflight、gate、audit、fallback、resume、eval
- 有共享 MCP 和共享数据结构
- 首支 skill 周期长，但后面会越来越快

这类系统表面上不一定“炫”，但真正能进组织内部长期使用。

## 你现在做的是哪一类

你现在显然做的是第二类。  
这也是为什么周期会长。

当前 `uxeval` 已经不只是一个 prompt skill，而是：
- 有 runtime
- 有 stage pipeline
- 有 evidence contract
- 有 delivery audit
- 有 fallback package
- 有 cross-tool distribution

这不是普通 GitHub skill 的复杂度。

## 为什么现在感觉周期长

因为你同时在做三件事：

1. 做一支 skill
2. 做一套 skill runtime
3. 做一条 skills OS 的生产方法论

如果这三件事同时混在一条线上，第一支一定慢。

## 什么时候算“慢得不合理”

不是现在慢不合理。  
真正不合理的是：

- 第 2 支 skill 还要重新发明 preflight
- 第 2 支 skill 还要重新发明 evidence schema
- 第 2 支 skill 还要重新发明 fallback / audit / resume
- 第 2 支 skill 还要重新讨论 naming、coverage、delivery gate

也就是说：

`uxeval 可以慢，但不能让后面 6 个 skills 继续按 uxeval 的方式重走一遍。`

## 后面怎么提速

## 阶段 1：先把 uxeval 收口，不再无限打磨

目标：
- 把 client mode 拉到你认可的可用线
- 同时保住 web mode 后续封装空间

做法：
- 只做最高杠杆的几批
- 不再继续零散打补丁
- 一旦达到 V1.5 结束线，就冻结为模板来源

## 阶段 2：把 uxeval 提炼成 Factory Template

这一步比继续修更多单点更值钱。

要抽出来的，不是 prompt，而是这些共性：

1. `Input Contract`
- PRD
- screenshots
- optional description/map/index
- scope

2. `Evidence Contract`
- inventory
- coverage
- verification_gap
- confidence
- evidence_basis

3. `Delivery Contract`
- final_delivery_ready
- fallback_safe
- supplement_required
- blocked

4. `Runtime Skeleton`
- preflight
- planning
- evidence collection
- issue detection
- audit
- fallback
- artifact packaging

5. `Release Skeleton`
- versioning
- npm/PyPI distribution
- cross-tool install
- test gates

## 阶段 3：定义 6 个 skills 的“类型”，不要逐个从零做

后面的 skills 不应该按“skill 名称”开发，而应该按“skill archetype”开发。

建议只分 3 类：

### A. Evaluation 型
例如：
- uxeval
- design-acceptance
- ai-analytics 类

复用最多：
- evidence
- audit
- fallback
- report

### B. Generation 型
例如：
- prd2proto
- brand / creative / 页面生成类

重点复用：
- input adapter
- artifact packaging
- review gate

### C. Workflow / Group 型
例如：
- 多 skill 串联
- 复杂品牌链路
- 多阶段设计交付链路

重点复用：
- orchestration
- sub-skill result merge
- checkpoint / resume

这样后面不是“再做 6 个 skills”，而是：
- 先做 3 个 archetype
- 再实例化 6 个 skills

## 阶段 4：把“修 skill”改成“装配 skill”

真正提速的标志不是：
- 改 prompt 更快了

而是：
- 一个新 skill 只需要填模板
- 共享 MCP 直接挂上
- preflight 自动生成
- report schema 自动沿用
- audit/fallback 自动沿用

到这一步，新的 skill 周期才会从“周级”压到“天级”。

## 我建议你的实际节奏

### 现在
1. 快速闭环 `uxeval client mode`
2. 不再无限细修
3. 同步规划 `web mode`

### 紧接着
4. 从 `uxeval` 中抽 `Factory Template`
5. 写清哪一层是：
- skill-specific
- shared platform
- MCP capability

### 再之后
6. 先做 1 个新的 Evaluation 型 skill
7. 验证 factory 是否真的让第二个 skill 明显变快

### 最后
8. 再批量推进剩余 5 个 skills

## 你现在最该避免的事

- 每个 skill 都做一遍深度手工打磨
- 每个 skill 都重新发明输入契约
- 每个 skill 都重新决定 fallback 规则
- 每个 skill 都重新做一套安装/发布/测试方法

如果这样做，工程一定会拖很久。

## 最终判断

当前周期长，不代表方向错。  
它只说明：

`你现在做的已经不是一个普通 skill，而是一套生产级 skills OS 的第一颗样板弹。`

第一颗样板弹慢是正常的。  
真正的关键不是这次慢，而是：

`从下一支 skill 开始，必须明显更快。`
