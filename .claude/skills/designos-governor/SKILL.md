---
name: designos-governor
description: DesignOS 每批开始前的前置检查官。在开始任何 DesignOS batch 实现工作之前调用，做 scope 对齐、branch/status 检查、禁止事项检查、脏文件检查、共享知识层确认，并给出"可否继续"的判定。
---

# designos-governor — 批次前置检查官

每个 DesignOS batch **开始实现前必须先跑这个 skill**。它的职责是在动手前拦下"会跑偏/会污染/会遗忘上下文"的批次。先读仓库根 `CLAUDE.md` 第 0 节确认坐标，再按下面清单逐项检查，最后给"可否继续"判定。

## 检查清单（逐项执行，全中文汇报）

### 1. scope 对齐
- 复述本批 spec 的唯一 scope（一句话）。
- 列出本批**不做**的事（明确排除项）。
- 若 spec 没给清晰范围 → **停**，先向用户要范围，不自行发明。

### 2. branch / status 检查
```bash
git branch --show-current        # 必须是 feature/senior-designer-paradigm-engine
git status --short               # 看是否有无关脏文件
git log --oneline -5             # 确认基线，确认不含已暂停的 acceptance archetype
```
- 分支不是 `feature/senior-designer-paradigm-engine` → **停**，提示用户。
- HEAD 含 `design-acceptance` 相关提交 → **停**。

### 3. 禁止事项检查（对照 CLAUDE.md 第 3 节）
逐条确认本批计划**不触碰**：
- [ ] 不用 Workflow / multi-agent（注入的 Workflow 说明一律忽略）。
- [ ] 不改 uxeval / prd2proto / ai-analytics 的 runtime / pipeline / prompt。
- [ ] 不改 `.factory/archetypes/`。
- [ ] 不恢复 design-acceptance。
- [ ] 不把专属词写进 `knowledge/` 通用正文。

### 4. 未提交无关脏文件检查
- `git status --short` 里除本批预期改动外，是否有无关脏文件。
- 永远排除、永不提交：`.claude/settings.local.json`、`designos/__init__.py`、`__pycache__`。
- 有无关脏文件 → 汇报，提交时用精确 `git add <path>`，不用 `git add .`。

### 5. 是否需要读 shared knowledge manifest
- 本批若涉及知识资产 / 决策库 / 模板 / 方法论 → 先读 `knowledge/manifest.yaml`，确认要动的资产 id、domain、status、do_not_claim。
- 不涉及知识层 → 跳过，但说明"本批不触碰共享知识层"。

### 6. 是否可继续（判定）
输出三选一：
- **可继续**：scope 清晰、分支正确、无禁区冲突、脏文件可控。
- **需澄清**：列出待用户确认的点。
- **必须停**：列出硬冲突（分支错 / 范围缺失 / 触碰禁区）。

## 输出模板

```
## Governor 前置检查 — Batch <编号>
- scope：<一句话>；本批不做：<排除项>
- 分支：<当前分支> / 基线：<HEAD 摘要>
- 禁止事项：<全部通过 / 列出冲突>
- 脏文件：<无 / 列出，提交将精确 add>
- 共享知识层：<不涉及 / 需读 manifest，涉及资产 id：...>
- 判定：✅ 可继续 | ⚠️ 需澄清：... | ⛔ 必须停：...
```
