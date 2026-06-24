# S2-H11-0 — 资深产品设计执行标准调研与 prd2proto 现状审计

> 性质:外部公开 benchmark 调研 + 当前 prd2proto 仓库证据审计。
> 范围:从 PRD 到原型的产品设计推理流程,不是单纯的 design system 对标。
> 安全声明:本报告未读取 private evidence、真实 PRD、截图、workspace run 产物或任何业务内容。

## 1. Executive Summary

DesignOS 当前真正需要对标的标准,不是"是否用了 design system"。Design system 只是后段的落地层,用于视觉一致性、组件、token、accessibility 和工程交付。

资深产品设计师标准应该是:系统能否先 critique PRD,定义正确问题,拆解目标,建模用户与任务,推导产品结构,推导流程与状态,推导 IA 与页面,基于这些决策实现 prototype,并用可追溯证据对结果做 critique。

当前 `prd2proto` 的方向是正确的:`pipeline.yaml` 定义了 reasoning-first 的 v2 pipeline, runtime 也 import 了 `kernel/quality-gates` 和 `kernel/traceability`。但它还不足以稳定保证高质量 HTML Demo:

- Source of truth 不一致:`pipeline.yaml` 是 v2 18-stage,但 `SKILL.md` 仍保留过时的 v1/8-stage 执行说明。
- PRD-to-prototype 推理链主要存在于 prompts/templates 中,并非每个关键质量判断都被 runtime 强制执行。
- 当前 quality gates 对 schema、traceability、code constraints、honesty 的保护更强;但对 product architecture、example dominance、visual-evidence readiness、verdict calibration 的保护不足。
- 当前状态可以支持低阶到部分中阶的结构化拆解,但不能诚实宣称"稳定产出资深可评审 prototype"。

## 2. 外部 Benchmark 来源

本报告不声称掌握 Google、Meta、腾讯、字节、阿里、Microsoft 的内部流程。这里只使用公开来源中可验证的 product design、enterprise design thinking、task analysis、IA、critique、inclusive design 方法。

| 来源 | 公开信号 | 对 DesignOS 的意义 |
|---|---|---|
| Google Design Sprint Kit | Design Sprint 阶段:Understand、Define、Sketch、Decide、Prototype、Validate。<https://designsprintkit.withgoogle.com/methodology> | 资深产品设计工作从理解和定义问题开始,不是直接生成 UI。 |
| GV Design Sprint | 用 5 天流程通过 design、prototype、customer testing 回答关键业务问题。<https://www.gv.com/sprint/> | Prototype 是回答关键问题的学习工具,不是"能点击 = 质量好"的捷径。 |
| IBM Enterprise Design Thinking | Hills、Playbacks、Sponsor Users;强调 user outcomes 而非 feature list。<https://www.ibm.com/design/approach/design-thinking/> 和 <https://www.ibm.com/training/enterprise-design-thinking/framework> | 要求 outcome framing、用户校准和阶段性 playback,而不是孤立地产出 artifact。 |
| NN/g Task Analysis | 系统研究用户如何完成 task 以达成 goal。<https://www.nngroup.com/articles/task-analysis/> | 把功能列表转成 user goals、tasks、steps、decision points。 |
| NN/g User Journeys vs. User Flows | Journey 和 flow 都应围绕 user goals 与用户视角。<https://www.nngroup.com/articles/user-journeys-vs-user-flows/> | 防止按公司模块或产品模块中心来设计流程。 |
| NN/g Journey Mapping 101 | Journey map 可视化一个人为了完成目标所经历的过程。<https://www.nngroup.com/articles/journey-mapping-101/> | 页面生成前需要 timeline、actions、thoughts/emotions、pain points。 |
| NN/g Information Architecture | IA 包含 structure、organization、labeling、navigation、information-seeking behavior。<https://www.nngroup.com/articles/ia-study-guide/> | IA 不等于 sitemap 或菜单列表。 |
| NN/g Critique in the AI Era | Design judgment 应被编码成明确评价标准。<https://www.nngroup.com/articles/ai-era-critique/> | 支撑 DesignOS 的 gates、failure modes、rubric-driven critique。 |
| Atlassian Problem Framing | 定义问题的性质、影响、位置和价值。<https://www.atlassian.com/team-playbook/plays/problem-framing> | 适用于 PRD intake 前的问题定义。 |
| Microsoft Inclusive Design | Inclusive design 是构建包容体验的方法;accessibility 和 inclusion 是产品质量的一部分。<https://inclusive.microsoft.design/> | 适用于后段 interaction、accessibility、visual-system readiness。 |

## 3. 十个资深产品设计能力域

后文评分规则:

- 0 = 不存在
- 1 = 过时或互相冲突的文档
- 2 = prompt/template 层指导
- 3 = partial runtime execution
- 4 = runtime enforced + test coverage
- 5 = 多个真实/合成 case 验证稳定

### 3.1 Benchmark Table

| # | 能力域 | 资深标准 | 中阶最低线 | 低阶表现 | 一票否决 | DesignOS 应有产物 | 当前 prd2proto 分数 |
|---|---|---|---|---|---|---|---|
| 1 | Problem Framing | 在进入方案前定义问题性质、影响、受影响用户、业务价值、约束和风险。 | 能说明业务目标和用户问题,并至少给出一个可衡量成功信号。 | 把 PRD bullet 直接转成页面。 | 没有问题定义却宣称方案可评审。 | problem_statement、success_metrics、constraints、risk_log。 | 2 |
| 2 | Input / PRD Critique | 判断输入类型和粒度,并决定它能支撑到什么输出保真度。 | 能区分 PRD、roadmap、MRD,并记录 gaps/assumptions。 | 把任何信息密集文档都当成 prototype-ready PRD。 | 输入无法支撑目标产出,但 pipeline 不降级继续。 | input-quality-gate、requirement_inventory、gap ledger。 | 3 |
| 3 | Goal Decomposition | 拆解 business/product/user/experience goals,并连接到 metrics。 | 能提取业务/用户目标与优先级。 | 只列功能。 | 没有 goal trace,但设计决策用确定口吻表达。 | design_objectives、goal_derivation_map。 | 3 |
| 4 | User / Task Modeling | 把功能转为 user goals、top tasks、task steps、hidden tasks、priority。 | 定义目标用户和主要任务。 | 只有 persona 标签,没有 task model。 | 关键流程没有 user goal 或 task owner。 | user_task_map、top_tasks、hidden_tasks。 | 3 |
| 5 | Domain / Product Model | 建模 domain objects、information objects、permissions、states、modules、scenario roles。 | 定义核心对象/模块和基础关系。 | 让一个详细示例变成产品架构。 | representative scenario 覆盖 product foundation。 | product_archetype、product_foundation_map、domain_model。 | 1 |
| 6 | Journey / Flow / State | 推导 main、exception、cross-role、permission、recovery、interruption flows。 | 覆盖主路径 + loading/empty/error 基础状态。 | 只有 happy path 或一个 demo path。 | 缺 failure/recovery states 却声称完整流程。 | business_flow、journey_map、page_flow、state_matrix。 | 3 |
| 7 | IA / Navigation / Surface Model | 按 tasks/roles/status 组织信息,定义 shells、surfaces、navigation levels、page inventory。 | 产出 IA、pages、routes 和 navigation rationale。 | 扁平模块菜单或泛化 admin sidebar。 | navigation 无 task rationale 或 product surface model。 | information_architecture、site_map、surface_model。 | 2 |
| 8 | Page / Interaction Design | 定义 page structure、content hierarchy、component strategy、interaction rules、responsive behavior。 | 覆盖关键页面、内容区域、组件选择和关键状态。 | 使用通用 cards/forms,缺少产品特定层级。 | 核心页面缺内容层级或交互状态。 | page_structure、component_strategy、interaction_rules。 | 3 |
| 9 | Visual / Design System / Accessibility | 使用已提供的 visual evidence、tokens、design system;若缺失则降级为 structural fidelity。 | 使用 component library 并标注视觉假设。 | 把 AntD/Tailwind 默认样式当作产品视觉方向。 | 无 visual source 却声称 visual-review-ready。 | design_spec、design_tokens、visual_source_status、accessibility checks。 | 1 |
| 10 | Prototype / Traceability / Critique | Prototype 消费上游 assets;traceability、gap、assumptions、confidence、critique 驱动 verdict。 | 产出 clickable prototype + traceability + gap report。 | 把 smoke test 当成质量 verdict。 | coverage 低或有 critical gaps 却 verdict 为 review-ready。 | prototype_code、traceability_map、professional_gap_report、self-review。 | 3 |

当前总分:24 / 50。这不是 senior-stable system,而是一个方向正确、已有部分 runtime-grade 基础的 reasoning-first pilot。

## 4. 当前 Source of Truth 盘点

| Artifact | 当前角色 | 证据 | 判断 |
|---|---|---|---|
| `skills/prd2proto/pipeline.yaml` | 理论主真源 | v2 18-stage pipeline,从 `input-diagnosis` 到 `liveness-check`。 | 战略方向正确。 |
| `skills/prd2proto/SKILL.md` | 用户可见 skill contract | Frontmatter 写 Pipeline v2 17 stages,正文仍有旧 8-stage overview 和 legacy output structure。 | 过时/冲突。 |
| `skills/prd2proto/prompts-v2/` | Stage prompts | 17 个 stage prompts 存在。 | Prompt 覆盖较强,但 prompt-level control 仍可能被 ad-hoc demo generation 绕过。 |
| `skills/prd2proto/templates/input-quality-gate.md` | 执行前 input gate 模板 | 包含 `input_document_type` 与 `can_generate_prototype_from_input`。 | S2-H9 hardening 有价值,但除非 runner 执行,否则仍是 template-level。 |
| `skills/prd2proto/templates/progressive-quality-checkpoints.md` | 执行中 checkpoint 模板 | CP-P1~P5,decision 包括 continue、continue_with_gaps、ask_user、degrade_scope、stop_blocked。 | 流程设计正确,但不是完全 runtime-hard。 |
| `skills/prd2proto/templates/self-review-gate.md` | 交付前 self-review 模板 | 检查 KR、FM、golden-template、gap/assumption/confidence/traceability。 | 有用,但如果 thresholds 弱,仍可能 verdict inflation。 |
| `skills/prd2proto/eval/failure/failure-modes.md` | Skill failure mode library | 8 条 FM 覆盖 schema、traceability、code constitution、honesty、gap、assumption、stage chain、state coverage。 | 缺 product-architecture 与 visual-evidence failure modes。 |
| `skills/prd2proto/runtime/executor.py` | Runtime executor | Import prompt loader、LLM client、schema validator、quality gates、traceability。 | 当前所有 skill 中 runtime 基础最强。 |
| `skills/prd2proto/tests/` | Regression tests | 测 pipeline load、gate semantics、liveness final stage、reality hardening。 | 锁住了基础设施,但对产品设计质量覆盖不足。 |

## 5. PRD-to-HTML Trace Chain 现状

| 链路步骤 | 是否存在 | 强制方式 | 主要缺口 |
|---|---:|---|---|
| PRD input | 是 | Input template + runtime inputs | PRD granularity 未始终绑定最终 fidelity cap。 |
| Input diagnosis | 是 | Runtime stage + gap gate | 基础好;仍需扩展 role/granularity/product-readiness。 |
| Design objectives | 是 | Runtime stage + schema/inference gates | Goal chain 存在;需增强 metric 和 problem-framing linkage。 |
| Product archetype | 是 | Runtime stage + schema gate | 对 product foundation/module/surface modeling 太弱。 |
| User task model | 是 | Runtime stage + traceability/inference gates | 基础好;需 top-task 与 scenario-role weighting。 |
| Business flow | 是 | Runtime stage | 需要 explicit example-only vs product-core guard。 |
| Journey map | 是 | Runtime stage | 需增强 cross-role/exception/recovery coverage。 |
| IA | 是 | Runtime stage + traceability gate | IA prompt 是 task-oriented,但缺 product shell/surface model enforcement。 |
| Page flow | 是 | Runtime stage | 需要 coverage-by-role,而非只看总 page 数。 |
| Page structure | 是 | Runtime stage | 页面结构基础可用;产品特定 hierarchy 仍弱。 |
| Component strategy | 是 | Runtime stage | 主要是 implementation/component choice,不够覆盖 product visual strategy。 |
| State matrix | 是 | Runtime stage | 状态层有帮助,但 visual/demo verdict 未与 state completeness 强绑定。 |
| Interaction rules | 是 | Runtime stage | 层次正确,但可被外部 ad-hoc prototype generation 绕过。 |
| Design spec | 是 | Prompt stage | 无 visual source 时可能发明视觉方向。 |
| Tokens | 是 | Prompt stage | Token 可能在无视觉证据时被推断。 |
| Prototype code | 是 | Prompt stage + code constraint gate | Code constraints 保护实现质量,不保护产品设计质量。 |
| Traceability | 是 | Runtime/prompt + tracer | 方向强;实际 run 中需要核查 evidence coverage。 |
| Professional gap report | 是 | Prompt stage | 需要与 coverage/gaps/visual evidence 强绑定的硬 verdict thresholds。 |
| Liveness / URL | 是 | Final stage/test expectation | 只能证明可运行,不能证明设计质量。 |

## 6. Quality Constraint Audit

| Constraint | 生效阶段 | 当前状态 | 能否防止低质量 clickable demo? | 风险 |
|---|---|---|---|---|
| Input Quality Gate | 执行前 | 有 PRD type classification 模板。 | 部分可以。能识别 roadmap/MRD vs PRD,但 product-model 与 visual-readiness criteria 不足。 | Medium |
| Progressive Checkpoints | 执行中 | 有 CP-P1~P5 模板。 | 部分可以。能降级,但依赖人工/runner 是否执行。 | Medium |
| Cross-Skill Consistency | Skill 间 | 有 contract docs。 | 能防止 assumption/gap 漂移,但不能直接保证 visual/demo quality。 | Medium |
| Self Review Gate | 交付前 | 有模板。 | 如果 verdict thresholds 弱,仍不能阻止"clickable = review-ready"。 | High |
| Failure Modes | 执行中/自评 | 有 8 条 FM。 | 缺 example dominance、architecture flattening、visual fallback overclaim、verdict inflation。 | High |
| Traceability | 生成后 | Runtime/tracer 存在。 | 能解释决策,但不能单独确保产品架构正确。 | Medium |
| Professional Gap Report | 生成后 | Prompt 存在。 | 能识别 gap,但当前 trial 证明仍可能高估 readiness。 | High |
| Liveness / Smoke | 交付检查 | Final stage 和测试要求 dev URL。 | 不能。它只证明 runnability/clickability。 | 若被当作质量代理则 High |

## 7. 替代能力判断

| 目标 | 当前判断 | 证据 | 缺失能力 |
|---|---|---|---|
| 替代低阶设计师 | 可部分达成,尤其是结构化拆解和简单 clickable scaffolds。 | v2 pipeline、prompts-v2、templates、runtime executor。 | 需要稳定 demo 质量和更强 page/surface model。 |
| 替代中阶设计师 | 尚不稳定。 | IA/page/state/traceability 链路较好,但 product-model 和 visual-readiness 缺口仍大。 | Product foundation modeling、role weighting、visual evidence gates、verdict thresholds。 |
| 资深可评审输出 | 尚未达成。 | Professional gap report 和 self-review 已存在,但 S2-H10.1 暴露 verdict inflation。 | Senior-level problem framing、architecture decisions、visual evidence handling、critique thresholds。 |
| 稳定资深输出 | 未达成。 | 缺 multi-case validation; prompt/template controls 并非全部 runtime-hard。 | Runtime enforcement、synthetic/real case matrix、hard reject/degrade rules。 |

## 8. Product/User Impact

如果当前流程直接使用,用户仍可能拿到一个 clickable demo,但它会:

- 过度放大一个详细 example workflow,弱化 product foundation;
- 把 multi-surface product 压平成 generic admin sidebar;
- 把 component library default 当作 visual direction;
- 把 liveness/smoke success 当作 product-design quality;
- 在 coverage 低或存在 critical gaps 时,仍把 partial prototype 标成 review-ready。

这与 S2-H10.1 暴露的问题一致。问题不是"没有流程",而是"正确流程在 product architecture、visual evidence、verdict boundaries 上还不够硬"。

## 9. Recommended Next Batches

### 9.1 Minimum Truth Fix

| Batch | Goal | Scope | Acceptance |
|---|---|---|---|
| S2-H11-A | Align source of truth | 只改文档:对齐 SKILL.md、pipeline.yaml、templates。 | 只有一个官方 v2 flow,无过时 8-stage public contract。 |
| S2-H11-B | 增加 senior product-design failure modes | 增加 example dominance、architecture flattening、visual fallback overclaim、verdict inflation 的 FM。 | Self-review 能阻断这四类失败。 |
| S2-H11-C | Calibrate prototype verdict | 为 structural/clickable/visual-review-ready 建硬阈值。 | Liveness/smoke 不能推出 review-ready。 |

### 9.2 Intermediate Stable Output

| Batch | Goal | Scope | Acceptance |
|---|---|---|---|
| S2-H12-A | Product model hardening | 增加 product foundation、core module、representative scenario、example-only 分类。 | 详细 example 不能主导 IA/prototype。 |
| S2-H12-B | Surface/IA hardening | 增加 host shell、product shell、surfaces、context navigation、page inventory。 | Prototype 先覆盖 product foundation 和 core surfaces。 |
| S2-H12-C | Synthetic replay matrix | 增加 example dominance、architecture flattening、no visual source、low coverage 合成 cases。 | 修复前测试失败,修复后通过。 |

### 9.3 Senior Reviewable Output

| Batch | Goal | Scope | Acceptance |
|---|---|---|---|
| S2-H13-A | Visual-evidence readiness | 增加 `visual_source_status` 和 `visual_fidelity_mode` 规则。 | 无 visual source 就不能声称 visual-review-ready。 |
| S2-H13-B | End-to-end quality ceiling trial | 仅外部 workspace;提供充分 PRD + visual references + IA + screenshots。 | Prototype 按 product architecture、visual reference、traceability、UX criteria 评审。 |
| S2-H13-C | Multi-case stability | 用代表性产品类型跑 sanitized/synthetic replay cases。 | 各 case 的 pass/degrade/block 决策稳定。 |

## 10. Knowledge / Template Library 建议

本 benchmark 被接受后,应沉淀为可复用知识资产。建议资产:

`knowledge/design/product-design/senior-product-design-execution-standard.md`

每个能力域建议包含:

- purpose
- methodology
- decision_rules
- quality_standard
- required_inputs
- required_outputs
- evidence_required
- failure_modes
- not_allowed_claims
- template_hooks
- applicable_skills

不要立即拆成十个资产。先建立一个 source-of-truth 资产,优先接入 `prd2proto`,真实消费后再按需拆分。

## 11. Safety Statement

本报告只读取了仓库文件和公开 web source。未读取 private evidence、真实 PRD、截图、外部 workspace outputs 或 prototype 文件。不包含任何私有业务内容。

本文件写入后需运行:

- `python3 scripts/security/scan_sensitive.py`
- `python3 -m unittest tests/security/test_scan_sensitive.py`
- `git diff --check`

