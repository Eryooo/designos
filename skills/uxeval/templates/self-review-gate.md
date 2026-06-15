# Self Review Gate — uxeval

> **🚫 SYNTHETIC / SANITIZED ONLY** — 本模板及示例不含真实业务/客户/截图/账号/内部链接。
> **本模板性质**:交付前自检门(引用层,非新标准)。阈值引用 S2-H1/H1.1,结构引用 S2-H2,failure mode 引用 `skills/uxeval/eval/failure/failure-modes.md`,约束引用 `skills/uxeval/constitution.md`(8 条)。
> **执行顺序**:见 `docs/audits/S2-H4-SELF-REVIEW-GATE.md` §3(8 步)。
> **当前状态**:uxeval = beta(S1-0B 实证偏乐观),prompt-grade,**无 runtime**;pipeline `gate:` 是暂停门非 kernel quality_gates。本 gate 通过 ≠ 已达资深水平。

---

## 1. Metadata

| 字段 | 值(填写时替换) |
|---|---|
| skill | uxeval |
| run_id | `run-synth-XXXX` |
| reviewer | `<reviewer-id>` |
| date | `YYYY-MM-DD` |
| input_summary | `[synthetic] Acme Demo Console 5 张截图,mode=client` |
| output_artifact_paths | `uxeval-out/<run_id>/01..06 + evidence/` |
| delivery_decision | `<填 §9 结论>` |

---

## 2. Minimum Delivery Line KR Check(全局)

| kr_id | requirement | evidence | status | gap_if_any |
|---|---|---|---|---|
| KR1.1 | 最低交付线(中阶可用)全过 | `<填>` | pass / warn / fail / not_applicable | |
| KR1.2 | 一票否决项命中数 = 0 | `<填:§4 结果>` | pass / fail | |
| KR3.1 | 不可宣称项命中数 = 0 | `<填:§8 结果>` | pass / fail | |

---

## 3. Skill-Specific KR Check

| kr_id | requirement | evidence | status | gap_if_any |
|---|---|---|---|---|
| KR-U1 | 每条 issue evidence_refs 非空率 = 100% | `<填>` | pass / warn / fail / not_applicable | |
| KR-U2 | severity 4 档枚举合规率 = 100% | `<填>` | pass / warn / fail | |
| KR-U3 | 建议三要素覆盖率达标 | `<填>` | pass / warn / fail | |
| KR-U4 | 敏感信息泄露 = 0 | `<填:scan-sensitive 结果>` | pass / fail | |
| KR-U5 | pipeline gate(暂停门)接入率 | `<填:非 kernel quality_gates>` | pass / warn / fail | |

---

## 4. One-Vote Veto Check

| veto_id | description | triggered | evidence | decision |
|---|---|---|---|---|
| V1 | Issue 无证据(evidence_refs 空) | yes / no / unknown | `<填>` | triggered=yes → block |
| V2 | 敏感信息泄露 | yes / no / unknown | `<填>` | triggered=yes → block |
| V3 | 严重等级越界(非 4 档枚举) | yes / no / unknown | `<填>` | triggered=yes → block |
| V4 | 建议不可执行 | yes / no / unknown | `<填>` | triggered=yes → block |

> 任一 triggered=yes → final delivery_decision **必须 block**。

---

## 5. Failure Mode Self Review

> 引用 `skills/uxeval/eval/failure/failure-modes.md`(仅 id/severity/self_review_question)。

| fm_id | severity | self_review_question | answer | evidence | remediation_if_failed |
|---|---|---|---|---|---|
| FM-UXEVAL-001 | blocker | 每条 issue 是否绑定 ≥1 条真实存在 evidence,无证据的是否移入 unverified_issues? | pass / warn / fail / unknown | `<填>` | 绑定证据或移附录 |
| FM-UXEVAL-002 | blocker | 报告与截图是否 scan-sensitive 0 命中,有则是否已打码并阻断? | pass / warn / fail / unknown | `<填>` | 打码/脱敏 |
| FM-UXEVAL-003 | blocker | severity 是否全在 4 档枚举内,非法值是否已阻断? | pass / warn / fail / unknown | `<填>` | 改合法枚举 |
| FM-UXEVAL-004 | blocker | recommendation 是否含改什么/改成什么/为什么三要素? | pass / warn / fail / unknown | `<填>` | 补三要素 |
| FM-UXEVAL-005 | major | 是否把功能缺失当体验问题,这类是否已标 out_of_scope? | pass / warn / fail / unknown | `<填>` | 标 out_of_scope |
| FM-UXEVAL-006 | major | issue 场景是否与 evidence 截图一致,不匹配是否已删/标? | pass / warn / fail / unknown | `<填>` | 删除或移 unverified |
| FM-UXEVAL-007 | major | 证据不足时 delivery 是否已降级为 fallback_safe/supplement? | pass / warn / fail / unknown | `<填>` | 降级交付状态 |
| FM-UXEVAL-008 | minor | 每条 issue 是否映射 ≥1 个 heuristic principle_id? | pass / warn / fail / unknown | `<填>` | 补 principle_id |

---

## 6. Golden Template Coverage Check

> 引用 `skills/uxeval/templates/golden-evaluation-report.md` 必填章节。

| section | required | present | evidence_path | gap_if_any |
|---|---|---|---|---|
| 输入前提 | yes | yes / no | `<填>` | |
| 输出 artifact 列表 | yes | yes / no | `<填>` | |
| 必填章节(issue 结构) | yes | yes / no | `<填>` | |
| 字段级要求(evidence/severity/建议) | yes | yes / no | `<填>` | |
| coverage 矩阵(旅程×角色×任务) | yes | yes / no | `<填>` | |
| delivery_assessment | yes | yes / no | `<填>` | |

---

## 7. Gap / Assumption / Confidence / Traceability Check

| 检查项 | requirement | evidence | gap |
|---|---|---|---|
| gaps 显式标注 | 覆盖不足已记入 gaps | `<填>` | |
| assumptions 有 confidence | 评估假设带风险等级 | `<填>` | |
| inferred 有来源 | 推断结论标依据 | `<填>` | |
| 关键结论可追溯 | issue → heuristic+旅程+任务+evidence 四维 | `<填>` | |

---

## 8. Not Allowed Claims Check

> 引用 FM-UXEVAL-002 等 not_allowed_claims。

| 禁止声明 | 是否命中 | 处置 |
|---|---|---|
| "已达资深 UX 评估专家水平" | yes / no | 命中 → block |
| "可替代专业 UX 研究员" | yes / no | 命中 → block |
| "已经过真实用户测试验证" | yes / no | 命中 → block |
| "已接入 kernel quality_gates"(实为 gate 暂停门) | yes / no | 命中 → block |
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
