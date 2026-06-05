# brand-strategy

> Phase 1 策略与定位 · B1.1 runtime ready

## 定位

品牌策略基线子技能,产出品牌战略核心要素:北极星/定位/差异化/核心价值/人格关键词。作为所有下游子技能的策略锚点。

## 核心能力

- 基于产品简介与目标用户产出品牌定位框架
- 消费竞品矩阵(competitor_matrix)时,差异化判定基于证据
- 竞品矩阵缺失或不足时,差异化标注 [inferred] 并声明未经验证
- 输出情感化北极星(非功能描述)
- 提供定位取舍理由与不选其他方向的冲突分析

## 核心产出

- `brand_brief`: 品牌策略基线(JSON)
  - `north_star`: 情感化价值
  - `positioning`: 品牌定位
  - `differentiation`: 差异化判定(含证据来源标注)
  - `core_values`: 核心价值观
  - `personality_keywords`: 人格关键词(3-5个)
  - `target_user`: 目标用户

## 输入依赖

**必需:**
- `product_brief`: 产品/服务简介
- `target_user`: 目标用户画像

**可选:**
- `competitor_matrix`: 竞品矩阵(由 competitive-analysis 产出或用户自带)
- `brand_audit_report`: 品牌审计报告(brand-refresh 场景)

## 质量标准

- 北极星必须是情感化价值,不能只是功能描述
- 差异化有竞品矩阵支撑时,必须引用证据(`basis: "competitor_matrix"`)
- 差异化无竞品支撑时,必须标注 `basis: "inferred"`
- 人格关键词必须 3-5 个,覆盖情感/价值/行为维度
- 必须输出定位取舍与不选其他方向的理由

## 能力边界

**不声称:**
- 不声称产出可直接商用，需资深品牌经理评审后方可进入商用决策
- 已覆盖完整品牌战略(营销/财务/组织不在范围)
- 差异化标 [inferred] 时已完成竞品对标验证

## 文件结构

```
brand-strategy/
├── SKILL.md              # 技能元数据与能力声明
├── pipeline.yaml         # 两阶段 pipeline(分析上下文 → 产出 brand_brief)
├── constitution.md       # 运行时强制约束(差异化判定/北极星/人格关键词规则)
├── README.md            # 本文件
├── prompts/             # LLM prompts
│   ├── 01-analyze-context.md
│   └── 02-generate-brand-brief.md
├── reference/           # 参考案例
│   ├── case-with-competitor-matrix.md
│   └── case-inferred-differentiation.md
├── eval/                # 评测集
│   ├── golden/
│   │   └── golden-01-with-matrix.yaml
│   ├── failure/
│   │   └── failure-01-inferred.yaml
│   └── promptfoo.yaml
└── tests/               # pytest 单元测试
    └── test_brand_strategy_structure.py
```

## 使用场景

- 用户输入产品简介与目标用户,需要建立品牌策略框架
- 品牌焕新场景,基于 brand-audit 产出重定策略
- workflow 运行时 competitive-analysis 产出 competitor_matrix 后调用

## 依赖关系

**上游(可选):**
- competitive-analysis (workflow 场景)
- brand-audit (brand-refresh workflow)

**下游消费者:**
- logo-design
- color-system
- typography-system
- brand-voice
- content-strategy

## 复用共享决策资产

- `knowledge/design/strategy/brand-strategy-methodology.md`
- `knowledge/design/quality/brand-identity-quality-rubric.md`
- `knowledge/design/quality/brand-creative-failure-modes.md`

## Pilot 限制

- 需资深品牌经理评审后方可商用
- 不覆盖完整品牌战略(营销/财务/组织)
- 差异化标 [inferred] 时未经竞品对标验证
