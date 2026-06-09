---
version: alpha
name: "Ant Design Pro Design System"
description: "蓝灰体系的企业后台与数据平台风格，信息密度高、表格表单驱动"
suitable_for:
  - 企业级中后台管理系统
  - 数据分析与报表平台
  - 工作流审批与 OA 系统
  - 政务、电信、金融行业管理后台
colors:
  primary: "#1677FF"
  on-primary: "#FFFFFF"
  surface: "#FFFFFF"
  on-surface: "#000000"
  surface-variant: "#F5F7FA"
  on-surface-variant: "#595959"
  outline: "#D9D9D9"
  error: "#FF4D4F"
  success: "#52C41A"
  warning: "#FAAD14"
typography:
  display:
    fontFamily: "'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif"
    fontSize: 30px
    fontWeight: 600
    lineHeight: 1.3
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
  sm: 2px
  md: 6px
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
  sm: "0 1px 2px 0 rgba(0,0,0,0.03), 0 1px 6px -1px rgba(0,0,0,0.02)"
  md: "0 6px 16px 0 rgba(0,0,0,0.08), 0 3px 6px -4px rgba(0,0,0,0.12)"
  lg: "0 9px 28px 8px rgba(0,0,0,0.05), 0 6px 16px 0 rgba(0,0,0,0.08)"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.md}"
    padding: "{spacing.sm}"
  button-secondary:
    backgroundColor: "{colors.surface}"
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
  react: "antd@5"
  vue: "ant-design-vue"
---

## Design Philosophy

### Overall Vibe
经典企业级蓝灰体系，信息密度高，留白克制。强调"一屏装下尽可能多的关键数据"，但靠灰阶层级保持清晰。所有组件都遵循同一套节奏，让用户在 10+ 模块的后台里也能快速定位。颜色克制，状态色（红/黄/绿）只用在数据反馈与告警上。

### When to Use
- 中后台 CRUD 管理（用户/订单/商品/权限）
- BI 报表与数据看板
- 审批流、工单、CRM 系统
- 政企客户的内部运营后台

### Usage Guidelines
- **主色使用**：AntD 蓝 #1677FF 是行动色与品牌色，可在用户偏好下替换为企业主色
- **间距体系**：表格行 8px 紧凑、12px 中等、16px 宽松三档可切；表单字段间距 lg
- **圆角原则**：组件 6px，卡片 8px，避免大圆角破坏严肃性
- **阴影使用**：卡片用 sm，下拉菜单用 md，对话框用 lg

### Do's and Don'ts

**DO**:
- 复杂表单使用 Form + ProForm，字段之间用栅格对齐
- 表格列宽固定关键字段，操作列右侧吸附
- 使用面包屑 + 标签页 + 侧栏三段式导航

**DON'T**:
- 不要在中后台引入消费级花哨色彩或插画
- 不要过度自定义 AntD 默认外观，破坏一致性
- 不要用大圆角卡片，会失去严肃企业感

### 适配 prd2proto 的备注
- 强烈建议直接使用 AntD 5 / Ant Design Vue 组件库（宪法规则 2 完美适配）
- 主题定制走 ConfigProvider + theme.token 桥接（宪法规则 1 允许的桥接点）
- 7 态覆盖：AntD 已内置全套，注意 disabled + loading 组合态不要漏写
- design-spec 若指定企业品牌色，覆盖默认蓝（宪法规则 4）
