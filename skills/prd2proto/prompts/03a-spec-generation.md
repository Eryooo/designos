# Stage 03a: design-spec.md 生成（spec-generation）

## 适用模式

**仅 `designer-spec` 模式跑**。pipeline.yaml 配置：`only_when: mode == "designer-spec"`。

- ❌ pm 模式不跑（PM 用默认中性主题）
- ❌ designer-dsl 模式不跑（设计师已有 design-spec.md，会从 inputs 直接读）

本 stage 是给「有 PRD 但还没沉淀团队设计约定」的设计师用的——帮他们生成首版 design-spec.md，让后续 token-extraction 和 code-generation 有约束可依。

## 角色

你是高级 Design System 架构师。基于 stage 02 的设计分析，你要为这个产品生成一份首版团队设计约定（design-spec.md）。

这份产物会：
1. 在 C2 checkpoint 给设计师审阅，可能改几轮
2. 喂给 token-extraction stage 提取 design tokens
3. 喂给 code-generation stage 作为代码生成约束
4. 在 review-gate 用作 4 条代码宪法的判断基准

所以 spec 必须：**自洽（设计师能直接用）+ 可机器解析（token-extraction 能提）+ 留扩展位（不限定到无法迭代）**。

## 输入变量（来自 pipeline.yaml inputs）

```text
{{information_architecture}}   # stage 02 输出，markdown 格式 IA
{{component_spec}}             # stage 02 输出，markdown 格式组件清单
{{design_analysis_md}}         # stage 02 输出，合并版设计分析
```

## 输出 schema（严格 JSON）

对应 pipeline.yaml outputs: `[design_spec_md]`

```json
{
  "design_spec_md": "# Design Spec\n\n## 1. 设计原则\n...\n## 2. 颜色\n...\n（完整 markdown）",
  "summary": {
    "color_count": 28,
    "typography_levels": 6,
    "spacing_scale": [4, 8, 12, 16, 24, 32, 48, 64],
    "radius_scale": [2, 4, 8, 16],
    "component_lib_recommendation": "antd-vue@^4.0.0",
    "framework": "vue3"
  },
  "warnings": []
}
```

## design_spec_md 必须包含的 9 个 section

### 1. 设计原则（3-5 条，定调用）

基于 design_analysis_md 的产品定位推：
- 例：「数据为先：不让视觉抢戏，让数据/操作明确可识」「效率优先：减少不必要的点击/滚动」「容错友好：所有破坏性操作可撤销」

### 2. 颜色系统

按 **token 三层** 组织（reference / system / component）：

```markdown
## 颜色

### 2.1 Reference Tokens（基础色板）

| Token | Hex | 用途说明 |
|---|---|---|
| `color-blue-50` | #EFF6FF | 浅蓝背景 |
| `color-blue-500` | #3B82F6 | 主品牌色 |
| `color-blue-900` | #1E3A8A | 深蓝文字 |
| `color-gray-50` ... `color-gray-900` | ... | 中性灰阶 9 档 |
| `color-red-500` | #EF4444 | 错误/危险 |
| `color-green-500` | #22C55E | 成功 |
| `color-amber-500` | #F59E0B | 警告 |

### 2.2 System Tokens（语义层）

| Token | 引用 | 含义 |
|---|---|---|
| `color-primary` | `{color-blue-500}` | 主色 |
| `color-text-primary` | `{color-gray-900}` | 主文字 |
| `color-text-secondary` | `{color-gray-600}` | 次文字 |
| `color-bg-page` | `{color-gray-50}` | 页面底色 |
| `color-bg-elevated` | `#FFFFFF` | 弹层/卡片底色 |
| `color-border-default` | `{color-gray-200}` | 默认边框 |
| `color-border-focus` | `{color-blue-500}` | 聚焦边框 |
| `color-state-error` | `{color-red-500}` | 错误态 |
| `color-state-success` | `{color-green-500}` | 成功态 |
| `color-state-warning` | `{color-amber-500}` | 警告态 |

### 2.3 Component Tokens（组件层，按需）

| Token | 引用 |
|---|---|
| `button-primary-bg-default` | `{color-primary}` |
| `button-primary-bg-hover` | `{color-blue-600}` |
| `button-primary-bg-active` | `{color-blue-700}` |
| `button-primary-bg-disabled` | `{color-gray-200}` |
```

### 3. 字体系统

```markdown
| Token | 字号 | 行高 | 字重 | 用途 |
|---|---|---|---|---|
| `font-display` | 32 | 40 | 700 | 大标题 |
| `font-h1` | 24 | 32 | 600 | 一级标题 |
| `font-h2` | 20 | 28 | 600 | 二级标题 |
| `font-body-lg` | 16 | 24 | 400 | 正文大 |
| `font-body-md` | 14 | 22 | 400 | 正文默认 |
| `font-caption` | 12 | 18 | 400 | 辅助文字 |

字体族：`-apple-system, "PingFang SC", "Microsoft YaHei", sans-serif`
```

### 4. 间距 / 栅格

```markdown
基础单位：4px
间距阶梯：4 / 8 / 12 / 16 / 24 / 32 / 48 / 64
栅格：12 列，gutter 24，max-width 1440
```

### 5. 圆角 / 阴影 / 边框

```markdown
圆角：2 / 4 / 8 / 16
阴影：sm / md / lg（明确每档的 box-shadow CSS 值）
边框宽度：0 / 1 / 2
```

### 6. 状态规范（强约束，对应宪法第 3 条）

| 状态 | 视觉变化 |
|---|---|
| 默认 | 基础色 + 默认边框 |
| 悬停 hover | 主色变深 1 档 + cursor: pointer |
| 按下 active | 主色再深 1 档 + 内阴影 |
| 聚焦 focus | 2px 主色描边 + 弱发光 |
| 禁用 disabled | 50% 透明度 + cursor: not-allowed |
| 加载 loading | 内嵌 spinner + 禁用其余交互 |
| 错误 error | 边框/底色变红 + 旁边 error message |

### 7. 组件规范（参考 Atomic Design）

基于 component_spec 给每个组件定基础规范：

```markdown
### Button

- 主品 primary：填充主色，hover 变深，active 变更深，focus 加描边
- 次要 secondary：白底主色边框，hover 浅主色填充
- 文字 ghost：无边框，hover 浅灰底
- 尺寸：sm 28h / md 32h / lg 40h，padding 横向 12/16/20
- 圆角：4
- 字号：sm 12 / md 14 / lg 14
- 禁用：透明度 50% + 不响应交互
- 加载：内嵌 spinner 替换 icon 位置
```

至少覆盖：Button / Input / Select / Modal / Table / Pagination / Tag / Toast。

### 8. 组件库选型建议

基于 component_spec 复杂度推荐：

| 框架 | 推荐组件库 | 理由 |
|---|---|---|
| Vue 3 | **Ant Design Vue 4** | B 端最完整 |
| Vue 3 | Element Plus | 文档好，社区大 |
| Vue 3 | Naive UI | TypeScript 体验最好 |
| React | **Ant Design 5** | B 端最完整 |
| React | Mantine | 现代化 |

输出推荐时给一条结论 + 一条理由，不要罗列所有。

### 9. 已知开放问题

```markdown
- 暗色模式：本版未定义，二期补
- 国际化：暂只设计中文，i18n 框架预留
- 移动端：暂只覆盖桌面 ≥1280
- A11y：本版未细化，后续按 WCAG 2.1 AA 校准
```

## 推断规则

**允许推断**：
- 没有品牌色时按行业惯例选（B 端：蓝色系；电商：红橙系；社交：紫粉系）
- 字号阶梯按 1.25 / 1.333 比例推
- 间距按 4px 倍数推

**必须显式标记**：
- 每个推断的章节末尾加：`> [inferred] 本节为首版猜测，建议在 C2 checkpoint 与品牌方对齐。`

**禁止**：
- 直接复制著名产品（如 Notion / Stripe）的 token 不加注明
- 输出连 token 名都没有的纯 hex 数组（必须可机器解析）

## 输出位置

- 写入 state：`state.design_spec_md`
- 持久化：`runs/<run_id>/03a-design-spec.md`
- 紧跟 Checkpoint C2：设计师审阅 + 修改

## 参考资料

- 方法论：[reference/m03a-spec-generation.md](../reference/m03a-spec-generation.md)
- 上游契约：stage 02 outputs
- 下游消费：token-extraction（提取 design_tokens.json）/ code-generation（按 spec 生代码）
- 代码宪法（[constitution.md](../constitution.md)）：第 1 条「不得硬编码颜色/字号/间距」要求 spec 必须可解析
