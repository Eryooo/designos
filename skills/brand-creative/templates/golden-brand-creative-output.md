# Golden Output Template — brand-creative

> **🚫 SYNTHETIC / SANITIZED ONLY** — 本模板及示例片段不含任何真实品牌、真实客户、真实商标、真实 logo。所有示例都用 `Acme Demo Brand` / `synthetic-logo-001` 等明显假名占位。
> **本模板性质**:品牌创意 Skill Group 输出规范,"中阶可用 + 资深目标"双层基准。
> **依据**:S2-H1 §2.5(brand-creative rubric)+ S2-H1.1 §6.2.5(KR-B1~B5)+ `knowledge/design/quality/{brand-identity-quality-rubric, brand-creative-failure-modes}.md`。
> **当前状态**:**maturity = alpha**(group skill 主线未成型);**13 sub-skill 仅 6 有 pipeline(46%, 未达 KR-B1 最低线 50%)**;无 root pipeline / 无 root constitution。

---

## 1. 输入前提

| 输入 | 强制 / 可选 | 说明 |
|---|---|---|
| 品牌策略输入 | 强制 | 业务定位 / 核心价值 / 目标用户(synthetic / sanitized) |
| 竞品品牌信息 | 强制 | ≥ 3 个竞品的 sanitized 信息 |
| 既有品牌资产 | 可选 | 主色 / 字体 / logo(若 brand-refresh 流程) |
| sub-skill 选择 | 强制 | 至少 1 个 sub-skill(brand-strategy / logo-design / color-system 等) |

---

## 2. 输出目录结构 / Artifact 列表

按 4 phase + 13 sub-skill 组织(✅ = 当前 6 个有 pipeline,⚠️ = 7 个 sub-skill 主线待建):

```
brand-creative-out/<run_id>/
├── phase-1-strategy/
│   ├── brand_brief.yaml          # ✅ brand-strategy
│   └── competitive_matrix.yaml   # ✅ competitive-analysis
├── phase-2-visual-identity/
│   ├── logo_spec.yaml            # ✅ logo-design
│   ├── color_palette.yaml        # ✅ color-system
│   ├── typography_spec.yaml      # ✅ typography-system
│   └── vi_manual.yaml            # ✅ visual-identity
├── phase-3-content/
│   ├── brand_voice_guide.yaml    # ⚠️ brand-voice (无 pipeline)
│   ├── content_plan.yaml         # ⚠️ content-strategy (无 pipeline)
│   └── campaign_brief.yaml       # ⚠️ campaign-creative (无 pipeline)
├── phase-4-collateral/
│   ├── collateral_spec.yaml      # ⚠️ brand-collateral (无 pipeline)
│   ├── digital_asset_kit.yaml    # ⚠️ digital-assets (无 pipeline)
│   └── brand_guidelines.yaml     # ⚠️ brand-guidelines (无 pipeline)
└── brand_audit_report.yaml       # ⚠️ brand-audit (无 pipeline)
```

> ⚠️ alpha 阶段:**至少 1 个 sub-skill 跑通 brief / 规范产出**即可作为最低线交付(KR-B1)。

---

## 3. 必填章节(每个 sub-skill 输出)

### 3.1 brand_brief 必填字段(brand-strategy sub-skill)

```yaml
brand_brief:
  project: <synthetic 项目代号>
  positioning: <定位陈述>           # ❗ 必填,不可只是形容词
  differentiation:
    statement: <差异化定位>
    competitor_blank: <基于竞品空白的依据>
    evidence_refs: [...]            # 可追溯到 competitive_matrix
  core_values: [...]
  personality_keywords: [...]       # ≥ 3 个具体词,不只是 "年轻 / 科技"
  target_audience: {primary: ..., secondary: ...}
```

### 3.2 logo_spec / color_palette / typography_spec 必填字段

```yaml
logo_spec:
  form_principle: <形态原则>
  recognition_test:
    at_32px: <可辨/糊/不可辨>
    at_silhouette: <可辨/糊/不可辨>
  legal_check:
    trademark_signal: <无/疑似/明显>   # 必填(KR-B3 V2 一票否决相关)
    flagged_for_lawyer: <bool>

color_palette:
  primary: "#XXXXXX"
  contrast_check:
    aa_compliant: <bool>              # WCAG AA 必查
    ratio: <对比度>
```

### 3.3 cross_subskill_consistency(KR-B4)

```yaml
cross_subskill_consistency:
  keyword_chain:
    strategy_keywords: [...]
    visual_keywords: [...]
    voice_keywords: [...]
  drift_check: <一致 / 漂移>
  drift_locations: [...]              # 漂移点必须明确
```

---

## 4. 字段级要求

### 4.1 positioning(KR-B3 V1 一票否决相关)
- 必须含可消费的差异化定位,**不能是空话**
- 严禁仅用形容词("年轻化 / 科技感 / 可信赖")堆砌

### 4.2 trademark_signal(KR-B3 V2 一票否决相关)
- 每个 logo / 名称必须显式标 trademark 风险信号
- 风险等级:`无 / 疑似 / 明显`
- `疑似` 或 `明显` 必须 `flagged_for_lawyer: true`

### 4.3 keyword_chain(KR-B4)
- 跨 sub-skill 关键词链路:strategy → visual → voice → collateral
- 漂移点必须显式记录,不可掩盖

### 4.4 contrast_check(WCAG)
- color_palette 必须含 WCAG AA 对比度检查(≥ 4.5:1)
- 不通过的色值必须标 "仅装饰用,非功能文本"

---

## 5. 最低线标准(中阶可用 — KR-B1~B5)

| KR | 要求 |
|---|---|
| KR-B1 | sub-skill 有 pipeline 比例 ≥ 50%(7/13)— **当前 6/13 = 46% 未达,本 skill 仍 alpha** |
| KR-B2 | 已实装 sub-skill 的 brand-identity rubric 自评中阶以上比例 ≥ 70% |
| KR-B3 | 一票否决项(策略空心 / 法务风险 / 跨子 skill 不一致)命中数 = 0 |
| KR-B4 | 跨 sub-skill 关键词链路一致性 ≥ 70% |
| KR-B5 | brand-creative-failure-modes 严重级命中数 = 0 |

---

## 6. 目标线标准(资深可评审)

- **sub-skill 实装 ≥ 7/13**(KR-B1 目标线)
- **rubric 自评中阶以上 ≥ 90%**(KR-B2 目标线)
- **跨 sub-skill 关键词链路一致性 ≥ 85%**(KR-B4 目标线):品牌策略关键词 → VI → 内容 → 物料 全链路无漂移
- **logo_spec 32px 可辨 + 远观可识别**
- **color_palette 全部通过 WCAG AA**
- **typography_spec 含授权风险检查**:商业字体使用授权显式标注

---

## 7. 一票否决项检查表(V1-V3)

| # | 检查 | 触发条件 |
|---|---|---|
| **V1** 策略空心化 | 品牌策略全是形容词(年轻 / 科技 / 信任),无可消费的差异化定位 | 直接拒绝交付 |
| **V2** 法务/商标风险 | 核心 logo / 名称有明显商标冲突信号但未标注 | 整方案返工 |
| **V3** 跨子 skill 不一致 | 策略说"高端简约",logo 用大量装饰性元素 | 整 phase 返工 |

---

## 8. Gap / Assumption / Confidence / Traceability 规范

| 字段 | 规范 |
|---|---|
| `gaps[]` | 主线缺口明确记录(如"7 sub-skill 无 pipeline")+ 已实装 sub-skill 的局部缺口 |
| `assumptions[]` | 推断决策的依据假设 + risk_if_wrong |
| `confidence` | 整体可靠性,基于 已实装 sub-skill 数 + rubric 自评加权 |
| `traceability` | 每个 sub-skill 输出必须可追溯到:① 上游 brand_brief ② 共享方法论 id(`design.strategy.*` / `design.visual.*`)③ 竞品/用户输入 |

---

## 9. 自评表(对账 KR)

```yaml
self_eval:
  KR-B1_subskill_pipeline_coverage:
    actual: <有 pipeline 的 sub-skill 数 / 13>
    target: ≥ 50% (最低), 100% (目标)
    pass: <bool>
    note: "S1-0B 实证当前 6/13 = 46%,未达最低线"
  KR-B2_rubric_mid_or_above:
    actual: <已实装 sub-skill 中阶以上比例>
    target: ≥ 70% (最低), ≥ 90% (目标)
    pass: <bool>
  KR-B3_one_strike_count:
    actual: <V1+V2+V3 触发数>
    target: = 0
    pass: <bool>
  KR-B4_cross_subskill_consistency:
    actual: <关键词链路一致比例>
    target: ≥ 70% (最低), ≥ 85% (目标)
    pass: <bool>
  KR-B5_severe_failure_count:
    actual: <brand-creative-failure-modes 严重级命中数>
    target: = 0
    pass: <bool>
  global_KR1.1_minimum_delivery:
    pass: <KR-B1~B5 是否全过最低线>
  global_KR1.2_one_strike_count:
    pass: <V1~V3 是否全为 0>
  global_KR3.2_gap_annotation:
    pass: <gaps 是否显式记录主线缺口>
```

---

## 10. 禁止声明清单

- ❌ "13 个 sub-skill 全部可用"(实际 6/13 有 pipeline,7 个无)
- ❌ "替代专业品牌咨询"
- ❌ "可直接用于品牌发布 / 商标注册"
- ❌ "已接入 runtime"(无 runtime)
- ❌ "已达资深品牌策略师水平"
- ❌ "production ready" / "fully automated" / "完全自动化"

允许声明:

- ✅ "Skill Group 框架已搭,13 sub-skill 中 6 个有 pipeline 主线"
- ✅ "可生成 brand-strategy + VI 框架"
- ✅ "alpha 阶段:contracts + 部分子 pipeline"
- ✅ "适合内部品牌 brief 起点"

---

## 11. Synthetic 示例片段(中阶可用档,sanitized only)

> ⚠️ 所有数据为 synthetic;占位符:`Acme Demo Brand`(假品牌)、`synthetic-logo-001`(假 logo)、`#A8C5FF`(假色值)。

### 11.1 brand_brief 中阶可用档示例

```yaml
brand_brief:
  project: "Acme Demo Cloud Service Brand"
  positioning: "[synthetic] 面向小型企业的'值得信赖的运维伙伴',不做炫酷,做可靠"
  differentiation:
    statement: "[synthetic] 区别于竞品 A 的'尖端 AI 高科技'路线和竞品 B 的'轻量化萌系'路线,主打'专业可靠的中段空间'"
    competitor_blank: "[synthetic] 高端 vs 萌系两端拥挤,'专业可靠'中段品牌少"
    evidence_refs: [
      "competitive_matrix.yaml#competitor-A-style",
      "competitive_matrix.yaml#competitor-B-style"
    ]
  core_values:
    - "可靠"
    - "省心"
    - "专业但不冷漠"
  personality_keywords: ["稳重", "细心", "略带技术感", "亲和"]
  target_audience:
    primary: "小型企业 IT 管理员(参考 ai-analytics 上游)"
    secondary: "DevOps 工程师"
  confidence: 0.65
  inferences:
    - field: "personality_keywords[3]"
      value: "[inferred] '亲和' 基于 small team 用户痛点('需要可靠感而非威慑感')推断"
```

### 11.2 logo_spec 中阶可用档示例

```yaml
logo_spec:
  project: "Acme Demo Cloud Service Brand"
  form_principle: "[synthetic] 简约几何形 + 暗示守护(盾形元素)"
  recognition_test:
    at_32px: "可辨"
    at_silhouette: "可辨"
  legal_check:
    trademark_signal: "无明显信号"
    flagged_for_lawyer: false
    note: "[synthetic] 已对照行业 5 个常见 logo 风格,无近似;但仍建议商标注册前由法务确认"
  rubric_self_eval:
    D1_distinctiveness: "中阶可用"
    D2_scalability: "中阶可用"
    D3_legal_safety: "中阶可用(待法务确认)"
```

### 11.3 cross_subskill_consistency 示例

```yaml
cross_subskill_consistency:
  keyword_chain:
    strategy_keywords: ["稳重", "细心", "专业", "亲和"]
    visual_keywords: ["简约几何", "蓝灰主调", "圆角", "不张扬"]
    voice_keywords: ["简洁", "肯定", "避免感叹号", "技术准确"]
  alignment_check:
    strategy_to_visual:
      status: "中阶一致"
      drift: "[synthetic] '亲和' 在 visual 中体现弱,圆角已用但仍偏冷"
      severity: "low"
    visual_to_voice:
      status: "中阶一致"
      drift: "无显著漂移"
  overall_consistency_score: 0.74   # ≥ 0.70 通过 KR-B4 最低线
```

### 11.4 当前主线状态(诚实声明)

```yaml
current_status:
  maturity: alpha
  pipeline_coverage:
    has_pipeline: ["brand-strategy", "competitive-analysis", "logo-design",
                   "color-system", "typography-system", "visual-identity"]
    no_pipeline: ["brand-voice", "content-strategy", "campaign-creative",
                  "brand-collateral", "digital-assets", "brand-guidelines", "brand-audit"]
    coverage: 6/13   # 46%, 未达 KR-B1 最低线 50%
  not_allowed_claims_check:
    "13 sub-skill 全部可用": false   # ❌ 不可宣称
    "可直接用于品牌发布": false       # ❌ 不可宣称
```

---

*template 结束。配套主报告:`docs/audits/S2-H2-GOLDEN-OUTPUT-TEMPLATES.md`。*
