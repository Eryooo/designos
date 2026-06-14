# S1-0B Audit — Declared vs Implemented Coverage（5 Skills）

> **本报告性质**:审计 5 个 skill 在 `knowledge-manifest.yaml` 中**声明引用**的 shared-knowledge 资产,与其在 `prompts / reference / pipeline / runtime / schema / tests` 中的**实现证据**之间的差距。只审计不改造。
> **真源依据**:`knowledge/manifest.yaml`(经 `S1-0B-STANDARD-SOURCE-OF-TRUTH-DECISION.md` 裁定为 active source-of-truth)。
> **方法**:严格按资产 id 字符串扫描 skill 目录;辅以人工核实区分「显式 id 锚定」与「隐式 reference 锚定」。
> **日期**:2026-06-12

---

## 0. 状态判定口径

| 状态 | 定义 |
|---|---|
| `implemented` | 资产 id 在 skill 的 prompt/reference/pipeline 中**显式锚定**(id 字符串出现),manifest traceability 有效 |
| `partially_implemented` | 方法论**实质实现**于私有 reference(如 `reference/m0X-*.md`),但 manifest 资产 id **未被显式锚定** → 实现存在但不可追溯到 manifest |
| `declared_only` | manifest 声明引用,但 skill 目录内**无任何实现证据**(prompt/reference/pipeline 均无对应方法论正文) |
| `not_applicable` | 该维度对此 skill 不适用(如 group skill 无 root pipeline) |
| `unknown` | 证据不足,无法判定(需人工深读才能确认) |

> **重要方法论说明**:本审计用 id 字符串作为「可追溯锚定」的客观信号。「未锚定 id」不等于「未实现方法论」——prd2proto/uxeval/ai-analytics 通过私有 `reference/m0X` 文件实现方法论,但因为不引用 manifest id,manifest 的 `applicable_skills` 字段对它们而言是**孤悬声明**。这是 declared-vs-implemented 的核心缺口。

---

## 1. 全局结论

### 1.1 两种实现锚定模式

| 模式 | 含义 | 采用 skill | traceability |
|---|---|---|---|
| **显式 id 锚定** | prompt 直接引用 `<domain>.<slug>` id | ip-design | ✅ manifest 可追溯 |
| **隐式 reference 锚定** | prompt 引用私有 `reference/m0X-*.md`,不提 id | prd2proto / uxeval / ai-analytics | ❌ manifest 不可追溯 |
| **基本未实现** | 无 root pipeline/prompts,方法论未落地 | brand-creative(主线) | ❌ |

### 1.2 资产锚定命中率（严格 id 扫描）

| skill | 声明资产 | 显式 id 命中 | 命中率 | 实际实现模式 |
|---|---|---|---|---|
| prd2proto | 11 | 0 | 0% | 隐式(reference/m01–m06 + prompts-v2) |
| uxeval | 7 | 0 | 0% | 隐式(reference/m01–m06 中文私有文件) |
| ai-analytics | 6 | 0 | 0% | 隐式(reference/m01–m06) |
| **ip-design** | 19 | **18** | **95%** | **显式 id 锚定**(prompt 内 `` `id`(M0X) ``) |
| brand-creative | 14 | 1 | 7% | 主线未实现(仅 tests 命中 1) |

### 1.3 runtime / quality-gate / artifact-base 接入

| skill | runtime 目录 | 真执行 kernel quality-gates | pipeline gate 类型 | artifact-base 继承 |
|---|---|---|---|---|
| prd2proto | ✅ 7 文件 | ✅ `quality_gates:`(10处)+ runtime import | **quality_gates(真质量门)** | 部分:3/7 schema `$ref` |
| uxeval | ❌ | ❌ 无 runtime | **gate(暂停门/checkpoint 语义)** | ❌ 无 schemas/ |
| ai-analytics | ❌ | ❌ 无 runtime | **gate(暂停门语义)** | ❌ 无 schemas/ |
| ip-design | ❌ | ❌ 无 runtime | **gate(暂停门语义)** | ❌ 无 schemas/ |
| brand-creative | ❌ | ❌ | 子 skill 各自 pipeline | ❌(用 16 个 contracts/) |

> ⚠️ **gate vs quality_gates 语义区分(重要)**:只有 prd2proto 用 `quality_gates:` 字段并由 runtime 真实调用 `kernel/quality-gates`。uxeval/ai-analytics/ip-design 用的是 `gate:`(单数)——这是 pipeline 的**暂停门 / checkpoint 语义**,**不是 kernel 质量门**,且无 runtime 执行体。不应将它们计为「已接入统一质量门」。

### 1.4 status.matrix maturity 核验

| skill | matrix maturity | 审计后是否合理 | 备注 |
|---|---|---|---|
| uxeval | beta | ⚠️ 偏高 | 有完整 prompts+eval,但无 runtime、id 未锚定、无质量门执行——「beta」对无 runtime 的 skill 偏乐观 |
| prd2proto | pilot | ✅ 合理 | 唯一有 runtime + 真质量门,pilot 准确 |
| ai-analytics | pilot | ✅ 合理 | prompts 存在但无 runtime,pilot 合理 |
| ip-design | pilot | ✅ 合理偏保守 | id 锚定最规范,但无 runtime,pilot 合理 |
| brand-creative | alpha | ✅ 准确 | 主线未实现,alpha 准确 |

---

## 2. 逐 Skill 审计

### 2.1 prd2proto（matrix: pilot）

**声明资产(11)**:`product.prd-understanding` / `product.user-story-mapping` / `product.information-architecture` / `product.interaction-state-coverage` / `frontend.atomic-design` / `frontend.design-token-rules` / `frontend.component-state-rules` / `frontend.code-quality-constitution` / `design.design-strategy` / `design.design-template-selection` / `design.tone-and-visual-direction`

| 维度 | 证据 | 状态 |
|---|---|---|
| 显式 id 锚定 | 11 个资产 id 在 prompt/reference **零命中** | declared_only(id 层) |
| 方法论实现 | `reference/m01-prd-understanding.md` … `m06-review-gate.md` + `prompts-v2/`(18 文件)实质实现 | partially_implemented(实现层) |
| pipeline gate | `quality_gates:`(10 处)——真质量门字段 | implemented |
| runtime quality-gates | `runtime/executor.py` + `executor_interactive.py` import `kernel/quality-gates/gates.py`,捕获 `QualityGateBlocked` | implemented |
| runtime traceability | 3 个 runtime 文件 import `kernel/traceability` | implemented |
| artifact-base 继承 | 7 schema 中 **3 个 `$ref` base**(business-flow / product-archetype / requirement-inventory);**4 个未继承**(design-traceability-map / interaction-rules / page-flow / page-structure) | partially_implemented |
| tests | 有 tests + golden-cases | implemented |

**综合判定**:**全链路接入最强的 skill**(唯一有 runtime + 真质量门 + traceability)。两个缺口:① 11 个共享资产 id 全未锚定(manifest 不可追溯,方法论靠私有 reference 实现);② 4/7 schema 未继承 artifact-base。

---

### 2.2 uxeval（matrix: beta）

**声明资产(7)**:`ux.heuristic-principles` / `ux.journey-modeling` / `ux.evidence-quality` / `ux.severity-rubric` / `ux.issue-attribution` / `ux.ux-failure-modes` / `product.interaction-state-coverage`

| 维度 | 证据 | 状态 |
|---|---|---|
| 显式 id 锚定 | 7 个资产 id **零命中** | declared_only(id 层) |
| 方法论实现 | `reference/m01-需求理解.md` … `m06-问题归因.md`(中文私有文件)+ prompt 引用 `reference/m02-启发式原则.md` 等 | partially_implemented(实现层) |
| pipeline gate | `gate:`(4 处)——**暂停门语义,非 kernel 质量门** | not_applicable(质量门维度) |
| runtime | **无 runtime/ 目录** | declared_only |
| artifact-base | 无 schemas/ 目录(输出靠 templates/)→ 未继承统一 I/O 基座 | not_applicable / 未接入 |
| tests / eval | 有 tests + eval | implemented |

**综合判定**:方法论实现充分(prompts + 私有 reference),但 ① id 未锚定;② 无 runtime;③ pipeline 的 `gate:` 是暂停门不是质量门;④ 输出未继承 artifact-base。**maturity「beta」对一个无 runtime 的 skill 偏乐观**,建议复核口径。

---

### 2.3 ai-analytics（matrix: pilot）

**声明资产(6)**:`research.methodology-selection` / `research.competitor-analysis` / `research.user-persona-quality` / `research.data-completeness-rubric` / `design.design-strategy` / `design.tone-and-visual-direction`

| 维度 | 证据 | 状态 |
|---|---|---|
| 显式 id 锚定 | 6 个资产 id **零命中** | declared_only(id 层) |
| 方法论实现 | `reference/m01-requirement-understanding.md` … `m06-report-generation.md` + prompts(7) | partially_implemented(实现层) |
| pipeline gate | `gate:`(1 处)——暂停门语义 | not_applicable(质量门维度) |
| runtime | **无 runtime/ 目录** | declared_only |
| artifact-base | 无 schemas/(有 templates/ 2 json) | 未接入 |
| tests / eval | 有 | implemented |

**综合判定**:与 uxeval 同构——隐式 reference 实现,无 runtime,id 未锚定。pilot 合理。

---

### 2.4 ip-design（matrix: pilot）

**声明资产(19)**:见下表。

| 维度 | 证据 | 状态 |
|---|---|---|
| 显式 id 锚定 | **18/19 资产 id 在 prompts 显式锚定**(如 `prompts/03-persona-modeling.md`:`` `design.persona.persona-modeling`(M03):... ``),且 reference/tests/pipeline 同步命中 | **implemented** |
| 唯一未命中 | `design.ip.methodology` 仅 tests 命中(prompt 未直接引 id) | partially_implemented |
| reference 模式 | `reference/adapter-*.md`(adapter 形式,把通用方法论适配到本 skill stage) | implemented |
| pipeline gate | `gate:`(2 处)——暂停门语义 | not_applicable(质量门维度) |
| runtime | **无 runtime/ 目录** | declared_only |
| artifact-base | 无 schemas/(用 templates/) | 未接入 |
| tests / eval | 有 | implemented |

**综合判定**:**id 锚定规范度最高的 skill**(95% 显式可追溯,manifest traceability 有效)——是其他 skill 应学习的锚定范式。缺口与同类一致:无 runtime、`gate:` 非质量门、未继承 artifact-base。

---

### 2.5 brand-creative（matrix: alpha）

**声明资产(14)**:`design.strategy.brand-strategy-methodology` / `design.visual.logo-design-methodology` / `design.visual.logo-cognitive-translation` / `design.visual.color-system-methodology` / `design.visual.typography-system-methodology` / `design.visual.visual-identity-integration-methodology` / `design.strategy.brand-audit-methodology` / `design.strategy.brand-voice-methodology` / `design.quality.brand-identity-quality-rubric` / `design.quality.brand-creative-failure-modes` / `research.competitor-analysis` / `design.persona.voice-and-behavior-boundary` / `design.visual.image-prompt-system` / `design.quality.professional-gap-report`

| 维度 | 证据 | 状态 |
|---|---|---|
| 结构 | **group skill**:`GROUP.md` + 13 sub-skills + 16 contracts json,**无 root pipeline.yaml** | not_applicable(root pipeline) |
| 显式 id 锚定 | 14 资产中 **仅 1 命中**(`design.quality.brand-identity-quality-rubric`,仅 tests) | declared_only(13 项) |
| sub-skills 实现 | 13 子 skill 中 **6 个有 pipeline.yaml**(brand-strategy/color-system/competitive-analysis/logo-design/typography-system/visual-identity),**7 个空**(brand-audit/brand-collateral/brand-guidelines/brand-voice/campaign-creative/content-strategy/digital-assets) | partially_implemented(46% 子 skill 有 pipeline) |
| root prompts / runtime / constitution | 均无 | declared_only |
| artifact-base | 用 16 个 contracts json,未确认继承 base | unknown |

**综合判定**:**主线框架未成型**(group 骨架 + 半数子 skill 有 pipeline,但无 root prompts/runtime/constitution)。alpha 准确。14 个声明资产基本是 declared_only。

---

## 3. 缺口汇总（按类型）

### 3.1 manifest traceability 断裂（最普遍）
- prd2proto / uxeval / ai-analytics:声明的 **24 个资产 id 全部未在实现层锚定**——manifest `applicable_skills` 对这 3 个 skill 是孤悬声明。
- 方法论**实质实现了**(私有 reference),但无法从 manifest id 追溯到实现。

### 3.2 runtime 覆盖 1/5
- 仅 prd2proto 有 runtime + 真质量门 + traceability。
- uxeval/ai-analytics/ip-design 无 runtime,pipeline 的 `gate:` 是暂停门非质量门。

### 3.3 artifact-base 统一 I/O 覆盖薄弱
- 仅 prd2proto 部分继承(3/7)。
- 其余 skill 无 schemas/,未接入统一 I/O 基座。

### 3.4 status.matrix 口径
- uxeval「beta」对无 runtime 的 skill 偏乐观,建议复核。
- 其余 maturity 合理。

---

## 4. 哪些是本地证据确认 / 哪些 unknown

**本地证据已确认**:
- 5 skill 的 id 锚定命中率(严格字符串扫描 + 人工抽查)。
- prd2proto 唯一 runtime + quality_gates + traceability(grep import 证据)。
- gate vs quality_gates 字段区分(pipeline.yaml 直读)。
- artifact-base 继承 3/7(逐文件 grep `$ref`)。
- brand-creative 6/13 子 skill 有 pipeline。

**unknown / 需深读才能确认**:
- prd2proto/uxeval/ai-analytics 的私有 `reference/m0X` 是否**内容上**等价于声明的共享资产(本审计只验 id 锚定,未逐句比对方法论正文)。
- brand-creative 16 个 contracts json 是否继承 artifact-base(未逐个 `$ref` 核验)。
- uxeval `gate:` 暂停门是否在某处被 runtime 外的机制执行(本地无 runtime,推定未执行,但未穷尽 kernel 调用链)。

---

## 5. 给后续批次的最小建议（仅建议，不执行）

| 优先级 | 建议 | 对应缺口 |
|---|---|---|
| P0 | 为 prd2proto/uxeval/ai-analytics 的私有 reference 补 manifest id 锚定(在 reference/prompt 头部标 `> 对应共享资产:<id>`),恢复 traceability | §3.1 |
| P1 | 复核 uxeval maturity(beta→是否降级,或补 runtime) | §3.4 |
| P1 | prd2proto 4 个未继承 base 的 schema 补 `$ref` | §3.3 |
| P2 | status.matrix 增加 `shared_knowledge_anchored`(id 锚定率)字段,表达 traceability 覆盖 | §3.1 |
| P2 | brand-creative 主线(root pipeline/prompts)补齐前,不宜提升 maturity | §2.5 |

⚠️ 全部留作建议。S1-0B 只审计不改造。

---

## 6. 与 S1-0A 报告的订正关系

S1-0B 的逐字段实证**精化并订正**了 S1-0A(`S1-0A-EXISTING-FOUNDATION-INVENTORY.md`)的若干结论。两份报告并存时,**以 S1-0B 为准**:

| # | S1-0A 原结论 | S1-0B 实证订正 | 影响 |
|---|---|---|---|
| 1 | S1-0A §3 把 uxeval/ai-analytics/ip-design 的 pipeline gate 计为「质量门」(4/1/2 处) | 它们是 `gate:`(暂停门/checkpoint 语义),**非 kernel 质量门**;只有 prd2proto 用 `quality_gates:` 且 runtime 真执行 | 「质量门覆盖」严格为 **1/5**,不是「3 个 skill 声明了 gate」 |
| 2 | S1-0A §3 表述「prd2proto schema 真 `$ref` 继承 base」(读感为全部) | 实际 **3/7 继承**,4 个未继承(design-traceability-map / interaction-rules / page-flow / page-structure) | artifact-base 遵守度更低 |
| 3 | S1-0A §10 把 ip-design 与 uxeval/ai-analytics 同列「声明已接入」 | ip-design 实为 **id 锚定最规范者(18/19 implemented)**,显著优于另两者 | ip-design 被 S1-0A 低估;它是 id 锚定范式样板 |
| 4 | S1-0A 多处称 design-work-paradigm「41 方法文件」 | 实为 **40 个 .md**(README 不计);且其 manifest 仅登记 20、含 15 处大小写不一致 | 计数订正 + 暴露 paradigm manifest 自身失效(S1-0A 未查) |

> S1-0A 的**框架性结论全部成立**(四大统一对标、prd2proto 唯一全链路、标准双源冲突);S1-0B 仅订正上述**计数与语义精度**问题。两者是「盘点 → 精化审计」的承接关系,非矛盾。

---

*配套矩阵见 `docs/audits/S1-0B-COVERAGE-MATRIX.md`。*
