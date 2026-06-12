# Stage: generate_vi_manual

基于一致性分析结果，产出完整 VI 手册，严格对齐 vi_manual.schema.json。

## 输入

- `integration_analysis`: 一致性检查结果（来自上一阶段）
- `visual_spec`: Logo 设计规范
- `color_palette`: 品牌色彩调色板
- `typography_spec`: 字体系统规范

## 任务

将三个视觉子系统聚合为统一 VI 手册，包含引用规则、应用规范、禁忌、一致性结论与缺口声明。

### 1. Logo 章节

从 visual_spec 提取并组织：
- 标志类型与形态方向
- 黑白可用性规则
- 最小尺寸与缩放规则
- 组合形式（横版/竖版/纯图标）
- 安全留白
- 辅助图形方向（引用 mother_shape 视觉变量）
- 商标风险声明

**不得重新描述 logo，必须引用 visual_spec 字段。**

### 2. Color 章节

从 color_palette 提取并组织：
- 主色/辅色/中性色定义
- 使用比例建议
- 对比度与可访问性规则
- 明暗背景使用规则
- 印刷色差风险声明
- 不可使用的色彩组合

**不得重新设计配色，必须引用 color_palette 字段。**

### 3. Typography 章节

从 typography_spec 提取并组织：
- 主/辅字体定义
- 字重层级与使用场景
- 字号比例
- 行高规则
- 中西文配对规则
- 跨端可用性规则
- 授权风险声明

**不得重新选字体，必须引用 typography_spec 字段。**

### 4. Application Rules（至少 5 个场景）

为以下场景定义 VI 应用规则：
1. **名片** — logo 尺寸/位置、色彩使用、字体层级
2. **网站** — header logo 规格、色彩系统应用、字体 web font 规则
3. **社交媒体** — 头像用纯图标版、色彩适配暗色模式、字体可读性
4. **包装** — logo 最小尺寸、CMYK 色彩规则、印刷字体
5. **海报/宣传** — 大尺寸 logo 细节展示、色彩氛围、标题字体

每个场景规则必须引用 logo/color/typography 的具体约束。

### 5. Taboos（使用禁忌）

从三个子系统提取"严格避免"项：
- 来自 visual_spec.avoidance_rule（如有）
- 来自 color_palette: 禁止的色彩组合
- 来自 typography_spec: 禁止的字体混搭
- 通用禁忌：拉伸变形、添加阴影/渐变（除非明确允许）、更改比例

### 6. Consistency Check

从 integration_analysis 直接引用一致性检查结论。

### 7. Inherited Warnings

从 integration_analysis.inherited_warnings 直接引用。

### 8. Gaps

合并以下来源：
- integration_analysis.gaps
- 场景覆盖不足的声明
- pilot 标准边界声明

**必须声明的固定 gaps（即使上游完美也要写）：**
- "本 VI 手册为 pilot 产出，需资深品牌设计师评审后方可商用"
- "商标注册状态未确认，logo 使用需专业商标检索"
- "字体授权状态需人工确认后方可最终采购"

## 输出

严格对齐 vi_manual.schema.json：

```json
{
  "logo": {
    "type": "引用 visual_spec 的标志类型",
    "form_direction": "引用形态方向",
    "black_white_usable": true,
    "min_size_px": 16,
    "lockups": ["horizontal", "vertical", "icon_only"],
    "clear_space_rule": "logo 高度的 25%",
    "trademark_disclaimer": "本信号非商标查重结果"
  },
  "color": {
    "primary": "引用 color_palette.primary",
    "secondary": "引用 color_palette.secondary",
    "accessibility": "引用 accessibility 状态",
    "usage_ratio": "引用使用比例",
    "print_risk": "引用印刷色差风险"
  },
  "typography": {
    "primary_font": "引用 typography_spec.primary_font",
    "secondary_font": "引用 secondary_font",
    "weight_hierarchy": "引用字重层级",
    "license_status": "引用授权状态",
    "cross_platform": "引用跨端规则"
  },
  "auxiliary_graphics": ["从 integration_analysis 引用辅助图形方向"],
  "application_rules": [
    {"scenario": "名片", "logo_rule": "...", "color_rule": "...", "typography_rule": "..."},
    {"scenario": "网站", "logo_rule": "...", "color_rule": "...", "typography_rule": "..."},
    {"scenario": "社交媒体", "logo_rule": "...", "color_rule": "...", "typography_rule": "..."},
    {"scenario": "包装", "logo_rule": "...", "color_rule": "...", "typography_rule": "..."},
    {"scenario": "海报", "logo_rule": "...", "color_rule": "...", "typography_rule": "..."}
  ],
  "taboos": ["拉伸变形", "添加阴影/渐变", "更改比例", "..."],
  "consistency_check": {
    "personality_alignment": "引用 integration_analysis",
    "technical_alignment": "引用 integration_analysis"
  },
  "inherited_warnings": ["引用 integration_analysis.inherited_warnings"],
  "gaps": [
    "本 VI 手册为 pilot 产出,需资深品牌设计师评审后方可商用",
    "商标注册状态未确认",
    "字体授权状态需人工确认"
  ]
}
```

## 质量自检

- [ ] logo/color/typography 三个章节均非空且引用上游字段？
- [ ] application_rules 至少 5 个场景？
- [ ] taboos 非空？
- [ ] consistency_check 引用了 integration_analysis 的一致性结论？
- [ ] inherited_warnings 继承了所有上游警告？
- [ ] gaps 非空且包含 pilot 标准边界声明？
- [ ] 未出现"final production ready / 商标已确认 / 字体授权已确认 / 印刷色已验证"？
- [ ] 未覆盖或修改上游 visual_spec / color_palette / typography_spec？

## 降级行为

若 integration_analysis 标注任一输入缺失：
- 产出降级版 vi_manual，缺失章节标注 `{ "status": "upstream_missing" }`
- gaps 中声明具体缺失项
- 不假装完成，不用占位数据填充
