# Synthetic Replay Case

> **🚫 SYNTHETIC / SANITIZED ONLY** — 本 case 必须是抽象后的 synthetic fixture,不得包含真实 PRD / 截图 / URL / 业务文案。
> **用途**:从 diagnostic summary 和 sanitized issue 抽象结构,用于防回归测试。

---

## 1. Metadata

| 字段 | 值 |
|---|---|
| case_id | `REPLAY-001` |
| original_issue_ref | `ISS-001` |
| skill | `<填>` |
| failure_mode | `<填:FM-XXX-NNN>` |
| created_at | `YYYY-MM-DD` |

---

## 2. Synthetic Disclaimer

**本 case 是从真实问题抽象而来的 synthetic fixture**:
- 已删除真实 PRD、截图、URL、业务文案、客户名、项目名
- 只保留结构性问题
- 必须可用于 dry-run replay
- 必须能复现 failure mode 或 gate 问题

---

## 3. Original Issue Reference

| 字段 | 值 |
|---|---|
| public_issue | `#123` |
| diagnostic_summary_ref | `RUN-YYYYMMDD-001` |
| evidence_ref | `PRIVATE-EVIDENCE-YYYYMMDD-001`(optional) |

---

## 4. Sanitized Scenario

`<填:抽象场景描述,删除真实行业/项目/文案细节>`

---

## 5. Input Fixture

```yaml
# synthetic input
skill: prd2proto
mode: pm
prd_synthetic: |
  [synthetic] Acme Demo 后台管理系统
  目标用户:[synthetic] IT管理员
  核心功能:[synthetic] 用户管理 + 权限配置
```

---

## 6. Expected Failure Mode

- FM-XXX-NNN: `<描述预期触发的 failure mode>`

---

## 7. Expected Gate / Checkpoint Behavior

| gate/checkpoint | expected_decision | reason |
|---|---|---|
| H5 Input Quality | blocked_insufficient_input | 业务目标缺失 |
| CP-P2 | ask_user | 需追问量化 KPI |

---

## 8. Expected Fix Target

- fix_target: `<填:knowledge/template/prompt/schema等>`
- proposed_fix: `<填:修复方向>`

---

## 9. Success Criteria

- [ ] synthetic input 可复现 failure mode
- [ ] gate/checkpoint decision 符合预期
- [ ] 修复后 replay pass

---

## 10. Privacy Checklist

- [ ] 已删除真实 PRD
- [ ] 已删除真实截图
- [ ] 已删除真实 URL
- [ ] 已删除真实业务文案
- [ ] 已删除真实客户名/项目名
- [ ] evidence_ref 仅含 ID
