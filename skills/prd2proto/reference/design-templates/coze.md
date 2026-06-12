---
version: alpha
name: "Coze-style Design System"
description: "AI Agent 平台与对话式工具的浅色卡片化风格，亲和力强、彩色点缀"
suitable_for:
  - AI Agent 编排平台
  - 对话式 AI 应用工作台
  - 大模型调试与 Prompt 工程
  - 智能体市场与插件中心
colors:
  primary: "#4D53E8"
  on-primary: "#FFFFFF"
  surface: "#FFFFFF"
  on-surface: "#1D1C23"
  surface-variant: "#F4F5FA"
  on-surface-variant: "#5C5D6E"
  outline: "#E2E3EC"
  error: "#F5483B"
  success: "#00B375"
  warning: "#FFA800"
typography:
  display:
    fontFamily: "'Inter', 'PingFang SC', system-ui, sans-serif"
    fontSize: 32px
    fontWeight: 600
    lineHeight: 1.25
  heading:
    fontFamily: "'Inter', 'PingFang SC', system-ui, sans-serif"
    fontSize: 20px
    fontWeight: 600
    lineHeight: 1.35
  body:
    fontFamily: "'Inter', 'PingFang SC', system-ui, sans-serif"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.55
  caption:
    fontFamily: "'Inter', 'PingFang SC', system-ui, sans-serif"
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.4
rounded:
  none: 0px
  sm: 6px
  md: 10px
  lg: 16px
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
  sm: "0 2px 8px rgba(31,35,41,0.05)"
  md: "0 6px 16px rgba(31,35,41,0.08)"
  lg: "0 12px 32px rgba(31,35,41,0.1)"
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
    rounded: "{rounded.lg}"
    elevation: "{elevation.sm}"
    padding: "{spacing.lg}"
  input:
    backgroundColor: "{colors.surface-variant}"
    rounded: "{rounded.md}"
    padding: "{spacing.sm}"
recommended_ui_lib:
  react: "antd@5"
  vue: "arco-design"
---

## Design Philosophy

### Overall Vibe
浅色全屏的工作台审美，模块化卡片让复杂的 AI 编排变得可读。圆角偏大（10-16px）传递亲和与"AI 时代"的柔软感。彩色仅在关键状态（成功/警告/AI 回复气泡）出现，主色蓝紫表达智能与品牌。整体是"严肃工具但不冷酷"。

### When to Use
- 智能体（Agent）拖拽编排画布
- 对话/工作流调试控制台
- Prompt 工程与模型评测平台
- 智能体市场、插件商店、模板库

### Usage Guidelines
- **主色使用**：蓝紫 #4D53E8 用于主行动按钮、当前选中节点、AI 回复气泡描边
- **间距体系**：卡片内 lg(16px)，卡片之间 xl(24px)，画布留白用 2xl/3xl
- **圆角原则**：基础元素 10px，卡片 16px，传递"柔软的 AI"
- **阴影使用**：极轻阴影 sm 即可衬托卡片，不需要重投影

### Do's and Don'ts

**DO**:
- 用大圆角卡片切分复杂工作台模块
- AI 输出区域使用浅彩色背景气泡区分人 / AI 角色
- 节点状态（运行中/成功/失败）用清晰彩色标记 + 文字标签

**DON'T**:
- 不要用过于鲜艳的霓虹渐变，与"工具"定位冲突
- 不要堆叠太多彩色，主色 + 中性灰为主，状态色为辅
- 不要把对话气泡做得过于"消费级"花哨，会失去专业感

### 适配 prd2proto 的备注
- 中文 UI 场景下推荐 antd@5 / arco-design，避免自建（宪法规则 2）
- AI 类组件（消息气泡、工具调用展示）若组件库无现成，可作为业务组件自建，但内部仍复用 Button/Tag/Tooltip 原子
- 7 态覆盖里 loading 态特别重要：AI 调用通常 1-10 秒，需要 skeleton + 进度反馈
- 暗色变体可作为可选第二主题（编排画布暗色更聚焦）
