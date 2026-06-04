# 品牌识别质量 Rubric(Brand Identity Quality Rubric)

> Domain: design | Type: rubric | Status: pilot
> DesignOS pilot synthesis(本资产为 pilot 阶段综合判断,非可追溯专业文献)。
>
> 本 rubric 是 brand-creative 的**专用质量标准**,区别于
> `design.quality.ip-design-quality-rubric`(IP 角色设计专用,含世界观/人格/IP 一致性
> 等 brand-creative 不适用的维度)。**禁止用 IP rubric 冒充品牌创意质量标准。**

## purpose

为 brand-creative 所有子技能产出提供统一的质量判定标尺:区分"高阶可评审 / 中阶可用 /
低阶不合格",并定义一票否决项。它解决的核心问题是:**没有量化质量标尺,品牌产出的
"好坏"沦为主观,无法判定能否进入真实项目讨论**。

## applies_to

- brand-creative 全部 13 个子技能的产出质量判定。
- 各子技能 quality_gate 引用本 rubric 作为评分依据。
- visual-identity / brand-guidelines 的最终质量门。
- 不适用:IP 角色设计(用 `design.quality.ip-design-quality-rubric`)。

## input_contract

- 任一子技能产出 + 其 schema。
- 上游产物(用于一致性检查)。

## decision_framework

### 质量三档定义
- **高阶可评审(senior-reviewable)**:资深品牌经理/设计总监愿意在此基础上评审微调,而非推倒重来。
- **中阶可用(mid-usable)**:可进入团队内部讨论,需补充但方向成立。
- **低阶不合格(junior-reject)**:方向或基本面有问题,需返工。

### 通用评分维度(所有子技能)
1. **策略一致性**:产出是否回到 brand_brief 的北极星/定位/人格。
   - 高阶:每个决策可追溯到策略;中阶:大方向一致;低阶:与策略脱节。
2. **可量化达标**:是否满足该子技能的硬指标(对比度/最小尺寸/字重层级等)。
   - 高阶:全部硬指标达标且标了数值;中阶:主要指标达标;低阶:硬指标未达标。
3. **可延展性**:产出能否支撑下游消费(schema 完整、字段可用)。
   - 高阶:schema 完整且下游可直接消费;中阶:基本可用;低阶:下游无法消费。
4. **诚实边界**:是否正确标注推断/风险/降级(inferred / needs_verification)。
   - 高阶:所有不确定项显式标注;中阶:主要风险标注;低阶:伪装完整。

### 一票否决项(任一触发即低阶不合格)
- **可访问性失败**:正文对比度 < 4.5:1(color-system / visual-identity)。
- **黑白不可用**:logo 灰度不可识别(logo-design / visual-identity)。
- **最小尺寸失效**:核心标识在最小尺寸不可辨(logo-design / visual-identity)。
- **授权风险未标**:使用商用字体未标授权(typography-system)。
- **策略脱节**:产出与 brand_brief 北极星无关(所有子技能)。
- **过度承诺**:声称"最终商用/版权清洁/可注册"(所有视觉子技能)。

## senior_heuristics

- **高阶 ≠ 完美**:高阶意味着"资深愿意在此基础上改",不是"无需改"。
- **一票否决先行**:先查一票否决项,触发即不合格,不进入维度评分。
- **量化优先主观**:能量化的维度(对比度/尺寸)用数值,不用"看起来不错"。
- **诚实是高阶门槛**:伪装完整(不标推断/风险)的产出最高只能中阶。
- **可延展是底线**:下游无法消费的产出,再好看也是低阶。

## output_contract

- 对任一子技能产出,输出:三档判定 + 各维度评分 + 一票否决检查结果 + 返工建议。
- 与 `design.quality.professional-gap-report` 配合:中阶/低阶产出附 gap 报告。

## quality_rubric

(本资产是 rubric 本身,以下为"如何评判一次 rubric 应用是否到位")

| 维度 | 高阶可评审 | 中阶可用 | 低阶不合格 |
|---|---|---|---|
| 一票否决检查 | 全部 6 项逐项检查并记录 | 主要项检查 | 跳过一票否决 |
| 维度评分 | 4 维全评 + 证据 | 4 维评分 | 主观无证据 |
| 返工指引 | 不合格项给明确返工条件 | 指出问题 | 仅打分无指引 |

**一票否决(对 rubric 应用本身)**:跳过一票否决检查 / 用 IP rubric 替代本 rubric。

## common_failure_modes

1. **用 IP rubric 冒充**:直接套 ip-design-quality-rubric 评品牌创意。返工信号:评分维度含世界观/人格。
2. **跳过一票否决**:直接进维度评分,漏掉可访问性/黑白可用检查。返工信号:低阶产出被评中阶。
3. **主观打分**:维度评分无证据(对比度未算/尺寸未测)。返工信号:量化维度无数值。
4. **高阶滥用**:把"完成了"当"高阶可评审"。返工信号:有未标风险却评高阶。
5. **无返工条件**:判低阶但不说怎么改。返工信号:gap 报告缺返工指引。
6. **忽略策略一致性**:只看视觉好看不看是否回到策略。返工信号:与 brand_brief 脱节却高分。

## senior_review_checklist

- [ ] 用的是本 rubric 而非 IP rubric?
- [ ] 6 项一票否决逐项检查并记录?
- [ ] 4 个通用维度(策略一致/量化达标/可延展/诚实边界)都评了分 + 证据?
- [ ] 量化维度(对比度/尺寸/字重)用了数值而非主观?
- [ ] 中阶/低阶产出附了 gap 报告与返工条件?
- [ ] "高阶可评审"判定经得起"资深愿意在此改"的检验?

## source_assets

- DesignOS pilot synthesis(本 rubric 框架为 pilot 阶段综合判断;WCAG 对比度阈值为公开标准事实)。
- 真实关联仓库文件:`knowledge/design/quality/ip-design-quality-rubric.md`(IP 专用,本资产为品牌识别专用对应物,二者不可互相替代);`knowledge/design/quality/professional-gap-report.md`(配合使用);`skills/brand-creative/contracts/sub-skill-contracts.yaml`(各子技能 quality_gate 引用本 rubric)。

## do_not_claim

- 不声称通过本 rubric 即代表品牌可最终商用(rubric 是质量门,不是商用许可)。
- 不声称本 rubric 覆盖商业/法务维度(仅设计与品牌识别质量)。
- 不声称"高阶可评审"等于终稿(意味着资深愿意在此基础上评审微调)。
- 不替代真实资深品牌经理/设计总监的人工评审。
