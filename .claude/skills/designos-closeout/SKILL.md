---
name: designos-closeout
description: DesignOS 每批结束前的收口检查官。在结束任何 DesignOS batch、提交或汇报之前调用，跑 git 状态/diff 检查、测试、禁止文件检查、旧 skill 行为变更检查，并按中文模板产出 closeout，给出能否进入下一批的判定。
---

# designos-closeout — 批次收口检查官

每个 DesignOS batch **结束前（提交/汇报前）必须先跑这个 skill**。它确保本批改动范围可控、测试有据、没污染禁区、没悄悄改变旧 skill 行为，并产出标准中文 closeout。

## 执行步骤（逐项，全中文汇报）

### 1. 改动盘点
```bash
git status --short
git diff --stat
git diff --name-only
```
- 核对实际改动文件是否都落在本批 scope 内。
- 出现 scope 外文件 → 解释原因或回退。

### 2. 禁止文件检查
确认改动 / 暂存里**没有**：
- `.claude/settings.local.json`
- `designos/__init__.py`
- 任何 `__pycache__` / `*.pyc`

若已误入暂存 → `git restore --staged <path>` 移出，提交用精确 `git add`。

### 3. 测试命令与结果
- 跑本批相关测试，记录**命令 + 结果数字**（如 `8 passed`），不能只写"测试通过"。
- 改动可能影响 factory 时，加跑 `.factory` 测试确认零回归：
```bash
python3 -m pytest -q <本批测试路径>
cd .factory && python3 -m pytest tests/ -q
```
- 涉及"红线"类断言（如禁止专属词）时，做一次负向验证：故意制造违规确认测试会失败，再恢复。

### 4. 旧 skill 行为变更检查
- 本批是否改了 uxeval / prd2proto / ai-analytics 的 runtime / pipeline / prompt？
- 是否改了 `.factory/archetypes/`？
- 正常答案应为"否"。若为"是"→ 必须显式说明，并确认这是本批 spec 明确授权的。

### 5. 能否进入下一批（判定）
- ✅ 可进入：scope 收口、测试有据、禁区未碰、旧行为未变。
- ⚠️ 有遗留：列出待办，说明是否阻塞下一批。
- ⛔ 不可进入：列出未解决问题。

## 中文 closeout 模板

```
# Batch <编号> Closeout — <一句话标题>

## 1. 改动盘点
- git status --short：<结果>
- git diff --stat：<结果>
- 改动文件是否都在 scope 内：<是/否，说明>

## 2. 禁止文件检查
- settings.local.json / designos/__init__.py / __pycache__：<均未触碰 / 处理说明>

## 3. 测试命令与结果
- <命令> → <X passed>
- factory 零回归：<命令> → <X passed>
- 负向验证（如适用）：<做了什么 / 结果 / 已恢复>

## 4. 旧 skill 行为
- uxeval/prd2proto/ai-analytics runtime/pipeline/prompt：<未改动 / 说明>
- factory archetype：<未改动 / 说明>

## 5. 是否可进入下一批
- <✅ 可进入 / ⚠️ 有遗留 / ⛔ 不可进入>，理由：...
- 是否推送：默认不推送，除非用户明确要求。
```
