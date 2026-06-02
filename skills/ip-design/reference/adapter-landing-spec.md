# Reference Adapter: Landing Spec (Stage 6)

> 本文档说明 ip-design skill 的 Stage 6(landing-spec)如何应用共享方法论。

## 共享方法论引用

- **主方法论**: `design.ip.brand-material-realization`(M06)
- **质量评审方法论**:
  - `design.quality.ip-design-quality-rubric`
  - `design.quality.stage-review-checklists`
  - `design.quality.common-failure-modes`
  - `design.quality.professional-gap-report`
- **产出模板**: `design.templates.brand-material-spec`

## 在本 stage 的应用方式

1. **输入映射**:
   - `visual_spec.strict_avoidance` → M06 的"禁止使用示例继承"
   - `persona_profile.voice_and_behavior.context_tone` → M06 的"传播语调分场景"
   - `content_plan.content_matrix` → M06 的"宣传物料尺寸决策"

2. **决策框架应用**(M06):
   - 品牌应用规范:IP+logo 联合使用(最小尺寸/安全区)/禁止使用示例 ≥5(继承 `visual_spec.strict_avoidance`)。
   - 衍生品清单:每条含**可落地性与成本档位**,避免过度复杂(M06 `expert_heuristics` 第 2 点)。
   - 印刷物料:**必须标注 CMYK/Pantone**(M06 `expert_heuristics` 第 3 点)。
   - 传播语调:与 `persona_profile.voice_and_behavior` 一致且分场景,**不重新发明**(M06 `expert_heuristics` 第 4 点)。

3. **质量评审应用**:
   - **九维 rubric 自评**(rubric):D1–D9 每维打四档(高阶可评审/中阶可用/低阶仅雏形/不合格),给简短依据;一票否决项(D2/D6/D8)任一不合格 → 整体不合格。
   - **失败模式自检**(failure-modes):列出命中的 F-* 编号,每个说明处理方式(已改/写入 gap)。
   - **professional gap report**(gap-report):触发条件(rubric 任一维度低于中阶 / 一票否决不合格 / 必过项未过 / 关键输入缺失);每条 gap 五段(gap_id / stage_or_dimension / current_state / reason / to_reach_mid_tier / temporary_release_boundary)。

4. **必过项对齐**(Quality Gate QG2):
   - M06 必过项 + rubric/checklists/failure-modes/gap-report 必过项与 QG2 对应:
     - 应用规范齐全 ✓
     - 衍生品含可落地性与成本 ✓
     - 印刷物料标注 CMYK/Pantone ✓
     - 传播语调与 persona 一致 ✓
     - 九维 rubric 自评全打且有依据 ✓
     - 一票否决项(D2/D6/D8)合格 ✓
     - 失败模式自检完成 ✓
     - 触发 gap 时已写 report ✓

5. **失败模式防线**:
   - F-M1 衍生品过度复杂:prompt 强制每条衍生品评估可落地性与成本。
   - F-M2 印刷无 CMYK/Pantone:prompt 强制印刷类物料标注色彩模式。
   - F-M3 传播语调脱节:prompt 强制复用 `persona.voice_and_behavior.context_tone`。
   - F-X2 假装完成不写 gap:prompt 强制触发 gap 时写 report,不允许空 gaps。

6. **产出结构**:
   两个产出物:
   - `brand_material_spec`:按 `design.templates.brand-material-spec`,含上述全部字段。
   - `professional_gap_report`:按 `design.quality.professional-gap-report`,含 `total_statement` / `rubric_self_eval` / `failure_mode_checklist` / `gaps`(若触发)。

## 本 stage 是最终质量闸门

QG2 是 pipeline 最后一道质量门,9 个必过项全过才允许标记 pipeline 完成。不达中阶或一票否决不合格的产出物必须附 gap report,向品牌方/设计师显式说明已知短板与临时放行边界,**不允许假装完成**(constitution 第 4 条)。
