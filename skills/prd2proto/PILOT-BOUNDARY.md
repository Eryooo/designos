# prd2proto 试点边界说明（Pilot Boundary）

> **版本**：P0 Paradigm Engine (v0.2.0-p0-refactor)  
> **日期**：2026-06-09  
> **状态**：Pilot（设计推理驱动重构）  
> **适用**：内部试点 + 外部试用

本文件回答一个问题：**prd2proto 经过 P0 设计推理驱动重构后，能信到哪、不能信到哪。**

---

## 重大变更（P0 重构）

### 架构变更

```
❌ 旧架构（P1.1 及之前）：PRD → 直接生成原型代码
✅ 新架构（P0）：PRD → 设计推理资产 → 受约束的原型代码
```

**核心改变**：
- 新增 12 个设计推理资产（design objectives, user task map, journey map, IA, page flow, component strategy, state matrix, interaction rules, etc.）
- 所有代码生成都必须基于这些资产约束
- 新增质量门机制（schema gate, traceability gate, gap transparency gate）
- 新增 traceability_map 和 professional_gap_report

---

## 1. 已实现（P0 Baseline）

### ✅ 设计推理资产生成

| 资产 | 状态 | 说明 |
|------|------|------|
| requirement_inventory | Schema Complete | 输入诊断，完整性评估 |
| design_objectives | Schema Complete | 业务目标、用户目标、体验目标分解 |
| product_archetype | Schema Baseline | 产品类型、交互复杂度定义 |
| user_task_map | Schema Complete | 主要任务、次要任务、边缘任务 |
| business_flow | Schema Baseline | 业务流程（状态转换、权限流、异常流） |
| user_journey_map | Schema Complete | 用户旅程（阶段、触点、痛点） |
| information_architecture | Schema Complete | 站点地图、导航、路由表 |
| page_flow | Schema Baseline | 页面流程（入口、分支、完成点） |
| page_structure | Schema Baseline | 页面结构（布局、模块） |
| component_strategy | Schema Complete | 组件库、组件映射、使用规则 |
| state_matrix | Schema Complete | 页面状态、组件状态、业务状态 |
| interaction_rules | Schema Baseline | 交互规则（导航、表单、表格、反馈） |

**实现程度**：
- ✅ 所有 schemas 已定义并继承 artifact-base
- ✅ 所有 artifact 包含 confidence, gaps, inferred_fields, warnings, traceability
- ⚠️ LLM 生成这些资产的 prompt 为 P0 baseline（深度不足，P1 补充）
- ⚠️ 资产之间的自动关联检查为 scaffold（P1 实现）

### ✅ 质量门机制（Scaffold）

| 质量门 | 状态 | 说明 |
|--------|------|------|
| schema_gate | Scaffold | Schema 验证逻辑存在，但未完整实现所有约束 |
| traceability_gate | Scaffold | 检查页面是否可追溯到 user_task，但未检查字段级追溯 |
| gap_transparency_gate | Scaffold | 检查 critical gaps，但未强制 blocked |
| inference_limit_gate | Not Implemented | 推断内容占比检查，P1 实现 |
| code_constraint_gate | Scaffold | 检查生成的页面是否来自 IA，但未检查组件级约束 |

**实现程度**：
- ✅ 质量门结构已建立
- ⚠️ 大部分质量门为 warning 模式，不阻塞执行
- ❌ 字段级验证逻辑未实现
- ❌ 质量门失败时的 fallback 逻辑未实现

### ✅ 追溯性与质量报告（Baseline）

| 产物 | 状态 | 说明 |
|------|------|------|
| design_traceability_map | Schema Complete, Runtime Baseline | Schema 完整，但字段级追溯未实现 |
| professional_gap_report | Schema Complete, Runtime Baseline | Schema 完整，但 9 维度评分为规则 based |

**实现程度**：
- ✅ traceability_map 包含输入追溯、资产追溯、决策追溯
- ⚠️ 字段级追溯（field_level_trace）为 scaffold
- ✅ professional_gap_report 包含 9 维度评分、人工复核边界、production_readiness
- ⚠️ 评分逻辑为规则 based，非 ML 模型

---

## 2. 部分实现（需人工复核）

### ⚠️ 设计推理深度

**现状**：
- LLM 能生成结构正确的设计推理资产
- 推理深度依赖 PRD 质量和 LLM 能力
- 部分推理可能为"形式正确但内容浅薄"

**人工复核要点**：
1. design_objectives 是否与真实业务目标对齐
2. user_task_map 是否覆盖真实用户任务
3. business_flow 是否符合真实业务规则
4. state_matrix 是否覆盖所有边缘情况

**示例**：
```json
// ✅ 形式正确
{
  "user_goals": [
    {
      "goal_id": "UG-001",
      "user_role": "销售主管",
      "goal_description": "快速录入客户信息",
      "job_to_be_done": "在会议后 5 分钟内完成客户信息记录"
    }
  ]
}

// ⚠️ 但可能遗漏：
// - 销售主管的其他关键任务（跟进线索、查看报表）
// - 不同角色的任务差异（销售员 vs 销售主管）
```

### ⚠️ 业务流程建模

**现状**：
- 能识别基础业务状态（待审核、已通过、已拒绝）
- 可能遗漏复杂业务规则（权限、并发、事务）

**人工复核要点**：
1. 状态转换是否完整（包括异常流）
2. 权限规则是否准确
3. 并发场景处理
4. 事务一致性考虑

### ⚠️ 代码生成约束

**现状**：
- 能基于 information_architecture 生成页面
- 能基于 component_strategy 选择组件
- 但约束不够严格，可能出现"授权外页面"或"未映射组件"

**人工复核要点**：
1. 检查 `traceability_map.coverage_analysis.scope_creep_items`
2. 检查是否有 unauthorized_page
3. 检查是否有 unmapped_component

---

## 3. 未实现（已知限制）

### ❌ 质量门强制执行

**当前状态**：
- 质量门失败时仅生成 warning，不阻塞执行
- 用户可能收到"看起来完整但实际有问题"的产物

**解决方案（P1）**：
- 实现质量门的 blocked 和 fallback_safe 模式
- critical 违规必须阻塞
- 提供人工批准机制（--force 参数）

### ❌ 字段级追溯验证

**当前状态**：
- traceability_map.field_level_trace 为 scaffold
- 无法验证"每个生成字段都可追溯"

**解决方案（P1）**：
- 实现字段级追溯生成逻辑
- 实现追溯完整性验证

### ❌ 推断内容自动检测

**当前状态**：
- 依赖 LLM 主动标注 `inferred: true`
- 如果 LLM 遗漏标注，系统无法自动检测

**解决方案（P1）**：
- 实现推断内容自动识别（对比输入和输出）
- 强制 inferred_fields 完整性检查

### ❌ 生产级代码生成

**当前状态**：
- 生成的代码为"演示原型"
- 状态管理简化（无 Redux/Zustand）
- 错误处理基础（无完整错误边界）
- 无国际化、无主题切换、无单元测试

**不会在 P1 实现**：
- 这是 pilot 阶段的架构决策
- 生产级代码需要工程师重构

---

## 4. 测试覆盖（P0 锁住的契约）

### ✅ Schema 验证测试
- 所有 artifact schemas 语法正确
- 所有 schemas 继承 artifact-base
- JSON Schema validator 通过

### ✅ Pipeline 结构测试
- pipeline.yaml 语法正确
- 所有 stages 定义完整
- 依赖关系正确

### ⚠️ 质量门测试（部分）
- schema_gate 能检测缺失字段
- traceability_gate 能检测无追溯页面
- 但未测试所有边缘情况

### ❌ 端到端测试（未实现）
- 未测试完整的 PRD → 推理资产 → 代码流程
- 未测试质量门的 blocked 模式
- 未测试 fallback_safe 降级逻辑

---

## 5. 使用建议

### ✅ 适合场景

1. **快速原型验证**
   - PRD 已完成，需要快速验证交互流程
   - 可接受"需要人工复核"的产物

2. **设计推理学习**
   - 学习资深设计师如何分解设计目标
   - 学习如何建模用户任务和业务流程

3. **设计资产生成**
   - 需要结构化的设计推理资产（design objectives, user task map, etc.）
   - 可接受"需要人工补充细节"

### ❌ 不适合场景

1. **直接用于生产**
   - 生成的代码为演示原型，不是生产代码
   - 需要工程师重构

2. **复杂业务系统**
   - 业务流程建模依赖 PRD 质量
   - 复杂业务规则可能遗漏

3. **完全自动化**
   - 所有设计推理资产需要人工复核
   - 业务流程、状态转换需要业务专家验证

---

## 6. 人工复核清单

使用 prd2proto 后，**必须**完成以下人工复核：

### Phase 1: 设计推理资产复核

- [ ] design_objectives 是否与业务目标对齐？
- [ ] user_task_map 是否覆盖所有关键任务？
- [ ] business_flow 是否符合真实业务规则？
- [ ] information_architecture 是否合理？
- [ ] state_matrix 是否覆盖边缘情况？

### Phase 2: 代码复核

- [ ] 生成的页面是否都来自 IA？
- [ ] 生成的组件是否都来自 component_strategy？
- [ ] 状态管理是否正确？
- [ ] 错误处理是否完整？
- [ ] 代码可维护性如何？

### Phase 3: 质量报告复核

- [ ] 检查 professional_gap_report
- [ ] 检查 traceability_map.coverage_analysis
- [ ] 检查所有 warnings 和 gaps
- [ ] 确认 production_readiness.blockers

---

## 7. 与 P1.1 的对比

| 维度 | P1.1 (旧) | P0 (新) | 改进 |
|------|-----------|---------|------|
| **架构** | PRD → 代码 | PRD → 推理资产 → 代码 | ✅ 可追溯、可审查 |
| **质量门** | 无 | Scaffold | ✅ 基础质量保障 |
| **追溯性** | 无 | Baseline | ✅ 决策可追溯 |
| **差距报告** | 无 | Baseline | ✅ 明确人工复核边界 |
| **代码约束** | LLM 自由发挥 | 基于资产约束 | ✅ 减少幻觉 |

---

## 8. 后续计划

### P1（下一步）
- 完整实现所有质量门
- 实现 blocked 和 fallback_safe 模式
- 字段级追溯验证
- 推断内容自动检测
- 端到端测试

### P2（未来）
- ML-based professional_gap_report 评分
- 真实 Figma/MasterGo MCP 集成
- 生成代码的单元测试
- 国际化和主题支持

---

## 9. 常见问题

### Q: P0 重构后，代码生成质量是否提升？
A: **部分提升**。代码现在基于设计推理资产生成，减少了"无依据的幻觉"，但仍需人工复核。

### Q: 质量门为什么只是 scaffold？
A: P0 重点是建立架构和 schema，质量门的完整实现需要更多工程时间，计划在 P1 完成。

### Q: 能否跳过设计推理资产直接生成代码？
A: **不能**。这违反了核心原则 1（禁止从输入直接跳到输出）。如果需要快速原型，建议使用 P1.1 旧版本（但无质量保障）。

### Q: 设计推理资产的质量如何保证？
A: **人工复核**。当前 pilot 阶段，所有设计推理资产都需要人工复核。P1 会实现更严格的质量门。

---

## 10. 联系与反馈

如遇到问题或有改进建议，请：
- 提交 Issue: https://github.com/Eryooo/designos/issues
- 查看文档: [knowledge/design-work-paradigm](../../knowledge/design-work-paradigm/)
- 查看 Skill Status: [skills/status.matrix.yaml](../status.matrix.yaml)
