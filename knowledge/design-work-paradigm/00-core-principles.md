# 00. 核心原则与约束

## 定义与目的

Senior Designer Work Paradigm Engine 的核心原则定义了所有设计推理流程必须遵循的基本规则，确保输出质量、可追溯性和人工复核边界。

这些原则不是建议，而是**强制约束**，违反核心原则的产物不得声称达到"资深设计师"标准。

## 7 大核心原则

### 原则 1: 禁止从输入直接跳到输出

**定义**：任何设计 skill 不得从 PRD/截图/简报等原始输入直接生成最终产物（原型代码、设计稿、评估报告）。

**要求**：
- ✅ 必须先生成中间设计推理资产（design objectives, user task map, journey map, etc.）
- ✅ 最终输出必须基于这些中间资产生成
- ❌ 禁止在一个 stage 同时完成"分析"和"生成"

**错误示例**（违反此原则）：
```yaml
# ❌ 错误：PRD 直接生成原型代码
stages:
  - id: generate-prototype
    inputs: [prd_file]
    outputs: [prototype_code]
```

**正确示例**：
```yaml
# ✅ 正确：PRD → 设计推理资产 → 受约束的原型代码
stages:
  - id: design-objectives
    inputs: [prd_file]
    outputs: [design_objectives]
  
  - id: user-task-map
    inputs: [design_objectives]
    outputs: [user_task_map]
  
  - id: information-architecture
    inputs: [user_task_map]
    outputs: [information_architecture]
  
  - id: constrained-prototype
    inputs: [information_architecture, user_task_map, design_objectives]
    outputs: [prototype_code]
```

**理由**：
- 资深设计师不会看完 PRD 就直接画图，而是先建立设计推理框架
- 中间资产是可审查、可修正的
- 如果最终输出有问题，可以追溯到哪个推理资产出错

---

### 原则 2: 过程资产必须可审查

**定义**：所有中间设计推理资产必须以结构化、可验证的格式输出，不得隐藏在"思考过程"中。

**要求**：
- ✅ 每个推理资产必须有对应的 artifact schema
- ✅ 输出必须是独立文件（JSON/YAML/Markdown），不得仅存在于 LLM 内部状态
- ✅ 资产必须包含元数据（confidence, gaps, assumptions, inferred_fields）
- ❌ 禁止将推理过程作为"注释"或"日志"隐藏

**正确格式**：
```json
{
  "artifact_id": "design-obj-20260609-001",
  "artifact_type": "design_objectives",
  "confidence": 0.85,
  "business_goals": [...],
  "user_goals": [...],
  "gaps": [
    {
      "gap_id": "GAP-001",
      "description": "PRD 未明确目标用户年龄段",
      "impact": "high",
      "mitigation": "假设为 25-40 岁职场人士，基于产品定位推断"
    }
  ],
  "inferred_fields": ["user_goals[1].pain_points"],
  "traceability": {
    "upstream_artifacts": [],
    "decision_trace": [...]
  }
}
```

**理由**：
- 人工复核需要看到推理过程
- 发现错误时可以只修正有问题的资产，不用重跑整个流程
- 多个 skill 可以复用同一套推理资产（如 ai-analytics 的 user_persona 可被 prd2proto 使用）

---

### 原则 3: 推断内容必须显式标注

**定义**：所有非直接来自输入的内容，必须在 `inferred_fields` 数组中列出，并在字段级别标注 `"inferred": true`。

**要求**：
- ✅ 每个 artifact 必须有 `inferred_fields` 数组
- ✅ 推断字段必须在 `assumptions` 中说明推断依据
- ✅ 高风险推断必须进入 `warnings`
- ❌ 禁止隐藏推断，让用户误以为所有内容都来自输入

**示例**：
```json
{
  "user_goals": [
    {
      "goal_id": "UG-001",
      "description": "快速录入客户信息",
      "pain_points": ["Excel 容易丢失", "团队无法实时查看"],
      "inferred": false,
      "traceable_to_prd": "PRD 3.2: 用户访谈记录"
    },
    {
      "goal_id": "UG-002",
      "description": "自动提醒跟进线索",
      "pain_points": ["容易忘记", "无提醒机制"],
      "inferred": true,
      "traceable_to_prd": "[inferred from UG-001 and industry best practice]"
    }
  ],
  "inferred_fields": ["user_goals[1]", "user_goals[1].pain_points"],
  "assumptions": [
    {
      "assumption_id": "ASM-001",
      "description": "假设销售主管需要自动提醒功能",
      "rationale": "基于 CRM 行业惯例，销售线索跟进通常需要自动提醒",
      "risk_if_wrong": "medium"
    }
  ]
}
```

**理由**：
- 用户需要知道哪些内容是"猜的"
- 人工复核时优先检查推断内容
- 降低"AI 幻觉"风险

---

### 原则 4: 输入缺失不得静默补全

**定义**：当输入缺失、模糊或不足时，不得静默补全，必须进入 `gaps` 数组并标注影响。

**要求**：
- ✅ 每个 artifact 必须有 `gaps` 数组
- ✅ 每个 gap 必须标注 `impact` (critical/high/medium/low)
- ✅ critical 和 high impact gaps 必须进入 `warnings`
- ✅ 如果 gap 导致无法生成合格产物，必须阻塞执行或降级到 `fallback_safe` 模式
- ❌ 禁止用"行业惯例"静默填补 critical gaps

**示例**：
```json
{
  "gaps": [
    {
      "gap_id": "GAP-001",
      "category": "missing_input",
      "description": "PRD 未定义目标用户角色",
      "impact": "high",
      "affected_fields": ["user_goals", "user_task_map"],
      "mitigation": "基于产品定位推断为'中小企业销售主管'，但需人工确认"
    },
    {
      "gap_id": "GAP-002",
      "category": "ambiguous_requirement",
      "description": "PRD 中'提升效率'未量化",
      "impact": "medium",
      "affected_fields": ["business_goals[0].success_metric"],
      "mitigation": "假设为'单客户管理时间减少 30%'"
    }
  ],
  "warnings": [
    {
      "warning_id": "WARN-001",
      "severity": "high",
      "category": "assumption_risk",
      "message": "目标用户角色为推断，如果错误将影响所有下游设计决策",
      "recommendation": "建议补充用户研究或访谈数据"
    }
  ]
}
```

**理由**：
- 让用户知道"数据不够"，而不是给一个看起来完美但不可靠的结果
- 资深设计师会说"这个地方信息不足，我需要更多输入"，而不是瞎猜

---

### 原则 5: 决策必须可追溯

**定义**：所有关键设计决策必须记录在 `decision_trace` 中，说明决策依据、考虑的备选方案和选择理由。

**要求**：
- ✅ 每个 artifact 的 `traceability.decision_trace` 必须记录关键决策
- ✅ 每个决策必须标注 `based_on`（来自哪个上游资产或输入）
- ✅ 每个决策必须列出 `alternatives_considered`
- ❌ 禁止"黑盒决策"（用户不知道为什么这样设计）

**示例**：
```json
{
  "traceability": {
    "decision_trace": [
      {
        "decision_id": "DEC-001",
        "decision_type": "navigation",
        "decision_point": "选择侧边栏导航而非顶部导航",
        "rationale": "基于用户任务复杂度（8 个一级菜单，3 层嵌套），侧边栏可展示更多信息",
        "based_on": [
          {
            "source_type": "reasoning_asset",
            "source_id": "user-task-map-001",
            "source_field": "primary_tasks.length"
          },
          {
            "source_type": "reasoning_asset",
            "source_id": "information-architecture-001",
            "source_field": "sitemap.hierarchy.depth"
          }
        ],
        "alternatives_considered": [
          {
            "alternative": "顶部导航",
            "pros": ["节省垂直空间", "符合移动端习惯"],
            "cons": ["无法展示 3 层嵌套", "切换效率低"],
            "why_rejected": "用户任务复杂度高，需要频繁切换模块"
          }
        ],
        "confidence": 0.9,
        "impact": "high"
      }
    ]
  }
}
```

**理由**：
- 用户可以理解"为什么这样设计"
- 如果需求变化，可以重新评估决策
- 人工复核时可以判断决策是否合理

---

### 原则 6: 质量门不得被绕过

**定义**：每个 skill 必须定义质量门（schema gate, traceability gate, gap transparency gate 等），不符合质量标准的产物不得声称"完成"。

**要求**：
- ✅ 每个 stage 必须定义输出质量标准
- ✅ 质量门失败时，必须进入以下状态之一：
  - `blocked`: 无法继续，必须人工介入
  - `fallback_safe`: 降级到低保真模式
  - `review_required`: 可继续但必须人工复核
- ❌ 禁止"警告但继续"的质量门（warning 不阻塞）

**质量门类型**：

1. **Schema Gate**：输出必须符合 artifact schema
   ```python
   if not validate_schema(output, DesignObjectives):
       raise QualityGateViolation("Schema validation failed")
   ```

2. **Traceability Gate**：关键字段必须有追溯来源
   ```python
   for page in output.pages:
       if not page.traceable_to_task:
           raise QualityGateViolation(f"Page {page.id} not traceable to user task")
   ```

3. **Gap Transparency Gate**：critical gaps 必须阻塞或降级
   ```python
   critical_gaps = [g for g in output.gaps if g.impact == "critical"]
   if critical_gaps:
       return FallbackSafeMode(gaps=critical_gaps)
   ```

4. **Inference Limit Gate**：推断内容不得超过阈值
   ```python
   inferred_ratio = len(output.inferred_fields) / total_fields
   if inferred_ratio > 0.3:  # 30% 阈值
       raise QualityGateViolation("Too many inferred fields")
   ```

**理由**：
- 资深设计师不会交付不合格的产物
- 质量门是"最低标准"，不是"建议"

---

### 原则 7: 人工复核边界必须明确

**定义**：每个 skill 必须在 `professional_gap_report` 中明确说明哪些内容必须人工复核，哪些可以直接使用。

**要求**：
- ✅ 最终产物必须生成 `professional_gap_report`
- ✅ 报告必须包含 `human_review_requirements`
- ✅ 报告必须包含 `claims_validation`（可声称 vs 不可声称）
- ❌ 禁止声称"production-ready"但实际需要大量人工调整

**示例**：
```json
{
  "human_review_requirements": {
    "review_required": true,
    "review_priority": "high",
    "review_focus_areas": [
      "所有业务流程正确性（系统无法验证业务逻辑）",
      "状态转换完整性（可能遗漏边缘情况）",
      "品牌调性一致性（主观判断）"
    ],
    "recommended_reviewers": [
      {"role": "product_manager", "why": "验证业务流程"},
      {"role": "senior_designer", "why": "验证交互合理性"},
      {"role": "engineer", "why": "验证技术可行性"}
    ]
  },
  "claims_validation": {
    "can_claim": [
      "信息架构符合用户任务优先级",
      "组件选择符合 Ant Design 规范",
      "路由表完整且无冲突"
    ],
    "cannot_claim": [
      {
        "claim": "业务流程 100% 正确",
        "reason": "系统仅基于 PRD 推断，未验证真实业务规则",
        "required_to_claim": "业务专家评审 + 实际业务场景验证"
      },
      {
        "claim": "可直接用于生产环境",
        "reason": "状态管理为简化实现，缺少错误边界和异常处理",
        "required_to_claim": "工程师重构状态管理 + 补充错误处理"
      }
    ]
  }
}
```

**理由**：
- 诚实告知用户"哪些地方 AI 不可靠"
- 避免用户过度信任 AI 输出
- 明确"AI 辅助"与"AI 替代"的边界

---

## 违反核心原则的后果

| 违反原则 | 后果 | 示例 |
|---------|------|------|
| 原则 1: 直接跳到输出 | 产物不可追溯，错误无法定位 | prd2proto 直接生成代码，发现页面错误但不知道是哪个推理环节出错 |
| 原则 2: 推理资产不可审查 | 无法人工介入，错误累积 | 用户发现导航结构不合理，但无法修正中间的 IA 资产 |
| 原则 3: 推断未标注 | 用户误以为所有内容都来自输入 | user_persona 看起来很详细，但实际 80% 是 LLM 编的 |
| 原则 4: 静默补全缺失 | 产物看起来完美但不可靠 | PRD 没有用户画像，系统自动假设但不告知用户 |
| 原则 5: 决策不可追溯 | 无法理解设计理由 | 用户问"为什么用表格而非卡片"，系统无法回答 |
| 原则 6: 质量门被绕过 | 低质量产物被标记为"完成" | schema 验证失败但仍然输出，导致下游 stage 崩溃 |
| 原则 7: 人工复核边界不明 | 用户过度信任或完全不信任 | 声称"production-ready"但实际需要 2 周人工调整 |

---

## 与其他方法的关系

- **所有其他 18 个方法都必须遵循这 7 大核心原则**
- 原则 1-2 确保**推理过程可见**
- 原则 3-4 确保**风险透明**
- 原则 5 确保**决策可理解**
- 原则 6-7 确保**质量可控**

---

## 实施检查清单

在开发新 skill 或重构现有 skill 时，使用此检查清单：

- [ ] 是否有清晰的设计推理资产 pipeline？（原则 1）
- [ ] 每个中间资产是否有 schema 和独立输出文件？（原则 2）
- [ ] 是否所有推断字段都标注了 `inferred: true`？（原则 3）
- [ ] 是否所有输入缺失都进入了 `gaps` 数组？（原则 4）
- [ ] 是否关键决策都记录在 `decision_trace`？（原则 5）
- [ ] 是否定义了质量门且不可绕过？（原则 6）
- [ ] 是否生成了 `professional_gap_report` 并明确人工复核边界？（原则 7）

---

## 版本历史

- **v1.0.0** (2026-06-09): 初始版本，定义 7 大核心原则
