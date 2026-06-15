# Golden Output Template — ip-design

> **🚫 SYNTHETIC / SANITIZED ONLY** — 本模板及示例片段不含任何真实品牌、真实 IP、真实客户、真实商标。所有示例都用 `Acme Demo IP` / `synthetic-mascot-001` 等明显假名占位。
> **本模板性质**:IP 设计输出规范,"中阶可用 + 资深目标"双层基准。
> **依据**:S2-H1 §2.4(ip-design rubric)+ S2-H1.1 §6.2.4(KR-I1~I5)+ `skills/ip-design/constitution.md`(8 条硬约束)+ `knowledge/design/quality/{ip-design-quality-rubric, common-failure-modes, stage-review-checklists, professional-gap-report}.md`。
> **当前状态**:**maturity = pilot**;**prompt-grade,无 runtime/ 目录**;9 维 rubric 自评待真实 LLM 链路实测。
> **特殊性**:本 skill 是 5 个 skill 中**唯一已具备完整 quality 四件套**(rubric + failure-modes + checklists + gap report),其他 skill 应对标。

---

## 1. 输入前提

| 输入 | 强制 / 可选 | 说明 |
|---|---|---|
| 产品 / 服务定义 | 强制 | 产品/服务的定位、目标用户、业务目标 |
| 目标用户描述 | 强制 | 职业、场景、痛点(synthetic / sanitized) |
| 竞品 IP 信息 | 强制 | ≥ 3 个竞品 IP 的 sanitized 描述,用于差异化 |
| 既有品牌资产 | 可选 | 主色/logo/字体/符号(sanitized);若是新品牌则跳过基因继承 |
| 文化原型 / 性格倾向 / 色彩气质偏好 | 可选 | 缺失时按北极星推断并标 `[inferred]` |

---

## 2. 输出目录结构 / Artifact 列表

按 6 阶段顺序产出:

```
ip-design-out/<run_id>/
├── 01-brand_brief.yaml              # M01 strategy-alignment
├── 02-worldview.yaml                # M02 worldview-building
├── 03-persona_profile.yaml          # M03 persona-modeling
├── 04-visual_spec.yaml              # M04 visual-translation
├── 05-image_prompt_pack.yaml        # M04 配套(跨平台 AI 绘图提示词)
├── 06-content_plan.yaml             # M05 narrative-planning
├── 07-brand_material_spec.yaml      # M06 landing-spec
└── professional_gap_report.yaml     # 必附诚实声明书
```

---

## 3. 必填章节(每个 artifact)

### 3.1 brand_brief 必填字段
```yaml
brand_brief:
  project: <synthetic 项目代号>
  north_star: <一句话品牌北极星>
  target_audience: {primary: ..., secondary: ...}
  core_values: [...]
  personality_keywords: [...]   # ≥ 3 个
  differentiation:
    statement: <差异化定位>
    rationale: <基于竞品空白的依据>
    evidence_refs: [...]        # 必须可追溯到竞品 IP 信息
```

### 3.2 visual_spec 必填字段(constitution #6/#7)
```yaml
visual_spec:
  inheritance:                  # 三栏:继承 / 调整 / 新增
    inherited: [...]
    adjusted: [...]
    new: [...]
  form_language: ...
  color_system:
    primary: "#XXXXXX"          # 必须 hex 十六进制
    secondary: [...]
    contrast_check: WCAG_AA     # ≥ 4.5:1
  recognition_test:
    at_32px: <可辨/糊/不可辨>
    at_silhouette: <可辨/糊/不可辨>
  state_extension: [default, hover, disabled, ...]
  style_quadrant: <风格坐标>
  strict_avoidance: [...]       # ≥ 5 条严格禁忌(KR-I3 必填)
```

### 3.3 image_prompt_pack 必填字段(constitution #6)

四层结构 + 负向控制(KR-I3 硬约束):
```yaml
image_prompt_pack:
  layer_1_core_symbol_position: ...
  layer_2_design_concept: ...
  layer_3_technical_params: {style, lighting, composition}
  layer_4_quality_and_avoidance:
    positive: [...]
    negative_prompt: [...]      # ❗ 必填非空(SD)
    midjourney_no: [...]        # ❗ 必填非空(MJ --no)
  cross_platform_consistency: <语义等价性检查>
```

---

## 4. 字段级要求

### 4.1 9 维 rubric 自评(KR-I1)
- 每个产物必须含 `rubric_self_eval` 段,9 维全自评
- 维度:D1 品牌一致性 / D2 差异化 / D3 可延展性 / D4 识别度 / D5 落地成本 / D6 法务/合规 / D7 提示词可控性 / D8 人格立体度 / D9 跨阶段证据
- 每维 4 档:`高阶可评审 / 中阶可用 / 低阶仅雏形 / 不合格`

### 4.2 一票否决项(KR-I2)
- D2 差异化 / D6 法务 / D8 人格立体度 任一不合格 → **整方案不合格**
- 视觉先行(constitution #1):先画图后反推策略 → **整方案返工**

### 4.3 negative_prompt(KR-I3)
- `image_prompt_pack` 必填 ≥ 5 条 negative_prompt
- 必须与 `visual_spec.strict_avoidance` 同步

### 4.4 [inferred] 标注(KR-I5)
- 关键决策(北极星 / 人格关键词 / 主形选择 / 色彩配比)的 [inferred] 比例 ≥ 90%
- 推断依据写入 `inferences[]` 列表(constitution #2)

### 4.5 professional_gap_report 必含(KR-I4)
- 9 维 rubric 自评 + 失败模式自检 + gap 清单 + 临时放行边界

---

## 5. 最低线标准(中阶可用 — KR-I1~I5)

| KR | 要求 |
|---|---|
| KR-I1 | 9 维 rubric 自评中阶可用以上 ≥ 7/9 |
| KR-I2 | 一票否决项(D2/D6/D8 + 视觉先行)命中数 = 0 |
| KR-I3 | image_prompt_pack 含 negative_prompt 率 = 100% |
| KR-I4 | professional_gap_report 完整生成率 = 100% |
| KR-I5 | 关键决策 `[inferred]` 标注覆盖率 ≥ 90% |

---

## 6. 目标线标准(资深可评审)

- **9 维全到中阶可用以上**(KR-I1 目标线 9/9)
- 至少 3 维到 **高阶可评审**(资深愿评审/微调)
- **跨阶段关键词链路**无漂移(D9 高阶):北极星 → 人格词 → 视觉关键词 → 传播语调 环环相扣
- **核心符号 32px 可辨**(D4 高阶)+ 远观凭轮廓认出
- **衍生品工艺、印刷成本可控**(D5 高阶):有首批清单
- **关键决策 `[inferred]` 100% 覆盖**(KR-I5 目标线)

---

## 7. 一票否决项检查表(V1-V4)

| # | 检查 | 触发条件 | 来源 |
|---|---|---|---|
| **V1** D2 差异化 | 差异化靠贬低/自夸,或与竞品高度重叠 | rubric D2 不合格 → 整方案返工 |
| **V2** D6 法务/合规 | 核心符号有未标注的潜在商标/版权风险,或敏感映射 | rubric D6 不合格 → 整方案返工 |
| **V3** D8 人格立体度 | 仅有 MBTI 标签或口头禅,无行为模式 / 动机 / 恐惧 / 成长弧 | rubric D8 不合格 → 整方案返工 |
| **V4** 视觉先行 | 先画图后反推策略 | constitution #1 → 整方案返工 |

---

## 8. Gap / Assumption / Confidence / Traceability 规范

| 字段 | 规范 |
|---|---|
| `gaps[]` | 数据缺口 / 用户研究不足 / 法务待确认 等明确记录 |
| `inferences[]` | 推断决策 + rationale + evidence_refs(constitution #2) |
| `confidence` | 9 维 rubric 自评的加权平均(D2/D6/D8 一票否决项权重 ×3) |
| `traceability` | 每阶段决策可追溯到:① 上一阶段产物 ② 共享方法论 ID(`design.ip.*` / `design.persona.*` / `design.visual.*`)③ 用户/竞品输入条目 |

---

## 9. 自评表(对账 KR)

```yaml
self_eval:
  KR-I1_rubric_mid_or_above:
    actual: <9 维中 ≥ 中阶可用 的维度数>
    target: ≥ 7/9 (最低), 9/9 (目标)
    pass: <bool>
  KR-I2_one_strike_count:
    actual: <D2/D6/D8/视觉先行 不合格触发数>
    target: = 0
    pass: <bool>
  KR-I3_negative_prompt_coverage:
    actual: <含 negative_prompt 的 image_prompt_pack 数 / 总数>
    target: 100%
    pass: <bool>
  KR-I4_gap_report_completion:
    actual: <gap report 完整生成率>
    target: 100%
    pass: <bool>
  KR-I5_inferred_annotation:
    actual: <关键决策标 [inferred] 数 / 应标推断决策数>
    target: ≥ 90%
    pass: <bool>
  global_KR1.1_minimum_delivery:
    pass: <KR-I1~I4 是否全过最低线>
  global_KR1.2_one_strike_count:
    pass: <V1~V4 是否全为 0>
  global_KR3.2_gap_annotation:
    pass: <inferences/gaps 是否显式>
```

---

## 10. 禁止声明清单

- ❌ "自动生成商用 Logo"
- ❌ "替代资深设计师终审"
- ❌ "本产出已完成商标审查"
- ❌ "可直接印刷 / 可直接发布"
- ❌ "已通过真实商业项目验证"(若无真实 case)
- ❌ "已达资深 IP 设计师水平"
- ❌ "production ready" / "fully automated" / "完全自动化"

允许声明:

- ✅ "六阶段结构化 IP 设计,产出 7 类资产"
- ✅ "至少替代中低阶设计师,达高阶可评审基线(rubric 9 维 × 4 档)"
- ✅ "提示词包跨平台 + 含负向控制"
- ✅ "中阶设计师可接手微调"
- ✅ "合成 case 验证(synthetic case)"

---

## 11. Synthetic 示例片段(中阶可用档,sanitized only)

> ⚠️ 所有数据为 synthetic;占位符:`Acme Demo IP`(假项目)、`synthetic-mascot-001`(假 IP 名)、`#A8C5FF`(假色值)。

### 11.1 brand_brief 中阶可用档示例

```yaml
brand_brief:
  project: "Acme Demo Cloud Service IP"
  north_star: "[synthetic] 让 IT 管理员感到'有个可靠伙伴在帮我看着'"
  target_audience:
    primary: "小型企业 IT 管理员(参考 ai-analytics 上游 design_strategy)"
    secondary: "DevOps 工程师"
  core_values:
    - "可靠"
    - "省心"
    - "技术专业但不冷漠"
  personality_keywords: ["稳重", "细心", "略带技术感"]
  differentiation:
    statement: "[synthetic] 不做'酷炫科幻 AI'(竞品 A 路线),也不做'呆萌客服'(竞品 B 路线),做'值得信赖的资深运维伙伴'"
    rationale: "竞品 IP 集中在两端(高科技 vs 萌系),中段'专业可靠'有空白"
    evidence_refs: [
      "competitive-research.md#competitor-A-style",
      "competitive-research.md#competitor-B-style"
    ]
  confidence: 0.70
  inferences:
    - field: "personality_keywords"
      value: "[inferred] 基于 north_star + 用户痛点(小团队需要可靠感)推断"
      rationale: "无真实用户测试数据"
```

### 11.2 visual_spec rubric 自评片段(中阶可用档)

```yaml
visual_spec:
  rubric_self_eval:
    D1_brand_consistency:
      tier: "中阶可用"
      rationale: "[synthetic] 主线一致(稳重 → 蓝色调 + 圆角)但部分细节关键词漂移"
    D2_differentiation:
      tier: "中阶可用"
      rationale: "[synthetic] 差异化基于'专业可靠'而非贬低,但描述偏抽象"
    D3_extensibility:
      tier: "中阶可用"
      rationale: "核心符号可在 3 状态延展,小尺寸偶有跑偏"
    D4_recognition:
      tier: "中阶可用"
      rationale: "32px 下可辨,但在远观中与竞品 B 略有撞色"
    D5_landing_cost:
      tier: "中阶可用"
      rationale: "印刷工艺可控,但 SVG 路径过多需简化"
    D6_legal_compliance:
      tier: "中阶可用(待法务确认)"   # ← 不打高阶,因 D6 一票否决敏感
      rationale: "[synthetic] 核心符号无明显商标信号,但需法务确认"
    D7_prompt_controllability:
      tier: "中阶可用"
      rationale: "四层结构齐全,负向 prompt 5 条;部分参数未量化"
    D8_persona_depth:
      tier: "中阶可用"
      rationale: "行为模式 + 动机已建,但成长弧偏单薄"
    D9_cross_stage_evidence:
      tier: "中阶可用"
      rationale: "多数有依据,部分跨阶段关键词推断处已标 [inferred]"
  
  one_strike_check:
    D2_status: "中阶可用 ✅(未触发)"
    D6_status: "中阶可用(待法务确认) ✅(未触发不合格)"
    D8_status: "中阶可用 ✅"
    visual_first_violation: false
```

### 11.3 image_prompt_pack 中阶可用档示例

```yaml
image_prompt_pack:
  layer_1_core_symbol_position:
    description: "[synthetic] 拟人化的'守护者'形象,中等身高,蓝灰色调"
  layer_2_design_concept:
    keywords: ["reliable", "professional but warm", "tech-savvy guardian"]
  layer_3_technical_params:
    style: "modern flat illustration, soft shadow"
    lighting: "even, slightly warm"
    composition: "front-facing, centered"
  layer_4_quality_and_avoidance:
    positive:
      - "clean lines"
      - "consistent color palette (#A8C5FF, #2C3E50)"
    negative_prompt:
      - "scary expression"
      - "robotic / metallic"
      - "cute mascot style (avoid competitor B path)"
      - "complex background"
      - "text or logo elements"
    midjourney_no:
      - "scary, robotic, cute mascot, complex background, text, logo"
  cross_platform_consistency:
    sd_vs_mj_check: "✅ 关键描述语义等价(已抽测 3 个 prompt)"
```

---

*template 结束。配套主报告:`docs/audits/S2-H2-GOLDEN-OUTPUT-TEMPLATES.md`。*
