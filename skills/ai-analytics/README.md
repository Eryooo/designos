# ai-analytics

分析型上游 skill（pilot baseline）。把竞品 / 市场 / 用户分析合成为结构化、可被下游 skill 消费的上游产物。

## 当前 pilot 范围

只稳定产出 prd2proto 最需要的两个上游产物：

- `design_strategy`：设计策略（JSON 契约）
- `user_persona`：用户画像（JSON 契约）

`analysis_report` / `comparison_matrix` 也产出，但当前仅供人读。

## 快速使用

```
inputs/scope_md            # 必需：分析 brief
inputs/competitor-data/    # 可选：用户提供的竞品资料
```

产物落在 `ai-analytics-out/<run_id>/`。

## 与 prd2proto 的对接

prd2proto 通过 `upstream_refs` 按 `output_type` 引用本 skill 的 `design_strategy`
与 `user_persona`，注入其 stage1 的 `{{design_strategy}}` / `{{existing_personas}}`。
详见 `SKILL.md` 的 Output Contract 节。

## 文档

- 定位 / 契约 / 边界：`SKILL.md`
- 输出 schema：`templates/design-strategy.schema.json`、`templates/user-persona.schema.json`
- pilot 边界与基线：`docs/releases/ai-analytics-baseline/`
