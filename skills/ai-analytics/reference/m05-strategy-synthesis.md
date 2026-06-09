# M05 — 策略合成（reference）

约束清单（pilot 核心 stage）：

- 输出三个 key：design_strategy / user_persona / data_completeness_assessment
- design_strategy 必须符合 templates/design-strategy.schema.json，且
  target_audience / business_goal 非空（prd2proto 注入必需）
- user_persona 必须符合 templates/user-persona.schema.json，是数组，每项
  role / goals / pain_points 非空（prd2proto 注入必需）
- data_completeness_assessment 含 coverage(0-1) / gaps / summary
- coverage < 0.70 触发 QG1 硬停；不得虚高（宪法规则 3）
- 每条策略/痛点尽量挂 evidence_refs（宪法规则 1）
