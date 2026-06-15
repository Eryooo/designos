# DesignOS 共享知识资产层（Shared Knowledge Layer）

这一层是 DesignOS 所有 skill 共享的**通用知识 source-of-truth**。它存在的理由很简单:在它出现之前,uxeval / prd2proto / ai-analytics 各自维护一套孤立的方法论、原则、标准、模板。同一个"严重等级口径""design token 命名标准""SWOT 怎么用",会在多个 skill 里被重复定义、各自漂移。共享层把这些**跨 skill 复用的通用知识**收敛到一处。

## 它放什么 / 不放什么

放(通用、跨 skill 复用):
- 方法论(methodology):story mapping、SWOT/KANO/JTBD、用户画像构建法……
- 原则(principles):启发式评估原则、组件结构原则、视觉策略准则……
- 标准(standard):严重等级口径、证据充分性标准、design token 命名标准……
- 目录(catalog):可复用模板族的选择维度目录……

不放(skill 私有、不可复用):
- 各 skill 的 `reference/m0x-*.md`:它们描述"该 skill 如何在自己 pipeline 的某个 stage 应用这些通用知识",绑定了具体 stage 编号、输出 schema、checkpoint。这类内容**留在各自 skill 内**。
- 任一 skill 的 constitution、pipeline、prompt 行为。
- 项目/产品专属数据(具体色值、具体页面树、具体竞品、具体 PRD)。

## 边界判定口诀

一条知识该进共享层,当且仅当:**把它正文里所有 skill 名 / 产品名删掉后,它依然完整成立、且对另一个 skill 仍然有用。** 否则它是 skill 私有 reference,不进来。

共享层资产正文严禁出现 skill 专属词(uxeval / prd2proto / ai-analytics 等)——这一点由结构测试强制校验。"这个资产被哪些 skill 用"只记录在 `manifest.yaml` 的 `applicable_skills` 字段里,不写进通用正文。

## 为什么不是一个大目录

知识按**领域(domain)** 切分成五个子目录,而不是全塞进一个 `knowledge/` 平铺目录:

- design / ux / product / frontend / research 各自有独立的专家心智模型与质量标准,混在一起会让"谁该维护、谁该引用"变得不可追踪。
- 后续 skill 通常只消费其中一两个 domain(如 ai-analytics 主要吃 research),按 domain 切分让 `applicable_skills` 与依赖关系清晰可审计。
- 每个资产都有 stable id(`<domain>.<slug>`)与 `source_of_truth` 路径,id 不随文件移动而变,引用方按 id 锚定。

## 目录结构

```
knowledge/
├── manifest.yaml          # 资产清单：id/version/domain/type/applicable_skills/...
├── README.md              # 本文件
├── design/                # 品牌/视觉策略、设计模板目录、设计质量标准
├── ux/                    # 评估原则、严重等级、证据标准
├── product/               # 故事地图、信息架构
├── frontend/              # design token、组件结构、代码质量规则
└── research/              # 竞品分析、方法论库、用户画像
```

## 两套知识体系的关系(source-of-truth 裁定)

DesignOS 有两个 `manifest.yaml`,职责必须分清(详见 `docs/audits/S1-0B-STANDARD-SOURCE-OF-TRUTH-DECISION.md`):

| | `knowledge/manifest.yaml` | `knowledge/design-work-paradigm/manifest.yaml` |
|---|---|---|
| 角色 | ✅ **active source-of-truth** | 📚 methodology reference library |
| 命名 | stable id(`<domain>.<slug>`) | 编号方法(00–39) |
| 谁引用 | **各 skill 的 `knowledge-manifest.yaml` 实际按 id 引用这一套** | 无 skill 按编号接入 |
| 用途 | skill 接入、依赖追溯、`applicable_skills` | 资深设计师工作范式的方法论正文参考 |

**裁定**:
- 各 skill 接入共享知识,**只认 `knowledge/manifest.yaml` 的 stable id**。
- `design-work-paradigm/` 是**方法论参考库**(Senior Designer Work Paradigm Engine),供人阅读/方法论沉淀,**不是 skill 接入真源**。它的 manifest 由 `scripts/validate-paradigm-manifest.py` 校验目录一致性,但不充当 skill 依赖锚点。
- **禁止**让 skill 直接按 `design-work-paradigm` 的编号(如 "method 17")接入——会制造与 stable id 并行的第二套依赖真源。

## 资产类型(type)的真源

资产的**类型**由 `manifest.yaml` 每条资产的 `type` 字段决定,**不是由它所在的物理目录决定**。

- 物理目录按 **domain** 切分(design / ux / product / frontend / research)——回答"属于哪个专家领域"。
- `type` 字段按**资产种类**标注——回答"这是什么:methodology / rubric / standard / failure_modes / checklist / report / principles / catalog"。
- 同一个 domain 目录下会混放多种 type(如 `design/quality/` 下同时有 rubric、failure_modes、checklist)——**这是设计如此,不是混乱**。要按类型检索资产,查 `manifest.yaml` 的 `type` 字段(或 `INDEX-BY-TYPE.md` 索引),不要靠目录名猜。

## 四层内容边界(放置规则)

DesignOS 的"知识/方法论/模板/案例"分四层,各有归属,**不可互相搬运正文**:

| 层 | 位置 | 放什么 | 谁是真源 |
|---|---|---|---|
| **shared knowledge** | `knowledge/<domain>/` | 跨 skill 复用的通用方法论/原则/标准/rubric/failure_modes | `knowledge/manifest.yaml`(按 id) |
| **skill reference** | `skills/<skill>/reference/m0x-*.md` | "本 skill 如何在某 stage 应用某共享知识"——绑定 stage/schema/checkpoint | skill 私有;按 id 锚定回 shared |
| **skill template** | `skills/<skill>/templates/*.md` | 本 skill 的输出模板/golden output 结构 | skill 私有 |
| **eval case** | `skills/<skill>/eval/golden/` 与 `eval/failure/` | 具体的 synthetic golden case 与 failure case | skill 私有;不放真实业务数据 |

判定:**通用且去掉 skill 名仍成立 → shared;绑定本 skill stage/输出 → reference/template;是具体跑通/跑挂的样例 → eval case。**

## 状态

本层处于 `pilot`。K0 批次只建**架构基线**:声明结构、边界、stable id,资产正文为 `draft` 占位。内容固化与从旧 skill 的有序迁移,留待后续批次(K1+)。
