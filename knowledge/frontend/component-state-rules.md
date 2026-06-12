# 组件状态规则（Component State Rules）

> 通用资产 · `frontend.component-state-rules` · status: pilot

## purpose

定义交互组件必须覆盖的状态与审查口径,保证代码和设计都不只覆盖默认态。

## applies_to

- Button/Input/Select/Checkbox/Radio/Switch/Link/Tab 等交互组件。
- 原型与前端代码的状态覆盖审查。

## decision_framework

七种核心状态:default / hover / active / focus / disabled / loading / error。

必全状态组件:
- Button / Input / Select / Checkbox / Radio / Switch / Link / Tab。
- 可点击 Card。
- DatePicker / Slider 等复合组件需覆盖主状态与子状态。

非全状态组件:
- Heading / Divider / Badge / Tag / Avatar 通常不需要交互态。
- Modal / Toast 关注 entering/leaving,不算七种交互态。

## senior_heuristics

- focus 是键盘可达性的底线,缺失通常是 major。
- disabled 没解释原因会造成反复试错。
- loading 与 error 需要配套文案,不是只加 spinner 或红框。
- pm 模式可降级,高保真/生产模式必须更严。

## quality_rubric

| 分级 | 信号 |
|---|---|
| 优 | 关键交互组件状态齐全,视觉/文案/行为一致 |
| 中 | 基本状态齐,但 loading/error 处理粗糙 |
| 差 | 只有 default/hover,无 focus/disabled/error |

## common_failure_modes

- 缺 focus-visible。
- loading 时仍可重复提交。
- error 只有颜色无说明。
- disabled 无 tooltip/原因。

## source_assets

- `skills/prd2proto/reference/m02-design-analysis.md`
- `skills/prd2proto/reference/m05-code-generation.md`
- `skills/prd2proto/reference/m06-review-gate.md`

## do_not_claim

- 不规定 CSS 选择器或框架实现。
- 不覆盖业务状态机的全部领域状态。
- 不替代无障碍专项测试。
