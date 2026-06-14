---
name: designos-knowledge-architect
description: DesignOS 共享知识资产层的架构守则。在新增、修改、迁移 knowledge/ 下任何知识资产，或设计决策库内容时调用。定义共享层架构、共享 vs 私有边界、五个 domain 职责、决策库四件套标准，以及通用知识库的专属词红线。
---

# designos-knowledge-architect — 共享知识层架构守则

涉及 `knowledge/` 下任何资产的增改迁，或设计"决策库"内容时调用本 skill。它保证共享知识层不退化成"又一个孤立流程库"。

## 0. Inventory-before-build（新建知识资产前必盘点，硬约束）

> 因 S1-0A 而立。统一底座已存在两套知识体系(`knowledge/manifest.yaml` shared-knowledge + `knowledge/design-work-paradigm/` 41 方法),新建前不盘点极易造第三套平行真源。详见 CLAUDE.md §3.5 与 `docs/audits/S1-0A-EXISTING-FOUNDATION-INVENTORY.md`。

**新增任何方法论 / 标准 / 决策库内容前,必须先确认它是否已存在于:**
- `knowledge/manifest.yaml`(shared-knowledge 体系,51 资产,`<domain>.<slug>` 命名,各 skill 实际引用)
- `knowledge/design-work-paradigm/`(方法论引擎,41 方法,编号体系)
- `knowledge/{design,ux,product,frontend,research}/`(资产正文真源)

必须回答:目标方法是否已有正文?在哪个体系?是否只是名字不同?应扩展现有资产还是新建?新增是否制造第二套真源?

**硬禁止**:只因「manifest 里没登记某 id」就断定「该方法论不存在」——它可能已在 `design-work-paradigm/` 或某 domain 正文里,只是未登记/换了名。

## 1. 共享知识层架构

```
knowledge/
├── manifest.yaml   # 资产契约：id/version/domain/type/applicable_skills/
│                   #   source_of_truth/decision_use/quality_bar/do_not_claim/owner/status
├── README.md
├── design/  ux/  product/  frontend/  research/
```

- 每个资产有 stable id `<domain>.<slug>`，引用方按 id 锚定，文件移动不改 id。
- 改动资产先读 `manifest.yaml`，对齐该资产的 domain / status / do_not_claim。
- 新增资产必须同步在 manifest 登记全部必填字段，并被结构测试覆盖。

## 2. 共享知识 vs skill 私有 reference 的边界

判定口诀:**把正文里所有 skill 名 / 产品名删掉后，它仍完整成立、且对另一个 skill 仍有用 → 进共享层；否则留在 skill 私有 reference。**

- 共享层放:通用方法论、原则、标准、可复用目录。
- skill 私有保留:各 skill `reference/m0x-*.md`，绑定具体 stage 编号 / 输出 schema / checkpoint，描述"该 skill 如何在自己 pipeline 里应用通用知识"。
- "谁在用"只记录在 manifest 的 `applicable_skills`，**不写进通用正文**。

## 3. 五个 domain 的职责

- **design**:品牌策略、视觉策略、IP 设计、设计模板目录、设计质量标准。
- **ux**:体验评估原则、旅程模型、证据标准、严重等级、问题归因。
- **product**:PRD 理解、用户故事、信息架构、需求拆解、交互模式。
- **frontend**:design token、组件结构、状态覆盖、代码质量规则。
- **research**:竞品分析、用户画像、SWOT、PEST、KANO、JTBD、AIPL 等方法论。

资产放错 domain → 视为架构错误，需归位。

## 4. 决策库四件套（资深决策库标准）

每个知识资产应朝以下四件套演进，这是"流程型 → 资深决策型"升级的核心:

- **rubric（评分标尺）**:用可观察信号判断产出好坏的分级标尺，不是"做没做"。
- **failure modes（失败模式）**:这个领域常见的翻车点 / 反模式，以及如何识别。
- **senior checklist（资深检查清单）**:资深设计师评审时实际会逐项过的清单。
- **do_not_claim（能力边界）**:本资产**不**保证什么、不替代什么，防止越界冒充。

只有步骤清单、没有 rubric / failure modes 的资产，仍属流程型，未达决策型标准。

## 5. 红线:禁止专属词进入通用知识库

- 通用资产正文严禁出现 `uxeval` / `prd2proto` / `ai-analytics` / `design-acceptance` 等专属词。
- 禁止把旧 skill 的知识库**原样搬迁**成共享库——迁移时必须去专属化、去 stage 绑定，提炼成通用决策内容。
- 该红线由 `tests/unit/test_shared_knowledge_layer.py` 强制；改动后必跑，并做负向验证。
