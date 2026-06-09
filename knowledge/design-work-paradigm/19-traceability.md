# 19. 可追溯性机制 (Traceability)

## 定义与目的

可追溯性（Traceability）是将最终设计产物的每个元素追溯到其来源（输入、推理资产、设计决策）的能力。资深设计师的核心特征是**所有决策都有依据**，而不是"凭感觉"或"黑盒输出"。

**核心目标**：
1. 回答"为什么这样设计？"
2. 验证"输出是否与输入一致？"
3. 定位"哪个环节出错了？"
4. 证明"哪些是数据支撑，哪些是推断？"

**业务价值**：
- ✅ 用户可以理解设计理由
- ✅ 需求变更时可以快速评估影响
- ✅ 发现错误时可以精准定位
- ✅ 人工复核时可以聚焦高风险部分
- ✅ 多个 skill 可以复用同一套推理资产

---

## 追溯性的 5 个层次

### Level 1: 输入追溯 (Input Trace)

**目标**：证明最终产物使用了哪些输入材料

**必需信息**：
- 主要输入列表（PRD, 截图, 设计简报）
- 次要输入列表（user_persona, design_strategy）
- 每个输入的使用方式和覆盖率
- 未使用的输入（及原因）

**Schema 结构**：
```json
{
  "input_trace": {
    "primary_inputs": [
      {
        "input_id": "prd-v1.2.pdf",
        "input_type": "prd",
        "file_path": "/path/to/prd.pdf",
        "usage": "提取业务目标、功能需求、用户定义",
        "coverage": 0.85,
        "sections_used": [
          "2. 商业目标",
          "3. 用户画像",
          "4. 核心功能"
        ],
        "sections_unused": [
          "6. 技术架构（超出设计范围）"
        ]
      }
    ],
    "secondary_inputs": [
      {
        "input_id": "user-persona-001",
        "input_type": "existing_artifact",
        "purpose": "补充用户行为模式"
      }
    ],
    "unused_inputs": [
      {
        "input_id": "competitor-analysis.pdf",
        "reason_not_used": "PRD 已包含竞品对比，无需重复分析"
      }
    ]
  }
}
```

**质量标准**：
- ✅ `coverage` >= 0.7（70% 输入被使用）
- ✅ `unused_inputs` 都有 `reason_not_used`
- ❌ 如果 `coverage` < 0.5，说明输入利用率低，可能是：
  - 输入质量差（无法提取有效信息）
  - 输入与任务不匹配
  - 系统处理能力不足

---

### Level 2: 推理资产追溯 (Reasoning Asset Trace)

**目标**：证明最终产物基于哪些中间推理资产生成

**必需信息**：
- 使用的所有推理资产列表
- 每个资产对最终产物的贡献
- 资产之间的依赖关系（DAG）

**Schema 结构**：
```json
{
  "reasoning_asset_trace": {
    "assets_used": [
      {
        "asset_id": "design-obj-001",
        "asset_type": "design_objectives",
        "usage_description": "约束页面优先级和功能范围",
        "output_elements_derived": [
          {
            "output_element": "information_architecture.pages[0-5]",
            "asset_field": "user_goals.priority",
            "transformation": "P0 user_goals 映射为 P0 pages"
          }
        ]
      },
      {
        "asset_id": "user-task-map-001",
        "asset_type": "user_task_map",
        "usage_description": "决定页面数量和导航结构",
        "output_elements_derived": [
          {
            "output_element": "information_architecture.sitemap",
            "asset_field": "primary_tasks",
            "transformation": "每个 primary_task 至少对应 1 个页面"
          }
        ]
      }
    ],
    "asset_dependency_graph": {
      "design-obj-001": [],
      "user-task-map-001": ["design-obj-001"],
      "journey-map-001": ["user-task-map-001"],
      "ia-001": ["user-task-map-001", "journey-map-001"]
    }
  }
}
```

**质量标准**：
- ✅ 所有生成类 stage 都有 `reasoning_asset_trace`
- ✅ `asset_dependency_graph` 是 DAG（无循环依赖）
- ✅ 最终产物至少使用 3 个推理资产（objectives, tasks, journey/IA）

---

### Level 3: 决策追溯 (Decision Trace)

**目标**：证明每个关键设计决策的依据和备选方案

**关键决策类型**：
1. **Architecture**：整体架构选择（SPA vs MPA, CSR vs SSR）
2. **Navigation**：导航模式（侧边栏 vs 顶栏 vs Tab）
3. **Interaction Pattern**：交互模式（Modal vs Drawer, Table vs Card）
4. **Component Choice**：组件选择（Ant Design vs Material UI）
5. **State Management**：状态管理（Redux vs Context vs Zustand）
6. **Data Model**：数据建模（关系型 vs 文档型）

**Schema 结构**：
```json
{
  "decision_trace": [
    {
      "decision_id": "DEC-001",
      "decision_type": "navigation",
      "decision_point": "选择侧边栏导航而非顶部导航",
      "rationale": "基于用户任务复杂度（8 个一级菜单，3 层嵌套），侧边栏可展示更多信息且支持折叠",
      "based_on": [
        {
          "source_type": "reasoning_asset",
          "source_id": "user-task-map-001",
          "source_field": "primary_tasks.length"
        },
        {
          "source_type": "reasoning_asset",
          "source_id": "ia-001",
          "source_field": "sitemap.hierarchy.depth"
        },
        {
          "source_type": "best_practice",
          "source_id": "Nielsen Heuristic #6",
          "source_field": "Recognition rather than recall"
        }
      ],
      "alternatives_considered": [
        {
          "alternative": "顶部导航 + 下拉菜单",
          "pros": [
            "节省垂直空间",
            "符合移动端习惯",
            "视觉更简洁"
          ],
          "cons": [
            "无法同时展示 3 层嵌套",
            "切换效率低（需要点击 2 次）",
            "鼠标移动距离长"
          ],
          "why_rejected": "用户任务复杂度高，需要频繁在多个模块间切换，顶部导航效率不足"
        },
        {
          "alternative": "Tab 导航",
          "pros": [
            "视觉清晰",
            "适合平级模块"
          ],
          "cons": [
            "无法处理 3 层嵌套",
            "Tab 过多时视觉拥挤"
          ],
          "why_rejected": "不支持层级结构"
        }
      ],
      "confidence": 0.9,
      "impact": "high",
      "reversibility": "medium",
      "validation_method": "用户测试验证导航效率"
    }
  ]
}
```

**质量标准**：
- ✅ 每个 `high` impact 决策都有至少 2 个 `alternatives_considered`
- ✅ 每个决策的 `based_on` 至少有 1 个 `reasoning_asset` 来源
- ✅ 所有 `best_practice` 来源都有明确引用（如 Nielsen Heuristic #6）
- ❌ 如果 `confidence` < 0.5，必须进入 `human_review_required`

**资深设计师标准**：
- Senior 设计师会说："我选择侧边栏导航，因为用户有 8 个主要任务，顶部导航无法同时展示。我考虑过 Tab 导航，但它不支持 3 层嵌套。"
- Junior 设计师会说："我觉得侧边栏好看。"

---

### Level 4: 字段级追溯 (Field-Level Trace)

**目标**：将最终产物的每个字段追溯到具体来源

**应用场景**：
- 用户问："为什么这个页面叫'数据看板'？"
- 系统答："来自 PRD 4.2 '销售数据报表'，经过 user_task_map PT-003 '查看销售数据' 映射而来。"

**Schema 结构**：
```json
{
  "field_level_trace": {
    "information_architecture.pages[0].page_name": {
      "field_path": "pages[0].page_name",
      "field_value": "客户管理",
      "sources": [
        {
          "source_type": "prd",
          "source_reference": "PRD 4.1: 客户信息 CRUD",
          "confidence": 1.0
        },
        {
          "source_type": "user_task_map",
          "source_reference": "PT-001: 快速录入和查询客户信息",
          "confidence": 1.0
        }
      ],
      "transformation": "PRD 功能名称 → User Task 名称 → Page 名称（直接映射）"
    },
    "information_architecture.pages[5].page_name": {
      "field_path": "pages[5].page_name",
      "field_value": "数据分析",
      "sources": [
        {
          "source_type": "inferred",
          "source_reference": "基于 PRD 4.3 '销售数据报表' 推断",
          "confidence": 0.7
        }
      ],
      "transformation": "PRD '报表' → 推断为独立的 '数据分析' 页面"
    }
  }
}
```

**质量标准**：
- ✅ 所有 `confidence` < 0.8 的字段都标注在 `inferred_fields`
- ✅ 所有 `inferred` 来源都在 `assumptions` 中说明
- ✅ 关键字段（页面名称、核心功能）的 `confidence` >= 0.9

---

### Level 5: 推断追溯 (Inference Trace)

**目标**：明确标注所有推断内容，并说明推断依据和风险

**必需信息**：
- 所有 `inferred: true` 的字段
- 推断的依据（基于什么假设）
- 推断的置信度
- 如果推断错误的影响

**Schema 结构**：
```json
{
  "inference_trace": {
    "inferred_fields": [
      {
        "field_path": "user_goals[1]",
        "inferred_value": {
          "goal_description": "自动提醒跟进线索",
          "pain_points": ["容易忘记", "无提醒机制"]
        },
        "inference_basis": "PRD 提到 '销售线索跟进'，但未明确用户痛点。基于 CRM 行业惯例，销售主管普遍需要自动提醒功能。",
        "confidence": 0.7,
        "risk_if_wrong": "medium",
        "validation_method": "用户访谈验证是否真的需要自动提醒",
        "fallback_plan": "如果用户不需要，可降级为手动设置跟进时间"
      }
    ],
    "total_inferred_percentage": 0.15,
    "high_risk_inferences": [
      {
        "field_path": "design_constraints.user[0]",
        "inference": "假设用户主要在移动端使用（80% 流量）",
        "risk": "如果用户实际在 PC 端使用，移动优先设计会导致 PC 体验差"
      }
    ]
  }
}
```

**质量标准**：
- ✅ `total_inferred_percentage` < 0.3（推断内容不超过 30%）
- ✅ 所有 `risk_if_wrong` = "high" 的推断都有 `validation_method`
- ✅ 所有 `high_risk_inferences` 都在 `professional_gap_report` 中标注

---

## 完整 Traceability Map 示例

**场景**：prd2proto 生成的某个页面

```json
{
  "artifact_type": "traceability_map",
  "output_artifact": {
    "artifact_id": "prototype-001",
    "artifact_type": "prototype",
    "output_files": [
      {
        "file_path": "src/pages/CustomerManagement.tsx",
        "file_type": "react_component"
      }
    ]
  },
  
  "input_trace": {
    "primary_inputs": [
      {
        "input_id": "crm-prd-v1.2.pdf",
        "input_type": "prd",
        "usage": "提取客户管理需求",
        "coverage": 0.85
      }
    ]
  },
  
  "reasoning_asset_trace": {
    "assets_used": [
      {
        "asset_id": "design-obj-001",
        "asset_type": "design_objectives",
        "output_elements_derived": [
          {
            "output_element": "CustomerManagement 页面优先级 P0",
            "asset_field": "business_goals[0].priority",
            "transformation": "BG-001 (P0) → 对应功能为 P0 → 页面为 P0"
          }
        ]
      },
      {
        "asset_id": "user-task-map-001",
        "asset_type": "user_task_map",
        "output_elements_derived": [
          {
            "output_element": "CustomerManagement 包含 CRUD 功能",
            "asset_field": "primary_tasks[0]",
            "transformation": "PT-001 '快速录入和查询客户' → 页面需要列表 + 表单"
          }
        ]
      },
      {
        "asset_id": "component-strategy-001",
        "asset_type": "component_strategy",
        "output_elements_derived": [
          {
            "output_element": "使用 Ant Design Table 组件",
            "asset_field": "component_mapping.table",
            "transformation": "列表展示 → 映射到 antd.Table"
          }
        ]
      }
    ]
  },
  
  "decision_trace": [
    {
      "decision_id": "DEC-010",
      "decision_type": "interaction_pattern",
      "decision_point": "使用 Modal 而非 Drawer 进行客户信息编辑",
      "rationale": "客户信息字段较少（6 个），Modal 足够；Drawer 占用屏幕空间大，不必要",
      "based_on": [
        {
          "source_type": "reasoning_asset",
          "source_id": "page-structure-001",
          "source_field": "pages[0].form_fields.length"
        }
      ],
      "alternatives_considered": [
        {
          "alternative": "Drawer",
          "pros": ["可展示更多字段"],
          "cons": ["占用空间大", "关闭需要额外操作"],
          "why_rejected": "字段少，Modal 足够"
        }
      ],
      "confidence": 0.85,
      "impact": "medium"
    }
  ],
  
  "field_level_trace": {
    "CustomerManagement.tsx:TableColumns": {
      "field_path": "Table columns definition",
      "sources": [
        {
          "source_type": "page_structure",
          "source_reference": "page-structure-001.content_model.customer_fields",
          "confidence": 1.0
        }
      ],
      "transformation": "content_model.customer_fields → Table columns"
    }
  },
  
  "inference_trace": {
    "inferred_fields": [
      {
        "field_path": "CustomerManagement.sortDefaultField",
        "inferred_value": "createdAt",
        "inference_basis": "PRD 未明确排序规则，假设默认按创建时间倒序（行业惯例）",
        "confidence": 0.8,
        "risk_if_wrong": "low"
      }
    ],
    "total_inferred_percentage": 0.12
  },
  
  "constraint_compliance": {
    "constraints_checked": [
      {
        "constraint_id": "CONS-001",
        "constraint_description": "必须使用 Ant Design 组件库",
        "compliance_status": "compliant",
        "evidence": "所有组件都来自 antd (Table, Modal, Form, Button)"
      }
    ]
  },
  
  "coverage_analysis": {
    "input_coverage": 0.85,
    "requirement_coverage": 0.90,
    "uncovered_requirements": [
      {
        "requirement": "FR-006: 批量导入客户",
        "reason_not_covered": "PRD 标记为 P1，当前仅实现 P0 功能",
        "planned_for": "Phase 2"
      }
    ],
    "scope_creep_items": []
  },
  
  "quality_gate_trace": {
    "gates_passed": [
      {
        "gate_id": "schema_gate",
        "gate_name": "Schema Validation",
        "pass_criteria": "输出符合 information_architecture.schema.json",
        "actual_result": "Pass"
      },
      {
        "gate_id": "traceability_gate",
        "gate_name": "Traceability Check",
        "pass_criteria": "所有页面可追溯到 user_task_map",
        "actual_result": "Pass"
      }
    ],
    "gates_failed": []
  }
}
```

---

## 追溯性验证清单

在生成 traceability_map 后，执行以下验证：

### Level 1: 输入追溯验证
- [ ] 所有输入文件都被记录
- [ ] `coverage` >= 0.7
- [ ] `unused_inputs` 都有 reason

### Level 2: 推理资产追溯验证
- [ ] 所有使用的推理资产都被记录
- [ ] `asset_dependency_graph` 无循环
- [ ] 最终产物至少使用 3 个推理资产

### Level 3: 决策追溯验证
- [ ] 所有 high impact 决策都有记录
- [ ] 每个决策都有 `based_on`
- [ ] 每个决策都有至少 1 个 alternative

### Level 4: 字段级追溯验证
- [ ] 关键字段都有追溯来源
- [ ] 所有 `inferred` 字段都标注

### Level 5: 推断追溯验证
- [ ] `total_inferred_percentage` < 0.3
- [ ] 所有 high risk 推断都有 validation method
- [ ] 所有推断都在 assumptions 中说明

---

## 常见反模式

### Anti-Pattern 1: "全部来自 PRD"
```json
// ❌ 错误
{
  "sources": [
    {"source_type": "prd", "confidence": 1.0}
  ]
}
```
**问题**：PRD 不可能直接指定每个设计细节，必然有推理过程。

**正确做法**：
```json
// ✅ 正确
{
  "sources": [
    {"source_type": "prd", "source_reference": "4.1: 客户信息 CRUD"},
    {"source_type": "user_task_map", "source_reference": "PT-001"},
    {"source_type": "component_strategy", "source_reference": "选择 Table 组件"}
  ]
}
```

---

### Anti-Pattern 2: "所有决策都基于最佳实践"
```json
// ❌ 错误
{
  "based_on": [
    {"source_type": "best_practice", "source_id": "行业惯例"}
  ]
}
```
**问题**："行业惯例"过于模糊，无法验证。

**正确做法**：
```json
// ✅ 正确
{
  "based_on": [
    {"source_type": "reasoning_asset", "source_id": "user-task-map-001"},
    {"source_type": "best_practice", "source_id": "Nielsen Heuristic #6: Recognition vs Recall"}
  ]
}
```

---

### Anti-Pattern 3: "无备选方案"
```json
// ❌ 错误
{
  "decision": "使用 Modal",
  "alternatives_considered": []
}
```
**问题**：资深设计师会考虑多种方案。

**正确做法**：
```json
// ✅ 正确
{
  "decision": "使用 Modal",
  "alternatives_considered": [
    {"alternative": "Drawer", "why_rejected": "字段少，不需要大空间"},
    {"alternative": "Inline Edit", "why_rejected": "需要展示更多字段"}
  ]
}
```

---

## 版本历史

- **v1.0.0** (2026-06-09): 初始版本，定义 5 层追溯模型
