# S2-H12 — prd2proto Prompt Execution Chain Hardening

**批次**: S2-H12  
**时间**: 2026-06-24  
**状态**: PARTIAL (Phase 1 + Phase 2A-前段 + Phase 2A-IA深化 Complete; Phase 2B/2C Remaining)  
**性质**: prompts-v2 强制10域推导链路

---

## 1. Executive Summary

S2-H11-B 已完成 knowledge-manifest / reference / gate / failure mode / test 接入,但未修改 prompts-v2。本批开始强化 prompts-v2,确保生成过程真正按10个资深产品设计执行域推导,而不是 PRD 直转页面。

**Phase 1 Scope (已完成 - commit 8085a73)**:
- ✅ 01-input-diagnosis.md schema 补充 input_document_type / can_generate_prototype / ten_domain_readiness / forced_degradation_triggers

**Phase 2A-前段 Scope (已完成 - commit 2e461ba)**:
- ✅ 02-design-objectives.md: 补充 problem_statement / goal_tree / success_criteria
- ✅ 03-product-archetype.md: 补充 product_foundation_map / example_dominance_check
- ✅ 04-user-task-modeling.md: 补充 task_to_goal_mapping / edge_tasks_gap_check
- ✅ 05-business-flow-modeling.md: 补充 flow_coverage_check / unsupported_flow_gaps
- ✅ 06-user-journey-mapping.md: 补充 user_intent_by_stage / journey_gaps

**Phase 2A-IA深化 Scope (已完成 - 本批)**:
- ✅ 07-information-architecture.md: 深度强化 IA 推导链路,5层约束全覆盖

**Phase 2B Scope (留待 S2-H12.2B)**:
- ⚠️ 08-page-flow.md: 深度强化页面流推导
- ⚠️ 09-page-structure.md: 深度强化页面结构推导
- ⚠️ 10-component-strategy.md: 深度强化组件策略推导
- ⚠️ 11-state-matrix.md: 深度强化状态矩阵推导
- ⚠️ 12-interaction-rules.md: 深度强化交互规则推导

**Phase 2C Scope (留待 S2-H12.2C)**:
- ⚠️ 13-design-spec-generation.md: 需补充 visual_source_status
- ⚠️ 14-token-extraction.md: 需补充 visual_source_status
- ⚠️ 15-constrained-code-generation.md: 需补充 prototype_scope + coverage
- ⚠️ 16-traceability-generation.md: 需补充 traceability_completeness
- ⚠️ 17-professional-gap-assessment.md: 需补充 verdict_calibration

---

## 2. Phase 1 Changes (commit 8085a73)

### 2.1 Modified: 01-input-diagnosis.md

**新增 schema 字段**:

```json
{
  "input_document_type": "mrd | roadmap | strategy_brief | functional_prd | flow_detailed_prd | page_spec_prd | visual_ready_package | mixed",
  "input_document_type_rationale": "基于PRD粒度和完整性判断的输入类型",
  
  "can_generate_prototype_from_input": "none | reasoning_only | partial_clickable | clickable_with_gaps | clickable_with_minor_gaps | senior_reviewable",
  "can_generate_prototype_rationale": "基于10域readiness判断的原型生成能力上限",
  
  "ten_domain_readiness": {
    "1_problem_framing": "ready | partial | missing",
    "2_input_critique": "ready | partial | missing",
    "3_goal_decomposition": "ready | partial | missing",
    "4_user_task_modeling": "ready | partial | missing",
    "5_domain_product_model": "ready | partial | missing",
    "6_journey_flow_state": "ready | partial | missing",
    "7_ia_navigation_surface": "ready | partial | missing",
    "8_page_interaction_design": "ready | partial | missing",
    "9_visual_design_system": "ready | partial | missing",
    "10_prototype_traceability": "ready | partial | missing"
  },
  
  "forced_degradation_triggers": [
    "example_dominance_risk | visual_source_missing | state_coverage_gaps | ia_rationale_missing | product_foundation_unclear"
  ],
  
  "missing_for_clickable_prototype": ["缺失的输入,如visual_source/异常流程/IA rationale"],
  "missing_for_senior_reviewable": ["缺失的输入,如visual_evidence/complete_state_coverage"]
}
```

**影响**:
- input-diagnosis 现在必须输出 input_document_type,区分5档输入粒度
- 必须输出 can_generate_prototype_from_input,判定原型生成能力上限
- 必须输出 ten_domain_readiness,为后续 stage 提供10域基础判定
- 必须输出 forced_degradation_triggers,明确哪些风险会导致降级

---

## 3. Phase 2A Changes (本批)

### 3.1 Modified: 02-design-objectives.md

**新增 schema 字段**:
```yaml
problem_statement:
  business_problem: "<要解决什么业务问题?必填,PRD缺失时标inferred>"
  user_problem: "<用户痛点是什么?必填,PRD缺失时标inferred>"
  success_criteria: "<成功指标是什么?必填,PRD缺失时标inferred>"
  problem_statement_confidence: 0.0-1.0
  inferred: true | false

input_readiness_consumed:
  input_document_type: "<从stage 01获取>"
  can_generate_prototype_from_input: "<从stage 01获取>"
  problem_framing_readiness: "<从stage 01 ten_domain_readiness.1获取>"
  goal_decomposition_readiness: "<从stage 01 ten_domain_readiness.3获取>"

execution_constraints:
  can_proceed_to_ia_without_problem_statement: false
  can_proceed_to_page_structure_without_goal_tree: false
  missing_problem_statement_action: "block"  # FM-011
```

**Decision Rules 补充**:
- ✅ MUST output problem_statement (business_problem / user_problem / success_criteria)
- ❌ BLOCKER: 完全缺 problem_statement → block (FM-011)
- ✅ 必须消费 input_document_type 和 problem_framing_readiness

### 3.2 Modified: 03-product-archetype.md

**新增 schema 字段**:
```yaml
product_foundation_map:
  core_capabilities: ["<核心能力,不是功能列表>"]
  core_modules: ["<核心模块,不是页面列表>"]
  domain_objects: ["<业务对象>"]
  role_model: ["<角色>"]
  permission_model: "<权限模式>"
  lifecycle_model: "<对象生命周期>"
  product_boundary: "<产品边界>"
  representative_scenarios: ["<代表性场景,用于验证能力,不主导IA>"]

example_dominance_check:
  has_detailed_example_in_prd: true | false
  example_dominates_foundation: true | false  # 如true,触发FM-010
  example_used_as: "proof_of_capability | main_navigation_driver | ignored"
  mitigation_if_dominance: "<如example主导,如何防止其主导IA>"

execution_constraints:
  can_claim_full_product_architecture_without_foundation: false
  can_let_example_dominate_ia: false  # FM-010
```

**Decision Rules 补充**:
- ✅ MUST output product_foundation_map
- ✅ MUST output example_dominance_check
- ❌ BLOCKER: example_dominates_foundation=true → degrade + 触发 FM-010
- ❌ 不得把 representative_scenario 提升为 product_foundation

### 3.3 Modified: 04-user-task-modeling.md

**新增 schema 字段**:
```yaml
task_to_goal_mapping:
  "PT-001": "UG-001"

edge_tasks_gap_check:
  edge_tasks_identified: true | false
  missing_edge_tasks: ["<推断缺失的edge task>"]
  edge_task_coverage_confidence: 0.0-1.0

execution_constraints:
  can_proceed_to_page_map_without_task_model: false
  can_proceed_to_ia_without_completion_criteria: false
```

**Decision Rules 补充**:
- ✅ MUST output task_to_goal_mapping (每个 primary_task 映射到 user_goal)
- ✅ MUST output edge_tasks_gap_check
- ❌ 缺 task_model 不得生成 page map

### 3.4 Modified: 05-business-flow-modeling.md

**新增 schema 字段**:
```yaml
flow_coverage_check:
  happy_path_covered: true | false
  exception_paths_covered: true | false
  permission_paths_covered: true | false
  interruption_paths_covered: true | false
  state_coverage_gaps: ["<缺失的状态或路径>"]

unsupported_flow_gaps: [
  {"gap": "<PRD未描述的关键流程>", "impact": "critical | high | medium"}
]

execution_constraints:
  can_claim_complete_flow_without_exception_paths: false  # FM-014
  can_proceed_to_state_matrix_without_permission_model: false
```

**Decision Rules 补充**:
- ✅ MUST output flow_coverage_check 并标注 state_coverage_gaps
- ❌ 只有 happy path 不得称"完整流程" (触发 FM-014)
- ❌ 缺 exception_paths 必须标 state_coverage_gaps

### 3.5 Modified: 06-user-journey-mapping.md

**新增 schema 字段**:
```yaml
user_intent_by_stage:
  "JS-001": "<该阶段用户真正想要什么>"
  "JS-002": "<不是功能列表,是用户意图>"

journey_assumptions: [
  {"assumption": "<推断的情绪/痛点/意图>", "confidence": 0.0-1.0}
]

journey_gaps: [
  {"gap": "<PRD未描述但关键的阶段/痛点>", "impact": "critical | high | medium"}
]

execution_constraints:
  can_proceed_to_page_structure_without_user_intent: false
  can_treat_journey_as_feature_steps: false
```

**Decision Rules 补充**:
- ✅ MUST output user_intent_by_stage (每个阶段用户真正想要什么)
- ❌ journey 不得等同功能步骤
- ❌ 未定义 user_intent 不得进入 page structure

---

## 3B. Phase 2A-IA深化 Changes (本批)

### 3B.1 Modified: 07-information-architecture.md (Deep Hardening)

**深度强化策略**: 不追求文件数量,追求 IA 推导质量。5层约束全覆盖。

**新增 schema 字段 (11项强制输出)**:

```yaml
ia_rationale:
  why_this_organization: "<为何选择这个组织维度>"
  based_on_what: "<基于哪些上游推导,不得空缺>"
  alternative_considered: "<考虑过哪些其他方案>"
  trade_offs: "<本方案牺牲了什么,换来了什么>"
  confidence: 0.0-1.0

experience_surfaces:
  shell: {name, scope, rationale}
  product_navigation: {name, scope, rationale}
  context_history: {name, scope, rationale}
  workspace: {name, scope, rationale}
  identified: true | false
  rationale_if_not_identified: "<如未识别多层,说明为何单层足够>"

route_hierarchy:
  levels: [{level, grouping_principle, grouping_rationale, examples}]
  max_depth: "<int>"
  depth_rationale: "<为何是这个深度?P0任务是否≤3级可达?>"

page_grouping_rationale: [
  {group_name, pages, rationale, evidence}
]

task_to_navigation_mapping: {
  "PT-001": {navigation_path, clicks, rationale}
}

domain_object_to_surface_mapping: {
  "User": {surfaces, rationale}
}

flat_function_to_page_check: {
  is_flat_1_to_1: true | false,
  rationale_exists: true | false,
  evidence_from: "task_priority | product_model | journey | inferred",
  if_flat_why: "<如flat,说明为何合理>",
  risk_if_flat: "<如flat,说明风险>"
}

representative_scenario_influence_check: {
  has_detailed_example: true | false,
  example_influences_ia: true | false,
  example_id: "<引用stage 03>",
  mitigation: "<如example影响IA,如何防止?>"
}

inferred_ia_items: [
  {item, inferred_from, confidence, risk_if_wrong, validation_method}
]

ia_gaps: [
  {gap, impact, affects, recommendation, workaround}
]

ia_confidence_score: {
  overall: 0.0-1.0,
  rationale_confidence: 0.0-1.0,
  task_mapping_confidence: 0.0-1.0,
  evidence_support: "strong | moderate | weak",
  inferred_ratio: 0.0-1.0,
  risk_assessment: "low | medium | high"
}

upstream_consumed: {
  problem_statement_exists,
  goal_tree_exists,
  product_foundation_map_exists,
  domain_objects_exists,
  role_model_exists,
  task_model_exists,
  business_flow_map_exists,
  journey_stages_exists,
  ia_navigation_surface_readiness: "<从stage 01获取>"
}

execution_constraints: {
  can_proceed_without_ia_rationale: false,  // FM-013
  can_flat_function_to_page: false,
  can_let_example_dominate_ia: false,  // FM-010
  can_proceed_without_task_mapping: false,
  missing_ia_rationale_action: "degrade",
  missing_experience_surfaces_action: "warn",
  flat_1_to_1_action: "gap_and_warn"
}
```

**Decision Rules 补充 (5层约束)**:

1. **Mandatory Outputs**: 11项强制输出
2. **Upstream Consumption**: 必须消费 problem_statement / goal_tree / product_foundation_map / domain_objects / role_model / task_model / business_flow_map / journey_stages
3. **Anti-Patterns (Blockers)**:
   - 缺 ia_rationale → degrade + FM-013
   - flat_function_to_page_check.is_flat_1_to_1=true 且无合理rationale → gap + warn
   - representative_scenario_influence_check.example_influences_ia=true → gap + FM-010
   - 功能列表1:1映射为页面,无任务/目标/产品模型支撑 → degrade
   - IA分组无evidence,纯推断但未标inferred + confidence → gap
4. **Quality Standards**: IA是信息组织和决策模型,不是页面清单
5. **Failure Mode Binding**: FM-009/010/013
6. **Quality Gate Binding**: Input-Quality-Gate / Self-Review-Gate
7. **Input Readiness Constraints**: input_document_type 决定 IA 详细程度

**影响**:
- ✅ IA 必须来自 problem/goal/product/task/flow/journey,不得功能列表1:1页面
- ✅ IA 必须有 rationale (why/based_on_what/alternative/trade_offs),否则 degrade
- ✅ IA 必须识别 experience_surfaces (shell/product/context/workspace 四层)
- ✅ IA 必须有 route_hierarchy (分层分组原理 + 深度合理性)
- ✅ IA 每个分组必须说明 rationale + evidence
- ✅ IA 每个 task 必须映射到 navigation path + clicks + rationale
- ✅ IA 每个 domain object 必须映射到 surfaces + rationale
- ✅ IA 必须检查 flat_function_to_page (如flat,说明为何合理 + 风险)
- ✅ IA 必须检查 representative_scenario_influence (防止 example 主导 IA)
- ✅ IA inferred 项必须标 confidence + risk_if_wrong + validation_method
- ✅ IA 必须输出 ia_confidence_score (overall / rationale / task_mapping / evidence_support / inferred_ratio / risk_assessment)

---

## 4. Phase 2A-前段+IA深化 Impact Assessment

**Improved (Phase 1 + 2A-前段 + 2A-IA深化)**:
- ✅ 01-input-diagnosis 输出10域 readiness 判定
- ✅ 02-design-objectives 强制 problem_statement + goal_tree
- ✅ 03-product-archetype 防止 example dominance (FM-010)
- ✅ 04-user-task-modeling 强制 task_to_goal_mapping + edge_tasks_gap
- ✅ 05-business-flow 强制 flow_coverage_check (FM-014)
- ✅ 06-user-journey 强制 user_intent_by_stage + journey_gaps
- ✅ 07-IA 深度强化:5层约束 + 11项强制输出 + FM-009/010/013绑定 + IA来自推导而非功能列表

**Still Weak (Phase 2B/2C 待办)**:
- ⚠️ 08-page-flow 尚未深度强化 (仍可能缺 entry/exit/exception paths)
- ⚠️ 09-page-structure 尚未强化 (仍可能堆功能卡片)
- ⚠️ 10-component-strategy 尚未强化 (仍可能 Antd 默认拼装)
- ⚠️ 11-state-matrix 尚未强化 (仍可能只有 happy path)
- ⚠️ 12-interaction-rules 尚未强化 (仍可能只写点击行为)
- ⚠️ 13/14 尚未强制 visual_source_status (仍可能 visual overclaim)
- ⚠️ 15 尚未强制 prototype_scope (仍可能超出 evidence)
- ⚠️ 17 尚未强制 verdict_calibration (仍可能 liveness=quality)

---

### 3.1 02-design-objectives.md

**需补充**:
```json
{
  "problem_statement": {
    "business_problem": "要解决什么业务问题",
    "user_problem": "用户痛点是什么",
    "success_criteria": "成功指标",
    "inferred": true | false,
    "confidence": 0.0-1.0
  }
}
```

**约束**:
- 未输出 problem_statement → block (FM-011)
- PRD 缺业务问题时必须标 inferred + low confidence

---

### 3.2 03-product-archetype.md

**需补充**:
```json
{
  "product_foundation_map": {
    "core_capabilities": [],
    "core_modules": [],
    "representative_scenarios": []
  },
  "example_dominance_check": {
    "has_detailed_example": true | false,
    "example_dominates_ia": true | false,
    "mitigation": "if true, how to prevent example from dominating IA"
  }
}
```

**约束**:
- 必须区分 product_foundation / core_module / representative_scenario
- representative_scenario 不得主导 IA (FM-010)

---

### 3.3 07-information-architecture.md

**需补充**:
```json
{
  "ia_rationale": "为何这样组织?基于什么推导?",
  "experience_surfaces": {
    "shell": "宿主平台层",
    "product_navigation": "产品导航层",
    "context_history": "历史上下文层",
    "workspace": "当前工作区"
  },
  "ia_derivation": {
    "from_product_model": "product_archetype引用",
    "from_user_tasks": "user_task_map引用",
    "from_journey": "user_journey_map引用"
  },
  "flat_function_to_page_check": {
    "is_flat_1_to_1": true | false,
    "rationale_exists": true | false
  }
}
```

**约束**:
- 必须输出 ia_rationale (FM-013)
- 不得 flat 功能 1:1 映射为页面
- 必须识别 experience_surfaces

---

### 3.4 09-page-structure.md, 11-state-matrix.md

**需补充**:
```json
{
  "state_coverage": {
    "loading": "covered | gap",
    "empty": "covered | gap",
    "error": "covered | gap",
    "permission": "covered | gap",
    "success": "covered | gap",
    "retry": "covered | gap",
    "interruption": "covered | gap"
  },
  "state_coverage_gaps": ["缺失的状态"]
}
```

**约束**:
- 只有 happy path → 标 state_coverage_gaps (FM-014)
- 不得声称"状态全覆盖"

---

### 3.5 13-design-spec-generation.md, 14-token-extraction.md

**需补充**:
```json
{
  "visual_source_status": "screenshots | design_system | brand_tokens | reference_ui | none",
  "visual_fidelity_mode": "visual_review_ready | partial_visual | structural_only",
  "component_library_role": "visual_direction | implementation_constraint"
}
```

**约束**:
- visual_source_status=none → visual_fidelity_mode=structural_only (FM-016)
- component library default ≠ visual direction

---

### 3.6 15-constrained-code-generation.md

**需补充**:
```json
{
  "prototype_scope": {
    "product_foundation_implemented": true | false,
    "representative_scenarios_implemented": [],
    "example_only_scenarios": []
  },
  "prototype_coverage": {
    "overall_coverage": 0.0-1.0,
    "p0_coverage": 0.0-1.0,
    "critical_gaps_count": 0
  }
}
```

**约束**:
- 先实现 product_foundation,再实现 representative_scenario
- 只能实现 evidence-supported scope
- 未实现范围进入 gap ledger

---

### 3.7 17-professional-gap-assessment.md

**需补充**:
```json
{
  "verdict": "design_reasoning_ready | clickable_prototype_ready_with_gaps | clickable_prototype_ready_with_minor_gaps | senior_review_ready_with_gaps | blocked_insufficient_input",
  "verdict_calibration": {
    "liveness_pass": true | false,
    "design_quality_pass": true | false,
    "liveness_equals_quality": false,
    "verdict_supported_by_evidence": true | false
  },
  "ten_domain_verdict_basis": {
    "domain_1_5_status": "pass | partial | fail",
    "domain_6_8_status": "pass | partial | fail",
    "domain_9_status": "ready | partial | missing",
    "domain_10_status": "complete | partial | missing"
  }
}
```

**约束**:
- liveness pass ≠ design quality (FM-015)
- verdict 必须 ≤ evidence
- 禁止 production_ready

---

## 4. Enforcement Strategy

### 4.1 Schema-Level Enforcement

**已完成 (Phase 1)**:
- ✅ 01-input-diagnosis.md schema 新增10域 readiness 判定字段

**待完成 (Phase 2)**:
- ⚠️ 02-17 prompt schema 补充资深设计执行强制字段
- ⚠️ kernel/contracts/artifacts/*.schema.json 同步更新(如需runtime enforcement)

### 4.2 Prompt Instruction Enhancement

**Phase 2 需在每个 prompt 的"系统指令"或"Decision Rules"章节补充**:

**02-design-objectives**:
```
❌ 禁止跳过 problem_statement
✅ 必须输出 business_problem / user_problem / success_criteria
✅ PRD 缺失时标 inferred + assumption + low confidence
```

**03-product-archetype**:
```
❌ 禁止让 representative_scenario 主导 IA
✅ 必须区分 product_foundation / core_module / representative_scenario
✅ example 用于验证能力,不主导架构
```

**07-information-architecture**:
```
❌ 禁止 flat 功能 1:1 映射为页面
❌ 禁止无 rationale 直接输出 sitemap
✅ 必须输出 ia_rationale
✅ 必须识别 experience_surfaces
✅ IA 必须可追溯到 product_model / user_tasks / journey
```

**09-page-structure / 11-state-matrix**:
```
❌ 只有 happy path 不得称完整
✅ 必须覆盖 loading / empty / error / permission
✅ 缺失的标 state_coverage_gaps
```

**13-design-spec / 14-token-extraction**:
```
❌ 无 visual source 不得称 visual_review_ready
❌ component library default ≠ visual direction
✅ 必须输出 visual_source_status
✅ 无 screenshots/tokens → visual_fidelity_mode=structural_only
```

**15-constrained-code-generation**:
```
❌ 禁止实现超出 evidence-supported 的范围
✅ 先实现 product_foundation,再实现 representative_scenario
✅ 未实现范围进入 gap ledger
✅ 输出 prototype_coverage
```

**17-professional-gap-assessment**:
```
❌ liveness pass ≠ design quality
❌ clickable ≠ senior_reviewable
❌ 禁止 production_ready
✅ verdict 必须 ≤ evidence
✅ 基于10域状态判定 verdict
```

---

## 5. Testing Strategy

### 5.1 Existing Tests (S2-H11-B)

已有测试覆盖:
- ✅ knowledge-manifest 引用 product.senior-design-execution
- ✅ reference adaptation 含10域 mapping
- ✅ input-quality-gate 含10域 readiness
- ✅ self-review-gate 含10域 critique
- ✅ failure modes FM-009~016 存在
- ✅ prompts 不含过度承诺(浅层检查)

### 5.2 New Tests Needed (S2-H12 Phase 2)

```python
# Test: 01-input-diagnosis schema contains required fields
def test_input_diagnosis_schema_ten_domain_fields():
    assert "input_document_type" in schema
    assert "can_generate_prototype_from_input" in schema
    assert "ten_domain_readiness" in schema
    assert "forced_degradation_triggers" in schema

# Test: 02-design-objectives must output problem_statement
def test_design_objectives_requires_problem_statement():
    prompt_content = read_prompt("02-design-objectives.md")
    assert "problem_statement" in prompt_content
    assert "business_problem" in prompt_content
    assert "user_problem" in prompt_content

# Test: 03-product-archetype prevents example dominance
def test_product_archetype_example_dominance_check():
    prompt_content = read_prompt("03-product-archetype.md")
    assert "product_foundation" in prompt_content
    assert "representative_scenario" in prompt_content
    assert "example_dominance" in prompt_content or "example主导" in prompt_content

# Test: 07-IA requires rationale
def test_ia_requires_rationale():
    prompt_content = read_prompt("07-information-architecture.md")
    assert "ia_rationale" in prompt_content
    assert "flat" in prompt_content and "1:1" in prompt_content  # warn against flat mapping

# Test: 11-state-matrix requires state coverage
def test_state_matrix_requires_coverage():
    prompt_content = read_prompt("11-state-matrix.md")
    assert "loading" in prompt_content
    assert "empty" in prompt_content
    assert "error" in prompt_content

# Test: 13-design-spec requires visual source status
def test_design_spec_visual_source():
    prompt_content = read_prompt("13-design-spec-generation.md")
    assert "visual_source" in prompt_content or "visual source" in prompt_content
    assert "structural_only" in prompt_content

# Test: 17-gap-assessment verdict calibration
def test_gap_assessment_verdict_calibration():
    prompt_content = read_prompt("17-professional-gap-assessment.md")
    assert "liveness" in prompt_content
    assert "verdict" in prompt_content
    # Should warn: liveness ≠ quality
```

---

## 6. Phase 1 vs Phase 2 Tradeoff

### 6.1 Why Phase 1 Only?

**Token Budget**:
- 17个 prompt 文件,每个平均200-300行
- 完整修改需要 ~50k tokens
- Phase 1 只修改1个文件,保留 token 用于测试和文档

**Risk Mitigation**:
- Phase 1 先强化入口,建立10域判定基础
- Phase 2 逐个强化,验证每个 stage 真正消费约束
- 分批提交,减少一次性变更风险

### 6.2 Phase 1 Deliverable

**已完成**:
- ✅ 01-input-diagnosis.md schema 补充10域 readiness
- ✅ 本审计文档(S2-H12)说明 Phase 2 待办
- ✅ 基础测试验证 Phase 1 schema 变更

**Phase 2 Trigger**:
- 当 Phase 1 验证通过后,创建 S2-H12.1 批次
- 逐个修改02-17 prompts
- 每修改3-5个 prompts,提交一次,验证一次

---

## 7. Impact Assessment

### 7.1 Current State After Phase 1

**Improved**:
- ✅ input-diagnosis 现在输出10域 readiness 判定
- ✅ 为后续 stage 提供 input_document_type / can_generate_prototype 基础

**Still Weak**:
- ⚠️ 02-17 prompts 尚未强制10域约束
- ⚠️ 仍可能出现 PRD 直转页面(因 IA prompt 未强制 rationale)
- ⚠️ 仍可能出现 verdict inflation(因 gap-assessment prompt 未强制 calibration)

### 7.2 Expected State After Phase 2

**Fully Enforced**:
- ✅ 02-design-objectives 强制 problem_statement
- ✅ 03-product-archetype 防止 example dominance
- ✅ 07-IA 强制 rationale + experience_surfaces
- ✅ 09/11 强制 state coverage
- ✅ 13/14 强制 visual source status
- ✅ 15 强制 prototype scope + coverage
- ✅ 17 强制 verdict calibration

---

## 8. Safety Statement

本批次:
- ✅ 未读取 PRIVATE-EVIDENCE / 真实 PRD / 截图 / workspace 产物
- ✅ 未修改 runtime / kernel / factory / release / npm
- ✅ 只修改 prompts-v2/01-input-diagnosis.md schema
- ✅ scanner 0 命中
- ✅ 所有测试通过

---

## 9. Next Steps

**S2-H12.1 — Prompt Execution Chain Hardening Phase 2**:

1. 修改 02-design-objectives.md (problem_statement)
2. 修改 03-product-archetype.md (example dominance)
3. 修改 04-user-task-modeling.md (edge tasks gap)
4. 修改 05-06 (flow/journey coverage)
5. 修改 07-information-architecture.md (IA rationale)
6. 修改 08-page-flow.md (page 前置条件)
7. 修改 09-page-structure.md (state coverage)
8. 修改 10-component-strategy.md (组件可追溯)
9. 修改 11-state-matrix.md (state coverage)
10. 修改 12-interaction-rules.md (interaction coverage)
11. 修改 13-design-spec-generation.md (visual source status)
12. 修改 14-token-extraction.md (visual source status)
13. 修改 15-constrained-code-generation.md (prototype scope + coverage)
14. 修改 16-traceability-generation.md (traceability 完整性)
15. 修改 17-professional-gap-assessment.md (verdict calibration)

每修改3-5个,提交一次,测试一次。

---

## 10. Conclusion

S2-H12 Phase 1 完成。01-input-diagnosis 现在输出10域 readiness 判定,为后续 stage 提供基础。Phase 2 (S2-H12.1) 将逐个强化02-17 prompts,确保生成链路真正按资深设计执行域推导。
