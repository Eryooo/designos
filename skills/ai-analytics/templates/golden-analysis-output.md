# Golden Output Template — ai-analytics

> **🚫 SYNTHETIC / SANITIZED ONLY** — 本模板及示例片段不含任何真实业务、真实客户、真实竞品价格、真实市场数据。所有示例都用 `Acme Demo` / `synthetic-competitor-A` / `[行业平均: inferred]` 等明显假名占位。
> **本模板性质**:分析输出规范,"中阶可用 + 资深目标"双层基准。
> **依据**:S2-H1 §2.3(ai-analytics rubric)+ S2-H1.1 §6.2.3(KR-A1~A5)+ `skills/ai-analytics/constitution.md`(4 条硬约束)+ `knowledge/manifest.yaml` 中 `research.*` 资产。
> **当前状态**:**maturity = pilot**;**prompt-grade,无 runtime/ 目录**;pilot 阶段仅稳产 `design_strategy` + `user_persona` 两个产物。

---

## 1. 输入前提

| 输入 | 强制 / 可选 | 说明 |
|---|---|---|
| `collected_data` | 强制 | 资料集合(竞品分析 / 市场报告 / 用户访谈 / PRD)(sanitized) |
| `analysis_scope` | 强制 | 分析范围说明(要产出什么类型的分析) |
| `methodology` | 可选 | JTBD / SWOT / PEST / AIPL / KANO 之一(不指定则自选) |

---

## 2. 输出目录结构 / Artifact 列表

```
ai-analytics-out/<run_id>/
├── collected_data/                  # 原始资料归档
│   ├── 01-竞品资料.md
│   ├── 02-用户访谈(synthetic).md
│   └── ...
├── data_completeness_assessment.json  # coverage 自评
├── design_strategy.json             # 核心产物 1:设计策略
├── user_persona.json                # 核心产物 2:用户画像
├── competitive_matrix.json          # 竞品对比矩阵
└── analysis_report.md               # 综合分析报告
```

> ⚠️ pilot 阶段 **仅 design_strategy + user_persona 必产**,其他产物可选。

---

## 3. 必填章节(design_strategy + user_persona)

### 3.1 design_strategy 必填字段(constitution #2)

```yaml
design_strategy:
  strategy_id: ...
  created_at: ...
  target_audience:        # ❗ 必填非空(constitution #2,KR-A2)
    primary: <具体描述>
    secondary: <...>
  business_goal:          # ❗ 必填非空
    - goal_id: BG-001
      description: <可被 prd2proto 消费的描述>
  design_principles:
    - principle_id: ...
  differentiation_statement:
    statement: <差异化定位,可追溯到竞品空白>
    evidence_refs: [...]  # 必须指向 collected_data 具体条目(KR-A1)
```

### 3.2 user_persona 必填字段(constitution #2)

```yaml
user_persona:
  - persona_id: P-001
    role: <角色名,可被 prd2proto 消费>
    goals: [...]          # ❗ 必填非空
    pain_points: [...]    # ❗ 必填非空
    demographics: {age_range: ..., occupation: ...}
```

---

## 4. 字段级要求

### 4.1 evidence_refs(KR-A1)
- **所有 findings / differentiation_statement 必须有 evidence_refs**,指向 `collected_data/` 中的具体条目
- 严禁出现 "竞品 A 定价 ¥99/月" 而 collected_data 中无竞品 A 价格信息(constitution #1:编造数据)

### 4.2 inferred_fields(KR-A5)
- 所有推断字段必须标 `[inferred]`,且附 rationale
- 示例:`"行业平均转化率 12% [inferred: 基于 SaaS Benchmark 2025 报告 p34 的中位数]"`

### 4.3 data_completeness_assessment.coverage(KR-A3)
- 必须 **真实反映** collected_data 的完整性
- `< 0.70` 触发 `QG1` 硬停(constitution #3)
- **严禁虚高**:实际 coverage 0.55 标成 0.85(KR-A3 一票否决)

### 4.4 not_in_scope(KR-A4)
- **严禁越界产出**:
  - ❌ 问题清单 + 严重度(uxeval 职责)
  - ❌ 代码 / 原型(prd2proto 职责)
- 可产出:竞品分析 / 市场定位 / 用户画像 / 设计策略 / 内容策略

---

## 5. 最低线标准(中阶可用 — KR-A1~A5)

| KR | 要求 |
|---|---|
| KR-A1 | 编造数据率 = 0(所有结论可追溯到 collected_data 具体条目) |
| KR-A2 | design_strategy / user_persona schema 必填字段非空率 = 100% |
| KR-A3 | data_completeness coverage ≥ 0.70;< 0.70 触发 QG1 硬停 |
| KR-A4 | 越界产出(代码/问题清单) = 0 |
| KR-A5 | 推断字段 `[inferred]` 标注覆盖率 ≥ 80% |

---

## 6. 目标线标准(资深可评审)

- **findings.evidence_refs 100% 反向校验通过**(每条 ref 都能在 collected_data 找到,KR-A1 目标线)
- **[inferred] 标注覆盖率 ≥ 95%**(KR-A5 目标线)
- **competitive_matrix 无大量 TBD**:单元格填充率 ≥ 80%,`TBD` / `?` / `未知` 占比 < 20%
- **design_strategy 不只是形容词**:target_audience 包含可消费的"年龄 / 职业 / 使用场景",不是只有"年轻人 / 科技感"
- **user_persona 不空洞**:每个 persona 有 ≥ 3 个 pain_points,不是只有姓名/年龄

---

## 7. 一票否决项检查表(V1-V4)

| # | 检查 | 触发条件 |
|---|---|---|
| **V1** 编造数据 | findings 中出现 collected_data 不存在的数据(如竞品定价 / 用户数 / 行业平均) | 直接拒绝交付 |
| **V2** 下游必填字段缺失 | `design_strategy.target_audience` / `business_goal` / `user_persona[].role / goals / pain_points` 为空 | 导致 prd2proto 注入失效,拒绝交付 |
| **V3** Coverage 虚高 | 实际 coverage < 0.70 却标 ≥ 0.70 | 拒绝交付 |
| **V4** 越界产出 | 产出问题清单 + 严重度 / 代码 / 原型 | 标"职责越界",拒绝交付 |

---

## 8. Gap / Assumption / Confidence / Traceability 规范

| 字段 | 规范 |
|---|---|
| `gaps[]` | 数据缺口明确记录(如"竞品 B 价格未找到") |
| `assumptions[]` | 推断的依据假设(如"假设行业平均适用于本场景") + `risk_if_wrong` 等级 |
| `confidence` | 整份分析的总体可靠性,基于 `data_completeness_assessment.coverage` |
| `traceability` | 每条 finding 必须有 `evidence_refs` 指向 `collected_data` 具体条目,且 ref 真实存在 |

---

## 9. 自评表(对账 KR)

```yaml
self_eval:
  KR-A1_no_fabrication:
    method: 反向校验 findings.evidence_refs → collected_data
    pass: <bool>
  KR-A2_required_fields_nonempty:
    actual: <必填字段非空数 / 总必填数>
    target: 100%
    pass: <bool>
  KR-A3_coverage_accuracy:
    reported_coverage: <data_completeness.coverage>
    target: ≥ 0.70
    actual_coverage: <抽审真实覆盖率>
    pass: <bool>
  KR-A4_out_of_scope_count:
    actual: <问题清单 / 代码出现次数>
    target: = 0
    pass: <bool>
  KR-A5_inferred_annotation:
    actual: <标 [inferred] 字段数 / 实际推断字段数>
    target: ≥ 80%
    pass: <bool>
  global_KR1.1_minimum_delivery:
    pass: <KR-A1~A4 是否全过>
  global_KR1.2_one_strike_count:
    pass: <V1~V4 是否全为 0>
  global_KR3.2_gap_annotation:
    pass: <gaps 是否显式记录>
```

---

## 10. 禁止声明清单

- ❌ "ai-analytics 可替代真实市场研究 / 用户访谈"
- ❌ "可作为产品决策唯一依据"
- ❌ "可用于财务/投资分析"
- ❌ "已接入 runtime"(实际 prompt-grade,无 runtime)
- ❌ "production ready" / "fully automated" / "完全自动化"

允许声明:

- ✅ "可消费 PRD 资料 + 竞品资料,产出可被 prd2proto 消费的 design_strategy / user_persona"
- ✅ "结构化的竞品对比框架,可追溯到来源条目"
- ✅ "适合作为 prd2proto 的上游分析输入"
- ✅ "pilot 阶段:仅稳定产出 design_strategy / user_persona 两个产物"

---

## 11. Synthetic 示例片段(中阶可用档,sanitized only)

> ⚠️ 所有数据为 synthetic;占位符:`Acme Demo SaaS`(假产品)、`synthetic-competitor-A`(假竞品)、`[inferred]` 显式标注。

### 11.1 design_strategy 中阶可用档示例

```yaml
design_strategy:
  strategy_id: DS-synth-001
  created_at: "2026-06-12T10:00:00Z"
  target_audience:
    primary: "小型企业 IT 管理员(10-50 人团队),日常负责服务器/数据库运维,希望减少重复手工操作"
    secondary: "DevOps 工程师,需自动化部署流程"
  business_goal:
    - goal_id: BG-001
      description: "3 个月内获取 500 家小企业试用,转化率 ≥ 20%"
      evidence_refs: ["collected_data/01-PRD-section-business.md#L45"]
  design_principles:
    - principle_id: DP-001
      principle: "减少手工操作步骤"
      rationale: "[synthetic] 用户访谈显示 80% IT 管理员抱怨 '重复配置浪费时间'"
      evidence_refs: ["collected_data/02-synthetic-user-interview.md#finding-003"]
  differentiation_statement:
    statement: "[synthetic] 专注小团队低学习成本,不做大企业复杂权限(竞品 A/B 都是大企业方案)"
    evidence_refs: [
      "collected_data/competitive-matrix.json#competitor-A-target-large-enterprise",
      "collected_data/competitive-matrix.json#competitor-B-target-large-enterprise"
    ]
  confidence: 0.68
  gaps:
    - "[synthetic] 竞品 C 价格未找到,无法对比定价策略"
```

### 11.2 user_persona 中阶可用档示例

```yaml
user_persona:
  - persona_id: P-001
    role: "小型企业 IT 管理员"
    goals:
      - "减少每日重复运维操作时间"
      - "快速响应业务部门的服务器配置需求"
    pain_points:
      - "[synthetic] 每次配置新服务器需手工执行 20+ 步骤,耗时 1 小时"
      - "[synthetic] 现有工具学习成本高,团队没有专职 DevOps"
      - "[synthetic] 频繁出错导致回滚,影响业务稳定性"
    demographics:
      age_range: "28-45"
      occupation: "IT 管理员 / 系统工程师"
      team_size: "10-50 人"
    evidence_refs: [
      "collected_data/02-synthetic-user-interview.md#persona-001"
    ]
```

### 11.3 data_completeness_assessment 示例

```yaml
data_completeness_assessment:
  coverage: 0.72   # ≥ 0.70 通过 QG1
  dimensions:
    competitor_analysis: 0.80
    user_research: 0.60  # 低,标 gap
    market_trend: 0.75
  gaps:
    - dimension: "user_research"
      description: "[synthetic] 用户访谈样本仅 5 人,未覆盖大企业 IT 管理员"
      impact: "medium"
      mitigation: "标注 target_audience 限定 '小型企业',不过度推广"
```

---

*template 结束。配套主报告:`docs/audits/S2-H2-GOLDEN-OUTPUT-TEMPLATES.md`。*
