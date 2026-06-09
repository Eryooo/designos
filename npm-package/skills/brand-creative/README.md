# brand-creative — 品牌创意 Skill Group

> **状态**: B0 architecture baseline(仅骨架,子技能未开发)  
> **类型**: Skill Group(13 子技能 + 4 workflows)

## 快速开始

brand-creative 是品牌创意全链路 Skill Group,覆盖品牌策略/视觉识别/内容传播/物料落地。

### 调用方式

1. **执行预定义 workflow**:
   ```python
   # 完整品牌识别全链路
   await orchestrator.run_workflow("brand-creative", "full-brand-identity", ctx)
   
   # Logo+VI 快速通道
   await orchestrator.run_workflow("brand-creative", "logo-vi-fast-track", ctx)
   ```

2. **单子技能调用**(B1+ 开发后):
   ```python
   # 只执行品牌策略
   result = await group.run_sub_skill("brand-strategy", ctx)
   ```

## 13 个子技能

| Phase | 子技能 | 状态 | 产出 |
|-------|--------|------|------|
| **策略** | brand-strategy | 🔲 占位 | brand_brief |
| | competitive-analysis | 🔲 占位 | competitor_matrix |
| **视觉** | logo-design | 🔲 占位 | logo_spec |
| | color-system | 🔲 占位 | color_palette |
| | typography-system | 🔲 占位 | typography_spec |
| | visual-identity | 🔲 占位 | vi_manual |
| **内容** | brand-voice | 🔲 占位 | brand_voice_guide |
| | content-strategy | 🔲 占位 | content_strategy |
| | campaign-creative | 🔲 占位 | campaign_brief |
| **物料** | brand-collateral | 🔲 占位 | collateral_spec |
| | digital-assets | 🔲 占位 | digital_asset_kit |
| | brand-guidelines | 🔲 占位 | brand_guidelines |
| | brand-audit | 🔲 占位 | brand_audit_report |

## 4 个预定义 workflow

1. **full-brand-identity**:完整品牌识别(策略 → VI → 内容 → 物料 → 手册),适合从零建立品牌。
2. **logo-vi-fast-track**:Logo+VI 快速通道(仅视觉识别),适合已有策略只需视觉执行。
3. **brand-refresh**:品牌焕新(审计 → 策略 → VI 更新),适合品牌升级。
4. **campaign-sprint**:营销创意冲刺(策略 → campaign),适合单次营销战役。

详见 `workflows/*.yaml`。

## 与 ip-design 的关系

- **ip-design**(单 skill):聚焦 IP 角色设计(人格化 IP,如吉祥物),产出 IP 世界观/人格/视觉。
- **brand-creative**(Skill Group):覆盖品牌识别系统(logo / VI / 品牌手册),更广但更浅(无 IP 人格/世界观)。

两者可组合:品牌先用 brand-creative 建立 VI,再用 ip-design 设计品牌 IP。

## 开发状态

**B0**(当前):Skill Group 架构基线,仅骨架(GROUP.md + workflows + 13 占位 README + tests)。

**B1**(计划):开发核心 MVP 三子技能(brand-strategy → logo-design → visual-identity),打通最小链路。

**B2+**(计划):按需开发剩余子技能(color-system / typography-system / brand-voice / content-strategy / ...)。

## 文档

- 架构设计:`docs/releases/brand-creative-baseline/README.md`
- 子技能分解:`sub-skills-design.md`
- 知识资产引用:`knowledge-manifest.yaml`
- 测试:`tests/test_brand_creative_group_structure.py`(10 passed)

## 开发路线图

推荐子技能开发顺序(开发并行 ≠ 运行时依赖,见 GROUP.md § 依赖关系):

**B1(策略基础)**:
- brand-strategy

**B2(视觉基础,可与 B1 并行基于冻结契约)**:
- logo-design ∥ color-system ∥ typography-system

**B3(视觉汇总,必须等待 B2 全部完成)**:
- visual-identity

**B4(内容层,可与 B2 并行)**:
- brand-voice ∥ content-strategy

**B5(物料层,必须等待 B3)**:
- brand-collateral ∥ digital-assets

**B6(汇总,必须等待前置全部)**:
- brand-guidelines

**B7(扩展,独立)**:
- competitive-analysis / campaign-creative / brand-audit

详见 `docs/releases/brand-creative-baseline/README.md` § 并行开发边界。
