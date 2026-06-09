# Reference Adapter: Strategy Alignment (Stage 1)

> 本文档说明 ip-design skill 的 Stage 1(strategy-alignment)如何应用共享方法论,不复制共享正文。

## 共享方法论引用

- **主方法论**: `design.strategy.brand-strategy-alignment`(M01)
- **产出模板**: `design.templates.brand-brief`

## 在本 stage 的应用方式

1. **输入映射**:
   - `product_brief` → M01 的"产品/服务定义、业务目标"
   - `target_user` → M01 的"用户画像"
   - `competitors` → M01 的"竞品矩阵"
   - `brand_assets` → M01 的"既有品牌资产(若有)"

2. **决策框架应用**:
   - 北极星五要素:从 `product_brief` 提炼能力与方式,从 `target_user` 提炼用户对象与期望感受,价值必须落在情感/体验层(M01 `decision_framework` 第 1 点)。
   - 人格关键词 3–5 个:从北极星 × 用户痛点推导,每个给依据链(M01 `decision_framework` 第 4 点)。
   - 差异化:从 `competitors` 找空白,一句话说清"为什么不是 X、不是 Y"(M01 `decision_framework` 第 5 点);**基于空白而非贬低**(M01 `expert_heuristics` 第 3 点)。

3. **必过项对齐**:
   - M01 必过项与本 stage Checkpoint C1 必过项一一对应:
     - 北极星五要素 + 情感价值 ✓
     - 用户画像推断标 `[inferred]` ✓
     - 人格关键词 3–5 且有依据 ✓
     - 竞品 ≥3 且差异化基于空白 ✓

4. **失败模式防线**:
   - F-S1 北极星功能化:prompt 强制自检"价值是否落在情感/体验层",不过不放行。
   - F-S2 用户画像臆造:推断处标 `[inferred]`,缺失字段写 gaps。
   - F-S3 差异化靠贬低:prompt 禁止"竞品做得不好"句式,必须基于空白。

5. **产出结构**:
   严格按 `design.templates.brand-brief` 的 YAML 字段输出,包含 `north_star.five_elements` / `personality_keywords[].rationale` / `competitor_matrix[].gap_we_can_fill` / `differentiation_summary` / `inferences` / `gaps`。

## 不在本 stage 做的事

- 不写视觉形态/色彩(留给 Stage 4)。
- 不写世界观规则/关系网(留给 Stage 2)。
- 不写声音边界/对话语料(留给 Stage 3)。

## 与下游 stage 的契约

- `brand_brief.personality_keywords` 供 Stage 3(persona-modeling)消费,作为行为模式推导的起点。
- `brand_brief.north_star` 供 Stage 2(worldview-building)与 Stage 5(narrative-planning)消费。
- `brand_brief.competitor_matrix` 供 Stage 6(landing-spec)的 D2 差异化维度 rubric 自评使用。
