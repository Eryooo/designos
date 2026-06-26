# S2-EVO-PRE — SkillOpt 启发下的 DesignOS 受控自进化执行策略

> **文档性质**：策略审计与后续执行指引。  
> **范围**：梳理现有 DesignOS 反馈闭环资产、SkillOpt 可复用机制、后续 batch 依赖关系。  
> **非目标**：不实现 runtime、不改 prompt、不读取 private evidence、不引入自动优化器、不 auto-adopt。  
> **结论**：现有 H7/H8/H9 机制可复用，但需要升级为“受控优化闭环”；后续不应只做 4 个大 batch，而应拆成质量优先的小批次。
> **最高约束**：复用是手段，不是目标。任何现有机制、模板、schema、prompt、流程、代码如果因为复用导致最终设计输出质量下降，必须立即放弃复用、重构或重做。DesignOS 的终极目标是替代中低阶设计师的设计执行产出，并帮助设计师提质提效。

---

## 1. 背景问题

DesignOS 当前已经完成两类重要基础：

1. **能力质量基础**：H1-H6 已定义 senior output rubric、OKR/KR、golden template、failure modes、self-review gate、input-quality gate、progressive checkpoint、cross-skill consistency。
2. **反馈安全基础**：H7A/H7B/H8/H9 已定义外部 workspace、diagnostic summary、sanitized issue、synthetic replay、trial readiness、PRD-only gap fix。

但真实试跑暴露出一个更深层问题：

- DesignOS 可以记录问题，但还没有完整定义“如何安全地把问题转成可验证的 skill 改进”。
- DesignOS 可以生成 synthetic replay，但还没有明确“候选修改必须通过什么 gate 才能合入”。
- DesignOS 可以做 prompt hardening，但还没有把每次修改限制为有预算、有证据、有拒绝记录的 bounded edit。
- DesignOS 可以做 trial，但还没有稳定区分 `skill defect`、`execution lapse`、`input insufficiency`、`evaluator gap`、`product/design standard gap`。

SkillOpt 的价值正好在这里：它不是给 DesignOS 一个“自动改 prompt”的捷径，而是提供一套可验证、可回滚、可审计的受控演进范式。

---

## 2. 现有资产盘点：哪些应直接复用

### 2.0 复用前提

以下资产的“可复用”只表示它们有继续利用价值，不表示必须保留原样。

复用必须满足四个前提：

- 不降低最终设计产出质量。
- 不削弱资深设计师式的分析、推导、判断、落地链路。
- 不牺牲隐私安全、traceability、gap honesty、validation gate。
- 不为了省时间保留明显不适合的旧结构。

如果复用与质量目标冲突，优先级是：

```text
最终输出质量 > 资深设计推理完整性 > 安全与可验证性 > 复用效率
```

允许的结果包括：

- 直接复用。
- 改造后复用。
- 只复用思想，不复用文件结构。
- 完全放弃旧资产，重新设计。

### 2.1 H7A：用户反馈安全基础设施

可复用资产：

- `docs/audits/S2-H7A-USER-FEEDBACK-SAFETY-INFRASTRUCTURE.md`
- `schemas/feedback/diagnostic-summary.schema.json`
- `schemas/feedback/sanitized-issue.schema.json`
- `templates/diagnostic-summary.md`
- `templates/sanitized-issue-registry.md`
- `templates/synthetic-replay-case.md`
- `.github/ISSUE_TEMPLATE/skill_quality_report.yml`

已解决的问题：

- 用户不需要提交真实 PRD、截图、URL、仓库、账号、业务文案。
- raw artifacts 写入 `<DESIGNOS_WORKSPACE_ROOT>`，不进入 Git。
- issue 侧只接收脱敏摘要和问题描述。
- 维护者内部做 sanitized issue、root cause、synthetic replay。

需要保留的原则：

- 用户反馈链路必须低成本。
- raw evidence 不进仓库。
- Git 只保存 sanitized / synthetic / generalized fix。

### 2.2 H7B：Offline Dry-Run Execution

可复用资产：

- `docs/audits/S2-H7B-OFFLINE-DRY-RUN-EXECUTION.md`
- `fixtures/synthetic/s2-h7b-dry-run/*`
- `docs/audits/sanitized-issues/S2-H7B-sanitized-issue-registry.md`

已解决的问题：

- 外部 workspace 能跑多 skill / 多 run / 多 batch。
- input gate、progressive checkpoint、cross-skill consistency、self-review 可以串联。
- synthetic fixture 可以复现输入缺口、过程降级、一致性冲突。

需要保留的原则：

- 仓库内只保留 synthetic fixture 和脱敏 registry。
- run outputs、logs、private evidence 不提交。
- dry-run 先验证机制，不夸大为“真实质量已验证”。

### 2.3 H8：Trial Readiness Audit

可复用资产：

- `docs/audits/S2-H8-TRIAL-READINESS-AUDIT.md`

已解决的问题：

- 明确 controlled trial 的前置条件。
- 确认 H1-H7.1 机制完整性。
- 明确 trial 不等于真实质量验证。

需要保留的原则：

- 进入真实试跑前必须通过 readiness audit。
- trial 只能证明机制路径，不自动证明 senior quality。
- trial 输出必须回到 sanitized issue / synthetic replay / generalized fix。

### 2.4 H9 / H9.1：PRD-only Gap Fix 与范围校准

可复用资产：

- `docs/audits/S2-H9-TRIAL-001-GAP-FIX.md`
- `docs/audits/S2-H9.1-SCOPE-CORRECTION.md`
- `skills/prd2proto/templates/input-quality-gate.md` 的 `input_document_type` 分类
- `schemas/feedback/diagnostic-summary.schema.json` 中的 prd2proto 输入类型字段

已解决的问题：

- 明确 PRD / MRD / roadmap / strategy brief / mixed / unknown 的输入类型识别。
- 避免 roadmap 或 MRD 被误当完整 PRD。
- 明确 uxeval 相关 evidence_type 校验应独立批次处理，不混入 PRD-only 测试路径。

需要保留的原则：

- 每个 batch 必须有明确 scope。
- 不要把不同输入形态、不同 skill 路径混在一个修复批次里。
- 先做 PRD-only，再做 screenshot / uxeval 专项。

---

## 3. 现有机制缺口：哪些必须改造

### 3.1 只有问题登记，没有候选修改协议

现有 `sanitized-issue` 能记录问题和 root cause，但没有定义：

- 候选修改是什么。
- 修改目标是 skill、prompt、template、schema、gate 还是 docs。
- 允许的 edit 操作是什么。
- 修改预算是多少。
- 修改为什么能解决问题。
- 修改对应哪个 synthetic replay。

需要补齐：

- `bounded-edit.schema.json`
- `fix-proposal.template.md`
- `edit_budget` 规则
- 修改前后 traceability

### 3.2 有 synthetic replay，但没有 validation gate

现有 `synthetic-replay-case.md` 能描述复现 case，但没有定义：

- gate 输入。
- gate 输出。
- hard gate 与 soft score。
- 通过 / 拒绝条件。
- 修复前后如何比较。
- 被拒绝的候选修改如何记录。

需要补齐：

- `validation-gate.schema.json`
- `gate-result.schema.json`
- hard gate 列表
- soft score rubric
- rejected edit buffer

### 3.3 有外部 workspace，但没有 staging/adopt

现有 workspace 负责存放运行产物，但没有定义：

- 候选修改如何 staged。
- staged proposal 应包含哪些信息。
- 人审通过后如何合入。
- 回滚路径是什么。
- 合入后如何记录 release note。

需要补齐：

- `staging-proposal.schema.json`
- `staging-proposal.md`
- `adopt-record.md`
- rollback checklist

### 3.4 有 root cause 枚举，但不够支持自进化

现有 root cause 包含：

`input_gap / template_gap / rule_gap / prompt_gap / schema_gap / runtime_gap / docs_gap / consistency_gap / privacy_gap / evidence_gap / validation_gap`

这对维护足够，但对自进化还不够。SkillOpt 启发下需要新增或映射：

- `skill_defect`：skill 规则缺失、错误、欠约束。
- `execution_lapse`：规则已存在，但执行器没有遵守。
- `input_insufficiency`：输入不足导致无法产出。
- `evaluator_gap`：评估器或 gate 无法识别问题。
- `standard_gap`：专业标准缺失或不明确。
- `process_gap`：流程阶段缺失或顺序错误。

需要补齐：

- root cause 二级分类。
- `skill defect vs execution lapse` 判定规则。
- root cause 到 fix target 的路由矩阵。

### 3.5 有质量门文档，但缺 eval adapter

现有 H4/H5/H5.1/H6 更多是模板与校验脚本，还不是完整的可运行 benchmark 环境。

需要补齐 DesignOS 版 `DataLoader / rollout / evaluator / adapter`：

- `DataLoader`：读取 synthetic / sanitized case。
- `rollout`：执行某个 skill 的标准任务。
- `evaluator`：按 hard gate / soft score 评分。
- `adapter`：把 skill 输出、gate、failure mode、KR 串起来。

---

## 4. SkillOpt 可复用机制清单

### 4.1 可直接复用为 DesignOS 标准的机制

| SkillOpt 机制 | DesignOS 应用 |
|---|---|
| skill 文档作为可优化文本状态 | skill / prompt / template 可被改进，但必须受控 |
| bounded edits | 每批只能有限修改，必须有 `edit_budget` |
| validation gate | 候选修改必须在独立 case 上证明变好 |
| staging proposal | 先提案，后人审合入 |
| rejected edits | 被拒绝的修改成为负样本 |
| train / val / test | 学习、选择、最终验证分离 |
| protected region | 隐私规则、质量门、核心标准不能被普通 edit 改写 |
| skill-aware reflection | 区分 skill defect 与 execution lapse |
| slow update | 阶段性总结长期指导，不频繁动主 prompt |
| meta skill | 优化器经验与正式 skill 分离 |

### 4.2 需要改造后复用的机制

| SkillOpt 机制 | 为什么不能直接照搬 | DesignOS 改造方式 |
|---|---|---|
| exact score / benchmark score | 产品设计质量不是简单 exact match | 引入 hard gate + senior design soft score |
| automatic replay | 真实 PRD / 截图有隐私风险 | 只跑 synthetic / sanitized replay，真实材料留 private evidence |
| auto-adopt | MVP / 内测阶段风险过高 | 默认禁止 auto-adopt |
| generic failure reflection | 设计问题需要专业方法论 | 绑定 senior design execution benchmark 与 failure modes |
| lexical recall | 设计问题不能只靠词相似 | 后续可用 issue type / skill / failure mode / KR 做结构化召回 |

### 4.3 暂不建议引入的机制

| 机制 | 暂缓原因 |
|---|---|
| 自动修改正式 prompts | 当前核心能力还在硬化阶段，风险过高 |
| 全量历史 session harvest | 隐私风险和噪声都高 |
| gate off / greedy accept | 容易把错误规则写入系统 |
| 自动 schedule nightly update | 需要先建立 gate 和 staging |
| 多 skill 同时自进化 | root cause 难以归因，容易交叉污染 |

---

## 5. 后续 Batch 依赖关系

### 5.1 总体依赖图

```text
当前 S2-H12/H13 核心输出硬化
  ↓
S2-EVO-PRE 本报告：策略和依赖清单
  ↓
S2-EVO-0 自进化协议层
  ↓
S2-EVO-1 复用并升级 H7/H8/H9 反馈安全层
  ↓
S2-EVO-2 root cause 与 skill-aware reflection 标准
  ↓
S2-EVO-3 bounded edit 与 edit_budget 标准
  ↓
S2-EVO-4 validation gate 设计
  ↓
S2-EVO-5 staging / adopt / rejected edit buffer
  ↓
S2-EVO-6 DesignOS eval adapter pattern
  ↓
S2-EVO-7 prd2proto pilot eval adapter
  ↓
S2-EVO-8 synthetic replay validation gate 跑通
  ↓
S2-EVO-9 受控持续改进机制（不 auto-adopt）
```

### 5.2 为什么必须先完成 S2-H12/H13

自进化不能替代核心能力建设。

如果 `prd2proto` 的产品设计推导链、视觉决策链、HTML demo 生成链本身还不稳定，过早引入自进化会出现两个问题：

- gate 没有可靠的质量目标。
- 优化器会围绕浅层输出做局部修补，不能补齐底层能力。

因此顺序必须是：

1. 先把核心 skill 输出能力建设到稳定达标。
2. 再用 validation / replay / feedback 证明和校准。
3. 最后才进入长期自进化。

---

## 6. 后续 Batch 详细执行清单

### S2-EVO-0：自进化协议层

**目标**：定义 DesignOS 受控自进化的总协议。

**输入依赖**：

- 本报告。
- SkillOpt 调研结论。
- H7A/H7B/H8/H9 现有机制。

**建议产物**：

- `docs/optimization/DESIGNOS-SKILLOPT-INSPIRED-PROTOCOL.md`
- `schemas/evolution/evolution-run.schema.json`
- `schemas/evolution/rollout-evidence.schema.json`
- `schemas/evolution/bounded-edit.schema.json`
- `schemas/evolution/validation-gate.schema.json`
- `schemas/evolution/staging-proposal.schema.json`
- `schemas/evolution/rejected-edit.schema.json`

**验收标准**：

- 明确不是自动优化器实现。
- 明确不读取 private evidence。
- 明确不修改 runtime / prompt。
- 明确所有自进化默认 review-first。

### S2-EVO-1：反馈安全层升级

**目标**：把 H7A/H7B/H8/H9 的反馈机制升级为 EVO 协议下的输入层。

**复用资产**：

- `diagnostic-summary.schema.json`
- `sanitized-issue.schema.json`
- `synthetic-replay-case.md`
- `sanitized-issue-registry.md`
- `S2-H7A/H7B/H8/H9` 报告。

**改造点**：

- 给 sanitized issue 增加 EVO 字段：`root_cause_classification_v2`、`candidate_replay_refs`、`validation_gate_refs`。
- 给 diagnostic summary 增加“是否可进入 evolution”的判断。
- 给 synthetic replay 增加 gate 期望字段。

**验收标准**：

- 不破坏现有 H7 validators。
- 不引入真实路径或真实内容。
- 可以从一个 sanitized issue 路由到 synthetic replay 和 gate。

### S2-EVO-2：Root Cause 与 Skill-Aware Reflection 标准

**目标**：建立 DesignOS 版 root cause 判定法。

**核心分类**：

- `skill_defect`
- `execution_lapse`
- `input_insufficiency`
- `evaluator_gap`
- `standard_gap`
- `process_gap`
- `privacy_gap`

**建议产物**：

- `docs/optimization/ROOT-CAUSE-CLASSIFICATION.md`
- `schemas/evolution/root-cause-classification.schema.json`
- `templates/evolution/root-cause-triage.md`

**验收标准**：

- 每个 root cause 都有判定问题、证据要求、fix target 路由。
- 明确“规则已存在但执行没遵守”不能直接改 prompt。
- 明确“输入不足”不能当作 skill 缺陷。

### S2-EVO-3：Bounded Edit 与 Edit Budget

**目标**：防止大批量低质量修改。

**建议产物**：

- `docs/optimization/BOUNDED-EDIT-STANDARD.md`
- `schemas/evolution/bounded-edit.schema.json`
- `templates/evolution/bounded-edit-proposal.md`

**建议规则**：

- 初期只允许 `append`、`replace`，谨慎允许 `insert_after`，禁止自动 `delete`。
- 每批必须声明 `edit_budget`。
- 一批默认只深修一个 prompt / template / schema。
- 所有 edit 必须绑定 issue、failure mode、KR、synthetic replay。

**验收标准**：

- 可以判断一个修改是否越界。
- 可以防止“token 不够所以高效补字段”。
- 可以沉淀 rejected edit。

### S2-EVO-4：Validation Gate 设计

**目标**：定义候选修改的接受 / 拒绝机制。

**hard gate 示例**：

- 隐私泄露。
- 过度承诺。
- inferred 被升级为 verified。
- 缺 traceability。
- 无视觉证据却宣称 visual-ready。
- 无生产验证却宣称 production-ready。

**soft score 示例**：

- senior reasoning quality。
- artifact completeness。
- traceability。
- gap honesty。
- interaction/state coverage。
- visual context fit。
- 可被中低阶设计师复用程度。
- 可被资深设计师接手评审程度。

**建议产物**：

- `docs/optimization/VALIDATION-GATE-STANDARD.md`
- `schemas/evolution/validation-gate.schema.json`
- `templates/evolution/validation-gate-result.md`

**验收标准**：

- 明确 pass / reject / needs_more_evidence。
- 明确修复前后对比方式。
- 明确 gate 不通过不能合入。

### S2-EVO-5：Staging / Adopt / Rejected Edit Buffer

**目标**：建立“建议先 staged，人工 adopt”的流程。

**建议产物**：

- `docs/optimization/STAGING-AND-ADOPT-PROTOCOL.md`
- `templates/evolution/staging-proposal.md`
- `templates/evolution/adopt-record.md`
- `templates/evolution/rejected-edit-registry.md`

**验收标准**：

- staging proposal 含：问题、root cause、edit、预期效果、gate 结果、rollback path。
- rejected edit 不被静默丢弃。
- auto-adopt 默认禁止。

### S2-EVO-6：DesignOS Eval Adapter Pattern

**目标**：定义每个 skill 的可运行评估四件套。

**四件套**：

- `DataLoader`：读取 synthetic / sanitized case。
- `rollout`：执行标准化任务。
- `evaluator`：输出 hard gate / soft score。
- `adapter`：连接 skill 输出、gate、KR、failure mode、traceability。

**建议产物**：

- `docs/optimization/DESIGNOS-EVAL-ADAPTER-PATTERN.md`
- `schemas/evaluation/eval-case.schema.json`
- `schemas/evaluation/eval-result.schema.json`
- `templates/evaluation/eval-adapter-readme.md`

**验收标准**：

- 不要求先实现所有 skill。
- 明确每个 skill 后续如何接入。
- prd2proto 作为第一个 pilot。

### S2-EVO-7：prd2proto Pilot Eval Adapter

**目标**：把 `prd2proto` 作为第一个可跑的 eval adapter 样板。

**输入依赖**：

- S2-H12/H13 完成。
- S2-EVO-0~6 完成。

**建议范围**：

- 只用 synthetic / sanitized PRD。
- 不读取 private evidence。
- 不生成 production-ready claim。
- 验证中间产物链，而不只看 HTML demo。

**验收标准**：

- 可跑一个 PRD-only synthetic case。
- 输出 hard gate / soft score。
- 输出 root cause 和 bounded edit proposal。
- 不自动修改 prompt。

### S2-EVO-8：Synthetic Replay Validation Gate 跑通

**目标**：证明一个候选修复可以被 gate 接受或拒绝。

**建议范围**：

- 选 1 个历史 synthetic replay。
- 制作 1 个 bounded edit proposal。
- 跑 gate。
- 产生 `accepted` 或 `rejected` 结果。

**验收标准**：

- gate 能拒绝至少 1 个不合格修改。
- gate 能接受至少 1 个合格修改。
- rejected edit 被记录。
- staging proposal 不直接合入。

### S2-EVO-9：受控持续改进机制

**目标**：进入长期循环，但仍不 auto-adopt。

**进入条件**：

- S2-H12/H13 已完成。
- prd2proto pilot adapter 跑通。
- validation gate 跑通。
- staging / rejected buffer 稳定。

**建议范围**：

- 每轮只处理 1~3 个 sanitized issue。
- 只召回同 skill、同 failure mode、同 root cause 的历史问题。
- 只生成 staging proposal。

**验收标准**：

- 能形成用户反馈到 release note 的闭环。
- 能防止重复修同类错误。
- 能持续积累 synthetic replay。

---

## 7. 任务间依赖矩阵

| Batch | 依赖 | 阻塞谁 | 说明 |
|---|---|---|---|
| S2-EVO-0 | 本报告 | 全部 EVO | 总协议，不先做会导致后面各自发明口径 |
| S2-EVO-1 | S2-EVO-0 + H7/H8/H9 | EVO-4/7/8 | 反馈记录是 gate 和 replay 的输入 |
| S2-EVO-2 | S2-EVO-0/1 | EVO-3/4/7 | 没有 root cause，bounded edit 不知道改什么 |
| S2-EVO-3 | S2-EVO-2 | EVO-5/7/8 | 没有 bounded edit，就无法 staging 和 gate |
| S2-EVO-4 | S2-EVO-1/2/3 | EVO-5/8/9 | 没有 gate，不能接受或拒绝修复 |
| S2-EVO-5 | S2-EVO-3/4 | EVO-9 | 没有 staging/rejected buffer，不能长期循环 |
| S2-EVO-6 | S2-EVO-4 | EVO-7/8 | 没有 adapter pattern，各 skill 会重复造轮子 |
| S2-EVO-7 | S2-EVO-6 + S2-H12/H13 | EVO-8/9 | prd2proto 是第一个 pilot |
| S2-EVO-8 | S2-EVO-7 | EVO-9 | 证明 gate 真实可运行 |
| S2-EVO-9 | S2-EVO-8 | 后续多 skill 扩展 | 进入长期循环 |

---

## 8. 与当前 S2-H12/H13 的关系

当前 `prd2proto` prompt hardening 仍是主线，不应被 EVO 打断。

建议顺序：

1. 继续完成 S2-H12.3：13/14 visual analysis / visual decision prompts。
2. 完成 15/16/17：HTML demo / traceability / gap report 相关链路硬化。
3. 做一次 S2-H12-FULL audit：检查 01-17 是否真的形成高级设计执行链。
4. 再进入 S2-EVO-0。

EVO 的作用不是补救当前 prompt 质量不足，而是在核心质量稳定后，提供长期、可控、可验证的迭代机制。

---

## 9. 后续给 Claude Code 的执行原则

所有后续 EVO 批次应遵守：

- 一批只做一个主题。
- 一批必须有明确 scope 和排除项。
- 默认不改 runtime。
- 默认不读 private evidence。
- 默认不 auto-adopt。
- 默认中文报告。
- 每批必须写清楚用户视角修复了什么、产品视角提升了什么、距离终极目标还差什么。
- 不能以“token 限制”为理由降低质量。
- 不能只做字符串检查就声称能力达标。
- 不能把一次真实试跑问题直接写死到通用 prompt。

---

## 10. 最终判断

现有 DesignOS 反馈机制不是废弃方案，而是后续自进化机制的输入层和安全层。

SkillOpt 提供的是更上层的受控优化思想：

- 如何产生候选修改。
- 如何限制修改规模。
- 如何验证是否变好。
- 如何拒绝错误修改。
- 如何 staging。
- 如何让长期反馈形成稳定闭环。

因此后续策略不是“重做反馈机制”，而是：

```text
复用 H7/H8/H9
  → 补 root cause 和 bounded edit
  → 补 validation gate
  → 补 staging / rejected buffer
  → 补 eval adapter
  → 先在 prd2proto 跑通
  → 再扩展到其他 skills
```

这条路径符合 DesignOS 的终极目标：不是等验证后大修大补，而是在正式验证前先具备稳定、高质量、可复用、可审计的资深设计执行能力，再用验证和用户反馈持续校准。
