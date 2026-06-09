# brand-creative Skill Group Architecture Baseline (B0)

**批次**: B0  
**日期**: 2026-06-02  
**分支**: skills-pilot-wave2  
**范围**: Skill Group 架构基线,不开发全部子技能,只建骨架

---

## 1. 产品视角

### 1.1 Skill Group 定位

brand-creative 是 **品牌创意全链路 Skill Group**,覆盖:
- **Phase 1 策略与定位**:品牌策略/竞品分析
- **Phase 2 视觉识别系统**:Logo/色彩/字体/VI 手册
- **Phase 3 品牌内容与传播**:品牌声音/内容策略/营销创意
- **Phase 4 物料与落地**:品牌物料/数字资产/品牌手册/品牌审计

与 ip-design 的关系:
- **ip-design**(单 skill):聚焦 **IP 角色设计**(人格化 IP,如吉祥物/虚拟代言人),产出 IP 世界观/人格/视觉/内容/物料。深度聚焦,单技能。
- **brand-creative**(Skill Group):覆盖 **品牌识别系统**(logo / VI / 品牌手册 / 营销创意),更广但更浅(无 IP 人格建模/世界观)。广度组合,Skill Group。

两者可组合:品牌先用 brand-creative 建立 VI,再用 ip-design 设计品牌 IP。

### 1.2 13 个子技能

| Phase | 子技能 | 产出 | 复用共享决策 |
|-------|--------|------|-------------|
| **Phase 1 策略** | brand-strategy | brand_brief | design.strategy.brand-strategy-alignment |
| | competitive-analysis | competitor_matrix | design.strategy.* |
| **Phase 2 视觉** | logo-design | logo_spec | design.visual.visual-translation + (B1 需补 logo-design-methodology) |
| | color-system | color_palette | design.visual.visual-translation |
| | typography-system | typography_spec | (B1 需补 typography-system-methodology) |
| | visual-identity | vi_manual | design.visual.* + design.quality.* |
| **Phase 3 内容** | brand-voice | brand_voice_guide | design.persona.voice-and-behavior-boundary |
| | content-strategy | content_strategy | design.ip.content-narrative |
| | campaign-creative | campaign_brief | design.ip.content-narrative + design.visual.image-prompt-system |
| **Phase 4 物料** | brand-collateral | collateral_spec | design.ip.brand-material-realization |
| | digital-assets | digital_asset_kit | design.ip.brand-material-realization + design.visual.image-prompt-system |
| | brand-guidelines | brand_guidelines | design.ip.brand-material-realization + design.quality.* |
| | brand-audit | brand_audit_report | (B1 需补 brand-audit-methodology) |

### 1.3 4 个预定义 workflow

1. **full-brand-identity**:完整品牌识别全链路(1 → 2 → 3-6 → 7-9 → 10-12),适合从零建立品牌。
2. **logo-vi-fast-track**:Logo+VI 快速通道(仅 3-6),适合已有策略只需视觉执行。
3. **brand-refresh**:品牌焕新(13 audit → 1 strategy → 3-6 VI 更新),适合品牌升级。
4. **campaign-sprint**:营销创意冲刺(1/2 → 9 campaign),适合单次营销战役。

---

## 2. 并行开发边界(核心交付)

### 2.1 主线程串行子技能(必须顺序开发)

这些子技能 **汇总上游产出**,必须在依赖项完成后开发:

1. **visual-identity**(VI 手册):
   - 依赖:`logo-design` + `color-system` + `typography-system`
   - 原因:汇总三者产出为完整 VI 手册。
   - 开发顺序:先完成 logo/color/typography,再开发 visual-identity。

2. **campaign-creative**(营销创意):
   - 依赖:`visual-identity` + `brand-voice`
   - 原因:campaign 视觉方向依赖 VI,传播话术依赖 brand-voice。
   - 开发顺序:先完成 visual-identity + brand-voice,再开发 campaign-creative。

3. **brand-guidelines**(完整品牌手册):
   - 依赖:几乎所有上游子技能(brand-strategy / visual-identity / brand-voice / content-strategy / brand-collateral / digital-assets)
   - 原因:最终汇总交付物。
   - 开发顺序:最后开发,前置子技能完成后。

### 2.2 可并行开发子技能(同批次并行)

这些子技能 **开发可并行**(基于冻结的输入输出契约),但 **运行时依赖关系不同**:

**批次 B1-P1**(Phase 1 策略):
- `brand-strategy` ∥ `competitive-analysis`
- 开发可并行(两者都只依赖用户输入契约)。
- 运行时:**workflow 始终先运行 competitive-analysis,后运行 brand-strategy**。
  - 用户已有 competitor_matrix 时,competitive-analysis 负责**验证、规范化和补充**,不跳过。
  - 用户未自带时,competitive-analysis 从用户业务输入产出 competitor_matrix。
  - 用户直接调用 brand-strategy 子技能(绕过 workflow)时,可使用已有 competitor_matrix,不强制要求先执行 competitive-analysis。
  - **生产者与消费者绝不放在同一 parallel step**。

**批次 B1-P2**(Phase 2 视觉基础):
- `logo-design` ∥ `color-system` ∥ `typography-system`
- 开发可并行(三者都依赖 brand-strategy 输出契约,但互不依赖)。
- 运行时:三者都必须等待 brand-strategy 完成产出 brand_brief,然后三路并行执行。

**批次 B1-P3**(Phase 3 内容基础):
- `brand-voice` ∥ `content-strategy`
- 开发可并行(两者都依赖 brand-strategy 输出契约,但互不依赖)。
- 运行时:两者都必须等待 brand-strategy 完成。

**批次 B1-P4**(Phase 4 物料基础):
- `brand-collateral` ∥ `digital-assets`
- 开发可并行(两者都依赖 visual-identity 输出契约,但互不依赖)。
- 运行时:两者都必须等待 visual-identity 完成。

**独立子技能**(不在主链路):
- `brand-audit`:可独立开发(brand-refresh workflow 中先行串行,但本身无依赖)。

### 2.3 并行开发建议路线图

**开发优先级**(开发并行 ≠ 运行时依赖):
1. **B1 策略层**:brand-strategy(基础子技能,后续全依赖)
2. **B2 视觉基础**(可与 B1 并行开发,基于冻结契约):logo-design ∥ color-system ∥ typography-system
3. **B3 视觉汇总**(必须等待 B2 开发完成):visual-identity
4. **B4 内容层**(可与 B2 并行开发):brand-voice ∥ content-strategy
5. **B5 物料层**(必须等待 B3 开发完成):brand-collateral ∥ digital-assets
6. **B6 汇总**(必须等待前置全部):brand-guidelines
7. **B7 扩展**(独立):competitive-analysis / campaign-creative / brand-audit

**错误路线**(已删除):**不存在** "brand-strategy → logo-design → visual-identity" 这样的三子技能串行 MVP。正确依赖是:brand-strategy → (logo-design ∥ color-system ∥ typography-system) → visual-identity,visual-identity **必须等待三者全部完成**,不能只依赖 logo-design。

推荐 B1 先开发 **brand-strategy**,然后 B2 开发 **logo-design ∥ color-system ∥ typography-system**(三路并行或按需串行),然后 B3 开发 **visual-identity**(汇总三者),打通最小 VI 链路,验证 Skill Group 调度与 workflow 编排。

---

## 3. 技术实现

### 3.1 新增文件清单

```
skills/brand-creative/
├── GROUP.md                          # Skill Group manifest(13 子技能 + 4 workflows)
├── knowledge-manifest.yaml           # 引用 I0 共享决策资产
├── sub-skills-design.md              # 子技能分解文档(本批设计,非产品代码)
├── workflows/                        # 4 个预定义 workflow
│   ├── full-brand-identity.yaml      # 完整品牌识别全链路
│   ├── logo-vi-fast-track.yaml       # Logo+VI 快速通道
│   ├── brand-refresh.yaml            # 品牌焕新
│   └── campaign-sprint.yaml          # 营销创意冲刺
├── sub-skills/                       # 13 个子技能占位目录
│   ├── brand-strategy/README.md
│   ├── competitive-analysis/README.md
│   ├── logo-design/README.md
│   ├── color-system/README.md
│   ├── typography-system/README.md
│   ├── visual-identity/README.md
│   ├── brand-voice/README.md
│   ├── content-strategy/README.md
│   ├── campaign-creative/README.md
│   ├── brand-collateral/README.md
│   ├── digital-assets/README.md
│   ├── brand-guidelines/README.md
│   └── brand-audit/README.md
├── tests/
│   └── test_brand_creative_group_structure.py  # 10 个测试锁定架构契约
└── README.md(可选)
```

### 3.2 kernel Skill Group 支持

kernel 已有完整 Skill Group 支持(`kernel/skill_loader/group_loader.py`),本批无需改 kernel:
- `load_skill_group()`:加载 GROUP.md + workflows
- `SkillGroup.list_sub_skills()`:列出子技能
- `SkillGroup.get_workflow()`:获取 workflow 定义
- `SkillGroup.run_sub_skill()`:懒加载并执行子技能
- WorkflowConfig / WorkflowStep 原生支持 `type: sequential|parallel`

### 3.3 Workflow 并行边界(技术)

4 个 workflow yaml 声明运行时依赖,kernel 在运行时调度。注意:生产者与消费者绝不放在同一 parallel step。

**full-brand-identity**(始终串行先行 + 3 个并行点):
1. Phase 1a:`competitive-analysis`(始终串行先行;有用户输入则验证/规范化/补充,无则从零分析)
2. Phase 1b:`brand-strategy`(串行,消费 competitor_matrix)
3. Phase 2 基础:`logo-design` ∥ `color-system` ∥ `typography-system`(并行)
4. Phase 2 汇总:`visual-identity`(串行,依赖上一并行组三者全部完成)
5. Phase 3 基础:`brand-voice` ∥ `content-strategy`(并行)
6. Phase 3 创意:`campaign-creative`(串行,依赖 visual-identity + brand-voice)
7. Phase 4 物料:`brand-collateral` ∥ `digital-assets`(并行)
8. Phase 4 手册:`brand-guidelines`(串行,汇总所有)

**logo-vi-fast-track**(最简单,1 个并行点):
1. `logo-design` ∥ `color-system` ∥ `typography-system`(并行)
2. `visual-identity`(串行汇总,依赖三者全部完成)

**brand-refresh**(审计驱动,1 个并行点):
1. `brand-audit`(串行先行)
2. `brand-strategy`(串行,依赖审计结论)
3. `logo-design` ∥ `color-system` ∥ `typography-system`(并行,VI 更新)
4. `visual-identity`(串行汇总,依赖三者全部完成)

**campaign-sprint**(始终串行):
1. `competitive-analysis`(始终串行先行)
2. `brand-strategy`(串行,消费 competitor_matrix)
3. `campaign-creative`(串行,依赖策略)
4. `digital-assets`(串行,依赖 campaign)

### 3.4 测试覆盖

10 个测试锁定架构契约:
1. GROUP.md 存在且 type=group
2. 声明 13 个子技能,id 正确
3. 声明 4 个 workflow
4. 13 个子技能目录存在且有占位 README
5. 子技能 path 可解析
6. 4 个 workflow yaml 存在且结构合法(name/description/steps)
7. workflow 引用的 sub_skills 都在声明内
8. knowledge-manifest 引用的 shared id 都存在
9. **kernel 能加载这个 Skill Group**(load_skill_group 不报错)
10. **并行 step 内的子技能互不依赖**(汇总型子技能不与其依赖项同 parallel step)

---

## 4. 验证结果

```bash
# 测试
$ python3 -m pytest -q skills/brand-creative/tests/
10 passed in 0.73s

# kernel 加载验证(测试 9 已覆盖)
from kernel.skill_loader.group_loader import load_skill_group
group = load_skill_group("skills/brand-creative")
assert group.name == "brand-creative"
assert len(group.list_sub_skills()) == 13
assert group.get_workflow("full-brand-identity") is not None
```

---

## 5. 后续批次

### B1:核心 MVP 三子技能
- brand-strategy / logo-design / visual-identity
- 打通策略 → Logo → VI 最小链路,验证 Skill Group 调度
- 需补知识资产:`design.visual.logo-design-methodology`

### B2:视觉系统扩展
- color-system / typography-system(可与 B1 logo-design 并行)
- 需补知识资产:`design.visual.typography-system-methodology`

### B3+:按需开发剩余子技能
- 优先级:content-strategy > brand-voice > campaign-creative > brand-collateral > digital-assets > brand-guidelines
- brand-audit 独立(焕新场景)

---

## 6. 关键决策

1. **为何 Skill Group 而非单 skill**:brand-creative 覆盖 13 个子场景,每个子技能独立可用(如"只要 Logo 设计"),Skill Group 提供灵活组合,避免单 skill 臃肿。

2. **为何只建骨架不开发全部子技能**:13 个子技能全开发成本高(每个约 2-3 批次工作量),B0 先建架构骨架,验证 Skill Group 调度与 workflow 编排可行性,再按需增量开发子技能。

3. **并行边界为何如此设计**:遵循品牌创意实际依赖关系:策略是基础(串行先行),视觉三要素(logo/color/typography)无依赖(并行),VI 汇总三者(串行后行),物料依赖 VI(并行),手册汇总全部(串行最后)。workflow yaml 的 sequential/parallel 直接映射这些依赖。

4. **为何部分子技能需补知识资产**:logo-design / typography-system / brand-audit 有独立于 IP 设计的方法论(商标查重/字体授权/品牌健康度评估),I0 共享决策库未覆盖,B1+ 开发这些子技能前需先补知识资产,或在子技能内内置方法论(后者不推荐,违反共享决策库原则)。

---

**B0 完成标志**:GROUP.md + 4 workflows + 13 占位 README + knowledge-manifest + tests 10 passed + kernel 能加载。✅
