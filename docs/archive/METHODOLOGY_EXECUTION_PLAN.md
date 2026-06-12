> ⚠️ **ARCHIVED / OUTDATED — DO NOT USE FOR CURRENT STATUS.**
> 本文件是历史过程记录，不代表当前状态。当前权威状态见仓库根
> `INTERNAL-PILOT-README.md` / `REVIEW-MANIFEST.md` / `skills/status.matrix.yaml`。

# 方法论完整执行计划（C+B）

**策略**: 按 skill 优先级逐个攻克（C），最终覆盖全部 skills（B）
**目标**: 所有 skill 达到资深设计师级别
**时间**: 无限制，质量优先

---

## 🎯 执行原则

1. **逐个 skill 完整攻克**（不是所有 skill 半成品）
2. **每个 skill 完成后真实验证**（达到资深级别再下一个）
3. **最终覆盖全部 5 主 + 13 子 = 18 个能力单元**
4. **方法论标准**：以 03-user-task-modeling 为标杆

---

## 📋 完整方法论清单（39 个）

### 通用流程方法论（00-19）

| 编号 | 方法论 | 服务 Skill | 状态 |
|------|--------|-----------|------|
| 00 | core-principles | 全部 | ✅ 完整 |
| 01 | input-diagnosis | 全部 | ✅ 完整 |
| 02 | objective-decomposition | prd2proto, ai-analytics | ⚠️ 框架 |
| 03 | user-task-modeling | prd2proto | ✅ **标杆** |
| 04 | scenario-modeling | prd2proto, ai-analytics | ⚠️ 框架 |
| 05 | business-flow-modeling | prd2proto | ⚠️ 框架 |
| 06 | user-journey-mapping | prd2proto, uxeval | ⚠️ 框架 |
| 07 | information-architecture | prd2proto | ⚠️ 框架 |
| 08 | page-flow-modeling | prd2proto | ⚠️ 框架 |
| 09 | content-structure | prd2proto | ⚠️ 框架 |
| 10 | component-strategy | prd2proto | ⚠️ 框架 |
| 11 | state-matrix | prd2proto | ⚠️ 框架 |
| 12 | interaction-rules | prd2proto | ⚠️ 框架 |
| 13 | visual-translation | ip-design | ⚠️ 框架(保留通用) |
| 14 | brand-strategy-modeling | brand-creative | ⚠️ 框架 |
| 15 | ip-character-modeling | ip-design | ⚠️ 框架 |
| 16 | evaluation-evidence | uxeval | ⚠️ 框架 |
| 17 | quality-rubrics | 全部 | ✅ 完整 |
| 18 | failure-modes | 全部 | ✅ 完整 |
| 19 | traceability | 全部 | ✅ 完整 |

### UX 评估方法论（20-22，新增）

| 编号 | 方法论 | 服务 Skill |
|------|--------|-----------|
| 20 | heuristic-evaluation | uxeval |
| 21 | severity-rating | uxeval |
| 22 | issue-attribution | uxeval |

### 研究方法论（23-25，新增）

| 编号 | 方法论 | 服务 Skill |
|------|--------|-----------|
| 23 | research-methodology | ai-analytics |
| 24 | evidence-extraction | ai-analytics |
| 25 | strategy-synthesis | ai-analytics |

### IP 设计方法论（26-28，新增）

| 编号 | 方法论 | 服务 Skill |
|------|--------|-----------|
| 26 | worldview-building | ip-design |
| 27 | persona-modeling | ip-design |
| 28 | visual-lock-definition | ip-design |

### 品牌设计方法论（29-39，新增）

| 编号 | 方法论 | 服务子技能 |
|------|--------|-----------|
| 29 | brand-audit | brand-audit |
| 30 | logo-design | logo-design |
| 31 | color-system | color-system |
| 32 | typography-system | typography-system |
| 33 | visual-identity-integration | visual-identity |
| 34 | brand-voice | brand-voice |
| 35 | content-strategy | content-strategy |
| 36 | campaign-creative | campaign-creative |
| 37 | brand-collateral | brand-collateral |
| 38 | digital-assets | digital-assets |
| 39 | brand-guidelines | brand-guidelines |

---

## 🚀 执行顺序（按 Skill 优先级）

### Skill 1: prd2proto（最核心）

**需要方法论**（11 个）：
- 02-objective-decomposition
- 05-business-flow-modeling
- 06-user-journey-mapping
- 07-information-architecture
- 08-page-flow-modeling
- 09-content-structure
- 10-component-strategy
- 11-state-matrix
- 12-interaction-rules
- (03-user-task-modeling ✅ 已完成)
- (04-scenario-modeling)

**完成标准**：
- 9 个方法论达到资深级别
- 真实 PRD 测试通过
- 资深设计师评审 >= 7/10

**预计产出**：~9 个 × 5000 字 = 45,000 字

---

### Skill 2: uxeval（评估能力）

**需要方法论**（4 个）：
- 16-evaluation-evidence（完善）
- 20-heuristic-evaluation（新增）
- 21-severity-rating（新增）
- 22-issue-attribution（新增）

**完成标准**：
- 4 个方法论达到资深级别
- 真实 UI 评估测试
- 评估结果专业可信

---

### Skill 3: ai-analytics（研究能力）

**需要方法论**（5 个）：
- 02-objective-decomposition（复用）
- 04-scenario-modeling（完善）
- 23-research-methodology（新增）
- 24-evidence-extraction（新增）
- 25-strategy-synthesis（新增）

**完成标准**：
- 3 个新方法论达到资深级别
- 真实竞品分析测试

---

### Skill 4: ip-design（创意能力）

**需要方法论**（5 个）：
- 13-visual-translation（完善）
- 15-ip-character-modeling（完善）
- 26-worldview-building（新增）
- 27-persona-modeling（新增）
- 28-visual-lock-definition（新增）

**完成标准**：
- 5 个方法论达到资深级别
- 真实 IP 设计测试

---

### Skill 5: brand-creative（最大缺口，13 子技能）

**需要方法论**（12 个）：
- 14-brand-strategy-modeling（完善）
- 29-brand-audit（新增）
- 30-logo-design（新增）
- 31-color-system（新增）
- 32-typography-system（新增）
- 33-visual-identity-integration（新增）
- 34-brand-voice（新增）
- 35-content-strategy（新增）
- 36-campaign-creative（新增）
- 37-brand-collateral（新增）
- 38-digital-assets（新增）
- 39-brand-guidelines（新增）

**完成标准**：
- 12 个方法论达到资深级别
- 每个子技能真实测试

---

## 📊 工作量总览

| Skill | 方法论数 | 完成/新增 | 预计字数 |
|-------|---------|----------|---------|
| prd2proto | 11 | 9完善+0新增 | ~45,000 |
| uxeval | 4 | 1完善+3新增 | ~20,000 |
| ai-analytics | 5 | 2完善+3新增 | ~25,000 |
| ip-design | 5 | 2完善+3新增 | ~25,000 |
| brand-creative | 12 | 1完善+11新增 | ~60,000 |
| **总计** | **37** | **15完善+22新增** | **~175,000 字** |

(已完成：03 + 00/01/17/18/19 = 6 个)

---

## 🎯 当前进度

### 已完成（6/39）
- ✅ 00-core-principles
- ✅ 01-input-diagnosis
- ✅ 03-user-task-modeling（标杆）
- ✅ 17-quality-rubrics
- ✅ 18-failure-modes
- ✅ 19-traceability

### 进行中
- 🚀 Skill 1: prd2proto（开始）

### 待完成（33/39）
- prd2proto 剩余 9 个
- uxeval 4 个
- ai-analytics 5 个
- ip-design 5 个
- brand-creative 12 个

---

## 📝 每个方法论的标准（标杆）

参考 03-user-task-modeling，每个方法论必须包含：

1. **定义与目的**
   - 资深 vs 初级的本质区别

2. **适用场景**

3. **输入输出规范**
   - 引用对应 schema

4. **推理过程**（核心）
   - 分步骤
   - 每步含"资深思考方式"
   - 每步含"junior 错误"

5. **质量标准**
   - Must Have / Should Have / Nice to Have

6. **失败模式**
   - 现象/信号/根因/修复

7. **Anti-Patterns**

8. **与其他方法的关系**

9. **完整实例**
   - senior vs junior 对比

**字数**：~5000 字
**标准**：资深设计师看了说"对，我就是这么想的"

---

## 🚀 立即开始

**当前任务**：完成 prd2proto 的 9 个方法论

**顺序**（按设计推理依赖）：
1. 02-objective-decomposition（目标分解，最上游）
2. 05-business-flow-modeling（业务流程）
3. 06-user-journey-mapping（用户旅程）
4. 07-information-architecture（信息架构，核心）
5. 08-page-flow-modeling（页面流程）
6. 09-content-structure（内容结构）
7. 10-component-strategy（组件策略）
8. 11-state-matrix（状态矩阵）
9. 12-interaction-rules（交互规则）

完成后：真实验证 prd2proto

---

**开始执行 prd2proto 方法论！**
