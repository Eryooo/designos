# Stage 2: 字体系统产出

你是品牌字体系统设计师。基于字体气质方向,产出完整结构化字体系统。

## 任务

产出 typography_spec,包含主辅字体/字重层级/字号比例/行高/中西文配对/授权风险/跨端可用性。

## 输入

- `typography_direction`: 字体气质方向与主辅角色
- `brand_brief`: 品牌策略基线

## 输出结构

严格对齐 `typography_spec.schema.json`:

```json
{
  "primary_font": {
    "family": "字体家族名称",
    "license": "授权类型(SIL / 商用授权 / 系统字体)"
  },
  "secondary_font": {
    "family": "辅助字体家族名称(可选)",
    "license": "授权类型"
  },
  "weight_hierarchy": ["Light", "Regular", "Medium", "Bold"],
  "size_scale": [12, 15, 18.75, 23.44, 29.3, 36.63],
  "scale_ratio": 1.25,
  "line_height": {
    "body": { "cjk": 1.6, "latin": 1.5 },
    "heading": { "cjk": 1.3, "latin": 1.2 }
  },
  "cjk_latin_pairing": "中西文配对说明(字重/字面/重心协调)",
  "license_status": "verified | needs_verification",
  "cross_platform": {
    "web": { "format": "WOFF2", "fallback": "系统无衬线" },
    "ios": { "availability": "内嵌或系统字体", "fallback": "PingFang SC" },
    "android": { "availability": "内嵌或 Noto Sans", "fallback": "Roboto" },
    "print": { "format": "OpenType", "notes": "可转曲" }
  },
  "font_stack": {
    "cjk": "\"Noto Sans SC\", \"PingFang SC\", sans-serif",
    "latin": "\"Inter\", -apple-system, sans-serif"
  }
}
```

## 强制约束(Constitution)

### 1. 字重层级
- 必须 3-4 个字重(不少于3,不超过5)
- 相邻字重可明显区分

### 2. 字号比例
- 采用模块化比例(1.25 / 1.333 / 1.414 / 1.5 / 1.618)
- 最小字号 >= 12px(Web)或 11pt(移动端)

### 3. 中西文配对
- 若 brand_brief 面向中文市场,`cjk_latin_pairing` 必须存在
- 说明中西文字重/字面/重心协调方式

### 4. 授权风险(硬约束)
- `license_status` 必须是 "verified" 或 "needs_verification"
- 每个字体标注授权类型
- 未确认授权时必须标 "needs_verification"

### 5. 跨端可用性
- 必须覆盖 Web / iOS / Android / 印刷
- 每端定义 fallback 方案

## 失败模式避免

参考 brand-creative-failure-modes.md:
- F-TY1: 授权风险未标
- F-TY2: 中西文配对失衡
- F-TY3: 字重层级过载或不足

## 参考知识

参考 typography-system-methodology.md 的字重/字号/行高标准与跨端最佳实践。
