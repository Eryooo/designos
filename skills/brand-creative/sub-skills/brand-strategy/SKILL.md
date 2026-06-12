---
name: brand-strategy
version: 0.1.0-pilot
type: pipeline
group: brand-creative
phase: 1-strategy
purpose: 产出品牌策略基线(定位/差异化/核心价值/人格关键词)
scope: 通用品牌战略决策(企业品牌/产品品牌/服务品牌)
inputs:
  required:
    - product_brief
    - target_user
  optional:
    - competitor_matrix
    - brand_audit_report
outputs:
  - id: brand_brief
    type: brand_brief
    format: json
    schema_ref: ../../contracts/schemas/brand_brief.schema.json
knowledge_dependencies:
  - ../../../../knowledge/design/strategy/brand-strategy-methodology.md
  - ../../../../knowledge/design/quality/brand-identity-quality-rubric.md
  - ../../../../knowledge/design/quality/brand-creative-failure-modes.md
quality_gate:
  checkpoint_id: C1-brand-strategy
  must_pass:
    - 北极星是情感化价值,不是功能描述
    - 差异化判定基于 competitor_matrix 或显式标注 [inferred]
    - 人格关键词 3-5 个,覆盖情感/价值/行为维度
contract_ref: ../../contracts/sub-skill-contracts.yaml#brand-strategy
pilot_status: runtime_ready
pilot_limitations:
  - 需资深品牌经理评审后方可商用
  - 不覆盖完整品牌战略(营销/财务/组织)
  - 差异化标 [inferred] 时未经竞品对标验证
---

# brand-strategy

## 定位

品牌策略基线子技能,产出品牌战略核心要素:北极星/定位/差异化/核心价值/人格关键词。

## 核心能力

- 基于产品简介与目标用户产出品牌定位框架
- 消费竞品矩阵(competitor_matrix)时,差异化判定基于证据
- 竞品矩阵缺失或不足时,差异化标注 [inferred] 并声明未经验证
- 输出情感化北极星(非功能描述)
- 提供定位取舍理由与不选其他方向的冲突分析

## 输入要求

**必需:**
- `product_brief`: 产品/服务简介(核心功能/目标市场/价值主张)
- `target_user`: 目标用户画像(人口统计/痛点/期待)

**可选:**
- `competitor_matrix`: 竞品矩阵(由 competitive-analysis 产出或用户自带)
- `brand_audit_report`: 品牌审计报告(brand-refresh workflow 场景)

## 输出产物

`brand_brief` (JSON):
- `north_star`: 情感化价值(如"让创业者感到被理解与支持")
- `positioning`: 品牌定位
- `differentiation`: { statement, basis: ["competitor_matrix" | "inferred"] }
- `core_values`: 核心价值观(至少1个)
- `personality_keywords`: 人格关键词(3-5个,覆盖情感/价值/行为维度)
- `target_user`: 目标用户

## 质量标准

- 北极星必须是情感化价值,不能只是功能描述
- 差异化有竞品矩阵支撑时,必须引用证据
- 差异化无竞品支撑时,必须标注 `basis: "inferred"`
- 人格关键词必须 3-5 个,覆盖情感/价值/行为维度
- 必须输出定位取舍与不选其他方向的理由

## 能力边界

**不声称:**
- 不声称产出可直接商用，需资深品牌经理评审后方可进入商用决策
- 已覆盖完整品牌战略(营销/财务/组织不在范围)
- 差异化标 [inferred] 时已完成竞品对标验证

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
