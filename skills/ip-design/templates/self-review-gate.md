# Self Review Gate — ip-design

> **🚫 SYNTHETIC / SANITIZED ONLY** — 本模板及示例不含真实品牌/IP/客户/商标。
> **本模板性质**:交付前自检门(引用层,非新标准)。阈值引用 S2-H1/H1.1,结构引用 S2-H2,failure mode 引用 `skills/ip-design/eval/failure/failure-modes.md`,约束引用 `skills/ip-design/constitution.md`(8 条)+ 9 维 rubric。
> **执行顺序**:见 `docs/audits/S2-H4-SELF-REVIEW-GATE.md` §3(8 步)。
> **当前状态**:ip-design = pilot,prompt-grade,**无 runtime**;有完整 quality 四件套。本 gate 通过 ≠ 已达资深水平。

---

## 1. Metadata

| 字段 | 值(填写时替换) |
|---|---|
| skill | ip-design |
| run_id | `run-synth-XXXX` |
| reviewer | `<reviewer-id>` |
| date | `YYYY-MM-DD` |
| input_summary | `[synthetic] Acme Demo IP,产品定义 + 目标用户 + 3 竞品 IP` |
| output_artifact_paths | `ip-design-out/<run_id>/01-brand_brief..07-brand_material_spec + professional_gap_report` |
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
| KR-I1 | 9 维 rubric 自评中阶以上 ≥ 7/9 | `<填:rubric_self_eval>` | pass / warn / fail | |
| KR-I2 | 一票否决项(D2/D6/D8+视觉先行)命中 = 0 | `<填>` | pass / fail | |
| KR-I3 | image_prompt_pack 含 negative_prompt 率 = 100% | `<填>` | pass / warn / fail | |
| KR-I4 | professional_gap_report 完整生成率 = 100% | `<填>` | pass / warn / fail | |
| KR-I5 | 关键决策 [inferred] 标注覆盖率达标 | `<填>` | pass / warn / fail | |

---

## 4. One-Vote Veto Check

| veto_id | description | triggered | evidence | decision |
|---|---|---|---|---|
| V1 | D2 差异化不合格 | yes / no / unknown | `<填>` | triggered=yes → block |
| V2 | D6 法务/合规风险未标 | yes / no / unknown | `<填>` | triggered=yes → block |
| V3 | D8 人格立体度不合格 | yes / no / unknown | `<填>` | triggered=yes → block |
| V4 | 视觉先行(先画图后反推策略) | yes / no / unknown | `<填>` | triggered=yes → block |

> 任一 triggered=yes → final delivery_decision **必须 block**。

---

## 5. Failure Mode Self Review

> 引用 `skills/ip-design/eval/failure/failure-modes.md`(仅 id/severity/self_review_question)。

| fm_id | severity | self_review_question | answer | evidence | remediation_if_failed |
|---|---|---|---|---|---|
| FM-IPDESIGN-001 | blocker | 差异化是否基于竞品空白且无贬损,D2 不合格是否已阻断? | pass / warn / fail / unknown | `<填>` | 重写差异化 |
| FM-IPDESIGN-002 | blocker | 商标/版权/敏感映射风险是否已标 [待法务确认],D6 不合格是否已阻断? | pass / warn / fail / unknown | `<填>` | 标风险信号 |
| FM-IPDESIGN-003 | blocker | persona 是否含五要素,仅 MBTI/口头禅(D8 不合格)是否已阻断? | pass / warn / fail / unknown | `<填>` | 补人格五要素 |
| FM-IPDESIGN-004 | blocker | visual_spec 是否回溯到 brand_brief/persona(先策略后视觉)? | pass / warn / fail / unknown | `<填>` | 重走 M01-M03 |
| FM-IPDESIGN-005 | major | image_prompt_pack 是否含 ≥5 条 negative_prompt 且与 strict_avoidance 同步? | pass / warn / fail / unknown | `<填>` | 补负向控制 |
| FM-IPDESIGN-006 | major | 北极星→人格→视觉→内容关键词链路是否无漂移? | pass / warn / fail / unknown | `<填>` | 补关键词链路 |
| FM-IPDESIGN-007 | major | 关键决策推断是否标 [inferred] 记入 inferences[]? | pass / warn / fail / unknown | `<填>` | 补标注 |
| FM-IPDESIGN-008 | minor | 核心符号是否过 32px 识别度测试含四级简化,D4 低阶是否已 warn? | pass / warn / fail / unknown | `<填>` | 补四级简化或标 gap |

---

## 6. Golden Template Coverage Check

> 引用 `skills/ip-design/templates/golden-ip-design-output.md` 必填章节。

| section | required | present | evidence_path | gap_if_any |
|---|---|---|---|---|
| 输入前提 | yes | yes / no | `<填>` | |
| 6 阶段 artifact 列表 | yes | yes / no | `<填>` | |
| brand_brief 必填字段 | yes | yes / no | `<填>` | |
| visual_spec(识别度/strict_avoidance) | yes | yes / no | `<填>` | |
| image_prompt_pack(四层+负向) | yes | yes / no | `<填>` | |
| 9 维 rubric 自评 + professional_gap_report | yes | yes / no | `<填>` | |

---

## 7. Gap / Assumption / Confidence / Traceability Check

| 检查项 | requirement | evidence | gap |
|---|---|---|---|
| gaps 显式标注 | 数据/法务/用户研究缺口已记 gaps | `<填>` | |
| assumptions 有 confidence | inferences 带依据 + 风险 | `<填>` | |
| inferred 有来源 | 关键决策 [inferred] 附依据 | `<填>` | |
| 关键结论可追溯 | 每阶段决策 → 上阶段 + 方法论 id + 输入 | `<填>` | |

---

## 8. Not Allowed Claims Check

> 引用 FM-IPDESIGN-002 等 not_allowed_claims。

| 禁止声明 | 是否命中 | 处置 |
|---|---|---|
| "自动生成商用 Logo" | yes / no | 命中 → block |
| "替代资深设计师终审" | yes / no | 命中 → block |
| "已通过商标审查 / 无版权风险" | yes / no | 命中 → block |
| "可直接印刷/发布 / 已达资深 IP 设计师水平" | yes / no | 命中 → block |
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
