# Progressive Quality Checkpoints — brand-creative

> **🚫 SYNTHETIC / SANITIZED ONLY** — 本模板及示例不含真实品牌/客户/商标/logo。
> **本模板性质**:brand-creative 执行中渐进质量检查点(引用层,非新标准)。规范见 `docs/audits/S2-H5.1-PROGRESSIVE-QUALITY-CHECKPOINTS.md`;FM 引用 `skills/brand-creative/eval/failure/failure-modes.md`;KR 引用 S2-H1.1;golden 引用 `skills/brand-creative/templates/golden-brand-creative-output.md`。
> **当前状态**:brand-creative = alpha,group skill,13 sub-skill 仅 6 有 pipeline(46%,未达 KR-B1 最低线 50%)。checkpoint 是过程探针,非真实验证。

---

## 1. Metadata

| 字段 | 值(填写时替换) |
|---|---|
| skill | brand-creative |
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
| CP-B1 | competitive-analysis 后 | 竞品矩阵是否足够支撑差异化 | KR-B2 | FM-BRANDCREATIVE-005 |
| CP-B2 | brand-strategy 后 | 策略是否空心 | KR-B3 | FM-BRANDCREATIVE-001 |
| CP-B3 | logo/color/type 三路完成后 | 三者是否一致 | KR-B4 | FM-BRANDCREATIVE-003 |
| CP-B4 | visual-identity 前 | 上游三件套是否齐全且不冲突 | KR-B2, KR-B4 | FM-BRANDCREATIVE-003, FM-BRANDCREATIVE-007 |
| CP-B5 | final brand package 前 | 跨子技能一致性是否成立 | KR-B4 | FM-BRANDCREATIVE-003, FM-BRANDCREATIVE-002 |

---

## 4. Checkpoint Records

### CP-B1 — competitive-analysis 后
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | competitive_matrix |
| required_evidence | 竞品 ≥ 3 + 维度 ≥ 4 |
| quality_probe_questions | 竞品矩阵是否足够支撑差异化?维度是否充分? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填 5 枚举>` |
| user_notice | `<填>` |
| carry_forward_items | `<填>` |

### CP-B2 — brand-strategy 后
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | brand_brief |
| required_evidence | 差异化定位 + 目标人群 + 品牌承诺 |
| quality_probe_questions | 策略是否空心(仅形容词)?定位是否可消费? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填>` |
| user_notice | `<填>` |
| carry_forward_items | `<填>` |

### CP-B3 — logo/color/type 三路完成后
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | logo_spec + color_palette + typography_spec |
| required_evidence | 三者 keyword_lineage 一致性 |
| quality_probe_questions | logo/color/type 三者是否一致?是否与 brand-strategy 对齐? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填>` |
| user_notice | `<填>` |
| carry_forward_items | `<填>` |

### CP-B4 — visual-identity 前
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | (尚未生成 vi_manual) |
| required_evidence | 上游 logo/color/type 齐全 |
| quality_probe_questions | 上游三件套是否齐全且不冲突? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填>` |
| user_notice | `<填>` |
| carry_forward_items | `<填>` |

### CP-B5 — final brand package 前
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | vi_manual + 全 sub-skill 产物 |
| required_evidence | 跨子技能关键词链路一致性 |
| quality_probe_questions | 跨子技能一致性是否成立?是否有商标风险未标? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填>` |
| user_notice | `<填>` |
| carry_forward_items | `<填>` |

---

## 5. Required User Notices

| checkpoint | 当前发现 | 对最终质量影响 | 用户可补什么 | 继续则如何降级 | 需确认 |
|---|---|---|---|---|---|
| CP-B<n> | `<填>` | `<填>` | `<填>` | `<填>` | yes / no |

**synthetic 示例**(CP-B2,decision=degrade_scope):
> 当前发现:[synthetic] brand_brief 定位仅有"年轻、科技"形容词,无可消费差异化。
> 影响:策略空心化(FM-BRANDCREATIVE-001,一票否决),下游视觉无锚点。
> 可补:明确"为谁解决什么、与谁不同"。
> 继续则降级:仅产出框架,标"策略待补强",不声称完整品牌系统。
> 需确认:yes。

---

## 6. Carry-Forward Rules

- H5 携带的 gaps / assumptions 从 CP-B1 起持续携带。
- 每个 checkpoint 新增 gap 加入 carry_forward_items,直到 H4 显式呈现。
- continue_with_gaps 必须列出所有 carry-forward 项。
- **alpha 特别项**:所选 sub-skill 无 pipeline 的限制必须从 CP-B1 起持续携带。

---

## 7. Degrade Scope Rules

| 触发 major FM | 降级动作 |
|---|---|
| FM-BRANDCREATIVE-004(sub-skill pipeline < 50%) | 降级声明,标 production_blocker,只交付已实装 sub-skill |
| FM-BRANDCREATIVE-005(竞品维度不足) | comparison_matrix 降级,缺维度标 gap |
| FM-BRANDCREATIVE-007(VI 不完整) | vi_manual 降级,缺模块标 gap |

---

## 8. Stop Blocked Rules

| 触发 blocker FM | 是否可补输入 | 决策 |
|---|---|---|
| FM-BRANDCREATIVE-001(策略空心,可追问定位) | yes | ask_user |
| FM-BRANDCREATIVE-002(商标风险,无禁区输入) | 可补禁区 | ask_user |
| FM-BRANDCREATIVE-003(跨子技能不一致) | 回 brand-strategy 对齐 | degrade_scope 或 stop_blocked |

---

## 9. Handoff To H4 Self Review

| 字段 | 内容 |
|---|---|
| checkpoint_log_path | `templates/progressive-quality-checkpoint-log.md`(本 run 实例) |
| all_carried_gaps | `<填>` |
| all_assumptions | `<填>` |
| scope_degradations | `<填>` |
| late_discovered_risks | `<填:如 VI 整合阶段才暴露的冲突>` |
| expected_h4_decision | `<填:基于 checkpoint 预判;alpha 阶段典型为 degrade_with_gaps>` |

> H4 若 block,必须能追溯到某 checkpoint 预警;否则标 late-discovered-risk。

---

## 10. Synthetic Example

> [synthetic] Acme Demo Brand,涉及 brand-strategy + competitive-analysis + logo-design。

```
CP-B1: decision=continue_with_gaps
  detected_gaps: [GAP-001 竞品矩阵缺 pricing 维度]
CP-B2: decision=degrade_scope
  user_notice: "策略空心化,仅产框架"(见 §5 示例)
  → 用户补差异化定位 → 升级为 continue
CP-B3: decision=continue
CP-B4: decision=ask_user
  user_notice: "所选 brand-voice 子技能当前无 pipeline(alpha),是否仅交付已实装的 logo/color/type?"
CP-B5: decision=continue_with_gaps
  carry_forward: [GAP-001, brand-voice 未实装]
final handoff: 2 gaps carried, expected_h4=degrade_with_gaps
```

> 产品价值:用户在 CP-B2(策略阶段)就被告知策略空心 + CP-B4 被告知 sub-skill 未实装,而非跑完整个品牌包才发现交付不完整。
