---
version: alpha
name: "Arco Design (字节系) Design System"
description: "清爽现代的年轻消费产品风格，橙红主色、丰富插画、活力"
suitable_for:
  - 年轻向消费级 Web 产品
  - 字节系产品风格的内容平台
  - 教育 / 兴趣社区 / 工具类 ToC 应用
  - 营销活动页与运营后台
colors:
  primary: "#F53F3F"
  on-primary: "#FFFFFF"
  surface: "#FFFFFF"
  on-surface: "#1D2129"
  surface-variant: "#F7F8FA"
  on-surface-variant: "#86909C"
  outline: "#E5E6EB"
  error: "#F53F3F"
  success: "#00B42A"
  warning: "#FF7D00"
typography:
  display:
    fontFamily: "'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif"
    fontSize: 32px
    fontWeight: 600
    lineHeight: 1.25
  heading:
    fontFamily: "'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif"
    fontSize: 20px
    fontWeight: 500
    lineHeight: 1.4
  body:
    fontFamily: "'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.5715
  caption:
    fontFamily: "'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif"
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.5
rounded:
  none: 0px
  sm: 4px
  md: 8px
  lg: 12px
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
  sm: "0 2px 4px 0 rgba(0,0,0,0.04)"
  md: "0 4px 10px 0 rgba(0,0,0,0.06)"
  lg: "0 12px 24px 0 rgba(0,0,0,0.08)"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.md}"
    padding: "{spacing.sm}"
  button-secondary:
    backgroundColor: "{colors.surface-variant}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
    padding: "{spacing.sm}"
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
  react: "@arco-design/web-react"
  vue: "@arco-design/web-vue"
---

## Design Philosophy

### Overall Vibe
清爽、年轻、有活力。橙红色作为主色传达热情与行动力，但靠浅色背景与留白避免过载。圆角中等（8-12px），字号克制，适合年轻消费用户长时间使用。视觉气质介于 AntD（严肃）与 Coze（柔软）之间，偏向"现代化但不冷冰冰"。

### When to Use
- 字节系或类似定位的 ToC 工具
- 教育、兴趣社区、轻量内容平台
- 营销活动页、电商促销页
- 同时承担 ToB 后台 + ToC 入口的混合产品

### Usage Guidelines
- **主色使用**：橙红 #F53F3F 用于主行动与品牌强调，慎用大面积背景
- **间距体系**：列表项 lg(16px)，模块之间 xl(24px)，活动页可放大到 2xl
- **圆角原则**：基础 8px，卡片 12px，传递"现代消费级"
- **阴影使用**：sm 浅阴影衬托卡片，hover 升级到 md

### Do's and Don'ts

**DO**:
- 在活动页与 banner 区域使用插画 + 渐变营造活力
- 重要数据用大字号 + 主色突出（如订单数、积分）
- ToC 入口使用大圆角卡片 + 图标增强亲和力

**DON'T**:
- 不要把橙红色铺满整页，会过于刺激
- 不要用过多状态色，保持主色 + 中性灰为主
- 不要用极小字号（<12px），年轻用户也需可读性

### 适配 prd2proto 的备注
- 强烈建议使用 @arco-design/web-react 或 @arco-design/web-vue（宪法规则 2 完美适配）
- Arco 默认主题已接近此模板，主要需调整品牌主色（如改为蓝/紫/绿适配不同业务）
- 7 态覆盖：Arco 内置完整状态，注意 hover 与 active 的颜色差需明显
- 主题切换走 ConfigProvider + theme tokens（宪法规则 1 允许的桥接点）
