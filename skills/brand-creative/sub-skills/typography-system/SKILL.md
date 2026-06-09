---
name: typography-system
version: 0.1.0-pilot
type: pipeline
group: brand-creative
phase: 2-visual-identity
purpose: 产出字体系统(主/辅字体/字重层级/字号比例/行高/中西文配对/授权风险信号)
scope: 企业/产品/服务品牌字体系统,覆盖跨端可用性(Web/iOS/Android/印刷)
inputs:
  required:
    - brand_brief
  optional: []
outputs:
  - id: typography_spec
    type: visual_spec
    format: json
    schema_ref: ../../contracts/schemas/typography_spec.schema.json
knowledge_dependencies:
  - ../../../../knowledge/design/visual/typography-system-methodology.md
  - ../../../../knowledge/design/quality/brand-identity-quality-rubric.md
  - ../../../../knowledge/design/quality/brand-creative-failure-modes.md
quality_gate:
  checkpoint_id: C4-typography-system
  must_pass:
    - 中西文配对验证(字重/字号协调)
    - 跨端可用性检查(Web font / iOS / Android / 印刷)
    - 授权风险信号(商用授权/开源协议/fallback 字体)
contract_ref: ../../contracts/sub-skill-contracts.yaml#typography-system
pilot_status: runtime_ready
pilot_limitations:
  - 不声称字体已完成商用授权采购
  - 不声称已覆盖所有语言场景
  - license_status 标 needs_verification 时不声称授权已确认
---

# typography-system

## 定位

字体系统子技能,产出可落地的品牌字体系统:字重层级清晰、字号比例和谐、中西文配对协调、跨端可用、授权风险可控。

## 核心能力

- 基于品牌人格关键词推导字体气质方向
- 主字体/辅助字体配对与中西文协调
- 字重层级定义(3-4 层级清晰可辨)
- 字号比例采用模块化比例(和谐梯度)
- 行高定义(中西文分别适配)
- 授权类型标注与 fallback 字体栈
- 跨端可用性验证(Web/iOS/Android/印刷)

## 输入要求

**必需:**
- `brand_brief`: 品牌策略基线(品牌人格关键词提供字体气质方向)

## 输出产物

`typography_spec` (JSON):
- `primary_font`: 主字体(family, license)
- `secondary_font`: 辅助字体(可选)
- `weight_hierarchy`: 字重层级(3-4个)
- `size_scale`: 字号比例(模块化梯度)
- `line_height`: 行高(中西文分别定义)
- `cjk_latin_pairing`: 中西文配对说明
- `license_status`: 授权状态("verified" | "needs_verification")
- `cross_platform`: 跨端可用性(Web/iOS/Android/印刷)

## 质量标准

- 中西文配对在字重/字面/重心上协调
- 字重层级 3-4 个且相邻可辨
- 字号采用模块化比例,梯度和谐
- 中西文行高分别定义且合理
- 每个字体标了授权类型,定义了 fallback 栈
- 各端(Web/iOS/Android/印刷)可用或有合理 fallback
- license_status 诚实(verified / needs_verification)

## 能力边界

**不声称:**
- 不声称字体已完成商用授权采购(产出授权类型识别与风险预警,采购需用户/法务确认)
- 不声称已覆盖所有语言场景(如阿拉伯文/泰文等复杂书写系统需专项)
- license_status 标 needs_verification 时,不声称授权已确认
- 不替代专业字体排印师的精细调校

## 使用场景

- brand-strategy 完成后,需要字体系统
- 与 logo-design / color-system 并行开发
- 品牌焕新场景,更新字体系统

## 依赖关系

**上游(必需):**
- brand-strategy

**并行同级:**
- logo-design
- color-system

**下游消费者:**
- visual-identity
