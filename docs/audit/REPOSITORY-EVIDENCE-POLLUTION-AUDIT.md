# Repository Evidence Pollution Audit Report

**版本**: S0-v1.0  
**日期**: 2026-06-12  
**审计范围**: feature/senior-designer-paradigm-engine 全分支 + 已推送远程历史  
**当前分支远端 HEAD**: 7d5fa73（已推送，公开可见）

> ⚠️ **本报告本身已脱敏** — 避免审计文档成为新污染源。
> 具体敏感词以类别代号引用：[PROD-1]=主产品代号、[PROD-2]=子项目代号、
> [COMP]=公司名、[IP-CHAR]=IP 角色、[IP-COLOR]=项目色名、
> [PROJ-DOMAIN]=项目专属域名术语、[CASE-DIR-X]=项目 case 目录代号。

---

## 0. 执行摘要

### 真实状况

- **57 个被 git track 的文件** 含真实业务证据（不是简单脱敏问题，是**证据被错误嵌入通用资产**）
- **已推送到公开仓库**（远程 origin），任何人能看
- **`npm-package/designos@0.6.2`** 可能已发布到 npm 公网注册表（**最严重**）
- **责任边界**：57 个文件里，**8 个是本会话期间引入的污染**（我的责任）；**49 个是项目历史遗留**

### 7 类污染分布

| 污染类型 | 文件数 | 风险级别 |
|---------|------|------|
| Path Pollution（路径含项目代号）| 8 | P0 |
| Content Pollution（通用文档含项目内容）| 18 | P0 |
| Prompt Example Pollution（prompt 示例污染）| 9 | P0 |
| Eval Case Pollution（评测用真实业务案例）| 6 | P0 |
| Methodology Pollution（方法论文档含项目案例）| 12 | P1 |
| Report Pollution（交付报告/示例输出）| 3 | P1 |
| History Pollution（已推送的旧 commit）| - | P0 |

### 关键判断

- **不能简单字符串替换** — 必须按 §2 分类做内容重构
- **必须 force push** — 远程历史里有完整 PRD / 业务详情，不改写无法清除
- **npm-package 必须立即处理** — 如果 0.6.2 已发布，需评估是否 deprecate

---

## 1. 污染类型分类（7 类）

### 1.1 Path Pollution（路径污染）

**文件路径或目录名直接含项目代号**

| 路径 | 命中类别 | 风险 |
|------|---------|------|
| `knowledge/design/cases/[CASE-DIR-1]/` | 目录代号 + 含 [PROD-1], [IP-CHAR], [IP-COLOR] | **P0** |
| `knowledge/design/cases/[CASE-DIR-2]/` | 目录代号 + 含 [PROD-1], [PROD-2] | **P0** |
| 含上述目录的所有 8 个文件 | path + content | **P0** |

**性质**：目录名本身就是泄露。即使内容脱敏，路径泄露项目代号。

---

### 1.2 Content Pollution（通用文档含项目内容）

**项目通用方法论/文档/配置文件中嵌入了真实项目内容**

| 文件 | 命中性质 | 风险 | 责任 |
|------|---------|------|------|
| `knowledge/manifest.yaml` | 第 456/467 行注册 [CASE-DIR-1/2] 为 stable_id | **P0** | 项目历史 |
| `knowledge/design-work-paradigm/31-Color-System.md` | 用项目专属色名 [IP-COLOR] 做举例 | P1 | **本会话引入** |
| `knowledge/design/ip/ip-design-methodology.md` | 方法论里嵌入 [PROD-1] 案例 | **P0** | 项目历史 |
| `knowledge/design/ip/worldview-building.md` | 同上 | **P0** | 项目历史 |
| `knowledge/design/ip/content-narrative.md` | 同上 | **P0** | 项目历史 |
| `knowledge/design/ip/brand-material-realization.md` | 同上 | **P0** | 项目历史 |
| `knowledge/design/persona/persona-modeling.md` | 含 [IP-CHAR] | **P0** | 项目历史 |
| `knowledge/design/persona/voice-and-behavior-boundary.md` | 同上 | **P0** | 项目历史 |
| `knowledge/design/strategy/brand-strategy-alignment.md` | 含 [PROD-1]/[COMP] | **P0** | 项目历史 |
| `knowledge/design/visual/image-prompt-system.md` | 含 [IP-COLOR]/[IP-CHAR] | **P0** | 项目历史 |
| `knowledge/design/visual/visual-translation.md` | 同上 | **P0** | 项目历史 |
| `legacy/agent-prototypes/ip-design-agent.html` | 9 处命中（早期 prototype）| P1 | 项目历史 |
| `docs/plans/2026-05-29-prd2proto-v0.2-completion.md` | 项目交付报告 | **P0** | 项目历史 |
| `docs/releases/ip-design-asset-baseline/README.md` | 发布说明含完整品牌资产清单 | **P0** | 项目历史 |
| `examples/prd2proto/outputs/02-design-objectives.json` | 真实 PRD 的产出 | **P0** | **本会话引入** |

---

### 1.3 Prompt Example Pollution（Prompt 示例污染）⚠️ 我的责任

**通用 prompt 模板中嵌入了真实项目示例**

| 文件 | 命中处 | 风险 | 责任 |
|------|-------|------|------|
| `skills/prd2proto/prompts-v2/02-design-objectives.md` | 5 处："示例（[PROD-1]）"/JTBD/UES rationale | **P0** | **本会话引入** |
| `skills/prd2proto/prompts-v2/03-product-archetype.md` | 引用 [PROD-1] | **P0** | **本会话引入** |
| `skills/prd2proto/prompts-v2/06-user-journey-mapping.md` | 2 处 | **P0** | **本会话引入** |
| `skills/prd2proto/prompts-v2/07-information-architecture.md` | 4 处 | **P0** | **本会话引入** |
| `skills/prd2proto/prompts-v2/08-page-flow.md` | 含 [PROD-1] | **P0** | **本会话引入** |
| `skills/prd2proto/prompts-v2/11-state-matrix.md` | 含 [PROJ-DOMAIN] | **P0** | **本会话引入** |
| `skills/prd2proto/prompts-v2/12-interaction-rules.md` | 含 [PROD-1] | **P0** | **本会话引入** |
| `skills/prd2proto/prompts-v2/16-traceability-generation.md` | 含 [PROD-1] | **P0** | **本会话引入** |
| `skills/prd2proto/runtime/llm_client.py` | 注释提到代理域名 | P1 | 本会话引入 |

**根本错误**：我把"用户给我的真实 PRD（验证用）"当作"通用 prompt 示例"嵌入了模板。
正确做法：用 `<合成案例>` / `<企业 AI 工具示例>` / 抽象占位词。

---

### 1.4 Eval Case Pollution（评测案例污染）

**eval 评测案例使用了项目真实业务场景**

| 文件 | 命中性质 | 风险 |
|------|---------|------|
| `skills/brand-creative/sub-skills/brand-strategy/eval/promptfoo.yaml` | "EduFlow K12 教师备课助手" + 真实业务详情 | **P0** |
| `skills/brand-creative/sub-skills/brand-strategy/eval/failure/failure-01-inferred.yaml` | 同上 | **P0** |
| `skills/brand-creative/sub-skills/brand-strategy/reference/case-inferred-differentiation.md` | 完整教育业务案例 | **P0** |
| `skills/ip-design/eval/golden/prompt-four-layers.md` | 含 [PROD-1]/[IP-CHAR] | **P0** |
| `skills/uxeval/prompts/04-task-generation.md` | 第 81 行："参考真实业务文档「任务脚本-[REAL-COURSE-NAME]」" | **P0** |
| `skills/prd2proto/tests/test_reality_hardening.py` | 第 73-75 行**列举所有内部品牌词作为防泄露黑名单** | **P0** |

⚠️ **`test_reality_hardening.py` 特殊**：意图是"防止项目专属词进通用 skill"的测试，但**测试代码本身列出所有项目专属词作为黑名单字符串**，等于公开。需重构为读外部加密配置。

---

### 1.5 Report Pollution（报告污染）

| 文件 | 命中 | 风险 |
|------|------|------|
| `docs/plans/2026-05-29-prd2proto-v0.2-completion.md` | 完成报告含项目业务 | **P0** |
| `docs/releases/ip-design-asset-baseline/README.md` | 发布说明 | **P0** |
| `examples/prd2proto/outputs/02-design-objectives.json` | 真实产出（我提交）| **P0** |

---

### 1.6 Methodology Pollution（方法论污染）

**方法论文档（应该是通用的）中引用了项目专属 case**

| 文件 | 命中 | 风险 |
|------|------|------|
| `knowledge/design/quality/professional-gap-report.md` | 引用 [CASE-DIR-1/2] 作示例 | **P0** |
| `knowledge/design/quality/common-failure-modes.md` | 同上 | **P0** |
| `knowledge/design/quality/stage-review-checklists.md` | 同上 | **P0** |
| `knowledge/design/quality/ip-design-quality-rubric.md` | 同上 | **P0** |
| 其他 8 个 knowledge/design/* 文件 | 同上 | **P0** |

---

### 1.7 npm-package（双份污染源）

| 文件 | 性质 |
|------|------|
| `npm-package/skills/ip-design/SKILL.md` 等 9 个 | **已发布到公网 npm registry**（如果发布过）|
| `npm-package/package.json` | designos@0.6.2 |

⚠️ **`npm-package/` 是 `skills/` 的镜像**（构建产物），用户 `npm install designos` 后能拿到。

---

### 1.8 History Pollution（历史污染）

**已推送到远程的提交里仍含污染**

- 远程 `origin/feature/senior-designer-paradigm-engine` HEAD = `7d5fa73`
- 含本会话 5 commit + 历史 commit
- 历史 commit 里包含：
  - 我引入污染的 commit（acdc7dc, 116b8f8, e7eb6c0, ec39156, 7ef3893 等 Phase 2 prompts）
  - 项目早期 commit（e4f1f7f 引入 IP cases，等更早的）

**结论**：必须 force push 才能从远程清除。

---

## 2. 资产处理原则

### 2.1 必须删除（delete）

| 类别 | 文件 | 理由 |
|------|------|------|
| 项目专属 case 目录 | `knowledge/design/cases/[CASE-DIR-1]/`（4文件）| 整个目录是项目证据，不属通用知识 |
| 项目专属 case 目录 | `knowledge/design/cases/[CASE-DIR-2]/`（4文件）| 同上 |
| 历史 prototype | `legacy/agent-prototypes/ip-design-agent.html` | 早期项目原型 |
| 项目交付报告 | `docs/plans/2026-05-29-prd2proto-v0.2-completion.md` | 项目内部报告 |
| 项目发布说明 | `docs/releases/ip-design-asset-baseline/` | 项目发布物 |
| 真实产出示例 | `examples/prd2proto/outputs/02-design-objectives.json` | 真实 PRD 的输出 |
| **`npm-package/` 整目录** | 9 个文件 | 镜像污染源，且已发布 |

### 2.2 必须重写（rewrite as synthetic）

| 文件 | 重写方向 |
|------|---------|
| 我编写的 8 个 prompts-v2 含项目示例 | 示例段落改为合成案例（"假设场景：B 端任务型 AI 工具"）|
| `knowledge/design-work-paradigm/31-Color-System.md` | 项目专属色名 [IP-COLOR] 等具体色名 → 通用色名（橙色/暖色调）|
| `skills/brand-creative/.../eval/promptfoo.yaml` | EduFlow 案例 → 合成案例（虚构产品 + 虚构市场）|
| `skills/brand-creative/.../eval/failure-*.yaml` | 同上 |
| `skills/brand-creative/.../reference/case-*.md` | 同上 |
| `skills/uxeval/prompts/04-task-generation.md` | 删除"参考真实业务文档"引用，改为合成案例 |
| `skills/ip-design/eval/golden/prompt-four-layers.md` | 同 prompts |
| `skills/prd2proto/tests/test_reality_hardening.py` | 黑名单移到外部加密文件，代码只引用文件路径 |
| `skills/prd2proto/runtime/llm_client.py` | 注释中代理域名脱敏 |

### 2.3 抽象保留（keep as pattern）

**通用方法论概念，与具体项目无关**

- "武侠/西游/赛博朋克" 等文化原型枚举（保留）
- "ENFP/INTJ" 等性格原型（通用心理学，保留）
- 设计方法论框架结构（UES/HEART/JTBD 等）（保留）

### 2.4 可作为合成案例重建

`knowledge/design/cases/` 应保留作为方法论案例，但内容**全部重建**：
- 用 `case-001-synthetic-edu-tool/`、`case-002-synthetic-saas/` 等合成场景
- 不再含真实业务、产品名、IP、色彩

### 2.5 不能进入公开仓库

- 任何含具体公司名、产品代号、IP 角色名、内部色彩、内部业务流程
- 任何含真实学校名、课程名、市场细分
- 任何本地路径、内部 URL、内部代理域名
- 任何 token / key / secret / api（不限于已扫到的）

---

## 3. 历史改写方案

### 3.1 工具

**`git filter-repo`**（Git 官方推荐，比 filter-branch 快 100×）

```bash
# 安装
pip install git-filter-repo
# 或
brew install git-filter-repo
```

### 3.2 改写步骤（草案，等你确认）

```bash
# 1. 备份
git tag backup-pre-S0-$(date +%s)
git push origin backup-pre-S0-... --tags  # 推备份

# 2. 删路径
git filter-repo \
  --path knowledge/design/cases/[CASE-DIR-1]/ --invert-paths \
  --path knowledge/design/cases/[CASE-DIR-2]/ --invert-paths \
  --path legacy/agent-prototypes/ip-design-agent.html --invert-paths \
  --path docs/plans/2026-05-29-prd2proto-v0.2-completion.md --invert-paths \
  --path docs/releases/ip-design-asset-baseline/ --invert-paths \
  --path examples/prd2proto/ --invert-paths \
  --path npm-package/ --invert-paths

# 3. 文本替换（敏感词 → 占位）
git filter-repo --replace-text replace-rules.txt
# replace-rules.txt 内容（每行 "原词==>替换词"，原词列表保存在本地私有文件，不入仓库）：
#   [PROD-1]==><PRODUCT-AI-ASSISTANT>
#   [COMP]==><INTERNAL-COMPANY>
#   ... 等

# 4. 验证
git ls-files | xargs grep -lE "敏感词清单"  # 应为空
git log -p | grep -E "敏感词清单"  # 应为空

# 5. force push
git push origin feature/senior-designer-paradigm-engine --force-with-lease
```

### 3.3 替换映射（待你确认）

| 原词类别 | 建议替换为 |
|---------|-----------|
| [PROD-1] 主产品代号 | `<INTERNAL-PROD>` 或合成名 |
| [PROD-2] 子项目代号 | `<INTERNAL-SUB-PROD>` |
| [COMP] 公司名 | `<INTERNAL-COMPANY>` |
| [IP-CHAR] IP 角色（多个）| 全部删除或换合成名（"角色 A/B"）|
| [IP-COLOR] 项目色名（多个）| `<BRAND-PRIMARY>` / `<BRAND-ACCENT>` 或具体 hex |
| [PROJ-DOMAIN] 项目专属域名术语（多个） | `<DOMAIN-A>` 或删除整段 |
| 学校名 | 删除整段（不是替换）|
| 真实业务案例（教育/医疗等具体）| 整段重写为合成案例 |

### 3.4 force push 风险

- 你单人开发 → 风险低
- 但所有 commit hash 会变
- 已发布的 npm @0.6.2 不可撤回（需 npm deprecate + 0.7.0 干净版本）
- ChatGPT/外部如果引用了 commit hash 会失效

### 3.5 回滚备份方案

```bash
# 改写前保留 tag
git tag backup-pre-S0-$(date +%Y%m%d-%H%M%S)
# 推到远程（私有备份分支，可选）
git push origin --tags
```

---

## 4. 待你确认项

### 4.1 删除决策（请逐项确认）

- [ ] 删除 `knowledge/design/cases/[CASE-DIR-1]/` 全部 4 文件
- [ ] 删除 `knowledge/design/cases/[CASE-DIR-2]/` 全部 4 文件
- [ ] 删除 `legacy/agent-prototypes/ip-design-agent.html`
- [ ] 删除 `docs/plans/2026-05-29-prd2proto-v0.2-completion.md`
- [ ] 删除 `docs/releases/ip-design-asset-baseline/` 整目录
- [ ] 删除 `examples/prd2proto/outputs/` 整目录
- [ ] 删除 `npm-package/` **整个目录**（双份污染源 + 已发布风险）
- [ ] `knowledge/manifest.yaml` 删除引用 [CASE-DIR-1/2] 的两个 entry

### 4.2 重写决策

- [ ] 我重写 8 个 prompts-v2 的示例段落（合成案例）—— **我的责任**
- [ ] `31-Color-System.md` 项目色名改通用色 —— **我的责任**
- [ ] `brand-creative/.../eval/*` 教育案例改合成 —— **谁来重写？**
- [ ] `uxeval/prompts/04-task-generation.md` 删除真实业务引用
- [ ] `ip-design/eval/golden/prompt-four-layers.md` 重写
- [ ] `test_reality_hardening.py` 黑名单外置（保留测试逻辑，去除字符串列表）

### 4.3 保留决策

- [ ] 保留"武侠/西游/赛博朋克"等通用文化原型词（不一刀切）
- [ ] 保留 ENFP/INTJ 等性格原型词
- [ ] 保留所有方法论框架结构（UES/HEART/JTBD/GSM）

### 4.4 npm 包决策

- [ ] 你要 deprecate `designos@0.6.2`（npm 公网）吗？
- [ ] 还是发 `0.7.0` 干净版本（不影响已下载用户）？
- [ ] `npm-package/` 目录**保留构建脚本但不存源码**（构建时从 `skills/` 复制+脱敏）？

### 4.5 force push 决策

- [ ] 同意 force push origin/feature/senior-designer-paradigm-engine
- [ ] 同意打 backup tag 备份当前远程 HEAD
- [ ] 改写后 ChatGPT 引用的 commit hash 会失效，可接受？

### 4.6 主分支决策

- [ ] main 分支需要同样改写吗？（如果 main 的历史也含污染）
- [ ] 还是只改写 feature 分支？

---

## 5. 资产升维重构原则（执行规范）

按用户红线："不是敏感词替换，而是证据到模式的升维重构"

### 5.1 原则

| 原则 | 含义 |
|------|------|
| 证据归证据 | 真实业务材料只在本地、私有，不入仓库 |
| 模式归模式 | 通用 prompt/skill/knowledge 用合成示例 |
| 案例归案例 | knowledge/design/cases/ 用合成 case，不用真实证据 |
| 升维优先于替换 | "[PROD-1] 是 B 端工具"→"假设是 B 端任务型 AI 工具"（重构语义，非字符替换）|
| 抽象优先于具体 | "[BRAND-COLOR] #0070C9"→"品牌主色（蓝色调，对比度≥4.5）"|
| 不损方法论 | 通用文化原型枚举（武侠/赛博朋克）保留 |

### 5.2 重写检查清单

每个重写后的文件必须通过：

- [ ] 不含任何具体公司/产品/IP/学校/色名
- [ ] 不含项目专属域名术语（[PROJ-DOMAIN] 类）
- [ ] 不含本地路径或内部 URL
- [ ] 示例使用合成场景（"虚构产品 X"、"假设场景"）
- [ ] 方法论本身的可复用性不受损
- [ ] 与同类资产风格一致

---

## 6. 执行前等你回答的关键问题

1. **删除范围**：§4.1 的 7 项删除，是否全部同意？特别是 **npm-package/ 整目录**和 **examples/prd2proto/**？
2. **重写工作量**：§4.2 涉及大量内容重构（不是字符替换），预计 4-6 小时。同意我做？
3. **替换映射**：§3.3 的占位词，用 `<INTERNAL-PROD>` 这种方括号占位，还是合成产品名（如 "AcmeAI"）？
4. **npm 公网**：§4.4 你想怎么处理已发布的 0.6.2？
5. **main 分支**：§4.6 main 是否同样改写？
6. **force push**：§4.5 同意吗？
7. **执行节奏**：A) 我一次做完所有 §4.1-4.4 再让你看？B) 分阶段（先删除/再重写/再历史改写）每阶段你确认？

---

## 7. 我的诚实承认

8 个我引入的污染（commit `acdc7dc` 等）是**我的责任**：
- 我把"用户给的真实 PRD"和"我应该写的通用 prompt 模板"混淆了
- 应该用合成示例，但用了真实产品名
- 这次重写以我承担为主

49 个项目历史污染**不是我引入**，但都已和我会话期间的污染一起推到远程，必须一起改写。

---

**审计报告完毕**。**未做任何改动**。等你回答 §6 的 7 个问题后再执行。
