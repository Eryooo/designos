# 竞品分析（Competitor Analysis）

> 通用资产 · `research.competitor-analysis` · status: pilot

## purpose

把竞品资料转成可追溯的 analysis findings 与比较矩阵,为设计策略、用户画像或产品机会判断提供证据。

## applies_to

- 竞品分析、市场分析、设计策略输入。
- 需要对多个对象按维度比较的场景。

## decision_framework

1. 定义目标产品、竞品范围、用户群。
2. 采集资料时每条 fact 必须有 source。
3. 选择分析维度,覆盖最终产物需要的输入。
4. 每条 finding 包含 methodology / dimension / finding / evidence_refs。
5. 比较矩阵用竞品 × 维度,每格事实可追溯。
6. 无数据支撑的推断标 `[inferred]`,完全无数据不编造。

## senior_heuristics

- 先保证证据链,再谈洞察质量。
- comparison matrix 的每格都应能回到 source。
- 分析维度不要只覆盖功能,还要覆盖目标用户、体验路径、差异化。
- 把"观察"和"判断"分开写。

## quality_rubric

| 分级 | 信号 |
|---|---|
| 优 | findings 与矩阵均可追溯,维度服务最终策略 |
| 中 | 基本可追溯,但维度与策略连接较弱 |
| 差 | 竞品印象罗列,缺 evidence_refs |

## common_failure_modes

- 未采集数据却编造竞品事实。
- 矩阵单元格写评价词而非事实。
- 只看功能列表,不看用户场景与策略含义。
- evidence_refs 指不到真实来源。

## source_assets

- `skills/ai-analytics/reference/m02-data-collection.md`
- `skills/ai-analytics/reference/m04-competitor-analysis.md`
- `skills/ai-analytics/reference/m06-report-generation.md`

## do_not_claim

- 不自动爬取或验证外部资料。
- 不预设行业。
- 不保证分析结论超过输入资料质量。
