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

## 状态

本层处于 `pilot`。K0 批次只建**架构基线**:声明结构、边界、stable id,资产正文为 `draft` 占位。内容固化与从旧 skill 的有序迁移,留待后续批次(K1+)。
