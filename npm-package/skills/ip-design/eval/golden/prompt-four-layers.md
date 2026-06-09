# Golden Case: 提示词四层结构

本 golden case 演示正确的 AI 绘图提示词包:四层结构 + 量化 + 负向 + 基准图。

## 输入

```yaml
visual_spec:
  core_symbol: {name: "效率权杖", visual_weight_pct: 60}
  color_system:
    primary: {hex: "#1A1A2E", ratio_pct: 60}
  style_spectrum:
    locked_position_summary: "扁平+几何+极简+成熟商务+2D"
  strict_avoidance:
    - "绝不过度 3D"
    - "绝不二次元/萌系"
    - "绝不动物化"
    - "绝不遮挡核心符号"
    - "绝不拉伸变形"
```

## 期望产出(golden)

```yaml
image_prompt_pack:
  canonical_image:
    prompt_four_layers:
      core_symbol: "效率权杖(主符号 60%),几何柱体顶端点状光源"
      design_philosophy: "扁平几何极简成熟商务 2D"
      technical_params: "深空灰 #1A1A2E (60%) + 活力橙 #FF6B35 (30%) + 科技蓝 #3A86FF (10%);毛玻璃 70% 透明度;右上 45° 光源;输出 4K PNG 透明背景"
      quality_and_avoidance: "32px 下权杖清晰可辨;严格避免:过度 3D/二次元萌系/动物化/遮挡核心符号/拉伸变形"
    locked_values:
      primary_hex: "#1A1A2E"
      core_symbol_name: "效率权杖"
      style_position: "扁平+几何+极简+成熟商务+2D"
  
  multi_platform:
    - platform: "Stable Diffusion"
      positive_prompt: "{{四层融合}}"
      negative_prompt: "3d render, anime, cute, kawaii, animal features, text watermark, distortion, symbol occlusion"
```

## 断言

- `canonical_image.prompt_four_layers` 四字段齐全
- `quality_and_avoidance` 含"严格避免"清单
- `multi_platform` 数组长度 ≥ 2
- `multi_platform` 中至少 1 个含 `negative_prompt` 字段(可控型平台)
