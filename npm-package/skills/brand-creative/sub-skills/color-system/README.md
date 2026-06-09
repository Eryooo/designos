# color-system

品牌色彩系统子技能 — 产出专业可用的品牌色彩规范。

## 概述

基于 brand_brief 的人格关键词,推导色彩情绪并产出完整色彩系统:主色/辅色/中性色/语义色,含对比度验证/明暗双模式/印刷色差预警/使用规则。

## 核心输出

- 结构化色彩调色板 (color_palette)
- HEX / RGB / CMYK / Pantone 完整编码
- 对比度比值与 WCAG AA 验证
- 明暗背景双模式应用规则
- RGB→CMYK 色差风险标注
- 场景化使用规则与比例建议

## 质量标准

- 正文对比度 ≥ 4.5:1 (WCAG AA)
- RGB + CMYK/Pantone 双介质
- 明暗双模式都定义且达标
- 高饱和色标注印刷色差风险
- 每个颜色有明确角色与场景
- accessibility 诚实标注 (pass / needs_manual_check)

## 使用方式

```python
from designos.kernel import SkillLoader

loader = SkillLoader()
skill = loader.load_skill("brand-creative:color-system")

result = skill.run({
    "brand_brief": {
        "north_star": "让创业者感到被理解与支持",
        "personality_keywords": ["活力", "信赖", "创新"],
        ...
    }
})

color_palette = result["color_palette"]
```

## 能力边界

- ✅ 产出色彩规范 + 对比度验证 + 色差预警
- ✅ WCAG AA 标准验证
- ✅ 明暗双模式定义
- ❌ 不声称已完成印刷打样验证
- ❌ 不声称覆盖所有可访问性场景(色盲模拟需专项工具)
- ❌ accessibility 标 needs_manual_check 时需人工复核

## 依赖

- 上游: brand-strategy (提供 brand_brief)
- 下游: visual-identity, campaign-creative, brand-collateral, digital-assets

## 文件结构

- `SKILL.md`: 子技能元数据
- `pipeline.yaml`: 两阶段 pipeline (色彩情绪分析 → 系统产出)
- `constitution.md`: 核心原则与红线
- `prompts/`: Stage prompts
- `tests/`: Runtime 测试
