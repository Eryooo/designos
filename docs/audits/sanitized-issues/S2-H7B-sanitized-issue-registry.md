# Sanitized Issue Registry

> **本文档性质**: 维护者内部归档，非用户填写。记录脱敏后的 issue、根因、修复目标、synthetic replay 链接。
> **Privacy Rule**: 不记录真实 PRD / 截图 / URL / 账号 / 路径 / 业务文案 / 客户名。evidence_ref 仅记 ID。

---

## 1. Registry Metadata

| 字段 | 值 |
|---|---|
| registry_version | 1.0.0 |
| last_updated | 2026-06-15 |
| total_issues | 6 |
| source_batch | S2-H7B |
| workspace_root | `<DESIGNOS_WORKSPACE_ROOT>` |

---

## 2. Privacy Rules

- ✅ 只记录 sanitized / synthetic 内容
- ❌ 不记录真实材料路径
- ❌ 不记录真实业务文案
- ✅ evidence_ref 仅记 ID，格式: `PRIVATE-EVIDENCE-YYYYMMDD-NNN`

---

## 3. Issue Table

| issue_id | public_issue_ref | skill | severity | root_cause_type | fix_target | status |
|---|---|---|---|---|---|---|
| ISS-H7B-001 | - | ai-analytics | medium | input_gap | template | open |
| ISS-H7B-002 | - | ai-analytics | minor | consistency_gap | docs | open |
| ISS-H7B-003 | - | prd2proto | medium | input_gap | template | open |
| ISS-H7B-004 | - | prd2proto | minor | consistency_gap | docs | open |
| ISS-H7B-005 | - | uxeval | high | input_gap | template | open |
| ISS-H7B-006 | - | uxeval | medium | template_gap | template | open |

---

## 4. Issue Details

### ISS-H7B-001: Input Gap - Missing Success Metrics (ai-analytics)

**Skill**: ai-analytics
**Severity**: medium
**Root Cause**: input_gap
**Fix Target**: template

**Description**:
Product brief 缺少明确的成功指标（如 DAU、留存率、NPS）。Input gate 触发了 `ready_with_assumptions`，假设了成功指标。

**Evidence**: PRIVATE-EVIDENCE-20260615-001

**Linked KR**: KR-INPUT-001

**Replay**: fixtures/synthetic/s2-h7b-dry-run/synthetic-replay-case.md

---

### ISS-H7B-002: Consistency Conflict - Target Audience Mismatch (ai-analytics)

**Skill**: ai-analytics
**Severity**: minor
**Root Cause**: consistency_gap
**Fix Target**: docs

**Description**:
Product brief 描述目标团队规模为"5-20 人"，可能与后续 PRD 中的"10-50 人"不一致。Consistency gate 触发 `needs_reconciliation`。

**Evidence**: PRIVATE-EVIDENCE-20260615-002

**Linked KR**: KR-CONSISTENCY-001

**Replay**: fixtures/synthetic/s2-h7b-dry-run/synthetic-replay-case.md

---

### ISS-H7B-003: Input Gap - Missing Success Metrics (prd2proto)

**Skill**: prd2proto
**Severity**: medium
**Root Cause**: input_gap
**Fix Target**: template

**Description**:
PRD 缺少成功指标。Input gate 触发 `ready_with_assumptions`。

**Evidence**: PRIVATE-EVIDENCE-20260615-003

**Linked KR**: KR-INPUT-001

**Replay**: fixtures/synthetic/s2-h7b-dry-run/synthetic-replay-case.md

---

### ISS-H7B-004: Consistency Conflict - Target Audience Mismatch (prd2proto)

**Skill**: prd2proto
**Severity**: minor
**Root Cause**: consistency_gap
**Fix Target**: docs

**Description**:
PRD 说"10-50 人"，与 ai-analytics 的"5-20 人"不一致。Consistency gate 触发 `needs_reconciliation`。

**Evidence**: PRIVATE-EVIDENCE-20260615-004

**Linked KR**: KR-CONSISTENCY-001

**Replay**: fixtures/synthetic/s2-h7b-dry-run/synthetic-replay-case.md

---

### ISS-H7B-005: Input Gap - Missing Page States (uxeval)

**Skill**: uxeval
**Severity**: high
**Root Cause**: input_gap
**Fix Target**: template

**Description**:
Screenshot notes 缺少空状态/错误状态/加载状态描述。Input gate 触发 `needs_user_clarification`，CP2 触发 `degrade_scope`。

**Evidence**: PRIVATE-EVIDENCE-20260615-005

**Linked KR**: KR-INPUT-002, KR-CHECKPOINT-004

**Replay**: fixtures/synthetic/s2-h7b-dry-run/synthetic-replay-case.md

---

### ISS-H7B-006: Template Gap - Degraded Scope Not Recorded (uxeval)

**Skill**: uxeval
**Severity**: medium
**Root Cause**: template_gap
**Fix Target**: template

**Description**:
Progressive checkpoint 触发 `degrade_scope`，但未记录"具体降级了哪些范围"。

**Evidence**: PRIVATE-EVIDENCE-20260615-006

**Linked KR**: KR-CHECKPOINT-004

**Replay**: fixtures/synthetic/s2-h7b-dry-run/synthetic-replay-case.md

---

## 5. Root Cause Summary

| root_cause_type | count |
|---|---|
| input_gap | 3 |
| consistency_gap | 2 |
| template_gap | 1 |

---

## 6. Fix Target Summary

| fix_target | count |
|---|---|
| template | 5 |
| docs | 2 |

---

## 7. Status Summary

| status | count |
|---|---|
| open | 6 |

---

## 8. Linked KR Summary

| KR | count |
|---|---|
| KR-INPUT-001 | 2 |
| KR-INPUT-002 | 1 |
| KR-CONSISTENCY-001 | 2 |
| KR-CHECKPOINT-004 | 2 |

---

## 9. Replay Case Registry

| replay_case | issues |
|---|---|
| fixtures/synthetic/s2-h7b-dry-run/synthetic-replay-case.md | ISS-H7B-001~006 |
