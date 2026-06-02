# Reference Adapter: Persona Modeling (Stage 3)

> 本文档说明 ip-design skill 的 Stage 3(persona-modeling)如何应用共享方法论。

## 共享方法论引用

- **主方法论**: `design.persona.persona-modeling`(M03)
- **配套方法论**: `design.persona.voice-and-behavior-boundary`
- **产出模板**: `design.templates.persona-profile`

## 在本 stage 的应用方式

1. **输入映射**:
   - `brand_brief.personality_keywords` → M03 的"人格关键词起点"
   - `worldview.rules` / `worldview.relationship_network` → M03 的"世界观约束"

2. **决策框架应用**:
   - **行为模式序列为主**,MBTI 仅辅助:从 `personality_keywords` 推导行为模式(识别 → 拆解 → 执行 → 提升),每步给可观测信号;MBTI 标签说明各维度如何体现在行为中,**强制保留** `mbti_aux.note`(M03 `decision_framework` 第 1–2 点)。
   - 动机与恐惧分层:四类恐惧(能力/理解/价值/安全)至少 2 类,每个给应对方式与视觉提示(M03 `decision_framework` 第 3 点)。
   - 成长弧:关键事件必须有合理触发(M03 `decision_framework` 第 4 点)。
   - 声音边界:≥6 场景含失败场景(M03 配套方法论 `voice-and-behavior-boundary`)。

3. **必过项对齐**:
   - M03 必过项与本 stage Checkpoint C3 必过项对应:
     - `behavior_model.sequence` 不为空且每步有可观测信号 ✓
     - `mbti_aux.note` 保留 ✓
     - `motivation_and_fear.fears` 至少 2 类 ✓
     - `voice_and_behavior.scene_phrases.fail` 不为空 ✓
     - `behavior_red_lines` 可判定 ✓
     - `growth_arc.key_event.trigger` 不为空 ✓

4. **失败模式防线**:
   - F-P1 仅 MBTI 标签:prompt 强制先写行为模式,MBTI 标签只作辅助。
   - F-P2 无恐惧无缺陷:prompt 强制 fears 至少 2 类 + hidden_flaw 必填。
   - F-P3 失败话术甩锅或机械:prompt 强制 fail 场景体现人格,不能只说"系统错误"。

5. **产出结构**:
   按 `design.templates.persona-profile` 输出,含 `behavior_model` / `mbti_aux.note` / `motivation_and_fear.fears` / `voice_and_behavior.scene_phrases.fail` / `behavior_red_lines` / `growth_arc`。

## 与下游 stage 的契约

- `persona_profile.voice_and_behavior.emotion_expressions` 供 Stage 4(visual-translation)的状态延展对齐,情绪 × 视觉提示一一对应。
- `persona_profile.voice_and_behavior.scene_phrases` 供 Stage 5(narrative-planning)的对话语料库复用,**不重新发明**。
- `persona_profile.voice_and_behavior.context_tone` 供 Stage 6(landing-spec)的传播语调分场景复用。
