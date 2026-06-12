# 设计策略（Design Strategy）

> 通用资产 · `design.design-strategy` · status: pilot

## purpose

把分析结论转成可被产品、视觉、原型消费的设计策略:目标人群、商业目标、设计原则、气质关键词与差异化定位。

## applies_to

- 从研究/竞品分析进入设计方向定义。
- 需要把 design_strategy 注入下游原型或设计规范的场景。

## decision_framework

策略至少回答:
1. target_audience:面向谁。
2. business_goal:为什么做。
3. design_principles:做设计时优先遵守哪些原则。
4. tone_keywords:视觉/语气气质关键词。
5. competitive_positioning:相对竞品的差异化(可选)。
6. evidence_refs:策略依据。

## senior_heuristics

- 设计原则必须能指导取舍,不能是"简洁、美观、易用"空话。
- tone_keywords 应与目标用户和业务目标一致。
- 商业目标与用户目标冲突时要显式标出,不强行统一。
- 每条策略尽量有证据,缺证据就降置信度。

## quality_rubric

| 分级 | 信号 |
|---|---|
| 优 | 策略可执行、可取舍、有证据,能指导模板/IA/组件选择 |
| 中 | 方向清楚但原则偏泛或证据弱 |
| 差 | 口号化,无法用于设计决策 |

## common_failure_modes

- 原则不可操作,像品牌 slogan。
- tone 与目标用户不匹配。
- 竞品定位无证据支撑。
- 下游拿不到可用的 business_goal / target_audience。

## source_assets

- `skills/ai-analytics/templates/design-strategy.schema.json`
- `skills/ai-analytics/reference/m05-strategy-synthesis.md`
- `skills/prd2proto/reference/m03a-spec-generation.md`

## do_not_claim

- 不替代品牌战略。
- 不保证策略正确,只定义质量标准。
- 不规定最终视觉稿。
