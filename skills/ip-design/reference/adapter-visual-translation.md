# Reference Adapter: Visual Translation (Stage 4)

> 本文档说明 ip-design skill 的 Stage 4(visual-translation)如何应用共享方法论。

## 共享方法论引用

- **主方法论**: `design.visual.visual-translation`(M04)
- **配套方法论**: `design.visual.image-prompt-system`
- **产出模板**: `design.templates.visual-spec`

## 在本 stage 的应用方式

1. **输入映射**:
   - `brand_brief.personality_keywords` → M04 的"人格关键词 → 形态映射"
   - `worldview.worldview_keywords` → M04 的"世界观关键词 → 材质/意象"
   - `persona_profile.voice_and_behavior.emotion_expressions` → M04 的"状态延展对齐"
   - `brand_assets` → M04 的"品牌基因继承"

2. **决策框架应用**:
   - **品牌基因继承**(若 `brand_assets` 非空):三栏(继承/新增/禁冲突)(M04 `decision_framework` 第 1 点)。
   - **形态设计**:主形/辅形有取舍依据,核心符号 1 个承担 60–70% 识别权重(M04 `decision_framework` 第 2 点)。
   - **识别度量化**:32px 可辨 + 四级简化(大/中/小/极小)(M04 `decision_framework` 第 5 点,`expert_heuristics` 第 1 点)。
   - **状态延展**:≥4 状态,每状态与 `persona_profile.emotion_expressions` 对齐(M04 `decision_framework` 第 6 点)。
   - **风格谱系坐标**:五维显式锁定(M04 `decision_framework` 第 7 点)。
   - **严格禁忌**:≥5 条可判定(M04 `decision_framework` 第 8 点),同步成提示词负向。
   - **提示词四层**:核心符号定位/设计理念/技术参数/质量与避免;覆盖 ≥2 平台;基准图 + 检查点(M04 配套方法论 `image-prompt-system`)。

3. **必过项对齐**(Quality Gate QG1):
   - M04 必过项与本 stage QG1 必过项对应:
     - 基因继承三栏(若有既有品牌)✓
     - 32px 可辨 ✓
     - 四级简化齐全 ✓
     - 风格谱系坐标锁定 ✓
     - 严格禁忌 ≥5 ✓
     - 提示词四层结构 ✓
     - 覆盖 ≥2 平台 ✓
     - 基准图 + 一致性检查点 ✓

4. **失败模式防线**:
   - F-V1 不继承品牌基因:prompt 检查 `brand_assets`,非空时三栏必填。
   - F-V2 32px 糊掉:prompt 强制 `recognizability.canonical_test.legible_at_32px: true`。
   - F-V3 风格漂移:prompt 强制五维风格坐标 + locked_position_summary。
   - F-V4 视觉跑偏(3D/二次元):prompt 强制 `strict_avoidance ≥5` + 负向 prompt。
   - F-PR1–F-PR4(提示词失败模式):prompt 强制四层 + 量化 + 负向 + 基准图。

5. **产出结构**:
   两个产出物:
   - `visual_spec`:按 `design.templates.visual-spec`,含上述全部字段。
   - `image_prompt_pack`:基准图(四层)+ 三视图 + 状态图(≥4)+ 多平台(≥2)+ 锁定值 + 检查点。

## 与下游 stage 的契约

- `visual_spec.state_extension` 供 Stage 5(narrative-planning)参考,但内容规划以 `persona_profile` 为主。
- `visual_spec.strict_avoidance` 供 Stage 6(landing-spec)的禁止使用示例继承。
- `visual_spec.prompt_handoff.locked_values` 供 Stage 6 物料规范一致性锁定。
