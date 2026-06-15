# [SYNTHETIC] S2-H7B Replay Case

**状态**: SYNTHETIC / SANITIZED
**用途**: 复现 S2-H7B dry-run 中发现的机制问题
**外部 workspace**: `<DESIGNOS_WORKSPACE_ROOT>/runs/RUN-20260615-*`

---

## 1. 用例概述

本 replay case 用于复现 S2-H7B offline dry-run 中发现的 3 类 synthetic 问题：
1. 输入缺口问题（input gate: ready_with_assumptions）
2. 过程降级问题（checkpoint: degrade_scope）
3. 跨 skill 一致性问题（consistency: needs_reconciliation）

不含真实业务数据、真实 PRD、真实截图、真实 URL、真实客户信息。

---

## 2. Replay Scenario 1: Input Gap

**触发机制**: Input Quality Gate
**预期决策**: `ready_with_assumptions` 或 `needs_user_clarification`

### 输入材料

使用 `fixtures/synthetic/s2-h7b-dry-run/synthetic-prd.md`

### 故意缺口

PRD 缺少明确的成功指标（如 DAU、留存率、NPS）。

### 预期 Gate 行为

- Input gate 应识别缺口
- 触发 `ready_with_assumptions`
- 记录 assumption: "假设成功指标为 DAU > 1000"
- 记录 gap: category=input_gap, severity=medium

### 复现步骤

1. 读取 `synthetic-prd.md`
2. 运行 ai-analytics 或 prd2proto input quality gate
3. 检查 `input-quality.json` 中的 decision / assumptions / gaps

### 期望结果

```json
{
  "decision": "ready_with_assumptions",
  "assumptions": ["假设成功指标为 DAU > 1000"],
  "gaps": [
    {
      "category": "input_gap",
      "description": "PRD 缺少明确成功指标",
      "severity": "medium"
    }
  ]
}
```

---

## 3. Replay Scenario 2: Progressive Degradation

**触发机制**: Progressive Checkpoint
**预期决策**: `degrade_scope` 或 `continue_with_gaps`

### 输入材料

使用 `fixtures/synthetic/s2-h7b-dry-run/synthetic-screenshot-notes.md`

### 故意缺口

Screenshot notes 缺少：
- 空状态（无任务时的引导界面）
- 错误状态（网络失败时的提示）
- 加载状态（数据拉取中的 loading 样式）

### 预期 Checkpoint 行为

- Input gate 应触发 `needs_user_clarification`
- CP2 应触发 `degrade_scope`
- 记录 gap: "缺少关键页面状态描述"

### 复现步骤

1. 读取 `synthetic-screenshot-notes.md`
2. 运行 uxeval input quality gate + progressive checkpoint
3. 检查 `progressive-checkpoints.json` 中 CP2 的 decision

### 期望结果

```json
{
  "checkpoint_id": "CP2",
  "decision": "degrade_scope",
  "gaps": [
    {
      "category": "input_gap",
      "description": "缺少空状态/错误状态/加载状态",
      "severity": "high"
    }
  ]
}
```

---

## 4. Replay Scenario 3: Cross-Skill Consistency Conflict

**触发机制**: Cross-Skill Consistency Contract
**预期决策**: `needs_reconciliation`

### 输入材料

- `fixtures/synthetic/s2-h7b-dry-run/synthetic-product-brief.md` (说"5-20 人")
- `fixtures/synthetic/s2-h7b-dry-run/synthetic-prd.md` (说"10-50 人")

### 故意冲突

Target audience 描述不一致。

### 预期 Consistency Gate 行为

- ai-analytics 应识别潜在冲突
- prd2proto 应识别实际冲突
- 触发 `needs_reconciliation`
- 记录 conflict: dimension=target_audience, severity=minor

### 复现步骤

1. 先运行 ai-analytics（读取 product brief）
2. 再运行 prd2proto（读取 PRD）
3. 检查 `cross-skill-consistency.json` 中的 decision / conflicts

### 期望结果

```json
{
  "decision": "needs_reconciliation",
  "conflicts": [
    {
      "dimension": "target_audience",
      "detail": "product brief 说 5-20 人，PRD 说 10-50 人",
      "severity": "minor",
      "recommendation": "reconcile_before_next_skill"
    }
  ]
}
```

---

## 5. 不包含

- 真实项目材料
- 真实业务文案
- 真实客户信息
- 真实 URL / email / token
- 真实本地路径
- 敏感数据

---

## 6. 使用方式

本 replay case 可用于：
- 验证 H5/H5.1/H6 机制修复后的行为
- 回归测试质量门逻辑
- 培训 / 演示质量门如何工作

不应用于：
- 生产环境真实 run
- 真实客户项目验证
