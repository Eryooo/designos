# Textbook: Design Tokens 三层架构（W3C Design Tokens Format）

> stage 03a / 04 reference 中只列输出约束，本文给愿意深读的读者。

## 1. Reference Tokens（基础层）

最底层、无语义、纯枚举。命名约定 `{category}-{scale}-{step}`：

```
color-blue-50, color-blue-100, ..., color-blue-900
font-size-12, font-size-14, ..., font-size-32
spacing-4, spacing-8, ..., spacing-64
```

**目的**：定义"我们这个产品有哪些颜色、字号、间距"。这一层不参与组件，只参与上层 token 的引用。

## 2. System Tokens（语义层）

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

## 3. Component Tokens（组件层，按需）

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

## 推荐尺度

### 间距（4px 基础）

```
spacing-1=4 / spacing-2=8 / spacing-3=12 / spacing-4=16 (默认)
spacing-5=20 / spacing-6=24 / spacing-8=32 / spacing-10=40
spacing-12=48 / spacing-16=64
```

不要 5px / 7px / 13px 这种奇数值，破坏视觉节奏。

### 圆角

```
radius-sm=2 / radius-md=4 (默认) / radius-lg=8 / radius-xl=16
radius-full=9999 (圆形)
```

### 阴影（借鉴 Tailwind 的阴影栈）

```
shadow-sm: 0 1px 2px 0 rgba(0,0,0,0.05);
shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
shadow-xl: 0 20px 25px -5px rgba(0,0,0,0.1);
```

### 字体阶梯（1.25 比例）

```
caption    12 / 18
body-md    14 / 22  ← 默认
body-lg    16 / 24
h3         18 / 28
h2         20 / 28
h1         24 / 32
display    32 / 40
```

## 参考资料（外部）

- W3C Design Tokens Format Module（spec）
- Brad Frost, *Designing with Tokens*
- Tailwind CSS（颜色 / 间距 / 阴影栈的工业级参考）
- Ant Design Token System（语义层 token 命名）
- Material Design 3 token system（component token 实践）
