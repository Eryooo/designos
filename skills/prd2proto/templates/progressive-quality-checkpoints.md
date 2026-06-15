# Progressive Quality Checkpoints — prd2proto

> **🚫 SYNTHETIC / SANITIZED ONLY** — 本模板及示例不含真实业务/客户/PRD。
> **本模板性质**:prd2proto 执行中渐进质量检查点(引用层,非新标准)。规范见 `docs/audits/S2-H5.1-PROGRESSIVE-QUALITY-CHECKPOINTS.md`;FM 引用 `skills/prd2proto/eval/failure/failure-modes.md`;KR 引用 S2-H1.1;golden 引用 `skills/prd2proto/templates/golden-prd2proto-output.md`。
> **当前状态**:prd2proto = pilot,runtime-grade。checkpoint 是过程探针,非真实验证。

---

## 1. Metadata

| 字段 | 值(填写时替换) |
|---|---|
| skill | prd2proto |
| run_id | `run-synth-XXXX` |
| reviewer | `<reviewer-id>` |
| date | `YYYY-MM-DD` |
| total_checkpoints | 5 |
| handoff_to_h4 | yes / no |

---

## 2. Checkpoint Decision Enum

唯一 5 枚举:
```
continue
continue_with_gaps
ask_user
degrade_scope
stop_blocked
```

判定逻辑见 S2-H5.1 §4.2(blocker 不可修 → stop_blocked;blocker 可补输入 → ask_user;major 影响关键产出 → degrade_scope;gap 不阻断 → continue_with_gaps;无风险 → continue)。

---

## 3. Skill Checkpoint Map

| checkpoint_id | stage_or_phase | 检查重点 | related_kr | related_failure_modes |
|---|---|---|---|---|
| CP-P1 | input-diagnosis 完成后 | 输入缺口与 assumptions | KR-P1, KR3.2 | FM-PRD2PROTO-005 |
| CP-P2 | requirement_inventory 完成后 | 需求完整度和目标清晰度 | KR-P1 | FM-PRD2PROTO-002, FM-PRD2PROTO-005 |
| CP-P3 | design_objectives / user_task_map 后 | 策略与任务链是否成立 | KR-P4 | FM-PRD2PROTO-002 |
| CP-P4 | state_matrix / traceability 前 | 状态覆盖是否足够 | KR-P4 | FM-PRD2PROTO-008, FM-PRD2PROTO-002 |
| CP-P5 | constrained-code-generation 前 | 是否允许进入生成阶段 | KR-P2, KR-P3 | FM-PRD2PROTO-001, FM-PRD2PROTO-003 |

---

## 4. Checkpoint Records

### CP-P1 — input-diagnosis 完成后
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | requirement_inventory(草稿) |
| required_evidence | completeness_assessment.overall_score + gaps |
| quality_probe_questions | PRD 缺失是否全记入 gaps?业务目标是否量化? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填 5 枚举>` |
| user_notice | `<填:若 ask_user/degrade/stop 则说明>` |
| carry_forward_items | `<填:带入后续的 gap/assumption>` |

### CP-P2 — requirement_inventory 完成后
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | requirement_inventory(定稿) |
| required_evidence | readiness_decision.decision |
| quality_probe_questions | completeness ≥ 0.65?业务目标/用户角色是否可追溯? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填>` |
| user_notice | `<填>` |
| carry_forward_items | `<填>` |
| **degradation_scope_detail (S2-H7.1)** | `<填:若 decision = degrade_scope,具体降级了什么范围>` |
| **affected_outputs (S2-H7.1)** | `<填:哪些产物受影响>` |
| **user_visible_impact (S2-H7.1)** | `<填:用户会看到什么质量变化>` |
| **continue_conditions (S2-H7.1)** | `<填:什么条件下仍可继续>` |

### CP-P3 — design_objectives / user_task_map 后
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | design_objectives + user_task_map |
| required_evidence | 目标↔任务映射 + decision_trace |
| quality_probe_questions | 每个业务目标是否有对应任务?edge_tasks 是否覆盖? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填>` |
| user_notice | `<填>` |
| carry_forward_items | `<填>` |
| **degradation_scope_detail (S2-H7.1)** | `<填:若 decision = degrade_scope,具体降级了什么范围>` |
| **affected_outputs (S2-H7.1)** | `<填:哪些产物受影响>` |
| **user_visible_impact (S2-H7.1)** | `<填:用户会看到什么质量变化>` |
| **continue_conditions (S2-H7.1)** | `<填:什么条件下仍可继续>` |

### CP-P4 — state_matrix / traceability 前
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | IA + page-flow + component-strategy |
| required_evidence | 状态枚举 + traceability 链路 |
| quality_probe_questions | 状态矩阵是否覆盖 loading/empty/error/权限态?关键决策可追溯? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填>` |
| user_notice | `<填>` |
| carry_forward_items | `<填>` |
| **degradation_scope_detail (S2-H7.1)** | `<填:若 decision = degrade_scope,具体降级了什么范围>` |
| **affected_outputs (S2-H7.1)** | `<填:哪些产物受影响>` |
| **user_visible_impact (S2-H7.1)** | `<填:用户会看到什么质量变化>` |
| **continue_conditions (S2-H7.1)** | `<填:什么条件下仍可继续>` |

### CP-P5 — constrained-code-generation 前
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | design_spec + design_tokens |
| required_evidence | tokens 完整性 + 组件库约束 |
| quality_probe_questions | 是否所有样式可引用 token?是否会出现硬编码? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填>` |
| user_notice | `<填>` |
| carry_forward_items | `<填>` |
| **degradation_scope_detail (S2-H7.1)** | `<填:若 decision = degrade_scope,具体降级了什么范围>` |
| **affected_outputs (S2-H7.1)** | `<填:哪些产物受影响>` |
| **user_visible_impact (S2-H7.1)** | `<填:用户会看到什么质量变化>` |
| **continue_conditions (S2-H7.1)** | `<填:什么条件下仍可继续>` |

---

## 5. Required User Notices

> 每个非 continue 决策必须含 5 项(S2-H5.1 §6)。

| checkpoint | 当前发现 | 对最终质量影响 | 用户可补什么 | 继续则如何降级 | 需确认 |
|---|---|---|---|---|---|
| CP-P<n> | `<填>` | `<填>` | `<填>` | `<填>` | yes / no |

**synthetic 示例**(CP-P2,decision=ask_user):
> 当前发现:[synthetic] PRD 未给量化业务目标。
> 影响:design-objectives 将无锚点,traceability 弱。
> 可补:一句话核心 KPI(如"3 个月试用转化 ≥ 20%")。
> 继续则降级:按通用目标推断,标 [inferred],置信度 ≤ 0.6。
> 需确认:yes。

---

## 6. Carry-Forward Rules

- H5 input gate 携带的 gaps / assumptions 必须在 CP-P1 起持续携带。
- 任一 checkpoint 新增的 gap 加入 carry_forward_items,直到 H4 显式呈现。
- continue_with_gaps 决策必须列出所有 carry-forward 项。

---

## 7. Degrade Scope Rules

| 触发 major FM | 降级动作 |
|---|---|
| FM-PRD2PROTO-005(静默脑补) | 缺失信息标 [inferred],降低 confidence |
| FM-PRD2PROTO-007(stage 链断) | 降级"完整 18-stage"声明为"已产出 N stage" |
| FM-PRD2PROTO-008(状态覆盖不全) | 降级状态矩阵为"覆盖核心态,边缘态标 gap" |

> degrade_scope 必须在 §5 user_notice 告知用户降级范围。

---

## 8. Stop Blocked Rules

| 触发 blocker FM | 是否可补输入 | 决策 |
|---|---|---|
| FM-PRD2PROTO-001(Schema 违约,无法修复) | no | stop_blocked |
| FM-PRD2PROTO-002(业务目标缺,可追问) | yes | ask_user |
| FM-PRD2PROTO-003(代码宪法,生成前可拦) | 阶段内可修 | continue 或 degrade |
| FM-PRD2PROTO-004(Honesty 违反) | 修正口径 | continue(修正后) |

---

## 9. Handoff To H4 Self Review

| 字段 | 内容 |
|---|---|
| checkpoint_log_path | `templates/progressive-quality-checkpoint-log.md`(本 run 实例) |
| all_carried_gaps | `<填>` |
| all_assumptions | `<填>` |
| scope_degradations | `<填>` |
| late_discovered_risks | `<填:仅 code-generation 才暴露的约束冲突等>` |
| expected_h4_decision | `<填:基于 checkpoint 预判 pass / degrade_with_gaps / block>` |

> H4 若 block,必须能追溯到某 checkpoint 预警;否则标 late-discovered-risk。

---

## 10. Synthetic Example

> [synthetic] Acme Demo 后台 PRD,mode=pm。

```
CP-P1: decision=continue_with_gaps
  detected_gaps: [GAP-001 业务目标未量化]
  carry_forward: GAP-001
CP-P2: decision=ask_user
  user_notice: "缺量化 KPI,请补充"(见 §5 示例)
  → 用户补充"试用转化 ≥ 20%" → 升级为 continue
CP-P3: decision=continue
CP-P4: decision=continue_with_gaps
  detected_gaps: [GAP-002 部分页面缺权限态]
  carry_forward: GAP-002
CP-P5: decision=continue
final handoff: 2 gaps carried, expected_h4=pass_with_minor_warnings
```

> 产品价值:用户在 CP-P2(执行早期)就补齐了关键目标,而非跑完 18 stage 才被 H4 拒绝。
