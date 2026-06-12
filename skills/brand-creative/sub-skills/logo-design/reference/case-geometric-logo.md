# 参考案例:几何图形标

## 输入

```json
{
  "brand_brief": {
    "north_star": "让创业者感到被理解与支持",
    "positioning": "专业可信赖的创业服务品牌",
    "differentiation": {
      "statement": "在理性专业基础上注入人文温暖",
      "basis": "competitor_matrix"
    },
    "core_values": ["专业", "可信赖", "支持"],
    "personality_keywords": ["专业", "温暖", "可靠", "创新", "亲和"],
    "target_user": "初创企业创始人"
  }
}
```

## 输出

### visual_spec (logo_spec)

```json
{
  "form": {
    "primary_shape": "几何组合标:圆角方形图形+字标横排",
    "rationale": "从品牌人格'专业/温暖/可靠'推导。选择几何形态传达专业可靠,方形象征结构与支撑(core value'支持'),圆角处理体现温暖亲和。组合标平衡识别度与可读性,适配创业服务品牌需要快速建立信任的场景。图形部分可独立作为 app icon,满足小尺寸应用。"
  },
  "color_refs": ["#0066CC", "#FFFFFF"],
  "black_white_usable": true,
  "min_size_px": 16,
  "auxiliary_graphics": [
    "从主图形圆角方形提炼的网格系统:圆角 4px,间距统一",
    "辅助图案:圆角矩形组合,可用于背景纹理、分割线、装饰元素",
    "与主 logo 同源,共享圆角半径与比例关系"
  ],
  "trademark_risk_signals": [
    "方形+圆角为常见几何形态,需在内部增加差异化符号细节",
    "建议在最终定稿前进行商标相似度专业检索",
    "本信号非商标查重结果,logo 注册需专业商标机构检索"
  ],
  "application_scenarios": [
    "网站 header 横版:最小 120px 宽,图形+字标",
    "favicon 纯图标版:16×16px,仅图形部分",
    "名片横版:黑白可用,图形+字标",
    "APP icon 纯图标版:iOS 1024×1024 / Android 512×512",
    "招牌大尺寸:展示圆角细节与字标清晰度",
    "反白版本:白色 logo + 深色背景,用于深色界面"
  ]
}
```

### image_prompt_pack (logo_prompt_pack)

```json
{
  "prompts": [
    {
      "platform": "Midjourney",
      "positive": "A minimalist geometric logo, rounded square symbol representing support and structure, professional and warm corporate identity, brand color #0066CC blue and white, clean lines, 16px scalable, flat vector style, high contrast for black-white compatibility --style raw --ar 1:1 --v 6",
      "negative": "--no 3D rendering, gradients, shadows, ornate decorations, text watermarks, animal features, complex machinery, cartoon style, distortion"
    },
    {
      "platform": "Stable Diffusion",
      "positive": "minimalist geometric logo design, rounded square symbol, professional corporate visual identity, flat vector 2D, color #0066CC blue and white, scalable to 16px favicon, black and white compatible, high contrast, simple clean shapes, modern business style",
      "negative": "3D render, gradient, shadow, texture, ornate decoration, hand-drawn, sketch, watercolor, anime, cartoon, realistic photo, text overlay, watermark, signature, complex details, animal features, magical elements, machinery, distortion, blur, low resolution, pixelated"
    },
    {
      "platform": "即梦",
      "positive": "极简几何 logo 设计,圆角方形主符号代表支撑与结构,专业商务风格融入温暖感,品牌色 #0066CC 蓝色与白色,扁平矢量 flat vector,16px 最小尺寸可识别,黑白模式完全可用,高对比度,简洁现代线条,企业品牌视觉",
      "negative": "严格避免:3D 渲染、渐变光影、复杂装饰花纹、手绘素描、二次元动漫、真实照片、文字水印签名、动物元素、魔法奇幻风格、机械零件、变形扭曲、模糊低分辨率、像素化"
    }
  ],
  "status": "available"
}
```

## 质量检查点

- ✓ 标志类型(组合标)有策略依据(平衡识别与可读)
- ✓ 形态语言(几何+圆角)回溯到人格关键词(专业+温暖)
- ✓ 黑白可用性已验证
- ✓ 最小尺寸 16px 可辨
- ✓ 辅助图形与主 logo 同源(共享圆角系统)
- ✓ 商标风险已标注且声明非查重
- ✓ prompt pack 含负向控制,覆盖 3 平台
- ✓ 无"可注册/版权清洁/最终商用"越界声明
