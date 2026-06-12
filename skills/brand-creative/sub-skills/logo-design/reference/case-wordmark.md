# 参考案例:字标

## 输入

```json
{
  "brand_brief": {
    "north_star": "让年轻创作者感到自由与可能",
    "positioning": "年轻创意工具品牌",
    "differentiation": {
      "statement": "在工具理性中注入创作激情",
      "basis": "inferred"
    },
    "core_values": ["创新", "自由", "表达"],
    "personality_keywords": ["年轻", "活力", "创意", "前卫", "自由"],
    "target_user": "18-28 岁内容创作者"
  }
}
```

## 输出

### visual_spec (logo_spec)

```json
{
  "form": {
    "primary_shape": "定制字标(wordmark)带动态倾斜,字母 'i' 替换为创意符号",
    "rationale": "从品牌人格'年轻/活力/创意'推导。品牌名短(假设 'Vibe')适合字标,定制字体增强识别度。字母轻微右倾 8° 传达动态与前卫,字母 'i' 点替换为闪电/星形等创意符号强化'创作激情'。纯字标在年轻受众中辨识度高,且适配社交媒体横幅。"
  },
  "color_refs": ["#FF3366", "#000000", "#FFFFFF"],
  "black_white_usable": true,
  "min_size_px": 24,
  "auxiliary_graphics": [
    "从字母倾斜角度提炼的动态线条系统:8° 倾斜栅格",
    "辅助符号:从 'i' 点创意符号衍生的小图标集",
    "与主字标同源,共享倾斜角度与字重"
  ],
  "trademark_risk_signals": [
    "定制字标相似度风险低于通用字体",
    "字母 'i' 创意替换需确认无相似注册案例",
    "品牌名'Vibe'等通用词汇注册难度较高,需专业检索",
    "本信号非商标查重结果,logo 注册需专业商标机构检索"
  ],
  "application_scenarios": [
    "社交媒体横幅:Twitter/Instagram header,横版字标",
    "网站 header:最小 100px 宽",
    "APP icon:字标首字母'V'简化版,32×32px 可辨",
    "T恤印刷:大尺寸字标,展示定制字体细节",
    "名片:横版,黑白/反白可用",
    "视频片头:动态字标,字母逐个出现"
  ]
}
```

### image_prompt_pack (logo_prompt_pack)

```json
{
  "prompts": [
    {
      "platform": "Midjourney",
      "positive": "A dynamic custom wordmark logo 'Vibe', letters with 8-degree right tilt, creative symbol replacing dot on letter 'i', bold sans-serif typeface, brand color #FF3366 pink and black, youthful and energetic style, 24px minimum readable, flat vector --style raw --ar 3:1 --v 6",
      "negative": "--no 3D effects, gradients, shadows, serif fonts, overly decorative, traditional style, low energy, symmetrical, static"
    },
    {
      "platform": "Stable Diffusion",
      "positive": "modern custom wordmark logo design, dynamic tilted letters 8 degrees, creative symbol icon, bold sans-serif typography, flat 2D vector, color #FF3366 pink and black, youthful energetic brand identity, scalable to 24px, high contrast black-white compatible",
      "negative": "3D render, gradient, shadow, texture, serif font, ornate decoration, traditional corporate, hand-drawn, sketch, realistic photo, watermark, complex patterns, symmetrical layout, static composition, low contrast, blur"
    },
    {
      "platform": "即梦",
      "positive": "年轻活力定制字标 logo,字母右倾 8° 动态感,'i' 字母点替换为创意符号,粗体无衬线字体 bold sans-serif,品牌色 #FF3366 粉红与黑色,扁平矢量 flat vector,24px 最小尺寸可读,黑白模式可用,高对比度现代设计",
      "negative": "严格避免:3D 渲染、渐变阴影、衬线字体、过度装饰、传统商务风格、低活力、对称静态布局、手绘素描、真实照片、文字水印、复杂图案、模糊低对比"
    }
  ],
  "status": "available"
}
```

## 质量检查点

- ✓ 标志类型(字标)有策略依据(品牌名短、年轻受众)
- ✓ 形态语言(倾斜+创意符号)回溯到人格关键词(年轻/活力/创意)
- ✓ 黑白可用性已验证
- ✓ 最小尺寸 24px(字标比图形标尺寸要求略大)
- ✓ 辅助图形与主字标同源(共享倾斜角度)
- ✓ 商标风险已标注(通用词汇注册难度)且声明非查重
- ✓ prompt pack 含负向控制,覆盖 3 平台
- ✓ 无越界声称

## 对比说明

此案例与 case-geometric-logo 的差异:
- **标志类型**:字标 vs 图形标,因品牌名长短与受众不同
- **风格坐标**:年轻活力(倾斜/前卫)vs 专业温暖(几何/圆润)
- **最小尺寸**:24px vs 16px(字标文字天然需要略大尺寸)
- **应用场景**:社交媒体/T恤 vs 网站/名片/APP icon
