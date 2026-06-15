# Progressive Quality Checkpoints — uxeval

> **🚫 SYNTHETIC / SANITIZED ONLY** — 本模板及示例不含真实业务/客户/截图/账号/内部 URL。
> **本模板性质**:uxeval 执行中渐进质量检查点(引用层,非新标准)。规范见 `docs/audits/S2-H5.1-PROGRESSIVE-QUALITY-CHECKPOINTS.md`;FM 引用 `skills/uxeval/eval/failure/failure-modes.md`;KR 引用 S2-H1.1;golden 引用 `skills/uxeval/templates/golden-evaluation-report.md`。
> **当前状态**:uxeval = beta,prompt-grade,无 runtime;`gate:` 是暂停门非 kernel quality_gates。checkpoint 是过程探针,非真实验证。

---

## 1. Metadata

| 字段 | 值(填写时替换) |
|---|---|
| skill | uxeval |
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
| CP-U1 | evidence_planning 后 | 关键页面/状态覆盖是否足够 | KR-U1 | FM-UXEVAL-007 |
| CP-U2 | screenshot/web collection 后 | 证据质量和可读性 | KR-U1, KR-U4 | FM-UXEVAL-001, FM-UXEVAL-002 |
| CP-U3 | issue identification 后 | 是否功能测试偏移/证据不足 | KR-U5 | FM-UXEVAL-005, FM-UXEVAL-006 |
| CP-U4 | severity attribution 后 | 严重级别是否可证明 | KR-U2 | FM-UXEVAL-003 |
| CP-U5 | report generation 前 | 是否 final / fallback / supplement | KR-U3 | FM-UXEVAL-004, FM-UXEVAL-007 |

---

## 4. Checkpoint Records

### CP-U1 — evidence_planning 后
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | 评估范围 + 旅程地图 + 任务清单 |
| required_evidence | 关键页面/流程清单 |
| quality_probe_questions | 关键页面/状态是否全覆盖?证据计划是否够支撑结论? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填 5 枚举>` |
| user_notice | `<填>` |
| carry_forward_items | `<填>` |

### CP-U2 — screenshot/web collection 后
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | evidence/ 目录 |
| required_evidence | 截图/DOM/trace + OCR 可读性 |
| quality_probe_questions | 证据是否充分?是否含真实账号/PII 需打码? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填>` |
| user_notice | `<填>` |
| carry_forward_items | `<填>` |

### CP-U3 — issue identification 后
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | raw_issues |
| required_evidence | issue ↔ heuristic ↔ evidence 映射 |
| quality_probe_questions | 是否把功能缺失当体验问题?场景与证据是否匹配? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填>` |
| user_notice | `<填>` |
| carry_forward_items | `<填>` |

### CP-U4 — severity attribution 后
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | issues(含 severity) |
| required_evidence | severity 4 档枚举 + 判定依据 |
| quality_probe_questions | severity 是否可证明?是否回避 critical? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填>` |
| user_notice | `<填>` |
| carry_forward_items | `<填>` |

### CP-U5 — report generation 前
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | delivery_assessment(草稿) |
| required_evidence | coverage 计算 + 建议三要素 |
| quality_probe_questions | 交付状态应为 final / fallback / supplement?建议是否可执行? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填>` |
| user_notice | `<填>` |
| carry_forward_items | `<填>` |

---

## 5. Required User Notices

| checkpoint | 当前发现 | 对最终质量影响 | 用户可补什么 | 继续则如何降级 | 需确认 |
|---|---|---|---|---|---|
| CP-U<n> | `<填>` | `<填>` | `<填>` | `<填>` | yes / no |

**synthetic 示例**(CP-U2,decision=ask_user):
> 当前发现:[synthetic] 关键流程的截图缺失 3 张,OCR 无法识别 2 张。
> 影响:对应 issue 将无证据(FM-UXEVAL-001 风险)。
> 可补:补充截图或 screens-description.md。
> 继续则降级:无证据 issue 移入 unverified_issues,交付状态降为 supplement_required。
> 需确认:yes。

---

## 6. Carry-Forward Rules

- H5 携带的 gaps / assumptions 从 CP-U1 起持续携带。
- 每个 checkpoint 新增 gap 加入 carry_forward_items,直到 H4 显式呈现。
- continue_with_gaps 必须列出所有 carry-forward 项。

---

## 7. Degrade Scope Rules

| 触发 major FM | 降级动作 |
|---|---|
| FM-UXEVAL-005(功能测试偏移) | 把功能缺失类 issue 标 out_of_scope |
| FM-UXEVAL-006(证据-场景不匹配) | 不匹配 issue 移入 unverified_issues |
| FM-UXEVAL-007(证据不足) | delivery_assessment 降为 fallback_safe / supplement_required |

---

## 8. Stop Blocked Rules

| 触发 blocker FM | 是否可补输入 | 决策 |
|---|---|---|
| FM-UXEVAL-001(无证据,无法补) | no | stop_blocked |
| FM-UXEVAL-001(可补截图) | yes | ask_user |
| FM-UXEVAL-002(敏感信息泄露) | 打码后可继续 | ask_user(要求脱敏) |
| FM-UXEVAL-003(严重等级越界) | 阶段内可修 | continue(修正后) |

---

## 9. Handoff To H4 Self Review

| 字段 | 内容 |
|---|---|
| checkpoint_log_path | `templates/progressive-quality-checkpoint-log.md`(本 run 实例) |
| all_carried_gaps | `<填>` |
| all_assumptions | `<填>` |
| scope_degradations | `<填>` |
| late_discovered_risks | `<填:如归因阶段才暴露的根因冲突>` |
| expected_h4_decision | `<填:基于 checkpoint 预判>` |

> H4 若 block,必须能追溯到某 checkpoint 预警;否则标 late-discovered-risk。

---

## 10. Synthetic Example

> [synthetic] Acme Demo Console,client 模式,5 张截图。

```
CP-U1: decision=continue
CP-U2: decision=ask_user
  user_notice: "3 张关键截图缺失"(见 §5 示例)
  → 用户补充截图 → 升级为 continue_with_gaps(2 张仍 OCR 不清)
CP-U3: decision=continue_with_gaps
  detected_gaps: [GAP-001 1 条 issue 场景待现场验证]
CP-U4: decision=continue
CP-U5: decision=degrade_scope
  user_notice: "证据覆盖 70%,交付状态降为 supplement_required"
final handoff: 1 gap carried, expected_h4=degrade_with_gaps
```

> 产品价值:用户在 CP-U2(证据采集阶段)就被告知截图缺失,而非跑完归因后才发现 issue 无证据。
