# Diagnostic Summary

> **🚫 SYNTHETIC / SANITIZED ONLY** — 本摘要必须脱敏,不得包含原始输入、PRD、截图OCR、URL、账号、路径、业务文案。
> **用途**:用户可选择将此摘要贴入 GitHub issue,帮助维护者定位问题,无需提交真实材料。

---

## 1. Metadata

| 字段 | 值 |
|---|---|
| run_id | `<填>` |
| run_workspace_id | `<填:ID only,not path>` |
| skill | `<填>` |
| designos_version | `<填>` |
| skill_version | `<填>` |
| mode | `<填>` |
| created_at | `<填>` |

---

## 2. Gate Decisions

| Gate | Decision |
|---|---|
| H5 Input Quality | `<填:ready/ready_with_assumptions/needs_user_clarification/blocked_insufficient_input>` |
| H5.1 Checkpoints | `<填:CP-X1~X5 各decision>` |
| H4 Self Review | `<填:pass/pass_with_minor_warnings/degrade_with_gaps/block>` |
| H6 Consistency | `<填:consistent/consistent_with_carried_gaps/needs_reconciliation/blocked_inconsistent>` |

---

## 3. Checkpoint Decisions

| checkpoint_id | decision |
|---|---|
| CP-X1 | `<填>` |
| CP-X2 | `<填>` |

---

## 4. Triggered Failure Modes

- FM-XXX-001: `<描述>`
- FM-XXX-002: `<描述>`

---

## 5. Linked KR

- KR-X1
- KR1.1

---

## 6. Gap / Assumption Summary

| type | count |
|---|---|
| gaps | `<填>` |
| assumptions | `<填>` |

### Recommended Missing Fields (S2-H7.1)

> 如果本次 run 存在输入缺口，推荐用户补充的字段。

| field_category | recommended_field | why_important | blocking_level |
|---|---|---|---|
| `<填>` | `<填>` | `<填>` | blocker / major / minor |

### Recommended User Questions (S2-H7.1)

> 可以直接问用户的问题，帮助用户快速补充关键输入。

| question_id | question | blocking_level |
|---|---|---|
| `<填>` | `<填>` | blocker / major / minor |

---

## 6.1 KR Aggregation View (S2-H7.1)

> 本次 run 涉及的 KR 聚合视图，显示哪些 KR 被影响、状态如何。

| kr_id | status | linked_gate | impact_level |
|---|---|---|---|
| `<填>` | pass / warn / fail / unknown | `<填:H5/H5.1/H4/H6>` | high / medium / low |

### KR Summary

- Total KR: `<填>`
- Pass: `<填>`
- Warn: `<填>`
- Fail: `<填>`
- Unknown: `<填>`

### Most Affected KR

`<填:影响最大的 1-3 个 KR,说明原因>`

---

## 7. Consistency Summary

- `<填:如有跨skill一致性问题>`

---

## 8. Sanitized Error Message

```
<填:脱敏后的错误信息,删除路径/URL/账号/业务文案>
```

---

## 9. Reproduction Hint

`<填:脱敏后的复现提示,只含结构性信息>`

---

## 10. Privacy Checklist

- [ ] 已删除原始输入
- [ ] 已删除 PRD 原文
- [ ] 已删除截图 OCR
- [ ] 已删除 URL
- [ ] 已删除账号/token/password
- [ ] 已删除本地路径
- [ ] 已删除业务文案
- [ ] 已删除客户名/项目名
- [ ] evidence_ref 仅含 ID,不含 path
