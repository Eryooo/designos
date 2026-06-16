# S2-H9 — Trial-001 Gap Fix: P0 Mechanism Hardening

**性质**:机制护栏强化(hardening),非 correctness bug 修复。Trial-001 机制总体工作正常(能诚实降级),但缺显式输入分类字段,存在自动化/半自动场景下被绕过的风险。
**日期**:2026-06-16
**关联 Trial**:Trial-001 Controlled Real PRD Test(`TRIAL-20260616-001-real-prd`)
**关联 Triage**:`<DESIGNOS_WORKSPACE_ROOT>/batches/TRIAL-20260616-001-real-prd/triage/`
**背景文档**:
- `docs/audits/S2-H8-TRIAL-READINESS-AUDIT.md`(Trial-001 准备审计)
- Triage 产物:`triage-report.md/json`、`fix-backlog-sanitized.md`、`next-input-request.md`、`synthetic-replay-plan.md`

---

## 1. Trial-001 Triage 摘要

- **Trial 结论**:3 个 skill 全部因输入不足降级(ai-analytics → degrade_with_gaps;prd2proto → degrade_with_gaps(partial);uxeval → supplement_required),但机制行为一致诚实,无脑补,无证据越界,gap 链完整,一票否决 0 命中。
- **主因**:输入材料是战略 MRD/执行 roadmap/文档位图,而非完整 PRD 正文+产品 UI 截图+页面状态。
- **8 个 sanitized issue**:5 个 mechanism_gap(护栏缺口),0 个输入不足本身,3 个 no_action(模板增强建议)。
- **核心发现**:机制行为正确(降级诚实),但缺显式 input_type / evidence_type 字段,靠"语义判断"区分材料类型,在自动化/半自动下存在误判风险(如把 roadmap 当 PRD、把文档位图当 UI 截图)。

---

## 2. P0 修复项

本批只修 P0 护栏(FB-01 / FB-02),不实现 P1(FB-03 / FB-04)。P0 共性:都是"降级路径护栏",不阻塞下一轮"质量上限测试"(给足输入时这些护栏根本不会触发)。

| ID | Issue | Skill | Priority | Fix Target |
|---|---|---|---|---|
| FB-01 | ISSUE-P1:prd2proto 缺前置输入类型识别(prd/roadmap/mrd) | prd2proto | P0 | `skills/prd2proto/templates/input-quality-gate.md` §2a |
| FB-02 | ISSUE-U1:uxeval 缺 evidence_type 校验(文档位图 vs 产品 UI) | uxeval | P0 | `skills/uxeval/templates/input-quality-gate.md` §2a |

---

## 3. FB-01 修复说明(ISSUE-P1 / prd2proto 输入类型识别)

### 问题描述(sanitized)
Trial-001 输入为执行 roadmap(里程碑+需求条目名+负责人+状态),信息密集但非 PRD 正文(缺页面清单/流程步骤/状态枚举)。prd2proto 最终行为正确(降级为 partial,停在模块级,不脑补页面),但模板缺显式 input_document_type 分类,用户可能在投入后才发现"给的是 roadmap 不是 PRD"。

### 修复内容
在 `skills/prd2proto/templates/input-quality-gate.md` §2 与 §3 之间新增 §2a(Input Document Type Classification),包含:
- `input_document_type` 枚举:`prd | mrd | roadmap | strategy_brief | mixed | unknown`。
- `document_type_confidence`:判定置信度。
- `document_type_reason`:为何判定为此类型(关键特征)。
- `minimum_prd_requirements_missing`:缺哪类 PRD 内容。
- `can_generate_prototype_from_input` 枚举:`yes | partial | no`。
- **守门规则**:roadmap/MRD 类 → `input_decision` 至多 `needs_user_clarification`(不得 `ready`);`can_generate_prototype_from_input=no` → `blocked_insufficient_input`。

### 影响范围
- **模板结构**:prd2proto input-quality gate 从 10 节(§1-10)变为 11 节(§1/§2/§2a/§4-11),其余 skill 维持 10 节。
- **validator**:`scripts/validate_input_quality_templates.py` 新增 `SKILLS_WITH_SECTION_2A = {"prd2proto", "uxeval"}`,对这两个 skill 预期 11 节,其余 skill 仍预期 10 节。
- **schema**:`schemas/feedback/diagnostic-summary.schema.json` 新增可选字段:`input_document_type / input_document_type_confidence / can_generate_prototype_from_input`(仅 prd2proto 填)。
- **diagnostic 模板**:`templates/diagnostic-summary.md` 新增 §2a(可选,仅 prd2proto 填)。
- **不改**:runtime / pipeline / kernel / prompts。

### 关联 FM / KR
- FM-PRD2PROTO-005(PRD 缺失信息记 gap 非脑补)— 守门规则联动。
- KR1.1(最低交付线)— roadmap 类无法达最低交付线,须早期告知。

---

## 4. FB-02 修复说明(ISSUE-U1 / uxeval evidence_type 校验)

### 问题描述(sanitized)
Trial-001 存在 PDF 分页位图(文档页面图,非产品 UI)。uxeval 最终行为正确(判 supplement_required,issue_count=0,不脑补),但模板缺显式 evidence_type 校验,靠语义判断区分"文档位图 vs 产品 UI",在自动化下存在误把文档图当 UI 证据的风险,直接关联 FM-UXEVAL-001(无证据 issue)/ FM-UXEVAL-003(PRD 推断当证据)两个 blocker。

### 修复内容
在 `skills/uxeval/templates/input-quality-gate.md` §2 与 §3 之间新增 §2a(Evidence Type Classification),包含:
- `evidence_type` 枚举:`product_ui_screenshot | web_capture | prototype_capture | document_screenshot | pdf_page_image | prd_text | mixed | unknown`。
- `evidence_type_confidence`:判定置信度。
- `evidence_type_reason`:为何判定为此类型(关键特征,如截图含应用 chrome vs 文档页眉)。
- `can_support_ux_evaluation` 枚举:`yes | partial | no`。
- `missing_ui_evidence`:需补哪些页面/状态截图。
- **守门规则**:document_screenshot / pdf_page_image / prd_text 类 → `can_support_ux_evaluation=partial`(仅需求理解,不可作 UX 问题证据);若无其他 UI 证据 → `blocked_insufficient_input`,`delivery_state=supplement_required`;FM-UXEVAL-001/003 预防。

### 影响范围
- **模板结构**:uxeval input-quality gate 从 10 节变为 11 节(同 prd2proto)。
- **validator**:同 FB-01,`SKILLS_WITH_SECTION_2A` 含 uxeval。
- **schema**:新增可选字段:`evidence_type / evidence_type_confidence / can_support_ux_evaluation`(仅 uxeval 填)。
- **diagnostic 模板**:§2a 包含 uxeval 段。
- **不改**:runtime / pipeline / kernel / prompts。

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

## 6. 影响范围

| 类别 | 改动文件 | 性质 |
|---|---|---|
| skill 模板 | `skills/prd2proto/templates/input-quality-gate.md` | 新增 §2a,原 §3-10 顺延为 §4-11 |
|  | `skills/uxeval/templates/input-quality-gate.md` | 新增 §2a,原 §3-10 顺延为 §4-11 |
| 脱敏产物模板 | `templates/diagnostic-summary.md` | 新增 §2a(可选,仅 prd2proto/uxeval 填) |
| 脱敏产物 schema | `schemas/feedback/diagnostic-summary.schema.json` | 新增 7 个可选字段(input_document_type 系+evidence_type 系) |
| 校验脚本 | `scripts/validate_input_quality_templates.py` | 允许 prd2proto/uxeval 有 11 节,其余 skill 仍 10 节 |
| 审计报告 | `docs/audits/S2-H9-TRIAL-001-GAP-FIX.md` | 新增(本文件) |

**未改**:
- runtime / kernel / pipeline / factory / release / npm / version / install。
- prompts(未新增约束)。
- 其余 skill(ai-analytics / ip-design / brand-creative)维持 10 节。
- workspace / private evidence / raw PRD / extracted PRD。

---

## 7. 验证结果

所有 validator 必须通过(见 §8 Checklist)。

---

## 8. 是否可以进入下一轮 Quality Ceiling Test

**是,推荐并行。**
理由:
1. FB-01/FB-02 修复了"降级路径护栏",但不触及"输入充分时的产出质量"。
2. Trial-001 全链降级主因是输入不足(缺 PRD 正文/UI 截图/页面状态),不是机制缺陷。
3. **下一轮给足输入**(核心需求 PRD 正文 + IA/流程步骤 + 产品 UI 截图 + 页面状态),FB-01/FB-02 护栏根本不会触发,因此不阻塞质量上限测试。
4. P1(FB-03/FB-04)可与质量上限测试并行修,非阻塞。

推荐顺序:
- **立即**:提交 FB-01/FB-02(本批,commit 但不 push)。
- **并行**:向用户索取充分输入(见 Triage `next-input-request.md`)+ 可选实施 FB-03/FB-04。
- **下一批**:Quality Ceiling Test(输入充分条件下验证产出质量上限)。

---

## 9. Validation Checklist

完整验证清单见 closeout。本批必须:
- `python3 scripts/validate_input_quality_templates.py` 通过(11 节 prd2proto/uxeval,10 节其余)。
- `python3 scripts/validate_feedback_safety_infrastructure.py` 通过(diagnostic schema 合法)。
- 其余 5 个 validators 通过(progressive/cross-skill/self-review/s2-h7b/paradigm)。
- `bash scripts/security/scan-sensitive.sh` 0 命中。
- `git diff --check` 无空白问题。
- `git ls-files` 无 workspace / private-evidence / raw-prd / .pdf / .zip。
