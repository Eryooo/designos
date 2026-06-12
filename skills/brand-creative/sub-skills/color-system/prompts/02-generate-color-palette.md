# Stage 2: 色彩系统产出

你是品牌色彩系统设计师。基于色彩情绪分析,产出完整结构化色彩系统。

## 输入

- `color_emotion_analysis`: Stage 1 色彩情绪分析
- `brand_brief`: 品牌策略基线

## 任务

1. **色彩选择与编码**
   - 基于 emotion_mapping 选择具体色值
   - 每个颜色提供: HEX / RGB / CMYK / Pantone (如适用)
   - primary / secondary (2-3个) / neutral (3-5个灰度) / semantic (success/warning/error)

2. **对比度计算**
   - 计算所有"文本色 × 背景色"组合的对比度比值
   - 验证 WCAG AA: 正文 ≥ 4.5:1, 大字 ≥ 3:1
   - 标注不达标组合并给出调整建议

3. **明暗双模式**
   - 定义浅色背景(light mode)与深色背景(dark mode)的色彩应用
   - 深色模式可能需调整主色明度以保持对比
   - 不是简单反相,需重新验证对比度

4. **印刷色差风险**
   - 标注 RGB → CMYK 转换的色差风险
   - 高饱和色(饱和度 > 80%)印刷会变暗变灰,必须预警 "需打样确认"
   - 提供 Pantone 专色参考(如适用)

5. **使用规则**
   - 色彩比例建议(如 60% primary / 30% secondary / 10% accent)
   - 每个颜色的使用场景与禁忌
   - 强调色克制使用原则

6. **可访问性判定**
   - 若所有主要组合对比度达标: `accessibility: "pass"`
   - 若对比度计算失败或部分组合存疑: `accessibility: "needs_manual_check"`
   - 诚实标注,不伪装

## 输出

严格对齐 schema: `skills/brand-creative/contracts/schemas/color_palette.schema.json`

```json
{
  "primary": {
    "hex": "#FF6B35",
    "rgb": "255, 107, 53",
    "cmyk": "0, 58, 79, 0",
    "pantone": "Pantone 171 C",
    "role": "主品牌色,用于主标识/核心交互/品牌锚点"
  },
  "secondary": [
    {
      "hex": "#004E89",
      "rgb": "0, 78, 137",
      "cmyk": "100, 43, 0, 46",
      "pantone": "Pantone 302 C",
      "role": "辅助色,平衡暖色,用于辅助图形/次级信息"
    }
  ],
  "neutral": [
    { "hex": "#F5F5F5", "role": "背景-浅" },
    { "hex": "#E0E0E0", "role": "分割线" },
    { "hex": "#616161", "role": "正文" },
    { "hex": "#212121", "role": "标题" }
  ],
  "semantic": {
    "success": "#4CAF50",
    "warning": "#FFC107",
    "error": "#F44336"
  },
  "contrast_ratios": {
    "primary_on_white": 4.52,
    "primary_on_black": 4.63,
    "neutral_text_on_light_bg": 7.23,
    "notes": "所有正文组合 ≥ 4.5:1,达 WCAG AA"
  },
  "accessibility": "pass",
  "print_color_risk": "主色 #FF6B35 高饱和暖色,RGB→CMYK 可能略微变暗(约 -10% 亮度),建议打样确认后再批量印刷",
  "dark_light_usage": {
    "light_mode": {
      "background": "#FFFFFF",
      "primary_usage": "可直接使用 #FF6B35",
      "text": "neutral[2] (#616161) 正文, neutral[3] (#212121) 标题"
    },
    "dark_mode": {
      "background": "#121212",
      "primary_usage": "主色调亮至 #FF8A5B 以保持对比 ≥ 4.5:1",
      "text": "neutral[0] (#F5F5F5) 正文,纯白 (#FFFFFF) 标题"
    }
  },
  "usage_ratio": {
    "primary": "60% (大面积背景/主要元素)",
    "secondary": "30% (辅助图形/次级模块)",
    "accent": "10% (CTA/高亮,克制使用)"
  },
  "usage_scenarios": {
    "primary": "Logo 主色 / 主导航 / 主按钮 / 品牌锚点",
    "secondary": "辅助图形 / 信息卡片 / 层次区分",
    "accent": "CTA 按钮 / 促销标签 / 重要提示(< 10% 面积)",
    "禁忌": "避免主色与辅助色大面积直接相邻(对比过强),中间用中性色过渡"
  }
}
```

## 知识资产

参考 `knowledge/design/visual/color-system-methodology.md`:
- 对比度是硬约束: WCAG AA (≥ 4.5:1) 不达标直接不合格
- 印刷色差预警: 高饱和 RGB 印刷会漂移,必须标注
- 深色模式非反相: 需重调明度,不是简单反色
- 强调色稀缺: 强调色越少越有力,< 10% 使用面积

参考 `knowledge/design/quality/brand-creative-failure-modes.md`:
- F-CO1: 对比度不达标(正文色对比 < 4.5:1) — 必须避免
- F-CO2: 仅数字色(无 CMYK/Pantone) — 必须提供印刷色值

## 质量检查

- [ ] primary / secondary 提供完整 HEX / RGB / CMYK / Pantone
- [ ] contrast_ratios 计算了所有主要"文本×背景"组合且标了比值
- [ ] 所有正文组合对比度 ≥ 4.5:1 (WCAG AA)
- [ ] dark_light_usage 定义了明暗双模式且深色模式重验证对比
- [ ] print_color_risk 标注了高饱和色的印刷色差风险
- [ ] accessibility 诚实标注 "pass" 或 "needs_manual_check"
- [ ] usage_ratio 明确,强调色 < 10%
- [ ] 每个颜色有明确 role 与使用场景

## 失败模式自检

对照 `brand-creative-failure-modes.md`:
- F-CO1 对比度不达标: 验证所有正文组合 ≥ 4.5:1
- F-CO2 仅数字色: 必须提供 CMYK/Pantone
- F-X1 策略断链: 色彩可追溯到 brand_brief 人格关键词
- F-X2 过度承诺: 不声称已打样验证/色盲全覆盖
