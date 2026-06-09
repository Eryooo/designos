# Reference Adapter: Narrative Planning (Stage 5)

> 本文档说明 ip-design skill 的 Stage 5(narrative-planning)如何应用共享方法论。

## 共享方法论引用

- **主方法论**: `design.ip.content-narrative`(M05)
- **产出模板**: `design.templates.content-plan`

## 在本 stage 的应用方式

1. **输入映射**:
   - `brand_brief.north_star` → M05 的"首秀目标推导"
   - `persona_profile.behavior_model` → M05 的"首秀亮相方式"
   - `persona_profile.voice_and_behavior` → M05 的"对话语料库复用"
   - `visual_spec.state_extension` → 参考,但内容以 persona 为主

2. **决策框架应用**:
   - IP 首秀:第一句台词**必须体现人格**,不能泛泛打招呼(M05 `decision_framework` 第 1 点,`expert_heuristics` 第 1 点)。
   - 核心事件 ≥3,关系递进(建立信任 → 深化关系 → 默契与惊喜),每事件的 `relationship_after` 必须清晰变化(M05 `decision_framework` 第 2 点,`expert_heuristics` 第 2 点)。
   - 对话语料库:复用 `persona_profile.voice_and_behavior.scene_phrases`,**不重新发明**(M05 `decision_framework` 第 3 点)。
   - 内容矩阵:渠道选择必须给 `target_user_match_rationale`(M05 `decision_framework` 第 4 点)。
   - 节奏日历:≥4 周期,可持续而非一次性(M05 `decision_framework` 第 5 点)。

3. **必过项对齐**:
   - M05 必过项与本 stage Checkpoint C4 必过项对应:
     - 首秀台词体现人格且首秀目标明确 ✓
     - 核心事件 ≥3 且关系递进不重复 ✓
     - 对话语料覆盖 ≥6 场景含失败场景 ✓
     - 内容矩阵渠道匹配目标用户 ✓
     - 节奏日历 ≥4 周期可持续 ✓

4. **失败模式防线**:
   - F-C1 首秀平淡:prompt 强制第一句台词体现人格,不能泛泛打招呼。
   - F-C2 事件展功能不展关系:prompt 强制每事件的 `relationship_after` 写清变化。

5. **产出结构**:
   按 `design.templates.content-plan` 输出,含 `ip_debut.first_line` / `core_events[].relationship_after` / `dialogue_corpus.fail` / `content_matrix[].target_user_match_rationale` / `cadence_calendar.schedule(≥4)`。

## 与下游 stage 的契约

- `content_plan.dialogue_corpus` 供 Stage 6(landing-spec)的传播语调分场景复用。
- `content_plan.content_matrix` 供 Stage 6 的宣传物料尺寸/渠道决策。
