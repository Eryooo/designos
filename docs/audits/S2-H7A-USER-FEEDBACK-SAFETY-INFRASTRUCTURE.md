# S2-H7A — User Feedback Safety Infrastructure

> **本报告性质**:用户反馈安全基础设施总控层。**引用层,非新标准层**——不新增 KR / failure mode / rubric / shared knowledge 真源;不改 runtime / pipeline / factory / release。
> **核心命题**:发布后不能要求用户提交真实 PRD / 截图 / 仓库 / 业务材料。DesignOS 必须自己生成可分享的脱敏诊断摘要,用低成本 issue template 收集反馈,维护者内部归因后回灌抽象修复,不让真实材料进入仓库。
> **日期**:2026-06-12

---

## 1. 为什么需要 H7A

| 现实 | 问题 |
|---|---|
| 用户不会主动提交真实仓库/PRD/业务材料 | 无可复现环境 |
| 用户反馈成本不能高 | 要求复制仓库/脱敏 PRD 会流失反馈 |
| DesignOS 需要自己生成可分享的脱敏诊断摘要 | 当前无此能力 |
| 维护者内部完成归因和 synthetic replay | 需要标准化流程 |
| 测试运行产物与项目源码必须分离 | 避免仓库污染和误提交真实材料 |

**H7A 解决方案**:
- 所有运行产物写入仓库外 `<DESIGNOS_WORKSPACE_ROOT>`
- 自动生成脱敏 diagnostic summary
- issue template 只收简短描述 + 可选 diagnostic summary
- 维护者内部归因 → sanitized issue → synthetic replay → 泛化修复
- 真实材料永远留在用户本地,不进 Git

---

## 2. 用户反馈链路

```
User runs DesignOS locally
   ↓
DesignOS writes raw artifacts to <DESIGNOS_WORKSPACE_ROOT>/runs/
   ↓
DesignOS generates sanitized diagnostic summary
   ↓
User files issue: short description + optional diagnostic summary
   ↓
Maintainer triages issue
   ↓
Maintainer creates sanitized issue record (internal)
   ↓
Maintainer creates synthetic replay case if needed
   ↓
Main project fixed by generalized change
   ↓
Synthetic replay prevents regression
```

**关键点**:用户只需说"我用了哪个 skill、想做什么、哪里不对",无需提交真实材料。

---

## 3. 外部 DesignOS Workspace 结构

```
<DESIGNOS_WORKSPACE_ROOT>/
  runs/       # 每次运行 inputs/outputs/logs/diagnostic summaries,不提交
  evidence/   # 私有真实材料(可选高级支持),不提交
  batches/    # 多 PRD / 多 skill / 多轮测试批次索引,不提交
  exports/    # 可选择性导出的脱敏候选,提交前必须人工确认和脚本扫描
```

**重要**:
- 仓库文档只能写 `<DESIGNOS_WORKSPACE_ROOT>` 占位,不允许写真实绝对路径
- 所有子目录默认不提交(via `.gitignore`)
- `evidence/` 只作为内部私有支持补充,普通用户不需要理解

---

## 4. 单次 Run Workspace 结构

```
<DESIGNOS_WORKSPACE_ROOT>/runs/RUN-YYYYMMDD-001-<skill-or-scenario>/
  run-manifest.yaml
  inputs/
  outputs/
  logs/
  gates/
    input-quality.json
    progressive-checkpoints.json
    cross-skill-consistency.json
    self-review.json
  diagnostic-summary.md
  diagnostic-summary.json
  sanitized-issue-candidate.md
  synthetic-replay-candidate.md
```

**重要**:
- 该目录默认不提交
- `diagnostic-summary.md/json` 必须默认脱敏
- issue 中**不允许**上传完整 run workspace 压缩包
- 主仓库只吸收:sanitized issue / synthetic replay / generalized fix

---

## 5. 多 PRD / 多 skill / 多轮测试结构

```
<DESIGNOS_WORKSPACE_ROOT>/batches/BATCH-YYYYMMDD-001/
  batch-manifest.yaml
  prd-index.yaml
  run-index.yaml
  evidence-map.yaml
  summary.md
```

支持:
- 一个 PRD 跑多个 skill
- 多个 PRD 批量跑
- 一个 skill 重复跑多次
- 同一 PRD 不同版本对比
- 多工具对比(Claude Code / Codex / Trae 等)
- 通过 `run_id` 归因到具体运行
- 通过 `evidence_ref` 指向私有材料(仅 ID,不暴露路径)

---

## 6. 用户默认**不需要**提供的内容

- ❌ 真实 PRD
- ❌ 真实截图
- ❌ 真实 URL
- ❌ 真实仓库
- ❌ 真实客户/项目名
- ❌ 真实业务文案
- ❌ 账号 / token / password
- ❌ 本地路径
- ❌ 完整 run workspace 压缩包

---

## 7. 用户**只需要**提供的内容

- ✅ 使用的 skill
- ✅ 目标任务
- ✅ 实际问题
- ✅ 期望结果
- ✅ 可选 diagnostic summary
- ✅ 可选脱敏截图

---

## 8. Diagnostic Summary 设计原则

### 必须包含:
- run_id
- run_workspace_id
- skill / designos_version / skill_version / mode
- input_decision / checkpoint_decisions / delivery_decision / consistency_decision
- triggered_failure_modes / linked_kr
- gap_count / assumption_count
- error_type / sanitized_error_message
- reproduction_hint_sanitized
- evidence_ref(optional, ID only, no path)

### 必须**不**包含:
- original_input / PRD 原文 / screenshot OCR / URL
- email / token / password / secret
- 本地绝对路径 / run workspace 真实路径 / private evidence 真实路径
- 真实业务文案 / 客户名 / 项目名

---

## 9. Issue Template 设计原则

公开 GitHub issue 只收:
- skill
- what_were_you_trying_to_do
- what_went_wrong
- expected_behavior
- diagnostic_summary(可选)
- environment
- **privacy_confirmation**(必填)

所有 template 必须明确提醒:
> Do not paste real PRD, screenshots with sensitive content, URLs, credentials, customer names, local paths, full run workspace archives, or business confidential text. Use sanitized summaries only.

---

## 10. Sanitized Issue Registry 设计原则

维护者内部归档(非用户填写):
- issue_id / public_issue_ref / diagnostic_summary_ref / evidence_ref(optional)
- skill / observed_problem_sanitized / expected_behavior
- severity / linked_kr / linked_failure_mode
- root_cause_type / fix_target / proposed_fix
- synthetic_replay_case_ref / status

---

## 11. Root Cause Taxonomy

固定枚举:
```
input_gap / template_gap / rule_gap / prompt_gap / schema_gap / runtime_gap / 
docs_gap / consistency_gap / privacy_gap / evidence_gap / validation_gap
```

---

## 12. Fix Target Routing

固定枚举:
```
knowledge / template / prompt / failure_mode / checkpoint / schema / 
script / runtime / docs / release / no_code_change
```

---

## 13. Synthetic Replay Case 规则

- 从 diagnostic summary 和 sanitized issue 抽象结构,不复制内容
- 不能从 raw PRD / raw screenshot 直接复制
- 改掉行业细节、项目名、文案、字段值、链接、截图、数据
- 只保留结构性问题
- synthetic case 必须标 `SYNTHETIC / SANITIZED`
- synthetic case 必须能复现 failure mode 或 gate 问题

---

## 14. Private Evidence 作为可选高级支持

- 普通用户**不需要** `evidence_ref`
- 只有内部私有支持时才使用 `evidence_ref`
- `evidence/` 必须在 `<DESIGNOS_WORKSPACE_ROOT>` 下,不在 Git 仓库内
- 仓库内只能记录 `evidence_ref` ID,不能记录路径或真实内容
- `evidence_ref` 不能含真实项目名、文件名、路径、URL

---

## 15. 发布后自循环机制

```
feedback
  ↓
diagnostic summary
  ↓
sanitized issue
  ↓
root cause
  ↓
fix target
  ↓
synthetic replay
  ↓
generalized fix
  ↓
regression prevention
```

**关键点**:
- 用户反馈 → 维护者归因 → 主项目修复 → synthetic replay 防回归
- 真实材料不进入主仓库
- 回灌的只有抽象后的 sanitized issue / synthetic replay / generalized fix

---

## 16. 本批文件清单

| 文件 | 类型 |
|---|---|
| `docs/audits/S2-H7A-USER-FEEDBACK-SAFETY-INFRASTRUCTURE.md` | 总控报告(本文件) |
| `.github/ISSUE_TEMPLATE/bug_report.yml` | GitHub issue template |
| `.github/ISSUE_TEMPLATE/skill_quality_report.yml` | GitHub issue template |
| `.github/ISSUE_TEMPLATE/config.yml` | GitHub issue template config |
| `schemas/feedback/diagnostic-summary.schema.json` | JSON Schema |
| `schemas/feedback/sanitized-issue.schema.json` | JSON Schema |
| `templates/diagnostic-summary.md` | 模板 |
| `templates/sanitized-issue-registry.md` | 模板 |
| `templates/synthetic-replay-case.md` | 模板 |
| `fixtures/synthetic/README.md` | 说明 |
| `.gitignore` | 更新(增加 workspace / runs / evidence 等规则) |
| `scripts/validate_feedback_safety_infrastructure.py` | 只读校验脚本 |

**未碰**:runtime / pipeline / .factory/archetypes / release/npm/tag/workflow / version / install / 禁止文件。

---

## 17. 状态

本批完成后,DesignOS 具备长期用户反馈收集能力:
- ✅ 用户低成本反馈(无需提交真实材料)
- ✅ 自动生成脱敏 diagnostic summary
- ✅ 维护者内部归因 → synthetic replay → 泛化修复
- ✅ 测试产物与源码彻底隔离(外部 workspace)
- ✅ 支持多 PRD / 多 skill / 多轮测试
- ⏭ 下一步:S2-H7B Offline Dry-Run Execution
