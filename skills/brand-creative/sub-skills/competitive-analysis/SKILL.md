---
skill: competitive-analysis
name: Competitive Analysis
version: 0.1.0-pilot
type: pipeline
status: pilot
description: 分析竞品视觉风格/传播策略/市场空白,产出结构化竞品矩阵与市场差距报告
requires:
  kernel: ">=1.0.0,<2.0.0"
outputs:
  - id: competitor_matrix
    type: comparison_matrix
    format: json
    description: 竞品对比矩阵(品牌/视觉/传播/市场)
  - id: comparison_matrix
    type: comparison_matrix
    format: json
    description: competitor_matrix 别名,供下游消费
  - id: market_gap_report
    type: analysis_report
    format: markdown
    description: 市场空白报告(未被竞品覆盖的情感/价值/视觉空间)
---

# competitive-analysis — 竞品分析子技能

> pipeline 型子技能,消费 DesignOS 共享决策库 `knowledge/research/competitor-analysis.md`,产出可追溯的竞品矩阵与市场空白报告。

## 定位与边界

competitive-analysis 是 brand-creative 技能组的**独立起点子技能**,目标:把用户提供的产品/市场信息与竞品线索,转化为结构化的竞品对比矩阵与市场差距分析,为后续 brand-strategy 提供证据基础。

**它能做什么:**
- 从 product_brief / target_market / competitor_hints 产出竞品矩阵
- 至少覆盖 3 个直接竞品,包含视觉风格/传播策略/市场定位维度
- 每条竞品事实区分 observed / inferred / unknown
- 识别至少 1 个未被竞品占据的市场空白(情感/价值/视觉空间)
- 输入不足时输出 status: insufficient_data,不编造事实

**它不能做什么(pilot 边界):**
- ❌ 不自动爬取或验证外部资料;仅消费用户提供的输入
- ❌ 不声称完成深度竞品审计(专利/财务/组织不在范围)
- ❌ 不保证分析结论超过输入资料质量
- ❌ 不预设行业;依赖用户输入的 target_market 范围

## 核心产出

| 产出物 | 类型 | 格式 | 用途 |
|-------|------|------|------|
| competitor_matrix | comparison_matrix | JSON | 竞品对比矩阵,至少 3 个竞品,必含 visual_style 维度 |
| comparison_matrix | comparison_matrix | JSON | competitor_matrix 别名,供 brand-strategy 消费 |
| market_gap_report | analysis_report | Markdown | 市场空白报告,至少 1 个有证据基础的 gap |

## 复用共享决策资产

- `knowledge/research/competitor-analysis.md`(K1 已交付)

## 质量标准

- 竞品矩阵至少覆盖 3 个直接竞品
- 视觉风格维度(色彩/形态/辅助图形)必须填充
- 每个竞品必须有 visual_style 字段(frozen schema 要求)
- market_gap_report 指出至少 1 个未被竞品占据的情感/视觉空间
- 未验证结论必须标注 `[inferred]`
- 输入不足时 status 字段标注 `insufficient_data`

## 下游消费者

- `brand-strategy` 子技能(消费 competitor_matrix 产出差异化判定)

## Fallback 行为

若用户未提供 competitor_hints 且无足够市场信息,产出 competitor_matrix 标注 `status: insufficient_data`,brand-strategy 消费时会标注差异化为 `[inferred]`。
