# 色彩系统方法论(Color System Methodology)

> Domain: design | Type: methodology | Status: pilot
> DesignOS pilot synthesis(本资产为 pilot 阶段综合判断,非可追溯专业文献;WCAG 对比度阈值为公开标准事实)。

## purpose

让品牌色彩不是"挑了几个好看的颜色",而是**可应用的色彩系统**:每个颜色有明确角色,
在明暗背景、数字印刷不同介质下可控,满足可访问性,色差风险可预判。它解决的核心问题
是:**色彩在不同屏幕/印刷下会漂移,可访问性缺陷会把一部分用户挡在门外**。

## applies_to

- 企业/产品/服务品牌的色彩系统设计。
- 品牌焕新场景的色彩更新。
- 产出 color_palette(内部)+ 作为 visual_spec 公开。
- 与 logo-design / typography-system 并行(都消费 brand_brief)。

## input_contract

- 必需:brand_brief(品牌人格关键词,提供色彩情绪方向)。
- 色彩情绪必须从品牌人格推导(如"活力"→暖色高饱和,"信赖"→冷色中低饱和)。

## decision_framework

### 1. 色彩角色分配(不是堆颜色)
- 主色(brand primary)/ 辅助色(secondary)/ 强调色(accent)/ 中性色(neutral)/ 语义色(成功/警告/错误)。
- **冲突取舍**:主色既要有品牌识别度,又要在大面积使用时不疲劳 → 高识别度主色配克制使用面积。
- 每个颜色有明确使用场景,无场景的颜色删除。

### 2. 对比度与可访问性(硬约束)
- 文本与背景对比度:正文 ≥ 4.5:1,大字 ≥ 3:1(WCAG AA)。
- 关键交互元素(按钮/链接)对比度达标。
- **可量化判断**:每个"文本色 × 背景色"组合算出对比度比值。
- 失败信号:主色当正文色但对比度 < 4.5:1。

### 3. 明暗背景双模式
- 定义浅色背景与深色背景下的色彩应用(同一品牌色在深色模式可能需调整明度)。
- **可量化判断**:主色在白底与黑底上是否都可识别且对比达标。

### 4. 数字 / 印刷介质差异
- 数字:RGB / HEX,定义屏幕显示值。
- 印刷:CMYK / Pantone,标注 RGB→CMYK 转换的色差风险(尤其高饱和色、荧光色)。
- **色差风险信号**:高饱和 RGB 色印刷会变暗变灰,必须预警并建议打样。

### 5. 色彩比例与节奏
- 定义主/辅/强调色的使用比例(如 60/30/10 原则的品牌化调整)。
- 强调色克制使用(过度使用强调色 = 没有强调)。

## senior_heuristics

- **角色先于颜色**:先定"需要几个角色的色",再选具体色值,而非反过来。
- **对比度是底线不是加分**:可访问性不达标的配色直接不合格,不是"可优化"。
- **印刷必预警**:屏幕好看的高饱和色印刷常翻车,不打样不承诺。
- **强调色稀缺**:强调色越少越有力;满屏强调等于无强调。
- **深色模式不是反色**:深色模式需重新调明度,不是简单反相。

## output_contract

- 产出 color_palette(schema: color_palette.schema.json),含 primary / secondary /
  contrast_ratios / accessibility(pass | needs_manual_check)/ print_color_risk / dark_light_usage。
- 作为 visual_spec 公开,供 visual-identity 汇总。

## quality_rubric

| 维度 | 高阶可评审 | 中阶可用 | 低阶不合格 |
|---|---|---|---|
| 色彩角色 | 角色齐全(主/辅/强调/中性/语义)有场景 | 主辅色有角色 | 堆颜色无角色 |
| 对比度 | 全组合 ≥ WCAG AA 且标比值 | 主要文本达标 | 正文对比 < 4.5:1 |
| 明暗双模式 | 浅/深背景均定义且达标 | 有主背景模式 | 单模式无深色 |
| 介质差异 | RGB+CMYK/Pantone + 色差预警 | 有 RGB + CMYK | 仅 RGB |
| 比例节奏 | 比例明确,强调色克制 | 有比例 | 无比例/强调泛滥 |

**一票否决**:正文对比度 < 4.5:1(可访问性失败)/ 仅给 RGB 不顾印刷。

## common_failure_modes

1. **对比度不达标**:主色当正文色,对比 < 4.5:1。返工信号:对比度计算失败。
2. **仅数字色**:只给 RGB,印刷物料无 CMYK/Pantone。返工信号:brand-collateral 无法下印。
3. **印刷色差**:高饱和 RGB 未预警印刷漂移。返工信号:打样与屏幕严重不符。
4. **无色彩角色**:列了一堆色但不知道哪个主哪个辅。返工信号:下游不知道用哪个。
5. **强调色泛滥**:满屏强调色,失去强调意义。返工信号:视觉无焦点。
6. **深色模式简单反相**:深色模式直接反色导致刺眼/不可读。返工信号:深色背景对比异常。

## senior_review_checklist

- [ ] 每个颜色有明确角色与使用场景?
- [ ] 所有"文本×背景"组合对比度 ≥ WCAG AA 且标了比值?
- [ ] 浅色 + 深色背景双模式都定义且达标?
- [ ] RGB + CMYK/Pantone 都给,高饱和色标了印刷色差风险?
- [ ] 色彩比例明确,强调色克制?
- [ ] accessibility 字段诚实(pass / needs_manual_check)?

## source_assets

- DesignOS pilot synthesis(本资产框架为 pilot 阶段综合判断;WCAG AA 对比度阈值 4.5:1 / 3:1 为公开可核查标准)。
- 真实关联仓库文件:`knowledge/design/visual/visual-translation.md`(IP 色彩情绪偏向);`skills/brand-creative/contracts/schemas/color_palette.schema.json`。

## do_not_claim

- 不声称色彩已完成印刷打样验证(产出规范 + 色差预警,实物需打样)。
- 不声称已覆盖所有可访问性场景(如各类色盲模拟需专项工具验证)。
- 不声称 Pantone 色值已与供应商确认(需印厂打样确认)。
- accessibility 标 needs_manual_check 时,不声称已通过可访问性审计。
