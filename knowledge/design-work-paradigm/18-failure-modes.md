# 18. 失败模式库 (Failure Modes)

## 定义与目的

失败模式库（Failure Modes）是设计推理流程中所有可能出错环节的系统化分类和处理策略。资深设计师的核心能力之一是**预判风险**并**提前防范**，而不是等问题发生后才应对。

**核心目标**：
1. 识别设计推理的所有失败点
2. 为每个失败模式定义检测机制
3. 明确失败时的处理策略（blocked / fallback / warning）
4. 防止低质量产物被误标为"完成"

**使用场景**：
- ✅ 设计 quality gate 时参考
- ✅ 编写 validation 逻辑时参考
- ✅ 调试 pipeline 失败时参考
- ✅ 用户报告"输出不符合预期"时排查

---

## 失败模式分类

### 类别 1: 输入问题 (Input Issues)

#### FM-I001: 主要输入缺失或不可读

**描述**：PRD 文件不存在、损坏、格式不支持

**检测方法**：
```python
if not os.path.exists(prd_path):
    raise FailureMode("FM-I001", "PRD file not found")
if not is_readable(prd_path):
    raise FailureMode("FM-I001", "PRD file corrupted or format unsupported")
```

**处理策略**：`blocked`

**用户提示**：
> 错误：无法读取 PRD 文件。请确认文件路径正确且格式为 PDF/MD/DOCX。

---

#### FM-I002: 输入质量极低

**描述**：PRD 完全没有功能描述、用户定义或业务目标

**检测方法**：
```python
completeness_score = assess_input_completeness(prd)
if completeness_score < 0.3:
    raise FailureMode("FM-I002", "Input quality too low")
```

**处理策略**：`blocked`

**用户提示**：
> 错误：PRD 缺少核心信息（业务目标、用户定义、功能列表）。当前完整性评分：0.25/1.0。
> 
> 缺失内容：
> - [ ] 业务目标章节
> - [ ] 用户角色定义
> - [ ] 核心功能列表
> 
> 建议：请补充以上内容后重新执行。

---

#### FM-I003: 输入存在严重冲突

**描述**：PRD 内部有无法调和的矛盾（如时间约束 vs 功能数量）

**检测方法**：
```python
conflicts = detect_conflicts(requirement_inventory)
critical_conflicts = [c for c in conflicts if c.severity == "critical"]
if critical_conflicts:
    raise FailureMode("FM-I003", "Critical conflicts in input")
```

**处理策略**：`blocked`（需要人工决策）

**用户提示**：
> 错误：PRD 存在严重冲突，需要人工决策：
> 
> 冲突 1: 时间 vs 范围
> - PRD 2.1: "必须 Q2 上线"（3 个月）
> - PRD 4.3: 功能列表包含 15 个复杂功能
> 
> 建议：请明确 MVP 范围，或调整时间预期。

---

#### FM-I004: 关键假设无法验证

**描述**：必须做出的假设风险极高（如用户画像完全推断）

**检测方法**：
```python
high_risk_assumptions = [a for a in assumptions if a.risk_if_wrong == "critical"]
if len(high_risk_assumptions) > 2:
    raise FailureMode("FM-I004", "Too many high-risk assumptions")
```

**处理策略**：`fallback_safe`（降级到低保真模式）

**用户提示**：
> 警告：因输入不足，系统做出了 3 个高风险假设：
> 
> ASM-001: 假设用户为 25-40 岁职场人士（无用户研究数据）
> ASM-002: 假设用户主要在移动端使用（无使用数据）
> ASM-003: 假设用户熟练使用企业微信（无技能评估）
> 
> 当前模式：降级到低保真原型（线框图），不生成高保真设计。
> 
> 建议：补充用户研究数据后可切换到高保真模式。

---

### 类别 2: 推理资产问题 (Reasoning Asset Issues)

#### FM-R001: 推理资产不符合 Schema

**描述**：生成的 design_objectives 缺少必需字段

**检测方法**：
```python
try:
    validate_schema(design_objectives, DesignObjectivesSchema)
except ValidationError as e:
    raise FailureMode("FM-R001", f"Schema validation failed: {e}")
```

**处理策略**：`blocked`（不允许进入下游 stage）

**用户提示**：
> 错误：design_objectives 不符合 schema 要求：
> 
> 缺少必需字段：
> - business_goals[0].success_metric
> - user_goals[1].job_to_be_done
> 
> 系统已停止执行，请修复后重试。

---

#### FM-R002: 推理资产置信度过低

**描述**：某个关键资产的 confidence < 0.5

**检测方法**：
```python
if user_task_map.confidence < 0.5:
    raise FailureMode("FM-R002", "User task map confidence too low")
```

**处理策略**：`warning`（可继续但必须人工复核）

**用户提示**：
> 警告：user_task_map 置信度较低（0.45），原因：
> - PRD 未明确用户任务
> - 80% 任务为推断
> 
> 已标记为需人工复核。建议：补充用户访谈数据。

---

#### FM-R003: 推断内容占比过高

**描述**：某个资产的 inferred_fields 超过 30%

**检测方法**：
```python
inferred_ratio = len(asset.inferred_fields) / total_fields
if inferred_ratio > 0.3:
    raise FailureMode("FM-R003", "Too many inferred fields")
```

**处理策略**：`warning`（标记为低置信度）

**用户提示**：
> 警告：design_objectives 中 40% 内容为推断：
> 
> 推断字段：
> - user_goals[1]（完全推断）
> - business_goals[2].success_metric（部分推断）
> - experience_goals[0].target（推断）
> 
> 建议：人工复核所有标注 [inferred] 的字段。

---

#### FM-R004: 关键字段无追溯来源

**描述**：页面生成时，某个页面无法追溯到 user_task_map

**检测方法**：
```python
for page in information_architecture.pages:
    if not page.traceable_to_task:
        raise FailureMode("FM-R004", f"Page {page.id} not traceable")
```

**处理策略**：`blocked`（违反核心原则 5）

**用户提示**：
> 错误：发现无追溯来源的页面：
> 
> - PG-005 "数据统计" 无法追溯到任何 user_task
> - PG-008 "系统设置" 无法追溯到任何 user_task
> 
> 可能原因：
> 1. 这些页面超出 PRD 范围（scope creep）
> 2. 遗漏了对应的 user_task 建模
> 
> 建议：要么补充 user_task，要么移除这些页面。

---

#### FM-R005: 推理资产之间不一致

**描述**：information_architecture 中的页面数量 > user_task_map 中的任务数量，且无法解释

**检测方法**：
```python
page_count = len(information_architecture.pages)
task_count = len(user_task_map.primary_tasks) + len(user_task_map.secondary_tasks)

if page_count > task_count * 1.5:  # 允许一定冗余
    raise FailureMode("FM-R005", "Page count far exceeds task count")
```

**处理策略**：`warning`（可能是 scope creep）

**用户提示**：
> 警告：页面数量（15）远超任务数量（6），可能存在范围蔓延。
> 
> 未映射到任务的页面：
> - PG-010 "帮助中心"
> - PG-011 "关于我们"
> - PG-012 "隐私政策"
> 
> 建议：确认这些页面是否为 MVP 必需。

---

### 类别 3: 最终输出问题 (Output Issues)

#### FM-O001: 生成的代码无法构建

**描述**：prototype_code 有语法错误或依赖缺失

**检测方法**：
```python
build_result = run_build(prototype_code)
if build_result.exit_code != 0:
    raise FailureMode("FM-O001", "Build failed")
```

**处理策略**：`blocked`（不得声称"原型完成"）

**用户提示**：
> 错误：生成的原型代码无法构建：
> 
> 构建错误：
> - src/pages/Dashboard.tsx:15 - 'useState' is not defined
> - src/components/Table.tsx:42 - Cannot find module 'antd'
> 
> 系统已停止，请修复后重试。

---

#### FM-O002: 原型与设计规范不一致

**描述**：生成的组件与 component_strategy 不匹配

**检测方法**：
```python
for component in generated_code.components:
    if component not in component_strategy.component_inventory:
        raise FailureMode("FM-O002", f"Unauthorized component: {component}")
```

**处理策略**：`warning`（可能需要调整）

**用户提示**：
> 警告：发现未经授权的组件：
> 
> - src/components/CustomModal.tsx（未在 component_strategy 中定义）
> 
> 建议：要么使用 Ant Design Modal，要么在 component_strategy 中声明此自定义组件。

---

#### FM-O003: 无障碍性严重违规

**描述**：生成的 HTML 缺少 alt 属性、ARIA 标签

**检测方法**：
```python
accessibility_issues = check_accessibility(generated_code)
critical_issues = [i for i in accessibility_issues if i.severity == "critical"]
if critical_issues:
    raise FailureMode("FM-O003", "Critical accessibility violations")
```

**处理策略**：`warning`（标记为需修复）

**用户提示**：
> 警告：发现 8 个严重无障碍性问题：
> 
> - 5 个图片缺少 alt 属性
> - 2 个按钮缺少 aria-label
> - 1 个表单缺少 label 关联
> 
> 当前状态：不符合 WCAG 2.1 AA 标准。
> 
> 建议：补充无障碍属性后再发布。

---

#### FM-O004: 状态管理逻辑错误

**描述**：生成的状态转换与 state_matrix 不一致

**检测方法**：
```python
for page in generated_code.pages:
    expected_states = state_matrix.get_states_for_page(page.id)
    actual_states = extract_states_from_code(page.code)
    
    if expected_states != actual_states:
        raise FailureMode("FM-O004", f"State mismatch in {page.id}")
```

**处理策略**：`blocked`（违反核心原则 1）

**用户提示**：
> 错误：页面 PG-003 的状态实现与 state_matrix 不一致：
> 
> 期望状态（来自 state_matrix）：
> - loading
> - success
> - error
> - empty
> 
> 实际实现状态：
> - loading
> - success
> 
> 缺失状态：error, empty
> 
> 建议：补充错误处理和空状态处理逻辑。

---

### 类别 4: 追溯性问题 (Traceability Issues)

#### FM-T001: Traceability Map 缺失

**描述**：最终产物没有生成 traceability_map

**检测方法**：
```python
if not os.path.exists(output_dir / "traceability-map.json"):
    raise FailureMode("FM-T001", "Traceability map missing")
```

**处理策略**：`blocked`（违反核心原则 5）

**用户提示**：
> 错误：未生成 traceability_map.json。
> 
> 根据核心原则 5，所有最终产物必须包含可追溯性地图。
> 
> 系统已停止，请补充后重试。

---

#### FM-T002: 关键决策无追溯依据

**描述**：decision_trace 中某个决策的 `based_on` 为空

**检测方法**：
```python
for decision in traceability_map.decision_trace:
    if not decision.based_on:
        raise FailureMode("FM-T002", f"Decision {decision.id} has no basis")
```

**处理策略**：`warning`（标记为需人工确认）

**用户提示**：
> 警告：发现 2 个无追溯依据的决策：
> 
> DEC-005: "选择侧边栏导航"
> - 缺少 based_on 字段
> - 无法追溯到 user_task_map 或 information_architecture
> 
> 建议：补充决策依据，或删除此决策记录。

---

#### FM-T003: 输入覆盖率过低

**描述**：PRD 中 50% 的需求未被实现

**检测方法**：
```python
implemented_requirements = traceability_map.coverage_analysis.requirement_coverage
if implemented_requirements < 0.7:
    raise FailureMode("FM-T003", "Input coverage too low")
```

**处理策略**：`warning`（可能是故意缩减范围）

**用户提示**：
> 警告：需求实现覆盖率仅 65%。
> 
> 未实现需求：
> - FR-005: 数据导入导出
> - FR-007: 团队协作
> - FR-009: 消息通知
> 
> 如果这是故意的范围缩减，请在 scope_boundaries.out_of_scope 中声明。

---

#### FM-T004: Scope Creep 未说明

**描述**：生成了 PRD 外的页面，但未在 traceability_map 中说明

**检测方法**：
```python
scope_creep_items = traceability_map.coverage_analysis.scope_creep_items
unapproved_items = [i for i in scope_creep_items if i.approval_status != "approved"]

if unapproved_items:
    raise FailureMode("FM-T004", "Unapproved scope creep")
```

**处理策略**：`blocked`（需要人工批准）

**用户提示**：
> 错误：发现未批准的范围扩展：
> 
> - PG-015 "数据分析仪表板"（PRD 中未提及）
> - PG-016 "AI 推荐"（PRD 中未提及）
> 
> 请选择：
> 1. 移除这些页面
> 2. 在 traceability_map.scope_creep_items 中标记为 approved 并说明理由

---

### 类别 5: 质量门问题 (Quality Gate Issues)

#### FM-Q001: Schema Gate 被绕过

**描述**：某个 stage 输出不符合 schema 但仍然继续执行

**检测方法**：
```python
# 在 pipeline 中强制验证
@enforce_schema_gate
def stage_output(data):
    return data

# 如果被绕过，记录违规
if schema_gate_bypassed:
    raise FailureMode("FM-Q001", "Schema gate bypassed")
```

**处理策略**：`blocked`（严重违规）

**用户提示**：
> 错误：检测到质量门被绕过！
> 
> Stage: design-analysis
> 输出: information_architecture.json
> 问题: 缺少必需字段 'navigation'，但仍然进入下游 stage
> 
> 这违反了核心原则 6（质量门不得被绕过）。
> 
> 系统已停止，请修复 schema 验证逻辑。

---

#### FM-Q002: Gap Transparency Gate 未执行

**描述**：存在 critical gaps 但未进入 blocked/fallback_safe 状态

**检测方法**：
```python
critical_gaps = [g for g in requirement_inventory.gaps if g.impact == "critical"]
if critical_gaps and readiness_decision != "blocked":
    raise FailureMode("FM-Q002", "Critical gaps not handled")
```

**处理策略**：`blocked`

**用户提示**：
> 错误：存在 critical gap 但系统仍然继续执行：
> 
> GAP-001 (critical): PRD 完全没有用户定义
> 
> 根据核心原则 4，critical gap 必须阻塞执行或降级到 fallback_safe。
> 
> 当前状态：违规
> 
> 系统已停止。

---

#### FM-Q003: Professional Gap Report 未生成

**描述**：最终产物没有 professional_gap_report.json

**检测方法**：
```python
if not os.path.exists(output_dir / "professional-gap-report.json"):
    raise FailureMode("FM-Q003", "Professional gap report missing")
```

**处理策略**：`blocked`（违反核心原则 7）

**用户提示**：
> 错误：未生成 professional_gap_report.json。
> 
> 根据核心原则 7，所有最终产物必须包含专业差距报告。
> 
> 系统已停止。

---

### 类别 6: 人工复核边界问题 (Human Review Boundary Issues)

#### FM-H001: 声称 production-ready 但实际不是

**描述**：professional_gap_report 显示 production_readiness.ready_for_production = false，但向用户声称"可直接使用"

**检测方法**：
```python
gap_report = load_gap_report()
if not gap_report.production_readiness.ready_for_production:
    if "production-ready" in user_facing_message:
        raise FailureMode("FM-H001", "False production-ready claim")
```

**处理策略**：`blocked`（诚信问题）

**用户提示**：
> 错误：检测到虚假声称！
> 
> 系统向用户显示："原型已完成，可直接用于生产环境"
> 
> 但 professional_gap_report 显示：
> - production_readiness.ready_for_production = false
> - 存在 3 个 must_fix blockers
> 
> 这违反了核心原则 7（人工复核边界必须明确）。
> 
> 系统已停止，请修正用户提示。

---

#### FM-H002: 高风险内容未标记需人工复核

**描述**：业务流程建模完全基于推断，但 human_review_required = false

**检测方法**：
```python
if business_flow.inferred_ratio > 0.5:
    if not gap_report.human_review_requirements.review_required:
        raise FailureMode("FM-H002", "High-risk content not flagged for review")
```

**处理策略**：`warning`（强制标记）

**用户提示**：
> 警告：business_flow 中 60% 内容为推断，但未标记需人工复核。
> 
> 系统已自动标记：
> - human_review_requirements.review_required = true
> - review_priority = high
> - review_focus_areas = ["业务流程正确性"]

---

## 失败模式处理决策树

```
检测到失败模式
    │
    ├─ 是否违反核心原则？
    │   ├─ 是 → blocked（立即停止）
    │   └─ 否 → 继续评估
    │
    ├─ 是否影响产物可用性？
    │   ├─ 严重影响 → blocked
    │   ├─ 中等影响 → fallback_safe（降级）
    │   └─ 轻微影响 → warning（标记）
    │
    └─ 是否可自动修复？
        ├─ 可以 → 修复并记录
        └─ 不可以 → 需要人工介入
```

---

## 失败模式优先级

### P0 (必须阻塞)
- FM-I001: 主要输入缺失
- FM-I002: 输入质量极低
- FM-R001: 推理资产不符合 Schema
- FM-R004: 关键字段无追溯来源
- FM-O001: 生成的代码无法构建
- FM-O004: 状态管理逻辑错误
- FM-T001: Traceability Map 缺失
- FM-Q001: Schema Gate 被绕过
- FM-Q002: Gap Transparency Gate 未执行
- FM-Q003: Professional Gap Report 未生成
- FM-H001: 声称 production-ready 但实际不是

### P1 (应该警告)
- FM-I003: 输入存在严重冲突
- FM-R002: 推理资产置信度过低
- FM-R003: 推断内容占比过高
- FM-R005: 推理资产之间不一致
- FM-O002: 原型与设计规范不一致
- FM-O003: 无障碍性严重违规
- FM-T002: 关键决策无追溯依据
- FM-T003: 输入覆盖率过低
- FM-H002: 高风险内容未标记需人工复核

### P2 (可记录)
- FM-I004: 关键假设无法验证
- FM-T004: Scope Creep 未说明

---

## 实施建议

### 在 Skill 开发中
1. 为每个 stage 定义可能的失败模式
2. 在 quality gate 中检测失败模式
3. 失败时提供明确的用户提示和修复建议

### 在测试中
1. 为每个失败模式编写测试用例
2. 确保失败模式被正确检测和处理
3. 验证用户提示的清晰度

### 在文档中
1. 在 SKILL.md 中列出常见失败模式
2. 在 PILOT-BOUNDARY.md 中说明已知的未处理失败模式
3. 在 professional_gap_report 中引用相关失败模式

---

## 版本历史

- **v1.0.0** (2026-06-09): 初始版本，定义 20+ 失败模式
