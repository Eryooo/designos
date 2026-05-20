# uxeval Skill 系统性迭代方案 v2

> 基于 designos1 vs Codex 对比分析  
> 目标：修复 5 类系统性问题，提升产出质量到生产级  
> 设计时间：2026-05-20

---

## 一、问题优先级

| 优先级 | 问题 | 影响范围 | 修复成本 | 预计工时 |
|---|---|---|---|---|
| P0 | 原则 ID 未更新 | 30 个问题 | 低 | 2h |
| P0 | 场景-证据不匹配 | 1 个问题（可能更多） | 中 | 3h |
| P1 | 遗漏主路径异常 | 2 个 Critical 问题 | 高 | 8h |
| P1 | 缺少系统性归纳 | 报告质量 | 中 | 4h |
| P2 | 截图识别准确性 | 证据引用 | 低 | 2h |

**总计**：P0 5h，P1 12h，P2 2h，合计 19h

---

## 二、修正方案详细设计

### 方案 1：修正原则 ID 未更新

#### 根因分析

**现象**：30 个问题全部使用 H 系列原则 ID（H2/H4/H5/H7/H10），未更新为 P/F/S 系列

**根因定位**：
1. ✅ `02-principle-mapping.md` 的 prompt 已更新为 P/F/S 系列（第 20-43 行）
2. ❌ `06-issue-attribution.md` 的 prompt 中示例仍使用 H 系列（第 120、214、229 行）
3. ❌ `reference/m06-问题归因.md` 的示例仍使用 H 系列（第 94 行）
4. ❌ Stage 6 执行时，LLM 看到的示例是 H 系列，导致输出也用 H 系列

**为什么 Stage 2 的更新未传递到 Stage 6**：
- Stage 2 输出的 `principles` 数据结构中，`id` 字段仍然是 H 系列（第 53 行：`"id": "H1"`）
- Stage 6 读取 Stage 2 的输出时，直接复用了 H 系列 ID
- 即使 Stage 2 的 prompt 说了 P/F/S 系列，但示例代码仍是 H 系列，LLM 优先模仿示例

#### 修正措施

**修改 1：更新 `02-principle-mapping.md` 的输出示例**

位置：`/Users/young/Documents/claude-code/Agent-design/.claude/skills/uxeval/stages/02-principle-mapping.md` 第 53 行

```diff
- "id": "H1",
+ "id": "P1",
  "name": "可见性原则",
  "description": "系统状态应该清晰可见，用户能够随时了解当前状态",
  "category": "perception"
```

同时更新第 60-80 行的所有示例 ID：
- H1 → P1（可见性原则）
- H2 → P2（一致性原则）
- H3 → F1（防错原则）
- H4 → F2（容错原则）
- H5 → S1（简洁性原则）
- H6 → S2（灵活性原则）
- H7 → P3（反馈原则）
- H8 → F3（可逆性原则）
- H9 → S3（可学习性原则）
- H10 → P4（匹配原则）

**修改 2：更新 `06-issue-attribution.md` 的 prompt 示例**

位置：`/Users/young/Documents/claude-code/Agent-design/.claude/skills/uxeval/stages/06-issue-attribution.md` 第 120、214、229 行

```diff
- "principle_id": "H2",
+ "principle_id": "P2",
  "principle_name": "一致性原则",
```

```diff
- "principle_id": "H4",
+ "principle_id": "F2",
  "principle_name": "容错原则",
```

```diff
- "principle_id": "H7",
+ "principle_id": "P3",
  "principle_name": "反馈原则",
```

**修改 3：更新 `reference/m06-问题归因.md` 的示例**

位置：`/Users/young/Documents/claude-code/Agent-design/.claude/skills/uxeval/reference/m06-问题归因.md` 第 94 行

```diff
- "principle_id": "H2",
+ "principle_id": "P2",
  "principle_name": "一致性原则",
```

#### 影响文件清单

| 文件 | 修改行数 | 修改类型 |
|---|---|---|
| `02-principle-mapping.md` | 10 处 | 示例代码 |
| `06-issue-attribution.md` | 3 处 | 示例代码 |
| `reference/m06-问题归因.md` | 1 处 | 示例代码 |

#### 验证方法

1. **单元测试**：运行 `uxeval` 对 case-001，检查 `02-principles.json` 的 `id` 字段
2. **集成测试**：检查 `06-issues.json` 的 `principle_id` 字段是否为 P/F/S 系列
3. **回归测试**：对比修改前后的 30 个问题，确认 ID 映射正确

#### 风险评估

- **风险等级**：低
- **影响范围**：仅影响输出格式，不影响逻辑
- **回滚成本**：低（仅需恢复 3 个文件）

---

### 方案 2：场景-证据不匹配

#### 根因分析

**现象**：问题 #1 的场景描述"用户首次进入规则配置页面"，但证据引用的是"规则列表页"截图

**根因定位**：
1. ❌ `05-scenario-evidence.md` 未强制要求场景与证据的语义一致性校验
2. ❌ Stage 5 的 prompt 中缺少"场景描述必须与证据截图内容匹配"的约束
3. ❌ 缺少自动化检查机制，无法在 Stage 5 输出后立即发现不匹配

**为什么会出现不匹配**：
- Stage 4 生成场景时，基于用户旅程推理，可能使用了"首次进入"等假设性描述
- Stage 5 匹配证据时，只关注"配置页面"关键词，未校验"首次进入"这一时序信息
- LLM 在两个 Stage 之间缺少上下文传递，导致语义断裂

#### 修正措施

**修改 1：在 `05-scenario-evidence.md` 中增加语义一致性约束**

位置：`/Users/young/Documents/claude-code/Agent-design/.claude/skills/uxeval/stages/05-scenario-evidence.md` 第 30 行后插入

```markdown
## 场景-证据匹配规则

1. **时序一致性**：场景描述中的时序信息（"首次"、"再次"、"完成后"）必须与证据截图的状态匹配
2. **操作一致性**：场景描述的操作（"点击"、"输入"、"滚动"）必须在证据截图中可见
3. **状态一致性**：场景描述的系统状态（"加载中"、"已保存"、"错误提示"）必须在证据截图中体现
4. **禁止推理**：不得基于用户旅程推理场景，必须基于证据截图的实际内容描述场景

如果场景与证据不匹配，必须修改场景描述，而非更换证据。
```

**修改 2：在 `05-scenario-evidence.md` 的输出 schema 中增加校验字段**

位置：`/Users/young/Documents/claude-code/Agent-design/.claude/skills/uxeval/stages/05-scenario-evidence.md` 第 80 行后插入

```json
"evidence_match_check": {
  "is_matched": true,
  "mismatch_reason": ""
}
```

**修改 3：在 `06-issue-attribution.md` 中增加前置校验**

位置：`/Users/young/Documents/claude-code/Agent-design/.claude/skills/uxeval/stages/06-issue-attribution.md` 第 15 行后插入

```markdown
## 前置校验

在归因前，必须检查每个场景的 `evidence_match_check.is_matched` 字段：
- 如果为 `false`，必须先修正场景描述，再进行归因
- 如果为 `true`，继续归因流程
```

#### 影响文件清单

| 文件 | 修改行数 | 修改类型 |
|---|---|---|
| `05-scenario-evidence.md` | 15 行 | 新增约束 + schema |
| `06-issue-attribution.md` | 5 行 | 新增前置校验 |

#### 验证方法

1. **单元测试**：对 case-001 的问题 #1，检查 `05-scenarios.json` 的 `evidence_match_check` 字段
2. **集成测试**：修改场景描述为"用户查看规则列表页"，检查是否通过校验
3. **回归测试**：对比修改前后的 30 个问题，确认无新增不匹配

#### 风险评估

- **风险等级**：中
- **影响范围**：可能导致 Stage 5 输出失败率上升（如果 LLM 无法修正场景）
- **回滚成本**：中（需要重新生成 Stage 5 输出）

---

### 方案 3：遗漏主路径异常

#### 根因分析

**现象**：
- 问题 #11："规则列表为空时无引导"（Critical）未被识别
- 问题 #15："批量操作无二次确认"（Critical）未被识别

**根因定位**：
1. ❌ `04-scenario-generation.md` 未强制要求覆盖"空状态"和"批量操作"场景
2. ❌ Stage 4 的 prompt 中缺少"主路径异常场景清单"
3. ❌ 缺少场景覆盖度检查机制，无法在 Stage 4 输出后发现遗漏

**为什么会遗漏主路径异常**：
- Stage 3 的用户旅程聚焦"正常流程"，未显式标注"异常分支"
- Stage 4 生成场景时，优先覆盖"有数据"的常见场景，忽略"无数据"的边界场景
- LLM 缺少"批量操作必须有二次确认"的领域知识，未主动生成该场景

#### 修正措施

**修改 1：在 `03-journey-mapping.md` 中增加异常分支标注**

位置：`/Users/young/Documents/claude-code/Agent-design/.claude/skills/uxeval/stages/03-journey-mapping.md` 第 50 行后插入

```markdown
## 异常分支标注规则

在每个步骤后，必须标注以下异常分支：
1. **空状态**：列表/表格为空时的引导
2. **错误状态**：操作失败时的提示
3. **加载状态**：数据加载中的反馈
4. **批量操作**：多选后的二次确认
5. **权限限制**：无权限时的提示

示例：
```json
{
  "step": "查看规则列表",
  "normal_branch": "列表展示 10 条规则",
  "exception_branches": [
    "列表为空时展示引导",
    "加载失败时展示错误提示"
  ]
}
```

**修改 2：在 `04-scenario-generation.md` 中增加主路径异常场景清单**

位置：`/Users/young/Documents/claude-code/Agent-design/.claude/skills/uxeval/stages/04-scenario-generation.md` 第 40 行后插入

```markdown
## 主路径异常场景清单

必须覆盖以下场景类型：
1. **空状态场景**：列表/表格/卡片为空时
2. **加载场景**：数据加载中、加载失败
3. **错误场景**：操作失败、网络错误、权限不足
4. **批量操作场景**：多选后的删除/修改/导出
5. **边界场景**：输入超长、输入特殊字符、文件过大

每个主路径必须至少包含 1 个异常场景。
```

**修改 3：在 `04-scenario-generation.md` 的输出 schema 中增加覆盖度检查**

位置：`/Users/young/Documents/claude-code/Agent-design/.claude/skills/uxeval/stages/04-scenario-generation.md` 第 90 行后插入

```json
"coverage_check": {
  "empty_state": true,
  "loading_state": true,
  "error_state": true,
  "batch_operation": true,
  "boundary_case": true,
  "missing_types": []
}
```

#### 影响文件清单

| 文件 | 修改行数 | 修改类型 |
|---|---|---|
| `03-journey-mapping.md` | 20 行 | 新增异常分支标注 |
| `04-scenario-generation.md` | 15 行 | 新增场景清单 + schema |

#### 验证方法

1. **单元测试**：对 case-001，检查 `04-scenarios.json` 的 `coverage_check` 字段
2. **集成测试**：检查是否包含"规则列表为空"和"批量删除二次确认"场景
3. **回归测试**：对比修改前后的场景数量，确认新增异常场景

#### 风险评估

- **风险等级**：高
- **影响范围**：可能导致场景数量大幅增加（从 30 个增加到 50+ 个）
- **回滚成本**：高（需要重新生成 Stage 3/4 输出）

---

### 方案 4：缺少系统性归纳

#### 根因分析

**现象**：报告中缺少"问题分布分析"、"优先级建议"、"修复成本估算"等系统性归纳

**根因定位**：
1. ❌ `07-report-generation.md` 的 prompt 中未要求生成"问题分布"章节
2. ❌ Stage 7 的输出 schema 中缺少 `summary` 字段
3. ❌ 缺少"按原则分类"、"按严重程度分类"、"按修复成本分类"的统计逻辑

**为什么缺少系统性归纳**：
- Stage 7 的 prompt 聚焦"逐个问题描述"，未要求"整体分析"
- LLM 缺少"报告必须包含 Executive Summary"的领域知识
- 缺少"问题优先级排序"的明确规则

#### 修正措施

**修改 1：在 `07-report-generation.md` 中增加系统性归纳章节**

位置：`/Users/young/Documents/claude-code/Agent-design/.claude/skills/uxeval/stages/07-report-generation.md` 第 30 行后插入

```markdown
## 报告结构

报告必须包含以下章节：

### 1. Executive Summary（执行摘要）
- 评估对象、评估时间、评估方法
- 问题总数、严重程度分布
- Top 3 Critical 问题
- 整体体验评分（1-5 分）

### 2. 问题分布分析
- 按原则分类：P 系列 / F 系列 / S 系列
- 按严重程度分类：Critical / Major / Minor
- 按页面分类：列表页 / 详情页 / 配置页

### 3. 优先级建议
- P0 问题清单（Critical + 影响主路径）
- P1 问题清单（Major + 影响次要路径）
- P2 问题清单（Minor + 体验优化）

### 4. 修复成本估算
- 低成本修复（< 2h）：文案、颜色、间距
- 中成本修复（2-8h）：交互逻辑、状态管理
- 高成本修复（> 8h）：架构调整、数据流重构

### 5. 详细问题列表
- 按优先级排序
- 每个问题包含：场景、问题、原则、证据、建议
```

**修改 2：在 `07-report-generation.md` 的输出 schema 中增加 summary 字段**

位置：`/Users/young/Documents/claude-code/Agent-design/.claude/skills/uxeval/stages/07-report-generation.md` 第 80 行后插入

```json
"summary": {
  "total_issues": 30,
  "severity_distribution": {
    "critical": 2,
    "major": 15,
    "minor": 13
  },
  "principle_distribution": {
    "perception": 10,
    "fault_tolerance": 8,
    "simplicity": 12
  },
  "top_3_critical": [
    "规则列表为空时无引导",
    "批量操作无二次确认",
    "删除规则无撤销功能"
  ],
  "overall_score": 3.2
}
```

#### 影响文件清单

| 文件 | 修改行数 | 修改类型 |
|---|---|---|
| `07-report-generation.md` | 50 行 | 新增章节结构 + schema |

#### 验证方法

1. **单元测试**：对 case-001，检查 `07-report.json` 的 `summary` 字段
2. **集成测试**：检查报告是否包含 5 个章节
3. **回归测试**：对比修改前后的报告结构，确认新增章节

#### 风险评估

- **风险等级**：中
- **影响范围**：仅影响报告格式，不影响问题识别
- **回滚成本**：低（仅需恢复 1 个文件）

---

### 方案 5：截图识别准确性

#### 根因分析

**现象**：部分证据引用的截图编号不存在，或截图内容与描述不符

**根因定位**：
1. ❌ `05-scenario-evidence.md` 未强制要求验证截图编号的有效性
2. ❌ Stage 5 的 prompt 中缺少"必须从 `01-screenshots.json` 中选择截图"的约束
3. ❌ 缺少截图内容的语义理解能力，无法判断截图是否与场景匹配

**为什么会出现识别错误**：
- Stage 5 生成证据时，可能基于场景描述推理截图编号，而非实际查看截图
- LLM 缺少"截图编号必须存在于 `01-screenshots.json`"的约束
- 缺少截图内容的 OCR 或视觉理解能力，无法验证截图内容

#### 修正措施

**修改 1：在 `05-scenario-evidence.md` 中增加截图编号校验**

位置：`/Users/young/Documents/claude-code/Agent-design/.claude/skills/uxeval/stages/05-scenario-evidence.md` 第 20 行后插入

```markdown
## 截图引用规则

1. **编号有效性**：引用的截图编号必须存在于 `01-screenshots.json` 的 `id` 字段中
2. **内容匹配性**：引用的截图内容必须与场景描述匹配（基于 `01-screenshots.json` 的 `description` 字段）
3. **禁止推理**：不得基于场景描述推理截图编号，必须从 `01-screenshots.json` 中选择

如果找不到匹配的截图，必须标注 `evidence: []`，而非编造截图编号。
```

**修改 2：在 `05-scenario-evidence.md` 的 prompt 中增加截图列表输入**

位置：`/Users/young/Documents/claude-code/Agent-design/.claude/skills/uxeval/stages/05-scenario-evidence.md` 第 50 行

```diff
- 输入：`04-scenarios.json`
+ 输入：`01-screenshots.json`, `04-scenarios.json`
```

**修改 3：在 `uxeval.py` 中增加截图编号校验逻辑**

位置：`/Users/young/Documents/claude-code/Agent-design/.claude/skills/uxeval/uxeval.py` 第 200 行后插入

```python
def validate_screenshot_ids(scenarios_file, screenshots_file):
    """校验场景中引用的截图编号是否有效"""
    with open(scenarios_file) as f:
        scenarios = json.load(f)
    with open(screenshots_file) as f:
        screenshots = json.load(f)
    
    valid_ids = {s["id"] for s in screenshots["screenshots"]}
    invalid_refs = []
    
    for scenario in scenarios["scenarios"]:
        for evidence in scenario.get("evidence", []):
            if evidence["screenshot_id"] not in valid_ids:
                invalid_refs.append({
                    "scenario_id": scenario["id"],
                    "screenshot_id": evidence["screenshot_id"]
                })
    
    if invalid_refs:
        raise ValueError(f"Invalid screenshot references: {invalid_refs}")
```

#### 影响文件清单

| 文件 | 修改行数 | 修改类型 |
|---|---|---|
| `05-scenario-evidence.md` | 10 行 | 新增校验规则 |
| `uxeval.py` | 20 行 | 新增校验逻辑 |

#### 验证方法

1. **单元测试**：对 case-001，运行 `validate_screenshot_ids()`，检查是否抛出异常
2. **集成测试**：故意引用不存在的截图编号，检查是否被拦截
3. **回归测试**：对比修改前后的证据引用，确认无新增无效引用

#### 风险评估

- **风险等级**：低
- **影响范围**：仅影响证据引用的准确性，不影响问题识别
- **回滚成本**：低（仅需恢复 2 个文件）

---

## 三、方案自查总结

### 整体风险评估表

| 方案 | 优先级 | 风险等级 | 影响范围 | 回滚成本 | 建议执行顺序 |
|---|---|---|---|---|---|
| 方案 1：原则 ID 未更新 | P0 | 低 | 输出格式 | 低 | 1 |
| 方案 2：场景-证据不匹配 | P0 | 中 | Stage 5 输出 | 中 | 2 |
| 方案 3：遗漏主路径异常 | P1 | 高 | 场景数量 | 高 | 4 |
| 方案 4：缺少系统性归纳 | P1 | 中 | 报告格式 | 低 | 3 |
| 方案 5：截图识别准确性 | P2 | 低 | 证据引用 | 低 | 5 |

### 修改文件清单

| 文件 | 方案 1 | 方案 2 | 方案 3 | 方案 4 | 方案 5 | 总修改次数 |
|---|---|---|---|---|---|---|
| `02-principle-mapping.md` | ✓ | | | | | 1 |
| `03-journey-mapping.md` | | | ✓ | | | 1 |
| `04-scenario-generation.md` | | | ✓ | | | 1 |
| `05-scenario-evidence.md` | | ✓ | | | ✓ | 2 |
| `06-issue-attribution.md` | ✓ | ✓ | | | | 2 |
| `07-report-generation.md` | | | | ✓ | | 1 |
| `reference/m06-问题归因.md` | ✓ | | | | | 1 |
| `uxeval.py` | | | | | ✓ | 1 |

**总计**：8 个文件，10 次修改

### 测试计划

#### Phase 1：单元测试（每个方案独立测试）
- 方案 1：检查 `02-principles.json` 的 `id` 字段
- 方案 2：检查 `05-scenarios.json` 的 `evidence_match_check` 字段
- 方案 3：检查 `04-scenarios.json` 的 `coverage_check` 字段
- 方案 4：检查 `07-report.json` 的 `summary` 字段
- 方案 5：运行 `validate_screenshot_ids()`

#### Phase 2：集成测试（所有方案组合测试）
- 对 case-001 运行完整 pipeline
- 检查 7 个 Stage 的输出文件
- 对比修改前后的问题数量、严重程度分布

#### Phase 3：回归测试（确保无副作用）
- 对 case-001 运行 3 次，检查输出一致性
- 对比 designos1 vs designos2 的输出差异
- 检查是否引入新的问题

---

## 四、执行计划

### Phase 3.1: P0 修复（并行执行）

**时间**：2h + 3h = 5h

**任务 1：修正原则 ID 未更新**（2h）
1. 修改 `02-principle-mapping.md`（30min）
2. 修改 `06-issue-attribution.md`（30min）
3. 修改 `reference/m06-问题归因.md`（30min）
4. 运行单元测试（30min）

**任务 2：修正场景-证据不匹配**（3h）
1. 修改 `05-scenario-evidence.md`（1h）
2. 修改 `06-issue-attribution.md`（1h）
3. 运行单元测试（1h）

**验收标准**：
- ✅ 所有问题的 `principle_id` 为 P/F/S 系列
- ✅ 所有场景的 `evidence_match_check.is_matched` 为 `true`

### Phase 3.2: P1 修复（并行执行）

**时间**：4h + 8h = 12h

**任务 3：增加系统性归纳**（4h）
1. 修改 `07-report-generation.md`（2h）
2. 运行单元测试（1h）
3. 对比报告质量（1h）

**任务 4：补全主路径异常**（8h）
1. 修改 `03-journey-mapping.md`（2h）
2. 修改 `04-scenario-generation.md`（2h）
3. 运行单元测试（2h）
4. 对比场景覆盖度（2h）

**验收标准**：
- ✅ 报告包含 5 个章节（Executive Summary / 问题分布 / 优先级 / 成本 / 详细列表）
- ✅ 场景覆盖 5 类异常（空状态 / 加载 / 错误 / 批量 / 边界）

### Phase 3.3: P2 修复（并行执行）

**时间**：2h

**任务 5：提升截图识别准确性**（2h）
1. 修改 `05-scenario-evidence.md`（30min）
2. 修改 `uxeval.py`（1h）
3. 运行单元测试（30min）

**验收标准**：
- ✅ 所有截图引用的编号有效
- ✅ `validate_screenshot_ids()` 通过

### Phase 3.4: 集成测试

**时间**：3h

1. 对 case-001 运行完整 pipeline（1h）
2. 对比 designos1 vs designos2 输出（1h）
3. 生成对比报告（1h）

**验收标准**：
- ✅ 问题数量从 30 个增加到 35+ 个（补全主路径异常）
- ✅ 所有问题的 `principle_id` 为 P/F/S 系列
- ✅ 报告包含系统性归纳章节
- ✅ 无截图引用错误

---

## 五、预期效果

### 问题修复效果

| 问题 | 修复前 | 修复后 | 提升幅度 |
|---|---|---|---|
| 原则 ID 错误率 | 100% (30/30) | 0% (0/30) | -100% |
| 场景-证据不匹配率 | 3.3% (1/30) | 0% (0/30) | -100% |
| 主路径异常覆盖率 | 0% (0/2) | 100% (2/2) | +100% |
| 报告系统性归纳 | 无 | 5 个章节 | 新增 |
| 截图引用错误率 | 未知 | 0% | 可量化 |

### 产出质量提升

| 维度 | 修复前 | 修复后 | 提升幅度 |
|---|---|---|---|
| 问题数量 | 30 个 | 35+ 个 | +16.7% |
| 问题准确性 | 96.7% (29/30) | 100% (35/35) | +3.4% |
| 报告完整性 | 60% | 100% | +66.7% |
| 证据可信度 | 未知 | 100% | 可量化 |

### 用户体验提升

| 场景 | 修复前 | 修复后 |
|---|---|---|
| 查看问题列表 | 需要手动修正原则 ID | 直接使用 |
| 查看问题详情 | 需要手动验证证据 | 直接使用 |
| 查看报告摘要 | 需要手动统计 | 直接查看 |
| 优先级排序 | 需要手动判断 | 直接查看 |

### 成本效益分析

| 项目 | 成本 | 收益 |
|---|---|---|
| 开发成本 | 19h | - |
| 测试成本 | 3h | - |
| 总成本 | 22h | - |
| 问题修复收益 | - | 节省 2h/次（手动修正） |
| 报告质量收益 | - | 节省 1h/次（手动统计） |
| ROI | - | 7 次使用后回本 |

---

**文档版本**：v2  
**最后更新**：2026-05-20  
**状态**：待执行
