# 语气与视觉方向（Tone and Visual Direction）

> 通用资产 · `design.tone-and-visual-direction` · status: pilot

## purpose

把目标用户、业务目标、竞品定位转成可执行的 tone keywords 与视觉方向,用于模板选择、设计原则和内容气质统一。

## applies_to

- 设计策略、视觉策略、品牌方向草案。
- 需要从研究结论进入界面气质选择的场景。

## decision_framework

1. 从 target_audience 判断用户心智与专业度。
2. 从 business_goal 判断业务优先级(效率/信任/探索/转化)。
3. 从 competitive_positioning 判断差异化方向。
4. 提炼 3–6 个 tone keywords。
5. 把每个关键词映射到可观察的视觉决策:信息密度、留白、色彩克制程度、圆角/阴影/动效倾向。

## senior_heuristics

- tone keyword 必须能指导视觉取舍,不能只是形容词堆砌。
- "专业"可以是高密度克制,也可以是留白可信,必须结合目标用户解释。
- tone 与交互效率冲突时,优先核心任务效率。
- 视觉方向应明确不做什么,否则很快发散。

## quality_rubric

| 分级 | 信号 |
|---|---|
| 优 | tone 与用户/目标/竞品定位一致,并能落到视觉决策 |
| 中 | 关键词合理,但映射到视觉决策不足 |
| 差 | 关键词空泛,无法指导模板或组件选择 |

## common_failure_modes

- 关键词互相矛盾(极简又热闹)但无仲裁。
- 视觉方向只写审美词,不写信息密度/状态/组件倾向。
- 忽略目标用户专业度。
- 没有 do-not-do 边界。

## source_assets

- `skills/ai-analytics/templates/design-strategy.schema.json`
- `skills/ai-analytics/reference/m05-strategy-synthesis.md`
- `skills/prd2proto/reference/m03a-spec-generation.md`

## do_not_claim

- 不替代品牌手册。
- 不产出最终视觉稿。
- 不保证 tone keywords 可被所有用户群接受,需后续验证。
