# 数据完整度 Rubric（Data Completeness Rubric）

> 通用资产 · `research.data-completeness-rubric` · status: pilot

## purpose

判断分析输入是否足以支撑策略、画像与竞品结论,避免数据不足时输出过度自信的设计判断。

## applies_to

- 竞品/市场/用户分析前后的质量门控。
- 决定是否可进入策略合成或需要补资料。

## decision_framework

评估维度:
- 对象覆盖:目标产品/竞品/用户群是否齐全。
- 维度覆盖:功能、体验、商业目标、用户痛点是否有资料。
- 证据可追溯:每条 fact 是否有 source。
- 缺口可见:缺失维度是否明确列出。

coverage 建议解释:
- ≥0.85:可支撑较稳定结论。
- 0.70–0.85:可输出但需标限制。
- <0.70:应阻断策略合成或要求补资料。

## senior_heuristics

- coverage 不得虚高;缺数据比弱结论更危险。
- 明确 gaps 比编造完整更专业。
- 对关键竞品/关键用户群缺资料时,即使总体资料多也不能高分。
- 每个策略/画像尽量挂 evidence_refs。

## quality_rubric

| 分级 | 信号 |
|---|---|
| 优 | coverage 与 gaps 有证据依据,能决定继续/补资料 |
| 中 | 大体指出缺口,但评分理由不够细 |
| 差 | 资料缺失仍给高 coverage,或不列 gaps |

## common_failure_modes

- 用公开常识填补事实缺口。
- 竞品资料少却输出完整矩阵。
- coverage 只看资料数量,不看关键维度。
- gaps 写得模糊,无法指导补资料。

## source_assets

- `skills/ai-analytics/reference/m02-data-collection.md`
- `skills/ai-analytics/reference/m05-strategy-synthesis.md`
- `skills/ai-analytics/SKILL.md`

## do_not_claim

- 不保证数据来源真实可靠。
- 不自动补齐缺失资料。
- 不替代研究采样设计。
