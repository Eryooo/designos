---
version: alpha
name: "Apple HIG-style Design System"
description: "圆润通透的消费级与高端品牌风格，动态层次、高质感、优雅"
suitable_for:
  - 消费级 iOS / iPadOS Web 配套应用
  - 高端品牌官网与会员中心
  - 健康 / 运动 / 生活方式类产品
  - 媒体与内容订阅类前端
colors:
  primary: "#0071E3"
  on-primary: "#FFFFFF"
  surface: "#FFFFFF"
  on-surface: "#1D1D1F"
  surface-variant: "#F5F5F7"
  on-surface-variant: "#6E6E73"
  outline: "#D2D2D7"
  error: "#FF3B30"
  success: "#30D158"
  warning: "#FF9F0A"
typography:
  display:
    fontFamily: "'SF Pro Display', -apple-system, 'Helvetica Neue', sans-serif"
    fontSize: 48px
    fontWeight: 600
    lineHeight: 1.08
  heading:
    fontFamily: "'SF Pro Display', -apple-system, 'Helvetica Neue', sans-serif"
    fontSize: 24px
    fontWeight: 600
    lineHeight: 1.2
  body:
    fontFamily: "'SF Pro Text', -apple-system, 'Helvetica Neue', sans-serif"
    fontSize: 17px
    fontWeight: 400
    lineHeight: 1.47
  caption:
    fontFamily: "'SF Pro Text', -apple-system, 'Helvetica Neue', sans-serif"
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.4
rounded:
  none: 0px
  sm: 8px
  md: 12px
  lg: 18px
  full: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  2xl: 48px
  3xl: 80px
elevation:
  none: "none"
  sm: "0 4px 12px rgba(0,0,0,0.06)"
  md: "0 12px 32px rgba(0,0,0,0.1)"
  lg: "0 24px 64px rgba(0,0,0,0.16)"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.full}"
    padding: "{spacing.md}"
  button-secondary:
    backgroundColor: "{colors.surface-variant}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.full}"
    padding: "{spacing.md}"
  card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.lg}"
    elevation: "{elevation.sm}"
    padding: "{spacing.lg}"
  input:
    backgroundColor: "{colors.surface-variant}"
    rounded: "{rounded.md}"
    padding: "{spacing.md}"
recommended_ui_lib:
  react: "radix"
  vue: "element-plus"
---

## Design Philosophy

### Overall Vibe
通透、克制、有质感。大量留白与精致字号阶梯营造高端感。圆角偏大（按钮做成胶囊形），整体气质偏向"消费级精品"。视觉语言极简但每一像素都讲究：行高、字重、间距对称都经过仔细打磨。强调动态层次感（hover 微缩放、淡入淡出）。

### When to Use
- 高端消费级 Web 产品（购物、订阅、会员）
- 与 iOS / iPadOS App 配套的 Web 后台
- 品牌官网、产品介绍页、订单中心
- 健康、运动、生活方式类前端

### Usage Guidelines
- **主色使用**：苹果蓝 #0071E3 用作行动按钮与链接，可被品牌色替换
- **间距体系**：3xl(80px) 用于页面 hero 区块；模块之间至少 2xl(48px)
- **圆角原则**：按钮使用 full（胶囊形）是该风格的灵魂；卡片用 18px 大圆角
- **阴影使用**：阴影偏柔，范围大且羽化，避免硬边

### Do's and Don'ts

**DO**:
- body 字号偏大（17px），SF Pro 是首选字体栈
- hero 区域使用大字号 display + 大量留白做"舞台感"
- 微交互（hover 1.02 缩放、200ms 淡入）让界面"活"起来

**DON'T**:
- 不要使用直角或小圆角（破坏圆润气质）
- 不要堆叠多种字重和字号，保持克制阶梯
- 不要在内容密集的中后台用此风格（信息密度不匹配）

### 适配 prd2proto 的备注
- 字体栈中 SF Pro 是 Apple 系统字体，Web 端通常 fallback 到 system-ui 即可
- 胶囊按钮（rounded.full）需要在组件库主题中显式覆盖默认（宪法规则 1，桥接层允许）
- 7 态覆盖里 hover 推荐用 transform: scale(1.02) + shadow 升级，而非颜色变化
- design-spec 若指定品牌主色，覆盖苹果蓝（宪法规则 4）
