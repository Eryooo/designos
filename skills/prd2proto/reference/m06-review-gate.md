# Reference: 代码审查（m06）

> Stage 06 `review-gate` 的方法论库。pipeline 在执行 stage 时 lazy-load 到 LLM 上下文。

## 4 条代码宪法（来自 ADR-003 §7.2）

每次 prd2proto 在 designer-dsl 模式下生成代码必须满足；pm 模式放宽前 3 条但保留状态覆盖。

### Rule 1：不得硬编码颜色 / 字号 / 间距 → 必须用 Token 变量

**为什么**：硬编码会让团队改色板时遍历几百个文件，且无法统一暗色模式 / 多品牌主题。

**违规模式**：

```css
/* ❌ 违规 */
.btn { color: #3B82F6; padding: 16px; font-size: 14px; }

/* ✅ 合规 */
.btn { color: var(--color-primary); padding: var(--spacing-4); font-size: var(--font-body-md); }

/* ✅ 合规：Tailwind utility（utility class 视为 token） */
<button class="bg-blue-500 px-4 text-sm">

/* ✅ 合规：Tailwind 任意值用 token 函数 */
<div class="bg-[var(--color-primary)]">
```

**白名单（不算违规）**：

| 字面量 | 理由 |
|---|---|
| `0`, `100%`, `auto`, `inherit` | 非数值 token |
| `1px solid` 中的 `1px` | 边框宽度有限枚举 |
| 100% / 50% / 33.33% 之类百分比 | 布局比例非颜色 token |
| `transparent`, `currentColor` | CSS 关键字 |
| 测试文件中的 mock 颜色 | 测试用 |
| `__tests__/*` 路径下任何字面量 | 测试代码豁免 |

**检测方法（pm 模式跳过）**：

- 正则扫 CSS / SFC `<style>`：`#[0-9a-fA-F]{3,8}`、`rgb\(`、`rgba\(`、`hsl\(`
- 正则扫 inline style 和 utility：`font-size:\s*\d+px`、`padding:\s*\d+px`、`margin:\s*\d+px`
- 命中后对照 design_tokens.json，看是否能匹配到某个 token；不能 → 违规

### Rule 2：不得自行编写基础组件 → 必须复用本地组件库

**为什么**：基础组件（Button、Input、Modal）业界已有成熟实现（无障碍、键盘导航、状态机等都很复杂），自己写不会比 Ant Design 好。

**违规模式**：

```vue
<!-- ❌ 违规：自定义 button 不用组件库 -->
<button class="my-custom-btn">{{ label }}</button>

<!-- ✅ 合规：用组件库 -->
<a-button type="primary">{{ label }}</a-button>

<!-- ✅ 合规：业务组件可以自己写 -->
<RuleEditor :rule="rule" @save="onSave" />
```

**怎么区分基础 vs 业务**：

| 类型 | 例子 | 自写允许？ |
|---|---|---|
| 基础组件 | Button, Input, Select, Checkbox, Radio, Switch, Modal, Drawer, Toast, Tooltip, DatePicker, Table, Pagination, Tabs, Menu | ❌ 必须用组件库 |
| 业务组件 | RuleEditor, VersionTimeline, ApprovalFlow, MetricCard | ✅ 自写 |
| 复合组件 | SearchBar (Input + Button) | ✅ 自写但内部要用基础组件库 |

**白名单**：

- form 提交 trigger：`<button type="submit">` 无样式 → 放行（trigger 不是按钮）
- a11y 测试占位：`<button data-testid="trigger">` → 放行

**检测方法（pm 模式松查）**：

- AST 扫描 import：所有 `<Button>` / `<Input>` / `<Select>` 等是否来自 component_lib_ref（如 `from 'antd-vue'`）
- 检查项目里是否有 `components/Button/index.vue` 这种自写基础组件路径

### Rule 3：不得跳过状态覆盖（**所有模式都查**）

**为什么**：用户反馈缺失 hover/focus 是 B 端产品最常见的"显得不专业"问题；缺失 loading/error 是数据系统最常见的体验崩塌点。

**七种状态**：

```
default | hover | active | focus | disabled | loading | error
```

**违规模式**：

```vue
<!-- ❌ 违规：Button 只定义 default + hover -->
<style>
.btn { background: var(--color-primary); }
.btn:hover { background: var(--color-primary-hover); }
/* 没 :focus / :disabled / :active */
</style>

<!-- ✅ 合规 -->
<style>
.btn { background: var(--color-primary); }
.btn:hover { background: var(--color-primary-hover); }
.btn:active { background: var(--color-primary-active); }
.btn:focus-visible { outline: 2px solid var(--color-primary); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn--loading { ... }   /* 通常 prop 控制 */
.btn--error  { ... }    /* error 对 Button 不适用，可豁免 */
</style>
```

**判断哪些组件需要全 7 种**：

| 组件 | 必查的状态 |
|---|---|
| Button | default / hover / active / focus / disabled / loading（error 可豁免） |
| Input / Select / Checkbox / Radio | default / hover / focus / disabled / error（active/loading 可豁免） |
| Link / Tab | default / hover / active / focus / disabled |
| Card-clickable | default / hover / active / focus |
| Heading / Divider / Badge / Avatar | 不需要交互状态 |

**检测方法**：

- 在 `<style>` 段或 CSS 文件搜 `:hover` `:focus` `:focus-visible` `:active` `:disabled`
- 在 props 或 reactive state 搜 `loading` / `error`（取决于用 prop 还是 css class 表达）
- 对照 `component_spec.md` 列出来的组件状态清单，缺项即违规
- 严重等级：交互组件缺 hover → minor；缺 focus → **major**（a11y 关键）；缺 disabled → minor

**模式差异**：

- pm 模式：至少要 hover + focus + disabled（其他可选）
- designer-spec 模式：必须 default + hover + active + focus + disabled
- designer-dsl 模式：必须全 7 种（除非组件本身豁免）

### Rule 4：不得忽略 Design.md 约束（仅 designer-spec / designer-dsl）

**为什么**：设计师团队 design-spec.md 是"团队约定"，优先级最高；代码默认值不能覆盖 spec。

**违规模式**：

```css
/* design-spec 写 Button radius=4 */
/* ❌ 违规 */
.btn { border-radius: 8px; }
/* ❌ 违规 */
.btn { border-radius: var(--radius-lg); }  /* radius-lg = 8 */

/* ✅ 合规 */
.btn { border-radius: var(--radius-md); }  /* radius-md = 4 */
```

**检测方法**：

- 解析 `design_spec_md` 提取关键约束（颜色 hex 值、字号、radius、间距）
- 对照生成的代码 / token 文件
- 关键差异 → 违规

**模糊匹配（不算违规）**：

- spec 没明确写到的细节（如 letter-spacing / text-transform）
- 同 token 名但实际值与 spec 略有偏差（>10% 才报，避免噪音）

**模式差异**：

- pm 模式：跳过（无 design_spec_md）
- designer-spec 模式：查
- designer-dsl 模式：严查

## 严重等级判定原则

| 等级 | 触发条件 |
|---|---|
| **critical** | 编译失败 / 运行崩溃 / 安全问题（XSS / dangerouslySetInnerHTML 滥用 / 暴露密钥） |
| **major** | 宪法核心条款违规：硬编码品牌色、自写基础 Button、缺 focus 状态（a11y 关键） |
| **minor** | 单点小漏洞：单文件硬编码、状态部分缺、token 命名不一致 |

**注意**：违规计数用于 gate 判断（`count > 0` 触发暂停），所以不要把 minor 漏掉，但也不要把"代码风格不一致"这种非宪法问题塞进 violations。

## fidelity_score 评分规则

```
base = 100
critical: -20 each
major:    -8 each
minor:    -3 each

最低 = 0；最高 = 100
```

**模式期望分**：

- pm 模式：≥ 60（放宽，演示用）
- designer-spec 模式：≥ 80
- designer-dsl 模式：≥ 95（生产代码）

低于期望分时即使 violations.count = 0，也建议在 `review_report` 末尾加段警示。

## 几种常见违规的修复模板

### 模板 1：硬编码颜色

```diff
- background-color: #3B82F6;
+ background-color: var(--color-primary);
```

`auto_fixable: true`（机械替换）。

### 模板 2：自写基础 Button

```diff
- <button class="my-btn">Click</button>
+ <a-button type="primary">Click</a-button>
```

`auto_fixable: false`（需要人判断 type）。

### 模板 3：缺状态覆盖

```diff
.btn { background: var(--color-primary); }
+ .btn:hover { background: var(--color-primary-hover); }
+ .btn:focus-visible { outline: 2px solid var(--color-primary); }
+ .btn:disabled { opacity: 0.5; cursor: not-allowed; }
```

`auto_fixable: false`（CSS 值需要人决定）。

### 模板 4：design-spec 偏差

```diff
- .btn { border-radius: 8px; }
+ .btn { border-radius: var(--radius-md); /* 4px per spec */ }
```

`auto_fixable: true`（直接替换）。

## 审查时的取舍原则

### 1. 宁可漏报不要误报

不确定的写到 `review_report` 的「⚠️ 待人工确认」段落，不进 `constitution_violations` 数组（避免触发 gate）。

### 2. location 必须可定位

每条违规必须 `file:line`（甚至 `file:line-line`）。如果 generate_code 没给行号，至少给 file 路径。让用户能 ⌘+P 跳过去看。

### 3. required_actions 是给人看的 todo

不超过 5 条，按严重程度排序。语言要简洁 + 动词开头：

```
✅ "替换 3 处硬编码颜色为 token 变量"
❌ "请认真检查代码中是否有不符合宪法第一条规定的内容"
```

### 4. summary_by_rule 是 gate 判断的输入

字段名固定，不要改：

```
rule_1_no_hardcoded
rule_2_use_component_lib
rule_3_state_coverage
rule_4_design_md_compliance
```

每条带 `passed: bool` + 可选 `skipped_reason`。kernel 会读这个聚合状态。

## 与上下游的契约

### 上游

- `code-generation` → `prototype_code` / `frontend_code` / `code_generation_summary`：代码全文 + 元数据
- `token-extraction`（仅 designer-spec/dsl）→ `design_tokens`：token 字典
- `component-mapping`（仅 designer-dsl）→ `component_mapping`：DSL→组件库映射

### 下游

- `gate` (QG_REVIEW) 读 `constitution_violations.count`：决定是否暂停
- `gate.status_reason_from`: `constitution_violations.summary` → 暂停时显示给用户
- `gate.required_actions_from`: `constitution_violations.required_actions` → 用户操作指南
- `gate.resume_from_stage`: `code-generation` → 用户选「修改」时回退到 code-generation 重跑

### Checkpoint C4

代码 + 报告通过 gate 后，C4 给用户最终确认：可以「continue」「modify」「supplement」。

## 当前阶段已知边界

1. **本 stage 是 LLM 软审查**：依赖模型识别违规，可能有漏；P3 阶段会改成静态扫描硬约束（AST + design-tokens.json 比对）。
2. **frontend-codegen 当前是 Mock**：generate_code 返回固定示例代码，违规模式相对单一；真 MCP 上线后违规模式更多，本 prompt 需要补全。
3. **不查的项**：代码风格 / 注释规范 / 命名一致性 / 性能 / 测试覆盖率（这些不在 4 条宪法范围内，归 lint/CI 管）。

## 参考资料（外部）

- ADR-003 §7.2「生产级代码最佳实践」
- W3C WCAG 2.1（focus visibility 是 a11y 必需）
- Ant Design Token System（token 命名参考）
- 项目内：[constitution.md](../constitution.md)
