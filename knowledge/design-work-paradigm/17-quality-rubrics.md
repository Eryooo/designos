# 17. 质量标准 (Quality Rubrics)

## 定义与目的

质量标准（Quality Rubrics）定义了设计产物的评估维度和分级标准，使用 9 维度模型对产物进行客观评分，生成 `professional_gap_report` 以明确产物与资深设计师标准的差距。

**核心目标**：
1. 客观评估设计产物质量
2. 识别距离 Senior 标准的差距
3. 明确人工复核边界
4. 指导质量改进

## 9 维度评估模型

### 维度 1: Strategic Alignment (战略对齐度)

**定义**：设计方案与业务目标、用户目标的对齐程度

**评分标准**：
- **10 (Expert)**：每个设计决策都可追溯到业务/用户目标，有明确的 ROI 预估
- **7-9 (Senior)**：核心设计决策与目标对齐，有清晰的价值主张
- **4-6 (Mid)**：大部分设计符合目标，但部分决策缺少理由
- **1-3 (Junior)**：设计与目标关联弱，存在"为了设计而设计"

**评估方法**：
```python
# 检查 design_objectives 和最终输出的映射关系
alignment_score = 0
for goal in design_objectives.business_goals:
    if goal.goal_id in output.goal_mapping:
        alignment_score += 1

alignment_ratio = alignment_score / len(design_objectives.business_goals)

if alignment_ratio >= 0.9:
    tier = "senior"
elif alignment_ratio >= 0.7:
    tier = "mid"
else:
    tier = "junior"
```

**Gap 示例**：
```json
{
  "dimension_name": "strategic_alignment",
  "score": 6,
  "tier": "mid",
  "gaps": [
    {
      "gap_description": "业务目标 BG-002 (提升 GMV) 无对应的设计策略",
      "severity": "high",
      "how_to_improve": "在用户旅程中明确标注促进转化的设计点（如简化结账流程、推荐相关商品）"
    }
  ]
}
```

---

### 维度 2: User Understanding (用户理解深度)

**定义**：对目标用户的特征、需求、行为模式的理解深度

**评分标准**：
- **10 (Expert)**：基于真实用户研究，有量化数据支撑
- **7-9 (Senior)**：用户画像清晰，任务地图完整，考虑边缘场景
- **4-6 (Mid)**：有基础用户画像，主要任务清晰，次要任务不完整
- **1-3 (Junior)**：用户定义模糊，任务建模不完整

**评估方法**：
- 检查 `user_task_map` 的完整性
- 检查 primary_tasks / secondary_tasks / edge_tasks 覆盖度
- 检查 pain_points 是否有证据支撑

**Gap 示例**：
```json
{
  "gaps": [
    {
      "gap_description": "用户画像基于 PRD 推断，无真实用户访谈数据",
      "severity": "medium",
      "how_to_improve": "补充 5-10 个目标用户访谈，验证假设的 pain_points"
    },
    {
      "gap_description": "edge_tasks 列表为空，未考虑异常场景",
      "severity": "medium",
      "how_to_improve": "补充错误处理、网络异常、权限异常等边缘任务"
    }
  ]
}
```

---

### 维度 3: Design Reasoning Depth (设计推理深度)

**定义**：设计推理资产的完整性和深度

**评分标准**：
- **10 (Expert)**：完整的推理链条，每个决策都有多个备选方案对比
- **7-9 (Senior)**：推理资产完整（objectives → tasks → journey → IA → flows），决策有理由
- **4-6 (Mid)**：部分推理资产缺失，决策理由简单
- **1-3 (Junior)**：直接从输入跳到输出，无中间推理

**评估方法**：
```python
required_assets = [
    "design_objectives",
    "user_task_map",
    "journey_map",
    "information_architecture",
    "page_flow"
]

existing_assets = get_artifacts_in_pipeline()
completeness = len(existing_assets) / len(required_assets)

if completeness >= 0.9:
    tier = "senior"
elif completeness >= 0.6:
    tier = "mid"
else:
    tier = "junior"
```

**Gap 示例**：
```json
{
  "gaps": [
    {
      "gap_description": "缺少 business_flow 资产，业务流程建模不完整",
      "severity": "high",
      "how_to_improve": "补充业务流程图，明确状态转换规则和异常流"
    }
  ]
}
```

---

### 维度 4: Technical Feasibility (技术可行性)

**定义**：设计方案的技术可实现性和工程成本评估

**评分标准**：
- **10 (Expert)**：考虑了所有技术约束，有性能优化策略，工程师无需返工
- **7-9 (Senior)**：技术方案可行，考虑了主要约束，工程实现成本可控
- **4-6 (Mid)**：基本可实现，但部分细节未考虑技术限制
- **1-3 (Junior)**：存在技术不可行的设计，或工程成本远超预期

**评估方法**：
- 检查是否有 `technical_constraints` 映射
- 检查组件选择是否在技术栈范围内
- 检查状态管理复杂度是否合理

**Gap 示例**：
```json
{
  "gaps": [
    {
      "gap_description": "状态矩阵中业务状态未考虑分布式事务一致性",
      "severity": "high",
      "how_to_improve": "补充状态同步机制设计，考虑网络异常时的状态回滚"
    }
  ]
}
```

---

### 维度 5: Visual Quality (视觉质量)

**定义**：视觉设计的专业度（仅适用于有视觉输出的 skill）

**评分标准**：
- **10 (Expert)**：品牌一致性、层级清晰、对比度合格、无障碍性完美
- **7-9 (Senior)**：视觉层级清晰，符合品牌调性，WCAG AA 级
- **4-6 (Mid)**：基础视觉规范符合，但细节粗糙
- **1-3 (Junior)**：视觉混乱，对比度不足，无品牌感

**评估方法**：
- 检查 color_system 是否有对比度验证
- 检查 typography_system 是否有层级定义
- 检查 visual_spec 是否与 brand_strategy 一致

---

### 维度 6: Interaction Sophistication (交互复杂度处理)

**定义**：处理复杂交互场景的能力

**评分标准**：
- **10 (Expert)**：覆盖所有交互场景（正常流、异常流、边缘情况），反馈及时明确
- **7-9 (Senior)**：核心交互场景完整，异常处理清晰，反馈合理
- **4-6 (Mid)**：基础交互覆盖，异常处理不完整
- **1-3 (Junior)**：仅考虑正常流，无错误处理

**评估方法**：
- 检查 `interaction_rules` 的完整性
- 检查 error_handling_rules 是否存在
- 检查 feedback_rules 是否及时明确

---

### 维度 7: Accessibility Compliance (无障碍合规性)

**定义**：符合 WCAG 2.1 标准的程度

**评分标准**：
- **10 (Expert)**：WCAG AAA 级，通过专业审计
- **7-9 (Senior)**：WCAG AA 级，关键流程无障碍
- **4-6 (Mid)**：部分符合 WCAG A 级
- **1-3 (Junior)**：无无障碍考虑

**评估方法**：
- 检查是否有 `accessibility_checklist`
- 检查是否有 keyboard navigation 规范
- 检查是否有 screen reader 支持说明

---

### 维度 8: Production Readiness (生产就绪度)

**定义**：产物距离可直接用于生产的距离

**评分标准**：
- **10 (Expert)**：可直接部署，无需调整
- **7-9 (Senior)**：需少量调整（< 10% 工作量）
- **4-6 (Mid)**：需中等调整（20-40% 工作量）
- **1-3 (Junior)**：需大量返工（> 50% 工作量）

**评估方法**：
```python
production_blockers = []

# 检查必需资产
if not has_traceability_map:
    production_blockers.append("缺少 traceability_map")

# 检查代码质量（如果有代码生成）
if code_generated:
    if lint_errors > 0:
        production_blockers.append("代码有 lint 错误")
    if no_error_handling:
        production_blockers.append("缺少错误处理")

readiness_score = max(0, 10 - len(production_blockers) * 2)
```

---

### 维度 9: Documentation Completeness (文档完整性)

**定义**：交付文档的完整性和可理解性

**评分标准**：
- **10 (Expert)**：文档完整，团队成员无需额外解释即可理解和执行
- **7-9 (Senior)**：核心文档齐全，关键决策有说明
- **4-6 (Mid)**：基础文档存在，但缺少细节
- **1-3 (Junior)**：文档缺失或不可理解

**评估方法**：
- 检查是否有 `design_spec.md`
- 检查是否有 `traceability_map.json`
- 检查是否有 `professional_gap_report.json`

---

## 整体评分计算

### 加权平均

```python
weights = {
    "strategic_alignment": 0.15,
    "user_understanding": 0.15,
    "design_reasoning_depth": 0.20,  # 最重要
    "technical_feasibility": 0.15,
    "visual_quality": 0.10,
    "interaction_sophistication": 0.10,
    "accessibility_compliance": 0.05,
    "production_readiness": 0.05,
    "documentation_completeness": 0.05
}

overall_score = sum(score * weight for score, weight in zip(dimension_scores, weights.values()))
```

### Tier 判断

```python
if overall_score >= 8.5:
    overall_tier = "expert"
elif overall_score >= 7.0:
    overall_tier = "senior"
elif overall_score >= 5.0:
    overall_tier = "mid"
else:
    overall_tier = "junior"
```

---

## Professional Gap Report 结构

```json
{
  "artifact_type": "professional_gap_report",
  "evaluated_artifact": {
    "artifact_id": "prototype-001",
    "artifact_type": "prototype"
  },
  "rubric_dimensions": [
    {
      "dimension_name": "strategic_alignment",
      "score": 7,
      "tier": "senior",
      "evidence": [
        "所有页面都可追溯到 user_task_map",
        "业务目标 BG-001, BG-002 有对应功能"
      ],
      "gaps": [
        {
          "gap_description": "业务目标 BG-003 (降低成本) 无设计策略",
          "severity": "medium",
          "how_to_improve": "补充自动化流程设计，减少人工操作"
        }
      ],
      "strengths": [
        "核心功能与业务目标对齐清晰"
      ]
    }
  ],
  "overall_assessment": {
    "overall_score": 7.2,
    "overall_tier": "senior",
    "summary": "设计推理完整，核心功能覆盖到位，但部分细节（错误处理、无障碍性）需补充。",
    "distance_to_senior": {
      "score_gap": 0,
      "key_blockers": [],
      "estimated_improvement_time": "已达到 Senior 水平"
    }
  },
  "human_review_requirements": {
    "review_required": true,
    "review_priority": "medium",
    "review_focus_areas": [
      "业务流程正确性（系统无法验证）",
      "品牌调性一致性（主观判断）"
    ],
    "recommended_reviewers": [
      {"role": "product_manager", "why": "验证业务流程"},
      {"role": "senior_designer", "why": "验证交互合理性"}
    ]
  },
  "production_readiness": {
    "ready_for_production": false,
    "blockers": [
      {
        "blocker": "状态管理为简化实现，缺少错误边界",
        "severity": "must_fix",
        "owner": "engineer"
      },
      {
        "blocker": "无国际化支持",
        "severity": "should_fix",
        "owner": "product_manager"
      }
    ],
    "risk_assessment": {
      "technical_risk": "medium",
      "business_risk": "low",
      "user_experience_risk": "low"
    }
  },
  "claims_validation": {
    "can_claim": [
      "信息架构符合用户任务优先级",
      "组件选择符合 Ant Design 规范"
    ],
    "cannot_claim": [
      {
        "claim": "可直接用于生产环境",
        "reason": "状态管理简化实现，缺少错误处理",
        "required_to_claim": "工程师重构状态管理"
      }
    ]
  }
}
```

---

## 质量标准

### Must Have
1. ✅ 所有 9 个维度都有评分
2. ✅ 每个维度都有 evidence（评分依据）
3. ✅ 每个维度的 gaps 都有 `how_to_improve`
4. ✅ `overall_assessment` 有明确的 summary
5. ✅ `human_review_requirements` 明确复核边界
6. ✅ `production_readiness` 列出所有 blockers
7. ✅ `claims_validation` 明确可声称 vs 不可声称

### Should Have
8. ✅ 低于 Senior 的维度都有改进建议
9. ✅ `production_readiness.blockers` 分配了 owner
10. ✅ `distance_to_senior` 有具体的改进时间估算

---

## 失败模式

1. ❌ 所有维度都是 10 分 → 过度乐观，需复核
2. ❌ 所有维度都是相同分数 → 评估不够细致
3. ❌ `overall_tier` 是 Senior 但 `production_readiness.ready_for_production` 是 false → 矛盾
4. ❌ Gaps 列表为空但分数 < 8 → 缺少改进建议
5. ❌ `can_claim` 列表为空 → 过度悲观
6. ❌ `human_review_requirements.review_required` 永远是 true → 不敢承担判断

---

## 版本历史

- **v1.0.0** (2026-06-09): 初始版本，定义 9 维度模型
