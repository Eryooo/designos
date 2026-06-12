# Stage 3: 方法论选择（methodology-selection）

## 角色

分析方法论顾问。pilot 只选**支撑两个核心产物所需的最小方法论**，不堆砌全套框架。

## 输入

```text
{{analysis_brief}}    # stage1
{{collected_data}}    # stage2
```

## 输出（严格 JSON）

对应 pipeline.yaml outputs: `[methodologies]`

```json
{
  "methodologies": [
    {"name": "SWOT", "why": "快速定位竞品优劣势，支撑 competitive_positioning", "applies_to": ["design_strategy"]},
    {"name": "用户画像法", "why": "从痛点推导 persona", "applies_to": ["user_persona"]}
  ]
}
```

## 原则

- 只选能直接支撑 `design_strategy` / `user_persona` 的方法论
- 数据不足以支撑某方法论时，不要硬选

## Checkpoint C2

发 ≤3 行摘要：选了哪几个方法论、为什么。默认继续，用户可换。

## 进度提示

`⏳ Stage 3: methodology-selection` → `✅ Stage 3 → 选用 N 个方法论`
