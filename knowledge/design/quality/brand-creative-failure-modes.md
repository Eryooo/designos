# 品牌创意失败模式库(Brand Creative Failure Modes)

> Domain: design | Type: failure-modes | Status: pilot
> DesignOS pilot synthesis(本资产为 pilot 阶段综合判断,非可追溯专业文献)。
>
> 本资产是 brand-creative 全链路的失败模式库,区别于
> `design.quality.common-failure-modes`(IP 设计偏向)。每个失败模式含:**现象 /
> 失败信号(可检测) / 根因 / 返工条件**,用于子技能自检与质量门。

## purpose

把品牌创意 AI 产出最常见的翻车点显式化,让每个子技能在产出前能自检、质量门能拦截。
它解决的核心问题是:**多 Agent 并行开发时,如果没有统一的失败模式库,每个子技能会
重复踩同样的坑,且坑在下游被放大**。

## applies_to

- brand-creative 全部子技能的产出前自检。
- 各子技能 quality_gate 的 failure_modes_ref。
- 跨子技能一致性审查。

## input_contract

- 任一子技能产出。
- 上游产物(用于检测断链类失败)。

## decision_framework

每个失败模式四要素:**现象 / 失败信号(可检测) / 根因 / 返工条件**。
按子技能分组列出。

### 策略层(brand-strategy / competitive-analysis)
- **F-BS1 北极星功能化**
  - 现象:北极星写成功能描述。失败信号:北极星含"提供/支持/实现"等功能动词,无情感词。
  - 根因:把产品卖点当品牌价值。返工条件:重写为情感/价值,通过"用户因何感受选我们"测试。
- **F-BS2 伪装竞品对标**
  - 现象:无竞品数据却称差异化已验证。失败信号:differentiation.basis=competitor_matrix 但无矩阵输入。
  - 根因:回避标注推断。返工条件:basis 改 inferred 并声明未验证。
- **F-CA1 竞品矩阵过浅**
  - 现象:竞品矩阵只有名字无维度。失败信号:competitors 项缺 visual_style。
  - 根因:未结构化分析。返工条件:每竞品补视觉/传播/定位维度,≥3 个。

### 视觉层(logo / color / typography / visual-identity)
- **F-LO1 黑白不可用**
  - 现象:logo 依赖颜色区分。失败信号:black_white_usable=false 或灰度测试糊。
  - 根因:先上色后想黑白。返工条件:重做至灰度/纯黑/反白三模式可识别。
- **F-LO2 小尺寸失效**
  - 现象:favicon 不可辨。失败信号:min_size_px 处轮廓认不出。
  - 根因:只设计大尺寸。返工条件:补简化版,16px 轮廓唯一可辨。
- **F-CO1 对比度不达标**
  - 现象:正文色对比 < 4.5:1。失败信号:contrast_ratios 任一正文组合 < 4.5。
  - 根因:重美观轻可访问。返工条件:调整至 WCAG AA,accessibility=pass。
- **F-CO2 仅数字色**
  - 现象:无 CMYK/Pantone。失败信号:print_color_risk 空且无 CMYK。
  - 根因:忽略印刷介质。返工条件:补 CMYK/Pantone + 高饱和色色差预警。
- **F-TY1 授权未标**
  - 现象:商用字体无授权信息。失败信号:license_status 空或非 verified/needs_verification。
  - 根因:忽略法律风险。返工条件:标授权类型 + fallback 栈。
- **F-TY2 中西文失衡**
  - 现象:中西文配对重心失调。失败信号:cjk_latin_pairing 缺失或字重明显不匹配。
  - 根因:只选单语字体。返工条件:补中西文配对协调说明。
- **F-VI1 三源不一致**
  - 现象:VI 汇总后 logo/色彩/字体风格冲突。失败信号:consistency_check 缺失或冲突。
  - 根因:汇总未做一致性校验。返工条件:逐对校验三源,记录冲突解决。

### 内容层(brand-voice / content-strategy / campaign-creative)
- **F-BV1 红线缺失**
  - 现象:声音指南无禁用清单。失败信号:red_lines 为空。
  - 根因:只写能做不写不能做。返工条件:补绝不使用的措辞/语气。
- **F-CS1 内容支柱脱离策略**
  - 现象:内容支柱与品牌核心价值无关。失败信号:content_pillars 不映射 core_values。
  - 根因:为内容而内容。返工条件:每支柱挂回一条核心价值。
- **F-CC1 生成视觉越界声明**
  - 现象:声称已生成最终营销视觉。失败信号:文档含"最终视觉资产/可直接投放"。
  - 根因:混淆 prompt pack 与成品。返工条件:改为"产出方向 + prompt",标 prompt 状态。

### 物料层(brand-collateral / digital-assets / brand-guidelines)
- **F-BC1 印刷规格缺失**
  - 现象:物料无出血/色彩模式/分辨率。失败信号:print_spec_status≠complete 且未标 needs_vendor_confirmation。
  - 根因:不懂印刷流程。返工条件:补印刷规范或诚实标 needs_vendor_confirmation。
- **F-BG1 缺核心章节**
  - 现象:品牌手册缺 VI 或策略。失败信号:strategy_section/vi_section/voice_section 任一空。
  - 根因:上游未完成就汇总。返工条件:补齐必需章节或标 not_included + gap。

### 跨层(所有子技能)
- **F-X1 策略断链**
  - 现象:下游产出找不到 brand_brief 锚点。失败信号:产出无法追溯到北极星/人格。
  - 根因:跳过策略输入。返工条件:重新对齐 brand_brief。
- **F-X2 过度承诺**
  - 现象:声称最终商用/版权清洁/可注册。失败信号:文档含这些词且非否定语境。
  - 根因:夸大能力。返工条件:删除越界声明,改为 pilot 边界声明。
- **F-X3 planned 资产误用**
  - 现象:ready 子技能消费了尚未实现的 planned 资产。失败信号:knowledge_ids.active 含 planned id。
  - 根因:契约与就绪状态不一致。返工条件:降级为 blocked_by_knowledge 或先补资产。

## senior_heuristics

- **失败信号必须可检测**:每个失败模式的信号要能被人工或脚本检出,不是"感觉不对"。
- **返工条件要具体**:返工条件是"改成什么样算过",不是"再改改"。
- **跨层失败最贵**:F-X 类(断链/过度承诺/误用 planned)会污染整个 Group,优先防。
- **并行前必读**:多 Agent 并行开发前,每个 Agent 先读本库对应分组。

## output_contract

- 子技能产出前:对照本库对应分组自检,记录命中的失败模式 + 处置。
- 质量门:作为 failure_modes_ref 被 quality_gate 引用。

## quality_rubric

| 维度 | 高阶可评审 | 中阶可用 | 低阶不合格 |
|---|---|---|---|
| 自检覆盖 | 对照本层全部模式自检 | 主要模式自检 | 跳过自检 |
| 信号可检测 | 命中信号有具体证据 | 有信号描述 | 主观判断 |
| 返工闭环 | 命中即给返工条件 | 指出问题 | 仅记录不处置 |

**一票否决**:F-X2 过度承诺命中未处置 / F-X3 planned 误用未处置。

## common_failure_modes

(本资产是失败模式库,以下为"如何误用本库")
1. **当读物不自检**:读了不对照产出检查。失败信号:产出无自检记录。返工:补自检。
2. **信号不可检测**:写"质量不高"这类无法检出的信号。返工:改为可检测信号。
3. **返工条件含糊**:写"优化一下"。返工:改为"改成什么算过"。
4. **漏跨层模式**:只查本层不查 F-X。返工:补 F-X 检查。
5. **新坑不沉淀**:发现新失败模式不回写本库。返工:沉淀进对应分组。

## senior_review_checklist

- [ ] 子技能产出前对照了本库对应分组?
- [ ] 命中的失败模式有具体可检测证据?
- [ ] 每个命中项给了返工条件(改成什么算过)?
- [ ] F-X 跨层模式(断链/过度承诺/planned 误用)逐项查了?
- [ ] 新发现的失败模式回写了本库?

## source_assets

- DesignOS pilot synthesis(本失败模式库为 pilot 阶段综合判断,无可追溯外部专业文献)。
- 真实关联仓库文件:`knowledge/design/quality/common-failure-modes.md`(IP 偏向,本资产为品牌创意对应物);`knowledge/design/quality/brand-identity-quality-rubric.md`(配合的质量 rubric);`skills/brand-creative/contracts/sub-skill-contracts.yaml`(各子技能 failure_modes_ref 引用本库)。

## do_not_claim

- 不声称覆盖所有可能的品牌创意失败模式(pilot 基线,持续沉淀)。
- 不声称通过自检即无缺陷(降低风险,非消除)。
- 不替代真实资深评审对深层问题的发现。
