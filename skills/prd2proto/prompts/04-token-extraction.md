# Stage 4: Token 提取

## 输入

- `design_spec_md`：Stage 3a 产出或用户提供的设计规范文档
- `dsl_tree`：Stage 3b 产出的 DSL 节点树（仅 designer-dsl 模式）
- `mode`：当前保真度档位

## 输出 JSON

```json
{
  "design_tokens": {
    "$schema": "https://design-tokens.github.io/community-group/format/",
    "color": { ... },
    "typography": { ... },
    "spacing": { ... },
    "radius": { ... },
    "shadow": { ... }
  }
}
```

## 格式要求（强制 W3C Design Tokens Community Group format）

每个 token 必须是：
```json
{
  "$type": "color | dimension | fontFamily | fontWeight | duration | cubicBezier | shadow | typography",
  "$value": "具体值",
  "$description": "可选说明"
}
```

### $type 枚举

| $type | $value 格式 | 示例 |
|---|---|---|
| color | hex (#RRGGBB) 或 rgba() | `"#3B82F6"` |
| dimension | 数字 + 单位 | `"16px"`, `"1.5rem"` |
| fontFamily | 逗号分隔字体栈 | `"Inter, system-ui, sans-serif"` |
| fontWeight | 数字 | `600` |
| shadow | 对象 | `{"offsetX": "0px", "offsetY": "2px", "blur": "4px", "color": "#0000001a"}` |
| typography | 复合对象 | `{"fontFamily": "{font.sans}", "fontSize": "{size.body}", "lineHeight": "1.5"}` |

### 引用语法

引用其他 token 用 `{path.to.token}`：
```json
{
  "color": {
    "brand": {
      "primary": { "$type": "color", "$value": "#3B82F6" }
    },
    "text": {
      "link": { "$type": "color", "$value": "{color.brand.primary}" }
    }
  }
}
```

## 分层结构（三层 token 架构）

```json
{
  "color": {
    "blue-50": { "$type": "color", "$value": "#EFF6FF" },
    "blue-500": { "$type": "color", "$value": "#3B82F6" },
    "blue-600": { "$type": "color", "$value": "#2563EB" }
  },
  "semantic": {
    "brand-primary": { "$type": "color", "$value": "{color.blue-500}" },
    "brand-primary-hover": { "$type": "color", "$value": "{color.blue-600}" },
    "text-primary": { "$type": "color", "$value": "#1F2937" },
    "text-secondary": { "$type": "color", "$value": "#6B7280" },
    "surface-background": { "$type": "color", "$value": "#FFFFFF" },
    "surface-border": { "$type": "color", "$value": "#E5E7EB" }
  },
  "component": {
    "button-bg": { "$type": "color", "$value": "{semantic.brand-primary}" },
    "button-bg-hover": { "$type": "color", "$value": "{semantic.brand-primary-hover}" },
    "input-border": { "$type": "color", "$value": "{semantic.surface-border}" }
  }
}
```

## 从 design-spec 提取的规则

1. 颜色 token 表格 → 逐行转为 `$type: color`
2. 字体大小表格 → 逐行转为 `$type: dimension`
3. 间距表格 → 逐行转为 `$type: dimension`
4. 圆角 → `$type: dimension`
5. 阴影 → `$type: shadow`
6. 排版组合 → `$type: typography`（复合）

如果 design-spec 没有明确定义某类 token，从 PRD 的视觉参考或选定组件库的默认 token 中推断，并标注 `"$description": "[inferred from antd@5 defaults]"`。

## 同时输出 CSS 变量版本

除了 JSON，还要生成 `tokens.css`，供 Stage 5 代码直接使用：

```css
:root {
  /* color */
  --color-brand-primary: #3B82F6;
  --color-brand-primary-hover: #2563EB;
  --color-text-primary: #1F2937;
  /* spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 12px;
  --spacing-lg: 16px;
  --spacing-xl: 24px;
  /* radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  /* typography */
  --font-size-xs: 12px;
  --font-size-sm: 13px;
  --font-size-body: 14px;
  --font-size-lg: 16px;
  --font-size-title: 20px;
  --font-size-heading: 24px;
}
```

CSS 变量命名规则：`--{category}-{semantic-name}`，全小写，横线分隔。

## 不要做的事

- 不要输出 SCSS / Less / Tailwind config（Stage 5 根据框架选型决定）
- 不要发明 design-spec 没写的颜色（只推断组件库默认值，标注 [inferred]）
- 不要把 token 拍扁成一级（必须保留三层分组）
