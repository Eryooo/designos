# Progressive Quality Checkpoints — ai-analytics

> **🚫 SYNTHETIC / SANITIZED ONLY** — 本模板及示例不含真实业务/客户/竞品价格/市场数据。
> **本模板性质**:ai-analytics 执行中渐进质量检查点(引用层,非新标准)。规范见 `docs/audits/S2-H5.1-PROGRESSIVE-QUALITY-CHECKPOINTS.md`;FM 引用 `skills/ai-analytics/eval/failure/failure-modes.md`;KR 引用 S2-H1.1;golden 引用 `skills/ai-analytics/templates/golden-analysis-output.md`。
> **当前状态**:ai-analytics = pilot,prompt-grade,无 runtime;pilot 仅稳产 design_strategy + user_persona。checkpoint 是过程探针,非真实验证。

---

## 1. Metadata

| 字段 | 值(填写时替换) |
|---|---|
| skill | ai-analytics |
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
判定逻辑见 S2-H5.1 §4.2。

---

## 3. Skill Checkpoint Map

| checkpoint_id | stage_or_phase | 检查重点 | related_kr | related_failure_modes |
|---|---|---|---|---|
| CP-A1 | input/source inventory 后 | 数据来源是否可信 | KR-A1 | FM-AIANALYTICS-001 |
| CP-A2 | competitor selection 后 | 竞品范围是否有效 | KR-A1 | FM-AIANALYTICS-007 |
| CP-A3 | strategy synthesis 后 | 结论是否由证据支撑 | KR-A2, KR-A3 | FM-AIANALYTICS-002, FM-AIANALYTICS-003 |
| CP-A4 | persona synthesis 后 | 画像是否有行为证据 | KR-A2 | FM-AIANALYTICS-006 |
| CP-A5 | final report 前 | 未验证结论是否标注 | KR-A5 | FM-AIANALYTICS-005, FM-AIANALYTICS-004 |

---

## 4. Checkpoint Records

### CP-A1 — input/source inventory 后
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | collected_data inventory |
| required_evidence | 每条 data 的 source + 可信度 |
| quality_probe_questions | 数据来源是否可追溯?是否有无来源的具体数据? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填 5 枚举>` |
| user_notice | `<填>` |
| carry_forward_items | `<填>` |

### CP-A2 — competitor selection 后
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | 竞品清单 |
| required_evidence | 竞品 ≥ 3 + 维度计划 |
| quality_probe_questions | 竞品数量是否够?维度是否足以支撑差异化? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填>` |
| user_notice | `<填>` |
| carry_forward_items | `<填>` |

### CP-A3 — strategy synthesis 后
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | design_strategy(草稿) |
| required_evidence | target_audience/business_goal + coverage |
| quality_probe_questions | 必填字段是否非空?coverage 是否真实 ≥ 0.70?结论是否有证据? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填>` |
| user_notice | `<填>` |
| carry_forward_items | `<填>` |

### CP-A4 — persona synthesis 后
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | user_persona(草稿) |
| required_evidence | goals/pain_points + 行为证据 |
| quality_probe_questions | 画像是否有行为证据?是否仅口号? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填>` |
| user_notice | `<填>` |
| carry_forward_items | `<填>` |

### CP-A5 — final report 前
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | analysis_report(草稿) |
| required_evidence | [inferred] 标注 + 不越界检查 |
| quality_probe_questions | 未验证结论是否标 [inferred]?是否越界产代码/问题清单? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填>` |
| user_notice | `<填>` |
| carry_forward_items | `<填>` |

---

## 5. Required User Notices

| checkpoint | 当前发现 | 对最终质量影响 | 用户可补什么 | 继续则如何降级 | 需确认 |
|---|---|---|---|---|---|
| CP-A<n> | `<填>` | `<填>` | `<填>` | `<填>` | yes / no |

**synthetic 示例**(CP-A2,decision=ask_user):
> 当前发现:[synthetic] 仅采集到 1 个竞品资料,不足 3 个。
> 影响:comparison_matrix 不足以支撑差异化(FM-AIANALYTICS-007)。
> 可补:再提供 2 个核心竞品资料。
> 继续则降级:差异化标 [inferred],design_strategy 置信度降低。
> 需确认:yes。

---

## 6. Carry-Forward Rules

- H5 携带的 gaps / assumptions 从 CP-A1 起持续携带。
- 每个 checkpoint 新增 gap 加入 carry_forward_items,直到 H4 显式呈现。
- continue_with_gaps 必须列出所有 carry-forward 项。

---

## 7. Degrade Scope Rules

| 触发 major FM | 降级动作 |
|---|---|
| FM-AIANALYTICS-006(画像空泛) | user_persona 降级,pain_points 标 [inferred] |
| FM-AIANALYTICS-007(竞品维度不足) | comparison_matrix 降级,缺维度标 gap |
| FM-AIANALYTICS-005(推断未标) | 推断结论加 [inferred],降 confidence |

---

## 8. Stop Blocked Rules

| 触发 blocker FM | 是否可补输入 | 决策 |
|---|---|---|
| FM-AIANALYTICS-001(编造数据,无来源) | no | stop_blocked |
| FM-AIANALYTICS-001(可补来源) | yes | ask_user |
| FM-AIANALYTICS-002(必填字段缺,可追问) | yes | ask_user |
| FM-AIANALYTICS-003(coverage 虚高) | 重评 | continue(真实重算后) |
| FM-AIANALYTICS-004(越界产出) | 删除越界内容 | continue(修正后) |

---

## 9. Handoff To H4 Self Review

| 字段 | 内容 |
|---|---|
| checkpoint_log_path | `templates/progressive-quality-checkpoint-log.md`(本 run 实例) |
| all_carried_gaps | `<填>` |
| all_assumptions | `<填>` |
| scope_degradations | `<填>` |
| late_discovered_risks | `<填:如合成阶段才暴露的数据冲突>` |
| expected_h4_decision | `<填:基于 checkpoint 预判>` |

> H4 若 block,必须能追溯到某 checkpoint 预警;否则标 late-discovered-risk。

---

## 10. Synthetic Example

> [synthetic] Acme Demo SaaS 竞品分析,目标产出 design_strategy + user_persona。

```
CP-A1: decision=continue_with_gaps
  detected_gaps: [GAP-001 行业平均无来源,需标 inferred]
CP-A2: decision=ask_user
  user_notice: "竞品仅 1 个"(见 §5 示例)
  → 用户补 2 个竞品 → 升级为 continue
CP-A3: decision=continue
CP-A4: decision=degrade_scope
  user_notice: "用户访谈缺,pain_points 标 [inferred] 降置信度"
CP-A5: decision=continue_with_gaps
  carry_forward: GAP-001
final handoff: 1 gap carried, expected_h4=degrade_with_gaps
```

> 产品价值:用户在 CP-A2(竞品选择阶段)就被告知竞品不足,而非合成完策略后才发现差异化无依据。
