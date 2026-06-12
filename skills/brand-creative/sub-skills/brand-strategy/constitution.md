# brand-strategy Constitution

本文件定义 brand-strategy 子技能的运行时强制约束(runtime hard constraints)。

## 1. 差异化判定规则(Differentiation Determination)

### 1.1 有竞品矩阵支撑时

**触发条件:**
- `competitor_matrix` 输入存在
- `competitor_matrix.status == "complete"`
- `competitor_matrix.competitors` 至少包含 3 个竞品

**强制要求:**
- `differentiation.basis` 必须设为 `"competitor_matrix"`
- `differentiation.statement` 必须引用竞品矩阵中的具体证据
- 差异化声明必须基于竞品对比的客观事实

**示例:**
```json
{
  "differentiation": {
    "statement": "竞品普遍采用理性功能叙事(如 CompetitorA 强调效率、CompetitorB 突出数据),我们选择情感共鸣路线,强调创业者心理支持",
    "basis": "competitor_matrix"
  }
}
```

### 1.2 无竞品矩阵或数据不足时

**触发条件(任一):**
- `competitor_matrix` 输入缺失
- `competitor_matrix.status == "insufficient_data"`
- `competitor_matrix.competitors` 少于 3 个

**强制要求:**
- `differentiation.basis` 必须设为 `"inferred"`
- `differentiation.statement` 必须显式说明"基于产品特性推断,未经竞品对标验证"
- 差异化声明必须保守,避免绝对化表述

**示例:**
```json
{
  "differentiation": {
    "statement": "[inferred] 基于产品的情感支持特性,推断可能与偏功能导向的同类产品形成差异,但未经竞品对标验证",
    "basis": "inferred"
  }
}
```

## 2. 北极星约束(North Star Constraints)

### 2.1 情感化价值要求

**禁止(功能描述):**
- ❌ "提供高效的项目管理工具"
- ❌ "帮助用户快速完成任务"
- ❌ "最强大的数据分析平台"

**必须(情感化价值):**
- ✅ "让创业者在不确定性中感到被理解与支持"
- ✅ "赋予设计师掌控复杂性的自信"
- ✅ "让团队在协作中体验到信任与尊重"

### 2.2 验证标准

北极星必须通过以下测试:
1. **情感共鸣测试**: 是否描述用户内在感受/状态/关系?
2. **非功能测试**: 去掉产品功能词汇后,语句是否仍然完整?
3. **持久价值测试**: 是否超越单次使用场景,指向长期关系?

## 3. 人格关键词约束(Personality Keywords Constraints)

### 3.1 数量与维度

**强制要求:**
- 必须 3-5 个关键词
- 必须覆盖以下维度:
  - **情感维度**: 品牌情绪特质(如温暖/冷静/活力)
  - **价值维度**: 品牌价值取向(如创新/稳健/开放)
  - **行为维度**: 品牌行为风格(如直接/细腻/幽默)

### 3.2 示例

**不合格(只有情感维度):**
```json
["温暖", "友好", "亲切"]  // 缺乏价值与行为维度
```

**合格:**
```json
["温暖(情感)", "进取(价值)", "直接(行为)", "可信赖(价值)"]
```

## 4. 定位取舍约束(Positioning Trade-offs Constraints)

### 4.1 必须输出内容

品牌策略产出必须包含(可在 context_analysis 或 brand_brief 备注中):
1. **选择理由**: 为何选择此定位方向
2. **未选方向**: 至少列举 2 个未选择的定位方向
3. **取舍冲突**: 说明选择此定位放弃了什么(如"放弃大众市场覆盖,聚焦垂直人群")

### 4.2 示例

```markdown
## 定位取舍

**选择**: 情感支持型品牌(陪伴创业者心理旅程)

**未选方向**:
1. 功能效率型(强调工具强大/快速)
2. 权威专家型(强调行业领先/数据驱动)

**取舍理由**:
- 选择情感支持,放弃了与大厂的功能参数竞争
- 获得了创业者情感信任,但可能在企业级市场受限
```

## 5. 竞品矩阵消费约束(Competitor Matrix Consumption)

### 5.1 必须检查字段

在消费 `competitor_matrix` 时,必须检查:
- `status`: "complete" / "insufficient_data"
- `competitors.length`: 是否 >= 3
- `competitors[].visual_style`: 视觉风格对比
- `competitors[].communication`: 沟通方式对比
- `competitors[].market_position`: 市场定位对比

### 5.2 降级策略

若 `competitor_matrix.status == "insufficient_data"`:
- 不得强行基于不足数据做差异化判定
- 必须降级为 `basis: "inferred"`
- 必须在差异化声明中说明数据不足

## 6. 输出合规性检查(Output Compliance Check)

### 6.1 必须字段

`brand_brief` 输出必须包含:
- `north_star` (string, 情感化价值)
- `positioning` (string)
- `differentiation` (object, 包含 statement 与 basis)
- `core_values` (array, minItems: 1)
- `personality_keywords` (array, minItems: 3, maxItems: 5)
- `target_user` (string)

### 6.2 Schema 合规

输出必须通过 `brand_brief.schema.json` 验证:
- `differentiation.basis` 只能是 `"competitor_matrix"` 或 `"inferred"`
- `personality_keywords` 长度必须在 [3, 5] 区间

## 7. 能力边界声明(Capability Boundary)

### 7.1 运行时不得声称

- 不得声称产出可直接商用(必须标注需资深评审)
- 不得声称已覆盖完整品牌战略(营销/财务/组织不在范围)
- `basis: "inferred"` 时不得声称已完成竞品对标

### 7.2 输出中的免责声明

在 `brand_brief` 中建议包含 `_meta.disclaimer`:
```json
{
  "_meta": {
    "disclaimer": "本策略基线需资深品牌经理评审后方可商用。差异化判定基于 [competitor_matrix/inferred],不构成完整竞品战略分析。"
  }
}
```

---

**Constitution 版本**: 0.1.0-pilot
**对应 Contract**: B1.0 sub-skill-contracts.yaml#brand-strategy
**强制执行**: 所有 pipeline stages 必须遵守上述约束,违反即视为 runtime error。
