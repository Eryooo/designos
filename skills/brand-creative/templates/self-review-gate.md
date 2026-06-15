# Self Review Gate — brand-creative

> **🚫 SYNTHETIC / SANITIZED ONLY** — 本模板及示例不含真实品牌/客户/商标/logo。
> **本模板性质**:交付前自检门(引用层,非新标准)。阈值引用 S2-H1/H1.1,结构引用 S2-H2,failure mode 引用 `skills/brand-creative/eval/failure/failure-modes.md`,约束引用 `knowledge/design/quality/brand-creative-failure-modes.md`(group skill 无 root constitution)。
> **执行顺序**:见 `docs/audits/S2-H4-SELF-REVIEW-GATE.md` §3(8 步)。
> **当前状态**:brand-creative = alpha,group skill,**13 sub-skill 仅 6 有 pipeline(46%,未达 KR-B1 最低线 50%)**。本 gate 通过 ≠ 已达资深水平。

---

## 1. Metadata

| 字段 | 值(填写时替换) |
|---|---|
| skill | brand-creative |
| run_id | `run-synth-XXXX` |
| reviewer | `<reviewer-id>` |
| date | `YYYY-MM-DD` |
| input_summary | `[synthetic] Acme Demo Brand 策略输入 + 3 竞品` |
| output_artifact_paths | `brand-creative-out/<run_id>/phase-1..4/` |
| delivery_decision | `<填 §9 结论>` |

---

## 2. Minimum Delivery Line KR Check(全局)

| kr_id | requirement | evidence | status | gap_if_any |
|---|---|---|---|---|
| KR1.1 | 最低交付线(中阶可用)全过 | `<填>` | pass / warn / fail / not_applicable | |
| KR1.2 | 一票否决项命中数 = 0 | `<填:§4 结果>` | pass / fail | |
| KR3.2 | gap/assumption/confidence 标注覆盖率 | `<填:§7 结果>` | pass / warn / fail | |

---

## 3. Skill-Specific KR Check

| kr_id | requirement | evidence | status | gap_if_any |
|---|---|---|---|---|
| KR-B1 | sub-skill 有 pipeline 比例 ≥ 50% | `<填:当前 6/13=46% 未达>` | pass / warn / fail | `alpha 主线未成型` |
| KR-B2 | rubric 自评中阶以上 ≥ 70%(已实装) | `<填>` | pass / warn / fail | |
| KR-B3 | 一票否决项命中 = 0 | `<填>` | pass / fail | |
| KR-B4 | 跨 sub-skill 关键词链路一致 ≥ 70% | `<填>` | pass / warn / fail | |
| KR-B5 | failure-modes 严重级命中 = 0 | `<填>` | pass / fail | |

---

## 4. One-Vote Veto Check

| veto_id | description | triggered | evidence | decision |
|---|---|---|---|---|
| V1 | 策略空心化(仅形容词无定位) | yes / no / unknown | `<填>` | triggered=yes → block |
| V2 | 法务/商标风险未标 | yes / no / unknown | `<填>` | triggered=yes → block |
| V3 | 跨子 skill 不一致 | yes / no / unknown | `<填>` | triggered=yes → block |

> 任一 triggered=yes → final delivery_decision **必须 block**。
> (注:brand-creative 一票否决项为 3 项,与其他 skill 4 项不同。)

---

## 5. Failure Mode Self Review

> 引用 `skills/brand-creative/eval/failure/failure-modes.md`(仅 id/severity/self_review_question)。

| fm_id | severity | self_review_question | answer | evidence | remediation_if_failed |
|---|---|---|---|---|---|
| FM-BRANDCREATIVE-001 | blocker | brand_brief 是否含差异化定位+人群+承诺,仅形容词堆砌是否已阻断? | pass / warn / fail / unknown | `<填>` | 补差异化定位 |
| FM-BRANDCREATIVE-002 | blocker | logo/名称商标风险是否已标 [待法务确认],明显冲突是否已阻断? | pass / warn / fail / unknown | `<填>` | 标风险信号 |
| FM-BRANDCREATIVE-003 | blocker | 各 sub-skill 关键词是否与 brand-strategy 一致,漂移≥30% 是否已阻断? | pass / warn / fail / unknown | `<填>` | 回 brand-strategy 对齐 |
| FM-BRANDCREATIVE-004 | major | sub-skill pipeline 比例是否 ≥50%,未达是否已 degrade 声明? | pass / warn / fail / unknown | `<填>` | degrade + 标 production_blocker |
| FM-BRANDCREATIVE-005 | major | competitor_matrix 是否覆盖 ≥4 维,过浅是否需 degrade? | pass / warn / fail / unknown | `<填>` | 补维度或标 gap |
| FM-BRANDCREATIVE-006 | major | 推断是否标 [inferred] 且 differentiation.basis 准确? | pass / warn / fail / unknown | `<填>` | 补标注/改 basis |
| FM-BRANDCREATIVE-007 | major | vi_manual 是否覆盖 5 大模块 ≥80%,缺模块是否需 degrade? | pass / warn / fail / unknown | `<填>` | 补模块或标 gap |
| FM-BRANDCREATIVE-008 | minor | failure-modes 自检严重级命中是否已记入 gaps? | pass / warn / fail / unknown | `<填>` | 记入 gaps |

---

## 6. Golden Template Coverage Check

> 引用 `skills/brand-creative/templates/golden-brand-creative-output.md` 必填章节。

| section | required | present | evidence_path | gap_if_any |
|---|---|---|---|---|
| 输入前提 | yes | yes / no | `<填>` | |
| 输出目录结构(4 phase) | yes | yes / no | `<填>` | |
| brand_brief 必填字段 | yes | yes / no | `<填>` | |
| logo/color/typography 必填字段 | yes | yes / no | `<填>` | |
| cross_subskill_consistency | yes | yes / no | `<填>` | |
| 当前主线状态(诚实声明) | yes | yes / no | `<填>` | |

---

## 7. Gap / Assumption / Confidence / Traceability Check

| 检查项 | requirement | evidence | gap |
|---|---|---|---|
| gaps 显式标注 | 主线缺口(7 sub-skill 无 pipeline)已记 gaps | `<填>` | |
| assumptions 有 confidence | 推断假设带 risk_if_wrong | `<填>` | |
| inferred 有来源 | [inferred] 附依据 | `<填>` | |
| 关键结论可追溯 | sub-skill → brand_brief + 方法论 id + 竞品输入 | `<填>` | |

---

## 8. Not Allowed Claims Check

> 引用 FM-BRANDCREATIVE-* 的 not_allowed_claims。

| 禁止声明 | 是否命中 | 处置 |
|---|---|---|
| "13 sub-skill 全部可用"(实 6/13) | yes / no | 命中 → block |
| "替代专业品牌咨询" | yes / no | 命中 → block |
| "可直接用于品牌发布 / 商标注册" | yes / no | 命中 → block |
| "已接入 runtime / 已达资深品牌策略师水平" | yes / no | 命中 → block |
| "production ready / fully automated / 完全自动化" | yes / no | 命中 → block |

> 任一命中 → delivery_decision = block。

---

## 9. Delivery Decision

```
delivery_decision: <pass | pass_with_minor_warnings | degrade_with_gaps | block>
```

判定理由(按 §4 规则):
- `<填:命中 blocker/veto → block;major → degrade_with_gaps;仅 minor → pass_with_minor_warnings;全过 → pass>`
- 注:alpha 阶段 KR-B1 当前未达最低线,典型结论为 degrade_with_gaps 或 block。

next_actions:
- `<填:具体动作清单>`

---

## 10. Reviewer Notes

- `<填:审查备注,不新增标准,不写真实业务信息>`
