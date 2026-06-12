# 代码质量宪法（Code Quality Constitution）

> 通用资产 · `frontend.code-quality-constitution` · status: pilot

## purpose

把原型/前端代码的质量底线前置成可审查宪法:不硬编码、不自写基础组件、状态覆盖、design-spec 优先。

## applies_to

- 生成式前端代码。
- 设计稿/规范到代码的 review gate。

## decision_framework

四条核心规则:
1. **无硬编码**:视觉值来自 token/theme,组件内不写死品牌色/字号/间距。
2. **不自写基础组件**:Button/Input/Select 等基础控件来自组件库。
3. **状态覆盖**:交互组件覆盖声明状态。
4. **设计规范优先**:明确 spec 高于组件库默认值。

审查原则:
- location 必须可定位。
- 不确定项写人工确认段,不进 violations。
- required_actions 控制在少数关键项。

## senior_heuristics

- 宁可少报不要误报,误报会毁掉开发信任。
- 编译失败/崩溃/密钥暴露是 critical,不与样式问题同级。
- pm 低保真可放宽,高保真/生产模式必须严查。
- 代码质量审查不等于 lint/性能/测试覆盖率审查。

## quality_rubric

| 分级 | 信号 |
|---|---|
| 优 | 四条规则可定位扫描,违规有修复建议与严重等级 |
| 中 | 能发现主要违规,但位置或建议不够具体 |
| 差 | 泛泛评价代码风格,没有宪法级约束 |

## common_failure_modes

- theme 之外散落 hex。
- 自写基础 Button/Input。
- 状态声明了但代码没实现。
- 低保真规则套到高保真导致漏查。

## source_assets

- `skills/prd2proto/reference/m05-code-generation.md`
- `skills/prd2proto/reference/m06-review-gate.md`
- `skills/prd2proto/constitution.md`

## do_not_claim

- 不定义 ESLint/Prettier/CI 配置。
- 不保证代码生产可上线。
- 不覆盖性能、安全、测试覆盖率的全部审查。
