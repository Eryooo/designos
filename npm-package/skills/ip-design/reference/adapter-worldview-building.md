# Reference Adapter: Worldview Building (Stage 2)

> 本文档说明 ip-design skill 的 Stage 2(worldview-building)如何应用共享方法论。

## 共享方法论引用

- **主方法论**: `design.ip.worldview-building`(M02)
- **产出模板**: `design.templates.worldview`

## 在本 stage 的应用方式

1. **输入映射**:
   - `brand_brief` → M02 的"北极星与人格关键词"

2. **决策框架应用**:
   - 时空定位:从 `brand_brief.north_star` 推导世界观基调(M02 `decision_framework` 第 1 点)。
   - 能力规则:**必须有边界**,显式列出"不能做什么"(M02 `decision_framework` 第 2 点,`expert_heuristics` 第 1 点)。
   - 社会规则:**必须含冲突来源与反对者**(M02 `decision_framework` 第 3 点),relationship_network.opponent 不为空。
   - 世界观关键词 3–5 个:供 Stage 4 visual-translation 消费(M02 `output_contract`)。

3. **必过项对齐**:
   - M02 必过项与本 stage Checkpoint C2 必过项对应:
     - `capability_rules.cannot_do` 不为空 ✓
     - `social_rules.conflict_sources` 不为空 ✓
     - `relationship_network.opponent` 不为空 ✓
     - `worldview_keywords` 数量 3–5 ✓
     - `consistency_check` 两项均为 true ✓

4. **失败模式防线**:
   - F-W1 万能 IP:prompt 强制 `cannot_do` 不为空,否则不放行。
   - F-W2 规则自相矛盾:prompt 要求做整体校对,`consistency_check` 任一为 false 不放行。

5. **产出结构**:
   按 `design.templates.worldview` 输出,含 `spacetime` / `rules.capability_rules.cannot_do` / `relationship_network.opponent` / `worldview_keywords` / `consistency_check`。

## 与下游 stage 的契约

- `worldview.worldview_keywords` 供 Stage 4(visual-translation)消费,转成材质/意象。
- `worldview.cultural_archetype` 供 Stage 4 设计理念与 Stage 5 内容叙事消费。
- `worldview.relationship_network` 供 Stage 3(persona-modeling)的 action_network 回扫对齐。
