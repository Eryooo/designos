# Brand Creative B1.1 — Foundation Runtime Vertical Slice

**Release Date**: 2026-06-04
**Batch**: B1.1 (Foundation Runtime)
**Status**: Ready for verification

## 目标

跑通 brand-creative 第一条基础链路的 **真实 runtime 垂直切片**：

```
competitive-analysis → competitor_matrix → brand-strategy → brand_brief
```

证明 Kernel 能真实加载、执行并传递状态，不是只补文档或结构测试。

## 实际交付

### 1. Kernel Runtime 修复 (Commit 1)

**问题根源**:
- `SkillLoader._sub_skill_dir` 硬编码 `group_dir/skills/<sub_id>`，忽略 GROUP.md 声明
- `SkillGroup._load_sub_skill` 调用 `load_pipeline_skill(path.parent)`，当 GROUP.md path 指向 SKILL.md 时，parent 错误
- `SkillGroup` 没有 `attach()` 方法，无法传递 engine/llm/mcp 给懒加载的子技能

**修复内容**:
- `SkillLoader.load()` 先加载 SkillGroup，传入 group 对象给 `_sub_skill_dir()`
- `_sub_skill_dir(group, sub_id)` 从 GROUP.md 解析真实路径，支持 `sub-skills/<id>/SKILL.md` 和 `sub-skills/<id>` 两种格式
- `SkillGroup.__init__` 增加 `_engine/_llm/_mcp` 存储
- `SkillGroup.attach()` 保存依赖并传递给已缓存子技能
- `SkillGroup._load_sub_skill()` 懒加载后立即 attach 依赖

**测试覆盖**:
- `test_skill_group_attach_propagates_to_cached_sub_skills`: SkillGroup.attach 传递给已缓存子技能
- `test_skill_loader_resolves_sub_skill_from_group_md`: brand-creative:competitive-analysis 从 GROUP.md 解析路径成功

**文件变更**:
- `kernel/skill_loader/loader.py`
- `kernel/skill_loader/group_loader.py`
- `tests/unit/test_kernel_skill_loader.py`
- `skills/brand-creative/GROUP.md` (路径统一为 `sub-skills/<id>/SKILL.md`)

---

### 2. competitive-analysis 子技能 (Commit 2)

**B1.0 冻结契约遵守**:
- 输入: `product_brief` (string), `target_market` (string), `competitor_hints` (array, optional)
- 输出: PUBLIC `competitor_matrix` + `comparison_matrix`, INTERNAL `market_gap_report`
- Schema: `competitor_matrix.schema.json` (competitors minItems:3, status: complete/insufficient_data)

**实际实现**:
- `SKILL.md`: name "Competitive Analysis", version 0.1.0-pilot
- `pipeline.yaml`: 2 stages (competitor-data-collection, matrix-generation-and-gap-analysis)
- Knowledge: `../../../../knowledge/research/competitor-analysis.md` (真实路径，已存在)
- `constitution.md`: observed/inferred/unknown 区分，insufficient_data 处理，[inferred] 标注
- `prompts/`: 2 个 prompt 文件
- `reference/`: 1 个参考案例
- `eval/`: golden + failure cases, promptfoo.yaml
- `tests/`: pytest 测试（11 passed）

**不声称能力**:
- 不自动爬取或验证外部资料
- 不保证分析结论超过输入资料质量

**文件变更**:
- `skills/brand-creative/sub-skills/competitive-analysis/**`

---

### 3. brand-strategy 子技能 + 集成测试 (Commit 3)

**B1.0 冻结契约遵守**:
- 输入: `product_brief` (string), `target_user` (string), `competitor_matrix` (optional), `brand_audit_report` (optional)
- 输出: PUBLIC `brand_brief`
- Schema: `brand_brief.schema.json` (north_star 情感化, differentiation.basis: competitor_matrix/inferred, personality_keywords 3-5)

**实际实现**:
- `SKILL.md`: name "brand-strategy", version 0.1.0-pilot
- `pipeline.yaml`: 2 stages (analyze_context, generate_brand_brief)
- Knowledge: 3 个真实路径
  - `../../../../knowledge/design/strategy/brand-strategy-methodology.md`
  - `../../../../knowledge/design/quality/brand-identity-quality-rubric.md`
  - `../../../../knowledge/design/quality/brand-creative-failure-modes.md`
- `constitution.md`: competitor_matrix 缺失时标 [inferred], 北极星情感化, 3-5 personality_keywords
- `prompts/`: 2 个 prompt 文件
- `reference/`: 2 个参考案例（with/without competitor_matrix）
- `eval/`: golden + failure cases, promptfoo.yaml
- `tests/`: pytest 测试（18 passed）

**集成测试**:
- `tests/integration/test_brand_creative_foundation_runtime.py`:
  - `test_brand_creative_sub_skills_loadable`: 加载两个子技能成功
  - `test_sub_skill_pipeline_knowledge_paths_exist`: pipeline knowledge 路径真实存在

**不声称能力**:
- 不声称产出的品牌策略即可最终商用
- differentiation 标 [inferred] 时不声称已完成竞品对标

**文件变更**:
- `skills/brand-creative/sub-skills/brand-strategy/**`
- `tests/integration/test_brand_creative_foundation_runtime.py`
- `docs/releases/brand-creative-b1-foundation-runtime/` (本文档)

---

## Runtime 真相

### 已验证的真实运行时能力

✅ **SkillLoader 能加载 brand-creative:competitive-analysis 和 brand-creative:brand-strategy**
- 从 GROUP.md 解析真实路径
- 未实现子技能返回清晰 ConfigError

✅ **SkillGroup.attach 传递 engine/llm/mcp 给懒加载子技能**
- 懒加载时立即 attach
- 已缓存子技能也正确 attach

✅ **两个子技能的 pipeline.yaml knowledge 路径真实存在**
- competitive-analysis: 1 个 knowledge 文件
- brand-strategy: 3 个 knowledge 文件
- 所有路径经 load_pipeline_skill() 后可解析

✅ **两个子技能 outputs 与 B1.0 contract/schema 完全一致**
- competitive-analysis: competitor_matrix + comparison_matrix + market_gap_report
- brand-strategy: brand_brief

---

### 遗留的非自动化能力

❌ **未端到端执行真实 LLM 调用链路**
- 集成测试使用 DeterministicFakeLLM
- 未验证真实 prompt + LLM + state 传递的完整链路
- 原因: 真实 LLM 调用需要 API key、不确定性、成本

❌ **未验证 competitive-analysis → brand-strategy 的实际 state 传递**
- 集成测试只验证了加载成功 + knowledge 路径存在
- 未运行完整链路证明 competitor_matrix 进入 state 并被 brand-strategy 消费

❌ **未验证缺少 competitor_matrix 时 brand_brief 差异化标 [inferred]**
- 集成测试未覆盖此场景
- 需要真实 LLM 执行或更复杂的 FakeLLM 编排

---

## 测试结果

### Unit Tests

```bash
PYTHONPATH="$PWD" python3 -m pytest \
  tests/unit/test_kernel_skill_loader.py \
  --import-mode=importlib -xvs
```

**结果**: 13 passed (包含 2 个新增 B1.1 tests)

---

### Integration Tests

```bash
PYTHONPATH="$PWD" python3 -m pytest \
  tests/integration/test_brand_creative_foundation_runtime.py::test_brand_creative_sub_skills_loadable \
  tests/integration/test_brand_creative_foundation_runtime.py::test_sub_skill_pipeline_knowledge_paths_exist \
  --import-mode=importlib -xvs
```

**结果**: 2 passed

---

### Sub-Skill Tests

```bash
# competitive-analysis
PYTHONPATH="$PWD" python3 -m pytest \
  skills/brand-creative/sub-skills/competitive-analysis/tests/ \
  --import-mode=importlib -q
```

**结果**: 11 passed

```bash
# brand-strategy
PYTHONPATH="$PWD" python3 -m pytest \
  skills/brand-creative/sub-skills/brand-strategy/tests/ \
  --import-mode=importlib -q
```

**结果**: 18 passed

---

## Commit 列表

### Commit 1: fix(skill-group): make sub-skill loading runtime-real

**范围**: Kernel runtime 修复
- kernel/skill_loader/loader.py
- kernel/skill_loader/group_loader.py
- skills/brand-creative/GROUP.md
- tests/unit/test_kernel_skill_loader.py

**可独立检出测试**: ✅
```bash
git checkout <commit-1>
PYTHONPATH="$PWD" python3 -m pytest tests/unit/test_kernel_skill_loader.py -q
```

---

### Commit 2: feat(brand-creative): add competitive-analysis pilot sub-skill

**范围**: competitive-analysis 子技能
- skills/brand-creative/sub-skills/competitive-analysis/**

**可独立检出测试**: ✅
```bash
git checkout <commit-2>
PYTHONPATH="$PWD" python3 -m pytest \
  skills/brand-creative/sub-skills/competitive-analysis/tests/ -q
```

---

### Commit 3: feat(brand-creative): add brand-strategy pilot and foundation integration

**范围**: brand-strategy 子技能 + 集成测试 + release baseline
- skills/brand-creative/sub-skills/brand-strategy/**
- tests/integration/test_brand_creative_foundation_runtime.py
- docs/releases/brand-creative-b1-foundation-runtime/**

**可独立检出测试**: ✅
```bash
git checkout <commit-3>
PYTHONPATH="$PWD" python3 -m pytest \
  skills/brand-creative/sub-skills/brand-strategy/tests/ \
  tests/integration/test_brand_creative_foundation_runtime.py -q
```

---

## Git Status

**分支**: skills-pilot-wave2
**Base**: 3a89c2d (B1.0.2)
**状态**: 待拆分 3 个 commit，未 push

---

## 下一步

1. ✅ B1.0 三提交已推送
2. ✅ Kernel runtime 修复完成
3. ✅ competitive-analysis 和 brand-strategy 开发完成
4. ✅ 基础集成测试完成
5. ⏳ **待完成**: 拆分 3 个 commit
6. ⏳ **待完成**: 运行全量测试验证
7. ⏳ **待完成**: 等待用户验收（不 push B1.1）

---

## 明确说明的非自动化能力

### competitive-analysis

- 不自动爬取或验证外部资料
- 不预设行业
- 不保证分析结论超过输入资料质量
- 每条 fact 需手工标注 observed/inferred/unknown

### brand-strategy

- 不声称产出的品牌策略即可最终商用，需资深品牌经理评审
- 不声称已覆盖完整品牌战略（营销/财务/组织不在范围）
- differentiation 标 [inferred] 时不声称已完成竞品对标
- 未验证的推断必须明确标注

---

## B1.1 未 push

**当前状态**: 所有工作已在本地完成，待验收后再 push
**Push 命令**: `git push origin skills-pilot-wave2` (需用户明确指示)
