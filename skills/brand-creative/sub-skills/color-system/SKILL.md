---
name: color-system
version: 0.1.0-pilot
type: pipeline
group: brand-creative
phase: 2-visual
purpose: 产出品牌色彩系统(主色/辅色/对比度/可访问性/介质差异)
scope: 品牌色彩决策(企业品牌/产品品牌/服务品牌)
inputs:
  required:
    - brand_brief
outputs:
  - id: color_palette
    type: visual_spec
    format: json
    schema_ref: ../../contracts/schemas/color_palette.schema.json
knowledge_dependencies:
  - ../../../../knowledge/design/visual/color-system-methodology.md
  - ../../../../knowledge/design/quality/brand-identity-quality-rubric.md
  - ../../../../knowledge/design/quality/brand-creative-failure-modes.md
quality_gate:
  checkpoint_id: C3-color-system
  must_pass:
    - 主色/辅色对比度 ≥ 4.5:1 (WCAG AA)
    - 明暗背景可用性验证
    - 数字/印刷色差风险标注(RGB → CMYK 转换)
contract_ref: ../../contracts/sub-skill-contracts.yaml#color-system
pilot_status: runtime_ready
pilot_limitations:
  - 不声称色彩已完成印刷打样验证
  - 不声称已覆盖所有可访问性场景(如色盲模式)
  - accessibility 标 needs_manual_check 时需人工验证
---

# color-system

## 定位

品牌色彩系统子技能,产出结构化色彩规范:主色/辅色/中性色/对比度/可访问性/介质差异。

## 核心能力

- 基于 brand_brief 人格关键词推导色彩情绪
- 产出完整色彩角色分配(primary/secondary/neutral/semantic)
- 计算对比度并验证 WCAG AA 标准(≥ 4.5:1)
- 定义明暗背景双模式色彩应用
- 标注 RGB→CMYK 色差风险(高饱和色印刷漂移预警)
- 提供场景化配色规则与使用比例

## 输入要求

**必需:**
- `brand_brief`: 品牌策略基线(由 brand-strategy 产出),含人格关键词提供色彩情绪方向

## 输出产物

`color_palette` (JSON):
- `primary`: { hex, rgb, cmyk, pantone, role }
- `secondary`: [{ hex, rgb, cmyk, pantone, role }, ...]
- `neutral`: [{ hex, role }, ...]
- `semantic`: { success, warning, error }
- `contrast_ratios`: { primary_on_white, primary_on_black, ... }
- `accessibility`: "pass" | "needs_manual_check"
- `print_color_risk`: 高饱和色印刷色差预警
- `dark_light_usage`: 明暗背景模式色彩应用规则
- `usage_ratio`: 主/辅/强调色使用比例建议

## 质量标准

- 主色与辅色对比度必须 ≥ 4.5:1 (WCAG AA)
- 明暗背景双模式都定义且对比度达标
- RGB + CMYK/Pantone 都提供,高饱和色标注色差风险
- 每个颜色有明确角色与使用场景
- 色彩比例明确,强调色克制使用
- accessibility 字段诚实标注(pass 或 needs_manual_check)

## 能力边界

**不声称:**
- 色彩已完成印刷打样验证(产出规范 + 色差预警,实物需打样)
- 已覆盖所有可访问性场景(如各类色盲模拟需专项工具验证)
- Pantone 色值已与供应商确认(需印厂打样确认)
- accessibility 标 needs_manual_check 时已通过可访问性审计

## 使用场景

- brand-strategy 完成后,需要色彩系统
- 与 logo-design / typography-system 并行开发(都消费 brand_brief)
- 品牌焕新场景,更新色彩体系

## 依赖关系

**上游:**
- brand-strategy (必须先完成)

**下游消费者:**
- visual-identity (消费 color_palette 汇总 VI 手册)
- campaign-creative
- brand-collateral
- digital-assets
