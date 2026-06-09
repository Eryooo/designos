---
version: alpha
name: "Notion-style Design System"
description: "温暖中性的知识管理与文档协作风格，灰白主调、可读性优先、轻量装饰"
suitable_for:
  - 知识库与团队 wiki
  - 文档协作与笔记工具
  - 内容管理系统 / 内部门户
  - 长内容阅读类产品
colors:
  primary: "#2F3437"
  on-primary: "#FFFFFF"
  surface: "#FFFFFF"
  on-surface: "#37352F"
  surface-variant: "#F7F6F3"
  on-surface-variant: "#787774"
  outline: "#E9E9E7"
  error: "#E03E3E"
  success: "#448361"
  warning: "#D9730D"
typography:
  display:
    fontFamily: "'Inter', 'PingFang SC', 'Hiragino Sans GB', system-ui, sans-serif"
    fontSize: 36px
    fontWeight: 700
    lineHeight: 1.2
  heading:
    fontFamily: "'Inter', 'PingFang SC', system-ui, sans-serif"
    fontSize: 22px
    fontWeight: 600
    lineHeight: 1.3
  body:
    fontFamily: "'Inter', 'PingFang SC', system-ui, sans-serif"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.65
  caption:
    fontFamily: "'Inter', 'PingFang SC', system-ui, sans-serif"
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.4
rounded:
  none: 0px
  sm: 3px
  md: 4px
  lg: 8px
  full: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 24px
  2xl: 32px
  3xl: 48px
elevation:
  none: "none"
  sm: "rgba(15,15,15,0.05) 0px 0px 0px 1px, rgba(15,15,15,0.1) 0px 3px 6px"
  md: "rgba(15,15,15,0.05) 0px 0px 0px 1px, rgba(15,15,15,0.1) 0px 5px 10px"
  lg: "rgba(15,15,15,0.05) 0px 0px 0px 1px, rgba(15,15,15,0.1) 0px 9px 24px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.md}"
    padding: "{spacing.md}"
  button-secondary:
    backgroundColor: "{colors.surface-variant}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
    padding: "{spacing.md}"
  card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.md}"
    elevation: "{elevation.sm}"
    padding: "{spacing.lg}"
  input:
    backgroundColor: "{colors.surface-variant}"
    rounded: "{rounded.sm}"
    padding: "{spacing.sm}"
recommended_ui_lib:
  react: "shadcn-ui"
  vue: "element-plus"
---

## Design Philosophy

### Overall Vibe
温暖、中性、像写在纸上。用米白与暖灰打底，避免冷蓝色调。Emoji 与轻量插画让工具不冰冷，但又保持极强的可读性。视觉上几乎没有"装饰"，只有内容与极小的功能性元素（折叠箭头、handle 拖拽点）。

### When to Use
- 团队知识库、产品 wiki、内部 SOP 文档
- 长内容阅读与写作工具（笔记、博客后台）
- 项目周报与会议纪要平台
- 强调"以内容为中心"的协作产品

### Usage Guidelines
- **主色使用**：深灰 #2F3437 替代纯黑，营造柔和阅读体验；强调色用棕橙系
- **间距体系**：行高放松到 1.65，段落之间至少 lg(16px)，让长文能"呼吸"
- **圆角原则**：偏小圆角（3-4px），避免过度圆润破坏文档的"纸面"感
- **阴影使用**：极薄的双层阴影（1px outline + 微下沉），只用在 popover 与卡片上

### Do's and Don'ts

**DO**:
- body 字号偏大（16px），行高放松到 1.6 以上
- 使用 emoji 与图标作为内容入口的视觉锚点
- 默认浅色，可提供暗色作为阅读模式

**DON'T**:
- 不要用纯白 + 纯黑的高对比，会失去温暖感
- 不要在文档区使用复杂的彩色按钮或装饰
- 不要堆叠厚重阴影或玻璃拟态，与文档气质冲突

### 适配 prd2proto 的备注
- 中文场景需要在 fontFamily 里追加 `'PingFang SC'`、`'Hiragino Sans GB'` 兜底（已包含）
- 推荐组件库未限定，但需选择默认风格偏柔和的（避免过强阴影/重圆角）
- 7 态覆盖：hover 用 surface-variant 微亮变体，focus 用 1px primary outline
- design-spec 优先级最高，本模板仅作起点（宪法规则 4）
