# S1-0B Decision — 标准 Source-of-Truth 裁定

> **本报告性质**:对 `knowledge/manifest.yaml` 与 `knowledge/design-work-paradigm/` 两套并行体系做最终裁定,确立各自角色,记录不一致问题。**只裁定不重构**——不修复目录/manifest 不一致,不新建第三套标准。
> **依据**:S1-0A 报告(`docs/audits/S1-0A-EXISTING-FOUNDATION-INVENTORY.md`)+ 本批次再核实证据。
> **日期**:2026-06-12

---

## 1. 决策摘要

| 体系 | 角色裁定 | 状态 |
|---|---|---|
| `knowledge/manifest.yaml` | **Active Skill-Integration Source-of-Truth**(skill 引用真源) | ✅ 保留为活体系 |
| `knowledge/design-work-paradigm/*.md`(40 个方法文件) | **Methodology Reference Library**(方法论正文参考库) | ✅ 保留,作为方法论正文 |
| `knowledge/design-work-paradigm/manifest.yaml`(20 method 索引) | **Stale Index**(过期/不完整索引,不再作为真源) | ⚠️ **降级**,后续(S1-0C)决定:重建为完整索引 / 移除 / 标注 deprecated |

**一句话决策**:
> **`knowledge/manifest.yaml` 是 skill 接入的唯一真源;`knowledge/design-work-paradigm/` 目录是方法论正文的物理存放地,正文继续保留;但其 `manifest.yaml` 不再作为真源使用——它登记 20 / 实际 40,且 15 处大小写不一致,自身已不可信。**

**不做的事**:
- ❌ 不新建 `docs/SENIOR-DESIGN-METHODOLOGY-KERNEL.md`(等于第三套真源)
- ❌ 不新建 `docs/SENIOR-CAPABILITY-STANDARD.md`(等于第三套真源)
- ❌ 本批不修复 paradigm manifest 的不一致(只裁定 + 记录,修复留 S1-0C)
- ❌ 不删除 `design-work-paradigm/` 任何方法文件(它们是方法论正文)

---

## 2. 两套标准体系证据

### 2.1 体系 A:`knowledge/manifest.yaml`(Active)

| 维度 | 实证 |
|---|---|
| 自我定位 | `layer: shared-knowledge`(显式 shared-knowledge layer) |
| 资产规模 | **51 个 assets**(命名空间 `<domain>.<slug>`) |
| 5 个 domain | design / ux / product / frontend / research |
| 决策库四件套字段 | ✅ `quality_bar` / ✅ `do_not_claim` / ✅ `decision_use` / ✅ `applicable_skills`(资产→skill 映射) |
| **是否被 skill 引用** | ✅ **5 个 skill 的 `knowledge-manifest.yaml` 全部引用此体系的 id** |
| 治理 skill 引用 | ✅ `.claude/skills/designos-knowledge-architect/SKILL.md` §1 明确指向此 manifest 为知识层架构 |

### 2.2 体系 B:`knowledge/design-work-paradigm/`(Reference Library)

| 维度 | 实证 |
|---|---|
| 自我定位 | `Senior Designer Work Paradigm Engine v1.0.0` |
| 文件规模 | **40 个方法 .md 文件**(00–39 编号,不含 README) |
| `manifest.yaml` 登记 | **仅 20 个 method**(00–19) |
| 缺口 1:**未登记** | **20 个文件未在 manifest 登记**(编号 20–39):覆盖 uxeval 的 Heuristic-Evaluation/Severity-Rating/Issue-Attribution、ai-analytics 的 Research-Methodology/Evidence-Extraction/Strategy-Synthesis、ip-design 的 Worldview/Persona/Visual-Lock、brand-creative 的 Logo/Color/Typography/VI/Brand-Voice/Content/Campaign/Collateral/Digital-Assets/Brand-Guidelines |
| 缺口 2:**大小写不一致** | **15 处**:manifest 写 `02-objective-decomposition.md`(全小写),磁盘是 `02-Objective-Decomposition.md`(Title-Case)——macOS HFS+ 不区分大小写**能跑**,Linux/Windows **会破**(这是潜在的跨平台 bug) |
| `skill_integration` 字段 | manifest 内有声明(prd2proto: methods=[01..19] 等),但**所引用编号无任何 skill 在 knowledge-manifest 中按编号引用** |
| **是否被 skill 引用** | ❌ **0 个 skill 的 knowledge-manifest 按方法编号引用此体系**(全部引用体系 A 的命名空间 id) |

### 2.3 关键不一致数据(本批次实证脚本输出)

```
shared_assets               : 51    (体系 A)
paradigm_manifest_methods   : 20    (体系 B 索引)
paradigm_method_md_excluding_readme : 40    (体系 B 实际)
真正未登记(大小写不敏感)    : 20    (50% 文件未索引)
大小写不一致登记            : 15    (75% 已登记项写法错)
```

---

## 3. 为什么选体系 A 作为 Active Source-of-Truth

### 3.1 **使用证据**(决定性):
- 5 个 skill 的 `knowledge-manifest.yaml` **全部按体系 A 的 `<domain>.<slug>` id 引用**(如 `ux.heuristic-principles`、`design.ip.methodology`、`research.competitor-analysis`)。
- 0 个 skill 按体系 B 的方法编号(`01`/`02`/...)引用。
- 治理 skill `designos-knowledge-architect` 的架构守则已基于体系 A。

### 3.2 **架构完整性**:
- 体系 A 有完整的资产元数据契约:`id` / `version` / `domain` / `type` / `applicable_skills` / `source_of_truth`(指向正文)/ `decision_use` / `quality_bar` / `do_not_claim` / `owner` / `status`。
- 体系 A 的 `source_of_truth` 字段即指向正文文件,与「方法论正文物理位置」解耦——这就是「manifest = 索引,正文 = 内容」的标准做法。

### 3.3 **体系 B 自身已失效**:
- B 的 manifest 索引覆盖率仅 50%(20/40)。
- B 的索引含 75% 大小写错误(15/20)。
- 一个**自身索引和目录都对不上**的 manifest,无资格作为 source-of-truth。
- B 的 `skill_integration` 编号声明从未被任何 skill 实际引用——是孤悬声明。

### 3.4 **避免双源治理负担**:
- 维持两套真源 = 任何更新都要双更新,极易漂移(本次 paradigm manifest 已经漂移)。
- 单一真源 + 物理正文库,是更经得起时间检验的架构。

---

## 4. 体系 B(`design-work-paradigm/`)的角色定位

裁定后,体系 B 的角色:

**正文层(40 个 .md 文件):**
- ✅ 保留为**方法论正文物理存放地**(Methodology Reference Library)。
- ✅ 体系 A(manifest.yaml)的资产可用 `source_of_truth` 字段指向这些 .md(部分已经如此)。
- ✅ 既有 .md 是优质方法论资产(从 S1-0A 抽样看,如 `14-Brand-Strategy-Modeling.md` 含「资深 vs 初级」「核心命题」等,质量高)。
- 不允许删除——这些是真实可用的方法论正文。

**索引层(`design-work-paradigm/manifest.yaml`):**
- ⚠️ **降级为 Stale Index**,不再作为真源使用。
- ⚠️ `skill_integration` 的方法编号映射在所有 skill 实际未引用,**视为孤悬声明**——后续(S1-0C 或更晚)决定:删除 / 重建 / 改写为体系 A 的索引视图。
- 本批不动它。

**`Senior Designer Work Paradigm Engine v1.0.0` 这个标识:**
- 不再视为「统一标准的真源标识」;视为方法论正文库的一个版本号。
- 任何对外文档不应再宣称「DesignOS 由 Senior Designer Work Paradigm Engine v1.0.0 驱动」(那是孤悬声明)——应说「DesignOS 的 skill 接入 `knowledge/manifest.yaml` 共享知识层,方法论正文存放于 `knowledge/design-work-paradigm/` 与各 domain 子目录」。

---

## 5. 目录文件与 manifest 登记不一致问题(只记录,不修复)

### 5.1 问题 1:20 个文件未登记

未登记文件清单(编号 20–39,共 20 个):

| 编号 | 文件 | 涉及 skill |
|---|---|---|
| 20 | 20-Heuristic-Evaluation.md | uxeval |
| 21 | 21-Severity-Rating.md | uxeval |
| 22 | 22-Issue-Attribution.md | uxeval |
| 23 | 23-Research-Methodology.md | ai-analytics |
| 24 | 24-Evidence-Extraction.md | ai-analytics |
| 25 | 25-Strategy-Synthesis.md | ai-analytics |
| 26 | 26-Worldview-Building.md | ip-design |
| 27 | 27-Persona-Modeling.md | ip-design |
| 28 | 28-Visual-Lock-Definition.md | ip-design |
| 29 | 29-Brand-Audit.md | brand-creative |
| 30 | 30-Logo-Design.md | brand-creative |
| 31 | 31-Color-System.md | brand-creative |
| 32 | 32-Typography-System.md | brand-creative |
| 33 | 33-Visual-Identity-Integration.md | brand-creative |
| 34 | 34-Brand-Voice.md | brand-creative |
| 35 | 35-Content-Strategy.md | brand-creative |
| 36 | 36-Campaign-Creative.md | brand-creative |
| 37 | 37-Brand-Collateral.md | brand-creative |
| 38 | 38-Digital-Assets.md | brand-creative |
| 39 | 39-Brand-Guidelines.md | brand-creative |

> 因为体系 B 已被裁定为 Reference Library 而非 Active source,本批**不修复**这 20 项的登记。

### 5.2 问题 2:15 处大小写不一致

manifest 写小写(`02-objective-decomposition.md`)vs 磁盘 Title-Case(`02-Objective-Decomposition.md`),涉及 02–16 共 15 个文件。

> 跨平台风险:macOS 不区分大小写**能用**,Linux/Windows 区分**会破**。S1-0C 必须修(否则未来在 Linux CI 上会失效)。本批不修。

---

## 6. 不新增第三套标准的理由

提议过的「新建 `docs/SENIOR-CAPABILITY-STANDARD.md` / `SENIOR-DESIGN-METHODOLOGY-KERNEL.md`」**确认不做**,理由:

1. **资深方法论正文已存在**(40 文件,体系 B)+ 体系 A 的 `quality_bar`/`do_not_claim` 已是资深决策库标准 → 新建即第三套真源。
2. **质量 rubric 已存在**:`knowledge/design-work-paradigm/17-Quality-Rubrics.md` + `knowledge/design/quality/*` → 新建 SENIOR-CAPABILITY-STANDARD = 第四套。
3. **失败模式已存在**:`18-Failure-Modes.md` + `knowledge/design/quality/common-failure-modes.md` → 已覆盖。
4. **追溯标准已存在**:`19-Traceability.md` + `kernel/contracts/artifacts/artifact-base.schema.json` 的 `traceability` 字段 → 已覆盖。
5. **CLAUDE.md §3.5 Inventory-before-build 已硬约束**:新建标准/方法论文档前必须先盘点这 10 处真源——这本身就堵住了「再造一套」的风险。

唯一的合规出口:发现现有体系**确实缺某部分能力**(在 S1-0C 覆盖审计后),通过「扩展现有体系 A」的方式补,而非新建文件。

---

## 7. 后续最小改造建议(给 S1-0C / 未来批次)

按优先级排序:

| 优先级 | 改造项 | 性质 | 触碰范围 |
|---|---|---|---|
| **P0** | 修 paradigm manifest 大小写(15 处) | 一行改名级 | `knowledge/design-work-paradigm/manifest.yaml` |
| **P1** | 决定 paradigm manifest 命运:重建为完整 40 索引 / 删除 / 标注 deprecated | 治理决策 | `knowledge/design-work-paradigm/manifest.yaml` |
| **P1** | 把已登记 20 个 paradigm 方法的元数据(`skill_integration`、`output_schema`)迁移到体系 A,统一在 manifest.yaml 表达 | 单源化 | `knowledge/manifest.yaml` |
| **P2** | 体系 A 的 `source_of_truth` 字段补全到所有引用 paradigm md 的资产 | 元数据补强 | `knowledge/manifest.yaml` |
| **P2** | 在 `knowledge/manifest.yaml` 顶部写明「本 manifest 为 active source-of-truth,paradigm/manifest.yaml 已 deprecated」 | 文档校准 | `knowledge/manifest.yaml` 头注释 |

⚠️ 上述全部**留作建议,本批不执行**。S1-0B 只裁定不重构。

---

## 8. 决策状态

| 项 | 状态 |
|---|---|
| Active source-of-truth | `knowledge/manifest.yaml` |
| Reference library | `knowledge/design-work-paradigm/*.md`(40 文件) |
| Stale index | `knowledge/design-work-paradigm/manifest.yaml`(20 登记 / 15 大小写错 / 20 未登记) |
| 是否新建第三套 | ❌ 否 |
| 本批是否修复不一致 | ❌ 否(只记录,留 S1-0C 决定) |
| 是否影响现有 skill | ❌ 否(各 skill 已经引用体系 A,本裁定确认现状,不要求 skill 改动) |

---

*本决策报告结束。配套 `docs/audits/S1-0B-DECLARED-VS-IMPLEMENTED-COVERAGE.md` 是体系 A 的 declared-vs-implemented 审计。*
