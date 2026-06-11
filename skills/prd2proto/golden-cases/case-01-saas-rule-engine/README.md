# Case 01: SaaS 规则引擎

**复杂度**: 高  
**重点能力**: 复杂业务流程 + 多角色权限 + 状态机 + 版本管理

---

## 场景描述

为 B 端运营团队提供"在线规则配置平台"：
- 运营专员配置数据治理规则（如"订单金额>10000元 → 自动审核"）
- 主管审批/驳回规则
- 规则上线后影响生产数据流

**典型用户角色**:
- 运营专员（创建/编辑规则草稿）
- 数据主管（审批/版本管理）
- 数据治理员（监控规则生效效果）

---

## 验证重点

| 能力维度 | 重点检查 |
|---------|---------|
| 业务流程建模（Stage 05） | 规则状态机：草稿/提交/审核中/已发布/已下线/版本回退 |
| 用户任务建模（Stage 04） | 隐藏任务：批量启用/规则版本对比/紧急下线 |
| 信息架构（Stage 07） | 按"规则状态" vs 按"业务模块"组织（按状态更优） |
| 状态矩阵（Stage 11） | 7态全覆盖 + 边界态（权限不足/规则冲突）|
| 可追溯性（Stage 16） | 决策链：业务目标→产品能力→规则配置体验 |

---

## 输入

- `inputs/prd.md`: PRD 文档（待补充）
- `inputs/scope.md`: 范围说明（可选）

---

## 预期输出（待 P1 补全）

scaffold 阶段仅说明各 stage 应产出什么：

| Stage | 文件 | 关键字段 |
|-------|------|---------|
| 01 | input-diagnosis.json | gaps（PRD缺失项）、readiness_decision |
| 02 | design-objectives.json | BG: 规则配置效率提升 / PG: 简化版本管理 / EG: 配置流程≤3步 |
| 04 | user-task-map.json | primary_tasks: 创建规则/审批规则；hidden_tasks: 批量启用 |
| 05 | business-flow.json | 状态机: 草稿→提交→审核→已发布；含异常: 审核驳回/紧急下线 |
| 07 | information-architecture.json | 按规则状态组织（待审核/已发布/已下线） |
| 11 | state-matrix.json | 规则编辑器: 7态 + AI 执行态（智能推荐配置） |
| 15 | prototype_code.json | constitution_compliance 全 compliant |
| 16 | traceability-map.json | 5 层追溯，coverage≥0.85 |
| 17 | professional-gap-report.json | overall_score≥85, level=senior |

---

## 状态

- ✅ scaffold 目录已建立
- 🔄 PRD 输入文档：占位，待 P1 补充真实场景
- 🔄 expected-outputs：占位，待 P1 跑真实 LLM 生成
