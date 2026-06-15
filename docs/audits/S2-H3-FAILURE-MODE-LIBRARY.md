# S2-H3 — Failure Mode Library

> **本报告性质**:整合 5 个核心 skill 的 skill-specific failure mode library,作为 S2-H1 rubric / S2-H1.1 OKR / S2-H2 golden template 的**配套失败检测层**。
> **不新建第二套通用 failure library** — 通用真源仍是已有 3 份(`design-work-paradigm/18-failure-modes.md` / `design/quality/common-failure-modes.md` / `design/quality/brand-creative-failure-modes.md` + skill 对应 `ux.ux-failure-modes`)。
> **放置规则**:严格遵守 `S2-H2.2-KNOWLEDGE-ARCHITECTURE-GUARDRAILS.md` §4 — skill-specific 配套层在 `skills/<skill>/eval/failure/failure-modes.md`,引用通用真源而非复制。
> **日期**:2026-06-12

---

## 1. Failure Mode 的统一定义

| 概念 | 含义 |
|---|---|
| **Failure mode** | 不达标输出的**可检测、可对账的反模式**——不是 bug,是"产出长得不对"的语义级失败 |
| **三要素** | detection_signal(怎么识别)+ trigger_condition(什么条件触发)+ delivery_decision(是否阻断交付) |
| **不是什么** | 不是 OKR(那是目标层 H1.1)、不是 rubric(那是评分层 H1)、不是 schema 违例(那是技术层 kernel/quality-gates)、不是真实 case(那是 skill `eval/failure/case-*` 的职责) |
| **使用纪律** | 由 S2-H4 self review gate 跑自检;命中 blocker → block;命中 major → degrade;命中 minor → warn;命中 gap → 显式标 gap 不阻断 |

### 1.1 字段级规范(每个 FM 必有 13 字段)

```
id · name · applies_to · related_kr · related_golden_template_section
source_reference · severity · detection_signal · trigger_condition
examples_synthetic_only · remediation · delivery_decision
not_allowed_claims · traceability_requirement
```

### 1.2 严重度三级

| severity | 含义 | delivery_decision 默认值 |
|---|---|---|
| **blocker** | 一票否决项命中,产物不达交付资格 | block |
| **major** | 单维度严重不足,需返工补强 | degrade(可降级声明) |
| **minor** | 局部改进点 | warn(可标 gap 后放行) |

### 1.3 与 design-work-paradigm/18 三态对齐

| 本报告 | design-work-paradigm/18 |
|---|---|
| `block` | `blocked` |
| `degrade` / `gap` | `fallback` |
| `warn` | `warning` |

**不发明新枚举**(S2-H2.2 §4 已固化)。

---

## 2. 与 S2-H1 OKR/KR 的映射

### 2.1 全局 KR 覆盖(每个 FM 都映射至少 1 个 KR)

| 全局 KR | 含义 | 覆盖该 KR 的 FM 类别 |
|---|---|---|
| **KR1.1** 最低交付线覆盖率 | 中阶可用档全过 | 各 skill major/minor FM(KR-X1~X5 未达) |
| **KR1.2** 一票否决项命中数=0 | 22 项一票否决全 0 | 各 skill 的 blocker FM(全部覆盖) |
| **KR3.1** 不可宣称项命中数=0 | 文档不超界 | 全局 F-OverClaim 类(prd2proto FM-004 / 各 skill not_allowed_claims) |
| **KR3.2** gap/assumption/confidence 标注覆盖率 | ≥ 90% | 各 skill 的 gap/inferred 类 FM(prd2proto FM-005/006 / ip-design FM-007 / ai-analytics FM-005 等) |
| **KR3.3** 关键决策可追溯率 | 100% | 各 skill 的 traceability 类 FM(prd2proto FM-002 / ip-design FM-006 等) |

### 2.2 Skill-specific KR 覆盖

| Skill | KR 编号 | 对应 FM 覆盖 |
|---|---|---|
| prd2proto | KR-P1 ~ KR-P5 | FM-001 ~ FM-008 全覆盖 5 个 KR |
| uxeval | KR-U1 ~ KR-U5 | FM-001 ~ FM-008 全覆盖 5 个 KR |
| ai-analytics | KR-A1 ~ KR-A5 | FM-001 ~ FM-008 全覆盖 5 个 KR |
| ip-design | KR-I1 ~ KR-I5 | FM-001 ~ FM-008 全覆盖 5 个 KR |
| brand-creative | KR-B1 ~ KR-B5 | FM-001 ~ FM-008 全覆盖 5 个 KR |

详见各 skill `eval/failure/failure-modes.md` 末尾的"KR 未达标覆盖"段。

---

## 3. 与 S2-H2 Golden Output Templates 的映射

每个 FM 通过 `related_golden_template_section` 字段链接到对应 golden template 章节。映射逻辑:

| FM 关注的失败 | 链接的 template 章节 |
|---|---|
| Schema/字段级失败 | §字段级要求 / §必填章节 |
| Traceability 失败 | §traceability 规范 / §gap / assumption / confidence / traceability 规范 |
| 一票否决类 | §一票否决检查 / §禁止声明 |
| 标注类(inferred/gap) | §gap / assumption / confidence 规范 |
| 流程顺序类(如视觉先行) | §禁止声明 / §一票否决检查 |

实际效果:**S2-H4 self review gate 跑 FM 检测时,可以一键跳到 template 对应章节看"应该长什么样"**,而不是只看到一条规则文字。

---

## 4. 与 S2-H2.2 放置规则的一致性

S2-H2.2 §4 定义了 failure modes 的放置规则,本批严格遵守:

| 规则(H2.2 §4.2) | 本批落实 |
|---|---|
| 通用真源不复制 | ✅ 各 skill failure-modes.md 通过 `source_reference` 字段引用通用真源,**未复制任何通用 FM 正文** |
| skill-specific 在 `skills/<skill>/eval/failure/failure-modes.md` | ✅ 5 个 skill 全部按此路径放置 |
| 总表映射放 docs/audits/ | ✅ 本报告就是总表(映射不复制) |
| 不新增共享 knowledge asset | ✅ 未碰 `knowledge/manifest.yaml` |
| `delivery_decision` 三态对齐 18-failure-modes | ✅ 仅用 block/degrade/warn/gap,无新枚举 |

---

## 5. 全局 Failure Mode 摘要(只引用,不复制)

下列通用 failure mode 真源已存在,本批不重写,各 skill failure-modes.md 通过 `source_reference` 引用:

### 5.1 输入/输出/追溯类(全 skill 适用)

| FM 主题 | 真源位置 | 谁引用 |
|---|---|---|
| 输入缺失 / 输入质量低 / 输入格式不支持 | `knowledge/design-work-paradigm/18-failure-modes.md` §FM-I001~I003 | 全 5 skill 的 input-diagnosis 类 FM |
| 输出 schema 不合规 / 必填字段缺失 | 同上 §FM-O00x | prd2proto FM-001 / ai-analytics FM-002 |
| 关键决策无追溯 | `knowledge/design-work-paradigm/19-traceability.md` | prd2proto FM-002 / ip-design FM-006 |
| 推断未标 [inferred] | 同上 + 各 skill constitution | 全 5 skill 的标注类 FM |

### 5.2 Honesty/OverClaim 类(全 skill 适用)

| FM 主题 | 真源位置 | 谁引用 |
|---|---|---|
| 编造数据 / 把推断当事实 | 各 skill constitution + `design.quality.common-failure-modes` | ai-analytics FM-001 / ip-design FM-007 |
| 把 mock 标"已跑通" / 把 prompt-grade 说成 runtime-grade | `PILOT-BOUNDARY.md` + S2-H1 §1.3 | prd2proto FM-004 |
| 跨 maturity 越界声明 | `docs/STATUS-DEFINITION.md` + S2-H1.1 §6.4 | 全 5 skill 的 not_allowed_claims 字段 |

### 5.3 Domain-specific 通用真源

| Domain | 真源 | 引用 skill |
|---|---|---|
| IP 设计 | `design.quality.common-failure-modes`(M01-M06 全阶段反模式) | ip-design FM-001~008 全部 |
| 品牌创意 | `design.quality.brand-creative-failure-modes`(F-BS/F-CA/F-LD 等) | brand-creative FM-001~008 全部 |
| UX 评估 | `ux.ux-failure-modes` | uxeval FM-005/008 |

**总计**:全局 FM 摘要 = 3 类底座(输入输出追溯 / Honesty / domain-specific),通过 `source_reference` 字段在各 skill 内被引用 **40 次**(5 skill × 8 FM 全部携带 source_reference)。

---

## 6. Skill-Specific Failure Mode 摘要

| Skill | 文件 | FM 总数 | blocker | major | minor | 一票否决覆盖 |
|---|---|---|---|---|---|---|
| prd2proto | `skills/prd2proto/eval/failure/failure-modes.md` | 8 | 4 | 3 | 1 | ✅ 4/4(Schema/Traceability/代码宪法/Honesty)|
| uxeval | `skills/uxeval/eval/failure/failure-modes.md` | 8 | 4 | 3 | 1 | ✅ 4/4(Evidence缺失/敏感信息/严重等级越界/建议不可执行)|
| ai-analytics | `skills/ai-analytics/eval/failure/failure-modes.md` | 8 | 4 | 3 | 1 | ✅ 4/4(编造数据/必填字段/Coverage虚高/越界)|
| ip-design | `skills/ip-design/eval/failure/failure-modes.md` | 8 | 4 | 3 | 1 | ✅ 4/4(D2差异化/D6法务/D8人格/视觉先行)|
| brand-creative | `skills/brand-creative/eval/failure/failure-modes.md` | 8 | 3 | 4 | 1 | ✅ 3/3(策略空心化/法务/跨子skill不一致)|
| **合计** | | **40** | **19** | **16** | **5** | **19/19**(全部 skill-specific 一票否决覆盖)|

加上 3 个全局底座一票否决(F-Honesty / F-Traceability / F-OverClaim),总覆盖面 = **22/22**(与 S2-H1.1 一致)。

---

## 7. 不新增第二套通用 Failure Library 的说明

本批严格遵守 inventory-before-build 纪律:

| 检查项 | 结论 |
|---|---|
| 是否新增了 `knowledge/` 下的 failure 类资产? | ❌ 否(`knowledge/manifest.yaml` 未改) |
| 是否复制了 `design-work-paradigm/18-failure-modes.md` 的正文? | ❌ 否(仅在 source_reference 字段引用) |
| 是否复制了 `design.quality.common-failure-modes` 的正文? | ❌ 否(仅引用) |
| 是否复制了 `design.quality.brand-creative-failure-modes` 的正文? | ❌ 否(仅引用) |
| 是否复制了 `ux.ux-failure-modes` 的正文? | ❌ 否(仅引用) |
| 是否新增 skill-specific failure 文件? | ✅ 是(5 个,各 skill 内聚,符合 H2.2 §4) |
| 是否产生了"哪个是真源"的歧义? | ❌ 否(skill-specific 引用通用真源,链路单向清晰) |

---

## 8. 与 maturity 状态的对账(防过度声明)

每个 FM 的 `not_allowed_claims` 字段已与 status.matrix maturity 对账:

| Skill | maturity | FM 强制不可宣称 |
|---|---|---|
| prd2proto | pilot, runtime-grade(唯一) | 不可宣称"已达资深水平 / 生产就绪 / 完全自动化" |
| uxeval | beta(S1-0B 实证偏乐观) | 不可宣称"已接 kernel quality_gates"(实为 `gate:` 暂停门 / 无 runtime) |
| ai-analytics | pilot, prompt-grade | 不可宣称"已接 runtime / 可替代真实研究 / 唯一决策依据" |
| ip-design | pilot, prompt-grade | 不可宣称"商用就绪 / 已通过商标审查 / 替代资深设计师" |
| brand-creative | alpha(6/13 sub-skill) | 不可宣称"全链路可用 / 13 sub-skill 全部 pipeline-ready" |

---

## 9. 下游对接(S2-H4 Self Review Gate 入口)

S2-H4 是**纯引用层**(H2.2 §5 已固化),不产生新标准。它的 gate 跑 FM 自检的具体路径:

```
1. 读取 skill 产出 + 对应 golden template
2. 按 KR 自评(引 H1.1 §6 KR 编号)
3. 按 FM 检测(引本报告 §6 + skill failure-modes.md 的 detection_signal)
4. 按一票否决项判定(引 H1 §2 一票否决 + 本报告 §6 的 19 项 blocker FM)
5. 输出 gate decision:
   - 任一 blocker 命中 → block(整体不放行)
   - 任一 major 命中 → degrade(降级声明 + 列入 gap)
   - 任一 minor 命中 → warn(可放行,但记录)
   - 全过 → pass
```

---

## 10. 本批文件清单

| 文件 | 类型 | 行数估计 |
|---|---|---|
| `docs/audits/S2-H3-FAILURE-MODE-LIBRARY.md` | 主报告(本文件) | ~240 |
| `skills/prd2proto/eval/failure/failure-modes.md` | skill FM | ~190 |
| `skills/uxeval/eval/failure/failure-modes.md` | skill FM | ~210 |
| `skills/ai-analytics/eval/failure/failure-modes.md` | skill FM | ~200 |
| `skills/ip-design/eval/failure/failure-modes.md` | skill FM | ~225 |
| `skills/brand-creative/eval/failure/failure-modes.md` | skill FM | ~200 |

**未碰**:runtime / pipeline / .factory/archetypes / release/npm/tag/workflow / `knowledge/manifest.yaml` / 各 skill `prompts/`。

---

## 11. 状态

本批完成后,DesignOS 已具备:
- ✅ 资深输出 rubric(S2-H1)
- ✅ 资深 OKR/KR 指标(S2-H1.1)
- ✅ Golden output templates(S2-H2)
- ✅ Knowledge architecture guardrails(S2-H2.2)
- ✅ Failure mode library(本批 S2-H3)
- ⏭ 下一步:Self review gate(S2-H4)— 把以上四件套串成自检闭环
