---
version: alpha
name: "Stripe-style Design System"
description: "干净专业的金融与企业 SaaS 风格，紫色主调、大量留白、清晰排版"
suitable_for:
  - 金融与支付产品
  - 企业 SaaS 控制台
  - 开发者文档与 API 平台
  - B 端订阅类工具
colors:
  primary: "#635BFF"
  on-primary: "#FFFFFF"
  surface: "#FFFFFF"
  on-surface: "#0A2540"
  surface-variant: "#F6F9FC"
  on-surface-variant: "#425466"
  outline: "#E3E8EE"
  error: "#DF1B41"
  success: "#1FB57F"
  warning: "#F6A609"
typography:
  display:
    fontFamily: "'Sohne', 'Inter', system-ui, -apple-system, sans-serif"
    fontSize: 48px
    fontWeight: 700
    lineHeight: 1.1
  heading:
    fontFamily: "'Sohne', 'Inter', system-ui, sans-serif"
    fontSize: 24px
    fontWeight: 600
    lineHeight: 1.3
  body:
    fontFamily: "'Sohne', 'Inter', system-ui, sans-serif"
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.6
  caption:
    fontFamily: "'Sohne', 'Inter', system-ui, sans-serif"
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.4
rounded:
  none: 0px
  sm: 4px
  md: 6px
  lg: 12px
  full: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  2xl: 48px
  3xl: 64px
elevation:
  none: "none"
  sm: "0 2px 5px -1px rgba(50,50,93,0.06), 0 1px 3px -1px rgba(0,0,0,0.05)"
  md: "0 7px 14px -3px rgba(50,50,93,0.08), 0 3px 6px -2px rgba(0,0,0,0.05)"
  lg: "0 13px 27px -5px rgba(50,50,93,0.12), 0 8px 16px -8px rgba(0,0,0,0.08)"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.md}"
    padding: "{spacing.md}"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.primary}"
    rounded: "{rounded.md}"
    padding: "{spacing.md}"
  card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.lg}"
    elevation: "{elevation.sm}"
    padding: "{spacing.lg}"
  input:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.md}"
    padding: "{spacing.sm}"
recommended_ui_lib:
  react: "shadcn-ui"
  vue: "element-plus"
---

## Design Philosophy

### Overall Vibe
干净、克制、专业。大面积留白衬托内容，紫色主色用作强调而非点缀。排版井然有序，行高放松，给人沉稳可靠的金融科技感。视觉降噪到极致，把信息层级和数据呈现放在第一位。

### When to Use
- 支付平台、收单系统、对账后台
- 面向开发者的 API 文档与控制台
- 企业级 SaaS 订阅、配额、计费类产品
- 财务与税务工具、发票管理

### Usage Guidelines
- **主色使用**：紫色 #635BFF 仅用于主行动按钮、关键链接、重要状态高亮，不要用作大面积背景
- **间距体系**：基础单元 8px 倍数，模块之间至少 lg(24px)，页边距 xl(32px) 起步
- **圆角原则**：按钮与输入框 6px 偏直角，卡片 12px 让信息块更柔和
- **阴影使用**：卡片用 sm 浅阴影体现层次，下拉与浮层用 md，大型对话框才用 lg

### Do's and Don'ts

**DO**:
- 用大量留白让数据呼吸
- 表格与列表保持稳定节奏，避免视觉抖动
- 用单色调灰阶区分次要信息，色彩只用在关键操作上

**DON'T**:
- 不要用渐变背景或彩色阴影制造廉价感
- 不要把紫色铺成大色块，会失去克制气质
- 不要用尖锐圆角（0 或 2px）破坏温润手感

### 适配 prd2proto 的备注
- 颜色 token 与组件库需要桥接到 `tailwind.config.*` 或 shadcn 的 CSS 变量层（符合宪法规则 1）
- 推荐 React shadcn-ui 或 Vue element-plus，避免自建基础组件（宪法规则 2）
- 状态体系（hover/active/focus/disabled/loading/error）紫色主色需要降饱和与提亮两个变体
- design-spec 优先级高于本模板（宪法规则 4），用户可在选中后调整品牌主色与字体栈
