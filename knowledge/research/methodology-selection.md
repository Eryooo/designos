# 方法论选择（Methodology Selection）

> 通用资产 · `research.methodology-selection` · status: pilot

## purpose

按分析目标与证据条件选择最小够用的方法论,避免为了显得专业而堆 SWOT/PEST/KANO/JTBD/AIPL。

## applies_to

- 竞品/市场/用户分析。
- 需要把分析方法映射到设计策略与用户画像的场景。

## decision_framework

1. 明确 objective / deliverables / questions。
2. 列可用证据与缺口。
3. 只选能支撑目标产物的方法论。
4. 每个方法论登记 name / why / applies_to。
5. 数据不足以支撑的方法论不硬选。

方法论边界:
- SWOT:综合判断优势/劣势/机会/威胁。
- PEST:宏观环境。
- KANO:需求优先级,需用户反馈支撑。
- JTBD:用户任务与替代方案。
- AIPL:消费链路与营销转化。

## senior_heuristics

- 方法论是手段,不是产出本身。
- 没有数据支撑的 KANO 比不用 KANO 更危险。
- 每个方法论必须能解释它服务哪个结论。
- 少而准优于多而空。

## quality_rubric

| 分级 | 信号 |
|---|---|
| 优 | 方法论与问题/证据/产物一一对应,缺口明确 |
| 中 | 方法论基本合理,但 why 或 applies_to 偏弱 |
| 差 | 堆方法论名词,没有证据支撑 |

## common_failure_modes

- 为了完整性硬选 PEST/SWOT/KANO 全套。
- 没有用户反馈却输出 KANO 结论。
- 方法论选择与最终 design_strategy 无关。
- 数据缺口未标,导致结论虚高。

## source_assets

- `skills/ai-analytics/reference/m03-methodology-selection.md`
- `skills/ai-analytics/reference/m01-requirement-understanding.md`

## do_not_claim

- 不规定某 skill 的选择算法。
- 不保证选中方法论即可得到真实结论。
- 不替代数据质量审查。
