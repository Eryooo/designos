---
version: alpha
name: "Vercel-style Design System"
description: "黑白高对比的极简几何风，单色调驱动开发者平台与性能监控产品"
suitable_for:
  - 部署平台与 CI/CD 控制台
  - 性能监控与可观测性工具
  - 开发者门户与文档站
  - 极简设计的营销首页
colors:
  primary: "#000000"
  on-primary: "#FFFFFF"
  surface: "#FFFFFF"
  on-surface: "#0A0A0A"
  surface-variant: "#FAFAFA"
  on-surface-variant: "#666666"
  outline: "#EAEAEA"
  error: "#E5484D"
  success: "#0070F3"
  warning: "#F5A623"
typography:
  display:
    fontFamily: "'Geist', 'Inter', system-ui, sans-serif"
    fontSize: 56px
    fontWeight: 700
    lineHeight: 1.05
  heading:
    fontFamily: "'Geist', 'Inter', system-ui, sans-serif"
    fontSize: 22px
    fontWeight: 600
    lineHeight: 1.25
  body:
    fontFamily: "'Geist', 'Inter', system-ui, sans-serif"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.5
  caption:
    fontFamily: "'Geist Mono', 'JetBrains Mono', monospace"
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.4
rounded:
  none: 0px
  sm: 4px
  md: 6px
  lg: 8px
  full: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 24px
  2xl: 40px
  3xl: 64px
elevation:
  none: "none"
  sm: "0 1px 2px rgba(0,0,0,0.04)"
  md: "0 4px 8px rgba(0,0,0,0.06)"
  lg: "0 12px 24px rgba(0,0,0,0.08)"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.md}"
    padding: "{spacing.md}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
    padding: "{spacing.md}"
  card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.lg}"
    elevation: "{elevation.none}"
    padding: "{spacing.lg}"
  input:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.md}"
    padding: "{spacing.sm}"
recommended_ui_lib:
  react: "shadcn-ui"
  vue: "arco-design"
---

## Design Philosophy

### Overall Vibe
黑白纯粹，几何感强。极少使用阴影，靠 1px 描边和留白建立层次。等宽字体在数据与代码区域提供"工程师审美"。整体气质是"零装饰即风格"，让产品本身的内容成为视觉主角。

### When to Use
- Serverless 部署平台、Edge / CDN 控制台
- 网站性能与 Core Web Vitals 监控
- 面向开发者的工具集首页与文档
- 强调速度感与极简主义的品牌站

### Usage Guidelines
- **主色使用**：纯黑作为主行动色，蓝色仅作为辅助强调与链接
- **间距体系**：基础 4px，模块之间偏好 xl/2xl 大留白
- **圆角原则**：6-8px 之间，绝不超过 12px，保持几何克制
- **阴影使用**：默认无阴影，靠 1px outline 分层；只有浮层与对话框才加 sm/md

### Do's and Don'ts

**DO**:
- 数据数字与代码片段使用等宽字体
- 用边框（1px outline）替代阴影做卡片分割
- 标题使用大号字重 700，body 用 400，对比制造节奏

**DON'T**:
- 不要引入彩色渐变或多色阴影
- 不要给基础卡片加复杂阴影，破坏几何纯粹
- 不要堆叠多层背景色，最多两层（surface + surface-variant）

### 适配 prd2proto 的备注
- 等宽字体需要在 Tailwind 主题中追加 `font-mono` 字段（宪法规则 1，桥接层允许）
- shadcn-ui 默认配色已接近此风格，几乎不需要二次定制
- 状态覆盖里 hover 偏好微小亮度变化（surface-variant），不引入新颜色
- 暗色变体可作为可选第二主题，但本模板优先浅色（与 Linear 互补）
