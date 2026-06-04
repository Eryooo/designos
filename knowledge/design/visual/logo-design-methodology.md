# Logo 设计方法论(Logo Design Methodology)

> Domain: design | Type: methodology | Status: pilot
> DesignOS pilot synthesis(本资产为 pilot 阶段综合判断,非可追溯专业文献)。
>
> 本资产覆盖 logo 设计的资深决策,区别于 `design.visual.visual-translation`(偏 IP 角色
> 形态)。Logo 是品牌识别的最小单元,有独立于角色设计的专业要求:黑白可用、极致缩放、
> 轮廓识别、组合形式、商标风险。

## purpose

让 logo 不是"好看的图形",而是**正确的品牌标识**:在任何尺寸、任何介质、任何颜色模式下
都可识别、可应用、可法律自洽(风险可控)。它解决的核心问题是:**logo 一旦定稿就极难
更换,初期的可用性缺陷会在所有物料上被放大**。

## applies_to

- 企业/产品/服务品牌的 logo 设计方向与规范。
- 品牌焕新场景的 logo 更新。
- 产出 logo_spec(内部)+ logo_prompt_pack(AI 绘图提示词)。
- 不适用:IP 角色造型设计(用 `design.visual.visual-translation`)。

## input_contract

- 必需:brand_brief(品牌策略,提供北极星/人格关键词/定位)。
- logo 形态必须从品牌人格关键词推导,不是设计师自由发挥。

## decision_framework

### 1. 标志类型选择
- 字标(wordmark)/ 字母标(lettermark)/ 图形标(symbol)/ 组合标(combination)/ 徽章(emblem)。
- **冲突取舍**:品牌名长 → 避免纯字标;需要小尺寸应用(favicon/app icon) → 优先可独立的图形标或字母标。
- 选择依据必须回到品牌策略(如"科技创新"倾向几何图形标,"传统信赖"倾向徽章)。

### 2. 黑白可用性(硬约束)
- logo 必须先在纯黑白下成立,再加色彩。
- **可量化判断**:转灰度 / 纯黑 / 纯白(反白)三种模式下,主体是否仍可识别。
- 失败信号:依赖颜色区分的元素,在灰度下糊成一团。

### 3. 缩放与轮廓识别
- 定义最小可识别尺寸(数字:favicon 16×16px;印刷:最小物理尺寸)。
- **可量化判断**:在最小尺寸下,轮廓是否唯一可辨(遮住细节只看剪影能否认出)。
- 大尺寸(招牌/包装)下细节是否仍精致,无像素/矢量瑕疵。

### 4. 组合形式与留白
- 定义横版/竖版/纯图标三种锁版(lockup)。
- 定义安全留白区(clear space,通常以 logo 某元素的 N 倍为单位)。
- 定义最小尺寸下的简化版(可省略次要元素)。

### 5. 辅助图形系统
- 从 logo 提炼可延展的辅助图形(图案/纹理/分割线),用于物料丰富度。
- 辅助图形必须与主 logo 同源(共享形态语言),不是另起炉灶。

### 6. 商标风险信号(非法律意见,仅信号)
- 检查:是否使用行业通用符号(难注册)、是否与知名品牌形态相似、是否含通用词汇。
- 标注风险信号,**明确声明这不是商标查重,需专业机构检索**。

## senior_heuristics

- **黑白先行**:先黑白成立再上色,是区分专业与业余的分水岭。
- **剪影测试**:好 logo 遮住细节只看轮廓仍可识别。
- **最小尺寸驱动**:从最难的 favicon 倒推,而非从大海报正推。
- **同源延展**:辅助图形从 logo 长出来,不是配一套无关花纹。
- **少元素**:logo 元素越少越耐用;堆叠元素是初阶炫技。
- **风险诚实**:能标商标风险信号,但绝不声称"可注册/版权清洁"。

## output_contract

- 产出 logo_spec(schema: logo_spec.schema.json),含 form / black_white_usable /
  min_size_px / auxiliary_graphics / trademark_risk_signals / application_scenarios。
- 产出 logo_prompt_pack(schema: logo_prompt_pack.schema.json,含负向控制)。
- logo_spec 作为 visual_spec 公开,供 visual-identity 汇总。

## quality_rubric

| 维度 | 高阶可评审 | 中阶可用 | 低阶不合格 |
|---|---|---|---|
| 标志类型 | 类型选择有策略依据 | 类型合理但依据弱 | 类型与品牌无关 |
| 黑白可用 | 三模式(灰/黑/白)均可识别 | 灰度可用 | 依赖颜色,黑白糊 |
| 缩放 | 16px 轮廓唯一可辨 + 大尺寸精致 | 标准尺寸可用 | 小尺寸不可辨 |
| 组合形式 | 横/竖/图标 + 留白 + 简化版齐全 | 有主锁版 | 无锁版规范 |
| 辅助图形 | 与 logo 同源可延展 | 有辅助图形 | 无 / 不同源 |
| 商标风险 | 信号标注 + 明确声明非查重 | 有风险提示 | 无风险意识 |

**一票否决**:黑白不可用 / 最小尺寸不可辨 / 声称"可注册或版权清洁"。

## common_failure_modes

1. **颜色依赖**:logo 靠颜色区分元素,黑白下失效。返工信号:灰度测试糊成一团。
2. **小尺寸失效**:只设计了大尺寸,favicon 不可辨。返工信号:16px 轮廓认不出。
3. **元素过载**:logo 含太多细节,缩放即丢失。返工信号:大小尺寸像两个 logo。
4. **辅助图形脱节**:配了一套与 logo 无关的花纹。返工信号:辅助图形换掉不影响识别。
5. **商标越界声明**:声称"可注册/版权清洁/最终商用"。返工信号:do_not_claim 被违反。
6. **类型错配**:长品牌名用纯字标,小尺寸挤成一坨。返工信号:app icon 无法容纳。

## senior_review_checklist

- [ ] 标志类型选择回到品牌策略?
- [ ] 灰度/纯黑/反白三模式均可识别?
- [ ] 最小尺寸(16px / 物理最小)轮廓唯一可辨?
- [ ] 横/竖/图标锁版 + 安全留白 + 简化版齐全?
- [ ] 辅助图形与 logo 同源?
- [ ] 商标风险信号已标,且明确声明"非查重,需专业机构检索"?
- [ ] 没有任何"可注册/版权清洁/最终商用"的声明?

## source_assets

- DesignOS pilot synthesis(本资产框架为 pilot 阶段综合判断,无可追溯外部专业文献)。
- 真实关联仓库文件:`knowledge/design/visual/visual-translation.md`(IP 形态偏向,本资产为 logo 专项补充);`knowledge/design/visual/image-prompt-system.md`(prompt pack 结构);`skills/brand-creative/contracts/schemas/logo_spec.schema.json`。

## do_not_claim

- **不声称 logo 已商标查重 / 版权清洁 / 可直接注册**(仅产出设计规范与风险信号,法律事项需专业机构)。
- **不声称已生成最终商用 logo 视觉资产**(仅产出 logo_spec 规范与 AI 绘图 prompt,非最终矢量图形)。
- 不声称辅助图形系统已完整设计(产出方向与约束,非全套素材)。
- 不替代专业 logo 设计师的矢量精修与品牌方定稿。
