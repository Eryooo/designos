# brand-creative 子技能分解与目录规划

> Batch B0 架构设计文档,不开发全部子技能,只建目录骨架。

## 1. 子技能分解逻辑

brand-creative Skill Group 覆盖**品牌创意全链路**,从策略到执行物料,对标 ip-design 但扩展到非 IP 品牌识别(logo / VI / 品牌手册 / 营销创意)。

**分解原则**:
- 每个子技能是独立 pipeline skill,可单独调用或组合。
- 子技能间有依赖关系(上游产出 → 下游输入),但尽量松耦合。
- 复用 I0 共享决策库(`knowledge/design/`),不重建方法论。

**13 个子技能** (按品牌创意链路):

### Phase 1: 策略与定位(2 个)
1. **brand-strategy**:品牌策略基线(定位/差异化/核心价值/人格关键词)。
   - 复用:`design.strategy.brand-strategy-alignment`(M01)
   - 输出:`brand_brief`

2. **competitive-analysis**:竞品分析(视觉风格/传播策略/市场空白)。
   - 输出:`competitor_matrix` / `market_gap_report`

### Phase 2: 视觉识别系统(4 个)
3. **logo-design**:Logo 设计(形态/色彩/辅助图形/应用规范)。
   - 复用:`design.visual.visual-translation`(部分,聚焦 logo)
   - 输出:`logo_spec` / `logo_prompt_pack`

4. **color-system**:品牌色彩系统(主色/辅色/色彩情绪/应用场景)。
   - 复用:`design.visual.visual-translation`(色彩部分)
   - 输出:`color_palette` / `color_usage_guide`

5. **typography-system**:字体系统(主字体/辅助字体/字号层级/排版规范)。
   - 输出:`typography_spec`

6. **visual-identity**:完整 VI 手册(logo / 色彩 / 字体 / 辅助图形 / 应用规范)。
   - 依赖:logo-design / color-system / typography-system
   - 输出:`vi_manual`

### Phase 3: 品牌内容与传播(3 个)
7. **brand-voice**:品牌声音(语调/口头禅/场景话术/内容原则)。
   - 复用:`design.persona.voice-and-behavior-boundary`
   - 输出:`brand_voice_guide`

8. **content-strategy**:内容策略(内容支柱/渠道矩阵/节奏日历)。
   - 复用:`design.ip.content-narrative`(部分)
   - 输出:`content_strategy`

9. **campaign-creative**:营销创意(campaign 主题/视觉方向/传播素材)。
   - 输出:`campaign_brief` / `creative_concepts`

### Phase 4: 物料与落地(4 个)
10. **brand-collateral**:品牌物料(名片/信头/包装/宣传册)。
    - 复用:`design.ip.brand-material-realization`(物料部分)
    - 输出:`collateral_spec`

11. **digital-assets**:数字资产(网站视觉/社交媒体模板/H5 规范)。
    - 输出:`digital_asset_kit`

12. **brand-guidelines**:完整品牌手册(策略/VI/声音/内容/物料)。
    - 依赖:所有上游子技能
    - 输出:`brand_guidelines`

13. **brand-audit**:品牌审计(当前品牌健康度/差距/优化建议)。
    - 输出:`brand_audit_report`

## 2. 目录结构规划

```
skills/brand-creative/
├── GROUP.md                          # Skill Group manifest
├── knowledge-manifest.yaml           # 引用 I0 共享决策资产
├── workflows/                        # 组合 workflow 定义
│   ├── full-brand-identity.yaml      # 完整品牌识别(1-12 全链路)
│   ├── logo-vi-fast-track.yaml       # Logo+VI 快速通道(3-6)
│   ├── brand-refresh.yaml            # 品牌焕新(audit → strategy → VI)
│   └── campaign-sprint.yaml          # 营销创意冲刺(strategy → campaign)
├── sub-skills/                       # 13 个子技能目录
│   ├── brand-strategy/               # 1. 品牌策略
│   │   ├── SKILL.md
│   │   ├── pipeline.yaml
│   │   ├── prompts/
│   │   └── tests/
│   ├── competitive-analysis/         # 2. 竞品分析
│   ├── logo-design/                  # 3. Logo 设计
│   ├── color-system/                 # 4. 色彩系统
│   ├── typography-system/            # 5. 字体系统
│   ├── visual-identity/              # 6. VI 手册
│   ├── brand-voice/                  # 7. 品牌声音
│   ├── content-strategy/             # 8. 内容策略
│   ├── campaign-creative/            # 9. 营销创意
│   ├── brand-collateral/             # 10. 品牌物料
│   ├── digital-assets/               # 11. 数字资产
│   ├── brand-guidelines/             # 12. 品牌手册
│   └── brand-audit/                  # 13. 品牌审计
├── tests/
│   └── test_brand_creative_group_structure.py
└── README.md
```

## 3. 子技能命名规范

- 全部用 kebab-case:brand-strategy / logo-design / brand-voice
- 避免缩写:用 typography-system 而非 typo-sys
- 对齐 OutputType:brand-strategy → brand_brief,logo-design → logo_spec

## 4. B0 批次范围

本批(B0)只建骨架,不开发全部 13 个子技能:
- ✅ 创建 `skills/brand-creative/GROUP.md`(frontmatter 声明 13 个子技能)
- ✅ 创建 `skills/brand-creative/knowledge-manifest.yaml`
- ✅ 创建 `skills/brand-creative/workflows/*.yaml`(4 个 workflow 草图)
- ✅ 创建 `skills/brand-creative/sub-skills/*/README.md`(13 个占位 README)
- ✅ 创建测试 + release baseline
- ❌ 不开发任何子技能的 SKILL.md / pipeline.yaml / prompts

后续批次(B1/B2/...)按需开发子技能,优先级:brand-strategy → logo-design → visual-identity。
