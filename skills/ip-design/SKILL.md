---
skill: ip-design
name: IP Design
version: 0.1.0-pilot
type: pipeline
archetype: creative-generation
status: pilot
description: 品牌 IP 设计六阶段生成流水线,消费 DesignOS 共享设计决策库,产出结构化 IP 资产
requires:
  kernel: ">=1.0.0,<2.0.0"
outputs:
  - type: brand_brief
    description: 品牌策略基线(北极星/人格关键词/差异化)
  - type: worldview
    description: IP 世界观(时空/规则/关系网/文化原型)
  - type: persona_profile
    description: IP 人格档案(行为模式/动机恐惧/成长弧/声音边界)
  - type: visual_spec
    description: 视觉系统规范(形态/色彩/识别度/状态/风格坐标/禁忌)
  - type: image_prompt_pack
    description: AI 绘图提示词包(四层结构+负向+跨平台)
  - type: content_plan
    description: 内容规划(首秀/核心事件/语料/矩阵/节奏)
  - type: brand_material_spec
    description: 物料落地规格(应用规范/衍生品/宣传物料/传播指南/生产清单)
  - type: professional_gap_report
    description: 专业 gap 报告(九维 rubric 自评/失败模式自检/gap 清单)
---

# ip-design — 品牌 IP 设计 Skill

> creative-generation 型 skill,消费 DesignOS 共享设计决策库,产出结构化 IP 设计资产。

## 定位与边界

ip-design 是一个 **pilot 级品牌 IP 设计 skill**,目标:让 AI 按 DesignOS 共享设计决策库(`knowledge/design/`)产出的 IP 方案,至少替代中低阶设计师,并达到高阶设计师"可评审/可进真实项目讨论"的质量基线。

**它能做什么:**
- 六阶段结构化 IP 设计:策略对齐 → 世界观构建 → 人格建模 → 视觉转化 → 内容规划 → 物料落地。
- 产出 7 类结构化资产:brand_brief / worldview / persona_profile / visual_spec / content_plan / brand_material_spec / image_prompt_pack。
- 每阶段应用共享方法论(M01–M06)的决策框架、专家启发式、质量 rubric、失败模式自检。
- 输出跨平台 AI 绘图提示词包(四层结构 + 负向控制),但**不调用图像生成 API**。
- 识别输入不足时输出 gaps,不脑补。

**它不能做什么(pilot 边界):**
- ❌ 不调用图像生成 API,不产出最终视觉图像;只输出提示词包供设计师使用。
- ❌ 不替代法务、商标/版权审查、真实用户研究。
- ❌ 不声明产出即可交付最终商用 Logo、VI、版权清洁 IP 形象;需资深设计师定稿与法务确认。
- ❌ 不自动执行印刷打样、代工厂询价、Pantone 色彩确认。
- ❌ 人格建模不替代心理学专业人格测评;MBTI 仅作辅助沟通语言。

## 核心产出

| 产出物 | 类型 | 产出阶段 | 用途 |
|-------|------|----------|------|
| brand_brief | YAML | strategy-alignment | M01 策略对齐,含北极星/用户画像/核心价值/人格词/差异化 |
| worldview | YAML | worldview-building | M02 世界观,含时空/规则/关系/文化原型/关键词 |
| persona_profile | YAML | persona-modeling | M03 人格档案,含行为模式/MBTI 辅助/动机恐惧/成长弧/声音边界 |
| visual_spec | YAML | visual-translation | M04 视觉规范,含基因继承/形态/色彩/识别度/状态延展/风格坐标/禁忌 |
| content_plan | YAML | narrative-planning | M05 内容规划,含首秀/核心事件/语料/矩阵/节奏 |
| brand_material_spec | YAML | landing-spec | M06 物料规格,含应用规范/衍生品/宣传物料/传播指南/生产清单 |
| image_prompt_pack | YAML | visual-translation | 跨平台 AI 绘图提示词包(基准图 + 三视图 + 状态图),四层结构 + 负向 |

## 质量承诺

- 每个产出物都对照共享质量 rubric 自评(九维)与失败模式自检。
- 阶段放行前过必过项清单;不过的要么返工要么写入 gap。
- 不达中阶的维度必须写入 professional gap report,显式标注临时放行边界。
- **不允许假装完成。**

## 与共享决策库的关系

本 skill 的 `knowledge-manifest.yaml` 引用 22 个共享设计决策资产 id:
- 8 个方法论(总纲 + M01–M06)
- 4 个质量门槛(rubric / checklists / failure-modes / gap-report)
- 6 个模板(brand-brief / worldview / persona-profile / visual-spec / content-plan / brand-material-spec)
- 合成案例（synthetic case；待在 `eval/golden-cases/` 下补充，不含真实项目证据）

私有 `reference/adapter-*.md` 只描述"本 skill 在自己 pipeline 的某 stage 如何应用某共享 id",**不复制共享正文**。决策内容的 source of truth 在 `knowledge/design/`,本 skill 只消费。

## 输入要求

必须输入:
- 产品/服务定义、业务目标。
- 目标用户描述(职业、场景、痛点);缺失或推断处会标注 `[inferred]` 并写入 gaps。
- 竞品 IP 信息(≥3 个),用于差异化。

可选输入:
- 既有品牌资产(主色/logo/字体/符号),用于基因继承;若是新品牌则跳过继承环节。
- 文化原型偏好、性格倾向、色彩气质偏好;缺失时按北极星推断并标注。

## 运行模式

本 pilot 无 mode 切换,固定走完六阶段。后续版本可按需增加"快速 brief 模式"或"仅视觉深化模式"。

## 验证与测试

```bash
cd .factory
python3 -m tools.validate ../skills/ip-design --archetype generation

cd ..
python3 -m pytest -q skills/ip-design/tests/
```

## 引用规范

使用本 skill 产出时:
- 必须附 professional gap report,向品牌方/设计师说明已知短板与临时放行边界。
- 视觉产出(visual_spec + image_prompt_pack)需资深设计师评审与微调,不可直接作为最终商用资产。
- 印刷物料(brand_material_spec)需打样验证 CMYK/Pantone 色彩,不可直接下印。
- 法务/商标/版权风险需专业机构审查,本 skill 只标注潜在风险信号。
