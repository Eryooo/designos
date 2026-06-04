# Brand Creative B1.0 — Contract Baseline

**Release Date:** 2026-06-04
**Batch:** B1.0 — brand-creative 契约冻结 + 知识就绪基线
**Branch:** `skills-pilot-wave2`
**Scope:** 契约冻结 + P0 知识资产就绪;不交付子技能 runtime(留给 B1.1+)

---

## 📦 交付物清单

### 1. 契约冻结(13 子技能)
- **文件:** `skills/brand-creative/contracts/sub-skill-contracts.yaml`
- **子技能:** brand-strategy / competitive-analysis / logo-design / color-system /
  typography-system / visual-identity / brand-voice / content-strategy /
  campaign-creative / brand-collateral / digital-assets / brand-guidelines / brand-audit
- **契约状态:**
  - 7 `ready_for_parallel`(P0 知识 gap=0,schema 完整,无未开发强制上游)
  - 1 `ready_after_upstream`(知识/schema 就绪,运行时等上游先开发)
  - 5 `blocked_by_knowledge`(依赖 partial_reuse 或缺专有资产,需 B1.1+ 补)
- **契约完整性:** 每个子技能 18 必填字段齐全(purpose / trigger_examples /
  required_inputs / optional_inputs / upstream_contracts / public_outputs /
  internal_outputs / output_schema_refs / downstream_consumers / runtime_dependencies /
  knowledge_ids / quality_gate / fallback_behavior / do_not_claim / contract_status / owner)。

### 2. 产物 Schema(16 个)
- **目录:** `skills/brand-creative/contracts/schemas/`
- **文件:** brand_brief / competitor_matrix / market_gap_report / logo_spec /
  logo_prompt_pack / color_palette / typography_spec / vi_manual / brand_voice_guide /
  content_strategy / campaign_brief / creative_concepts / collateral_spec /
  digital_asset_kit / brand_guidelines / brand_audit_report(全部 .schema.json)
- **标准:** 全部合法 JSON Schema draft-07(含 $schema / type=object / properties / required)。

### 3. 专业决策资产(7 个,已登记全局 manifest)
- **design.strategy.brand-strategy-methodology**
  - 通用品牌策略决策(北极星/定位/价值分层/人格关键词/差异化)
  - 含量化判断 + 冲突取舍 + 失败信号 + 一票否决 + 返工条件
- **design.visual.logo-design-methodology**
  - Logo 设计决策(类型/黑白/缩放/组合/辅助图形/商标风险)
- **design.visual.color-system-methodology**
  - 色彩系统决策(角色/对比度/明暗/介质差异/可访问性)
- **design.visual.typography-system-methodology**
  - 字体系统决策(配对/字重/比例/行高/授权/跨端)
- **design.strategy.brand-audit-methodology**
  - 品牌审计决策(健康度/差距/对标/优先级)
- **design.quality.brand-identity-quality-rubric**
  - 品牌识别专用质量 rubric(高阶/中阶/低阶三档 + 6 项一票否决)
  - 禁止用 IP rubric 冒充
- **design.quality.brand-creative-failure-modes**
  - 品牌创意失败模式库(现象/可检测信号/根因/返工条件)

**资产标准(守则 4):** 每个资产 11 段结构(purpose / applies_to / input_contract /
decision_framework / senior_heuristics / output_contract / quality_rubric /
common_failure_modes / senior_review_checklist / source_assets / do_not_claim),
含真实的资深判断能力(量化标准/冲突取舍/失败信号/一票否决/返工条件)。

### 4. 知识就绪审计
- **文件:** `skills/brand-creative/contracts/knowledge-readiness-matrix.yaml`
- **内容:** 逐个子技能审计 P0 knowledge gap / schema_ready / runtime_deps_ready,
  诚实区分 direct_reuse / partial_reuse / must_create。
- **守则 3 合规:** 7 个 ready_for_parallel 子技能的 P0 gap 全部 = 0。

### 5. 知识清单
- **文件:** `skills/brand-creative/knowledge-manifest.yaml`
- **内容:** active(11) / partial_reuse(6,明确 caveat) / planned(0,原 3 个已实现);5 个 blocked 子技能仍有 P0 gap。
- **守则 2 合规:** source_assets 仅引用真实仓库文件或标注 DesignOS pilot synthesis。

### 6. 测试覆盖
- **文件:** `skills/brand-creative/tests/test_brand_creative_contracts.py`
- **覆盖:** 批次第六节 10 条要求全部落地为自动化测试(契约完整性 / public_outputs
  合法性 / Kernel 不改 / schema 存在与合法 / workflow 依赖一致 / active 知识存在 /
  planned 不被 ready 消费 / ready 子技能 P0 gap=0 / 不用 IP rubric 冒充 / 无过度承诺)。
- **结果:** 23 passed。

---

## ✅ 验证通过清单

1. **共享层测试:** 9 passed(7 个新资产符合 DesignOS 资产标准)
2. **brand-creative 契约测试:** 23 passed
3. **其他 pilot skills 无回归:** ip-design / prd2proto / ai-analytics 全绿(101 passed)
4. **source_assets 真实引用:** 15 个文件引用全部存在
5. **Kernel 未改:** kernel/contracts/enums.py 无 B1.0 改动
6. **Factory 测试:** 61 passed
7. **4 个 skill validate:** ip-design / uxeval / prd2proto / ai-analytics 全过

---

## 📝 关键修正(守则 2 + 守则 3)

### 守则 2:source_assets 诚实性
- ❌ 修正前:"综合公开品牌战略实践"(冒充可追溯来源)
- ✅ 修正后:"DesignOS pilot synthesis(本资产为 pilot 阶段综合判断,非可追溯专业文献)"
- ✅ 所有 source_assets 仅引用真实仓库文件或明确标注 pilot synthesis。

### 守则 3:契约状态诚实性
- ❌ 修正前:visual-identity 标 `ready_for_parallel`,但运行时依赖 logo/color/typography
  三个尚未开发的上游。
- ✅ 修正后:visual-identity 改为 `ready_after_upstream`(知识/schema 就绪,但不能与上游
  同批并行)。
- ✅ 7 个 ready_for_parallel 子技能的 P0 knowledge gap 全部 = 0,且无未开发强制上游。

### 守则 4:资产质量(真实资深判断)
- ✅ 全部 7 个资产含 11 段必需结构。
- ✅ decision_framework 含量化标准 + 冲突取舍。
- ✅ common_failure_modes 含可检测失败信号 + 返工条件。
- ✅ quality_rubric 含一票否决项。
- ✅ senior_review_checklist 含可执行检查项。

---

## 🚫 明确不交付(B1.0 范围外)

- 任何子技能的 SKILL.md / pipeline.yaml / prompts(留给 B1.1+)。
- partial_reuse 资产的私有 adapter(留给对应子技能开发批次)。
- content-strategy / campaign-creative / brand-collateral / digital-assets /
  brand-guidelines 的 P0 知识资产(5 个 blocked 子技能留给 B1.1+)。
- 不修改 Kernel / Factory。
- 两个本地 commit(先 knowledge 后 contracts),不 push。

---

## 📊 就绪汇总

| 维度 | 数量 | 说明 |
|---|---|---|
| 子技能契约 | 13 | 全部冻结,18 必填字段齐全 |
| 产物 Schema | 16 | 全部合法 JSON Schema draft-07 |
| 专业决策资产 | 7 | 已登记全局 manifest,符合共享层标准 |
| ready_for_parallel | 7 | P0 gap=0,可第一波并行启动 |
| ready_after_upstream | 1 | visual-identity(等三个上游先开发) |
| blocked_by_knowledge | 5 | 需 B1.1+ 补 P0 知识或 adapter |
| planned 已实现 | 3 → 0 | 原 3 个 planned 全部实现并移入 active |

---

## 🔄 后续批次(B1.1+)

### B1.1(可选):第一波 7 子技能 runtime
- brand-strategy / competitive-analysis / logo-design / color-system /
  typography-system / brand-voice / brand-audit
- 交付每个子技能的 SKILL.md / pipeline.yaml / prompts / smoke test。

### B1.2(可选):第二波 visual-identity
- 依赖 B1.1 三个上游(logo/color/typography)完成。

### B1.3+(可选):blocked 子技能解锁
- 先补 P0 知识资产或 partial_reuse adapter,再开发 runtime。

---

## 📋 B1.0 closeout 检查清单

- [x] 13 子技能契约冻结(18 必填字段齐全)
- [x] 16 产物 Schema 存在且合法
- [x] 7 专业决策资产登记全局 manifest
- [x] 知识就绪审计矩阵完成
- [x] 知识清单(active/partial/planned)冻结
- [x] 23 个契约测试全绿
- [x] 共享层测试 9 passed
- [x] 其他 pilot skills 无回归
- [x] source_assets 真实引用全部存在
- [x] Kernel/Factory 未改
- [x] 守则 2/3/4 全部满足
- [x] release baseline 文档完成
- [x] 无过度承诺(测试验证通过)

---

**Next:** 两个 commit(B1.0 contracts + B1.0 knowledge),不 push。
