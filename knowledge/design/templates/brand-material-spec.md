# 模板:Brand Material Spec（M06 产出物）

> 通用模板 · `design.templates.brand-material-spec` · status: pilot

```yaml
brand_material_spec:
  meta:
    project: ""
    version: "0.1.0-draft"
    upstream:
      visual_spec_ref: ""
      persona_ref: ""

  brand_application:         # 品牌应用规范
    ip_logo_combo:
      composition: ""
      position_relation: ""
      min_size_px: 0
      safe_zone: ""
    ip_form_usage:
      - scenario: ""
        recommended_form: ""
        size_range: ""
        color_mode: ""       # CMYK / RGB / Pantone
        notes: ""
    forbidden_examples:      # ≥5,继承 visual_spec.strict_avoidance
      - ""
      - ""
      - ""
      - ""
      - ""

  derivative_products:       # 衍生品清单(含可落地性与成本)
    - category: ""           # 贴纸/玩偶/生活/文具/收藏
      name: ""
      design_points: ""
      material: ""
      craft: ""              # 工艺
      size: ""
      feasibility: ""        # 可落地性评估
      cost_band: ""          # 成本档位:低/中/高
      notes: ""

  promotion_materials:       # 宣传物料规范
    social_media:
      - type: ""             # 表情包/视频封面/图文模板
        size_px: ""
        layout_principles: ""
        color_mode: "RGB"
    activity:
      - type: ""             # 海报/易拉宝/展板/包装/名片
        size: ""
        layout_principles: ""
        color_mode: ""       # CMYK / Pantone(印刷必填)
    layout_rules:
      hierarchy: ""          # 主标题 > IP > 副标题 > 正文 > 按钮
      whitespace_principle: ""

  communication_guide:       # 传播指南
    color_emotion_mapping:   # 场景 × 色彩情绪
      - scenario: ""
        color_mood: ""
    tone_per_scenario:       # 与 voice_and_behavior 一致
      - scenario: ""
        tone: ""
    ip_role_per_scenario:    # 主视觉/向导/伙伴/符号
      - scenario: ""
        role: ""

  production_list:           # 首批物料生产清单
    - serial: 1
      name: ""
      quantity: 0
      lead_time_days: 0
      budget_band: ""        # 低/中/高
    production_advice:
      - "打样 → 材质确认"
      - "批次管理"
      - "版权登记提示"

  inferences: []
  gaps: []
```

## 字段使用约束

- `forbidden_examples` 数量 ≥ 5,继承 visual_spec.strict_avoidance。
- 印刷类物料(`activity`)必填 `color_mode` 为 `CMYK` 或 `Pantone`。
- `derivative_products` 每条必填 `feasibility` 与 `cost_band`。
- `tone_per_scenario` 必须与 voice-and-behavior 一致,不重发明。
- `production_list` 每条含 `lead_time_days` 与 `budget_band`。

## 与下游契约

- `production_list` 是品牌方/采购方的可执行交接物。
- `forbidden_examples` 进入 image-prompt-system 的负向 prompt 同步源。
