# Reference: PRD 结构化理解（m01）

> Stage 01 `prd-understanding` 的方法论与约束库。pipeline 在执行 stage 时会把本文件 lazy-load 到 LLM 上下文。

## 方法论：用户故事 + 信息架构基本原则

### 1. PRD 拆解的三层结构

把 PRD 拆成 modules → key_features → pages → user_flows，对应**自顶向下**的产品视角：

```
business_goal (一句话)
    │
    ├─ modules (业务能力域，3-15 个)
    │   │
    │   ├─ key_features (具体功能点，每个挂到 module)
    │   │
    │   └─ pages (UI 承载，每个挂到 module)
    │
    └─ user_flows (跨模块的端到端任务流)
```

这个结构来自 **Jeff Patton 的 Story Mapping** 思想：
- backbone（modules）= 用户的主要活动
- walking skeleton（key_features + pages）= 完成活动需要的最小动作
- user_flows = 用户实际做事的横向切片

### 2. INVEST 原则（user story 拆分）

每个 `key_feature` 应满足：

| 字母 | 含义 | 在本 stage 的体现 |
|---|---|---|
| **I** ndependent | 独立 | 一个 feature 描述清楚不需要其他 feature 上下文 |
| **N** egotiable | 可协商 | 推断的 acceptance 标 `[inferred]`，让 PM 在 C1 改 |
| **V** aluable | 有价值 | `user_value` 字段必须填，不能写"系统功能" |
| **E** stimable | 可估算 | 描述具体到能让前端估开发量 |
| **S** mall | 小 | 一个 feature 不超过 3 行描述；过长就拆 |
| **T** estable | 可测试 | `acceptance` 必须是可验证的（"草稿仍在"而非"用户体验良好"） |

### 3. 信息架构基本原则（IA 5 步法 / Rosenfeld）

stage 01 不直接产出 IA（那是 stage 02 的事），但 `pages` 已经是 IA 的原材料：

- **Page = 信息消费单元**（用户在一个 URL 内完成一个或一组目标）
- **page_type 枚举**：list / form / detail / dashboard / wizard / settings / auth / error
- **path 命名约定**：复数名词（`/rules` 不是 `/rule-list`）；动词不进 path（`/rules/new` 不是 `/createRule`）

### 4. 关键路径识别（Critical Path）

`user_flows[].is_critical_path = true` 的标准：

- 直接对应 `business_goal` 的核心动词（如"规则上线效率提升 3x" → 关键路径就是"新建规则到上线"）
- 跨 ≥ 2 个 module
- 在 PRD 中用例数 > 1（PRD 反复提的就是关键路径）

## 输出字段约束库

### modules

| 维度 | 约束 |
|---|---|
| 数量 | 1-15（超过 15 通常是过度拆分；少于 3 通常是 PRD 太薄） |
| id 格式 | `M-001` 三位顺序编号 |
| name | 名词短语，2-6 个汉字或 2-4 个英文词；避免动词 |
| priority | `P0` / `P1` / `P2`，从 PRD 推；PRD 没明说时全 P0 |
| page_ids | 必须与 `pages[].id` 对得上 |

### key_features

| 维度 | 约束 |
|---|---|
| 数量 | 3-30 |
| 必填 | id / name / module_id / description / user_value |
| description | 一句话动词开头："新增/编辑/查看/删除/批量..." |
| acceptance | 数组，每条可验证；`[inferred]` 标记必须保留 |

### pages

| 维度 | 约束 |
|---|---|
| 数量 | 2-50 |
| path | `/xxx`、`/xxx/:id`、`/xxx/:id?` 三种形式 |
| page_type | 枚举见上 |
| primary_actions | 1-5 个，按页面用户最可能做的动作排序 |
| navigates_to | 列出本页能跳到哪些其他 page_id |

### user_flows

| 维度 | 约束 |
|---|---|
| 数量 | 1-10 |
| steps 长度 | 2-8 步；超过 8 步通常是流程没拆好 |
| 每步必填 | step（序号）/ page_id（在哪个页面）/ action（做什么）/ expected（期望结果） |
| critical_path | 至少有 1 个 `is_critical_path: true` |

## 常见陷阱

### 陷阱 1：替 PM 写需求

❌ PRD 没提"导入 Excel"，但你觉得"B 端规则管理通常都有"，于是加进 key_features。
✅ 不写。如果你强烈认为缺失，写到 `warnings`：`"PRD 未提批量导入功能，建议 PM 评估"`。

### 陷阱 2：把"PRD 章节标题"当 module

❌ PRD 第 4 章叫"非功能需求"，你把它建成 `M-XXX` "非功能需求"。
✅ 非功能需求（性能/安全/可用性）不是 module，是约束。该信息丢到 `business_goal` 或 `warnings`。

### 陷阱 3：page 与 feature 混淆

❌ "保存草稿" 既建 page `/save-draft` 又建 feature。
✅ "保存草稿"是 feature，对应的 page 是 `/rules/edit/:id?`（草稿编辑页）。

### 陷阱 4：业务流当 user_flow

❌ "数据每天凌晨同步" 当 user_flow（这是系统行为不是用户操作）。
✅ user_flow 必须有 `actor`（人类角色）触发；系统流程写到 `key_features.description` 里。

### 陷阱 5：过度拆分页面

❌ 把 `/rules` 列表拆成 `/rules/list`、`/rules/filter`、`/rules/sort` 三个 page。
✅ 一个 page = 一个 URL。filter/sort 是页面内的交互，写到 `primary_actions`。

## 与下游 stage 的契约

| 字段 | 谁消费 | 怎么用 |
|---|---|---|
| `modules` | design-analysis | 推站点导航分组 |
| `key_features` | design-analysis | 推组件需求（每个 feature 决定一组组件） |
| `pages` | design-analysis | 直接生成路由表；推每页组件 |
| `user_flows` | design-analysis | 标关键路径；review-gate 用来校验代码是否覆盖关键路径 |
| `business_goal` | review-gate | 总评时引用，回答"代码满足业务目标了吗" |

## 推断标记规范

任何推断必须满足：

```text
"description": "[inferred] 自动每 30s 保存一次"
```

或在数组中：

```text
"pain_points": ["规则版本切换会误覆盖在用规则", "[inferred] 批量调整缺少撤销"]
```

C1 checkpoint 会把所有 `[inferred]` 项高亮给用户审，所以**漏标比误标更糟**。

## 参考资料（外部）

- Jeff Patton, *User Story Mapping*（Story Mapping 起源）
- Bill Wake 的 INVEST checklist（独立功能单元判断）
- Peter Morville & Louis Rosenfeld, *Information Architecture*（IA 五步法）
- Marty Cagan, *Inspired*（PRD 反向解读视角）
