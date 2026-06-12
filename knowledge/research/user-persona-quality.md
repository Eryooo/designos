# 用户画像质量（User Persona Quality）

> 通用资产 · `research.user-persona-quality` · status: pilot

## purpose

定义可被下游设计/产品消费的用户画像质量标准,避免画像变成泛泛的"用户类型描述"。

## applies_to

- 用户画像生成与评审。
- 从竞品/市场/用户资料合成 persona 的场景。

## decision_framework

高质量 persona 至少包含:
- id:稳定唯一标识。
- role:角色名。
- goals:核心目标。
- pain_points:痛点。
- scenarios:典型场景(可选但建议)。
- evidence_refs:支撑画像的证据来源。

判定链:角色是否明确 → 目标是否可行动 → 痛点是否可设计响应 → 场景是否具体 → 证据是否可追溯。

## senior_heuristics

- persona 不是人口统计标签,而是设计决策工具。
- 没有 goals/pain_points 的 persona 无法指导 user_flow。
- 痛点必须能转成产品/体验机会,不能只是情绪词。
- 证据弱的画像要标低可信度或待验证。

## quality_rubric

| 分级 | 信号 |
|---|---|
| 优 | 角色、目标、痛点、场景、证据完整,能直接支撑流程/策略 |
| 中 | 结构完整但痛点或证据偏弱 |
| 差 | 泛泛用户描述,无可行动目标和证据 |

## common_failure_modes

- 把 persona 写成"25-35 岁白领"。
- goals 与 pain_points 空泛。
- 没有 evidence_refs。
- 多个 persona 互相重叠,区分度低。

## source_assets

- `skills/ai-analytics/templates/user-persona.schema.json`
- `skills/ai-analytics/reference/m05-strategy-synthesis.md`

## do_not_claim

- 不替代真实用户研究。
- 不预设具体用户群。
- 不规定输出字段名必须与某 schema 一致。
