# Product Archetypes — 规则层

> **定位**：本目录定义产品类型识别规则与各 archetype 的抽象判断维度。
> 用于 `prd2proto` pipeline 的 stage 03 (product-archetype) 识别 + 后续 stage 按类型应用规则。
>
> **核心原则**：
> - 本文件**仅放规则**，不放任何业务叙事案例（不论真实或合成）。
> - 公开仓库不含真实项目证据（参见 `docs/EVIDENCE-GOVERNANCE.md` 与
>   `scripts/security/scan-sensitive.sh`）。

---

## 1. 九类 Product Archetype

| ID | Archetype | 核心定义 |
|----|-----------|---------|
| `b2b-enterprise-workflow` | B2B 企业流程 | 多角色协作完成业务流程的工作系统（含审批/审计/权限） |
| `b2c-consumer-product` | C 端消费产品 | 单一用户完成自我目标，强调获客/留存/动机 |
| `b2b2c-platform` | 双边/多边平台 | 至少两类角色（供给方+消费方+平台运营方）通过平台撮合 |
| `brand-identity-brief` | 品牌识别 brief | 输入是品牌策略/视觉/识别资产请求，**不是产品功能** |
| `internal-tool` | 内部工具 | 特定团队内部使用，用户被指派使用，非自愿采纳 |
| `ai-agent-product` | AI Agent 产品 | 核心交互是与 AI 对话/任务委派，含 thinking/streaming/中断态 |
| `data-dashboard` | 数据看板 | 数据展示+下钻+决策辅助，强调 KPI/筛选/可视化 |
| `content-community-product` | 内容/社区产品 | 内容消费+UGC+社交关系，强调推荐/参与/创作激励 |
| `hybrid-ambiguous` | 混合/模糊 | 包含上述 ≥2 类特征，或输入证据不足以唯一归类 |

---

## 2. 选择决策树

```
输入：requirement_inventory
  │
  ├─ 是品牌策略/识别/视觉资产请求？
  │    └─ 是 → brand-identity-brief
  │       │
  │       └─ 同时要求落地 web/活动页/品牌展示页？
  │            ├─ 是 → secondary: b2c-consumer-product / b2b-enterprise-workflow
  │            │      （pri: brand, sec: 体验承载类型）
  │            └─ 否 → handoff: brand-creative skill
  │
  ├─ 核心交互是 AI 对话/Agent 任务委派？
  │    └─ 是 → ai-agent-product（可与 b2b/b2c 叠加）
  │
  ├─ 数据展示+决策辅助为主，无复杂业务流程？
  │    └─ 是 → data-dashboard
  │
  ├─ 内容消费+UGC+社交关系？
  │    └─ 是 → content-community-product
  │
  ├─ 至少两类角色通过平台撮合（供给+消费+平台）？
  │    └─ 是 → b2b2c-platform
  │
  ├─ 单一企业内部多角色完成业务流程？
  │    ├─ 团队内部强制使用？→ internal-tool
  │    └─ 跨企业服务？→ b2b-enterprise-workflow
  │
  ├─ 单一用户、自愿使用、强调获客/留存？
  │    └─ 是 → b2c-consumer-product
  │
  └─ 证据不足或多类特征明显 → hybrid-ambiguous（必须列出 ambiguity_gaps）
```

---

## 3. 各 Archetype 的判断维度（抽象）

> 每个 archetype 后续应有独立 `<id>.md` 详述。本表为概览。

### 3.1 b2b-enterprise-workflow
- **核心维度**：效率、角色、权限、流程、状态、协作、审计、信息密度、异常处理、业务闭环
- **目标层优先级**：
  - BG: 降本/提效/流程规范/风险控制
  - PG: 任务闭环/流程透明/权限准确/数据可追踪
  - UG: 快速完成工作/减少沟通/降低错误
  - EG: 少跳转/少重复录入/状态清晰/异常可恢复
- **反模式**：套 C 端"激活/留存/动机"逻辑

### 3.2 b2c-consumer-product
- **核心维度**：获客、激活、留存、转化、情绪、信任、动机、内容消费、个性化、增长路径
- **目标层优先级**：
  - BG: 增长/转化/留存/收入/传播
  - PG: 降低首次使用门槛/提升核心行为频次/增强粘性
  - UG: 快速获得价值/被吸引/被理解/愿意持续使用
  - EG: 低认知成本/强反馈/情绪愉悦/路径短/动机强化
- **反模式**：套 B 端"权限/流程/审批/审计"逻辑

### 3.3 b2b2c-platform
- **核心维度**：多角色、双边价值、供需匹配、角色切换、信任机制、治理机制、增长与履约并存、前台体验+后台运营
- **目标拆解必须三层**：
  - C 端用户目标：发现/理解/购买/使用/持续参与
  - B 端用户目标：管理/发布/履约/运营/分析
  - 平台目标：撮合效率/供需平衡/信任治理/生态增长
  - EG: 前台低门槛/后台高效率/跨角色状态一致
- **反模式**：只用单边视角（B 或 C）拆目标

### 3.4 brand-identity-brief
- **核心维度**：定位、受众、心智、差异化、品牌人格、视觉母题、识别资产、传播场景、应用规范、一致性
- **目标层优先级**：
  - BG: 建立认知/提升信任/形成差异化/支撑传播
  - 品牌目标: 明确定位/统一识别/建立风格资产
  - UG: 快速理解品牌是谁/提供什么价值/为什么可信
  - EG: 可识别/可记忆/可延展/可落地
- **routing**：纯品牌 brief → handoff `brand-creative` skill；含 web/页面落地需求 → 在 prd2proto 继续但仅处理体验层
- **反模式**：硬生成产品页面流，替代品牌策略

### 3.5 internal-tool
- **核心维度**：被指派使用、非自愿采纳、效率优先、培训成本控制、与现有工作流集成、最小化打扰
- **目标层优先级**：
  - BG: 团队效率/数据合规/工作标准化
  - PG: 与既有流程无缝集成/低培训成本/可被审计
  - UG: 快速完成被指派的任务/不干扰主工作
  - EG: 与既有工具一致/最小学习/可关闭打扰
- **反模式**：套 C 端"促活留存"或 B2B 商业化逻辑

### 3.6 ai-agent-product
- **核心维度**：对话/任务委派为主、AI 执行态（thinking/streaming/中断/失败）、上下文管理、可信度、可纠错、用户与 AI 的边界
- **目标层优先级**：
  - BG: 提升 AI 任务完成率/用户对 AI 的信任/单 session 价值
  - PG: 准确响应/可中断重来/上下文保持/失败可恢复
  - UG: 快速获得有用结果/能纠正 AI/不被 AI 误导
  - EG: 流式反馈/思考过程透明/失败可重试/中断保留上下文
- **可与其他 archetype 叠加**（例：b2b + ai-agent / b2c + ai-agent）
- **反模式**：把 AI 当普通表单/隐藏 AI 不确定性

### 3.7 data-dashboard
- **核心维度**：KPI 优先、下钻路径、筛选/对比、可视化清晰度、数据时效、决策支持
- **目标层优先级**：
  - BG: 决策效率/数据驱动文化/异常发现
  - PG: KPI 准确/下钻顺畅/筛选灵活/对比直观
  - UG: 快速看懂当前状态/找到异常/支撑决策
  - EG: 视觉清晰/默认聚焦关键指标/响应快/可对比
- **反模式**：套 b2c 增长逻辑或 ai-agent 对话逻辑

### 3.8 content-community-product
- **核心维度**：内容消费、UGC 创作、社交关系、推荐机制、参与激励、社区氛围、举报治理
- **目标层优先级**：
  - BG: 内容生产量/消费时长/社区健康/创作者留存
  - PG: 内容供给/推荐准确/参与门槛/治理有效
  - UG: 快速发现感兴趣内容/愿意创作/感受社区氛围
  - EG: 沉浸/低互动门槛/反馈即时/创作激励可见
- **反模式**：套 b2b 流程逻辑或单纯电商交易逻辑

### 3.9 hybrid-ambiguous
- **触发条件**：
  - 输入同时包含 ≥2 类 archetype 的核心维度
  - 或证据不足以唯一归类
- **必须输出**：
  - `secondary_archetypes` 列出所有候选
  - `ambiguity_gaps` 列出导致模糊的具体证据缺失
  - `archetype_confidence` < 0.7
  - 建议补充输入或标记 `human_review_required: true`
- **反模式**：默认套 b2b 或 b2c 之一

---

## 4. Archetype 之间的叠加规则

某些 archetype 可作为 **modifier** 叠加于 primary：
- `ai-agent-product` 常作为 modifier 叠加于 b2b / b2c / b2b2c
- `internal-tool` 是 b2b 的子类（可视为 b2b 的 internal 变体）

**合法叠加**示例：
- primary: `b2b-enterprise-workflow`, secondary: `ai-agent-product`
- primary: `b2c-consumer-product`, secondary: `content-community-product`

**禁止叠加**示例：
- `brand-identity-brief` + `data-dashboard`（性质相反）

---

## 5. 03-product-archetype 必须输出的稳定字段

stage 03 必须产出以下字段（供下游 stage 04~17 消费）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `primary_archetype` | enum (§1) | 唯一主类型 |
| `secondary_archetypes` | list of enum | 0~N 个 modifier/次类型 |
| `archetype_confidence` | 0.0~1.0 | 整体识别置信度 |
| `routing_decision` | enum | `proceed` / `handoff` / `human_review` |
| `handoff_recommendation` | string \| null | 如 `handoff` → 目标 skill 名 |
| `downstream_rule_sets` | list | 后续 stage 应用的规则集 ID 引用 |
| `archetype_specific_priorities` | object | 各 archetype 的目标层优先级（引自 §3） |
| `archetype_specific_risks` | list | 该 archetype 易踩的风险/反模式 |
| `ambiguity_gaps` | list | 模糊点（hybrid-ambiguous 必填） |
| `do_not_apply_patterns` | list | 明确不应套用的其他 archetype 逻辑 |

---

## 6. Routing & Handoff 规则

| 输入特征 | routing_decision | handoff_recommendation |
|---------|------------------|----------------------|
| 纯品牌策略/视觉/识别 brief | `handoff` | `brand-creative` |
| 品牌 brief + 明确 web/活动页/展示页落地 | `proceed` | null（在 prd2proto 内处理体验层）|
| 输入证据不足 + archetype 不明 | `human_review` | null（标记 `human_review_required`） |
| 任何明确的 b2b/b2c/b2b2c/internal/ai-agent/dashboard/content | `proceed` | null |

---

## 7. 后续应补全的 archetype-specific 文件

本 README 是轻量规则层。完整 archetype-specific 规则应分别落入：
- `b2b-enterprise-workflow.md`
- `b2c-consumer-product.md`
- `b2b2c-platform.md`
- `brand-identity-brief.md`
- `internal-tool.md`
- `ai-agent-product.md`
- `data-dashboard.md`
- `content-community-product.md`
- `hybrid-ambiguous.md`

每个文件应包含：
- 完整的核心维度展开
- BG/PG/UG/EG 拆解优先级
- 反模式
- 与其他 archetype 的混合判断
- 不放业务案例（业务案例属 `eval/golden-cases/`）

---

## 8. 防污染检查清单

任何新增/修改本目录文件前必须验证：

- [ ] 不含具体公司/产品/IP/学校/品牌名
- [ ] 不含项目专属域名术语
- [ ] 不含具体业务路径（如"打开 X → 进入 Y"）
- [ ] 不含具体业务指标样例（如"周活 ≥ 40%"）
- [ ] 教学说明使用 `<placeholder>` 而非业务叙事
- [ ] 通过 `bash scripts/security/scan-sensitive.sh --file <path>` 0 命中

---

## 9. Do-Not-Apply Matrix（跨 archetype 互斥逻辑）

stage 03 输出 `do_not_apply_patterns` 时引用本矩阵。每个 archetype 明确
**不应套用**哪些其他 archetype 的判断逻辑：

| 当前 archetype | 不应套用的逻辑 | 原因 |
|---------------|--------------|------|
| `b2b-enterprise-workflow` | b2c 的"激活/留存/动机/增长漏斗" | 用户非自愿使用，增长指标误导 |
| `internal-tool` | b2c 促活留存；b2b 商业化/定价 | 被指派使用，无采纳漏斗与付费转化 |
| `b2c-consumer-product` | b2b 的"权限/审批/审计/流程合规" | 单用户自我目标，无组织流程 |
| `b2b2c-platform` | 任何单边视角（只 b2b 或只 b2c） | 必须三角色（供给/消费/平台）同时建模 |
| `brand-identity-brief` | prd2proto 页面流生成；data-dashboard 指标逻辑 | 品牌策略 ≠ 产品功能，应 handoff |
| `ai-agent-product` | 把 AI 当普通表单/CRUD；隐藏不确定性 | 必须建模 thinking/streaming/中断/失败态 |
| `data-dashboard` | b2c 增长逻辑；ai-agent 对话逻辑 | 决策支持工具，核心是 KPI 与下钻 |
| `content-community-product` | b2b 流程审批；纯电商交易闭环 | 核心是内容消费/UGC/社区关系 |
| `hybrid-ambiguous` | 默认套 b2b 或 b2c 之一 | 必须列 ambiguity_gaps，不得静默默认 |

**使用规则**：
- stage 03 必须为 `primary_archetype` 至少列出本矩阵对应行的 1~2 条
  `do_not_apply_patterns`。
- 下游 stage 04~17 读取该字段，主动抑制错误 archetype 的推理路径。

---

**Version**: S0-v1.0（2026-06-12 - Batch S0 重构后初版）
**Status**: 轻量规则层（9 类 archetype + 决策树 + routing + 字段契约 + do-not-apply 矩阵）
**Next**: 9 个 archetype-specific 文件由后续批次补全
