# ai-analytics 分析宪法

analysis 型 skill 的 4 条硬约束。strategy-synthesis 与 report-generation 必须满足。

---

## 规则 1：不得编造数据

所有分析结论必须可追溯到 `collected_data` 中的具体来源条目。
- 推断的内容必须显式标 `[inferred]` 并说明依据。
- 没有数据支撑的结论返回 `null` 或写入 `data_completeness_assessment.gaps`，不得瞎编。

**违规示例**：竞品资料里没提价格，却在 comparison_matrix 写"竞品 A 定价 ¥99/月"。

---

## 规则 2：产物必须符合 output schema

`design_strategy` / `user_persona` 必须严格符合 `templates/*.schema.json`：
- 字段名、层级、必填项不得缺。
- prd2proto 实际消费的字段（`design_strategy.target_audience` / `.business_goal`，
  `user_persona[].role` / `.goals` / `.pain_points`）**必须非空**，否则下游注入失效。

这条是 pilot 的核心：output 是契约，不是散文。

---

## 规则 3：数据完整度必须诚实评估

`strategy-synthesis` 必须输出 `data_completeness_assessment`：
- `coverage`（0-1）：已采集数据对 brief 需求的覆盖率
- `gaps`：缺哪些关键数据
- `summary`：一句话结论

`coverage < 0.70` 触发 QG1 gate 硬停。**不得为了出产物而虚高 coverage。**

---

## 规则 4：不得越界产出下游职责

ai-analytics 只产出分析与上游策略，不得：
- 产出问题清单 + 严重度（那是 uxeval / evaluation 的职责）
- 产出代码 / 原型 / 设计稿（那是 prd2proto / generation 的职责）

越界内容应转化为 `design_strategy` 里的约束建议，由下游 skill 决定如何落地。

---

## 严重等级

| 等级 | 触发条件 |
|---|---|
| critical | 规则 1 编造关键数据；规则 2 下游必需字段缺失 |
| major | 规则 3 coverage 虚高（实际 < 0.70 标成 ≥ 0.70）；规则 4 越界产代码/问题清单 |
| minor | 规则 1 个别 [inferred] 未标注 |
