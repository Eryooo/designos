# 用户故事地图（User Story Mapping）

> 通用资产 · `product.user-story-mapping` · status: pilot

## purpose

用故事地图把业务目标拆成 modules、features、pages、flows，帮助团队从用户活动主线理解产品，而不是只看功能列表。

## applies_to

- PRD 拆解、原型规划、MVP 范围划定。
- 需要识别关键路径与 walking skeleton 的场景。

## decision_framework

1. `business_goal` 定义目标。
2. `modules` 作为 backbone，对应用户主要活动。
3. `key_features + pages` 作为 walking skeleton，表示完成活动的最小动作与承载。
4. `user_flows` 作为横向切片，串联跨模块任务。
5. 每个 feature 用 INVEST 检查：Independent / Negotiable / Valuable / Estimable / Small / Testable。

## senior_heuristics

- 先找用户活动，再找系统模块。
- feature 必须有 user_value，否则只是系统功能点。
- acceptance 必须可验证，不能写成愿望。
- 关键路径应跨至少两个模块，且直接对应 business_goal。

## quality_rubric

| 分级 | 信号 |
|---|---|
| 优 | modules/features/pages/flows 互相可追踪，关键路径清楚 |
| 中 | 结构完整但 user_value 或 acceptance 偏弱 |
| 差 | 功能清单平铺，没有用户活动骨架 |

## common_failure_modes

- 以研发模块替代用户活动。
- feature 过大，无法估算或测试。
- 没有 critical path。
- acceptance 是主观描述，无法验证。

## source_assets

- `skills/prd2proto/reference/textbook/story-mapping.md`
- `skills/prd2proto/reference/m01-prd-understanding.md`

## do_not_claim

- 不替代 roadmap 排期。
- 不决定功能是否应该做。
- 不规定具体 JSON schema。
