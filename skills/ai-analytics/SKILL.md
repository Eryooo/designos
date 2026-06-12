---
name: ai-analytics
version: 0.1.0
type: pipeline
description: 竞品 / 市场 / 用户分析 → 结构化上游产物。当用户说竞品分析、市场分析、用户画像、设计策略、ai-analytics 时使用。pilot 阶段只稳定产出 prd2proto 最需要的 design_strategy 与 user_persona 两个上游产物。
requires:
  kernel: ">=1.0.0,<2.0.0"
  mcp_servers: []
outputs:
  - id: analysis_report
    type: analysis_report
    format: markdown
  - id: design_strategy
    type: design_strategy
    format: json
  - id: user_persona
    type: user_persona
    format: json
  - id: comparison_matrix
    type: comparison_matrix
    format: markdown
---

# ai-analytics — 分析型上游 skill（pilot baseline）

## 定位（先把这件事说清楚）

ai-analytics 是 **analysis 型上游 skill**：
- ❌ 不是评估 skill（uxeval 才是）：它不产出"问题清单 + 严重度"
- ❌ 不是生成 skill（prd2proto 才是）：它不产出代码 / 原型
- ✅ 它产出"关于竞品 / 市场 / 用户，我们分析出了什么"——结构化、可被下游 skill 消费的上游产物

## pilot scope（本批只解决这一件事）

当前 pilot **只稳定产出 prd2proto 最需要的两个上游产物**：

- `design_strategy`：设计策略（目标人群、气质关键词、设计原则、竞品定位）
- `user_persona`：用户画像（角色、目标、痛点、场景）

archetype 还要求 `analysis_report` / `comparison_matrix` 两个产物，pilot 也会产出，但**当前只作为人读的佐证**，不承诺被下游机器消费。

## 当前稳定产出 vs 暂不纳入 pilot

| 能力 | 状态 |
|---|---|
| design_strategy（JSON 契约） | ✅ pilot 稳定产出，已可被 prd2proto 引用 |
| user_persona（JSON 契约） | ✅ pilot 稳定产出，已可被 prd2proto 引用 |
| analysis_report / comparison_matrix | ⚠️ 产出但仅供人读，不承诺机器消费 |
| 真实竞品自动采集（爬虫 / 截图） | ❌ 不纳入 pilot：data-collection 消费用户提供的资料 |
| PEST/SWOT/KANO/AIPL 全方法论矩阵 | ❌ 不纳入 pilot：只做支撑两个产物所需的最小分析 |
| BI / 图表 / 大盘 | ❌ 不纳入 pilot |

## 实装现状（不假装自动化）

| Stage | 类型 | 实装 |
|---|---|---|
| 1 requirement-understanding | LLM | ✅ 理解分析 brief 与目标范围 |
| 2 data-collection | LLM | ⚠️ 消费**用户提供**的竞品资料，不自动爬取 |
| 3 methodology-selection | LLM | ✅ 按场景选最小够用的方法论 |
| 4 competitor-analysis | LLM | ✅ 在已采集数据上应用方法论 |
| 5 strategy-synthesis | LLM | ✅ 合成 design_strategy + user_persona + 数据完整度评估 |
| 6 report-generation | LLM | ⚠️ LLM 渲染 analysis_report + comparison_matrix（非工具产物） |

pilot 全部 stage 都是 **LLM synthesis**，没有真实数据采集工具。这不是"已完全自动化的分析平台"，而是"结构化、契约化的分析合成"。

## Input Contract

```text
inputs/scope_md            # 必需：分析 brief（目标产品 / 竞品范围 / 想得到什么）
inputs/competitor-data/    # 可选：用户提供的竞品资料（*.md 文本摘要 / 截图说明）
```

缺 `competitor-data/` 时基于 brief + 公开常识分析，但 `data_completeness_assessment` 会标低，QG1 gate 拦在"数据不足"。

## Output Contract（可被下游消费，不是概念接口）

字段结构见 `templates/`：
- `templates/design-strategy.schema.json` → `design_strategy` 字段契约
- `templates/user-persona.schema.json` → `user_persona` 字段契约

产物形态：
- `design_strategy` / `user_persona`：严格 JSON，落 `ai-analytics-out/<run_id>/products/`
- `analysis_report` / `comparison_matrix`：Markdown，落 `ai-analytics-out/<run_id>/reports/`

### prd2proto 如何引用（upstream_refs 对接）

prd2proto/pipeline.yaml 已声明：

```yaml
upstream_refs:
  - skill: ai-analytics
    output_type: design_strategy
    inject_as: design_strategy      # → prd2proto stage1 的 {{design_strategy}}
  - skill: ai-analytics
    output_type: user_persona
    inject_as: existing_personas    # → prd2proto stage1 的 {{existing_personas}}
```

kernel 按 `output_type` 匹配产物 → 按 `inject_as` 注入下游 prompt 变量。
因此本 skill 的 `outputs[].type` 必须**精确等于** `design_strategy` / `user_persona`（已对齐）。

prd2proto stage1 实际消费的关键字段（契约必须提供）：
- `design_strategy.target_audience`、`design_strategy.business_goal`
- `user_persona[].role`、`user_persona[].goals`、`user_persona[].pain_points`

## Output Path Convention

```
ai-analytics-out/<run_id>/
├── products/{design-strategy.json, user-persona.json}
└── reports/{analysis-report.md, comparison-matrix.md}
```

`run_id` 格式：`YYYYMMDD-<slug>`。

## Checkpoint / Gate 行为（沿用 prd2proto 聊天模式纪律）

- C1（data-collection 后）：≤3 行摘要确认竞品范围，默认继续，可打断
- C2（methodology-selection 后）：≤3 行摘要确认方法论，默认继续，可打断
- QG1（strategy-synthesis 上）：**数据完整度不足时硬停**——真实质量门

## 参考

- Constitution: `constitution.md` ｜ Pipeline: `pipeline.yaml` ｜ Schemas: `templates/`
- Pilot 边界与基线：`docs/releases/ai-analytics-baseline/`
