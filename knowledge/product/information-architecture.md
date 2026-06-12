# 信息架构（Information Architecture）

> 通用资产 · `product.information-architecture` · status: pilot

## purpose

把页面、导航、路由、关键路径组织成用户可理解、下游可消费的信息架构。IA 的目标是降低定位成本,不是复刻后端模块。

## applies_to

- 原型、后台、工具型产品、内容型产品的信息组织。
- 从需求拆解进入页面规划和路由设计的场景。

## decision_framework

1. 产出 Sitemap：顶层节点是用户可识别的模块入口。
2. 产出 Navigation：选择 1–2 种主要导航模式并说明覆盖页面。
3. 产出 Route Table：path / 名称 / 类型 / 模块 / 登录要求 / 备注。
4. 产出 Critical Path：只画关键用户流的页面跳转链。
5. 页面类型用稳定枚举：list / form / detail / dashboard / wizard / settings / auth / error。

## senior_heuristics

- 一 URL 一 page，筛选/排序/Tab 不一定是新 page。
- 导航反映用户心智，不反映数据库表。
- 面包屑只在层级真的有意义时使用。
- 关键路径优先保证触达深度浅。

## quality_rubric

| 分级 | 信号 |
|---|---|
| 优 | sitemap/navigation/route/critical path 四视图一致，可直接供实现消费 |
| 中 | 页面结构合理，但关键路径或导航说明不足 |
| 差 | 只列页面清单，无导航与路径关系 |

## common_failure_modes

- 把菜单树当旅程。
- 路由命名含动作或实现细节。
- 页面粒度过细，造成导航噪音。
- 关键路径没有在 IA 中高亮。

## source_assets

- `skills/prd2proto/reference/m02-design-analysis.md`
- `skills/prd2proto/reference/textbook/atomic-design.md`

## do_not_claim

- 不规定前端路由库。
- 不生成具体页面设计稿。
- 不替代可用性验证。
