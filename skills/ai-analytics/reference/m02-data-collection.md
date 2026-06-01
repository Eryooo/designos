# M02 — 数据采集（reference）

约束清单：

- pilot 不自动爬取，只消费 inputs/competitor-data/ 的用户资料
- 每条 collected_data 必须有 id + competitor + dimension + fact + source
- 每条 fact 必须可追溯到一个 data_sources 条目
- 资料缺失维度如实留空，不得编造（宪法规则 1）
- C1 摘要：竞品数 / 维度数 / 明显缺口
