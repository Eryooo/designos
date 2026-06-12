# PRD 理解（PRD Understanding）

> 通用资产 · `product.prd-understanding` · status: pilot

## purpose

把非结构化需求材料理解为可下游消费的产品结构：业务目标、模块、关键功能、页面、用户流与风险提示。核心不是替产品经理补需求，而是把已有需求边界结构化，并明确哪些内容是推断。

## applies_to

- 从 PRD / brief / scope 文档拆解产品结构的场景。
- 需要把需求交给信息架构、组件设计、代码生成或评估任务消费的场景。

## decision_framework

1. 抽一句话 `business_goal`，作为所有拆解的上位约束。
2. 拆 `modules`，数量控制在 1–15，模块名用名词短语。
3. 拆 `key_features`，每条包含用户价值和可验证 acceptance。
4. 拆 `pages`，一 URL 一 page，页面类型稳定枚举。
5. 拆 `user_flows`，必须是人类 actor 的端到端动作链，至少一条 critical path。
6. PRD 没写但合理推断的内容全部标 `[inferred]`，缺失但不应补的写 warnings。

## senior_heuristics

- 漏标 `[inferred]` 比误标更糟，因为它会把推断伪装成需求。
- 章节标题不等于 module，"非功能需求"通常应进 warnings 或约束。
- page 与 feature 分清：页面承载，feature 表达用户动作。
- user_flow 必须有人类角色，系统批处理不是用户流。

## quality_rubric

| 分级 | 信号 |
|---|---|
| 优 | 结构可直接被 IA/组件/评审消费，推断与缺口清晰 |
| 中 | 主结构可用，但部分 acceptance 或 flow 不够可验证 |
| 差 | 替 PM 发明需求，或把章节标题机械转 module |

## common_failure_modes

- 替产品经理加功能。
- 把业务流/系统流程当 user_flow。
- 页面过度拆分，把 filter/tab 当独立 URL。
- 关键路径缺失，后续无法校验覆盖。

## source_assets

- `skills/prd2proto/reference/m01-prd-understanding.md`
- `skills/prd2proto/reference/textbook/story-mapping.md`

## do_not_claim

- 不替代需求评审。
- 不保证推断需求真实成立。
- 不规定消费方的输出 schema 字段名。
