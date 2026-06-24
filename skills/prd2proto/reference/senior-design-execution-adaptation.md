# prd2proto Adaptation — Senior Design Execution Standard

> **Status**: pilot | **Source**: `knowledge/product/senior-design-execution.md`
> **Purpose**: prd2proto 如何消费共享资深产品设计执行标准(10域)的 skill-specific adaptation。
> **Scope**: 映射10域到prd2proto stages、定义PRD-only降级规则、定义prototype生成范围判定、防止过度声明。
> **Not a copy**: 本文档不复制shared knowledge正文,只做skill-specific adaptation和stage mapping。

---

## 1. Ten-Domain to Stage Mapping

| Domain | prd2proto Stages | Enforcement Point | Degradation Rule |
|---|---|---|---|
| 1. Problem Framing | input-diagnosis, design-objectives | input-quality-gate | PRD缺业务问题/用户问题时 → 标注inferred,降低confidence |
| 2. Input / PRD Critique | input-diagnosis | input-quality-gate | 识别PRD类型(functional/flow/page/visual),判断can_generate_prototype,输出missing_for_X |
| 3. Goal Decomposition | design-objectives | progressive-checkpoint-1 | 缺业务目标时必须标注inferred+assumption,不得静默补全 |
| 4. User / Task Modeling | user-task-modeling | progressive-checkpoint-2 | 缺用户角色时可推断,但edge tasks必须标gap,不得over-claim coverage |
| 5. Domain / Product Model | product-archetype | progressive-checkpoint-2 | 必须区分product_foundation/core_module/representative_scenario/example_only;example不得主导IA |
| 6. Journey / Flow / State | business-flow-modeling, user-journey-mapping, state-matrix | progressive-checkpoint-3 | 缺异常流程/权限流程/中断状态时必须标gap;只有happy path不得称完整 |
| 7. IA / Navigation / Surface Model | information-architecture, page-flow | progressive-checkpoint-3 | 必须先有product model;experience_surfaces/shell/context/history必须明确;不得function→page 1:1 flatten |
| 8. Page / Interaction Design | page-structure, component-strategy, interaction-rules | progressive-checkpoint-4 | 必须覆盖loading/empty/error/permission;组件选择必须可追溯 |
| 9. Visual / Design System / Accessibility | design-spec-generation, token-extraction | progressive-checkpoint-4 | 无visual source时visual_fidelity_mode=structural_only;component library≠visual direction |
| 10. Prototype / Traceability / Critique | constrained-code-generation, traceability-generation, professional-gap-assessment | self-review-gate | liveness/smoke pass≠design quality pass;coverage低/critical gaps>0时不得review-ready |

---

## 2. PRD-Only Input Degradation Rules

当输入是PRD-only(无design spec/screenshots/DSL/tokens)时:

### 2.1 Input Type vs. Output Capability

| Input Granularity | Can Generate | Cannot Generate | Must Flag |
|---|---|---|---|
| MRD / Roadmap / Strategy Brief | problem framing, goal tree, high-level product model | clickable prototype, IA, page structure | not_sufficient_for_prototype |
| Functional PRD | problem framing, goals, product model, user tasks, IA skeleton | complete page structure, visual-ready prototype | partial_clickable_prototype |
| Flow-Detailed PRD | above + journey, flow, state coverage | visual review-ready prototype | missing_visual_evidence |
| Page-Spec PRD | above + page structure, component strategy | visual review-ready prototype | missing_visual_evidence |
| Visual-Ready Input | all domains | N/A | N/A (sufficient) |

### 2.2 Forced Degradation Triggers

**Trigger**: PRD缺产品foundation描述,只有一个详细example flow。
**Action**: 不得让example flow主导整个IA;必须标注`example_dominance_risk`,输出`product_foundation_inferred`,降级为`partial_clickable_prototype`。

**Trigger**: PRD缺视觉证据(screenshots/design system/brand tokens/reference UI)。
**Action**: 不得宣称`visual_review_ready`;必须标注`visual_fidelity_mode: structural_only`,输出`missing_visual_evidence`。

**Trigger**: PRD缺异常流程/权限流程/中断状态/empty state描述。
**Action**: state-matrix必须标注`inferred_states`,输出`state_coverage_gaps`,不得宣称`interaction_complete`。

**Trigger**: PRD缺IA rationale,只有flat功能清单。
**Action**: information-architecture必须标注`ia_inferred_from_features`,输出`navigation_rationale_missing`,不得宣称`senior_reviewable_ia`。

---

## 3. Prototype Generation Capability Matrix

| Input Completeness | Generated Prototype Fidelity | Allowed Verdict | Forbidden Verdict |
|---|---|---|---|
| concept/strategy-only | N/A | blocked_insufficient_input | any prototype claim |
| functional PRD | product model + IA skeleton + structural pages | design_reasoning_ready | clickable_prototype_ready |
| flow-detailed PRD | above + clickable flows + state coverage | clickable_prototype_ready_with_gaps | senior_review_ready |
| page-spec PRD | above + component strategy + interaction rules | clickable_prototype_ready_with_minor_gaps | visual_review_ready |
| visual-ready input | above + visual tokens + brand language | senior_review_ready_with_gaps | production_candidate |

**Absolute Rules**:
1. `liveness_check: pass` ≠ `design_quality: pass`
2. `smoke_test: pass` ≠ `requirement_coverage: sufficient`
3. `component_library: consistent` ≠ `visual_direction: established`
4. `clickable: true` ≠ `senior_reviewable: true`

---

## 4. Not-Allowed Claims (prd2proto-specific)

继承 `knowledge/product/senior-design-execution.md` 的 `not_allowed_claims`,并补充prd2proto专属禁止:

**禁止在PRD-only输入下宣称**:
- "完整产品原型"(只能说"基于PRD的结构原型"或"部分可点击原型")
- "视觉可评审"(visual_review_ready)
- "资深设计师可评审"(senior_reviewable,除非10域全覆盖+有visual evidence)
- "生产就绪"(production_candidate)
- "完全自动化生成"(prompt-grade需人工复核)

**禁止行为**:
- PRD直转页面,跳过problem framing / goal decomposition / product model
- 把某个详细example flow放大成整个产品主架构
- 把功能清单1:1映射为flat sitemap,无IA rationale
- 把component library default当成visual direction established
- 把liveness/smoke pass当作design quality证明
- 在缺visual source时输出visual tokens并宣称"已提取品牌token"
- 在coverage<80%或critical gaps>0时判定review-ready

---

## 5. Quality Gate Integration

### 5.1 Input Quality Gate Enhancement

`skills/prd2proto/templates/input-quality-gate.md` 必须新增:

**Section: Ten-Domain Readiness Assessment**

| Domain | Input Evidence | Readiness | Can Infer | Degradation If Missing |
|---|---|---|---|---|
| Problem Framing | 业务问题/用户问题/成功指标 | ready / partial / missing | partial | 降低confidence,标inferred |
| Input Critique | PRD type/completeness/granularity | ready / partial / missing | no | block if missing |
| Goal Decomposition | 业务目标/产品目标/用户目标 | ready / partial / missing | partial | 标inferred+assumption |
| User/Task Modeling | 用户角色/主任务 | ready / partial / missing | yes | edge tasks标gap |
| Domain/Product Model | 产品类型/核心对象/模块关系 | ready / partial / missing | yes | example不得主导IA |
| Journey/Flow/State | 主流程/异常流程/状态 | ready / partial / missing | partial | 只有happy path→标gap |
| IA/Navigation/Surface | sitemap rationale/导航层级 | ready / partial / missing | yes | flat功能清单→标inferred |
| Page/Interaction | 页面结构/组件/交互/状态 | ready / partial / missing | yes | loading/error/empty标gap |
| Visual/Design System | screenshots/tokens/design system | ready / partial / missing | no | 缺失→structural_only |
| Prototype/Traceability | 可追溯性要求 | ready / partial / missing | yes | 无→降级verdict |

**Readiness Decision Logic**:
- `design_reasoning_ready`: 1-5域 ready, 6-10域 partial 可接受
- `clickable_prototype_ready_with_gaps`: 1-8域 ready, 9域 partial, 10域 partial
- `senior_review_ready`: 1-10域 ready, 9域需有visual evidence

### 5.2 Self Review Gate Enhancement

`skills/prd2proto/templates/self-review-gate.md` 必须新增:

**Section: Ten-Domain Self Critique**

| Domain | Delivered Artifact | Quality Check | Pass Criteria | Blocker If Failed |
|---|---|---|---|---|
| 1. Problem Framing | design_objectives.problem_statement | 是否明确业务问题/用户问题/成功指标? | 有且可追溯 | yes |
| 2. Input Critique | input_diagnosis.readiness_decision | 是否判断PRD type/completeness? | 有decision | yes |
| 3. Goal Decomposition | design_objectives.goal_tree | 是否拆解BG/PG/UG? | 有且标inferred | no(标gap) |
| 4. User/Task Modeling | user_task_map.roles/tasks | 是否建模用户角色与主任务? | 有且标edge gap | no(标gap) |
| 5. Domain/Product Model | product_archetype.foundation/modules | 是否区分foundation/example? | 有且example未主导IA | yes |
| 6. Journey/Flow/State | state_matrix.states | 是否覆盖异常/权限/中断? | 至少标gap | no(标gap) |
| 7. IA/Navigation/Surface | information_architecture.rationale | 是否有IA rationale? | 有且非flat 1:1 | yes |
| 8. Page/Interaction | page_structure.states | 是否覆盖loading/error/empty? | 至少标gap | no(标gap) |
| 9. Visual/Design System | design_spec.visual_source_status | 是否有visual evidence? | 有或标structural_only | yes(若over-claim) |
| 10. Prototype/Traceability | traceability_map.coverage | 是否有coverage/gap/verdict? | 有且verdict≤evidence | yes |

**Verdict Calibration**:
- `partial_clickable_prototype`: 可接受(诚实边界)
- `clickable_prototype_ready_with_gaps`: 需1-8域pass, 9域structural, 10域有traceability
- `clickable_prototype_review_ready_with_minor_gaps`: 需1-8域pass, P0 coverage≥90%, critical gaps=0, 9域partial, 10域完整
- `senior_review_ready`: 需1-10域全pass, 9域有visual evidence, coverage≥80%, critical gaps=0

---

## 6. Failure Mode Supplements

prd2proto必须补充以下failure modes(见§7):

- FM-PRD2PROTO-009: PRD-to-Page Shortcut
- FM-PRD2PROTO-010: Example Flow Dominance
- FM-PRD2PROTO-011: Missing Problem Framing
- FM-PRD2PROTO-012: Missing Product/Domain Model
- FM-PRD2PROTO-013: IA Unsupported By Evidence
- FM-PRD2PROTO-014: State Coverage Illusion
- FM-PRD2PROTO-015: Clickable Prototype Verdict Inflation
- FM-PRD2PROTO-016: Visual Polish Overclaim

每条需包含: id/severity/detection_signal/trigger_condition/related_kr/source_reference/self_review_question/remediation/not_allowed_claims。

---

## 7. Test Coverage Requirements

prd2proto tests必须覆盖:

1. `test_knowledge_manifest_references_senior_design_execution.py`: 验证`product.senior-design-execution` id存在且stage_mapping完整。
2. `test_ten_domain_stage_mapping.py`: 验证reference中10域→stages mapping存在。
3. `test_input_gate_ten_domain_readiness.py`: 验证input gate含10域readiness assessment。
4. `test_self_review_gate_ten_domain_critique.py`: 验证self review gate含10域self critique。
5. `test_failure_modes_senior_execution_gaps.py`: 验证FM-009~016存在且含required fields。
6. `test_prompts_no_prd_to_page_shortcut.py`: 验证prompts-v2不含"直接生成完整页面/完整原型"的过度承诺。
7. `test_synthetic_prd_only_degradation.py`: 合成PRD-only case,验证缺IA/状态/视觉时输出gap/degrade,不得pass为senior_review_ready。

---

## 8. Usage in Prompts

prompts-v2各stage消费本adaptation的方式:

**Stage 01 input-diagnosis**:
- 引用Domain 1-2
- 判断PRD type, completeness, can_generate_prototype
- 输出missing_for_structure/clickable/visual/production

**Stage 02 design-objectives**:
- 引用Domain 1,3
- 必须输出problem_statement(业务问题/用户问题/成功指标)
- 必须输出goal_tree(BG/PG/UG),标注inferred

**Stage 03 product-archetype**:
- 引用Domain 5
- 必须区分product_foundation/core_module/representative_scenario/example_only
- 禁止example主导IA

**Stage 04 user-task-modeling**:
- 引用Domain 4
- 必须输出roles/tasks, edge tasks标gap

**Stage 05-06 business-flow / user-journey**:
- 引用Domain 6
- 必须覆盖异常/权限/中断,缺失标gap

**Stage 07 information-architecture**:
- 引用Domain 7
- 必须输出IA rationale, experience_surfaces, shell, 禁止flat 1:1

**Stage 08-12 page-flow / page-structure / component-strategy / state-matrix / interaction-rules**:
- 引用Domain 6,8
- 必须覆盖loading/error/empty/permission, 标gap

**Stage 13-14 design-spec / token-extraction**:
- 引用Domain 9
- 无visual source时visual_fidelity_mode=structural_only

**Stage 15 constrained-code-generation**:
- 引用Domain 10
- 先实现product foundation,再代表流程,标coverage

**Stage 16-17 traceability / gap-assessment**:
- 引用Domain 10
- 输出coverage/gap/verdict, verdict≤evidence

---

## 9. Migration Path

本adaptation接入后:

**Phase 1 (S2-H11-B)**: 接入knowledge-manifest, 建立reference, 强化gate/failure mode/test, 不修runtime。
**Phase 2 (S2-H12)**: 修改prompts-v2,强制10域推导链路, 不跳步。
**Phase 3 (S2-H13)**: runtime强制gate, 多case验证, 稳定senior-reviewable输出。

当前batch只做Phase 1。

---

## 10. References

- Shared Knowledge Source: `knowledge/product/senior-design-execution.md`
- Audit Report: `docs/audits/S2-H11-0-SENIOR-PRODUCT-DESIGN-BENCHMARK.md`
- prd2proto Knowledge Manifest: `skills/prd2proto/knowledge-manifest.yaml`
- Input Quality Gate: `skills/prd2proto/templates/input-quality-gate.md`
- Self Review Gate: `skills/prd2proto/templates/self-review-gate.md`
- Failure Modes: `skills/prd2proto/eval/failure/failure-modes.md`
- Progressive Checkpoints: `skills/prd2proto/templates/progressive-quality-checkpoints.md`
