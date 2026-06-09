# 严重等级 Rubric（Severity Rubric）

> 通用资产 · `ux.severity-rubric` · status: pilot
> 体验问题严重等级的判定标尺。它把"拍脑袋定级"改为按用户影响、频次、风险、
> 可恢复性判断。

## purpose

统一 critical / major / minor / suggestion 的判定口径,让不同评估者对同类问题给出接近的等级,并能解释扣分理由。

## applies_to

- 体验问题清单的 severity 字段。
- 评估报告中的优先级排序与修复建议分层。

## decision_framework

核心判定表:

| 用户影响 | 频次 | 等级 |
|---|---|---|
| 无法完成核心任务 | 任意 | critical |
| 数据/资金/合规风险 | 任意 | critical |
| 显著阻碍效率(多步绕过、等待 >10s) | 高频 | major |
| 显著阻碍效率 | 低频 | minor |
| 体验不佳但可完成 | 任意 | minor |
| 不影响行为的优化 | 任意 | suggestion |

边界判定:
- critical vs major:是否阻断/是否不可恢复/是否涉及重大风险。
- major vs minor:是否显著阻碍核心任务效率,且是否高频。
- minor vs suggestion:是否有可观察的体验损害。

## senior_heuristics

- critical 不是"我觉得严重",而是任务失败、不可恢复或重大风险。
- 高频低损害问题可上调;低频可绕过问题可下调。
- 全部都是 critical → 可能标过严;一个 critical 都没有 → 可能没测关键路径。
- 严重等级必须跟 user_impact 对齐,不能跟视觉喜好对齐。

## quality_rubric

| 分级 | 信号 |
|---|---|
| 优 | 每条等级都能从用户影响 + 频次 + 风险解释,critical/major 边界清楚 |
| 中 | 大部分有解释,少量靠直觉 |
| 差 | 用"丑/不舒服/建议优化"等主观词定级 |

## common_failure_modes

- **视觉偏好上纲上线**:把审美建议标成 major。
- **功能缺失混入体验问题**:把"功能没做"当体验 issue。
- **频次缺失**:不知道问题是否高频,仍直接上 major。
- **未区分可恢复性**:可撤销误操作与不可逆误操作同级。

## source_assets

- `skills/uxeval/reference/m06-问题归因.md`(严重等级决策表与 critical/major/minor/suggestion 标准)
- `skills/uxeval/reference/m02-启发式原则.md`(各原则的严重等级映射)

## do_not_claim

- 不定义产品级优先级路线图。
- 不替代真实用户数据;频次不足时需标推断。
- 不规定扣分公式,只给等级判定口径。
