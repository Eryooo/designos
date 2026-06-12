# Stage: generate_prompt_pack

产出 AI 绘图 prompt pack,对齐 logo_prompt_pack.schema.json。

## 输入

- `visual_spec`: logo 设计规范(来自上一阶段)
- `brand_brief`: 品牌策略基线

## 任务

基于 logo_spec 产出 AI 绘图提示词包,支持多平台(Midjourney/Stable Diffusion/即梦等)。

**关键要求**:
- 必须消费 visual_spec.avoidance_rule,进入负向 prompt
- 必须消费 visual_spec.mother_shape,作为核心符号定位
- 负向 prompt 优先级:avoidance_rule > 通用高频避免项

## 提示词结构(来自 image-prompt-system)

### 四层结构(平台无关骨架)

每条提示词按四层组织,顺序固定:

1. **核心符号定位**:主符号 + 视觉权重,高度符号化
2. **设计理念表达**:风格坐标词(扁平/几何/极简/成熟商务等)
3. **技术参数**:色值(HEX + 配比)、输出规格(分辨率/背景/矢量)
4. **质量与避免**:必须达成项 + 严格避免项

### 多平台适配

- **Midjourney**:核心描述 + `--style` / `--ar` / `--v` 参数
- **Stable Diffusion**:正向 prompt + **负向 prompt**(承载严格避免项)
- **即梦/可灵(中文平台)**:结构化中文描述 + 关键英文术语

### 负向控制(关键)

**优先级 1:来自 visual_spec.avoidance_rule**
- 直接翻译 avoidance_rule 到负向 prompt
- 示例:avoidance_rule = "不封闭顶部" → negative: "closed top, complete enclosure"

**优先级 2:通用高频避免项**:
- 过度 3D 渲染
- 复杂机械结构
- 动物特征(除非品牌策略明确要求)
- 二次元/萌系(若风格坐标为成熟商务)
- 魔法元素/奇幻装饰
- 多余装饰/花纹
- 文字水印/签名
- 变形拉伸/像素化

## 输出

严格对齐 logo_prompt_pack.schema.json:

```json
{
  "prompts": [
    {
      "platform": "Midjourney",
      "positive": "A minimalist geometric logo, primary symbol: interlocking circle and square representing connection and structure, clean lines, professional and warm tone, brand colors #0066CC blue and white, 32px recognizable, flat vector style, high contrast for black-white usability --style raw --ar 1:1 --v 6",
      "negative": "--no 3D rendering, gradients, shadows, decorative elements, text, watermarks, animal features, complex details, distortion"
    },
    {
      "platform": "Stable Diffusion",
      "positive": "minimalist geometric logo design, interlocking circle and square symbol, clean vector style, professional corporate identity, color palette #0066CC blue and white, flat 2D, scalable to 16px favicon, black and white compatible, high contrast, simple shapes",
      "negative": "3D render, gradient, shadow, texture, ornate decoration, hand-drawn, sketch, watercolor, anime style, cartoon, realistic photo, text overlay, watermark, signature, complex machinery, animal features, magical elements, distortion, blur, low resolution"
    },
    {
      "platform": "即梦",
      "positive": "极简几何 logo 设计,主符号为圆形与方形交错代表连接与结构,专业商务风格带温暖感,品牌色 #0066CC 蓝色与白色,扁平矢量 flat vector style,16px 最小尺寸可识别,黑白模式可用,高对比度,简洁线条",
      "negative": "严格避免:3D 渲染、渐变阴影、复杂装饰、手绘素描、二次元动漫风格、真实照片、文字水印、动物元素、魔法奇幻、机械结构、变形模糊、低分辨率"
    }
  ],
  "status": "available"
}
```

若 prompt 生成失败,输出:
```json
{
  "prompts": [],
  "status": "unavailable"
}
```

## 质量自检

- [ ] 四层结构齐全(符号/理念/技术/避免)
- [ ] **核心符号基于 mother_shape**(不是重新发明符号) ✓
- [ ] **avoidance_rule 全部进入负向 prompt** ✓
- [ ] 覆盖 ≥2 平台且语义等价
- [ ] 色值用 HEX(从 visual_spec.color_refs 取)
- [ ] 必须达成项含:min_size_px 可识别、黑白可用、风格一致
- [ ] 负向 prompt 齐全(avoidance_rule + 至少 5 项通用避免)
- [ ] 无"最终商用/可直接使用"等越界声明

## 降级行为

若无法生成有效 prompt(如 visual_spec 信息不足):
- 返回 `{ "prompts": [], "status": "unavailable" }`
- 下游 visual-identity 会提示需人工补 prompt
