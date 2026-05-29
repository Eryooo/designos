# Reference: design-spec.md 生成（m03a）

> Stage 03a `spec-generation` 的方法论库。仅 designer-spec 模式下 lazy-load。

## 方法论：Design Tokens 三层架构（W3C Design Tokens Format）

### 1. Reference Tokens（基础层）

最底层、无语义、纯枚举。命名约定 `{category}-{scale}-{step}`：

```
color-blue-50, color-blue-100, ..., color-blue-900
font-size-12, font-size-14, ..., font-size-32
spacing-4, spacing-8, ..., spacing-64
```

**目的**：定义"我们这个产品有哪些颜色、字号、间距"。这一层不参与组件，只参与上层 token 的引用。

### 2. System Tokens（语义层）

引用 reference tokens，赋予含义。命名约定 `{role}-{property}`：

```
color-primary           → {color-blue-500}
color-text-primary      → {color-gray-900}
color-text-secondary    → {color-gray-600}
color-bg-page           → {color-gray-50}
color-border-default    → {color-gray-200}
color-state-error       → {color-red-500}
font-body-md            → {font-size-14}
spacing-component-md    → {spacing-16}
```

**目的**：让组件代码引用语义化 token，未来换 reference 值不影响组件。

### 3. Component Tokens（组件层，按需）

引用 system tokens，做组件级细分。命名 `{component}-{part}-{state}`：

```
button-primary-bg-default     → {color-primary}
button-primary-bg-hover       → {color-blue-600}
button-primary-bg-active      → {color-blue-700}
button-primary-bg-disabled    → {color-gray-200}
button-primary-text-default   → {color-white}
button-primary-radius         → {radius-md}
```

**目的**：组件有自己的特殊需求（如 hover 用 blue-600 而不是 system token）。不是所有组件都需要这一层；通用组件库（antd / element）通常自带。

## 设计原则的提炼方法

### 1. 从 PRD `business_goal` 推

例如 PRD 写"提升数据治理团队效率 3x"，设计原则就要有：
- "效率优先：减少不必要的点击"
- "数据为先：界面让位于数据"

### 2. 从 user_flows 关键路径推

如果关键路径有"3 步内完成新建规则"，设计原则要支撑：
- "操作在 3 步内可达"
- "破坏性操作可撤销"（避免误操作浪费步骤）

### 3. 从产品形态推

| 产品形态 | 典型设计原则 |
|---|---|
| B 端管理后台 | 效率 / 信息密度高 / 容错友好 / 减少视觉噪音 |
| 消费级 App | 情绪化 / 沉浸 / 友好引导 / 个性化 |
| 工具类产品 | 即时反馈 / 专业感 / 极简 |

写 3-5 条，每条带"为什么"（一句话）。

## 颜色系统的快速生成方法

### 1. 主色（primary）

来源优先级：
1. PRD/scope_md 明确指定 → 直接用
2. 推断行业惯例 → 标 `[inferred]`：
   - B 端 SaaS：蓝色（`#3B82F6` Tailwind blue-500）
   - 电商：红/橙（`#EF4444` red-500 或 `#F97316` orange-500）
   - 社交：紫/粉（`#A855F7` purple-500 或 `#EC4899` pink-500）
   - 生产力工具：绿/青（`#10B981` emerald-500）

### 2. 中性灰阶（gray scale）

用 Tailwind gray 9 档：50/100/200/300/400/500/600/700/800/900。直接复制就行：

```
gray-50  #F9FAFB
gray-100 #F3F4F6
gray-200 #E5E7EB
gray-300 #D1D5DB
gray-400 #9CA3AF
gray-500 #6B7280
gray-600 #4B5563
gray-700 #374151
gray-800 #1F2937
gray-900 #111827
```

### 3. 状态色

固定推荐：
- 错误：`#EF4444` (red-500)
- 成功：`#22C55E` (green-500)
- 警告：`#F59E0B` (amber-500)
- 信息：主色或 `#3B82F6`

### 4. 主色衍生

按 primary 推 hover/active 色：

```
primary       = #3B82F6  (blue-500)
primary-hover = #2563EB  (blue-600，加深一档)
primary-active = #1D4ED8 (blue-700，再加深一档)
primary-disabled = primary @ 40% opacity
```

## 字体系统的快速生成方法

### 1. 类型阶梯（Type Scale）

用 1.25（minor third）或 1.333（perfect fourth）比例：

```
caption    12 / 18
body-md    14 / 22  ← 默认
body-lg    16 / 24
h3         18 / 28
h2         20 / 28
h1         24 / 32
display    32 / 40
```

### 2. 字体族

中文产品默认：

```
font-family: -apple-system, BlinkMacSystemFont, "PingFang SC",
             "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
```

英文产品：

```
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
             Roboto, Helvetica, Arial, sans-serif;
```

代码字体（如有）：

```
font-family: "SF Mono", Monaco, Menlo, "Courier New", monospace;
```

## 间距 / 圆角 / 阴影

### 间距阶梯（4px 基础）

```
spacing-1  = 4
spacing-2  = 8
spacing-3  = 12
spacing-4  = 16  ← 最常用
spacing-5  = 20
spacing-6  = 24
spacing-8  = 32
spacing-10 = 40
spacing-12 = 48
spacing-16 = 64
```

不要 5px / 7px / 13px 这种奇数值，破坏视觉节奏。

### 圆角

```
radius-sm  = 2
radius-md  = 4   ← 默认
radius-lg  = 8
radius-xl  = 16
radius-full = 9999  (圆形)
```

### 阴影

```
shadow-sm: 0 1px 2px 0 rgba(0,0,0,0.05);
shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
shadow-xl: 0 20px 25px -5px rgba(0,0,0,0.1);
```

借鉴 Tailwind 的阴影栈，工业界已验证。

## 状态规范模板（强约束）

每个 design-spec.md 必须包含「状态规范」段，明确 7 种状态的视觉变化：

```markdown
| 状态 | bg | border | text | shadow | cursor |
|---|---|---|---|---|---|
| default | white | border-default | text-primary | none | default |
| hover | gray-50 | border-default | text-primary | sm | pointer |
| active | gray-100 | border-default | text-primary | inset | pointer |
| focus | white | border-focus (2px) | text-primary | focus-ring | pointer |
| disabled | gray-50 | border-default | text-disabled | none | not-allowed |
| loading | white | border-default | text-secondary | none | wait |
| error | white | border-error | text-primary + error-msg below | none | default |
```

## 组件库选型参考

### Vue 3

| 组件库 | 优势 | 劣势 | 适合 |
|---|---|---|---|
| **Ant Design Vue 4** | B 端最完整、文档齐 | 视觉样式偏统一、定制成本中 | 数据治理 / SaaS 后台 |
| Element Plus | 文档好、社区大、定制易 | 组件深度浅于 antd | 中小型管理系统 |
| Naive UI | TypeScript 一流、全 ESM | 社区相对小 | 现代化产品 |

### React

| 组件库 | 优势 | 劣势 | 适合 |
|---|---|---|---|
| **Ant Design 5** | 生态最大、设计 token 化彻底 | 包体偏大 | B 端通吃 |
| MUI（Material UI） | Material Design 完整 | Material 风格强烈 | 国际化产品 |
| Mantine | 现代、原子组件丰富 | 国内文档少 | 创业团队 |
| shadcn/ui | 不打包、纯抄代码、Tailwind 原生 | 不是组件库 是组件食谱 | 高度定制 |

### 推荐输出格式

不要罗列所有，只给 1 条结论 + 1 条理由：

```markdown
**推荐**：Ant Design Vue 4

**理由**：本产品是 B 端数据治理后台，需要 Table / Form / Tree / DatePicker 等复杂组件，Ant Design Vue 在这些场景的成熟度最高，且 token 系统已 W3C 化，与本 spec 兼容。
```

## 与下游 stage 的契约

| 产物 | 谁消费 | 怎么用 |
|---|---|---|
| `design_spec_md.颜色 token 表` | token-extraction | 解析为 design-tokens.json (W3C format) |
| `design_spec_md.组件规范` | code-generation | 生成组件代码时遵循 |
| `design_spec_md.状态规范表` | code-generation + review-gate | 生成 + 审查所有状态 CSS |
| `design_spec_md.组件库选型` | code-generation | 决定 import 哪个 UI 库 |
| `summary.framework` | code-generation MCP | 决定生成 React 还是 Vue |

## 推断标记规范

每个推断的章节末尾必须加：

```markdown
> [inferred] 本节为首版猜测，建议在 C2 checkpoint 与品牌方对齐。具体推断依据：本产品定位为 B 端 SaaS，按行业惯例选用蓝色系作为主色。
```

C2 checkpoint 会高亮所有 `[inferred]` 段落，让设计师确认或改。

## 参考资料（外部）

- W3C Design Tokens Format Module（spec）
- Brad Frost, *Designing with Tokens*
- Tailwind CSS（颜色 / 间距 / 阴影栈的工业级参考）
- Ant Design Token System（语义层 token 命名）
- Material Design 3 token system（component token 实践）
