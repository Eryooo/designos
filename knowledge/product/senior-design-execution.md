# 资深产品设计执行标准（Senior Design Execution）

> Domain: product | Type: methodology | Status: pilot
> Public benchmark synthesis: Google/GV Design Sprint、IBM Enterprise Design Thinking、
> NN/g Task Analysis / Journey / IA / Critique、Atlassian Problem Framing、Microsoft
> Inclusive Design。
>
> 本资产是 DesignOS 从 PRD 到 prototype 的共享产品设计执行标准。它不是某个
> skill 的 prompt,也不是 design system 规范。Design system 只属于第 9 域
> Visual / Design System / Accessibility。

## purpose

把"资深设计师如何理解 PRD、拆解目标、建模任务、推导 IA/页面/流程、判断原型质量"沉淀为可复用的共享知识资产,供各 skill 在需要产品设计推理时引用。

本资产重点解决:

1. 防止把 PRD 直接转页面,跳过问题定义与目标拆解。
2. 防止把某个详细 example flow 放大成整个产品架构。
3. 防止把 runnable / clickable prototype 误判为 senior-reviewable output。

## applies_to

- PRD → 设计推理资产 → prototype 的生成型能力。
- 竞品 / 用户 / 策略分析能力,需要对齐 problem framing、goal decomposition、user/task modeling。
- 体验评估能力,需要反查 journey / flow / state、IA、page interaction、prototype critique。
- IP / 品牌人格设计能力,仍需基于 problem framing 与目标拆解。
- 品牌策略 / 视觉系统能力,需消费 problem framing、goal decomposition 与 visual readiness。

## source_assets

- Google Design Sprint Kit: Understand / Define / Sketch / Decide / Prototype / Validate。
- GV Design Sprint: 用 prototype + customer test 回答 critical business questions。
- IBM Enterprise Design Thinking: Hills / Sponsor Users / Playbacks,强调 user outcomes。
- NN/g Task Analysis: 围绕用户如何完成目标来拆 task。
- NN/g User Journeys / User Flows: 从用户目标和用户视角描述过程。
- NN/g Information Architecture: IA 包含 structure / organization / labeling / navigation。
- NN/g Critique in the AI Era: 把 design judgment 编码成明确评价标准。
- Atlassian Problem Framing: 定义问题性质、影响、位置与价值。
- Microsoft Inclusive Design: 包容性与 accessibility 属于产品质量。

## senior_execution_domains

### 1. Problem Framing

**methodology**: 进入方案前先回答"为什么要解决这个问题"。拆出 business problem、user problem、affected users、success signal、constraints、risks。

**decision_rules**:
- 没有 problem statement,不得进入 review-ready 原型宣称。
- 只有功能列表时,必须先转成 problem + outcome。
- 业务目标和用户目标冲突时,必须显式列出 trade-off。

**quality_standard**:
- 中阶最低线:至少有业务目标、用户问题、一个可衡量成功信号。
- 资深线:有 problem framing、约束、风险、取舍和验证策略。

**failure_modes**:
- 把功能清单当问题定义。
- 只写"提升效率/优化体验",没有指标或用户场景。
- 没有说明为什么当前方案优先。

**template_hooks**: `problem_statement`, `business_goal`, `user_problem`, `success_metrics`, `constraints`, `risk_log`

### 2. Input / PRD Critique

**methodology**: 先判断输入类型,再判断它能支撑什么输出。区分 PRD、MRD、roadmap、strategy brief、mixed input。

**decision_rules**:
- Roadmap/MRD 只能支撑目标/模块/方向推导,不能直接支撑完整 prototype。
- 功能级 PRD 默认最多支撑 structural/clickable partial prototype。
- 页面级 PRD + 状态 + visual source 才可能支撑 visual-review-ready prototype。

**quality_standard**:
- 中阶最低线:识别输入类型、缺口、假设和是否可继续。
- 资深线:明确 output fidelity cap,并把 gap/assumption 传递到后续产物。

**failure_modes**:
- 把信息密集的 roadmap 当 PRD。
- 把功能级 PRD 当页面级 PRD。
- 输入不足却不降级。

**template_hooks**: `input_document_type`, `document_type_confidence`, `can_generate_prototype_from_input`, `minimum_prd_requirements_missing`, `input_decision`

### 3. Goal Decomposition

**methodology**: 拆解 business goal、product goal、user goal、experience goal,并建立指标和优先级。

**decision_rules**:
- 没有 goal trace 的设计决策只能标 `[inferred]`。
- 页面、流程、组件优先级必须能回到目标优先级。
- 目标之间冲突时,必须给出裁定依据。

**quality_standard**:
- 中阶最低线:业务/用户目标清楚,有优先级。
- 资深线:目标链路可追溯,每个关键设计决策能说明服务哪个目标。

**failure_modes**:
- 只有 feature priority,没有 goal priority。
- 指标缺失却宣称目标明确。
- 体验目标与业务目标脱节。

**template_hooks**: `business_goals`, `product_goals`, `user_goals`, `experience_goals`, `goal_derivation_map`, `metric_map`

### 4. User / Task Modeling

**methodology**: 从功能转成用户要完成的任务。识别 top tasks、JTBD、task steps、hidden tasks、任务频率和任务风险。

**decision_rules**:
- 不能只写 persona 标签,必须写任务。
- 高频/高风险任务优先于低频配置项。
- hidden tasks(错误恢复、批量、协作、权限)必须显式检查。

**quality_standard**:
- 中阶最低线:主要用户和主要任务清楚。
- 资深线:任务优先级、隐藏任务、边界任务和证据来源完整。

**failure_modes**:
- 角色清单替代 task model。
- 只覆盖 happy task。
- 把后台管理模块当用户任务。

**template_hooks**: `target_users`, `top_tasks`, `job_to_be_done`, `task_steps`, `hidden_tasks`, `task_priority_matrix`

### 5. Domain / Product Model

**methodology**: 抽象产品底层对象、信息对象、模块、权限、状态机和关系。区分 product foundation、core module、representative scenario、example_only。

**decision_rules**:
- Representative scenario 不能覆盖 product foundation。
- 详细 example flow 只能作为 proof-of-flow,不能决定主导航架构。
- Domain objects 不清楚时,IA 和 page model 必须降级。

**quality_standard**:
- 中阶最低线:核心对象、模块和基础关系明确。
- 资深线:对象关系、权限、状态、模块边界和 scenario role 可追溯。

**failure_modes**:
- Example dominance:一个详细例子主导整个产品。
- Architecture flattening:复杂产品被压平成通用 admin sidebar。
- 权限/状态机缺失。

**template_hooks**: `product_foundation_map`, `core_module_map`, `domain_objects`, `information_objects`, `permission_model`, `scenario_role`

### 6. Journey / Flow / State

**methodology**: 从用户目标推导主流程、异常流程、跨角色流程、权限流程、恢复流程和中断状态。

**decision_rules**:
- 只有 happy path 不得称为完整流程。
- 关键流程必须覆盖 loading / empty / error / permission / success / retry / interruption。
- 跨角色流程必须标出 handoff 与责任边界。

**quality_standard**:
- 中阶最低线:主流程和基础异常态齐全。
- 资深线:异常、恢复、中断、权限、跨角色协同都可追溯。

**failure_modes**:
- 状态矩阵只覆盖默认态。
- 流程无法恢复或无法解释失败。
- Journey 按系统步骤而非用户目标组织。

**template_hooks**: `main_flow`, `exception_flows`, `recovery_flows`, `permission_flows`, `state_matrix`, `journey_map`

### 7. IA / Navigation / Surface Model

**methodology**: IA 不只是 sitemap。它包含结构、组织、标签、导航、搜索/发现路径、工作区和产品 surface。

**decision_rules**:
- 导航必须说明按 task / role / status / module 哪个维度组织。
- P0 task 应在浅层可达。
- 多 surface 产品必须先定义 host shell、product shell、primary workspace、management surface。

**quality_standard**:
- 中阶最低线:页面清单、路由、导航层级和入口关系清楚。
- 资深线:信息组织原则、surface model、导航取舍和扩展位完整。

**failure_modes**:
- Generic admin sidebar。
- Sitemap 有页面但无任务依据。
- 多产品 surface 被混成一个菜单。

**template_hooks**: `information_architecture`, `surface_model`, `host_shell`, `product_shell`, `primary_workspaces`, `navigation_rationale`, `page_inventory`

### 8. Page / Interaction Design

**methodology**: 页面由内容层级、布局区域、组件策略、交互规则和响应式策略共同决定,不是简单摆组件。

**decision_rules**:
- 核心页面必须有 L1/L2/L3 内容层级。
- 每个关键组件必须有状态和交互规则。
- 响应式不能只靠组件库默认行为。

**quality_standard**:
- 中阶最低线:关键页面结构、内容区域、组件选择和主要状态明确。
- 资深线:页面结构服务任务优先级,交互细节与状态矩阵一致。

**failure_modes**:
- 页面用通用 card/form 填充,缺产品信息层级。
- 缺空态、错态、加载态、权限态。
- 组件选择无法解释。

**template_hooks**: `page_structure`, `content_hierarchy`, `component_strategy`, `interaction_rules`, `responsive_rules`, `state_coverage`

### 9. Visual / Design System / Accessibility

**methodology**: 视觉必须有来源。Design system 用于一致性和落地,但不能替代产品设计推理。

**decision_rules**:
- 无 screenshots / design system / brand tokens / reference UI 时,不得称为 visual-review-ready。
- Component library default 只是 implementation choice,不是 visual direction。
- Accessibility 与 inclusive design 是质量要求,不是可选附加项。

**quality_standard**:
- 中阶最低线:组件库选择、基础 tokens、视觉假设标注清楚。
- 资深线:视觉证据、token、组件、品牌语言、accessibility 均可追溯。

**failure_modes**:
- Visual fallback overclaim。
- 把 AntD/Tailwind 默认风格当产品视觉。
- 没有 accessibility 检查。

**template_hooks**: `visual_source_status`, `visual_fidelity_mode`, `design_tokens`, `component_library`, `accessibility_checklist`, `visual_comparison`

### 10. Prototype / Traceability / Critique

**methodology**: Prototype 必须消费上游推理资产。交付前必须做 traceability、gap、assumption、confidence、failure-mode 和 verdict 检查。

**decision_rules**:
- Liveness / smoke test 只能证明可运行,不能证明设计质量。
- Coverage 低或有 critical gap 时,不得 review-ready。
- 所有推断必须进入 assumption/inferred ledger。

**quality_standard**:
- 中阶最低线:可点击 prototype + traceability + gap report。
- 资深线:prototype 决策可追溯,verdict 与 evidence/gap/coverage 一致。

**failure_modes**:
- Verdict inflation。
- Traceability 断裂。
- Gap/assumption 丢失。
- 代码可运行但产品结构错误。

**template_hooks**: `prototype_code`, `traceability_map`, `professional_gap_report`, `self_review_gate`, `coverage_by_role`, `delivery_verdict`

## decision_framework

出现输入、流程、视觉证据或产出质量争议时,按以下顺序裁定:

1. 输入是否足以支撑目标输出?不足则降级或追问。
2. 是否有明确 problem / goal / task?没有则不得进入高置信设计。
3. 是否有 product foundation?没有则不得让代表流程主导 IA。
4. 是否覆盖关键 journey / flow / state?没有则不得称完整。
5. 是否有 visual source?没有则不得称 visual-review-ready。
6. 是否有 traceability / gap / assumption?没有则不得称 senior-reviewable。
7. 是否通过多 case 验证?没有则不得称 stable senior output。

## quality_rubric

| Level | 判定 |
|---|---|
| Junior | 能把 PRD 转成页面草图或简单 demo,但缺目标、任务、状态、追溯。 |
| Intermediate | 能产出目标、任务、IA、页面、状态和可点击 prototype,并显式记录 gap。 |
| Senior reviewable | 能做问题定义、目标取舍、product model、IA/surface 决策、视觉证据判断和 traceable critique。 |
| Stable senior output | 上述能力被 runtime/test/multi-case validation 稳定证明。 |

## not_allowed_claims

- 不得说"只要 PRD 足够长就可以生成高质量 prototype"。
- 不得把 roadmap/MRD 当成完整 PRD。
- 不得把 component library default 当成 visual direction。
- 不得把 liveness/smoke pass 当作 design quality pass。
- 不得在缺 visual source 时宣称 visual-review-ready。
- 不得在缺 multi-case validation 时宣称 stable senior output。

## template_library

后续模板库应从本资产派生,但不应先建立第二套真源。建议优先派生:

1. PRD Critique Template
2. Goal Decomposition Template
3. User / Task Modeling Template
4. Domain / Product Model Template
5. Journey / Flow / State Template
6. IA / Navigation / Surface Template
7. Page / Interaction Design Template
8. Visual Evidence Readiness Template
9. Prototype Traceability Template
10. Senior Design Critique Template

## do_not_claim

- 本资产不是 Google/Meta/腾讯/字节/阿里内部流程复刻。
- 本资产不替代真实用户研究、产品战略、视觉设计系统或可用性测试。
- 本资产只是 DesignOS 的公开 benchmark synthesis,需要通过 skill 接入和多 case 验证证明有效。
