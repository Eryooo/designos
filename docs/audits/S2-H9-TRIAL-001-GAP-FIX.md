# S2-H9 — Trial-001 Gap Fix: P0 Mechanism Hardening

**性质**:机制护栏强化(hardening),非 correctness bug 修复。Trial-001 机制总体工作正常(能诚实降级),但缺显式输入分类字段,存在自动化/半自动场景下被绕过的风险。
**日期**:2026-06-16
**关联 Trial**:Trial-001 Controlled Real PRD Test(`TRIAL-20260616-001-real-prd`)
**关联 Triage**:`<DESIGNOS_WORKSPACE_ROOT>/batches/TRIAL-20260616-001-real-prd/triage/`

> **⚠️ 范围更正(S2-H9.1)**:本报告原始版本同时实现了 FB-01(prd2proto)与 FB-02(uxeval)。但用户最新范围要求是"先做只需要 PRD 的测试,先不要搞 uxeval"。因此 S2-H9.1 已将本批**收窄为 PRD-only**:
> - **实际保留**:FB-01 / ISSUE-P1 / prd2proto input document type classification。
> - **改为 deferred backlog**:FB-02 / ISSUE-U1 / uxeval evidence_type classification(不在当前 PRD-only 测试路径处理)。
> - S2-H9 安全扫描通过、**未发现泄露**,S2-H9.1 是 scope correction(范围漂移更正),**不是安全修复**。
> 详见 `docs/audits/S2-H9.1-SCOPE-CORRECTION.md`。本报告以下内容已按收窄后口径更新。

**背景文档**:
- `docs/audits/S2-H8-TRIAL-READINESS-AUDIT.md`(Trial-001 准备审计)
- `docs/audits/S2-H9.1-SCOPE-CORRECTION.md`(范围更正)
- Triage 产物:`triage-report.md/json`、`fix-backlog-sanitized.md`、`next-input-request.md`、`synthetic-replay-plan.md`

---

## 1. Trial-001 Triage 摘要

- **Trial 结论**:3 个 skill 全部因输入不足降级(ai-analytics → degrade_with_gaps;prd2proto → degrade_with_gaps(partial);uxeval → supplement_required),但机制行为一致诚实,无脑补,无证据越界,gap 链完整,一票否决 0 命中。
- **主因**:输入材料是战略 MRD/执行 roadmap/文档位图,而非完整 PRD 正文+产品 UI 截图+页面状态。
- **8 个 sanitized issue**:5 个 mechanism_gap(护栏缺口),0 个输入不足本身,3 个 no_action(模板增强建议)。
- **核心发现**:机制行为正确(降级诚实),但缺显式 input_type / evidence_type 字段,靠"语义判断"区分材料类型,在自动化/半自动下存在误判风险(如把 roadmap 当 PRD、把文档位图当 UI 截图)。

---

## 2. 修复项(收窄后)

本批(S2-H9.1 收窄后)只保留 FB-01(prd2proto),FB-02(uxeval)改为 deferred backlog,不实现 P1(FB-03 / FB-04)。FB-01 是"降级路径护栏",不阻塞下一轮"PRD-only 质量上限测试"(给足 PRD 正文时该护栏根本不会触发)。

| ID | Issue | Skill | Priority | 状态 | Fix Target |
|---|---|---|---|---|---|
| FB-01 | ISSUE-P1:prd2proto 缺前置输入类型识别(prd/roadmap/mrd) | prd2proto | P0 | ✅ 保留实现 | `skills/prd2proto/templates/input-quality-gate.md` §2a |
| FB-02 | ISSUE-U1:uxeval 缺 evidence_type 校验(文档位图 vs 产品 UI) | uxeval | P0 | ⏸️ deferred backlog(S2-H9.1 移除) | 待 uxeval 专项/截图证据测试时处理 |

---

## 3. FB-01 修复说明(ISSUE-P1 / prd2proto 输入类型识别)

### 问题描述(sanitized)
Trial-001 输入为执行 roadmap(里程碑+需求条目名+负责人+状态),信息密集但非 PRD 正文(缺页面清单/流程步骤/状态枚举)。prd2proto 最终行为正确(降级为 partial,停在模块级,不脑补页面),但模板缺显式 input_document_type 分类,用户可能在投入后才发现"给的是 roadmap 不是 PRD"。

### 修复内容
在 `skills/prd2proto/templates/input-quality-gate.md` §2(Input Source Inventory)末尾新增 ### 2a 子节(Input Document Type Classification),包含:
- `input_document_type` 枚举:`prd | mrd | roadmap | strategy_brief | mixed | unknown`。
- `document_type_confidence`:判定置信度。
- `document_type_reason`:为何判定为此类型(关键特征)。
- `minimum_prd_requirements_missing`:缺哪类 PRD 内容。
- `can_generate_prototype_from_input` 枚举:`yes | partial | no`。
- **守门规则**:roadmap/MRD 类 → `input_decision` 至多 `needs_user_clarification`(不得 `ready`);`can_generate_prototype_from_input=no` → `blocked_insufficient_input`。

### 影响范围
- **模板结构**:§2a 实现为 §2 内的 ### 子节,顶层仍是 §1-10(不破坏 validator 的 10 节检查)。
- **validator**:`scripts/validate_input_quality_templates.py` **无需改动**(维持 10 节检查;§2a 为子节)。
- **schema**:`schemas/feedback/diagnostic-summary.schema.json` 新增可选字段:`input_document_type / input_document_type_confidence / can_generate_prototype_from_input`(仅 prd2proto 填)。
- **diagnostic 模板**:`templates/diagnostic-summary.md` 新增 §2a(可选,仅 prd2proto 填)。
- **不改**:runtime / pipeline / kernel / prompts。

### 关联 FM / KR
- FM-PRD2PROTO-005(PRD 缺失信息记 gap 非脑补)— 守门规则联动。
- KR1.1(最低交付线)— roadmap 类无法达最低交付线,须早期告知。

---

## 4. FB-02 状态(ISSUE-U1 / uxeval evidence_type 校验)— DEFERRED BACKLOG

> **S2-H9.1 范围更正**:FB-02 已从本批移除,改为 deferred backlog。理由:用户最新范围要求"先做只需要 PRD 的测试,先不要搞 uxeval"。uxeval evidence_type 校验属于截图证据路径,不在当前 PRD-only 测试链路(ai-analytics → prd2proto)内。

### 原问题描述(保留备查,sanitized)
Trial-001 存在 PDF 分页位图(文档页面图,非产品 UI)。uxeval 最终行为正确(判 supplement_required,issue_count=0,不脑补),但模板缺显式 evidence_type 校验。**该问题真实存在,但不在当前 PRD-only 路径,延后处理。**

### 当前处置
- `skills/uxeval/templates/input-quality-gate.md` 已**回滚**至 S2-H9 前版本(无 §2a evidence_type)。
- diagnostic 模板 / schema 中的 uxeval 字段(`evidence_type` / `evidence_type_confidence` / `can_support_ux_evaluation`)已**移除**。
- 处理时机:进入 uxeval 专项或截图证据测试时再实现(关联 FM-UXEVAL-001 / FM-UXEVAL-003)。

### 关联 FM / KR
- FM-UXEVAL-001(无证据 issue)— 守门规则显式预防。
- FM-UXEVAL-003(PRD 推断当证据)— 守门规则显式预防。
- KR1.2(一票否决=0)— 守门规则防触发。

---

## 5. 未修 P1 / P2 Backlog

| ID | Issue | Priority | 理由 |
|---|---|---|---|
| FB-03 | ISSUE-A3:coverage<0.70 定性降级例外路径 | P1 | 规则歧义,但下一轮给足材料 coverage 应 ≥0.70,非阻塞质量上限测试 |
| FB-04 | ISSUE-P2:引用型需求处理路径 | P1 | partial 缺陷,下一轮给 PRD 正文即可绕过 |
| FB-05 | ISSUE-A1:竞品来源独立性字段 | P2 | 字段增强(非缺陷),backlog |
| FB-06 | ISSUE-P3:部分交付物模板变体 | P2 | 模板增强(非缺陷),backlog |
| FB-07 | ISSUE-U2:补充证据需求单模板 | P2 | 模板增强(非缺陷),backlog |

> P1 可在后续 Gap Fix 批实施(与质量上限测试并行);P2 进长期 backlog。

---

## 6. 影响范围(S2-H9.1 收窄后)

| 类别 | 改动文件 | 性质 |
|---|---|---|
| skill 模板 | `skills/prd2proto/templates/input-quality-gate.md` | §2 末新增 ### 2a 子节(Input Document Type),顶层仍 10 节 |
|  | `skills/uxeval/templates/input-quality-gate.md` | **已回滚至 S2-H9 前版本**(无 §2a) |
| 脱敏产物模板 | `templates/diagnostic-summary.md` | 新增 §2a(可选,仅 prd2proto 填);uxeval 段已删除 |
| 脱敏产物 schema | `schemas/feedback/diagnostic-summary.schema.json` | 新增 3 个可选字段(input_document_type 系);uxeval 的 evidence_type 系已移除 |
| 校验脚本 | `scripts/validate_input_quality_templates.py` | **无需改动**(§2a 为子节,顶层仍 10 节) |
| 审计报告 | `docs/audits/S2-H9-TRIAL-001-GAP-FIX.md` | 本文件(已更新收窄口径) |
|  | `docs/audits/S2-H9.1-SCOPE-CORRECTION.md` | 新增(范围更正说明) |

**未改**:
- runtime / kernel / pipeline / factory / release / npm / version / install。
- prompts(未新增约束)。
- 其余 skill(ai-analytics / ip-design / brand-creative / uxeval)模板维持 10 节。
- workspace / private evidence / raw PRD / extracted PRD。

---

## 7. 验证结果

所有 validator 必须通过(见 §8 Checklist)。

---

## 8. 是否可以进入下一轮 Quality Ceiling Test

**✅ 是,推荐立即进入 PRD-only Quality Ceiling Test。**

理由:
1. **S2-H9.1 收窄后只保留 FB-01(prd2proto 输入类型识别)**,修复了"降级路径护栏",但不触及"输入充分时的产出质量"。
2. **Trial-001 全链降级主因是输入不足**(缺核心需求 PRD 正文/IA/流程步骤),不是机制缺陷。
3. **下一轮给足 PRD 正文 + IA/流程步骤**,FB-01 护栏根本不会触发(roadmap case 不会再出现),因此不阻塞质量上限测试。
4. **uxeval 已移出本批**(FB-02 deferred),当前测试路径为 **PRD-only**:ai-analytics → prd2proto,不包含 uxeval,因此不需要 UI 截图/页面状态。
5. P1(FB-03/FB-04)可后续修,不阻塞 PRD-only 测试。

推荐顺序:
- **立即**:提交 S2-H9.1 scope correction(本批,commit 但不 push)。
- **下一批**:**PRD-only Quality Ceiling Test**:ai-analytics(战略分析)→ prd2proto(PRD 转设计产物),输入为充分 PRD 正文(核心需求 + IA + 流程步骤),验证产出质量上限 vs 资深设计师可评审水准。

---

## 9. Validation Checklist

完整验证清单见 S2-H9.1 closeout。本批必须:
- `python3 scripts/validate_input_quality_templates.py` 通过(全部 skill 10 节,§2a 为子节)。
- `python3 scripts/validate_feedback_safety_infrastructure.py` 通过(diagnostic schema 合法)。
- 其余 5 个 validators 通过(progressive/cross-skill/self-review/s2-h7b/paradigm)。
- `bash scripts/security/scan-sensitive.sh` 0 命中。
- `git diff --check` 无空白问题。
- `git ls-files` 无 workspace / private-evidence / raw-prd / .pdf / .zip。
