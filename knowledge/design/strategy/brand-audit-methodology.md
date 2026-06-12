# 品牌审计方法论(Brand Audit Methodology)

> Domain: design | Type: methodology | Status: pilot
> DesignOS pilot synthesis(本资产为 pilot 阶段综合判断,非可追溯专业文献)。

## purpose

让品牌审计不是"看着觉得旧了",而是**可量化的品牌健康诊断**:多维度评分、当前 vs 目标
差距、竞品对标、优先级排序的优化建议。它解决的核心问题是:**品牌焕新若不先诊断就重做,
等于用直觉推翻历史资产,可能丢掉已积累的品牌资产**。

## applies_to

- 品牌焕新前的现状诊断(brand-refresh workflow 先行步骤)。
- 独立的品牌健康度评估。
- 产出 brand_audit_report(内部 + 作为 analysis_report 公开)。
- 下游:brand-strategy(基于审计结论重定策略)。

## input_contract

- 必需:existing_brand_materials(现有品牌资料:logo/色彩/物料/传播现状)。
- 可选:competitor_matrix(用于竞品对标维度)。
- 资料不足时:审计报告标 confidence: low,列缺失资料清单。

## decision_framework

### 1. 健康度多维评分(≥5 维)
至少覆盖:
- **一致性**:跨触点视觉/语调是否统一。
- **识别度**:logo/色彩在无品牌名时是否可识别。
- **差异化**:与竞品的区分度。
- **可延展性**:现有系统能否支撑新场景/新产品。
- **可访问性**:色彩对比/字体可读是否达标。
- **可量化判断**:每维给分级(强/中/弱)+ 证据,不是拍脑袋。

### 2. 差距分析(当前 vs 目标)
- 明确每个维度的"当前状态"与"目标状态"。
- 差距 = 目标 − 当前,标注差距大小与影响。
- **冲突取舍**:历史资产价值 vs 焕新需求 —— 高资产价值的元素谨慎更换。

### 3. 竞品对标
- 若有 competitor_matrix,在健康度维度上与竞品对比。
- 找出品牌落后于竞品的维度(优先改)与领先维度(保持)。

### 4. 优化建议与优先级
- 每条建议:可执行 + 优先级(P0/P1/P2)+ 预期影响。
- **优先级排序依据**:差距大小 × 影响范围 × 实施成本。
- P0 = 影响品牌基本可用性(如可访问性不达标)。

## senior_heuristics

- **先诊断后焕新**:不审计就重做,等于丢弃品牌资产。
- **量化优于感觉**:"觉得旧"不是审计结论,"一致性弱:5 个触点 3 种 logo 用法"才是。
- **保护高资产元素**:用户已熟悉的强识别元素,焕新时谨慎动。
- **优先级诚实**:P0 是基本可用性问题,不是"设计师想改的"。
- **资料不足标低置信**:资料不全时明确 confidence: low,不假装诊断完整。

## output_contract

- 产出 brand_audit_report(schema: brand_audit_report.schema.json),含 health_scores
  (≥5 维)/ gap_analysis(current vs target)/ recommendations(action + priority)/
  confidence(high | medium | low)。
- 作为 analysis_report 公开,brand-refresh 中供 brand-strategy 消费。

## quality_rubric

| 维度 | 高阶可评审 | 中阶可用 | 低阶不合格 |
|---|---|---|---|
| 健康度评分 | ≥5 维,每维有分级+证据 | ≥5 维有分级 | <5 维/无证据 |
| 差距分析 | 当前 vs 目标清晰,标差距大小 | 有差距描述 | 仅"觉得旧" |
| 竞品对标 | 健康维度上对标竞品 | 有竞品提及 | 无对标 |
| 优化建议 | 可执行 + 优先级 + 影响 | 有建议 | 笼统建议无优先级 |
| 置信度 | confidence 诚实标注 | 有置信意识 | 资料不足仍称完整 |

**一票否决**:健康度维度 < 5 / 优化建议无优先级 / 资料不足却标 high confidence。

## common_failure_modes

1. **主观诊断**:"看着旧了"无证据。返工信号:health_scores 无证据支撑。
2. **维度不足**:只看 logo 不看一致性/可访问性。返工信号:维度 < 5。
3. **无优先级**:一堆建议不排序。返工信号:recommendations 缺 priority。
4. **丢弃资产**:建议推翻高识别度元素。返工信号:动了用户最熟悉的标识。
5. **置信度造假**:资料严重不足却标 high。返工信号:confidence 与资料量不符。
6. **无目标态**:只说当前差,不说目标是什么。返工信号:gap_analysis 缺 target。

## senior_review_checklist

- [ ] 健康度评分 ≥5 维,每维有分级 + 证据?
- [ ] 差距分析有"当前 vs 目标",标了差距大小?
- [ ] 若有竞品数据,在健康维度上做了对标?
- [ ] 优化建议可执行 + 有优先级(P0/P1/P2)+ 预期影响?
- [ ] 高资产价值元素在建议中被保护?
- [ ] confidence 与实际资料量一致?

## source_assets

- DesignOS pilot synthesis(本资产框架为 pilot 阶段综合判断,无可追溯外部专业文献)。
- 真实关联仓库文件:`skills/brand-creative/contracts/schemas/brand_audit_report.schema.json`(产出结构契约)。
- 此前无现有共享资产覆盖品牌审计(planned → 本批实现)。

## do_not_claim

- 不声称审计已覆盖商业表现/市场份额/财务维度(仅设计与品牌识别维度)。
- 不声称优化建议已经过 ROI 验证。
- confidence 标 low 时,不声称诊断完整。
- 不替代专业品牌咨询的深度调研(用户访谈/市场调研)。
