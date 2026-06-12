> ⚠️ **ARCHIVED / OUTDATED — DO NOT USE FOR CURRENT STATUS.**
> 本文件是历史过程记录，不代表当前状态。当前权威状态见仓库根
> `INTERNAL-PILOT-README.md` / `REVIEW-MANIFEST.md` / `skills/status.matrix.yaml`。

# 方法论覆盖分析

**分析日期**: 2026-06-09
**核心问题**: 现有 19 个方法论是否覆盖所有 skills？
**诚实结论**: ❌ 覆盖严重不足，尤其 brand-creative

---

## 🎯 Skills 全景

### 主 Skills（5 个）
1. uxeval - UX 评估
2. prd2proto - PRD 转原型
3. ai-analytics - AI 分析
4. ip-design - IP 设计
5. brand-creative - 品牌创意（含 13 子技能）

### brand-creative 子技能（13 个）
1. brand-strategy - 品牌策略
2. brand-audit - 品牌审计
3. competitive-analysis - 竞品分析
4. logo-design - Logo 设计
5. color-system - 色彩系统
6. typography-system - 字体系统
7. visual-identity - 视觉识别
8. brand-voice - 品牌声音
9. content-strategy - 内容策略
10. campaign-creative - 营销创意
11. brand-collateral - 品牌物料
12. digital-assets - 数字资产
13. brand-guidelines - 品牌手册

**总计**: 5 主 + 13 子 = 18 个能力单元

---

## 📋 覆盖矩阵

### prd2proto（覆盖良好）

| 方法论 | 覆盖 | 状态 |
|--------|------|------|
| 01-input-diagnosis | ✅ | 完整 |
| 02-objective-decomposition | ✅ | 框架 |
| 03-user-task-modeling | ✅ | **完整(标杆)** |
| 05-business-flow-modeling | ✅ | 框架 |
| 06-user-journey-mapping | ✅ | 框架 |
| 07-information-architecture | ✅ | 框架 |
| 08-page-flow-modeling | ✅ | 框架 |
| 09-content-structure | ✅ | 框架 |
| 10-component-strategy | ✅ | 框架 |
| 11-state-matrix | ✅ | 框架 |
| 12-interaction-rules | ✅ | 框架 |

**覆盖率**: ✅ 优秀（11 个方法论完整覆盖流程）

---

### uxeval（覆盖不足）

| 需要的方法论 | 现状 | 问题 |
|-------------|------|------|
| 输入诊断 | ✅ 01 | 可用 |
| 用户旅程 | ✅ 06 | 可用 |
| **启发式评估** | ❌ 缺失 | Nielsen 10 原则应用方法 |
| **严重度评级** | ❌ 缺失 | 问题严重度判断方法 |
| **问题归因** | ❌ 缺失 | 根因分析方法 |
| 评估证据 | ⚠️ 16 框架 | 需完善 |

**覆盖率**: ⚠️ 不足（缺 3 个核心评估方法论）

**缺失方法论**:
- `20-heuristic-evaluation`（启发式评估）
- `21-severity-rating`（严重度评级）
- `22-issue-attribution`（问题归因）

---

### ai-analytics（覆盖不足）

| 需要的方法论 | 现状 | 问题 |
|-------------|------|------|
| 输入诊断 | ✅ 01 | 可用 |
| 目标分解 | ✅ 02 | 可用 |
| **研究方法选择** | ❌ 缺失 | 如何选择分析方法 |
| **证据提取** | ❌ 缺失 | 从资料提取洞察 |
| **竞品分析** | ⚠️ 04 部分 | 场景建模不专门 |
| **策略综合** | ❌ 缺失 | 从洞察到策略 |

**覆盖率**: ⚠️ 不足（缺 3 个研究方法论）

**缺失方法论**:
- `23-research-methodology`（研究方法选择）
- `24-evidence-extraction`（证据提取）
- `25-strategy-synthesis`（策略综合）

---

### ip-design（覆盖不足）

| 需要的方法论 | 现状 | 问题 |
|-------------|------|------|
| IP 角色建模 | ⚠️ 15 框架 | 需完善 |
| 视觉翻译 | ⚠️ 13 框架 | 太笼统 |
| **世界观构建** | ❌ 缺失 | IP 世界观方法 |
| **人格建模** | ❌ 缺失 | 角色人格方法 |
| **视觉锁定** | ❌ 缺失 | design locks 方法 |

**覆盖率**: ⚠️ 不足（缺 3 个 IP 专门方法论）

**缺失方法论**:
- `26-worldview-building`（世界观构建）
- `27-persona-modeling`（人格建模）
- `28-visual-lock-definition`（视觉锁定）

---

### brand-creative 子技能（严重不足）

#### 已有部分覆盖（4/13）

| 子技能 | 对应方法论 | 状态 |
|--------|-----------|------|
| brand-strategy | 14-brand-strategy-modeling | ⚠️ 框架 |
| competitive-analysis | (ai 的 04) | ⚠️ 借用 |
| logo-design | 13-visual-translation | ❌ 不专门 |
| visual-identity | 13-visual-translation | ❌ 不专门 |

#### 完全缺失（9/13）

| 子技能 | 需要的方法论 | 状态 |
|--------|-------------|------|
| brand-audit | 品牌审计方法 | ❌ 缺失 |
| color-system | 色彩系统方法 | ❌ 缺失 |
| typography-system | 字体系统方法 | ❌ 缺失 |
| brand-voice | 品牌声音方法 | ❌ 缺失 |
| content-strategy | 内容策略方法 | ❌ 缺失 |
| campaign-creative | 营销创意方法 | ❌ 缺失 |
| brand-collateral | 物料设计方法 | ❌ 缺失 |
| digital-assets | 数字资产方法 | ❌ 缺失 |
| brand-guidelines | 品牌手册方法 | ❌ 缺失 |

**覆盖率**: ❌ 严重不足（13 个子技能仅 4 个部分覆盖）

**缺失方法论**:
- `29-brand-audit`（品牌审计）
- `30-logo-design`（Logo 设计专门方法）
- `31-color-system`（色彩系统）
- `32-typography-system`（字体系统）
- `33-visual-identity-integration`（视觉识别整合）
- `34-brand-voice`（品牌声音）
- `35-content-strategy`（内容策略）
- `36-campaign-creative`（营销创意）
- `37-brand-collateral`（品牌物料）
- `38-digital-assets`（数字资产）
- `39-brand-guidelines`（品牌手册）

---

## 📊 总体覆盖率

### 按 Skill 统计

| Skill | 需要方法论 | 已覆盖 | 完整 | 覆盖率 |
|-------|-----------|--------|------|--------|
| prd2proto | 11 | 11 | 1 | ✅ 100%(框架) |
| uxeval | 6 | 3 | 0 | ⚠️ 50% |
| ai-analytics | 6 | 3 | 0 | ⚠️ 50% |
| ip-design | 5 | 2 | 0 | ⚠️ 40% |
| brand-creative | 13 | 4 | 0 | ❌ 31% |

### 方法论数量

```
现有方法论：19 个（1 完整 + 18 框架）
需要补充：~20 个（覆盖所有 skills）
────────────────────────────
完整方法论库：~39 个
```

---

## 🎯 完整方法论规划

### 通用方法论（00-19，已有）

```
00-core-principles          ✅ 完整
01-input-diagnosis          ✅ 完整
02-objective-decomposition  ⚠️ 框架
03-user-task-modeling       ✅ 完整(标杆)
04-scenario-modeling        ⚠️ 框架
05-business-flow-modeling   ⚠️ 框架
06-user-journey-mapping     ⚠️ 框架
07-information-architecture ⚠️ 框架
08-page-flow-modeling       ⚠️ 框架
09-content-structure        ⚠️ 框架
10-component-strategy       ⚠️ 框架
11-state-matrix             ⚠️ 框架
12-interaction-rules        ⚠️ 框架
13-visual-translation       ⚠️ 框架(需拆分)
14-brand-strategy-modeling  ⚠️ 框架
15-ip-character-modeling    ⚠️ 框架(需拆分)
16-evaluation-evidence      ⚠️ 框架
17-quality-rubrics          ✅ 完整
18-failure-modes            ✅ 完整
19-traceability             ✅ 完整
```

### UX 评估方法论（20-22，需新增）

```
20-heuristic-evaluation     启发式评估（Nielsen 10 原则）
21-severity-rating          严重度评级
22-issue-attribution        问题归因
```

### 研究方法论（23-25，需新增）

```
23-research-methodology     研究方法选择
24-evidence-extraction      证据提取
25-strategy-synthesis       策略综合
```

### IP 设计方法论（26-28，需新增）

```
26-worldview-building       世界观构建
27-persona-modeling         人格建模
28-visual-lock-definition   视觉锁定
```

### 品牌设计方法论（29-39，需新增）

```
29-brand-audit              品牌审计
30-logo-design              Logo 设计
31-color-system             色彩系统
32-typography-system        字体系统
33-visual-identity-integration 视觉识别整合
34-brand-voice              品牌声音
35-content-strategy         内容策略
36-campaign-creative        营销创意
37-brand-collateral         品牌物料
38-digital-assets           数字资产
39-brand-guidelines         品牌手册
```

---

## 💡 关键决策

### 决策 1：是否覆盖全部 skills？

**选项 A：先覆盖核心 skills（prd2proto + uxeval）**
- 完善 prd2proto 的 11 个方法论
- 新增 uxeval 的 3 个方法论
- **工作量**: ~14 个方法论
- **价值**: 让 2 个核心 skill 达到资深级别

**选项 B：覆盖全部 skills**
- 完善现有 19 个
- 新增 20 个
- **工作量**: ~39 个方法论
- **价值**: 全部 skill 达到资深级别

### 决策 2：方法论粒度

**问题**：13-visual-translation 太笼统

**方案**：
- 拆分为：logo-design / color-system / typography-system
- 或保留通用 + 各 skill 专门补充

---

## 🎯 我的建议

### 诚实评估

**当前方法论库的真实覆盖率**：
- prd2proto: 100%（框架）
- 其他 4 个主 skill: 31-50%
- **整体: ~45%**

**要达到"所有 skill 资深级别"**：
- 需要约 39 个完整方法论
- 当前只有 1 个完整（03）

### 推荐路径

**Phase A1：核心流程方法论（prd2proto）**
- 完善 02, 05, 06, 07, 08, 09, 10, 11, 12（9 个）
- 让 prd2proto 完全达到资深级别
- 这是最核心的 skill

**Phase A2：UX 评估方法论（uxeval）**
- 新增 20, 21, 22（3 个）
- 完善 16
- 让 uxeval 达到资深级别

**Phase A3：研究方法论（ai-analytics）**
- 新增 23, 24, 25（3 个）
- 完善 02, 04

**Phase A4：IP 设计方法论（ip-design）**
- 新增 26, 27, 28（3 个）
- 完善 13, 15

**Phase A5：品牌设计方法论（brand-creative）**
- 新增 29-39（11 个）
- 这是最大的缺口

---

## ✅ 结论

**回答你的问题**："方法论是否覆盖全部 skills？"

**诚实答案**: ❌ **没有**

- prd2proto: ✅ 覆盖（但需完善）
- uxeval: ⚠️ 50%（缺评估方法论）
- ai-analytics: ⚠️ 50%（缺研究方法论）
- ip-design: ⚠️ 40%（缺 IP 方法论）
- brand-creative: ❌ 31%（缺品牌方法论）

**要全覆盖需要**：
- 完善现有 16 个框架方法论
- 新增约 20 个方法论
- 总计约 39 个完整方法论

**这是一个巨大的工作量，但这才是"所有 skill 都达到资深级别"的真实要求。**
