---
name: logo-design
version: 0.1.0-pilot
type: pipeline
group: brand-creative
phase: 2-visual-identity
purpose: 产出 Logo 设计规范(形态/色彩/应用场景/辅助图形)与 AI 绘图 prompt pack
scope: 企业/产品/服务品牌的 logo 设计方向与规范
inputs:
  required:
    - brand_brief
  optional: []
outputs:
  - id: visual_spec
    type: visual_spec
    format: json
    schema_ref: ../../contracts/schemas/logo_spec.schema.json
  - id: image_prompt_pack
    type: image_prompt_pack
    format: json
    schema_ref: ../../contracts/schemas/logo_prompt_pack.schema.json
knowledge_dependencies:
  - ../../../../knowledge/design/visual/logo-design-methodology.md
  - ../../../../knowledge/design/visual/image-prompt-system.md
  - ../../../../knowledge/design/quality/brand-identity-quality-rubric.md
  - ../../../../knowledge/design/quality/brand-creative-failure-modes.md
quality_gate:
  checkpoint_id: C2-logo-design
  must_pass:
    - 黑白可用性验证(logo 转灰度后仍可识别)
    - 小尺寸验证(16x16px 轮廓清晰)
    - 商标风险信号检查(通用符号/行业禁忌/相似度)
contract_ref: ../../contracts/sub-skill-contracts.yaml#logo-design
pilot_status: runtime_ready
pilot_limitations:
  - 不声称 Logo 已商标查重/版权清洁/可直接注册
  - 不声称已生成最终商用 logo 视觉资产
  - 不声称辅助图形系统已完整设计
---

# logo-design

## 定位

Logo 设计规范子技能,产出品牌标识的形态方向、应用规范与 AI 绘图提示词包。

## 核心能力

- 基于品牌策略(brand_brief)推导 logo 形态方向
- 黑白可用性验证(灰度/纯黑/反白三模式)
- 极致缩放验证(16×16px favicon 轮廓可辨,大尺寸精致)
- 组合形式规范(横/竖/图标锁版 + 安全留白)
- 辅助图形系统(从 logo 同源延展)
- 商标风险信号标注(非法律意见,需专业机构检索)
- AI 绘图 prompt pack 产出(含负向控制)

## 输入要求

**必需:**
- `brand_brief`: 品牌策略基线(由 brand-strategy 产出,含北极星/定位/人格关键词)

## 输出产物

**visual_spec** (JSON, schema: logo_spec.schema.json):
- `form`: { primary_shape, rationale }
- `color_refs`: 主色参考(HEX值)
- `black_white_usable`: 黑白可用性验证结果(boolean)
- `min_size_px`: 最小可识别尺寸(integer)
- `auxiliary_graphics`: 辅助图形方向
- `trademark_risk_signals`: 商标风险信号列表
- `application_scenarios`: 应用场景清单

**image_prompt_pack** (JSON, schema: logo_prompt_pack.schema.json):
- `prompts`: [{ platform, positive, negative }]
- `status`: "available" | "unavailable"

## 质量标准

- **黑白可用性**:灰度/纯黑/反白三模式均可识别
- **32px 识别度**:在 32×32px favicon 尺寸下轮廓唯一可辨(实际要求16px但留安全余量)
- **轮廓测试**:遮住细节只看剪影能认出
- **组合形式**:横/竖/图标锁版齐全
- **矢量缩放**:定义最小与最大尺寸范围
- **商标风险**:标注风险信号并明确声明"非查重,需专业机构检索"
- **策略一致**:logo 形态回溯到 brand_brief 人格关键词

## 能力边界

**不声称:**
- 不声称 Logo 已商标查重/版权清洁/可直接注册(仅产出设计规范与风险信号)
- 不声称已生成最终商用 logo 视觉资产(仅产出 logo_spec 规范与 AI 绘图 prompt)
- 不声称辅助图形系统已完整设计(产出方向与约束,非全套素材)

## 使用场景

- brand-strategy 完成后,需要 Logo 视觉方向
- 品牌焕新场景,更新 Logo 系统
- 与 color-system / typography-system 并行开发(基于冻结的 brand_brief 契约)

## 依赖关系

**上游(必需):**
- brand-strategy (消费 brand_brief)

**并行同级:**
- color-system
- typography-system

**下游消费者:**
- visual-identity (消费 logo_spec)
