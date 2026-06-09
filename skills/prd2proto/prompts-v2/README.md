# prd2proto Prompts (v2) - Design Reasoning Driven

基于 P0 Senior Designer Work Paradigm Engine 重构的完整 prompts。

## Prompt 列表

### Phase 1: 输入诊断与目标分解
- `01-input-diagnosis.md` - 输入诊断与完整性评估
- `02-design-objectives.md` - 设计目标分解

### Phase 2: 用户与任务建模
- `03-product-archetype.md` - 产品原型定义
- `04-user-task-modeling.md` - 用户任务建模
- `05-business-flow-modeling.md` - 业务流程建模
- `06-user-journey-mapping.md` - 用户旅程地图

### Phase 3: 信息架构与页面设计
- `07-information-architecture.md` - 信息架构设计
- `08-page-flow.md` - 页面流程建模
- `09-page-structure.md` - 页面结构设计

### Phase 4: 组件与交互设计
- `10-component-strategy.md` - 组件策略
- `11-state-matrix.md` - 状态矩阵
- `12-interaction-rules.md` - 交互规则

### Phase 5: 受约束的代码生成
- `13-design-spec-generation.md` - 设计规范生成
- `14-token-extraction.md` - Design Tokens 提取
- `15-constrained-code-generation.md` - 受约束的代码生成

### Phase 6: 追溯性与质量评估
- `16-traceability-generation.md` - 可追溯性地图生成
- `17-professional-gap-assessment.md` - 专业差距评估

---

## Prompt 编写原则

1. **基于方法文档**：每个 prompt 必须严格遵循 `knowledge/design-work-paradigm/` 对应方法
2. **Schema 约束**：明确引用对应的 artifact schema
3. **质量门明确**：说明输出需要通过哪些质量门
4. **示例完整**：提供至少一个完整的输入输出示例
5. **失败模式**：说明常见错误和如何避免

## 版本历史

- **v2.0.0** (2026-06-09 P1.3): 基于 P0 重构的完整版
- **v1.0.0** (2026-05-15): 初始版本（已弃用）
