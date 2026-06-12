# Design Token 规则（Design Token Rules）

> 通用资产 · `frontend.design-token-rules` · status: pilot

## purpose

定义 design token 的分层、命名、引用与输出规则,避免把视觉值硬编码进组件或拍平成不可维护的一层变量。

## applies_to

- design-spec 到 token 的提取。
- 前端主题、CSS 变量、组件样式生成。

## decision_framework

采用三层架构:
1. reference/primitive:纯值层,如色板刻度、尺寸刻度,不得引用其他 token。
2. semantic/alias:语义层,把基础值映射到用途,如品牌主色、正文色。
3. component:组件层,把语义值绑定到具体组件部位。

引用规则:
- 用 `{path.to.token}` 形式引用。
- 引用路径必须存在。
- 组件层引用 semantic,不直接引用 reference。
- CSS 变量输出为终值,不含引用语法。

## senior_heuristics

- 组件代码只消费语义 token,否则主题切换会失控。
- 推断 token 必须标来源,不要把默认值伪装成设计指定。
- token 命名表达用途,不要表达当前颜色外观。
- 引用层级超过三层通常说明设计系统过度抽象。

## quality_rubric

| 分级 | 信号 |
|---|---|
| 优 | 三层清楚、引用可解析、命名语义化、CSS 变量与 JSON 对应 |
| 中 | 基本可用但少量组件直连 primitive |
| 差 | 一级拍扁、组件硬编码值、引用路径不存在 |

## common_failure_modes

- 把 token 拍扁成一级。
- reference 层引用其他 token。
- 组件层绕过 semantic。
- CSS 变量里保留 `{}` 未解析引用。

## source_assets

- `skills/prd2proto/reference/m04-token-extraction.md`
- `skills/prd2proto/reference/textbook/design-tokens-w3c.md`

## do_not_claim

- 不规定具体 token 值。
- 不规定构建工具或主题切换实现。
- 不替代品牌规范。
