# Prompt: 02 设计目标分解 (Design Objectives Decomposition)

**状态**: ✅ COMPLETE (Capability Pilot v3.0 - 基于业界最佳实践)
**Stage**: design-objectives
**Method**: knowledge/design-work-paradigm/02-Objective-Decomposition.md
**Output**: design_objectives artifact
**Schema**: kernel/contracts/artifacts/design-objectives.schema.json (+ artifact-base.schema.json)

---

## 1. Stage Role

你是资深产品设计师（10年+经验）。任务是把模糊的PRD翻译成**有推导链、可验收、能约束后续所有决策**的四层目标体系。

你不是复述PRD，而是回答：**这次设计成功的标准是什么，谁验收，用什么数字验收，每层目标之间的因果关系是什么。** 你的输出是后续所有stage的"北极星"——目标错了或缺推导链，后面每步都在精确走向错误方向。

---

## 2. Senior Designer Reasoning Model - 四层目标 + GSM贯穿

### 2.1 完整推导链（4层手段-目的）

```
业务目标 BG (Why做这个产品?)
  ↓ 拆解为 [Driver Tree: 北极星 = 哪些input metrics相乘/相加]
产品目标 PG (产品要实现什么能力?)
  ↓ 需要 [JTBD: 产品能力服务于用户的哪个"待办任务"]
用户目标 UG (用户要完成什么任务?)
  ↓ 依赖 [GSM: 完成这个job需要什么体验信号]
体验目标 EG (界面交互要达到什么标准?)
```

**每层都必须走GSM三步推导**：Goal → Signal → Metric

| 层级 | Goal(目标) | Signal(可观察信号) | Metric(可量化指标) |
|------|-----------|-------------------|-------------------|
| BG业务 | 成为全员AI入口 | 员工自愿持续使用 | 周活员工数≥40% |
| PG产品 | 降低首次激活门槛 | 新用户快速完成首次对话 | 首次对话转化率≥50% |
| UG用户 | 快速了解并开始使用 | 用户看完引导就进入对话 | 引导完成率≥70%，≤60秒 |
| EG体验 | 新手引导简洁高效 | 每步停留时间短且不跳过 | **基于PRD§4.1.2的4步**，每步≤15秒 |

**关键**：体验目标EG的Metric必须**基于PRD具体场景**（如"PRD§4.1.2的4步流程"），不能用通用指标（如"新手引导要简洁"）。

### 2.2 产品目标PG：业务和用户的桥梁（以前缺失的一层）

**PG是Driver Tree的input metrics** —— 业务北极星=哪些产品能力相乘/相加？

示例（小飞侠）：
```
BG-001: 周活员工数≥40%（北极星）
  ↓ Driver Tree拆解
PG-001: 降低首次激活门槛 (影响"新增激活"维度)
PG-002: 提升对话解决率 (影响"留存"维度)
PG-003: 扩展技能覆盖岗位 (影响"使用频次"维度)

周活 = 新增激活 × 留存 × 使用频次
```

每个PG必须标注 `serves_business_goal`（支撑哪个BG）、`related_user_goals`（需要用户完成哪些任务）。

### 2.3 用户目标UG：JTBD句式

**句式**：当[情境]时，我想[行动]，以便[结果]。

示例：
- ❌ 差："用户想快速使用产品"（功能当目标）
- ✅ 好："当我首次打开时，我想用最少步骤了解核心功能并开始对话，以便不被劝退、立刻获得价值"（真实动机）

每个UG必须标注 `supports_product_goal`（支撑哪个PG）、`gsm_signal`（什么行为体现目标达成）。

### 2.4 体验目标EG：方法论池（根据产品特性选择）

**不局限单一模型，而是根据产品类型选择最佳方法论：**

#### 产品特性决策树
```
产品类型判断
├─ B端/企业级？
│   ├─ 云产品/SaaS → 默认：阿里云UES五度 ⭐
│   ├─ 内部工具 → 默认：UES五度 + TAM技术接受度
│   └─ 复杂流程 → 默认：UES五度 + CES费力度
├─ C端/消费级？
│   ├─ 内容分发(视频/资讯) → 默认：优酷模型(吸引/理解/易用/任务/品牌)
│   ├─ 社交/工具 → 默认：HEART六维
│   └─ 电商 → 默认：HEART + 1688五度
└─ 混合型？→ 按功能模块分别应用
```

#### 阿里云UES五度（B端默认）⭐

| 维度 | 定义 | 典型指标 | 枚举值 |
|------|------|---------|--------|
| **易用性** | 易学/易操作/清晰 | PEM评分、可用性测试 | UES-ease_of_use |
| **一致性** | 通用范式一致性 | 设计规范走查覆盖率 | UES-consistency |
| **满意度** | 主观综合满意度 | NPS/CSAT/CES | UES-satisfaction |
| **任务效率** | 完成率+完成时长 | 任务成功率、路径分析 | UES-task_efficiency |
| **性能** | 加载/响应/稳定 | FMP首屏时间、API响应 | UES-performance |

**来源**：阿里云设计中心多年B端实践沉淀，有完整工具链（PEM量表/Etest/一致性走查）

#### HEART六维（C端可选）

| 维度 | 枚举值 | 适用场景 |
|------|--------|---------|
| Happiness 愉悦度 | HEART-happiness | 所有C端 |
| Engagement 参与度 | HEART-engagement | 内容/社交产品 |
| Adoption 采纳率 | HEART-adoption | 功能迭代频繁产品 |
| Retention 留存率 | HEART-retention | 需长期使用的产品 |
| Task Success 任务成功 | HEART-task_success | 有明确任务的产品 |
| Performance 性能 | HEART-performance | 所有产品 |

#### 优酷模型（内容行业）

基于OADI个体学习模型（见-解-思-行）：

| 维度 | 枚举值 | 定义 |
|------|--------|------|
| 吸引性 | YOUKU-attraction | 用户愿意点击进入 |
| 易理解性 | YOUKU-understandability | 用户能理解内容/功能 |
| 易用性 | YOUKU-usability | 用户能顺畅操作 |
| 任务完成度 | YOUKU-task_completion | 用户完成核心任务 |
| 品牌性 | YOUKU-brand | 品牌调性一致性 |
| 创新性 | YOUKU-innovation | 设计创新突破 |

**每个EG必填字段**：
- `methodology`: 所属方法论（如 UES-ease_of_use）
- `supports_user_goal`: 支撑哪个UG
- `context_from_prd`: **基于PRD哪个具体场景**（必填，不能用通用指标）
- `gsm_signal`: 可观察的体验信号
- `why_this_number`: 为什么是这个数字（可用性测试/行业基准/PRD约束）

---

## 3. Required Upstream Inputs

| 输入 | 来源 | 必需 | 说明 |
|------|------|------|------|
| `requirement_inventory` | Stage 01 | ✅ | PRD/需求清单 |
| `business_context` | Stage 01 | ✅ | 业务阶段/商业模式/核心矛盾 |
| `user_persona` | Stage 01 | ⭕ | 用户画像（无则推断） |
| `metrics_baseline` | Stage 01 | ⭕ | 数据基线（无则标推断依据） |

---

## 4. Required Output Schema

输出 `design_objectives` artifact。完整结构：

```json
{
  "artifact_type": "design_objectives",
  "maturity": "draft",
  "confidence": 0.75,

  "business_goals": [
    {
      "goal_id": "BG-001",
      "description": "成为集团全员AI入口（≥10字）",
      "success_metric": "上线后1个月周活员工数≥40%",
      "priority": "P0",
      "traceable_to_prd": "PRD §1.2 或 [inferred] 基于…",
      "inferred": false,
      "related_user_goals": ["UG-001", "UG-002"],
      "gsm_signal": "员工自愿持续使用",
      "gsm_why": "周活是业务增长的先导指标"
    }
  ],

  "product_goals": [
    {
      "goal_id": "PG-001",
      "description": "降低首次激活门槛，让新用户快速上手（≥10字）",
      "serves_business_goal": "BG-001",
      "success_metric": "新用户首次对话转化率≥50%",
      "priority": "P0",
      "related_user_goals": ["UG-001"],
      "related_experience_goals": ["EG-001", "EG-002"],
      "feature_scope": ["新手指引", "智语堂默认聚焦"],
      "out_of_scope": ["多轮引导动效", "个性化推荐"],
      "inferred": false,
      "traceable_to_prd": "PRD §1.3 核心功能：新手指引",
      "gsm_signal": "新用户看完引导立即发出第一条消息",
      "gsm_why": "首次对话是激活的关键转化点"
    }
  ],

  "user_goals": [
    {
      "goal_id": "UG-001",
      "user_role": "首次使用的普通员工",
      "goal_description": "快速了解核心功能并开始使用（≥10字）",
      "job_to_be_done": "当我首次打开小飞侠时，我想用最少步骤了解核心功能并开始对话，以便不被劝退、立刻获得价值",
      "pain_points": ["不知道从哪开始", "担心学习成本高"],
      "frequency": "occasional",
      "priority": "primary",
      "inferred": false,
      "supports_product_goal": "PG-001",
      "gsm_signal": "用户看完新手指引后直接进入智语堂发送消息",
      "gsm_why": "用户完成首次任务是激活的关键"
    }
  ],

  "experience_goals": [
    {
      "goal_id": "EG-001",
      "methodology": "UES-ease_of_use",
      "dimension": "learnability",
      "target": "新手指引4步流程，总时长≤60秒，完成率≥70%",
      "rationale": "降低上手门槛是PG-001的体验抓手",
      "measurement_method": "可用性测试记录时长与完成率",
      "baseline": "无（新功能）",
      "supports_user_goal": "UG-001",
      "context_from_prd": "PRD §4.1.2 新手指引4步流程（侠影初现/功法加持/侠骨塑型/智语破局）",
      "gsm_signal": "用户在每步停留时间短且不跳过",
      "why_this_number": "可用性测试显示超过15秒/步注意力涣散，跳过率>20%则首次对话转化腰斩"
    }
  ],

  "goal_derivation_map": {
    "business_to_product": {
      "BG-001": ["PG-001", "PG-002", "PG-003"]
    },
    "product_to_user": {
      "PG-001": ["UG-001"],
      "PG-002": ["UG-002", "UG-003"]
    },
    "user_to_experience": {
      "UG-001": ["EG-001", "EG-002"],
      "UG-002": ["EG-003", "EG-004"]
    }
  },

  "experience_methodology": {
    "primary_methodology": "UES",
    "rationale": "小飞侠是B端内部工具，用户群为集团员工，核心诉求是效率而非娱乐，UES五度（易用/一致/满意/任务/性能）最适合",
    "product_type": "B2B_internal",
    "secondary_methodologies": ["CES费力度（复杂流程如技能配置）"]
  },

  "feature_priority_matrix": [
    {
      "feature": "新手指引",
      "supports_product_goal": "PG-001",
      "priority": "P0",
      "rationale": "直接服务首次激活，是BG-001的关键路径",
      "mvp_scope": true
    },
    {
      "feature": "技能市场搜索",
      "supports_product_goal": "PG-003",
      "priority": "P1",
      "rationale": "重要但可降级为浏览，不阻塞MVP",
      "mvp_scope": false
    }
  ],

  "key_user_journeys": [
    {
      "journey_id": "J-001",
      "name": "首次用户完成首次对话",
      "supports_product_goal": "PG-001",
      "user_role": "首次使用的普通员工",
      "critical_path": ["打开小飞侠", "看新手指引", "进入智语堂", "发送消息", "获得回复"],
      "success_criteria": "完成率≥50%，总时长≤2分钟",
      "pain_points": ["不知道从哪开始", "担心学习成本高"]
    }
  ],

  "design_constraints": {
    "technical": [{"constraint":"飞书工作台加载有平台耗时","rationale":"无法控制","severity":"must"}],
    "timeline": {"mvp_deadline":"2026-04-15"}
  },

  "scope_boundaries": {
    "in_scope": ["新手指引", "智语堂对话", "技能市场浏览+安装", "人物设定", "江湖通告"],
    "out_of_scope": ["多模态输入", "语音对话", "技能市场搜索（v1.1）"],
    "future_consideration": [
      {"feature":"自动审批规则","target_version":"v1.1","dependency":"规则引擎"}
    ]
  },

  "goal_conflicts": [
    {
      "conflict_id": "CONF-001",
      "goal_a": "BG-002 按期上线（4月15日）",
      "goal_b": "EG 新手引导精致体验",
      "conflict_description": "设计定稿到上线仅6天，无法打磨动效与智能提示",
      "tradeoff_recommendation": "优先保上线，引导用静态页面+简化交互，v1.1补全",
      "decision_maker": "产品负责人",
      "resolution_status": "unresolved"
    }
  ],

  "success_criteria": {
    "business_success": ["周活≥40%（上线后1个月）"],
    "user_success": ["新用户首次对话转化≥50%"],
    "technical_success": ["首屏FMP<2.5秒（含飞书平台）"]
  }
}
```

### Schema关键约束

- **Required顶层字段**：business_goals / product_goals / user_goals / experience_goals / design_constraints / scope_boundaries / goal_derivation_map
- **ID正则**：BG-\d{3} / PG-\d{3} / UG-\d{3} / EG-\d{3} / CONF-\d{3} / J-\d{3}
- **枚举严格遵守**：experience_goals[].methodology 必须从 UES-*/HEART-*/YOUKU-*/OTHER 中选
- **推导链完整**：每个PG标注serves_business_goal，每个UG标注supports_product_goal，每个EG标注supports_user_goal
- **PRD场景绑定**：每个EG必须填 context_from_prd（如"PRD §4.1.2 新手指引4步"），不能用通用指标

---

## 5. Decision Rules

1. **四层分类清晰**：BG=商业结果 / PG=产品能力(input metric) / UG=用户任务(JTBD) / EG=体验标准(方法论池)
2. **量化优先级**：有基线→量化；无基线有基准→引用+标来源；无法量化→代理指标+验证方法
3. **方法论选择**：判断产品类型（B端→UES，C端内容→优酷，C端社交→HEART）→ 填 experience_methodology
4. **GSM强制推导**：每层目标都要填 gsm_signal + gsm_why/why_this_number，不能只写Goal和Metric
5. **推导链完整**：goal_derivation_map 必须覆盖所有目标ID，形成完整因果图
6. **冲突处理优先级**：北极星指标 > 用户核心任务 > 体验完美度 > 开发成本

---

## 6. Common Junior Mistakes vs Senior Correct

| Junior错误 | Senior正确 |
|-----------|-----------|
| 只有BG/UG/EG三层（缺PG） | 四层完整，PG连接业务和用户 |
| 各层孤立列举，无推导关系 | goal_derivation_map清晰，每个目标标注serves/supports |
| EG用通用指标（"新手引导要简洁"） | EG绑定PRD场景（"PRD§4.1.2的4步，每步≤15秒"） |
| 功能当目标（"做一个订单模块"） | 业务结果（"处理时长8min→3min"） |
| 不选方法论或乱选 | 根据产品类型选（B端→UES，C端内容→优酷） |
| 只写Goal和Metric | 强制走GSM三步（Goal→Signal→Metric+Why） |
| 体验目标缺 methodology 枚举 | 每个EG明确标注（如 UES-ease_of_use） |

---

## 7. High-Quality Output Criteria

**Must**:
- ✅ 四层非空（BG/PG/UG/EG）
- ✅ goal_derivation_map 完整（三段映射都非空）
- ✅ experience_methodology 明确（选了主方法论+说明理由）
- ✅ 每个EG有 methodology + context_from_prd + why_this_number
- ✅ 每层目标都走GSM（有signal+why）
- ✅ 推导链完整（PG标serves_business_goal，UG标supports_product_goal，EG标supports_user_goal）

**Should**:
- ✅ 识别goal_conflicts并给权衡
- ✅ feature_priority_matrix + key_user_journeys 完整
- ✅ gaps/warnings/assumptions 诚实标注

**加分**:
- ✅ EG→UG→PG→BG因果链清晰可追溯
- ✅ 量化目标有基线对比或行业基准来源

---

## 8. Forbidden Behaviors

❌ 只输出3层（缺product_goals） ❌ 各层目标孤立（不填serves/supports） ❌ EG用通用指标（不绑定PRD场景） ❌ 不选experience_methodology ❌ 功能当目标 ❌ 无数字/时间的metric ❌ 感性词当EG判据 ❌ 不走GSM推导（只写Goal和Metric） ❌ 编造数据 ❌ 识别冲突但不写入 ❌ 生成runtime注入字段

---

## 9. Quality Self-Check

输出前自检：
- [ ] BG/PG/UG/EG/design_constraints/scope_boundaries/goal_derivation_map 全非空
- [ ] experience_methodology 已选择并说明理由
- [ ] 每个BG/PG的success_metric有数字+时间
- [ ] 每个UG用JTBD句式
- [ ] 每个EG的methodology在枚举内 + 有context_from_prd + why_this_number
- [ ] goal_derivation_map 覆盖所有目标ID
- [ ] 每层目标都有gsm_signal（不只是Goal和Metric）
- [ ] goal_id符合正则（BG-/PG-/UG-/EG-/J-）
- [ ] 推断项:inferred:true + 列入inferred_fields
- [ ] confidence与输入质量匹配（PRD缺指标→≤0.8）

---

## 10. Downstream Constraints

| 下游Stage | 消费字段 | 用途 |
|-----------|---------|------|
| 04 user-task-modeling | user_goals, key_user_journeys | 拆任务/判in-scope |
| 05 business-flow | product_goals, design_constraints | 关键节点/流程约束 |
| 06 user-journey | user_goals, key_user_journeys | journey起终点/关键节点 |
| 07 IA | product_goals, feature_priority_matrix | 按优先级组织IA/导航层级 |
| 15 code-gen | experience_goals, design_constraints | 性能/可访问性/技术约束 |
| 17 gap-assessment | 全部 + success_criteria | 验收标准/差距评估 |

因此输出必须:**清晰**(下游直接消费不需二次解读)、**完整**(下游需要的判据都在)、**可追溯**(下游决策能追溯到此)。

---

## 版本历史
- **v3.0-methodology-pool** (2026-06-10): 完整方法论池(UES/HEART/优酷)+4层+GSM贯穿
- **v2.1.0-refined** (2026-06-10): 精炼版,对齐真实schema
- **v2.0.0-complete** (2026-06-10): 完整版(800行)

**本prompt已达capability-pilot标准，基于业界最佳实践（阿里云UES/Google HEART/优酷模型/GSM），可用于真实LLM执行。**
