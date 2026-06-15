# Sanitized Issue Registry

> **本文档性质**:维护者内部归档,非用户填写。记录脱敏后的 issue、根因、修复目标、synthetic replay 链接。
> **Privacy Rule**:不记录真实 PRD / 截图 / URL / 账号 / 路径 / 业务文案 / 客户名。evidence_ref 仅记 ID。

---

## 1. Registry Metadata

| 字段 | 值 |
|---|---|
| registry_version | 1.0.0 |
| last_updated | YYYY-MM-DD |
| total_issues | `<填>` |

---

## 2. Privacy Rules

- ✅ 只记录 sanitized / synthetic 内容
- ❌ 不记录真实材料路径
- ❌ 不记录真实业务文案
- ✅ evidence_ref 仅记 ID,格式:`PRIVATE-EVIDENCE-YYYYMMDD-NNN`

---

## 3. Issue Table

| issue_id | public_issue_ref | skill | severity | root_cause_type | fix_target | status |
|---|---|---|---|---|---|---|
| ISS-001 | #123 | prd2proto | blocker | schema_gap | schema | fixed |

---

## 4. Root Cause Summary

| root_cause_type | count |
|---|---|
| input_gap | `<填>` |
| template_gap | `<填>` |
| prompt_gap | `<填>` |

---

## 5. Fix Target Summary

| fix_target | count |
|---|---|
| knowledge | `<填>` |
| template | `<填>` |
| prompt | `<填>` |

---

## 6. Synthetic Replay Case Links

| issue_id | replay_case_ref |
|---|---|
| ISS-001 | `fixtures/synthetic/replay-001.md` |

---

## 7. Open Questions

- `<填:需进一步调查的项>`

---

## 8. Verification Status

| issue_id | verified | notes |
|---|---|---|
| ISS-001 | yes | synthetic replay passed |
