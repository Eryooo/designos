# Self Review Gate — ai-analytics

> **🚫 SYNTHETIC / SANITIZED ONLY** — 本模板及示例不含真实业务/客户/竞品价格/市场数据。
> **本模板性质**:交付前自检门(引用层,非新标准)。阈值引用 S2-H1/H1.1,结构引用 S2-H2,failure mode 引用 `skills/ai-analytics/eval/failure/failure-modes.md`,约束引用 `skills/ai-analytics/constitution.md`(4 条)。
> **执行顺序**:见 `docs/audits/S2-H4-SELF-REVIEW-GATE.md` §3(8 步)。
> **当前状态**:ai-analytics = pilot,prompt-grade,**无 runtime**;pilot 仅稳产 design_strategy + user_persona。本 gate 通过 ≠ 已达资深水平。

---

## 1. Metadata

| 字段 | 值(填写时替换) |
|---|---|
| skill | ai-analytics |
| run_id | `run-synth-XXXX` |
| reviewer | `<reviewer-id>` |
| date | `YYYY-MM-DD` |
| input_summary | `[synthetic] Acme Demo SaaS 竞品资料 + PRD` |
| output_artifact_paths | `ai-analytics-out/<run_id>/design_strategy.json + user_persona.json` |
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
| KR-A1 | 编造数据率 = 0 | `<填:evidence_refs 反向校验>` | pass / fail | |
| KR-A2 | schema 必填字段非空率 = 100% | `<填>` | pass / warn / fail | |
| KR-A3 | coverage ≥ 0.70 且评估准确 | `<填>` | pass / warn / fail | |
| KR-A4 | 越界产出 = 0 | `<填>` | pass / fail | |
| KR-A5 | [inferred] 标注覆盖率达标 | `<填>` | pass / warn / fail | |

---

## 4. One-Vote Veto Check

| veto_id | description | triggered | evidence | decision |
|---|---|---|---|---|
| V1 | 编造数据 | yes / no / unknown | `<填>` | triggered=yes → block |
| V2 | 下游必填字段缺失 | yes / no / unknown | `<填>` | triggered=yes → block |
| V3 | Coverage 虚高 | yes / no / unknown | `<填>` | triggered=yes → block |
| V4 | 越界产出(代码/问题清单) | yes / no / unknown | `<填>` | triggered=yes → block |

> 任一 triggered=yes → final delivery_decision **必须 block**。

---

## 5. Failure Mode Self Review

> 引用 `skills/ai-analytics/eval/failure/failure-modes.md`(仅 id/severity/self_review_question)。

| fm_id | severity | self_review_question | answer | evidence | remediation_if_failed |
|---|---|---|---|---|---|
| FM-AIANALYTICS-001 | blocker | 每条 finding 是否有 evidence_refs 指向真实 collected_data,无来源数据是否已删/标 inferred 并阻断? | pass / warn / fail / unknown | `<填>` | 删除或标 inferred |
| FM-AIANALYTICS-002 | blocker | design_strategy/user_persona 必填字段是否全非空且合 schema,缺失是否已阻断? | pass / warn / fail / unknown | `<填>` | 补必填字段 |
| FM-AIANALYTICS-003 | blocker | coverage 是否真实反映资料量,<0.70 是否已 QG1 硬停而非虚标? | pass / warn / fail / unknown | `<填>` | 重评 coverage |
| FM-AIANALYTICS-004 | blocker | 输出是否仅含分析,未越界产代码/原型/问题清单? | pass / warn / fail / unknown | `<填>` | 删除越界内容 |
| FM-AIANALYTICS-005 | major | 推断是否全标 [inferred] 附依据? | pass / warn / fail / unknown | `<填>` | 补标注 |
| FM-AIANALYTICS-006 | major | user_persona goals/pain_points 是否场景化有证据,非口号? | pass / warn / fail / unknown | `<填>` | 补场景化描述 |
| FM-AIANALYTICS-007 | major | comparison_matrix 是否覆盖 ≥4 维,维度过浅是否需 degrade? | pass / warn / fail / unknown | `<填>` | 补维度或标 gap |
| FM-AIANALYTICS-008 | minor | methodology 是否有数据支撑,不足是否已 warn 改选? | pass / warn / fail / unknown | `<填>` | 改选低数据要求方法 |

---

## 6. Golden Template Coverage Check

> 引用 `skills/ai-analytics/templates/golden-analysis-output.md` 必填章节。

| section | required | present | evidence_path | gap_if_any |
|---|---|---|---|---|
| 输入前提 | yes | yes / no | `<填>` | |
| 输出 artifact 列表 | yes | yes / no | `<填>` | |
| design_strategy 必填字段 | yes | yes / no | `<填>` | |
| user_persona 必填字段 | yes | yes / no | `<填>` | |
| data_completeness_assessment | yes | yes / no | `<填>` | |
| traceability 规范 | yes | yes / no | `<填>` | |

---

## 7. Gap / Assumption / Confidence / Traceability Check

| 检查项 | requirement | evidence | gap |
|---|---|---|---|
| gaps 显式标注 | 数据缺口已记入 gaps | `<填>` | |
| assumptions 有 confidence | 推断假设带 risk_if_wrong | `<填>` | |
| inferred 有来源 | [inferred] 附依据(行业/类比/访谈) | `<填>` | |
| 关键结论可追溯 | finding → collected_data 条目 | `<填>` | |

---

## 8. Not Allowed Claims Check

> 引用 FM-AIANALYTICS-* 的 not_allowed_claims。

| 禁止声明 | 是否命中 | 处置 |
|---|---|---|
| "可替代真实市场研究 / 用户访谈" | yes / no | 命中 → block |
| "作为产品决策唯一依据" | yes / no | 命中 → block |
| "已接入 runtime"(实为 prompt-grade) | yes / no | 命中 → block |
| "production ready / fully automated / 完全自动化" | yes / no | 命中 → block |

> 任一命中 → delivery_decision = block。

---

## 9. Delivery Decision

```
delivery_decision: <pass | pass_with_minor_warnings | degrade_with_gaps | block>
```

判定理由(按 §4 规则):
- `<填:命中 blocker/veto → block;major → degrade_with_gaps;仅 minor → pass_with_minor_warnings;全过 → pass>`

next_actions:
- `<填:具体动作清单>`

---

## 10. Reviewer Notes

- `<填:审查备注,不新增标准,不写真实业务信息>`
