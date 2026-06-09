# Reference: Token 提取（m04 checklist）

> Stage 04 `token-extraction` 约束清单。教学材料见 `textbook/design-tokens-w3c.md`。

## 输出格式强制 W3C DTCG

每个 token：

```json
{
  "$type": "...",
  "$value": "...",
  "$description": "可选"
}
```

## $type 枚举对照

| $type | $value 格式 | 示例 |
|---|---|---|
| color | hex / rgba | `"#3B82F6"` |
| dimension | 数字+单位 | `"16px"`, `"1.5rem"` |
| fontFamily | 逗号分隔字体栈 | `"Inter, system-ui, sans-serif"` |
| fontWeight | 数字 | `600` |
| shadow | 对象 | `{"offsetX":"0px","offsetY":"2px","blur":"4px","color":"#0000001a"}` |
| typography | 复合对象 | `{"fontFamily":"{font.sans}","fontSize":"{size.body}","lineHeight":"1.5"}` |
| duration | ms/s | `"200ms"` |
| cubicBezier | 4 元数组 | `[0.4, 0, 0.2, 1]` |

## 引用语法

```json
{"text": {"link": {"$type":"color","$value":"{color.brand.primary}"}}}
```

- [ ] 必须 `{}` 包裹（不能用 `var()` 或裸名）
- [ ] 引用路径必须实际存在
- [ ] 引用层级 ≤ 3（reference → semantic → component）

## 三层架构强约束

```
color.<reference>     "blue-50", "blue-500"（最底层，纯 hex）
semantic.<purpose>    "brand-primary"（引用 reference）
component.<part>      "button-bg"（引用 semantic）
```

- [ ] reference 层只含纯值，不能引用其他 token
- [ ] semantic 层至少引用一次 reference
- [ ] component 层引用 semantic（不能直接引用 reference）
- [ ] 不允许拍扁成一级

## 同时输出 CSS 变量版本

`tokens.css` 命名规则 `--{category}-{semantic-name}`，全小写横线分隔：

```css
:root {
  --color-brand-primary: #3B82F6;
  --spacing-md: 12px;
  --font-size-body: 14px;
}
```

- [ ] JSON 路径 `color.brand.primary` ↔ CSS `--color-brand-primary`
- [ ] CSS 变量值是终值（解析所有引用），不含 `{}`
- [ ] 必须放 `:root`

## 从 design-spec 提取规则

| design-spec 表格 | $type |
|---|---|
| 颜色 token | color |
| 字体大小 / 间距 / 圆角 | dimension（加 `px`） |
| 阴影 | shadow（拆 offsetX/Y/blur/color） |
| 排版组合 | typography（复合） |

design-spec 没明确的 token，从组件库默认值推断 + 标 `"$description": "[inferred from antd@5 defaults]"`。

## 不要做的事

- [ ] 不要输出 SCSS / Less / Tailwind config（Stage 5 决定）
- [ ] 不要发明 design-spec 没写的颜色（只推断 + 标 [inferred]）
- [ ] 不要拍扁成一级
- [ ] 不要在 reference 层用引用语法

## 与下游 stage 的契约

| 产物 | 谁消费 |
|---|---|
| `design_tokens` JSON | code-generation |
| `tokens.css` | code-generation 直接 import |
| token 命名 | review-gate 校验代码引用 |

教学材料：`textbook/design-tokens-w3c.md`。
