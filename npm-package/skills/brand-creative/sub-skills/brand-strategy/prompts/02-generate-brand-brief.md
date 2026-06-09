# Stage 2: 产出品牌策略基线(brand_brief)

你是资深品牌战略顾问。任务:基于上下文分析,产出品牌策略基线。

## 输入

**context_analysis**(来自 Stage 1):
```
{{context_analysis}}
```

**product_brief**:
```
{{product_brief}}
```

**target_user**:
```
{{target_user}}
```

**competitor_matrix** (可选):
```json
{{competitor_matrix}}
```

## 产出任务

基于上下文分析,产出品牌策略基线(`brand_brief`),包含:

### 1. north_star(北极星)

**要求:**
- 必须是**情感化价值**,描述用户内在感受/状态/关系
- 不能只是功能描述(如"提供高效工具")
- 通过情感共鸣测试:是否描述用户心理/关系层面的价值?

**示例:**
- ✅ "让创业者在不确定性中感到被理解与支持"
- ✅ "赋予设计师掌控复杂性的自信"
- ❌ "提供最强大的项目管理工具"(功能描述)

### 2. positioning(品牌定位)

简洁陈述品牌在目标用户心智中的位置:
- 我们是谁
- 为谁服务
- 提供什么独特价值

**示例:**
"面向技术创业者的情感支持型生产力工具,在功能之上提供心理陪伴"

### 3. differentiation(差异化判定)

**包含两个字段:**
- `statement`(string): 差异化声明
- `basis`(enum): 判定基础 ["competitor_matrix" | "inferred"]

**规则:**

**若 competitor_matrix 存在且 status="complete":**
```json
{
  "statement": "竞品普遍采用理性功能叙事(如 CompetitorA 强调效率、CompetitorB 突出数据),我们选择情感共鸣路线,强调创业者心理支持",
  "basis": "competitor_matrix"
}
```

**若 competitor_matrix 缺失或 status="insufficient_data":**
```json
{
  "statement": "[inferred] 基于产品的情感支持特性,推断可能与偏功能导向的同类产品形成差异,但未经竞品对标验证",
  "basis": "inferred"
}
```

### 4. core_values(核心价值观)

至少 1 个核心价值观,指导品牌行为与决策。

**示例:**
```json
["同理心", "诚实透明", "持续进化"]
```

### 5. personality_keywords(人格关键词)

**要求:**
- 必须 3-5 个关键词
- 必须覆盖三个维度:
  - **情感维度**: 品牌情绪特质(温暖/冷静/活力/...)
  - **价值维度**: 品牌价值取向(创新/稳健/开放/...)
  - **行为维度**: 品牌行为风格(直接/细腻/幽默/...)

**示例:**
```json
["温暖(情感)", "进取(价值)", "直接(行为)", "可信赖(价值)"]
```

### 6. target_user(目标用户)

简洁描述目标用户画像。

**示例:**
"25-40岁技术背景创业者,面临高不确定性与心理压力,需要工具之外的情感支持"

## 输出格式

输出必须是严格的 JSON,符合以下 schema:

```json
{
  "north_star": "string (情感化价值)",
  "positioning": "string",
  "differentiation": {
    "statement": "string",
    "basis": "competitor_matrix" | "inferred"
  },
  "core_values": ["string", ...],  // minItems: 1
  "personality_keywords": ["string", ...],  // minItems: 3, maxItems: 5
  "target_user": "string",
  "_meta": {
    "positioning_tradeoffs": {
      "chosen_direction": "string",
      "unchosen_directions": ["string", ...],
      "tradeoff_reasoning": "string"
    },
    "disclaimer": "本策略基线需资深品牌经理评审后方可商用。差异化判定基于 [competitor_matrix/inferred],不构成完整竞品战略分析。"
  }
}
```

## 强制约束

1. `north_star` 必须通过情感共鸣测试(描述用户内在感受)
2. `competitor_matrix` 存在时,`differentiation.basis` 必须是 `"competitor_matrix"`
3. `competitor_matrix` 缺失或不足时,`differentiation.basis` 必须是 `"inferred"`
4. `personality_keywords` 必须 3-5 个,覆盖情感/价值/行为维度
5. `_meta.positioning_tradeoffs` 必须说明选择此定位放弃了什么

## 质量检查清单

产出前自检:
- [ ] north_star 是情感化价值,不是功能描述
- [ ] differentiation.basis 与 competitor_matrix 状态一致
- [ ] personality_keywords 数量在 [3, 5],覆盖三个维度
- [ ] positioning_tradeoffs 说明了未选方向与取舍理由
- [ ] 若 basis="inferred",差异化声明中包含"未经验证"说明

---

**参考资产**:
- `knowledge/design/strategy/brand-strategy-methodology.md`: 品牌战略决策框架
- `knowledge/design/quality/brand-identity-quality-rubric.md`: 品牌策略质量标准
- `knowledge/design/quality/brand-creative-failure-modes.md`: 常见失败模式
