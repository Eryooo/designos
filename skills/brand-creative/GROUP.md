---
name: brand-creative
version: 0.1.0-baseline
type: group
description: 品牌创意全链路 Skill Group,从策略到落地物料,覆盖品牌识别/VI/内容/营销创意
requires:
  kernel: ">=1.0.0,<2.0.0"
sub_skills:
  # Phase 1: 策略与定位
  - id: brand-strategy
    path: sub-skills/brand-strategy/SKILL.md
    description: 品牌策略基线(定位/差异化/核心价值/人格关键词)
  - id: competitive-analysis
    path: sub-skills/competitive-analysis/SKILL.md
    description: 竞品分析(视觉风格/传播策略/市场空白)
  # Phase 2: 视觉识别系统
  - id: logo-design
    path: sub-skills/logo-design/SKILL.md
    description: Logo 设计(形态/色彩/辅助图形/应用规范)
  - id: color-system
    path: sub-skills/color-system/SKILL.md
    description: 品牌色彩系统(主色/辅色/色彩情绪/应用场景)
  - id: typography-system
    path: sub-skills/typography-system/SKILL.md
    description: 字体系统(主字体/辅助字体/字号层级/排版规范)
  - id: visual-identity
    path: sub-skills/visual-identity/SKILL.md
    description: 完整 VI 手册(logo/色彩/字体/辅助图形/应用规范)
  # Phase 3: 品牌内容与传播
  - id: brand-voice
    path: sub-skills/brand-voice/SKILL.md
    description: 品牌声音(语调/口头禅/场景话术/内容原则)
  - id: content-strategy
    path: sub-skills/content-strategy/SKILL.md
    description: 内容策略(内容支柱/渠道矩阵/节奏日历)
  - id: campaign-creative
    path: sub-skills/campaign-creative/SKILL.md
    description: 营销创意(campaign 主题/视觉方向/传播素材)
  # Phase 4: 物料与落地
  - id: brand-collateral
    path: sub-skills/brand-collateral/SKILL.md
    description: 品牌物料(名片/信头/包装/宣传册)
  - id: digital-assets
    path: sub-skills/digital-assets/SKILL.md
    description: 数字资产(网站视觉/社交媒体模板/H5 规范)
  - id: brand-guidelines
    path: sub-skills/brand-guidelines/SKILL.md
    description: 完整品牌手册(策略/VI/声音/内容/物料)
  - id: brand-audit
    path: sub-skills/brand-audit/SKILL.md
    description: 品牌审计(当前品牌健康度/差距/优化建议)
workflows:
  - id: full-brand-identity
    file: workflows/full-brand-identity.yaml
    description: 完整品牌识别全链路(策略 → VI → 内容 → 物料 → 手册)
  - id: logo-vi-fast-track
    file: workflows/logo-vi-fast-track.yaml
    description: Logo+VI 快速通道(仅视觉识别系统)
  - id: brand-refresh
    file: workflows/brand-refresh.yaml
    description: 品牌焕新(审计 → 策略 → VI 更新)
  - id: campaign-sprint
    file: workflows/campaign-sprint.yaml
    description: 营销创意冲刺(策略 → campaign 概念 → 素材)
---

# brand-creative — 品牌创意 Skill Group

> Skill Group 型,13 个子技能覆盖品牌创意全链路,4 个预定义 workflow 组合。

## 定位

brand-creative 是一个 **Skill Group**,覆盖品牌创意全链路:从品牌策略、视觉识别系统(logo / VI)、品牌内容与传播、到执行物料与品牌手册。它对标 ip-design,但扩展到非 IP 品牌识别(企业品牌/产品品牌/服务品牌)。

**与 ip-design 的关系**:
- **ip-design**(单 skill):聚焦 **IP 角色设计**(人格化 IP,如吉祥物/虚拟代言人),产出 IP 世界观/人格/视觉/内容/物料。
- **brand-creative**(Skill Group):覆盖 **品牌识别系统**(logo / VI / 品牌手册 / 营销创意),更广但更浅(无 IP 人格建模/世界观)。

两者可组合:品牌先用 brand-creative 建立 VI,再用 ip-design 设计品牌 IP。

## 13 个子技能

### Phase 1: 策略与定位(2 个)
1. **brand-strategy**:品牌策略基线(定位/差异化/核心价值/人格关键词)。
2. **competitive-analysis**:竞品分析(视觉风格/传播策略/市场空白)。

### Phase 2: 视觉识别系统(4 个)
3. **logo-design**:Logo 设计(形态/色彩/辅助图形/应用规范)。
4. **color-system**:品牌色彩系统(主色/辅色/色彩情绪/应用场景)。
5. **typography-system**:字体系统(主字体/辅助字体/字号层级/排版规范)。
6. **visual-identity**:完整 VI 手册(logo / 色彩 / 字体 / 辅助图形 / 应用规范)。

### Phase 3: 品牌内容与传播(3 个)
7. **brand-voice**:品牌声音(语调/口头禅/场景话术/内容原则)。
8. **content-strategy**:内容策略(内容支柱/渠道矩阵/节奏日历)。
9. **campaign-creative**:营销创意(campaign 主题/视觉方向/传播素材)。

### Phase 4: 物料与落地(4 个)
10. **brand-collateral**:品牌物料(名片/信头/包装/宣传册)。
11. **digital-assets**:数字资产(网站视觉/社交媒体模板/H5 规范)。
12. **brand-guidelines**:完整品牌手册(策略/VI/声音/内容/物料)。
13. **brand-audit**:品牌审计(当前品牌健康度/差距/优化建议)。

## 4 个预定义 workflow

1. **full-brand-identity**:完整品牌识别全链路(1 → 2 → 3-6 → 7-9 → 10-12),适合从零建立品牌。
2. **logo-vi-fast-track**:Logo+VI 快速通道(仅 3-6),适合已有策略只需视觉执行。
3. **brand-refresh**:品牌焕新(13 audit → 1 strategy → 3-6 VI 更新),适合品牌升级。
4. **campaign-sprint**:营销创意冲刺(1/2 → 9 campaign),适合单次营销战役。

## 调用方式

- **单子技能调用**:直接调用某个子技能,如 `brand-creative/logo-design`。
- **Workflow 调用**:执行预定义 workflow,如 `brand-creative:full-brand-identity`。
- **自定义组合**:用户自建 workflow 组合子技能。

## 与共享决策库的关系

brand-creative 的子技能复用 I0 共享决策库(`knowledge/design/`):
- brand-strategy 复用 `design.strategy.brand-strategy-alignment`(M01)
- logo-design / color-system 复用 `design.visual.visual-translation`(M04 部分)
- brand-voice 复用 `design.persona.voice-and-behavior-boundary`
- content-strategy 复用 `design.ip.content-narrative`(M05 部分)
- brand-collateral 复用 `design.ip.brand-material-realization`(M06 部分)

## Baseline 范围(B0)

本批(B0)只建 Skill Group 架构基线,不开发全部子技能:
- ✅ GROUP.md(frontmatter 声明 13 子技能 + 4 workflows)
- ✅ knowledge-manifest.yaml(引用共享决策资产)
- ✅ workflows/*.yaml(4 个 workflow 草图)
- ✅ sub-skills/*/README.md(13 个占位 README)
- ✅ tests + release baseline
- ❌ 不开发任何子技能的 SKILL.md / pipeline.yaml / prompts

后续批次(B1/B2/...)按需开发子技能。**开发顺序**(开发并行不等于运行时并行,见 § 依赖关系):
- B1:brand-strategy(基础)
- B2:logo-design ∥ color-system ∥ typography-system(开发可并行,运行时都依赖 brand-strategy 产出)
- B3:visual-identity(开发与运行时都必须等待 B2 三者完成)

## 依赖关系:开发并行 ≠ 运行时依赖

两类关系必须区分:

**开发并行**:不同 Agent/团队基于冻结的输入输出契约可以并行开发子技能 SKILL.md/pipeline/prompts。
**运行时依赖**:子技能在 workflow 中执行时,下游必须等待真实上游产物。

| 子技能 | 开发可并行的对象 | 运行时上游(必须先完成) |
|--------|-----------------|----------------------|
| brand-strategy | competitive-analysis | competitive-analysis(可选;若用户已自带竞品矩阵则跳过) |
| competitive-analysis | brand-strategy | (无;仅依赖用户输入) |
| logo-design | color-system / typography-system | brand-strategy |
| color-system | logo-design / typography-system | brand-strategy |
| typography-system | logo-design / color-system | brand-strategy |
| **visual-identity** | (无平行子技能) | **logo-design + color-system + typography-system 三者全部完成** |
| brand-voice | content-strategy | brand-strategy |
| content-strategy | brand-voice | brand-strategy |
| campaign-creative | (无平行子技能) | visual-identity + brand-voice |
| brand-collateral | digital-assets | visual-identity |
| digital-assets | brand-collateral | visual-identity |
| brand-guidelines | (无平行子技能) | 几乎所有上游 |
| brand-audit | (任意,独立场景) | (无;独立子技能) |

**competitive-analysis 在 full-brand-identity / campaign-sprint 中的角色**:
- **开发并行**:与 brand-strategy 可并行开发(两者都基于用户输入契约,互不依赖契约定义)。
- **运行时依赖**(workflow 调用):
  - workflow 始终先运行 competitive-analysis,后运行 brand-strategy。
  - 用户已有 `competitor_matrix` 时,competitive-analysis 负责**验证、规范化和补充**(校验完整性 / 标准化字段 / 补充市场空白分析),不会跳过。
  - 用户未自带时,competitive-analysis 从用户业务输入产出 competitor_matrix。
  - 若 competitive-analysis 失败(`on_failure: continue`),brand-strategy 差异化标注 `[inferred]`。
  - **生产者(competitive-analysis)与消费者(brand-strategy)绝不放在同一 parallel step**。
- **直接调用 brand-strategy 子技能**:用户绕过 workflow 直接调用 brand-strategy 时,可使用已有 competitor_matrix,不要求先执行 competitive-analysis。

| 子技能调用方式 | competitive-analysis 行为 |
|---|---|
| `full-brand-identity` workflow | 始终先运行(验证/规范化/补充用户输入) |
| `campaign-sprint` workflow | 始终先运行(同上) |
| 直接调用 brand-strategy | 不强制要求,brand-strategy 可消费用户已有 competitor_matrix |
