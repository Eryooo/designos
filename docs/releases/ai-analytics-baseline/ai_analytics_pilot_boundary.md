# ai-analytics Pilot Boundary（试点边界说明）

> 版本：A1 Pilot Baseline ｜ 日期：2026-06-01 ｜ 适用：内部试点
> 定位：analysis 型**上游** skill。产出"关于竞品/市场/用户分析出了什么"，
> 供 prd2proto 等下游 skill 通过 upstream_refs 引用。不是评估 skill，不是生成 skill。

本文件回答一个问题：**ai-analytics 现在能信到哪、不能信到哪。**

## 1. 当前适合哪些场景

- 已有 PRD / 分析 brief，想为下游 prd2proto 补一份结构化的 `design_strategy` + `user_persona`，替代"PRD 内部脑补画像"。
- 手上有竞品资料（URL 摘要 / 截图说明 / 公开文档文本），放进 `inputs/competitor-data/` 供分析消费。
- 需要一份可追溯（每条结论挂 evidence_refs）、且数据不足会被 gate 拦住的分析合成，而不是自由发挥的散文。

## 2. 当前不适合哪些场景

- 要真实自动爬取竞品（爬虫 / 截图抓取）：pilot 不做，data-collection 只消费用户提供的资料。
- 要全套 PEST / SWOT / KANO / AIPL 方法论矩阵：pilot 只做支撑两个核心产物所需的最小分析。
- 要 BI、图表、数据大盘：不在 pilot。
- 要问题清单 + 严重度（那是 uxeval / evaluation 职责）或代码 / 原型（那是 prd2proto / generation 职责）：宪法规则 4 禁止越界。

## 3. design_strategy / user_persona 的可信边界

**已可信（pilot 稳定产出，已可被 prd2proto 机器消费）：**
- `design_strategy`：JSON 契约，必含 `target_audience` / `business_goal` / `design_principles` / `tone_keywords`。prd2proto stage1 读 `target_audience`、`business_goal` 校准 business_goal。
- `user_persona`：JSON 数组契约，每项必含 `role` / `goals` / `pain_points`。prd2proto stage1 用它校准 user_flows。
- 字段 schema 见 `skills/ai-analytics/templates/*.schema.json`，测试锁死下游必需字段非空。

**可信的前提（不满足则不可信）：**
- 依赖输入数据质量：`coverage < 0.70` 时 QG1 gate 硬停，不在数据不足时硬合成策略。
- 全部为 LLM synthesis，无真实采集工具。结论可信度 = 用户提供资料的质量 + LLM 合成质量，不是"自动化保证"。
- 与 PRD 冲突时：prd2proto 侧已约定**以 PRD 为准**，本 skill 产物是校准参考，不是最终事实。

## 4. analysis_report / comparison_matrix 为什么只作为人读佐证

- 这两个产物没有被任何下游 skill 的 upstream_refs 声明引用——没有机器消费方。
- 它们是叙述性 Markdown，结构不像 design_strategy/user_persona 那样有严格 JSON schema 约束，机器解析不稳定。
- pilot 阶段把"机器契约"和"人读佐证"显式分开：契约产物收窄到两个、做严，佐证产物不做过度承诺。这是诚实，不是偷工。

## 5. 当前验证命令和结果

见 `ai_analytics_validation_baseline.md`。摘要：archetype validate 9 维全过 / ai-analytics 7 测试绿 / prd2proto 73 回归绿。

## 6. release blocker 是否为 0

**是 0。** 判据：
- analysis archetype validate 全过（结构、契约、gate、宪法齐备）。
- 7 个 pilot 契约测试绿，含"output_type 与 prd2proto upstream_refs 精确对齐"。
- 未改任何现有文件，prd2proto 回归无损。

pilot 的"不是真自动化""佐证产物不机器消费"是**已声明的设计边界**，不是 blocker。
