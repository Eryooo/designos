# Senior Designer Work Paradigm Engine

## 概述

本模块是 DesignOS 的核心设计推理底座，将资深设计师的专业工作范式、判断模型、过程资产、质量门、追溯机制工程化。

**核心原则**：
1. ❌ 禁止从原始输入直接跳到最终输出
2. ✅ 必须先生成可审查的专业过程资产
3. ✅ 最终输出必须被过程资产约束，而不是由 LLM 自由发挥
4. ✅ 所有关键设计决策必须可追溯到上游过程资产
5. ✅ 推断内容必须显式标注 `[inferred]`
6. ✅ 缺失输入不得静默补全，必须进入 gap / assumption / risk
7. ✅ 每个 skill 必须有质量门、失败模式、自评报告和人工复核边界

## 目标用户

- **AI Skills 开发者**：了解如何构建设计推理流程
- **DesignOS 贡献者**：扩展设计方法库
- **企业用户**：理解 DesignOS 的专业标准

## 设计方法库

本模块包含 19 个核心设计方法，覆盖从输入诊断到质量评估的完整流程：

### 基础方法（输入理解与目标分解）
- [00-core-principles.md](00-core-principles.md) - 核心原则与约束
- [01-input-diagnosis.md](01-input-diagnosis.md) - 输入诊断与完整性评估
- [02-objective-decomposition.md](02-objective-decomposition.md) - 设计目标分解

### 用户与任务建模
- [03-user-task-modeling.md](03-user-task-modeling.md) - 用户任务地图
- [04-scenario-modeling.md](04-scenario-modeling.md) - 场景建模
- [06-user-journey-mapping.md](06-user-journey-mapping.md) - 用户旅程地图

### 业务与信息建模
- [05-business-flow-modeling.md](05-business-flow-modeling.md) - 业务流程建模
- [07-information-architecture.md](07-information-architecture.md) - 信息架构设计

### 交互与界面设计
- [08-page-flow-modeling.md](08-page-flow-modeling.md) - 页面流程建模
- [09-content-structure.md](09-content-structure.md) - 内容结构设计
- [10-component-strategy.md](10-component-strategy.md) - 组件策略
- [11-state-matrix.md](11-state-matrix.md) - 状态矩阵
- [12-interaction-rules.md](12-interaction-rules.md) - 交互规则

### 视觉与品牌设计
- [13-visual-translation.md](13-visual-translation.md) - 视觉翻译
- [14-brand-strategy-modeling.md](14-brand-strategy-modeling.md) - 品牌策略建模
- [15-ip-character-modeling.md](15-ip-character-modeling.md) - IP 角色建模

### 评估与质量保证
- [16-evaluation-evidence-modeling.md](16-evaluation-evidence-modeling.md) - 评估证据建模
- [17-quality-rubrics.md](17-quality-rubrics.md) - 质量标准
- [18-failure-modes.md](18-failure-modes.md) - 失败模式库
- [19-traceability.md](19-traceability.md) - 可追溯性机制

## Schema 模板

`templates/` 目录包含所有设计推理资产的 JSON Schema 定义，与 `kernel/contracts/artifacts/` 保持同步。

## 使用方式

### 对于 Skill 开发者

1. **选择适用的设计方法**：根据 skill 类型选择相关方法
   - 生成类 skill (prd2proto)：使用 02-15 号方法
   - 评估类 skill (uxeval)：使用 01, 16, 17, 18 号方法
   - 研究类 skill (ai-analytics)：使用 01, 03, 04, 14 号方法

2. **构建推理流程**：将方法组合成 pipeline stages
   ```yaml
   stages:
     - id: input-diagnosis
       method: 01-input-diagnosis
       outputs: [requirement_inventory, gaps, assumptions]
     
     - id: objective-decomposition
       method: 02-objective-decomposition
       inputs: [requirement_inventory]
       outputs: [design_objectives]
   ```

3. **引用 Schema**：使用对应的 artifact schema 验证输出
   ```python
   from kernel.contracts.artifacts import DesignObjectives
   objectives = validate_schema(output, DesignObjectives)
   ```

4. **实现质量门**：根据 17-quality-rubrics 和 18-failure-modes 设置验证规则

### 对于企业用户

每个方法文档说明了：
- **输入要求**：需要提供什么材料
- **输出规范**：会得到什么产物
- **质量标准**：如何判断产物是否合格
- **人工复核边界**：哪些地方必须人工介入

## 与现有 skills 的关系

| Skill | 使用的设计方法 | 覆盖度 |
|-------|--------------|-------|
| **prd2proto** | 01, 02, 03, 05, 06, 07, 08, 09, 10, 11, 12 | 完整（P0 重点） |
| **uxeval** | 01, 06, 16, 17, 18 | 部分（P1 升级） |
| **ai-analytics** | 01, 02, 03, 04, 14 | 部分（P1 升级） |
| **ip-design** | 01, 15, 13, 17, 18 | 部分（P1 升级） |
| **brand-creative** | 01, 14, 13, 17, 18 | 部分（P1 升级） |

## 扩展指南

新增设计方法时，必须包含以下章节：

1. **定义与目的**（200-300 字）
2. **适用场景**（150-200 字）
3. **输入要求**（列表形式）
4. **输出规范**（引用对应 schema）
5. **推理过程**（分步说明，500-800 字）
6. **质量标准**（列表，10-15 条）
7. **失败模式**（列表，5-10 条）
8. **与其他方法的关系**（200 字）
9. **实例**（完整示例）

## 版本历史

- **v1.0.0** (2026-06-09): 初始版本，19 个核心方法
- 基于文档：
  - 《DesignOS Skills 问题汇总与审计分析文档》
  - 《DesignOS Skills 完整迭代说明文档｜Claude Code 执行版》

## 贡献

请参考 [CONTRIBUTING.md](../../CONTRIBUTING.md)

## 许可

Apache 2.0 - 详见 [LICENSE](../../LICENSE)
