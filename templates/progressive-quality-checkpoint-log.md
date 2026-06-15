# Progressive Quality Checkpoint Log (Global Template)

> **🚫 SYNTHETIC / SANITIZED ONLY** — 本模板及示例不含真实业务/客户/截图/内部链接。
> **本模板性质**:执行中渐进质量检查点的统一运行日志(引用层,非新标准)。规范见 `docs/audits/S2-H5.1-PROGRESSIVE-QUALITY-CHECKPOINTS.md`。
> **用途**:任一 skill 执行时,用本日志记录各 checkpoint 的决策、用户通知、carry-forward;交付前移交 H4 self review gate 读取。
> **checkpoint_decision 枚举**(唯一 5 个):`continue` / `continue_with_gaps` / `ask_user` / `degrade_scope` / `stop_blocked`。

---

## 1. Metadata

| 字段 | 值(填写时替换) |
|---|---|
| skill | `<填:prd2proto / uxeval / ai-analytics / ip-design / brand-creative>` |
| run_id | `run-synth-XXXX` |
| reviewer | `<reviewer-id>` |
| date | `YYYY-MM-DD` |
| total_checkpoints | 5 |
| final_checkpoint_state | `<填:最后一个 checkpoint 的 decision>` |
| handoff_to_h4 | yes / no |

---

## 2. Input Gate Summary(承接 H5)

> 引用 H5 Input Quality Gate 的 input_decision 与 ledger。

| 字段 | 值 |
|---|---|
| h5_input_decision | `<填:ready / ready_with_assumptions / needs_user_clarification / blocked_insufficient_input>` |
| carried_gaps_from_h5 | `<填:H5 GAP-XXX 清单>` |
| carried_assumptions_from_h5 | `<填:H5 ASM-XXX 清单>` |
| confidence_boundary | `<填:H5 设定的置信度上限>` |

---

## 3. Checkpoint Timeline

| checkpoint_id | stage_or_phase | checkpoint_decision | timestamp_synthetic | user_notified |
|---|---|---|---|---|
| CP-X1 | `<填>` | `<填 5 枚举>` | `T+<synthetic>` | yes / no |
| CP-X2 | `<填>` | `<填>` | `T+<synthetic>` | yes / no |
| CP-X3 | `<填>` | `<填>` | `T+<synthetic>` | yes / no |
| CP-X4 | `<填>` | `<填>` | `T+<synthetic>` | yes / no |
| CP-X5 | `<填>` | `<填>` | `T+<synthetic>` | yes / no |

---

## 4. Per-Checkpoint Record

> 每个 checkpoint 一条记录。字段见 S2-H5.1 §5。

### CP-X1
| 字段 | 值 |
|---|---|
| checkpoint_id | CP-X1 |
| stage_or_phase | `<填>` |
| expected_intermediate_artifact | `<填>` |
| required_evidence | `<填>` |
| related_kr | `<填:KR-XX>` |
| related_failure_modes | `<填:FM-XXX(仅 id,不复制正文)>` |
| quality_probe_questions | `<填:该 checkpoint 的探针问题>` |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填 5 枚举>` |
| user_notice | `<填:非 continue 决策的用户说明,见 §5>` |
| carry_forward_items | `<填:带入后续阶段的 gap/assumption>` |
| **degradation_scope_detail (S2-H7.1)** | `<填:若 decision = degrade_scope,具体降级了什么范围>` |
| **affected_outputs (S2-H7.1)** | `<填:哪些产物受影响>` |
| **user_visible_impact (S2-H7.1)** | `<填:用户会看到什么质量变化>` |
| **continue_conditions (S2-H7.1)** | `<填:什么条件下仍可继续>` |

*(CP-X2 ~ CP-X5 同结构,实际运行时按 skill 的 5 个 checkpoint 填写)*

---

## 5. User Notices

> 每个非 continue 决策必须含 5 项(S2-H5.1 §6)。

### Notice for CP-X<n>(若决策 ≠ continue)
| 字段 | 内容 |
|---|---|
| 当前发现了什么 | `<填:检测到的 gap / FM 命中>` |
| 对最终质量有什么影响 | `<填:影响哪个产出 / KR>` |
| 用户可以补什么 | `<填:对应 ask_user 的可补输入>` |
| 如果继续会以什么降级方式交付 | `<填:degrade_scope 的范围说明>` |
| 是否需要用户确认 | yes / no |

---

## 6. Carry-Forward Gaps

| gap_id | source_checkpoint | description | must_show_in_final_output |
|---|---|---|---|
| GAP-001 | CP-X<n> | `<填>` | yes |

---

## 7. Scope Degradation Log

| degrade_id | checkpoint | original_scope | degraded_scope | reason | user_confirmed |
|---|---|---|---|---|---|
| DEG-001 | CP-X<n> | `<填>` | `<填>` | `<填:命中的 major FM>` | yes / no |

---

## 8. Late-Discovered Risk Log

> 仅记录"最后阶段才可发现、前面 checkpoint 无法预警"的风险(No surprise block 例外)。

| risk_id | discovered_at | description | why_not_earlier | impact_on_h4 |
|---|---|---|---|---|
| LDR-001 | `<填:阶段>` | `<填>` | `<填:为何前面 checkpoint 无法发现>` | `<填:导致 H4 block 但属合理>` |

> 注:若 H4 出现的 blocker **不在**本日志(既非 carry-forward,也非 late-discovered),则属于"surprise block",违反 H5.1 原则,需复盘检查点切分。

---

## 9. Final Handoff To Self Review Gate

| 字段 | 内容 |
|---|---|
| all_gaps_carried | `<填:§6 全部 gap>` |
| all_assumptions_carried | `<填:H5 + checkpoint 累积的 assumption>` |
| scope_degradations | `<填:§7 全部降级>` |
| late_discovered_risks | `<填:§8 全部>` |
| recommended_h4_focus | `<填:H4 应重点核验的 FM / KR>` |
| expected_h4_decision | `<填:基于 checkpoint 状态预判 pass / degrade_with_gaps / block>` |

---

## 10. Appendix: Referenced KR / FM / Golden Template

| 类别 | 引用 |
|---|---|
| KR | `<填:本次涉及的 H1.1 KR 编号>` |
| Failure Modes | `<填:本次涉及的 H3 FM id(仅 id)>` |
| Golden Template | `<填:对应 skill 的 golden-*.md 路径>` |
| Self Review Gate | `<填:对应 skill 的 self-review-gate.md 路径>` |
| Input Quality Gate | `<填:对应 skill 的 input-quality-gate.md 路径>` |
