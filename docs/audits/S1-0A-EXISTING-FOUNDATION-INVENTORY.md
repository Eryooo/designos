# S1-0A — 现有统一底座盘点 + 四大统一目标对标分析

> **本报告性质**:只读盘点 + 对标分析,不改造任何业务代码/runtime/pipeline。
> **盘点范围**:开发源仓库 `Agent-design-webmode`(feature/senior-designer-paradigm-engine 分支)。
> **核验边界**:npm registry、公网 GitHub 仓库的实际状态属于**外部系统**,本地无法核验,相关项标注「待外部核验」。
> **日期**:2026-06-12

---

## 1. Executive Summary（执行摘要）

**一句话结论**:DesignOS 的统一底座**不是缺失,而是已建成约 90%,但只有 1 个 skill(prd2proto)真正全链路接入**;真正的工程债不在「建标准/建内核」,而在「source-of-truth 双源未裁定 + 声明 vs 实现从未审计 + 强制层覆盖仅 1/5」。

**四个最重要的判断**:

1. **底座已存在**:`knowledge/`(2 套方法体系)+ `kernel/contracts/`(11 接口 + 22 artifact schema)+ `kernel/quality-gates`(真 blocking)+ `kernel/traceability` + `.factory/`(archetype + 3 工具)+ `.claude/skills/`(4 治理 skill)+ `status.matrix` 已经构成完整六层底座。

2. **prd2proto 是唯一全链路接入者**:它继承 `artifact-base`、pipeline 引用 gate、runtime `import` 并调用 `kernel/quality-gates` 与 `kernel/traceability`。其余 4 个 skill 主要停留在 knowledge-manifest 的**声明层**。

3. **暴露两个原计划未预见的双源风险**:
   - **标准双源**:`design-work-paradigm/`(`manifest.yaml` 登记 20 方法,目录另有 20–39 扩展文件)vs `knowledge/manifest.yaml`(51 资产、`domain.slug` 命名)。
   - **Schema 双源**:`skills/prd2proto/schemas/`(7 个)与 `kernel/contracts/artifacts/`(22 个)部分重复。

4. **"声明 vs 实现"是核心缺口**:uxeval / ai-analytics / ip-design 的 `pipeline.yaml` **都声明了 pipeline gate/pause 门**(分别 4/1/2 处),但**都没有 runtime 目录**去执行这些门控语义;它们也不是 prd2proto 所接入的 `kernel/quality-gates` 执行器。声明存在,执行未证实。

**因此本轮确认:之前计划新建的 `SENIOR-CAPABILITY-STANDARD.md` / `SENIOR-DESIGN-METHODOLOGY-KERNEL.md` / `skill-capability.schema.json` / `kernel/seniorcap/*` / 独立 validator,全部不应新建**——它们会制造第二套真源。正确方向是裁定双源、审计覆盖、扩展现有体系。

---

## 2. 当前 DesignOS 统一底座全景图

```
┌──────────────────────────────────────────────────────────────────────┐
│ L1 知识层 Knowledge                                                    │
│   knowledge/manifest.yaml          (shared-knowledge, 51 资产)  ← 活体系│
│   knowledge/design-work-paradigm/  (manifest 登记 20 方法 + 目录扩展文件)│
│   knowledge/{design,ux,product,frontend,research}/  (资产正文真源)     │
├──────────────────────────────────────────────────────────────────────┤
│ L2 契约层 Contract                                                     │
│   kernel/contracts/interfaces.py   (11 个冻结接口, ADR 治理)           │
│   kernel/contracts/schemas.py      (共享数据 schema)                   │
│   kernel/contracts/artifacts/      (22 个 artifact schema + base)      │
│   .factory/archetypes/             (4 archetype: eval/gen/analysis/    │
│                                     creative-gen; generation 为 provisional)│
├──────────────────────────────────────────────────────────────────────┤
│ L3 内核层 Kernel Module                                                │
│   kernel/skill_loader  pipeline  quality-gates(真 blocking)           │
│   kernel/traceability  preflight  checkpoint  llm  memory  output …    │
├──────────────────────────────────────────────────────────────────────┤
│ L4 工厂层 Factory                                                      │
│   .factory/CONTRACT.md  (复用率≥80% 目标, 5 道验收门)                  │
│   .factory/tools/  extract.py / validate.py / scaffold.py             │
├──────────────────────────────────────────────────────────────────────┤
│ L5 治理层 Governance                                                   │
│   .claude/skills/  governor / closeout / knowledge-architect /        │
│                    skill-factory                                       │
├──────────────────────────────────────────────────────────────────────┤
│ L6 状态层 Readiness                                                    │
│   skills/status.matrix.yaml  +  docs/STATUS-DEFINITION.md (五层口径)   │
└──────────────────────────────────────────────────────────────────────┘
```

**承担统一底座的目录清单**:`knowledge/`、`kernel/contracts/`、`kernel/quality-gates/`、`kernel/traceability/`、`kernel/preflight/`、`.factory/`、`.claude/skills/`、`skills/status.matrix.yaml`、`docs/STATUS-DEFINITION.md`。

---

## 3. 四大统一目标对标矩阵（报告核心）

对标维度:每个目标拆成三层看成熟度——**定义层**(标准/契约是否写了)、**强制层**(runtime 是否真执行)、**审计层**(各 skill 实现是否被验证过)。

| 统一目标 | 定义层 | 强制层(runtime) | 审计层(实现验证) | source-of-truth 风险 | 真实成熟度 |
|---|---|---|---|---|---|
| **统一标准** | ✅ 双份(paradigm manifest 20 方法 + manifest 51 资产;paradigm 目录另有未登记扩展文件) | — (标准不直接 runtime 执行) | ❌ 从未审计 skill 是否真按标准实现 | 🔴 **高:双源未裁定** | ⚠️ 内容富余,真源未定 |
| **统一契约** | ✅ 强(11 接口 + 22 artifact schema + 4 archetype) | ✅ skill_loader 加载时校验 frontmatter/结构 | 🟡 仅数据契约被校验;**能力接入契约缺失** | 🟡 中:generation archetype 为 provisional | 🟡 数据契约强 / 能力契约空 |
| **统一输入输出** | ✅ `artifact-base.schema.json` 统一基座(含 traceability/gaps/warnings/assumptions/validation_status 通用字段) | ✅ prd2proto schema 真 `$ref` 继承 base | ❌ 仅 prd2proto 证实;其余 skill 用 templates/ 未证实继承 | 🔴 **高:prd2proto/schemas(7) 与 kernel/contracts/artifacts(22) 部分重复** | ⚠️ 基座强 / 遵守度仅 1/5 + schema 双源 |
| **统一质量门** | ✅ 5 个 `kernel/quality-gates` gate 已实现 | ✅ **真 blocking**(`on_blocked: stop_execution` + `QualityGateBlocked` 异常 + 阈值 warning/blocked) | ❌ 仅 prd2proto runtime 真 import+调用;uxeval/ai-analytics/ip-design **pipeline 声明的是 gate/pause 语义,无 runtime 执行且未接入 kernel quality-gates** | 🟡 中:status.matrix 称"warning 不阻塞"与代码矛盾 | 🟡 框架真 blocking / 覆盖仅 1/5 |

### 对标揭示的真实结构

> **四大统一目标的瓶颈不在"定义层"——定义层全都有,标准和 schema 甚至各多了一套(是双源问题,不是缺失问题)。瓶颈在"强制层覆盖"和"审计层空白":**
> - **强制层**:质量门是真 blocking,artifact-base 是真继承,但只有 prd2proto 接进去。
> - **审计层**:`applicable_skills` / `skill_integration` / pipeline 里的 gate 声明,全是**声明**,从未有人验证"声明 = 实现"。

### 每个目标的 S1-0B 建议动作(仅建议,不执行)

| 统一目标 | S1-0B 建议动作 |
|---|---|
| 统一标准 | 裁定 `design-work-paradigm` 与 `manifest.yaml` 的关系:确立一个为真源,另一个降级为「引用/索引」或显式标注派生关系 |
| 统一契约 | 不新建 capability schema;先做覆盖审计,确认是否真需要「能力接入契约」,若需要则扩展 `.factory/archetypes` 或 `kernel/contracts` |
| 统一输入输出 | 裁定 schema 双源:确认 `kernel/contracts/artifacts` 为真源,`skills/prd2proto/schemas` 改为 `$ref` 引用或删除重复 |
| 统一质量门 | 先修正 status.matrix 过时表述;再审计 uxeval/ai-analytics/ip-design 的 gate 声明是否真能执行(它们无 runtime) |

---

## 4. Knowledge Layer 盘点

### 4.1 两套并行体系（核心张力）

| | 体系 A:shared-knowledge | 体系 B:work-paradigm |
|---|---|---|
| 文件 | `knowledge/manifest.yaml` | `knowledge/design-work-paradigm/manifest.yaml` |
| 规模 | 51 资产 | `manifest.yaml` 登记 20 方法(00–19);目录另有 20–39 扩展 md 文件但未进 manifest |
| 命名 | `<domain>.<slug>`(`ux.heuristic-principles`) | 数字编号(`01-input-diagnosis`) |
| 映射字段 | `applicable_skills`(资产 → skill) | `skill_integration`(skill → 方法编号) |
| 决策库四件套 | ✅ `quality_bar` / `do_not_claim` / `decision_use` | 方法正文含「资深 vs 初级」「核心命题」 |
| **各 skill 实际引用** | ✅ **5 个 skill 的 knowledge-manifest 全部引用这套** | ❌ **无任何 skill 按编号引用** |
| 自我定位 | `layer: shared-knowledge` | `Senior Designer Work Paradigm Engine v1.0.0` |

**判断**:体系 A 是**活体系**(skill 真引用);体系 B 是**声明但未串联的方法论引擎**,且自身存在登记口径不一致(`manifest.yaml` 登记 00–19,目录存在 20–39 扩展文件,README 仍写 19 个核心方法)。两者内容部分重叠(如 paradigm 的 `14-Brand-Strategy-Modeling` 与 `knowledge/design/strategy` 主题相同)。这是**最高优先级的 source-of-truth 冲突**。

### 4.2 资产内容真源

`knowledge/{design,ux,product,frontend,research}/` 是资产正文的物理位置(如 `knowledge/design/visual/logo-design-methodology.md`)。manifest A 的 `source_of_truth` 字段指向这些文件。这一层是清晰的、无冲突的。

### 4.3 不应被重复定义的内容

- ❌ 不应新建 `docs/SENIOR-DESIGN-METHODOLOGY-KERNEL.md`:方法论内核已在 `design-work-paradigm/`(manifest 登记 00–19,目录扩展到 39) + `knowledge/{domain}/` 正文。
- ❌ 不应新建 `docs/SENIOR-CAPABILITY-STANDARD.md`:资深标准已在 manifest 的 `quality_bar`/`do_not_claim` + `17-quality-rubrics`(9 维)+ `18-failure-modes`。

---

## 5. Factory Layer 盘点

| 组件 | 现状 |
|---|---|
| `.factory/CONTRACT.md` | 定义工厂北极星(Time-to-Skeleton ≤5min、复用率 ≥80%、零回归)+ 5 道验收门 |
| `.factory/archetypes/` | 4 个:`evaluation.yaml`(成熟,从 uxeval 萃取)、`generation.yaml`(**provisional 0.1.0,自带「待 reconcile」注释**)、`analysis.yaml`、`creative-generation.yaml` + `archetype_schema.py` |
| `.factory/tools/extract.py` | 从现有 skill 反向萃取 archetype 定义 |
| `.factory/tools/validate.py` | 按 archetype 校验 skill 目录结构/frontmatter/stage/gate 拓扑 |
| `.factory/tools/scaffold.py` | 按 archetype 装配新 skill 骨架 |

**判断**:
- `.factory` **已经是 skill factory**,不需新建。
- validate.py 校验的是**结构合规**(目录/frontmatter/stage 拓扑),**不校验 paradigm coverage**(skill 是否真接入了声明的方法)。
- **S1-0B 若要做覆盖校验:应扩展 `.factory/tools/validate.py` 或新增 `.factory/tools/validate_paradigm_coverage.py`,不应新建脱离 .factory 的独立 validator。** 倾向后者(新增独立文件),因为覆盖校验与结构校验是不同关注点,且 CLAUDE.md 禁止改 `.factory/archetypes/`,但新增 tools 文件不受限。

---

## 6. Contract Layer 盘点

| 组件 | 内容 |
|---|---|
| `kernel/contracts/interfaces.py` | 11 个冻结接口:`ISkill` / `IPipelineSkill` / `ISkillGroup` / `IPipelineEngine` / `IWorkflowOrchestrator` / `ILLMClient` / `IMCPClient` / `IMemoryAdapter` / `IPreflightChecker` / `IOutputRenderer` / `ISkillLoader` / `ICheckpointManager`(ADR 治理,改动需协调) |
| `kernel/contracts/schemas.py` | 共享数据 schema(SkillConfig/StageConfig/CheckpointConfig/Evidence/Issue/JourneyStage 等) |
| `kernel/contracts/enums.py` | 通用枚举(SkillType/StageType/SeverityLevel/RunStatus 等) |
| `kernel/contracts/artifacts/` | **22 个 artifact schema** + `artifact-base.schema.json`(统一基座) |
| `.factory/archetypes/` | archetype 契约(form-factor 级,与 kernel/contracts 数据契约级分工) |

**分工**:`kernel/contracts` = 数据/接口契约(细粒度,什么字段、什么类型);`.factory/archetypes` = 形态契约(粗粒度,什么类型 skill 该有什么目录/stage/gate)。两者**互补不冲突**。

**判断**:
- ❌ 不应新建 `kernel/contracts/skill-capability.schema.json`(平行 schema)。
- 契约层现状:**数据契约强,能力接入契约缺失**——没有一个契约描述「skill X 声明它实现了哪些 paradigm 能力 + readiness + gap」。是否需要补这个契约,**应在 S1-0B 覆盖审计后再决定**,而非现在臆断。

---

## 7. Kernel Layer 盘点

| 模块 | 承担能力 | 与「资深能力」的关系 |
|---|---|---|
| `kernel/skill_loader` | 加载 SKILL.md/GROUP.md/pipeline,解析 frontmatter | 已可校验 skill 结构合规 |
| `kernel/pipeline` | 多 stage 流水线执行引擎 | 已是统一执行底座 |
| `kernel/quality-gates` | **真 blocking 质量门**(gates.py + gate-config.yaml,5 gate,阈值化) | **统一质量门已存在,无需新建** |
| `kernel/traceability` | 追溯(tracer.py) | **统一追溯已存在,无需新建** |
| `kernel/preflight` | 外部依赖预检 | input diagnosis 的环境检查可由此承接 |
| `kernel/checkpoint` | 暂停/恢复快照 | — |
| `kernel/{llm,memory,output,workspace,errors,config,mcp,trace}` | LLM 适配/三级记忆/渲染/工作区等 | 全部已存在 |

**重点判断**:
- **input diagnosis**:方法论在 `design-work-paradigm/01` + prd2proto prompt;环境预检在 `kernel/preflight`。无需新建模块。
- **senior quality gate**:`kernel/quality-gates` 已是真 blocking 实现。无需新建。
- **senior traceability**:`kernel/traceability` 已存在。无需新建。
- ❌ **确认不需要新建 `kernel/seniorcap/*`**——其所有设想能力(input_diagnosis/traceability/gap_report/quality_gate)在现有 kernel 模块 + paradigm 方法中均已有归属。后续若要强化,应**扩展已有模块**,不新建平行包。

---

## 8. Governance Layer 盘点

| 治理 skill | 当前管什么 | 与 Inventory-before-build 的关系 |
|---|---|---|
| `designos-governor` | 批次前置:scope/branch/status/禁止事项/脏文件/(软性)读 manifest | **第 5 项「是否需读 shared knowledge manifest」是软性的**(仅涉及知识资产才读),**未强制 inventory-before-build** ← 本轮要补 |
| `designos-closeout` | 批次后置:git status/diff/测试/禁止文件/能否进下一批 | 后续 senior 改造的收口可接入 |
| `designos-knowledge-architect` | 共享知识层架构守则:共享vs私有边界、5 domain、决策库四件套、专属词红线 | **未含「新建前先盘点是否已存在」** ← 本轮要补 |
| `designos-skill-factory` | 新建/扩展 skill 时的工厂守则 | — |

**判断**:governor 和 knowledge-architect 都**缺少 inventory-before-build 强制**——这正是本轮(我)差点重复建设的根因。本轮 Part A 补这条规则。

---

## 9. Readiness Layer 盘点

- `skills/status.matrix.yaml`(version 2.0.0):5 个 skill 的五层 readiness + maturity + blockers + not_allowed_claims。
- `docs/STATUS-DEFINITION.md`:五层口径定义(methodology_ready → prompt_ready → runtime_ready → validated → enterprise_ready),禁止跨层推导。
- **缺口**:status.matrix **无 paradigm coverage 字段**——无法表达「该 skill 声明接入了哪些方法 / 实际实现了几个」。

---

## 10. 5 个 Skill 接入情况（声明 vs 实现）

| 维度 | prd2proto | uxeval | ai-analytics | ip-design | brand-creative |
|---|---|---|---|---|---|
| SKILL.md / GROUP.md | ✅ SKILL | ✅ SKILL | ✅ SKILL | ✅ SKILL | ✅ GROUP |
| knowledge-manifest.yaml | ✅ | ✅ | ✅ | ✅ | ✅ |
| pipeline.yaml | ✅ | ✅ | ✅ | ✅ | ❌ |
| prompts / prompts-v2 | ✅ 10 + **18(v2)** | ✅ 9 | ✅ 7 | ✅ 7 | ❌ 0 |
| runtime/ | ✅ **8 文件** | ❌ | ❌ | ❌ | ❌ |
| eval / golden-cases | ✅ + golden-cases | ✅ eval | ✅ eval | ✅ eval | ❌ |
| constitution.md | ✅ | ✅ | ✅ | ✅ | ❌ |
| 引用 shared-knowledge(体系A) | ✅ | ✅ | ✅ | ✅ | ✅ |
| 引用 paradigm 编号(体系B) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 接入 kernel artifacts | ✅ `$ref` base | ❌ 未证实 | ❌ 未证实 | ❌ 未证实 | ❌ |
| pipeline 声明门控 | ✅ `quality_gates:` 多处,且 runtime 执行 | ✅ `gate:` 4 处,无 runtime 执行 | ✅ `gate:` 1 处,无 runtime 执行 | ✅ `gate:` 2 处,无 runtime 执行 | ❌ |
| **runtime 真执行 gate** | ✅ import+调用 | ❌ **无 runtime** | ❌ **无 runtime** | ❌ **无 runtime** | ❌ |
| 接入 traceability | ✅ runtime import | ❌ | ❌ | ❌ | ❌ |
| status.matrix maturity | pilot | beta | pilot | pilot | alpha |
| **接入状态** | **实现已接入** | **声明已接入** | **声明已接入** | **声明已接入** | **框架未成型** |

### 关键结论

1. **prd2proto 是唯一接近全链路接入统一底座的 skill**:schema `$ref` artifact-base、pipeline 声明 gate、runtime 真 import 并调用 `kernel/quality-gates` + `kernel/traceability`。是 seniorization pilot 的合理选择。
2. **uxeval / ai-analytics / ip-design 主要停留在 shared-knowledge 声明层**:有 prompts + pipeline + 在 pipeline 里声明了 `gate:` 暂停门,但**没有 runtime 目录去执行这些门控语义**,也未接入 `kernel/quality-gates`——「声明了门控,无执行体」。这是「声明 vs 实现」缺口的最典型证据。
3. **brand-creative 仍是 group/sub-skills 框架**:无 pipeline / prompts / runtime / constitution 主线,与 status.matrix 标的 alpha 一致。
4. **5 个 skill 全部引用体系 A、全部不引用体系 B 编号**——再次印证 paradigm 编号体系是「声明但未串联」。

---

## 11. Source-of-truth 冲突清单（只记录，不修复）

| # | 冲突 | 证据 | 严重度 | 核验状态 |
|---|---|---|---|---|
| C1 | **标准双源**:`manifest.yaml`(命名空间)vs `design-work-paradigm/manifest.yaml`(编号) | skill 全引用前者,后者 skill_integration 编号无人引用 | 🔴 高 | 本地已证实 |
| C2 | **方法 id 双源**:shared-knowledge asset id(`ux.*`)vs paradigm method id(`01-19`) | 两套 id 描述部分重叠的方法论 | 🔴 高 | 本地已证实 |
| C3 | **Schema 双源**:`skills/prd2proto/schemas/`(7)vs `kernel/contracts/artifacts/`(22) | business-flow/product-archetype/page-flow 等两边都有定义 | 🟡 中 | 本地已证实 |
| C4 | **质量门口径过时**:status.matrix 称 prd2proto「质量门 warning 模式不阻塞」vs `kernel/quality-gates` 实为 blocking | gate-config `on_blocked: stop_execution` + `QualityGateBlocked` 异常 | 🟡 中 | 本地已证实 |
| C5 | **generation archetype 未定稿**:`.factory/archetypes/generation.yaml` = `0.1.0-provisional`,自带「待 reconcile」注释 | 文件头注释 | 🟡 中 | 本地已证实 |
| C6 | **版本口径不一致**:`pyproject.toml` = 0.6.2、`docs/architecture.md` = 0.6.2,但实际已发 npm 0.7.1 | 本地文件停在 0.6.2 | 🟡 中 | 本地已证实;npm 0.7.1 **待外部核验** |
| C7 | **README/AGENTS/status 口径** | 需逐文件比对(本轮未深比) | ⚪ 低 | 部分待核验 |
| C8 | **公网 repo 显示旧版本口径** | 公网 GitHub 仓库状态 | ⚪ 低 | **待外部核验**(本地无法查) |
| C9 | **install/pyproject/package/npm 发布口径** | package.json 本地不存在(已知:发布配置在 clean-seed 快照) | ⚪ 低 | **待外部核验** |

> **核验边界声明**:C6/C8/C9 涉及 npm registry 与公网仓库,属外部系统,开发仓库本地无法核验,仅作记录。本轮**只记录冲突,不修复**。

---

## 12. 缺口三维矩阵（已存在 / 存在未串联 / 声明未验证）

把能力分到三个互斥状态,这是 S1-0B 的输入:

### 12.1 已存在，不应重复建设（❌ 禁止新建）

| 能力 | 真源位置 | 原计划误打算新建的 |
|---|---|---|
| 资深方法论内核 | `knowledge/design-work-paradigm/`(manifest 登记 00–19,目录扩展到 39)+ `knowledge/{domain}/` 正文 | ~~docs/SENIOR-DESIGN-METHODOLOGY-KERNEL.md~~ |
| 资深能力标准 | `manifest.yaml` quality_bar/do_not_claim + `17-quality-rubrics` + `18-failure-modes` | ~~docs/SENIOR-CAPABILITY-STANDARD.md~~ |
| 统一数据契约 | `kernel/contracts/`(11 接口 + 22 artifact schema) | ~~kernel/contracts/skill-capability.schema.json~~ |
| 统一输入输出基座 | `kernel/contracts/artifacts/artifact-base.schema.json` | —— |
| 统一质量门 | `kernel/quality-gates`(真 blocking) | ~~kernel/seniorcap/quality_gate.py~~ |
| 统一追溯 | `kernel/traceability` | ~~kernel/seniorcap/traceability.py~~ |
| skill 工厂 + 结构校验 | `.factory/`(archetype + extract/validate/scaffold) | ~~脱离 .factory 的独立 validator~~ |
| readiness 口径 | `status.matrix.yaml` + `STATUS-DEFINITION.md` | —— |

### 12.2 已存在但未串联（🔗 需打通，不需新建）

| 能力 | 现状 | 未串联点 |
|---|---|---|
| paradigm skill_integration 映射 | manifest 已声明 prd2proto→[01,02,…] 等 | skill 实际引用的是体系 A 的 id,与编号映射**未对齐** |
| factory validator | 校验结构合规 | **不校验 paradigm coverage**(声明的方法是否真实现) |
| status.matrix readiness | 有五层 readiness | **无 paradigm coverage 字段** |
| governor 前置检查 | 有 scope/branch/禁止事项检查 | **无 inventory-before-build 强制**(本轮 Part A 补) |
| 质量门(真 blocking) | kernel 已实现 | 仅 prd2proto runtime 接入,其他 3 个 skill 声明 gate 但无 runtime 执行 |

### 12.3 已声明但未验证实现（🔍 需审计，S1-0B 核心）

| 声明 | 声明位置 | 未验证点 |
|---|---|---|
| 各 skill 接入哪些共享知识 | `knowledge-manifest.yaml` 的 applicable assets | 是否真在 prompt/runtime 里用了这些知识——**从未审计** |
| paradigm 方法覆盖 | manifest `skill_integration` | skill 是否真实现对应方法——**从未审计** |
| 门控覆盖 | prd2proto 的 `quality_gates:` + 其他 skill pipeline.yaml 的 `gate:` | prd2proto 已有 runtime 执行;uxeval/ai-analytics/ip-design 无 runtime,声明的 `gate:` **未证实可执行**,且不是 kernel quality-gates |
| artifact-base 遵守 | —— | 除 prd2proto 外,其余 skill 是否继承 base——**未证实** |

---

## 13. P0 / P1 / P2 Blockers

**P0(阻塞统一底座可信度,必须先解)**
- P0-1:**标准双源未裁定**(C1/C2)——不裁定真源,后续所有 skill 资深化都会面临「按哪套标准」的歧义。
- P0-2:**声明 vs 实现从未审计**——manifest/pipeline 的所有接入声明都未经验证,status.matrix 的 readiness 可能虚高或虚低。

**P1(影响一致性与可执行性)**
- P1-1:Schema 双源(C3)——prd2proto/schemas 与 kernel artifacts 重复,改一处易漏另一处。
- P1-2:质量门口径过时(C4)——status.matrix 表述与代码矛盾,误导读者。
- P1-3:generation archetype provisional(C5)——prd2proto 的形态契约未定稿。
- P1-4:3 个 skill 声明 `gate:` 但无 runtime 执行——门控覆盖名不副实,且不能等同于已接入 `kernel/quality-gates`。

**P2(发布口径/外部一致性,待外部核验)**
- P2-1:版本口径不一致(C6,本地 0.6.2 vs 已发 0.7.1)。
- P2-2:公网 repo / npm 发布口径(C8/C9,待外部核验)。
- P2-3:README/AGENTS/status 口径细比(C7)。

---

## 14. 确认不应新建的原计划文件

以下原 S1-0 计划文件,经盘点**确认不应新建**(理由见 §12.1):

- ❌ `docs/SENIOR-CAPABILITY-STANDARD.md`
- ❌ `docs/SENIOR-DESIGN-METHODOLOGY-KERNEL.md`
- ❌ `kernel/contracts/skill-capability.schema.json`
- ❌ `kernel/seniorcap/*`(整个包)
- ❌ 5 份 `skills/*/capability.yaml`(**改为 S1-0B 评估后再定形态**,很可能是 `paradigm-coverage.yaml` 且优先扩展现有体系)
- ❌ 脱离 `.factory` 的独立 validator

---

## 15. S1-0B 最小可执行建议（仅建议，不执行）

按优先级排序,**每步都是「扩展现有体系」而非「新建平行体系」**:

| 优先级 | S1-0B 动作 | 性质 | 对应 blocker |
|---|---|---|---|
| **S1-0B-1** | **裁定标准双源**:确立 `manifest.yaml`(体系A)为 skill 接入真源;`design-work-paradigm` 显式标注为「方法论正文库」并建立 A↔B 的 id 映射索引(或将 B 降级为 A 的正文来源) | 文档/manifest 校准 | P0-1 |
| **S1-0B-2** | **declared-vs-implemented coverage audit**:对 5 skill 逐个核验「knowledge-manifest 声明的资产 / pipeline 声明的 gate」是否在 prompt/runtime 真实现,产出覆盖审计报告 | 只读审计 | P0-2 |
| **S1-0B-3** | **裁定 schema 双源**:确认 `kernel/contracts/artifacts` 为真源,`skills/prd2proto/schemas` 收敛为 `$ref` 引用或移除重复 | 契约校准 | P1-1 |
| **S1-0B-4** | **修正 status.matrix 过时口径**(质量门 blocking)+ 增加 `paradigm_coverage` 字段表达覆盖度 | 状态校准 | P1-2/P1-4 |
| **S1-0B-5** | **覆盖校验器**:基于 S1-0B-2 结果,新增 `.factory/tools/validate_paradigm_coverage.py`(独立于 validate.py,不改 archetypes) | 工具扩展 | P0-2 持续化 |
| **S1-0B-6** | reconcile `generation.yaml` provisional(需碰 `.factory/archetypes/`,受 CLAUDE.md 约束,**须单独申请范围**) | archetype 定稿 | P1-3 |
| **S1-0B-7** | 发布口径校准(版本/README/AGENTS),涉及外部系统,**单独阶段处理** | 发布治理 | P2 |

**推荐 S1-0B 起步**:**先做 S1-0B-1(裁定标准双源)+ S1-0B-2(覆盖审计)**——这两步是 P0,且是只读/校准性质,不碰业务逻辑,做完才知道 capability 契约到底要不要、长什么样。**不建议**一上来就建 capability.yaml/validator(那是 S1-0B-2 之后才有依据的决定)。

---

## 16. 本轮治理固化（Part A 摘要）

为防止「只查目标文件不存在就开建」再次发生(本轮即差点重复建设),已将 **Inventory-before-build rule** 固化进:
- `CLAUDE.md`(新增治理条款)
- `.claude/skills/designos-governor/SKILL.md`(新增前置检查项)
- `.claude/skills/designos-knowledge-architect/SKILL.md`(新增盘点前置)

规则详见各文件。核心:**任何新建标准/契约/方法论/validator 前,必须先读 10 处现有 source-of-truth 并回答 6 个问题,禁止仅凭「目标文件不存在」推断「能力不存在」。**

---

*报告结束。本轮只盘点 + 固化治理,不进入 S1-0B,不进入 S1-1。*
