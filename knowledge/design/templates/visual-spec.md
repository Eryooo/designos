# 模板:Visual Spec（M04 产出物）

> 通用模板 · `design.templates.visual-spec` · status: pilot
> M04 视觉转化的填空骨架。覆盖品牌基因继承、识别度量化、小尺寸分级、状态延展、风格谱系、严格禁忌——这些是旧库缺失的强约束。

```yaml
visual_spec:
  meta:
    project: ""
    version: "0.1.0-draft"
    upstream:
      brand_brief_ref: ""
      worldview_ref: ""
      persona_ref: ""

  brand_gene_inheritance:    # 已有品牌时必填(三栏)
    has_existing_brand: true
    inherited:               # 继承(不可动基因)
      primary_color: ""
      logo_relation: ""
      typography_feel: ""
      core_symbols: []
    new_for_ip:              # 新增(IP 专属)
      symbols: []
      motion_signature: ""
    forbidden_conflict:      # 禁冲突(绝不与既有品牌冲突)
      - ""

  shape_design:
    persona_to_shape:        # 人格→形态映射
      - keyword: ""
        geometry: ""         # 圆/三角/有机/方等
    primary_shape: ""        # 主形(与依据)
    primary_rationale: ""    # 为什么是它(取舍依据)
    auxiliary_shapes: []     # 辅形 1-2
    core_symbol:             # 核心识别符号
      name: ""
      visual_weight_pct: 60  # 核心符号视觉权重 ~60-70%
      description: ""
    secondary_symbols: []    # 辅助符号 1-2

  color_system:              # 60-30-10
    primary:
      hex: ""
      ratio_pct: 60
      usage: ""
    accent:
      hex: ""
      ratio_pct: 30
      usage: ""
    highlight:
      hex: ""
      ratio_pct: 10
      usage: ""
    contrast_check:          # 可访问性
      body_text_ratio: ""    # 与背景的对比度,目标 ≥ WCAG AA
      passes: true
    binding_to_persona_or_world: ""  # 色彩为何挂钩人格/世界观

  material_and_light:
    material_mapping:        # 材质映射世界观
      - material: ""         # 毛玻璃/金属/丝绸/光效等
        from_worldview: ""
    light_source:
      direction: ""          # 固定方向,如右上 45°
      layers:                # 光影层次
        highlight_pct: 10
        light_pct: 30
        mid_pct: 40
        shadow_pct: 15
        bounce_pct: 5
    special_effects: []      # 点/线/面光源等

  recognizability:           # 识别度(必)
    canonical_test:
      legible_at_32px: true  # 32px 下必须可辨
      remote_silhouette_recognizable: true
    size_tiers:              # 四级简化(必)
      large_ge_128px:
        spec: ""             # 完整形态与细节
      mid_48_to_128:
        spec: ""             # 标准形态,弱化次要细节
      small_24_to_48:
        spec: ""             # 简化为核心符号 + 主色
      tiny_lt_24:
        spec: ""             # 退化为单符号/单色

  state_extension:           # 状态延展(≥4)
    states:
      - id: ""               # idle/active/executing/confirm/done/fail 等
        visual: ""
        duration_ms: 0
        scenario: ""
        bound_emotion: ""    # 与 voice_and_behavior.emotion_expressions 对齐

  style_spectrum:            # 风格谱系坐标(必)
    flat_vs_skeuomorphic: ""    # 扁平 / 拟物
    geometric_vs_organic: ""    # 几何 / 有机
    minimal_vs_ornate: ""       # 极简 / 繁复
    business_vs_cute: ""        # 成熟商务 / 萌系
    "2d_vs_3d": ""              # 2D / 3D
    locked_position_summary: ""  # 一句话锁定坐标

  strict_avoidance:          # 严格禁忌项(≥5,可判定)
    - ""
    - ""
    - ""
    - ""
    - ""

  prompt_handoff:            # 给 image-prompt-system 的输入
    locked_values:           # 锁定项
      primary_hex: ""
      core_symbol_name: ""
      style_position: ""
    canonical_image_brief: ""  # 基准图描述

  inferences: []
  gaps: []
```

## 字段使用约束

- `has_existing_brand: true` 时三栏(inherited/new_for_ip/forbidden_conflict)非空。
- `recognizability.size_tiers` 四级齐全,且 32px 测试为 true。
- `state_extension.states` 数量 ≥ 4。
- `strict_avoidance` 数量 ≥ 5。
- `style_spectrum.locked_position_summary` 不能为空。
- `color_system.contrast_check.passes` 必须为 true。

## 与下游契约

- `prompt_handoff` 由 `design.visual.image-prompt-system` 直接消费。
- `state_extension` 与 `design.persona.voice-and-behavior-boundary.emotion_expressions` 一一对应。
- `strict_avoidance` 进入 M06 物料禁止使用示例 + 提示词负向 prompt。
