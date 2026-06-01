# Reference: 代码审查（m06 checklist）

> Stage 06 `review-gate` 约束清单。宪法定义见 `../constitution.md`，动机见 `textbook/code-constitution-rationale.md`。

## 输出 schema 强约束

```json
{
  "constitution_violations": [
    {"rule_id":1,"severity":"critical|major|minor","location":"file:line",
     "description":"...","fix_suggestion":"...","auto_fixable":true}
  ],
  "summary_by_rule": {
    "rule_1_no_hardcoded": {"passed":false,"count":3},
    "rule_2_use_component_lib": {"passed":true,"count":0},
    "rule_3_state_coverage": {"passed":false,"count":1,"skipped_reason":null},
    "rule_4_design_md_compliance": {"passed":true,"count":0,"skipped_reason":"pm mode"}
  },
  "fidelity_score": 0,
  "review_report": "<markdown>",
  "required_actions": ["..."]
}
```

字段名固定不要改。kernel 读 `summary_by_rule` 聚合状态。

## 4 条宪法扫描清单

### Rule 1：硬编码颜色/字号/间距
- [ ] 正则扫 CSS / `<style>` / inline / utility：`#[0-9a-fA-F]{3,8}` / `rgb\(` / `rgba\(` / `hsl\(` / `font-size:\s*\d+px` / `padding:\s*\d+px` / `margin:\s*\d+px`
- [ ] 命中后对照 `design_tokens.json`，无匹配 → 违规
- 白名单：`0` / `100%` / `auto` / `inherit` / `transparent` / `currentColor` / 边框 `1px 2px` / `__tests__/*` / `src/styles/theme.*` / `tailwind.config.*`
- 模式：pm 跳过；designer-spec/dsl 严查

### Rule 2：自写基础组件
- [ ] AST 扫 import：`<Button>`/`<Input>`/`<Select>` 是否来自 component_lib_ref
- [ ] 检查项目里有无 `components/Button/index.vue` 自写路径
- 基础（必须组件库）：Button/Input/Select/Checkbox/Radio/Switch/Modal/Drawer/Toast/Tooltip/DatePicker/Table/Pagination/Tabs/Menu/Tag/Badge
- 业务（允许自写）：RuleEditor/VersionTimeline/ApprovalFlow/MetricCard
- 白名单：`<button type="submit">` 无样式 / `<button data-testid="trigger">` 测试占位
- 模式：pm 松；designer-spec/dsl 严

### Rule 3：状态覆盖（所有模式都查）
- [ ] CSS 搜 `:hover` / `:focus` / `:focus-visible` / `:active` / `:disabled`
- [ ] props/state 搜 `loading` / `error`
- [ ] 对照 `component_spec.md` 状态清单，缺项即违规
- 严重等级：缺 hover → minor；缺 focus → **major**（a11y 关键）；缺 disabled → minor
- 模式：pm 至少 hover+focus+disabled；designer-spec default+hover+active+focus+disabled；designer-dsl 全 7 种

### Rule 4：design-spec 偏差（仅 designer-spec/dsl）
- [ ] 解析 `design_spec_md` 提取关键约束（颜色 hex / 字号 / radius / 间距）
- [ ] 对照生成代码 / token，关键差异 → 违规
- 模糊匹配（不算违规）：spec 没明确写到的细节；同 token 名值偏差 ≤10%
- 模式：pm 跳过；designer-spec 查；designer-dsl 严

## 严重等级 + fidelity_score

| 等级 | 触发 | 扣分 |
|---|---|---|
| critical | 编译失败 / 崩溃 / 安全（XSS / 暴露密钥） | -20 |
| major | 硬编码品牌色 / 自写基础 Button / 缺 focus | -8 |
| minor | 单文件硬编码 / 部分状态缺 / token 命名不一致 | -3 |

```
base = 100；最低 0 最高 100
```

期望分：pm ≥60；designer-spec ≥80；designer-dsl ≥95。低于期望即使 violations.count=0 也在 review_report 末尾加警示。

## 审查取舍原则

- [ ] 宁可漏报不要误报：不确定写到 review_report「⚠️ 待人工确认」段，不进 violations 数组
- [ ] location 必须 `file:line` 可定位
- [ ] required_actions ≤ 5 条，按严重程度排序，动词开头
- [ ] 不查项：代码风格 / 注释 / 命名一致性 / 性能 / 测试覆盖率（归 lint/CI）

## summary_by_rule 字段名（不要改）

```
rule_1_no_hardcoded
rule_2_use_component_lib
rule_3_state_coverage
rule_4_design_md_compliance
```

每条带 `passed: bool` + `count: int` + 可选 `skipped_reason: str`。

## 与上下游契约

来源：code-generation 给 `prototype_code/frontend_code/code_generation_summary`；token-extraction 给 `design_tokens`；component-mapping（dsl）给 `component_mapping`。

下游：`gate (QG_REVIEW)` 读 `constitution_violations.count`，count > 0 触发暂停；`resume_from_stage = code-generation`；Checkpoint C4 给用户最终确认。

教学材料：`textbook/code-constitution-rationale.md`（4 条宪法动机 + 4 种修复模板）。
