# Golden Output Template — prd2proto

> **🚫 SYNTHETIC / SANITIZED ONLY** — 本模板及示例片段不含任何真实业务、真实客户、真实截图、真实内部链接。所有示例字符串都用 `Acme Demo` / `synthetic-product` 等明显假名占位。
> **本模板性质**:输出规范的"中阶可用 + 资深目标"双层基准。**不是 prompt,不是 schema,不是真实 case**。
> **依据**:S2-H1 §2.1(prd2proto rubric)+ S2-H1.1 §6.2.1(KR-P1~P5)+ `skills/prd2proto/constitution.md` + `knowledge/design/quality/*` + `knowledge/design-work-paradigm/17-quality-rubrics.md`。
> **当前状态**(per status.matrix):**maturity = pilot,runtime-grade**(全 5 skill 中唯一)。runtime 已通跑前 5+ stage,18 stage 全链路 validated 待 trial。

---

## 1. 输入前提

跑 prd2proto 前必须满足:

| 输入 | 强制 / 可选 | 说明 |
|---|---|---|
| `prd_file` | 强制 | PRD/简报文档(md/pdf 等) |
| `prd_content` | 强制(可由 prd_file 解出) | PRD 全文 |
| `scope_md` | 可选 | 范围说明 |
| `mode` | 强制 | `pm` / `designer-spec` / `designer-dsl` 之一 |
| `existing_personas` | 可选(若存在则需符合 schema) | 来自 ai-analytics 的上游 |
| `design_strategy` | 可选(若存在则需符合 schema) | 来自 ai-analytics 的上游 |

---

## 2. 输出目录结构 / Artifact 列表

按 pipeline v2.0.0-p1 18 stage 顺序产出:

```
prd2proto-out/<run_id>/
├── 01-requirement_inventory.json          # input-diagnosis
├── 02-design_objectives.json              # design-objectives
├── 03-product_archetype.json              # product-archetype
├── 04-user_task_map.json                  # user-task-modeling
├── 05-business_flow.json                  # business-flow-modeling
├── 06-journey_map.json                    # user-journey-mapping
├── 07-information_architecture.json       # information-architecture
├── 08-page_flow.json                      # page-flow
├── 09-page_structure.json                 # page-structure
├── 10-component_strategy.json             # component-strategy
├── 11-state_matrix.json                   # state-matrix
├── 12-interaction_rules.json              # interaction-rules
├── 13-design_spec.md                      # design-spec-generation
│                                          # (designer-dsl 模式跳过)
├── 14-design_tokens.json                  # token-extraction (W3C DTCG)
├── 15-prototype_code/                     # constrained-code-generation
│   ├── package.json
│   └── src/
├── 16-traceability_map.json               # traceability-generation
├── 17-professional_gap_report.json        # professional-gap-assessment
└── liveness-check.log                     # liveness-check (dev_url 探活)
```

> ⚠️ 全 18 个产物均必须**通过对应 schema 校验**(`kernel/contracts/artifacts/*.schema.json`)——这是 KR-P5 + KR1.4 的硬约束。

---

## 3. 必填章节(每个 artifact 都要有)

每个 JSON artifact 必须含 **artifact-base 通用元数据**(prd2proto 的 7 个 schema 全部继承,3 direct + 4 transitive,见 S2-2):

```json
{
  "artifact_id": "...",
  "artifact_type": "...",
  "skill_id": "prd2proto",
  "run_id": "run-xxx",
  "created_at": "2026-...",
  "maturity": "draft | reviewable | validated | deprecated",
  "confidence": 0.0..1.0,
  "source_inputs": [...],
  "inferred_fields": [...],
  "gaps": [...],
  "warnings": [...],
  "assumptions": [...],
  "traceability": {
    "upstream_artifacts": [...],
    "decision_trace": [...],
    "evidence_map": {...}
  },
  "validation_status": {...},
  "metadata": {...}
}
```

---

## 4. 字段级要求(关键字段)

### 4.1 confidence
- 必填,`number`,`0.0..1.0`,反映该 artifact 整体置信度
- < 0.5:严重不足,触发 `gap_transparency_gate`(参 S1-0B/0C 校准:这是 kernel 真 blocking)

### 4.2 inferred_fields
- 必填(可空数组),所有推断字段的 JSON Path 列表
- 触发 `inference_limit_gate`:推断比例 ≥ 0.30 → warning;≥ 0.50 → blocked

### 4.3 gaps
- 必填(可空数组),每条 gap 含 `gap_id` (`GAP-\d{3}`)+ `category` + `description` + `impact` (`critical/high/medium/low`)
- impact = `critical` 时整个 stage 进入 `blocked` 状态,触发 `gap_transparency_gate`

### 4.4 traceability.decision_trace
- 关键决策(IA / page-flow / state-matrix / component-strategy)必填,每条含 `decision_id` + `decision_point` + `rationale` + `evidence`
- `evidence` 不可为空(KR-P4 硬约束:关键决策追溯率 100%)

### 4.5 quality_gates(pipeline.yaml 真接 kernel)
- 关键 stage 必须显式声明 `quality_gates:` 字段(列表,kernel 真 blocking 字段;**不是** `gate:` 暂停门)
- `constrained-code-generation` stage 必含 `code_constraint_gate`(KR-P3 触发点)

---

## 5. 最低线标准(中阶可用 — KR-P1~P5)

| KR | 要求 |
|---|---|
| KR-P1 | 18 stage 全产出(designer-dsl 17),无 stage 缺失 |
| KR-P2 | 每个带 `quality_gates:` 的 stage 通过 schema 校验,`QualityGateBlocked` 触发率 < 20% |
| KR-P3 | `code_constraint_gate` 触发后修正再 pass 率 ≥ 80% |
| KR-P4 | `traceability_map.decision_trace` 中 IA / page-flow / state-matrix / component-strategy 的 evidence 非空率 ≥ 80% |
| KR-P5 | 7 schema 全部继承 artifact-base(已实证 100%) |

---

## 6. 目标线标准(资深可评审)

- 9 维 rubric 自评(参 `knowledge/design-work-paradigm/17-quality-rubrics.md`)全部 ≥ "中阶可用",其中 Strategic Alignment / Design Reasoning Depth / Internal Consistency 至少 1 项达 "高阶可评审"
- `traceability_map` 关键决策追溯率 = 100%(KR-P4 目标线)
- `professional_gap_report` 9 维全自评 + 显式列出"距资深差距"
- `inferred_fields` 比例 < 0.20

---

## 7. 一票否决项检查表(V1-V4)

| # | 检查 | 触发条件 |
|---|---|---|
| **V1** Schema 违约 | 任一 stage artifact 未通过对应 `kernel/contracts/artifacts/*.schema.json` | 直接拒绝交付,返工 |
| **V2** Traceability 断裂 | 关键决策(IA/page-flow/state-matrix/component-strategy)无 evidence | 直接拒绝 |
| **V3** 代码宪法违反 | 生成代码出现:硬编码颜色/字号、绕过 design-tokens、自建非组件库 div、未覆盖 7 状态 | `code_constraint_gate` 拦截 |
| **V4** Honesty 违反 | 推断字段未标 `[inferred]`,或 gaps/warnings 缺失,或 confidence 虚高 | `gap_transparency_gate` 拦截 |

---

## 8. Gap / Assumption / Confidence / Traceability 规范

| 字段 | 规范 |
|---|---|
| `gaps[]` | 每条必含 `gap_id` (`GAP-\d{3}`)+ category + description + impact + affected_fields + mitigation |
| `assumptions[]` | 每条必含 `assumption_id` (`ASM-\d{3}`)+ description + rationale + validation_method + risk_if_wrong |
| `confidence` | 0.0..1.0,反映该 artifact 整体可靠性;**严禁** > 0.95 除非已通过 multi-case 验证 |
| `traceability.upstream_artifacts[]` | 每条必含 artifact_id + artifact_type + relationship |
| `traceability.decision_trace[]` | 关键决策必含 evidence;evidence 来源类型限于:`prd_reference / user_research / industry_best_practice / heuristic / inferred` |

---

## 9. 自评表(对账 KR)

跑完 prd2proto 后用本表对账:

```yaml
self_eval:
  KR-P1_18_stage_completion:
    actual: <实际产出 stage 数>
    target: 18  # designer-dsl 17
    pass: <bool>
  KR-P2_schema_blocking_rate:
    actual: <QualityGateBlocked 触发率>
    target: < 20%
    pass: <bool>
  KR-P3_code_constraint_recovery:
    actual: <gate 拦截后修正再 pass 率>
    target: ≥ 80%
    pass: <bool>
  KR-P4_traceability_evidence_coverage:
    actual: <decision_trace.evidence 非空率>
    target: ≥ 80%
    pass: <bool>
  KR-P5_artifact_base_inheritance:
    actual: 7/7  # 已实证
    target: 100%
    pass: true
  global_KR1.1_minimum_delivery:
    pass: <KR-P1~P4 是否全过最低线>
  global_KR1.2_one_strike_count:
    pass: <V1~V4 是否全为 0>
  global_KR3.3_traceability:
    pass: <KR-P4 是否过>
```

---

## 10. 禁止声明清单(`not_allowed_claims`)

模板自身、引用本模板的产物、relevant docs 不得出现:

- ❌ "prd2proto 已达资深交互设计师水平"
- ❌ "可生成可直接用于生产的代码"
- ❌ "无需人工复核"
- ❌ "可替代资深设计师"
- ❌ "production ready" / 全自动无人值守 / 无需人工干预的自动化
- ❌ "已稳定通过真实业务多 case 验证"(除非有实证 commit)

允许声明:

- ✅ "prd2proto 是 DesignOS 当前最深的资深化样板,真接入 kernel/quality-gates"
- ✅ "pipeline v2 18 stage 中 prd2proto 是唯一 runtime-grade skill"
- ✅ "可作为资深设计师评审起点"

---

## 11. Synthetic 示例片段(中阶可用档,sanitized only)

> ⚠️ 以下所有数据均为 synthetic 示例,**不含任何真实业务、真实客户、真实截图**。占位符:`Acme Demo`(假产品名)、`synthetic-prd-001`(假文档 ID)。

### 11.1 input-diagnosis 输出片段(中阶可用档)

```json
{
  "artifact_id": "requirement-inventory-20260612-synth0001",
  "artifact_type": "requirement_inventory",
  "skill_id": "prd2proto",
  "run_id": "run-synth-001",
  "created_at": "2026-06-12T10:00:00Z",
  "maturity": "draft",
  "confidence": 0.72,
  "source_inputs": [
    {"input_type": "prd", "input_id": "synthetic-prd-001", "input_status": "partial", "quality_score": 0.65}
  ],
  "input_materials": {
    "primary": {"type": "prd", "file_path": "synthetic-prd-001.md", "format": "markdown", "quality_score": 0.65, "readability": "medium"}
  },
  "completeness_assessment": {
    "overall_score": 0.68,
    "dimensions": {
      "business_goals_clarity": 0.80,
      "user_definition_clarity": 0.60,
      "functional_requirements_completeness": 0.75
    }
  },
  "gaps": [
    {"gap_id": "GAP-001", "category": "ambiguous_requirement",
     "description": "[synthetic] 'Acme Demo dashboard' 未指定布局密度",
     "impact": "medium", "mitigation": "默认采用 antd-pro 中等密度"}
  ],
  "ambiguities": [
    {"ambiguity_id": "AMB-001", "description": "[synthetic] 用户角色仅写 'admin user',未细分权限",
     "affected_areas": ["permission_model"], "risk_if_wrong": "high"}
  ],
  "readiness_decision": {"decision": "proceed", "rationale": "完整性 ≥ 0.65 阈值,可继续(低 impact gap 已记录)"}
}
```

### 11.2 traceability_map 决策片段(中阶可用档)

```json
{
  "decision_trace": [
    {
      "decision_id": "DEC-IA-001",
      "decision_point": "IA 主导航分 3 段(workspace / settings / help)",
      "rationale": "[synthetic] 用户任务地图显示 80% 任务集中在 workspace,settings/help 为低频",
      "evidence": [
        {"source": "user_task_map.json#primary_tasks", "reference": "8/10 任务在 workspace"},
        {"source": "knowledge/design/design-template-selection", "reference": "antd-pro 标准 3 段导航"}
      ]
    }
  ]
}
```

---

*template 结束。配套主报告:`docs/audits/S2-H2-GOLDEN-OUTPUT-TEMPLATES.md`。*
