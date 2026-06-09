# prd2proto 代码宪法

4 条不可违反的硬约束。review-gate 逐条检查，违反任一条即触发 QG_REVIEW gate。

---

## 规则 1：不得硬编码颜色 / 字号 / 间距

所有视觉维度必须通过 Design Token 变量引用，禁止在组件代码中出现字面量。

**违规示例**：
```tsx
<div style={{ color: '#3B82F6', fontSize: 14, padding: 16 }}>
```

**合规示例**：
```tsx
<div style={{ color: 'var(--color-brand-primary)', fontSize: 'var(--font-size-body)', padding: 'var(--spacing-md)' }}>
```

**允许的字面量白名单**（不视为硬编码）：
- `0`, `100%`, `auto`, `inherit`, `currentColor`, `transparent`
- `border-width` 属性中的 `1px`, `2px`（仅限 border-* / outline-*）
- design-spec 显式枚举的固定值

**组件库主题桥接文件例外**：
以下路径允许 hex 字面量，但每个值必须与 design-spec 完全一致：
- `src/styles/theme.*`（AntD ConfigProvider / MUI createTheme）
- `tailwind.config.*`
- 文件顶部必须有注释标明"单一桥接点，值来自 design-spec §X"

**pm 模式**：此规则放宽为建议（不触发 gate），但 review-report 仍记录。

---

## 规则 2：不得自行编写基础组件

所有基础 UI 元素（Button / Input / Select / Modal / Table / Form / Tabs / Menu / Tooltip / Drawer / Tag / Badge）必须从用户指定的组件库导入，禁止自行实现。

**违规示例**：
```tsx
function Button({ children }) {
  return <button className="my-btn">{children}</button>;
}
```

**合规示例**：
```tsx
import { Button } from 'antd';
```

**例外**：
- 组件库不提供的业务组件（如 FlowEditor / GanttChart）允许自建
- 自建组件内部仍必须复用组件库原子（如自建 FlowEditor 内的按钮用 antd Button）

**pm 模式**：放宽为"尽量复用"，允许用原生 HTML 快速出原型。

---

## 规则 3：不得跳过状态覆盖

每个交互组件必须覆盖以下 7 种状态，缺任何一种即违规：

| 状态 | 说明 |
|---|---|
| default | 初始态 |
| hover | 鼠标悬停 |
| active / pressed | 按下 |
| focus | 键盘聚焦（含 focus-visible） |
| disabled | 不可用 |
| loading | 异步等待 |
| error | 错误态 |

**适用范围**：Button / Input / Select / Checkbox / Radio / Switch / Link / Tab / MenuItem

**不适用**：纯展示组件（Text / Image / Divider / Spacer）

**pm 模式**：此规则**不放宽**。即使低保真原型也必须覆盖 7 态。

---

## 规则 4：不得忽略 Design.md 约束

当用户提供 `design-spec.md` 或 `Design.md` 时，其中的约定优先级**高于**所有其他规范。

**具体含义**：
- design-spec 指定的颜色 > 组件库默认主题色
- design-spec 指定的间距 > 组件库默认间距
- design-spec 指定的圆角 > 组件库默认圆角
- design-spec 指定的组件库选型 > LLM 自行判断

**违规示例**：design-spec 写"主色 #3B82F6"，代码用了 AntD 默认蓝 `#1677ff`。

**pm 模式**：如果用户没提供 design-spec，此规则不适用。

---

## 严重等级判定

| 等级 | 扣分 | 触发条件 |
|---|---|---|
| critical | -20 | 规则 3 缺 3 种以上状态；规则 2 自建了组件库已有的基础组件 |
| major | -8 | 规则 1 硬编码 3 处以上；规则 4 与 design-spec 偏差 3 处以上 |
| minor | -3 | 规则 1 硬编码 1-2 处；规则 3 缺 1 种状态；规则 4 偏差 1-2 处 |

**fidelity_score 计算**：100 - sum(扣分)。低于 60 分强制触发 QG_REVIEW gate。

---

## review-gate 检查清单

review-gate 必须逐条输出：

```json
{
  "constitution_violations": [
    {
      "rule_id": 1,
      "severity": "major",
      "location": "src/components/TaskCard.tsx:42",
      "description": "硬编码 fontSize: 14",
      "fix_suggestion": "改为 var(--font-size-body) 或 token.fontSizeBody"
    }
  ],
  "fidelity_score": 85,
  "mode_adjustments": "pm 模式：规则 1/4 降为建议，规则 2/3 仍强制"
}
```
