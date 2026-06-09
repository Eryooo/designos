# Design Token 标准（Design Tokens）

> 通用资产 · `frontend.design-tokens` · status: draft
> design token 的通用分层与命名标准（与 W3C token 口径对齐）。本文与具体取值
> 无关,只规定层级、命名、引用方式;不内嵌任何模板的 token 取值,不规定打包工具。

## 三层结构

- **基础层（primitive / global）**:原始值,如调色板刻度、尺寸刻度。无语义。
- **语义层（semantic / alias）**:把基础值映射到用途,如 `color.text.primary`、`space.inline.md`。组件只引用语义层。
- **组件层（component）**:可选,把语义值绑定到具体组件,如 `button.bg.default`。

## 命名约定

- 点分命名,从类别到具体:`<category>.<usage>.<modifier>`。
- 语义命名表达"用途"而非"外观"(用 `text.primary` 而非 `gray.900`)。
- 同类 token 命名风格一致,可预测。

## 引用规则

- 组件引用语义层,不直接引用基础层字面量。
- 不在组件代码里写死视觉字面量(对应 `frontend.code-quality-rules` 的不硬编码规则)。

## 适用边界

本文给分层与命名口径;具体取值、主题切换实现、打包工具由消费方 skill 决定。

## 占位说明

本文为 K0 架构基线的 draft 占位,后续批次补全命名表与示例。
