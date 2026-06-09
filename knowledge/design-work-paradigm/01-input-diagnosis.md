# 01. 输入诊断与完整性评估

## 定义与目的

输入诊断（Input Diagnosis）是设计推理流程的第一步，负责评估输入材料的质量、完整性和可用性，识别缺失、模糊和冲突的信息，为后续推理建立可靠基础。

**核心目标**：
1. 清点所有输入材料
2. 评估输入质量和完整性
3. 识别 gaps、ambiguities、conflicts
4. 生成 assumptions 列表
5. 判断是否可以继续（或需要 blocked/fallback_safe）

## 适用场景

- ✅ 所有设计类 skills 的第一个 stage
- ✅ 用户提供 PRD、截图、设计简报等输入时
- ✅ 需要判断"输入是否足够支撑高质量输出"

## 输入要求

| 输入类型 | 必需 | 说明 |
|---------|------|------|
| `primary_input` | ✅ | 主要输入（PRD、截图目录、设计简报） |
| `secondary_inputs` | ❌ | 辅助输入（用户画像、设计策略、竞品分析） |
| `constraints` | ❌ | 已知约束（技术栈、时间、预算） |

## 输出规范

输出 `requirement_inventory` artifact，包含以下字段：

```json
{
  "artifact_type": "requirement_inventory",
  "input_materials": {
    "primary": {
      "type": "prd | screenshots | design_brief",
      "file_path": "string",
      "file_size": "integer (bytes)",
      "format": "string",
      "quality_score": 0.0-1.0,
      "readability": "high | medium | low"
    },
    "secondary": [
      {
        "type": "string",
        "file_path": "string",
        "availability": "complete | partial | missing"
      }
    ]
  },
  "completeness_assessment": {
    "overall_score": 0.0-1.0,
    "dimensions": {
      "business_goals_clarity": 0.0-1.0,
      "user_definition_clarity": 0.0-1.0,
      "functional_requirements_completeness": 0.0-1.0,
      "non_functional_requirements_completeness": 0.0-1.0,
      "constraints_clarity": 0.0-1.0
    }
  },
  "functional_requirements": [],
  "non_functional_requirements": [],
  "ambiguities": [
    {
      "ambiguity_id": "AMB-001",
      "description": "string",
      "affected_areas": ["array"],
      "clarification_needed": "string"
    }
  ],
  "conflicts": [
    {
      "conflict_id": "CONF-001",
      "description": "string",
      "conflicting_statements": ["array"],
      "resolution_recommendation": "string"
    }
  ],
  "gaps": [],
  "assumptions": [],
  "readiness_decision": {
    "decision": "proceed | fallback_safe | blocked",
    "rationale": "string",
    "blockers": ["array"],
    "mitigation_strategy": "string"
  }
}
```

## 推理过程

### Step 1: 清点输入材料

1. 识别主要输入类型（PRD / 截图 / 设计简报）
2. 检查文件可读性（格式、大小、编码）
3. 识别次要输入（user_persona, design_strategy, existing_analytics）
4. 记录输入来源和版本

**质量标准**：
- ✅ 主要输入必须存在且可读
- ✅ 文件格式必须被支持（PDF, MD, DOCX, PNG, JPG）
- ❌ 如果主要输入不可读，立即进入 `blocked` 状态

### Step 2: 评估输入完整性

按 5 个维度评估：

1. **业务目标清晰度** (business_goals_clarity)
   - PRD 是否有明确的商业目标章节？
   - 目标是否可量化？
   - 是否有优先级？
   - 评分规则：
     - 1.0: 有明确章节 + 可量化指标 + 优先级
     - 0.7: 有提及但不够量化
     - 0.3: 仅有模糊描述
     - 0.0: 完全没有

2. **用户定义清晰度** (user_definition_clarity)
   - 是否有用户画像 / 用户角色？
   - 是否定义用户特征（年龄、职业、技能水平）？
   - 是否有用户痛点 / 需求？
   - 评分规则：同上

3. **功能需求完整性** (functional_requirements_completeness)
   - 是否列出核心功能？
   - 是否有功能优先级？
   - 是否有用户故事或用例？
   - 评分规则：
     - 1.0: ≥ 10 个明确功能 + 优先级 + 用例
     - 0.7: 5-9 个功能
     - 0.3: < 5 个功能
     - 0.0: 无功能列表

4. **非功能需求完整性** (non_functional_requirements_completeness)
   - 是否有性能要求？
   - 是否有安全 / 隐私要求？
   - 是否有兼容性要求？
   - 评分规则：同上

5. **约束清晰度** (constraints_clarity)
   - 是否有技术栈限制？
   - 是否有时间 / 预算限制？
   - 是否有合规要求？

**整体完整性评分**：
```
overall_score = (
    business_goals_clarity * 0.3 +
    user_definition_clarity * 0.25 +
    functional_requirements_completeness * 0.25 +
    non_functional_requirements_completeness * 0.1 +
    constraints_clarity * 0.1
)
```

### Step 3: 识别模糊需求 (Ambiguities)

扫描输入中的模糊表达：

**常见模糊模式**：
- "提升效率"（未量化）
- "用户友好"（主观）
- "尽可能快"（无具体指标）
- "支持主流浏览器"（未定义"主流"）
- "简洁美观"（无具体标准）

**处理方式**：
```json
{
  "ambiguity_id": "AMB-001",
  "description": "PRD 提到'提升效率'但未量化",
  "affected_areas": ["business_goals", "success_metrics"],
  "clarification_needed": "需要明确：提升哪个环节的效率？提升多少？如何衡量？",
  "default_interpretation": "假设为'用户完成核心任务的时间减少 30%'",
  "risk_if_wrong": "medium"
}
```

### Step 4: 识别冲突信息 (Conflicts)

检查内部矛盾：

**常见冲突模式**：
- 目标冲突："快速上线" vs "完美体验"
- 用户冲突：不同章节对用户的描述不一致
- 功能冲突：需求列表 vs 范围声明不一致
- 约束冲突："必须支持 IE11" vs "使用最新前端技术"

**处理方式**：
```json
{
  "conflict_id": "CONF-001",
  "description": "目标与约束冲突",
  "conflicting_statements": [
    "PRD 2.1: 要求 Q2 上线（3 个月）",
    "PRD 4.3: 功能列表包含 15 个复杂功能"
  ],
  "resolution_recommendation": "建议 MVP 仅包含 P0 功能（5 个），其余 10 个功能放入 Phase 2",
  "requires_stakeholder_decision": true
}
```

### Step 5: 识别信息缺失 (Gaps)

记录所有缺失的关键信息：

**必需信息清单**（根据 skill 类型）：

**prd2proto 必需**：
- [ ] 业务目标
- [ ] 用户角色定义
- [ ] 核心功能列表
- [ ] 技术栈约束

**uxeval 必需**：
- [ ] 产品定位
- [ ] 目标用户
- [ ] 核心任务流程

**ai-analytics 必需**：
- [ ] 业务背景
- [ ] 数据来源
- [ ] 分析目标

**Gap 严重程度判断**：
- **critical**: 缺失后无法生成合格产物（如 prd2proto 缺少功能列表）
- **high**: 严重影响质量（如缺少用户画像）
- **medium**: 影响部分功能（如缺少非功能需求）
- **low**: 可用默认值补充（如缺少配色偏好）

### Step 6: 生成假设列表 (Assumptions)

对于无法避免的缺失信息，明确列出假设：

```json
{
  "assumption_id": "ASM-001",
  "description": "假设用户为中小企业销售主管（25-40 岁）",
  "rationale": "基于产品定位（CRM）和行业惯例",
  "validation_method": "需要真实用户访谈验证",
  "risk_if_wrong": "high",
  "affected_downstream": ["user_task_map", "user_journey_map", "interaction_rules"]
}
```

### Step 7: 做出就绪决策 (Readiness Decision)

基于以上分析，判断是否可以继续：

**决策规则**：

```python
if overall_score >= 0.8 and len(critical_gaps) == 0:
    decision = "proceed"
    # 可以继续，质量有保障
    
elif overall_score >= 0.5 and len(critical_gaps) == 0:
    decision = "proceed"
    warnings.append("输入质量中等，推断内容会较多，需人工复核")
    
elif overall_score >= 0.3 or len(critical_gaps) > 0:
    decision = "fallback_safe"
    # 输入不足，降级到低保真模式
    # 例如：prd2proto 只生成线框图，不生成高保真原型
    
else:
    decision = "blocked"
    # 输入严重不足，无法继续
    blockers = list(critical_gaps)
```

**输出示例**：

```json
{
  "readiness_decision": {
    "decision": "fallback_safe",
    "rationale": "输入完整性评分 0.65，缺少用户画像和部分非功能需求。可生成低保真原型，但不建议直接用于高保真设计。",
    "blockers": [],
    "mitigation_strategy": "降级到 PM 模式（线框图），标注所有推断内容，生成 professional_gap_report 说明质量限制"
  }
}
```

## 质量标准

### Must Have
1. ✅ 所有输入文件都被扫描
2. ✅ `completeness_assessment` 的 5 个维度都有评分
3. ✅ 所有识别的 ambiguities 都有 `default_interpretation`
4. ✅ 所有识别的 conflicts 都有 `resolution_recommendation`
5. ✅ 所有 critical gaps 都被记录
6. ✅ `readiness_decision` 有明确的 rationale
7. ✅ 如果决策是 `blocked`，必须列出 blockers

### Should Have
8. ✅ `overall_score` < 0.7 时，必须生成 warnings
9. ✅ 每个 assumption 都有 `risk_if_wrong` 评估
10. ✅ 每个 gap 都有 `mitigation` 建议

### Nice to Have
11. ✅ 提供输入质量改进建议
12. ✅ 对比行业标准 PRD/设计简报的完整性

## 失败模式

### 输入问题
1. ❌ 主要输入文件损坏或不可读 → 立即 `blocked`
2. ❌ PRD 完全没有功能描述 → `blocked`，要求补充
3. ❌ 截图质量极低（< 100px）→ `blocked` 或要求重新截图

### 输出问题
4. ❌ `completeness_assessment` 所有维度都是 1.0 → 可能过度乐观，需复核
5. ❌ `ambiguities` 列表为空但 PRD 有明显模糊表达 → 识别不足
6. ❌ `readiness_decision` 是 `proceed` 但 `overall_score` < 0.5 → 判断错误

### 追溯问题
7. ❌ Gap 标注为 `critical` 但决策是 `proceed` → 逻辑矛盾
8. ❌ Assumption 的 `affected_downstream` 为空 → 缺少影响分析

## Anti-Patterns

1. ❌ 为了"让流程继续"而低估 gaps 的严重性
2. ❌ 将明显的冲突标记为"可接受的权衡"
3. ❌ 隐藏 ambiguities，直接用"最可能的解释"
4. ❌ 所有 ambiguities 都用"行业惯例"解释
5. ❌ `readiness_decision` 永远是 `proceed`（不敢说"输入不够"）
6. ❌ 将"输入不足"归咎于用户，而不是诚实记录
7. ❌ 为了提高 `overall_score` 而人为调整维度权重
8. ❌ 将"未明确"和"明确为空"混淆（如 PRD 说"暂无非功能需求" vs PRD 没提）

## 与其他方法的关系

- **上游**：无（这是第一步）
- **下游**：
  - `02-objective-decomposition`：依赖 `requirement_inventory`
  - `03-user-task-modeling`：受 user_definition_clarity 影响
  - 所有后续方法：受 `readiness_decision` 约束

**如果 `readiness_decision` 是 `fallback_safe`**：
- 所有下游方法必须进入"低保真模式"
- 所有推断内容的 `risk_if_wrong` 自动升级一档
- 最终 `professional_gap_report` 必须强调"输入不足导致质量受限"

**如果 `readiness_decision` 是 `blocked`**：
- Pipeline 立即停止
- 返回 blockers 列表给用户
- 不生成任何下游资产

## 实例

### 输入：高质量 PRD

```markdown
# CRM 系统 PRD

## 1. 商业目标
- Q2 获取 50 家付费企业客户
- GMV 达到 100 万元
- 单客户管理时间减少 30%

## 2. 用户画像
- 主要用户：中小企业销售主管
- 年龄：25-40 岁
- 技能水平：熟练使用企业微信、钉钉
- 痛点：Excel 管理客户信息容易丢失、团队无法实时查看

## 3. 核心功能（按优先级）
P0:
- 客户信息 CRUD
- 销售线索跟进提醒

P1:
- 销售数据报表
- 团队协作

## 4. 非功能需求
- 并发：支持 500 用户
- 性能：页面加载 < 2s
- 安全：数据加密存储
- 兼容性：支持企业微信、钉钉 OAuth

## 5. 技术约束
- 前端：React + Ant Design
- 后端：Node.js
- 部署：阿里云
- 时间：3 个月
```

### 输出：Requirement Inventory

```json
{
  "artifact_id": "req-inv-20260609-001",
  "artifact_type": "requirement_inventory",
  "completeness_assessment": {
    "overall_score": 0.92,
    "dimensions": {
      "business_goals_clarity": 1.0,
      "user_definition_clarity": 0.9,
      "functional_requirements_completeness": 0.8,
      "non_functional_requirements_completeness": 1.0,
      "constraints_clarity": 1.0
    }
  },
  "functional_requirements": [
    {
      "req_id": "FR-001",
      "description": "客户信息 CRUD",
      "priority": "P0",
      "source": "PRD 3.0"
    },
    {
      "req_id": "FR-002",
      "description": "销售线索跟进提醒",
      "priority": "P0",
      "source": "PRD 3.0"
    }
  ],
  "ambiguities": [
    {
      "ambiguity_id": "AMB-001",
      "description": "PRD 未明确'销售线索'的字段定义",
      "affected_areas": ["data_model", "form_design"],
      "clarification_needed": "线索包含哪些字段？必填/选填？",
      "default_interpretation": "假设包含：客户名称、联系方式、意向产品、跟进状态、下次跟进时间",
      "risk_if_wrong": "medium"
    }
  ],
  "conflicts": [],
  "gaps": [
    {
      "gap_id": "GAP-001",
      "category": "missing_detail",
      "description": "PRD 未定义'销售数据报表'的具体维度",
      "impact": "medium",
      "affected_fields": ["dashboard_design"],
      "mitigation": "假设包含：销售额、客户数、转化率、团队排名"
    }
  ],
  "assumptions": [
    {
      "assumption_id": "ASM-001",
      "description": "假设用户主要在移动端使用（80% 流量）",
      "rationale": "销售主管经常外出拜访客户",
      "validation_method": "需要真实使用数据验证",
      "risk_if_wrong": "high"
    }
  ],
  "readiness_decision": {
    "decision": "proceed",
    "rationale": "输入质量高（0.92），仅有少量细节缺失，可用行业惯例补充。建议在 design-analysis 阶段详细定义数据模型。",
    "blockers": [],
    "mitigation_strategy": "将所有推断内容标注 [inferred]，在 professional_gap_report 中说明需人工确认的部分"
  }
}
```

---

## 版本历史

- **v1.0.0** (2026-06-09): 初始版本
