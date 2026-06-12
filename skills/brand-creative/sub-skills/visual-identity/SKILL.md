---
name: visual-identity
version: 0.1.0-pilot
type: pipeline
group: brand-creative
phase: 2-visual-identity
purpose: 汇总 logo/color/typography 三者产出完整 VI 手册,补充一致性检查/应用规范/禁忌/缺口声明
scope: 品牌视觉识别系统聚合(企业品牌/产品品牌/服务品牌)
inputs:
  required:
    - visual_spec
    - color_palette
    - typography_spec
  optional: []
outputs:
  - id: vi_manual
    type: style_guide
    format: json
    schema_ref: ../../contracts/schemas/vi_manual.schema.json
knowledge_dependencies:
  - ../../../../knowledge/design/visual/visual-identity-integration-methodology.md
  - ../../../../knowledge/design/quality/brand-identity-quality-rubric.md
  - ../../../../knowledge/design/quality/brand-creative-failure-modes.md
  - ../../../../knowledge/design/quality/professional-gap-report.md
quality_gate:
  checkpoint_id: C5-visual-identity
  must_pass:
    - logo/color/typography 三者一致性检查(气质/情绪/使用场景无冲突)
    - application_rules 至少覆盖 5 个场景(名片/网站/社交媒体/包装/海报)
    - 上游 needs_verification / needs_manual_check 警告全部继承到 inherited_warnings
    - gaps 字段显式声明待人工确认项(不得吞掉缺口)
  one_vote_veto:
    - logo 黑白不可用(继承自 logo-design)
    - 主色对比度 < 3:1(继承自 color-system)
    - 覆盖或修改上游产物(visual_spec / color_palette / typography_spec)
contract_ref: ../../contracts/sub-skill-contracts.yaml#visual-identity
pilot_status: runtime_ready
pilot_limitations:
  - 不声称 VI 手册已完成所有场景应用设计
  - 不声称已达"高阶可评审"(默认中阶可用)
  - 不声称已完成法务/印刷/字体授权确认
  - 不声称是最终品牌手册(brand-guidelines 才是最终交付物)
---

# visual-identity

## 定位

视觉识别系统聚合子技能,消费 logo-design / color-system / typography-system 三者产出,做资深设计总监式一致性判断,产出完整 VI 手册。

## 核心能力

- 聚合三个上游产物为统一的视觉识别系统
- 检查 logo 气质与品牌人格是否一致
- 检查色彩情绪与 logo 方向是否冲突
- 检查字体气质与 logo/color 是否同一品牌语义
- 继承上游的黑白、小尺寸、可访问性、跨端、授权风险等警告
- 明确"不一致如何处理"：保留、降级、待确认、返工建议
- 产出 professional gap report，不得把缺口吞掉

## 输入要求

**必需（全部来自上游子技能产出）:**
- `visual_spec`: Logo 设计规范（来自 logo-design）
- `color_palette`: 品牌色彩调色板（来自 color-system）
- `typography_spec`: 字体系统规范（来自 typography-system）

## 输出产物

`vi_manual` (JSON):
- `logo`: 引用 visual_spec 的关键规则
- `color`: 引用 color_palette 的关键规则
- `typography`: 引用 typography_spec 的关键规则
- `auxiliary_graphics`: 辅助图形方向
- `application_rules`: 基础应用规范（至少 5 个场景）
- `taboos`: 使用禁忌
- `consistency_check`: 三者一致性检查结果
- `inherited_warnings`: 继承自上游的警告
- `gaps`: 待人工确认项（不得为空，至少声明标准边界）

## 质量标准

- 不重新生成 logo / 色彩 / 字体，不覆盖上游产物
- 一致性检查必须在 logo/color/typography 三者之间做交叉判断
- 不一致项必须明确处理策略（保留/降级/待确认/返工建议）
- application_rules 必须至少 5 个场景
- 上游 needs_verification / needs_manual_check 必须继承
- gaps 字段不得为空，至少声明 pilot 标准边界
