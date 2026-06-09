---
version: alpha
name: "Linear-style Design System"
description: "暗色优先、信息密度高的开发者工具与项目管理风格，键盘优先、灰阶克制"
suitable_for:
  - Issue tracker / Bug 管理
  - 项目管理与冲刺看板
  - 开发者协作工具
  - 代码评审与版本控制后台
colors:
  primary: "#5E6AD2"
  on-primary: "#FFFFFF"
  surface: "#1B1C20"
  on-surface: "#E6E6E6"
  surface-variant: "#26272B"
  on-surface-variant: "#A0A0A8"
  outline: "#363639"
  error: "#EB5757"
  success: "#4CB782"
  warning: "#F2C94C"
typography:
  display:
    fontFamily: "'Inter', 'SF Pro Display', system-ui, sans-serif"
    fontSize: 28px
    fontWeight: 600
    lineHeight: 1.2
  heading:
    fontFamily: "'Inter', system-ui, sans-serif"
    fontSize: 18px
    fontWeight: 600
    lineHeight: 1.3
  body:
    fontFamily: "'Inter', system-ui, sans-serif"
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.5
  caption:
    fontFamily: "'Inter', system-ui, sans-serif"
    fontSize: 11px
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
  sm: 6px
  md: 8px
  lg: 12px
  xl: 16px
  2xl: 24px
  3xl: 32px
elevation:
  none: "none"
  sm: "0 1px 2px rgba(0,0,0,0.3)"
  md: "0 4px 12px rgba(0,0,0,0.4)"
  lg: "0 12px 28px rgba(0,0,0,0.5)"
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
    backgroundColor: "{colors.surface-variant}"
    rounded: "{rounded.lg}"
    elevation: "{elevation.sm}"
    padding: "{spacing.lg}"
  input:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.sm}"
    padding: "{spacing.sm}"
recommended_ui_lib:
  react: "radix"
  vue: "arco-design"
---

## Design Philosophy

### Overall Vibe
暗色基底上的高密度信息架构，灰阶分级精细。圆角偏小，间距紧凑，速度感与专业感并重。视觉表达克制到几乎只剩排版与微妙的灰度差，强调"工程师的工具"气质。键盘快捷键随处可见，每一个 hover 都有明确反馈。

### When to Use
- 软件工程团队的 issue / bug / sprint 管理
- 代码评审与变更追踪平台
- 长时间盯屏使用的运营后台（暗色护眼）
- DevOps / 监控类信息密集型工具

### Usage Guidelines
- **主色使用**：靛紫色仅用于行动按钮、当前选中态与品牌点缀，不做大面积背景
- **间距体系**：基础 4px 网格，列表项之间用 sm/md，页面分区才用 xl/2xl
- **圆角原则**：统一小圆角（4-8px），过大会破坏紧凑感与工程感
- **阴影使用**：暗色场景下阴影偏深、范围小，仅用在浮层与菜单上

### Do's and Don'ts

**DO**:
- 优先暗色主题，浅色主题作为可选变体
- 列表与表格采用紧凑行高，靠灰阶分级建立层次
- 给每个按钮显式的键盘快捷键提示

**DON'T**:
- 不要用纯白背景 + 多彩高亮的"花哨配色"
- 不要堆叠大圆角和厚重阴影，会失去工程感
- 不要在暗色界面用纯黑（#000000），统一到 #1B1C20 一类的深灰

### 适配 prd2proto 的备注
- 暗色主题需要在组件库配置中显式启用（如 Radix 的 dark theme，或 Arco 的 darkTheme）
- 紧凑间距需要在 Tailwind / 主题桥接层重定义 spacing scale（宪法规则 1，桥接文件允许 hex）
- 7 态覆盖里的 focus 必须用键盘可见 ring（focus-visible），这是 Linear 风格的灵魂
- design-spec 若与本模板冲突，优先使用 design-spec（宪法规则 4）
