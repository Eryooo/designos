# 交互状态覆盖（Interaction State Coverage）

> 通用资产 · `product.interaction-state-coverage` · status: pilot

## purpose

确保交互组件和关键流程覆盖用户会遇到的状态,避免只设计 happy path。状态覆盖是产品体验完整性的底线。

## applies_to

- 组件设计、原型评审、代码生成评审。
- 表单、按钮、列表、异步任务、错误恢复等交互场景。

## decision_framework

常见交互状态：default / hover / active / focus / disabled / loading / error。

判定流程：
1. 识别所有可交互组件。
2. 按组件类型判断是否需要全 7 状态。
3. 对不需要的状态显式标记不适用并给理由。
4. 对流程类交互补充空状态、成功态、失败态、撤销/回退路径。

## senior_heuristics

- 缺 focus 是可达性风险，通常比缺 hover 严重。
- loading/error 不是装饰态，是异步体验的核心。
- disabled 必须解释原因，否则用户会反复试错。
- 状态覆盖要从用户任务出发，不是给组件表格打勾。

## quality_rubric

| 分级 | 信号 |
|---|---|
| 优 | 所有关键交互状态齐全，非适用状态有理由 |
| 中 | 基本状态齐全，但异步/错误/禁用解释不足 |
| 差 | 只设计默认态或 happy path |

## common_failure_modes

- Button 只有 default + hover。
- 表单没有 error 与 disabled 说明。
- 异步操作无 loading/success/error 状态机。
- 禁用态无 tooltip 或上下文解释。

## source_assets

- `skills/prd2proto/reference/m02-design-analysis.md`
- `skills/prd2proto/reference/textbook/atomic-design.md`
- `skills/uxeval/reference/m05-证据采集.md`

## do_not_claim

- 不规定具体 CSS 实现。
- 不要求所有非交互元素具备七状态。
- 不替代无障碍专项审查。
