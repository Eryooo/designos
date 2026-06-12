# Textbook: Story Mapping 与 INVEST

> Jeff Patton 的 Story Mapping 与 Bill Wake 的 INVEST 原则展开。stage 01 reference 中只列约束，本文给愿意深读的读者。

## Story Mapping 三层结构

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

## INVEST 原则

每个 `key_feature` 应满足：

| 字母 | 含义 | 在 stage 01 的体现 |
|---|---|---|
| **I**ndependent | 独立 | 一个 feature 描述清楚不需要其他 feature 上下文 |
| **N**egotiable | 可协商 | 推断的 acceptance 标 `[inferred]`，让 PM 在 C1 改 |
| **V**aluable | 有价值 | `user_value` 字段必须填，不能写"系统功能" |
| **E**stimable | 可估算 | 描述具体到能让前端估开发量 |
| **S**mall | 小 | 一个 feature 不超过 3 行描述；过长就拆 |
| **T**estable | 可测试 | `acceptance` 必须是可验证的 |

## 信息架构 5 步法（Rosenfeld）

stage 01 不直接产出 IA（那是 stage 02 的事），但 `pages` 已经是 IA 的原材料：

- **Page = 信息消费单元**（用户在一个 URL 内完成一个或一组目标）
- **page_type 枚举**：list / form / detail / dashboard / wizard / settings / auth / error
- **path 命名约定**：复数名词（`/rules` 不是 `/rule-list`）；动词不进 path

## 关键路径识别（Critical Path）

`user_flows[].is_critical_path = true` 的标准：

- 直接对应 `business_goal` 的核心动词
- 跨 ≥ 2 个 module
- 在 PRD 中用例数 > 1

## 参考资料（外部）

- Jeff Patton, *User Story Mapping*（Story Mapping 起源）
- Bill Wake 的 INVEST checklist（独立功能单元判断）
- Peter Morville & Louis Rosenfeld, *Information Architecture*（IA 五步法）
- Marty Cagan, *Inspired*（PRD 反向解读视角）
