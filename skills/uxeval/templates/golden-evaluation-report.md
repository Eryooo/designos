# Golden Output Template — uxeval

> **🚫 SYNTHETIC / SANITIZED ONLY** — 本模板及示例片段不含任何真实业务、真实客户、真实截图、真实账号、真实内部 URL。所有示例都用 `Acme Demo` / `synthetic-screenshot-001` 等明显假名占位。
> **本模板性质**:体验评估输出规范,"中阶可用 + 资深目标"双层基准。
> **依据**:S2-H1 §2.2(uxeval rubric)+ S2-H1.1 §6.2.2(KR-U1~U5)+ `skills/uxeval/constitution.md`(8 条硬约束)+ `knowledge/manifest.yaml` 中 `ux.*` 资产 + `knowledge/design-work-paradigm/20-22`。
> **当前状态**:**maturity = beta(S1-0B 实证偏乐观)**;**prompt-grade,无 runtime/ 目录**;pipeline 用 `gate:`(checkpoint 暂停门),**不是** kernel `quality_gates:`。

---

## 1. 输入前提

| 输入 | 强制 / 可选 | 说明 |
|---|---|---|
| `prd_file` 或 `feature_spec` | 强制 | 待评估的产品 PRD/特性说明 |
| `screenshots/` 目录 | 强制(client 模式) | 至少 5 张界面截图(synthetic / sanitized) |
| `screens-description.md` | 可选(client 模式) | 当 OCR 不可用时的人工说明 |
| `app_base_url` | 强制(web 模式) | 仅用于 sanitized demo 环境,**严禁真实生产 URL** |
| `mode` | 强制 | `client` / `web` |

---

## 2. 输出目录结构 / Artifact 列表

```
uxeval-out/<run_id>/
├── 01-需求理解.md                # PRD 结构化理解
├── 02-启发式映射.json            # 已选启发式 + 适用模块
├── 03-旅程地图.md                # 用户旅程
├── 04-任务清单-完整版.md         # 体验任务清单
├── 04-任务清单-简洁版.md         # 简洁版
├── 05-evidence/                  # 证据采集结果
│   ├── E-001-...
│   └── ...
├── 06-问题清单.json              # 结构化 issues(含 evidence_refs)
├── 06-问题报告.md                # 人读报告(可选)
└── delivery_assessment.json      # 交付状态
```

---

## 3. 必填章节(每条 issue 都要有)

每条 issue 必须含:

```yaml
- id: I-001
  title: <短描述>
  evidence_refs: [E-001, ...]   # 必须非空(constitution #1)
  severity: critical | major | minor | suggestion   # 必须 4 档之一(constitution #3)
  conflict_type: prd_missing_in_screenshot | screenshot_not_in_prd | none
  journey_stage: <对应旅程阶段 ID>
  task: <对应任务 ID>
  module: <对应功能模块>
  root_cause: <根因,不停留在表象>
  business_impact: <业务影响>
  user_impact: <用户影响>
  recommendation:
    what_to_change: <改什么>
    target_state: <改成什么>
    rationale: <为什么>
```

---

## 4. 字段级要求

### 4.1 evidence_refs(KR-U1)
- **必须非空**——空 evidence_refs 直接拒绝交付(constitution #1)
- 每个 ref 指向 `evidence/` 中的一个 `Evidence` 文件,且 `kind ∈ {screenshot, dom, trace, video}`
- evidence 路径**不可含真实账号/URL**(constitution #2)

### 4.2 severity(KR-U2)
- 严格 4 档枚举,**不允许** `P0` / `high` / `中` / `1` / `2` 等其他写法
- 等级标准:
  - `critical`:用户无法完成核心任务,或数据/资金/合规风险
  - `major`:能完成但显著阻碍效率,或多步骤绕过
  - `minor`:体验不佳但不影响完成
  - `suggestion`:优化建议,无直接影响

### 4.3 recommendation(KR-U3)
- 必须含三要素:`what_to_change` + `target_state` + `rationale`
- 严禁出现 "这里要改一下" / "需要优化" / "用户体验差" 等无可执行内容(constitution #5)

### 4.4 root_cause
- 必须指向具体的 heuristic 违反或交互模式问题
- 严禁 "用户体验差" / "不够直观" 等空泛词

### 4.5 conflict_type
- 必须显式标注;`out_of_scope` 用于"功能存在与否"问题(不是 uxeval 范围,constitution #4)

---

## 5. 最低线标准(中阶可用 — KR-U1~U5)

| KR | 要求 |
|---|---|
| KR-U1 | 每条 issue 的 `evidence_refs` 非空率 = 100% |
| KR-U2 | severity 字段用 4 档枚举合规率 = 100% |
| KR-U3 | 建议三要素覆盖率 ≥ 80% |
| KR-U4 | 敏感信息泄露(真实账号/姓名/内部 URL 全路径) = 0 |
| KR-U5 | pipeline.yaml `gate:` 暂停门接入率 ≥ 70%(目前 4 处 / 当前 stage 总数;`gate:` 是 checkpoint,**不是** kernel quality_gates) |

---

## 6. 目标线标准(资深可评审)

- **Coverage 矩阵齐全**:旅程阶段 × 角色 × 任务,每个 cell 有 issue 或显式标 "无问题"(不留空)
- **根因深度**:每条 issue 的 root_cause 指向具体 heuristic + 交互模式,且 ≥ 1 条 evidence 直接支撑根因(不只是支撑现象)
- **建议三要素覆盖率** ≥ 90%(KR-U3 目标线)
- **Issue 聚类**:同一 root_cause 的多条现象聚类为 1 条 issue,不重复(常见低阶失败:同一原因列 N 条 issue)
- **不只覆盖 happy path**:必须含 error / edge / permission / network 异常路径的 issue

---

## 7. 一票否决项检查表(V1-V4)

| # | 检查 | 触发条件 |
|---|---|---|
| **V1** Evidence 缺失 | 任一 issue 的 `evidence_refs` 为空 | 直接拒绝该 issue |
| **V2** 敏感信息泄露 | 出现真实账号 / 密码 / Token / API Key / 真实姓名 / 内部 URL 全路径 | 立即返工(constitution #2) |
| **V3** 严重等级越界 | severity 字段值 ∉ {critical, major, minor, suggestion} | 直接修正(constitution #3) |
| **V4** 建议不可执行 | "这里要改一下" / "用户体验差" 等空话,无三要素 | 标 "建议不可执行",列 gap |

---

## 8. Gap / Assumption / Confidence / Traceability 规范

| 字段 | 规范 |
|---|---|
| `gaps[]` | 评估覆盖不足的明确记录(如"未覆盖 X 旅程阶段") |
| `assumptions[]` | 评估时的假设(如"假设用户已登录") + 风险等级 |
| `confidence` | 整份评估报告的总体可靠性,基于 evidence 充分性(`ux.evidence-quality`) |
| `traceability` | 每条 issue 必须可追溯到:① 触发的 heuristic principle id ② 旅程阶段 ID ③ 任务 ID ④ evidence ID(全 4 维) |

---

## 9. 自评表(对账 KR)

```yaml
self_eval:
  KR-U1_evidence_refs_nonempty:
    actual: <非空 issue 数 / 总 issue 数>
    target: 100%
    pass: <bool>
  KR-U2_severity_enum_compliance:
    actual: <合规 issue 数 / 总 issue 数>
    target: 100%
    pass: <bool>
  KR-U3_recommendation_three_elements:
    actual: <三要素齐 issue 数 / 总 issue 数>
    target: ≥ 80%
    pass: <bool>
  KR-U4_sensitive_leak_count:
    actual: <scan-sensitive 命中数>
    target: = 0
    pass: <bool>
  KR-U5_gate_checkpoint_coverage:
    actual: <pipeline.yaml gate: 数 / 总 stage 数>
    target: ≥ 70%
    pass: <bool>
    note: "`gate:` 是 checkpoint 暂停门,非 kernel quality_gates"
  global_KR1.1_minimum_delivery:
    pass: <KR-U1~U4 是否全过>
  global_KR1.2_one_strike_count:
    pass: <V1~V4 是否全为 0>
  global_KR3.1_no_overclaim:
    pass: <文档中无禁止声明>
```

---

## 10. 禁止声明清单

- ❌ "uxeval 已达资深 UX 评估专家水平"
- ❌ "可替代专业 UX 研究员"
- ❌ "可作为合规/法律认证依据"
- ❌ "已经过真实用户测试验证"
- ❌ "uxeval 已接入 kernel quality_gates"(实际是 `gate:` 暂停门,无 runtime)
- ❌ "production ready" / "fully automated" / "完全自动化"

允许声明:

- ✅ "基于 Nielsen 启发式 + WCAG 部分覆盖的体验评估"
- ✅ "可识别明显可用性问题,生成结构化 issue 报告"
- ✅ "证据 → 问题 → 根因 → 建议 闭环"
- ✅ "适合内部 review 起点"

---

## 11. Synthetic 示例片段(中阶可用档,sanitized only)

> ⚠️ 所有数据为 synthetic;占位符:`Acme Demo Console`(假产品)、`synthetic-screenshot-001.png`(假截图)、`*.example.internal`(假域名占位)。

### 11.1 issue 中阶可用档示例

```yaml
- id: I-001
  title: "[synthetic] 用户在 'Acme Demo Console' 设置页保存按钮无 loading 反馈"
  evidence_refs: [E-001, E-002]
  severity: major
  conflict_type: none
  journey_stage: STAGE-03-settings-update
  task: T-12-update-profile
  module: settings
  root_cause: "违反 H4 系统状态可见性 — 异步操作无中间状态反馈,用户多次点击触发重复请求"
  business_impact: "重复请求增加后端负载,可能产生数据冲突"
  user_impact: "用户不确定操作是否成功,信任感下降"
  recommendation:
    what_to_change: "保存按钮点击后立即显示 loading 状态"
    target_state: "按钮文字变 '保存中...' + spinner,禁用点击,3s 超时切换为 'retry'"
    rationale: "符合 H4 + 防重复请求最佳实践;用户感知操作进行中"
```

### 11.2 evidence 文件示例

```yaml
# evidence/E-001.yaml
id: E-001
kind: screenshot
path: "evidence/synthetic-screenshot-001.png"   # synthetic-only
captured_at: "2026-06-12T10:00:00Z"
description: "[synthetic] Acme Demo settings 页保存按钮无视觉反馈"
related_heuristic: H4-system-status-visibility
sensitive_check: pass   # 无真实账号/姓名/内部 URL 全路径
```

### 11.3 delivery_assessment 示例

```yaml
delivery_assessment:
  status: reviewable
  confidence: 0.72
  coverage:
    journey_stages: 5/5
    roles: 2/2
    tasks: 12/12
  gaps:
    - "[synthetic] 未覆盖网络异常 fallback 路径(无对应 evidence)"
  assumptions:
    - "[synthetic] 假设所有用户已登录;未评估首次注册流程"
```

---

*template 结束。配套主报告:`docs/audits/S2-H2-GOLDEN-OUTPUT-TEMPLATES.md`。*
