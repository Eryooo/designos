# 字体系统方法论(Typography System Methodology)

> Domain: design | Type: methodology | Status: pilot
> DesignOS pilot synthesis(本资产为 pilot 阶段综合判断,非可追溯专业文献)。

## purpose

让品牌字体不是"选了个好看的字体",而是**可落地的字体系统**:字重层级清晰、字号比例
和谐、中西文配对协调、跨端可用、授权风险可控。它解决的核心问题是:**字体授权不当会
带来法律风险,中西文配对失调会让中文品牌在国际化时崩塌,跨端字体缺失会导致 fallback
丑陋**。

## applies_to

- 企业/产品/服务品牌的字体系统设计。
- 品牌焕新场景的字体更新。
- 产出 typography_spec(内部)+ 作为 visual_spec 公开。
- 与 logo-design / color-system 并行(都消费 brand_brief)。

## input_contract

- 必需:brand_brief(品牌人格关键词,提供字体气质方向)。
- 字体气质从品牌人格推导(如"现代科技"→几何无衬线,"传统人文"→衬线/楷宋)。

## decision_framework

### 1. 字体角色与配对
- 主字体(标题/品牌展示)+ 辅助字体(正文/功能文本),通常 1-2 个家族。
- **中西文配对(关键)**:中文字体与西文字体需在字重、字面、重心上协调。
  - 失败信号:中文用粗黑,西文配细衬线,视觉重量失衡。
- **冲突取舍**:展示性(标题独特)与功能性(正文易读)冲突时,标题可个性,正文必须易读。

### 2. 字重层级
- 定义品牌使用的字重集合(如 Light / Regular / Medium / Bold)。
- **可量化判断**:相邻层级字重差异是否足以区分(避免 Regular 与 Medium 难辨)。
- 字重不是越多越好;3-4 个层级通常够用。

### 3. 字号比例(模块化比例)
- 采用模块化比例(如 1.25 / 1.333 比例尺)建立字号梯度。
- **可量化判断**:相邻字号比值是否一致(形成和谐梯度,而非随意取值)。
- 定义最小可读字号(正文不小于平台可读下限)。

### 4. 行高与间距
- 正文行高(line-height)通常 1.4-1.6 倍字号;标题可紧凑。
- 中文行高通常需大于西文(中文字面满,需更多呼吸)。
- 字间距(letter-spacing):中文一般不加,西文大写标题可微调。

### 5. 授权风险(硬约束)
- 标注每个字体的授权类型:商用授权 / 开源协议(SIL/OFL)/ 系统字体 / 需采购。
- **授权风险信号**:使用未授权商用字体是法律风险,必须预警。
- 定义 fallback 字体栈(主字体不可用时的降级)。

### 6. 跨端可用性
- Web(web font 加载 / 系统字体)、iOS、Android、印刷各端字体可用性。
- **可量化判断**:每端是否有可用字体或合理 fallback,避免 fallback 到丑陋默认字体。

## senior_heuristics

- **配对先于选字**:中西文配对失调比单个字体不好看更致命。
- **正文易读是底线**:标题可以个性,正文牺牲易读性就是失败。
- **字重克制**:3-4 个字重够用,堆字重 = 没有层级。
- **授权必查**:商用字体授权是法律红线,不确认不承诺。
- **fallback 必备**:不定义 fallback 栈 = 在缺字体的端上裸奔。
- **中文行高更大**:照搬西文行高到中文会显得拥挤。

## output_contract

- 产出 typography_spec(schema: typography_spec.schema.json),含 primary_font /
  secondary_font / weight_hierarchy / size_scale / line_height / cjk_latin_pairing /
  license_status(verified | needs_verification)/ cross_platform。
- 作为 visual_spec 公开,供 visual-identity 汇总。

## quality_rubric

| 维度 | 高阶可评审 | 中阶可用 | 低阶不合格 |
|---|---|---|---|
| 配对 | 中西文配对协调(字重/字面/重心) | 有配对但略失衡 | 配对失调/无中西文考虑 |
| 字重层级 | 3-4 层级清晰可辨 | 有层级 | 层级混乱/难辨 |
| 字号比例 | 模块化比例和谐 | 有梯度 | 随意取值 |
| 行高 | 中西文分别定义合理 | 有行高 | 无行高/中文照搬西文 |
| 授权 | 每字体标授权 + fallback 栈 | 有授权意识 | 无授权信息 |
| 跨端 | 各端可用或合理 fallback | 主端可用 | 未考虑跨端 |

**一票否决**:使用未标注授权的商用字体 / 正文字体不可读 / 无 fallback 栈。

## common_failure_modes

1. **中西文失衡**:中文粗西文细,视觉重量不协调。返工信号:中英混排重心乱。
2. **授权缺失**:用了商用字体不标授权。返工信号:license_status 空或假。
3. **无 fallback**:主字体不可用时降级到系统丑字体。返工信号:跨端测试 fallback 难看。
4. **字重过载**:用了 7-8 个字重,层级反而混乱。返工信号:相邻字重难区分。
5. **字号随意**:字号梯度无规律。返工信号:相邻字号比值不一致。
6. **正文不可读**:正文字号过小或字体不适合长文。返工信号:正文阅读吃力。

## senior_review_checklist

- [ ] 中西文配对在字重/字面/重心上协调?
- [ ] 字重层级 3-4 个且相邻可辨?
- [ ] 字号采用模块化比例,梯度和谐?
- [ ] 中西文行高分别定义且合理?
- [ ] 每个字体标了授权类型,定义了 fallback 栈?
- [ ] 各端(Web/iOS/Android/印刷)可用或有合理 fallback?
- [ ] license_status 诚实(verified / needs_verification)?

## source_assets

- DesignOS pilot synthesis(本资产框架为 pilot 阶段综合判断,无可追溯外部专业文献)。
- 真实关联仓库文件:`skills/brand-creative/contracts/schemas/typography_spec.schema.json`(产出结构契约)。
- 此前无现有共享资产覆盖字体系统(planned → 本批实现)。

## do_not_claim

- 不声称字体已完成商用授权采购(产出授权类型识别与风险预警,采购需用户/法务确认)。
- 不声称已覆盖所有语言场景(如阿拉伯文/泰文等复杂书写系统需专项)。
- license_status 标 needs_verification 时,不声称授权已确认。
- 不替代专业字体排印师的精细调校。
