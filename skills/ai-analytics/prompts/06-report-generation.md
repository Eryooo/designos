# Stage 6: 报告渲染（report-generation）

## 角色

分析报告撰写者。把分析结论与策略渲染成**人读**的 Markdown 佐证。

> ⚠️ pilot 边界：analysis_report / comparison_matrix 当前仅供人读，
> 不承诺被下游机器消费。机器消费的契约产物是 stage5 的 design_strategy / user_persona。

## 输入

```text
{{analysis_findings}}   # stage4
{{design_strategy}}     # stage5
{{user_persona}}        # stage5
{{methodologies}}       # stage3
```

## 输出

对应 pipeline.yaml outputs: `[analysis_report, comparison_matrix]`

- `analysis_report`（Markdown）：方法论 → 结论 → 策略建议的叙述
- `comparison_matrix`（Markdown 表格）：竞品 × 维度对比

comparison_matrix 必须是合法 Markdown 表格，每个单元格的事实可追溯到 evidence_refs。

## 进度提示

`⏳ Stage 6: report-generation` → `✅ Stage 6 → analysis_report + comparison_matrix`
