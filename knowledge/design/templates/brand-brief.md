# 模板:Brand Brief（M01 产出物）

> 通用模板 · `design.templates.brand-brief` · status: pilot
> M01 策略对齐法的填空骨架。每个字段对应 `design.strategy.brand-strategy-alignment`
> 的必过项;未填或推断必须显式标 `[inferred]` 或 `[gap]`。

```yaml
brand_brief:
  meta:
    project: ""              # 项目代号(非品牌名,通用层不写真实品牌)
    version: "0.1.0-draft"
    generated_at: ""

  north_star:                # 北极星(必)
    statement: ""            # 一句话,必须包含五要素
    five_elements:
      user_object: ""        # 用户对象
      method: ""             # 方式
      capability: ""         # 能力
      value: ""              # 价值(必须为情感/体验,不是功能)
      result: ""             # 结果
    is_emotional_value: true # 必为 true,否则 M01 必过项不过
    rationale: ""            # 选这条北极星的依据

  target_persona:            # 用户画像(必,基于真实研究优先)
    age_range: ""
    occupation: ""
    typical_day: ""          # 典型一天
    core_pain_points: []
    expected_feelings: []
    research_basis: ""       # 真实研究 / 推断;推断处必标 [inferred]

  core_values:               # 四层核心价值,各 3-5 项
    product_value: []
    user_value: []
    organization_value: []
    brand_value: []

  personality_keywords:      # 3-5 个,每个有依据
    - keyword: ""
      rationale: ""

  competitor_matrix:         # ≥3 个,客观不贬低
    - name: ""
      ip_form: ""
      personality: ""
      visual_style: ""
      gap_we_can_fill: ""    # 差异化机会:对手未占的空白

  differentiation_summary: ""  # 一句话:"为什么不是 X、不是 Y"

  inferences: []             # 所有推断显式列出 [inferred] 项
  gaps: []                   # 当前缺口(资料/研究不足),交 gap report
```

## 字段使用约束

- `north_star.is_emotional_value` 为 false 时不允许进入 M02。
- `personality_keywords` 数量 3–5,超出报错。
- `competitor_matrix` 项 ≥3 且每项含 `gap_we_can_fill`。
- 任一推断字段必须 `[inferred]` 标注 + 依据。

## 与下游契约

- `personality_keywords` 由 M03、M04 消费。
- `north_star` 与 `core_values` 由 M02、M05、M06 消费做一致性回扫。
- `competitor_matrix.differentiation` 进入 rubric D2 评分。
