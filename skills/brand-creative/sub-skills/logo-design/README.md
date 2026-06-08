# logo-design

品牌 Logo 设计规范子技能。

## 快速开始

```python
from designos import SkillLoader

skill = SkillLoader.load("brand-creative:logo-design")
result = skill.run({
    "brand_brief": {
        "north_star": "让创业者感到被理解与支持",
        "positioning": "专业可信赖的创业服务品牌",
        "personality_keywords": ["专业", "温暖", "可靠", "创新"],
        "target_user": "初创企业创始人"
    }
})

print(result["visual_spec"])
print(result["image_prompt_pack"])
```

## 产出说明

### visual_spec (logo_spec)
包含 logo 设计规范:
- 形态方向与设计理由
- 色彩参考(HEX值)
- 黑白可用性验证
- 最小可识别尺寸
- 辅助图形方向
- 商标风险信号
- 应用场景

### image_prompt_pack
包含 AI 绘图提示词:
- 多平台适配(Midjourney/Stable Diffusion/即梦等)
- 正向提示词(四层结构)
- 负向提示词(严格避免项)

## 质量标准

- ✓ 黑白可用(灰度/纯黑/反白三模式)
- ✓ 32px 识别度(实际16px,留安全余量)
- ✓ 轮廓唯一可辨(剪影测试)
- ✓ 组合形式齐全(横/竖/图标)
- ✓ 商标风险已标注
- ✓ 策略回溯(形态对应人格关键词)

## 能力边界

**不声称:**
- 不声称 Logo 已商标查重/版权清洁/可直接注册
- 不声称已生成最终商用 logo 视觉资产
- 不声称辅助图形系统已完整设计

**产出定位:**
设计规范与方向,需专业 logo 设计师矢量精修与品牌方定稿。

## 依赖

**上游必需:**
- brand-strategy (提供 brand_brief)

**下游消费:**
- visual-identity (消费 logo_spec)

**知识资产:**
- knowledge/design/visual/logo-design-methodology.md
- knowledge/design/visual/logo-cognitive-translation.md
- knowledge/design/visual/image-prompt-system.md
- knowledge/design/quality/brand-identity-quality-rubric.md
- knowledge/design/quality/brand-creative-failure-modes.md

## 测试

```bash
# 运行 runtime 测试
pytest skills/brand-creative/sub-skills/logo-design/tests/test_logo_design_runtime.py -v

# 运行质量评估(promptfoo)
cd skills/brand-creative/sub-skills/logo-design/eval
promptfoo eval
```

## 参考案例

- `reference/case-geometric-logo.md` - 几何图形标参考
- `reference/case-wordmark.md` - 字标参考

## 版本

- 0.1.0-pilot: 初始 pilot 版本,runtime ready
