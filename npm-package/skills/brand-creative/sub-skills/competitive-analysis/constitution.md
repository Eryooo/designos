# competitive-analysis — Constitution

> 本文件是 competitive-analysis 子技能的核心约束,所有 stage prompt 必须遵守。

## 核心原则

1. **证据可追溯**:每条竞品事实必须区分 observed / inferred / unknown。
2. **不编造事实**:输入不足时输出 `status: insufficient_data`,不假装自动爬取。
3. **维度完整性**:competitor_matrix 至少覆盖品牌/定位/目标用户/视觉/传播/差异点。
4. **市场空白证据**:market_gap_report 至少包含一个有证据基础的市场空白;证据不足则明确 gap。

## Schema 强制约束(B1.0 frozen contract)

### competitor_matrix

- `competitors`: array, minItems: 3
- 每个竞品必须包含:
  - `name`: string(required)
  - `visual_style`: string(required) — 至少描述色彩/形态/辅助图形
  - `communication`: string(optional) — 传播策略与语调
  - `market_position`: string(optional) — 市场定位与目标用户
- `status`: enum ["complete", "insufficient_data"]

### market_gap_report

- `gaps`: array, minItems: 1
- 每个 gap 必须包含:
  - `dimension`: string(required) — 维度(情感/价值/视觉/传播)
  - `description`: string(required) — 描述,含证据引用或明确标注证据不足

## 事实分级规则

### observed(已观察)
- 用户在 product_brief / competitor_hints 中直接提供的竞品资料
- 用户明确描述的竞品特点(如"竞品 A 主色调是蓝色")
- **标注方式**:不标注,直接作为事实使用

### inferred(推断)
- 从用户提供的部分信息推导的结论
- 基于 target_market 的行业常识推断
- **标注方式**:在描述中追加 `[inferred]`,如"竞品 B 可能使用年轻化语调 [inferred]"

### unknown(未知)
- 用户未提供且无法合理推断的信息
- **标注方式**:不写入 competitor_matrix;在 market_gap_report 中标注 "insufficient_data on [dimension]"

## 维度覆盖要求

competitor_matrix 每个竞品至少覆盖:

1. **品牌名称**(name, required)
2. **视觉风格**(visual_style, required):
   - 主色调(色彩)
   - 核心形态(几何/有机/写实/抽象)
   - 辅助图形或视觉元素
   - 示例:`"主色调为科技蓝#0052CC,几何简洁风格,线性图标作为辅助元素"`
3. **传播策略**(communication, optional):
   - 语调(专业/亲和/年轻化/高端)
   - 核心传播渠道
   - 示例:`"专业理性语调,重视技术博客与开发者社区传播"`
4. **市场定位**(market_position, optional):
   - 目标用户群
   - 价格区间/市场细分
   - 示例:`"面向中小企业,SaaS 订阅模式,月费 $49-199"`

## market_gap_report 要求

至少包含 1 个 gap,每个 gap 包含:
- **dimension**(维度):情感/价值/视觉/传播之一
- **description**(描述):
  - 有证据:描述竞品共同覆盖的空间 + 未覆盖的空间 + 证据引用
  - 证据不足:明确标注 `insufficient data on [specific aspect], gap identification requires [needed info]`

示例(有证据):
```yaml
dimension: visual
description: |
  竞品 A/B/C 均采用科技蓝+几何简洁风格,未见暖色调或有机形态。
  市场空白:亲和温暖的视觉语言,可用橙/黄暖色+圆润形态切入。
  证据:product_brief 提到"家庭场景",竞品均为 B2B 冷色调。
```

示例(证据不足):
```yaml
dimension: communication
description: |
  insufficient data on competitor communication channels.
  gap identification requires: competitor_hints 包含传播策略或渠道资料。
```

## 输出状态控制

- **status: complete**:至少 3 个竞品,visual_style 全部填充,market_gap_report 至少 1 个有证据 gap
- **status: insufficient_data**:
  - competitor_hints 为空或不足 3 个竞品
  - 或 visual_style 无法填充(用户未提供视觉资料)
  - 此时 competitor_matrix 仍需输出已有竞品(可少于 3 个),但标注 status

## 禁止行为

- ❌ 不假装自动爬取竞品官网/社交媒体
- ❌ 不声称"已验证"未在用户输入中出现的事实
- ❌ 不把推断结论当作 observed 事实使用
- ❌ 不在证据不足时编造 market_gap_report 的具体空白
- ❌ 不把项目/产品/行业专属词写入 constitution(通用决策在 knowledge/)
