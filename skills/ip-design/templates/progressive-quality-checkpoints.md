# Progressive Quality Checkpoints — ip-design

> **🚫 SYNTHETIC / SANITIZED ONLY** — 本模板及示例不含真实品牌/IP/客户/商标。
> **本模板性质**:ip-design 执行中渐进质量检查点(引用层,非新标准)。规范见 `docs/audits/S2-H5.1-PROGRESSIVE-QUALITY-CHECKPOINTS.md`;FM 引用 `skills/ip-design/eval/failure/failure-modes.md`;KR 引用 S2-H1.1;golden 引用 `skills/ip-design/templates/golden-ip-design-output.md`。
> **当前状态**:ip-design = pilot,prompt-grade,无 runtime。checkpoint 是过程探针,非真实验证。

---

## 1. Metadata

| 字段 | 值(填写时替换) |
|---|---|
| skill | ip-design |
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
| CP-I1 | strategy-alignment 后 | 品牌策略是否足以支撑 IP | KR-I1 | FM-IPDESIGN-001 |
| CP-I2 | persona/worldview 后 | 人格是否立体,避免 MBTI 单标签 | KR-I1 | FM-IPDESIGN-003 |
| CP-I3 | visual-translation 前 | 是否禁止视觉先行 | KR-I2 | FM-IPDESIGN-004 |
| CP-I4 | image_prompt_pack 前 | 视觉符号是否可控/可识别/可延展 | KR-I3 | FM-IPDESIGN-005, FM-IPDESIGN-008 |
| CP-I5 | final package 前 | D2/D6/D8/视觉先行一票否决是否为 0 | KR-I2 | FM-IPDESIGN-001, FM-IPDESIGN-002, FM-IPDESIGN-003, FM-IPDESIGN-004 |

---

## 4. Checkpoint Records

### CP-I1 — strategy-alignment 后
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | brand_brief |
| required_evidence | 北极星 + 差异化 + 竞品空白 |
| quality_probe_questions | 品牌策略是否足以支撑 IP?差异化是否基于竞品空白? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填 5 枚举>` |
| user_notice | `<填>` |
| carry_forward_items | `<填>` |

### CP-I2 — persona/worldview 后
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | persona_profile + worldview |
| required_evidence | 行为模式/动机/恐惧/成长弧/关系网 |
| quality_probe_questions | 人格是否立体?是否仅 MBTI 标签? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填>` |
| user_notice | `<填>` |
| carry_forward_items | `<填>` |

### CP-I3 — visual-translation 前
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | (尚未生成 visual_spec) |
| required_evidence | brand_brief + persona 已完成 |
| quality_probe_questions | 是否已有完整策略链?是否会视觉先行? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填>` |
| user_notice | `<填>` |
| carry_forward_items | `<填>` |

### CP-I4 — image_prompt_pack 前
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | visual_spec |
| required_evidence | 识别度测试 + strict_avoidance ≥ 5 |
| quality_probe_questions | 32px 可识别?四级简化?禁忌项是否齐全? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填>` |
| user_notice | `<填>` |
| carry_forward_items | `<填>` |

### CP-I5 — final package 前
| 字段 | 值 |
|---|---|
| expected_intermediate_artifact | 6 阶段产物 + professional_gap_report |
| required_evidence | 9 维 rubric 自评 + 一票否决检查 |
| quality_probe_questions | D2/D6/D8/视觉先行一票否决是否全为 0? |
| detected_gaps | `<填>` |
| checkpoint_decision | `<填>` |
| user_notice | `<填>` |
| carry_forward_items | `<填>` |

---

## 5. Required User Notices

| checkpoint | 当前发现 | 对最终质量影响 | 用户可补什么 | 继续则如何降级 | 需确认 |
|---|---|---|---|---|---|
| CP-I<n> | `<填>` | `<填>` | `<填>` | `<填>` | yes / no |

**synthetic 示例**(CP-I1,decision=ask_user):
> 当前发现:[synthetic] 仅提供 1 个竞品 IP,差异化无足够依据。
> 影响:D2 差异化可能不合格(FM-IPDESIGN-001,一票否决)。
> 可补:再提供 2 个竞品 IP 的视觉/定位信息。
> 继续则降级:差异化标 [inferred],D2 最高打"中阶可用"。
> 需确认:yes。

---

## 6. Carry-Forward Rules

- H5 携带的 gaps / assumptions 从 CP-I1 起持续携带。
- 每个 checkpoint 新增 gap 加入 carry_forward_items,直到 H4 显式呈现。
- continue_with_gaps 必须列出所有 carry-forward 项。

---

## 7. Degrade Scope Rules

| 触发 major FM | 降级动作 |
|---|---|
| FM-IPDESIGN-005(无负向 prompt) | image_prompt_pack 降级,补 negative_prompt 或标 gap |
| FM-IPDESIGN-006(跨阶段漂移) | 标关键词漂移点,professional_gap_report 显式 |
| FM-IPDESIGN-007(推断未标) | 关键决策标 [inferred],降 confidence |
| FM-IPDESIGN-008(识别度低) | D4 标"中阶/低阶",不声称可商用 |

---

## 8. Stop Blocked Rules

| 触发 blocker FM | 是否可补输入 | 决策 |
|---|---|---|
| FM-IPDESIGN-001(差异化不合格,无竞品) | 可补竞品 | ask_user |
| FM-IPDESIGN-002(法务风险,无禁忌输入) | 可补禁忌 | ask_user |
| FM-IPDESIGN-003(人格扁平,无用户洞察) | 可补人群痛点 | ask_user |
| FM-IPDESIGN-004(视觉先行) | 重走策略链 | stop_blocked(若已先画图)/ continue(若按序) |

---

## 9. Handoff To H4 Self Review

| 字段 | 内容 |
|---|---|
| checkpoint_log_path | `templates/progressive-quality-checkpoint-log.md`(本 run 实例) |
| all_carried_gaps | `<填>` |
| all_assumptions | `<填>` |
| scope_degradations | `<填>` |
| late_discovered_risks | `<填:如视觉阶段才暴露的识别度问题>` |
| expected_h4_decision | `<填:基于 checkpoint 预判>` |

> H4 若 block,必须能追溯到某 checkpoint 预警;否则标 late-discovered-risk。

---

## 10. Synthetic Example

> [synthetic] Acme Demo IP,目标产出 6 阶段 IP 资产。

```
CP-I1: decision=ask_user
  user_notice: "竞品 IP 仅 1 个"(见 §5 示例)
  → 用户补 2 个竞品 → 升级为 continue
CP-I2: decision=continue
CP-I3: decision=continue
  (策略链完整,无视觉先行)
CP-I4: decision=degrade_scope
  user_notice: "核心符号 32px 模糊,D4 标中阶,不声称可商用"
CP-I5: decision=continue_with_gaps
  detected_gaps: [GAP-001 D6 待法务确认]
  carry_forward: GAP-001
final handoff: 1 gap carried, expected_h4=degrade_with_gaps
```

> 产品价值:用户在 CP-I1(策略阶段)就被告知差异化依据不足,而非画完视觉才发现 D2 一票否决失败。
