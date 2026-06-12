# 设计模板选择（Design Template Selection）

> 通用资产 · `design.design-template-selection` · status: pilot

## purpose

定义如何从可复用视觉模板族中选择合适模板,并在不破坏核心 vibe 的前提下做有限微调。

## applies_to

- 从 PRD/设计策略生成设计规范或视觉方向。
- 需要在多种视觉风格模板间做可解释选择的场景。

## decision_framework

模板匹配特征:
- product_type
- target_user
- vibe_keywords
- info_density_need
- color_preference

选择流程:
1. 从输入提取五类定位特征。
2. 与模板 suitable_for 字段评分。
3. 取最高分;平局看 product_type,再按稳定规则仲裁。
4. 只允许有限微调:品牌主色、状态色、组件库、字体本地化。
5. 禁止改整体 vibe / spacing / radius / elevation / component structure。

## senior_heuristics

- 模板核心 vibe 是系统,不是皮肤;随意改 spacing/radius 会破坏整体。
- 用户显式偏好高于内容推断,内容推断高于行业惯例。
- 微调必须写 field/from/to/reason,推断理由标注。
- 找不到合适模板时输出 fallback 与 warnings,不要假装命中。

## quality_rubric

| 分级 | 信号 |
|---|---|
| 优 | 选择理由可解释,微调有限且不破坏模板核心 |
| 中 | 模板选择合理但理由或调整记录不完整 |
| 差 | 随意选模板,或把模板改到失去一致性 |

## common_failure_modes

- 只按行业选模板,忽略信息密度与用户类型。
- 私自调整 spacing/radius/elevation。
- 推断调整不标 `[inferred]`。
- 平局仲裁不稳定,结果不可复现。

## source_assets

- `skills/prd2proto/reference/m03a-spec-generation.md`
- `skills/prd2proto/reference/design-templates/README.md`

## do_not_claim

- 不复制模板 token 全文。
- 不替代用户提供的 design-spec。
- 不保证模板就是最终品牌视觉。
