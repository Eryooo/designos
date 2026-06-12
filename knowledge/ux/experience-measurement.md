# 体验度量方法论库

> 通用资产 · `ux.experience-measurement` · status: pilot
> 跨 skill 复用的用户体验度量方法论集，包含 UES / HEART / YOUKU / GSM 等业界公认模型。
> 本文是体验度量方法选择与维度定义的 source of truth，不含任何产品专属数据。

## purpose

为体验目标设定提供稳定、可引用的度量方法论。每个方法论有适用场景、维度定义、典型指标、GSM推导示例。使用方按产品特征选取适用方法论，体验目标按方法论维度归类。

## applies_to

- 任何需要"设定可验收的体验目标"的设计场景。
- 消费方在设定 experience_goals 时选择方法论，按维度标注 methodology 枚举值。

## decision_framework

选取适用方法论的决策链:
1. **判产品类型**: B端/C端、企业级/消费级、内容/社交/工具/电商、内部/外部。
2. **判核心诉求**: 效率>情感（B端）、增长>规范（C端）、吸引>效率（内容）。
3. **选方法论**:
   - B端/企业级 → **UES五度**（易用/一致/满意/任务/性能）
   - C端/社交工具 → **HEART六维**（Happiness/Engagement/Adoption/Retention/Task Success/Performance）
   - C端/内容分发 → **YOUKU模型**（吸引/理解/易用/任务/品牌/创新）
   - 混合型 → 按功能模块分别选择
4. **辅助方法论**: TAM（新技术接受）、CES（复杂流程费力度）、PSSUQ（情景后评估）。

## senior_heuristics

- 体验目标必须基于PRD具体场景，不能用通用指标（"要简洁"是通用，"4步流程每步≤15秒"是具体）。
- 每个体验目标走GSM推导：Goal → Signal → Metric + Why this number。
- B端不要盲目套用C端方法论（如用Engagement/Retention），反之亦然。
- 方法论选择写明理由（基于产品类型/用户群/业务特性）。
- **数量平衡**：不要为了追求每个EG都极度详尽而导致总数不足，遗漏关键目标；也不要为了凑数而产出通用指标。正确做法：识别所有关键目标，每个目标有足够的GSM推导+PRD绑定（80-150字/目标），覆盖全面优先于单个极致。合理数量：BG 3-5个，PG 5-8个，UG 5-8个，EG 10-15个。
- **PG是关键**：BG→UG之间必须有PG桥梁，PG是Driver Tree的input metrics，可被团队直接影响。若只有BG/UG/EG三层，说明缺了产品能力分解。

## quality_rubric

| 分级 | 信号 |
|------|------|
| 优 | 方法论与产品特征强匹配，体验目标基于PRD具体场景，有GSM推导链，methodology枚举正确 |
| 中 | 方法论选择合理，但部分体验目标用通用指标 |
| 差 | 方法论选择与产品类型不匹配，或体验目标全是通用指标 |

## common_failure_modes

- **盲目套用**: B端产品用HEART的Engagement/Retention（B端用户被迫使用，这些指标价值有限）。
- **通用指标**: 体验目标写"新手引导要简洁"而非"PRD§4.1.2的4步流程，每步≤15秒"。
- **不走GSM**: 只写Goal和Metric，缺Signal和Why。
- **不选方法论**: experience_goals[].methodology留空或随意选。

---

## 方法论详解

### UES 五度（阿里云）⭐ B端默认

**来源**: 阿里云设计中心  
**适用**: B端/企业级产品、云产品、SaaS、内部工具  
**特点**: 强调效率>情感，有完整工具链（PEM量表/Etest/一致性走查）

**五个维度**:

| 维度 | 定义 | Schema枚举 | 典型指标 |
|------|------|-----------|---------|
| **易用性** | 易学/易操作/清晰 | `UES-ease_of_use` | PEM评分、可用性测试通过率 |
| **一致性** | 通用范式一致程度 | `UES-consistency` | 规范覆盖率、一致性得分≥85分 |
| **满意度** | 主观综合满意度 | `UES-satisfaction` | CSAT/CES（B端用CES而非NPS） |
| **任务效率** | 完成率+时长 | `UES-task_efficiency` | 任务完成率、路径偏离度 |
| **性能** | 加载/响应/稳定 | `UES-performance` | FMP<1.5秒、API响应<2秒 |

**GSM示例**（技能安装）:
- Goal: 技能安装操作顺畅
- Signal: 用户无疑惑点击"安装"
- Metric: 基于PRD§4.3.3流程，≤3步，成功率≥95%
- Why: 可用性测试显示超3步放弃率>40%

**适用场景**: B端/企业级产品、核心诉求是效率、需要规范统一的体验。

---

### HEART 六维（Google）— C端可选

**来源**: Google UX Team (2010)  
**适用**: C端/消费级产品、社交/工具产品  
**特点**: 关注增长和情感、以用户为中心

**六个维度**:

| 维度 | 定义 | Schema枚举 | 典型指标 |
|------|------|-----------|---------|
| **Happiness** | 愉悦度/满意度 | `HEART-happiness` | NPS、满意度评分 |
| **Engagement** | 参与度/使用粘性 | `HEART-engagement` | DAU、使用时长、互动次数 |
| **Adoption** | 新功能采纳率 | `HEART-adoption` | 新功能使用率 |
| **Retention** | 留存率 | `HEART-retention` | 次日/7日/30日留存 |
| **Task Success** | 任务成功率 | `HEART-task_success` | 完成率、时长、错误率 |
| **Performance** | 性能体验 | `HEART-performance` | 加载速度、崩溃率 |

**适用场景**: C端/消费级产品、需要关注用户增长和留存、用户自愿主动使用的产品。

**与UES对比**: HEART强调增长（Adoption/Retention/Engagement），UES强调效率（任务效率）和规范（一致性）。

---

### YOUKU 模型 — 内容行业

**来源**: 优酷设计团队  
**适用**: 内容分发产品（视频/资讯）  
**特点**: 基于OADI个体学习模型（见-解-思-行）

**六个维度**:

| 维度 | 对应OADI | Schema枚举 | 定义 |
|------|----------|-----------|------|
| **吸引性** | 见Observe | `YOUKU-attraction` | 用户愿意点击进入 |
| **易理解性** | 解Assess | `YOUKU-understandability` | 用户能理解内容/功能 |
| **易用性** | 思Design | `YOUKU-usability` | 用户能顺畅操作 |
| **任务完成度** | 行Implement | `YOUKU-task_completion` | 用户完成核心任务 |
| **品牌性** | 扩展 | `YOUKU-brand` | 品牌调性一致性 |
| **创新性** | 扩展 | `YOUKU-innovation` | 设计创新突破 |

**适用场景**: 内容分发产品、需要强调品牌调性的产品。

---

### GSM 推导框架 — 全产品必用

**来源**: Google  
**定义**: Goals-Signals-Metrics，从目标推导到可测量指标的桥梁

**三步推导**:
1. **Goal**: 想达成什么目标（用户层面的目标，而非功能）
2. **Signal**: 什么行为/信号表明目标达成（可观察的用户行为）
3. **Metric**: 如何量化这个信号（具体数字 + 为什么是这个数）

**强制要求**: 每层目标（BG/PG/UG/EG）都必须走GSM推导，不能只写Goal和Metric。

---

### 其他辅助方法论

| 方法论 | 适用场景 | 核心价值 |
|--------|---------|---------|
| **TAM** | 内部工具/新技术产品 | 有用性+易用性决定采纳意愿 |
| **CES** | 复杂流程B端产品 | 发现用户痛点+提升忠诚度 |
| **PSSUQ** | 可用性测试情景 | 快速评估系统/信息/界面质量 |
| **1688五度** | 电商C端 | 全生命周期（吸引→完成→满意→忠诚→推荐） |

---

## source_assets

- 阿里云UES揭秘：https://mp.weixin.qq.com/s/9LJXsdXL54BzyuKcMjo8KA
- 优酷设计质量评估体系：https://www.uisdc.com/youku-design-1
- Google HEART Framework: https://research.google/pubs/pub36299/
- ISO/IEC 9241-11:1998 可用性定义

## do_not_claim

- 不规定具体产品的体验目标值（如"首屏必须<1秒"）。
- 不定义某个产品该选哪个方法论（只提供决策框架）。
- 不包含可用性测试具体流程（属于研究方法，非度量模型）。
