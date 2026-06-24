# Self Review Gate — prd2proto

> **🚫 SYNTHETIC / SANITIZED ONLY** — 本模板及示例不含真实业务/客户/截图/内部链接。
> **本模板性质**:交付前自检门(引用层,非新标准)。阈值引用 S2-H1/H1.1,结构引用 S2-H2,failure mode 引用 `skills/prd2proto/eval/failure/failure-modes.md`,约束引用 `skills/prd2proto/constitution.md` + `PILOT-BOUNDARY.md`。
> **执行顺序**:见 `docs/audits/S2-H4-SELF-REVIEW-GATE.md` §3(8 步)。
> **当前状态**:prd2proto = pilot,runtime-grade。本 gate 通过 ≠ 已达资深水平。

---

## 1. Metadata

| 字段 | 值(填写时替换) |
|---|---|
| skill | prd2proto |
| run_id | `run-synth-XXXX` |
| reviewer | `<reviewer-id>` |
| date | `YYYY-MM-DD` |
| input_summary | `[synthetic] Acme Demo PRD,mode=pm` |
| output_artifact_paths | `prd2proto-out/<run_id>/01..17 + prototype_code/` |
| delivery_decision | `<填 §9 结论>` |

---

## 2. Minimum Delivery Line KR Check(全局)

| kr_id | requirement | evidence | status | gap_if_any |
|---|---|---|---|---|
| KR1.1 | 最低交付线(中阶可用)全过 | `<填:rubric self-eval 结果>` | pass / warn / fail / not_applicable | |
| KR1.2 | 一票否决项命中数 = 0 | `<填:§4 结果>` | pass / fail | |
| KR3.1 | 不可宣称项命中数 = 0 | `<填:§8 结果>` | pass / fail | |
| KR3.3 | 关键决策可追溯率 = 100% | `<填:traceability_map 覆盖>` | pass / warn / fail | |

---

## 3. Skill-Specific KR Check

| kr_id | requirement | evidence | status | gap_if_any |
|---|---|---|---|---|
| KR-P1 | 18 stage 全产出(designer-dsl 17) | `<填>` | pass / warn / fail / not_applicable | |
| KR-P2 | schema 真 blocking 通过率达标 | `<填>` | pass / warn / fail | |
| KR-P3 | code_constraint_gate 触发后修正率 | `<填>` | pass / warn / fail | |
| KR-P4 | traceability 关键决策追溯率 | `<填>` | pass / warn / fail | |
| KR-P5 | artifact-base 继承 7/7 | `<填:已实证 7/7>` | pass | |

---

## 4. One-Vote Veto Check

| veto_id | description | triggered | evidence | decision |
|---|---|---|---|---|
| V1 | Schema 违约交付 | yes / no / unknown | `<填>` | triggered=yes → block |
| V2 | Traceability 断裂 | yes / no / unknown | `<填>` | triggered=yes → block |
| V3 | 代码宪法违反 | yes / no / unknown | `<填>` | triggered=yes → block |
| V4 | Honesty 违反 | yes / no / unknown | `<填>` | triggered=yes → block |

> 任一 triggered=yes → final delivery_decision **必须 block**。

---

## 5. Failure Mode Self Review

> 引用 `skills/prd2proto/eval/failure/failure-modes.md`(仅 id/severity/self_review_question,不复制正文)。

| fm_id | severity | self_review_question | answer | evidence | remediation_if_failed |
|---|---|---|---|---|---|
| FM-PRD2PROTO-001 | blocker | 当前 stage artifact 是否通过 schema 校验且失败时已阻断进入下一 stage? | pass / warn / fail / unknown | `<填>` | 补字段/修枚举,重过校验 |
| FM-PRD2PROTO-002 | blocker | 关键设计决策是否在 traceability_map 链接到上游 artifact_id? | pass / warn / fail / unknown | `<填>` | 补 decision_trace |
| FM-PRD2PROTO-003 | blocker | 生成代码是否全引用 token+组件库,无硬编码/非组件库 div? | pass / warn / fail / unknown | `<填>` | code-constraint-gate 重生成 |
| FM-PRD2PROTO-004 | blocker | 输出是否命中 not_allowed_claims,命中是否已改诚实表述? | pass / warn / fail / unknown | `<填>` | 改边界表述 |
| FM-PRD2PROTO-005 | major | PRD 缺失是否全记入 gaps,而非静默脑补? | pass / warn / fail / unknown | `<填>` | 缺失记入 gaps |
| FM-PRD2PROTO-006 | major | 推断是否进 inferred_fields,assumptions 带 risk_if_wrong? | pass / warn / fail / unknown | `<填>` | 补标注 |
| FM-PRD2PROTO-007 | major | 18 stage 是否全产出,跳过的是否已标 gap 并降级声明? | pass / warn / fail / unknown | `<填>` | 补 stage 或标 gap |
| FM-PRD2PROTO-008 | minor | 状态矩阵是否覆盖 loading/empty/error/权限态? | pass / warn / fail / unknown | `<填>` | 补状态或标 gap |

---

## 6. Golden Template Coverage Check

> 引用 `skills/prd2proto/templates/golden-prd2proto-output.md` 必填章节。

| section | required | present | evidence_path | gap_if_any |
|---|---|---|---|---|
| 输入前提 | yes | yes / no | `<填>` | |
| 输出 artifact 列表(18) | yes | yes / no | `<填>` | |
| 必填章节(artifact-base 元数据) | yes | yes / no | `<填>` | |
| 字段级要求(quality_gates 等) | yes | yes / no | `<填>` | |
| traceability 规范 | yes | yes / no | `<填>` | |
| professional_gap_report | yes | yes / no | `<填>` | |

---

## 7. Gap / Assumption / Confidence / Traceability Check

| 检查项 | requirement | evidence | gap |
|---|---|---|---|
| gaps 显式标注 | 缺失/模糊已进 gaps 数组 | `<填>` | |
| assumptions 有 confidence | 每条 assumption 带 risk_if_wrong | `<填>` | |
| inferred_fields 有来源 | 推断字段列入 inferred_fields + 依据 | `<填>` | |
| 关键结论可追溯 | decision_trace evidence 非空 | `<填>` | |

---

## 8. Not Allowed Claims Check

> 引用 FM-PRD2PROTO-004 的 not_allowed_claims。

| 禁止声明 | 是否命中 | 处置 |
|---|---|---|
| "已达资深交互设计师水平" | yes / no | 命中 → block |
| "生成可直接用于生产的代码" | yes / no | 命中 → block |
| 全自动无人值守 / 无需人工复核 | yes / no | 命中 → block |
| "production ready" | yes / no | 命中 → block |

> 任一命中 → delivery_decision = block。

---

## 9. Delivery Decision

```
delivery_decision: <pass | pass_with_minor_warnings | degrade_with_gaps | block>
```

判定理由(按 §4 + §9.1 规则):
- `<填:命中的 blocker/veto → block;major → degrade_with_gaps;仅 minor → pass_with_minor_warnings;全过 → pass>`

next_actions:
- `<填:需返工/补充的具体动作清单>`

---

## 9.1. Ten-Domain Self Critique (S2-H11-B)

> 引用 `knowledge/product/senior-design-execution.md` 10个资深产品设计执行域,检查产出是否覆盖各域及质量标准。
> 对应 `skills/prd2proto/reference/senior-design-execution-adaptation.md` §5.2 Self Review Gate Enhancement。

| Domain | Delivered Artifact | Quality Check Question | Pass Criteria | Evidence | Blocker If Failed |
|---|---|---|---|---|---|
| 1. Problem Framing | `design_objectives.problem_statement` | 是否明确业务问题/用户问题/成功指标? | 有且可追溯 | `<填>` | yes |
| 2. Input / PRD Critique | `input_diagnosis.readiness_decision` | 是否判断PRD type/completeness/can_generate_prototype? | 有decision + missing_for_X | `<填>` | yes |
| 3. Goal Decomposition | `design_objectives.goal_tree` | 是否拆解BG/PG/UG? 推断的是否标inferred? | 有且标inferred+assumption | `<填>` | no(标gap) |
| 4. User / Task Modeling | `user_task_map.roles/tasks` | 是否建模用户角色与主任务? edge tasks是否标gap? | 有且edge gap标注 | `<填>` | no(标gap) |
| 5. Domain / Product Model | `product_archetype.foundation/modules` | 是否区分product_foundation/core_module/representative_scenario/example? example是否主导IA? | 有且example未主导IA | `<填>` | yes |
| 6. Journey / Flow / State | `state_matrix.states` | 是否覆盖异常/权限/中断/边缘态? 只有happy path的是否标gap? | 至少标state_coverage_gaps | `<填>` | no(标gap) |
| 7. IA / Navigation / Surface | `information_architecture.ia_rationale` | 是否有IA rationale? 是否识别experience_surfaces? 是否flat功能1:1页面? | 有rationale且非flat 1:1 | `<填>` | yes |
| 8. Page / Interaction Design | `page_structure.state_coverage` | 是否覆盖loading/error/empty/permission? 组件选择是否可追溯? | 至少标gap | `<填>` | no(标gap) |
| 9. Visual / Design System / Accessibility | `design_spec.visual_source_status` | 是否有visual evidence(screenshots/design system/tokens)? 无时是否标structural_only? component library是否被误认为visual direction? | 有visual source 或 标structural_only | `<填>` | yes(若over-claim) |
| 10. Prototype / Traceability / Critique | `traceability_map.coverage`, `professional_gap_report.verdict` | 是否有coverage/gap report? verdict是否≤evidence? liveness pass是否被当作design quality? | 有且verdict≤evidence | `<填>` | yes |

**Verdict Calibration Matrix (基于10域)**:

| Verdict | Domain 1-5 | Domain 6-8 | Domain 9 | Domain 10 | Coverage | Critical Gaps | Allowed? |
|---|---|---|---|---|---|---|---|
| `partial_clickable_prototype` | any | any | any | any | any | any | ✅ always(诚实边界) |
| `clickable_prototype_ready_with_gaps` | pass | pass | structural_only | has traceability | ≥60% | ≤3 | ✅ |
| `clickable_prototype_ready_with_minor_gaps` | pass | pass | partial | complete | ≥80% | 0 | ✅ |
| `clickable_prototype_review_ready_with_minor_gaps` | pass | pass | partial | complete | ≥90% | 0 | ✅ (P0 only) |
| `senior_review_ready` | pass | pass | has visual evidence | complete | ≥80% | 0 | ✅ |
| `visual_review_ready` | pass | pass | has visual evidence | complete | ≥90% | 0 | ✅ |
| `production_candidate` | N/A | N/A | N/A | N/A | N/A | N/A | ❌ forbidden(prd2proto=pilot) |

**Blocker Detection (来自 senior-design-execution-adaptation.md §3 Absolute Rules + FM-009/011/015)**:

| Blocker Condition | Detection Signal | Delivery Decision | Remediation |
|---|---|---|---|
| PRD直转页面(FM-009) | design_objectives缺problem_statement; product_archetype缺foundation; IA无rationale | block | 补problem framing/goal/product model/IA rationale |
| 缺Problem Framing(FM-011) | design_objectives缺problem_statement且未标inferred | block | 补problem_statement或标inferred+low confidence |
| Example主导IA(FM-010) | representative_scenario被提升为main navigation; product_foundation被边缘化 | degrade | 区分foundation/example; 标example_dominance_risk |
| IA无rationale(FM-013) | IA直接从功能清单生成; 缺experience_surfaces; flat 1:1 | degrade | 补ia_rationale; 识别experience_surfaces |
| Verdict Inflation(FM-015) | liveness pass→quality pass; coverage<80%且critical gaps>0→review-ready; 缺visual evidence→visual_review_ready | block | 校准verdict; liveness≠quality; clickable≠senior-reviewable |
| Visual Overclaim(FM-016) | 无screenshots/tokens但声称visual_review_ready; component library→visual direction | degrade | 标visual_source_status=none, structural_only |

**Not-Allowed Claims (补充 §8)**:

- 不得在Domain 1缺失时宣称"基于明确问题定义的设计"
- 不得在Domain 5缺失时宣称"完整产品架构"
- 不得在Domain 7 flat 1:1时宣称"资深IA决策"
- 不得在Domain 9缺visual evidence时宣称"visual review ready"
- 不得在Domain 10 liveness pass时宣称"design quality pass"
- 不得在coverage<80%或critical gaps>0时宣称"senior review ready"

**Ten-Domain Summary**:

| Field | Value |
|---|---|
| ten_domain_pass_count | `<填:1-10域中pass数量>` / 10 |
| blocker_domains | `<填:failed且blocker=yes的域,如"1,5,7,10">` |
| gap_domains | `<填:failed但可标gap的域,如"3,4,6,8">` |
| verdict_supported_by_evidence | yes / no |
| verdict_inflation_detected | yes / no(若liveness→quality/clickable→senior/缺visual→visual ready) |

---

## 10. Reviewer Notes

- `<填:审查备注,不新增标准,不写真实业务信息>`
