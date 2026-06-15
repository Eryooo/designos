# S2-H2 — Golden Output Templates(中阶可用 + 资深目标)

> **本报告性质**:基于 S2-H1 资深 rubric 与 S2-H1.1 OKR/KR,为 5 个核心 skill 建立 golden output 模板。**不跑真实验证、不引入真实业务数据、不引入真实截图/客户/项目名**——所有示例片段均为 synthetic / sanitized。
> **golden template 的角色**:输出规范的"中阶可用 + 资深目标"双层基准;后续 S2-H3 failure modes 与 S2-H4 self review gate 都基于这些 template 跑自检。
> **依据**:S2-H1 §2(per-skill rubric)+ S2-H1.1 §6(OKR/KR)+ 各 skill constitution + 现有 quality 资产(`knowledge/design/quality/`)。
> **日期**:2026-06-12

---

## 1. Golden Template 的定义

| 概念 | 含义 |
|---|---|
| **Golden output template** | 描述「资深设计师水准的输出长什么样」的可对账规范——含必填章节、字段级要求、最低线/目标线、一票否决项、自评表(引 KR 编号)、不可宣称边界 |
| **不是什么** | 不是真实业务案例(那是 `eval/golden/` 的职责),不是 prompt(那是 `prompts/` 的职责),不是 schema(那是 `schemas/` 的职责) |
| **使用纪律** | 模板里所有示例片段必须标 `synthetic / sanitized`;严禁出现真实客户、真实账号、真实截图 URL、真实内部链接 |

**与既有目录的边界**:
- `templates/`(本批新建文件位置):**输出规范模板**,本批产物
- `eval/golden/<case-name>/`:具体 golden case(数据级,本批不动)
- `eval/failure/<case-name>/`:failure case(本批不动,留 S2-H3)
- `schemas/`:JSON Schema(本批不动)
- `prompts/`:LLM prompt(本批不动)

---

## 2. 与 S2-H1 OKR/KR 的映射(交叉表)

每个 skill 的 golden template 至少引用 **3 个 KR 编号**(spec 要求),实际本批所有 5 个 template 各引用 **5 个 skill-specific KR + 关联全局 KR**。

| Skill | template 文件 | 引用的 KR 编号 | 一票否决项 |
|---|---|---|---|
| prd2proto | `skills/prd2proto/templates/golden-prd2proto-output.md` | KR-P1 ~ KR-P5 + 全局 KR1.1/1.2/1.4/3.1/3.3 | 4 项(Schema/Traceability/代码宪法/Honesty) |
| uxeval | `skills/uxeval/templates/golden-evaluation-report.md` | KR-U1 ~ KR-U5 + 全局 KR1.1/1.2/3.1 | 4 项(Evidence/敏感泄露/严重等级越界/建议不可执行) |
| ai-analytics | `skills/ai-analytics/templates/golden-analysis-output.md` | KR-A1 ~ KR-A5 + 全局 KR1.1/1.2/3.2 | 4 项(编造/必填字段/Coverage 虚高/越界) |
| ip-design | `skills/ip-design/templates/golden-ip-design-output.md` | KR-I1 ~ KR-I5 + 全局 KR1.1/1.2/3.2 | 4 项(D2 差异化/D6 法务/D8 人格/视觉先行) |
| brand-creative | `skills/brand-creative/templates/golden-brand-creative-output.md` | KR-B1 ~ KR-B5 + 全局 KR1.1/1.2/3.2 | 3 项(策略空心/法务/跨子 skill 不一致) |

---

## 3. 通用 Template 骨架(全 5 skill 共用结构)

每个 skill 的 golden template 都按下面 12 节组织,确保格式一致、可被 H3/H4 自检脚本统一扫描:

```
1. Synthetic Sanitized Notice           # 顶部硬声明:本模板不含真实业务
2. 输入前提                             # 跑这个 skill 需要什么输入
3. 输出目录结构 / artifact 列表         # 产物清单(对应 schema)
4. 必填章节                             # 每节是什么、最低字数/字段
5. 字段级要求                          # 每个关键字段的合法值/枚举/约束
6. 最低线标准(中阶可用)               # 引用 S2-H1 §2.X 的最低线
7. 目标线标准(资深可评审)             # 引用 S2-H1 §2.X 的目标线
8. 一票否决项检查表                    # 引用 S2-H1 §2.X 的 V1-Vn
9. Gap / Assumption / Confidence / Traceability 规范  # 必填字段细则
10. 自评表(引 KR 编号)                # 跑完用本表对账
11. 禁止声明清单                       # 引 S2-H1 §2.X 的"不可宣称"
12. Synthetic 示例片段                 # 中阶可用档的 sanitized 例子
```

**为什么用这个统一骨架**:S2-H3 failure mode library 和 S2-H4 self review gate 可以用同一个解析器跑这 12 节,不需要为每个 skill 写 5 套自检脚本。

---

## 4. 每 Skill 的 Golden Output 设计要点

### 4.1 prd2proto

**核心**:18-stage 推理资产链,每 stage 产出 1 个 artifact,最终 traceability_map + professional_gap_report 闭环。
**最低线焦点**:18 artifact 全产 + 每 artifact schema 校验 + traceability 关键决策 + 代码宪法不违反。
**目标线焦点**:9 维 rubric 自评全到中阶以上 + 关键 stage 的 [inferred] 标注 + traceability evidence 链路完整。
**一票否决**:Schema 违约 / Traceability 断裂 / 代码宪法违反 / Honesty 违反(V1-V4)。
**特殊性(全 5 skill 中唯一)**:runtime-grade,真接 kernel/quality-gates(blocking),示例需含 `quality_gates:` 字段(不是 `gate:` 暂停门)。

### 4.2 uxeval

**核心**:证据 → 问题 → 根因 → 影响 → 优先级 → 建议 闭环。
**最低线焦点**:每 issue 必有 evidence_refs(constitution #1)+ severity 用 4 档枚举 + 不输出敏感信息。
**目标线焦点**:根因深度(不停留表象)+ 建议三要素齐全 + 旅程阶段 × 角色 × 任务 coverage 矩阵全。
**一票否决**:Evidence 缺失 / 敏感泄露 / 严重等级越界 / 建议不可执行(V1-V4)。
**特殊性**:prompt-grade(无 runtime),示例不能宣称已接 kernel quality_gates;pipeline 用的是 `gate:`(checkpoint 暂停门)。

### 4.3 ai-analytics

**核心**:可被 prd2proto 消费的 design_strategy + user_persona,每条结论可追溯到 collected_data。
**最低线焦点**:不编造(constitution #1)+ schema 必填字段非空 + coverage ≥ 0.70 + 不越界产代码。
**目标线焦点**:findings.evidence_refs 100% 反向校验通过 + [inferred] 90%+ 标注 + competitive matrix 无大量 TBD。
**一票否决**:编造 / 必填字段缺失 / Coverage 虚高 / 越界产出。
**特殊性**:prompt-grade(无 runtime),pilot 阶段只稳产 design_strategy + user_persona 两个产物。

### 4.4 ip-design

**核心**:6 阶段闭环——brand_brief → worldview → persona_profile → visual_spec → content_plan → brand_material_spec(+ image_prompt_pack)。
**最低线焦点**:6 阶段产物齐全 + 9 维 rubric 全到中阶 + 一票否决项(D2/D6/D8 + 视觉先行)无触发 + image_prompt_pack 含负向提示词。
**目标线焦点**:9 维到高阶可评审 + 关键决策依据链显式 + 跨阶段关键词链路无漂移。
**一票否决**:D2 差异化 / D6 法务 / D8 人格立体度 / 视觉先行(V1-V4)。
**特殊性**:有最完整的 quality 四件套(rubric+fm+checklists+gap report),其他 skill 应对标。

### 4.5 brand-creative

**核心**:Skill Group + 13 sub-skill,主线建成是当前 P0(13 中仅 6 有 pipeline)。
**最低线焦点**:策略基线齐全 + ≥ 1 sub-skill 跑通 + brand-identity rubric 自评中阶以上 + failure-modes 自检无严重级。
**目标线焦点**:6 sub-skill 实装 → ≥ 7 + 跨 sub-skill 关键词链路一致性 ≥ 85% + 跨子 skill 无矛盾。
**一票否决**:策略空心化 / 法务/商标风险 / 跨子 skill 不一致(V1-V3)。
**特殊性**:alpha 阶段,group skill 框架,golden template 反映"半成品骨架"现状,不能假装完整。

---

## 5. 不可宣称边界(全 5 skill 共用底座)

任何 golden template 自带或被引用时,**禁止**出现以下声明:

| 不可宣称类别 | 禁用关键词举例 |
|---|---|
| **资深水准达成** | "已达资深设计师水平" / "AI 已替代设计师" / "无需复核" |
| **生产可用** | "production ready" / "可直接用于生产" / "可直接发布" / "fully automated" / "完全自动化" / "无人值守自动化" |
| **runtime grade 假冒** | "uxeval/ai-analytics/ip-design 已接入 kernel quality_gates"(实际是 `gate:` 暂停门,无 runtime) |
| **真实数据假冒** | 真实客户名 / 真实截图 URL / 真实账号 / token / password / 内部域名 / 公网发布相关 |
| **覆盖率虚高** | "已达 X%" 类陈述,除非有 S2-H1.1 §6.4 列出的实证 |

---

## 6. 与 maturity 的对账

每个 skill 的 golden template 自带"当前状态"段,反映 status.matrix 实际:

| Skill | maturity | template 中"当前状态"如何写 |
|---|---|---|
| prd2proto | pilot | "本模板按资深要求定义判断标准;runtime 已通跑前 5+ stage,18 stage 全链路 validated 待 trial" |
| uxeval | beta | "本模板按资深要求定义判断标准;无 runtime/ 目录,maturity beta 偏乐观,详见 S1-0B-DECLARED §2.2" |
| ai-analytics | pilot | "本模板按资深要求定义判断标准;无 runtime,pilot 阶段仅稳产 design_strategy + user_persona 两个产物" |
| ip-design | pilot | "本模板按资深要求定义判断标准;无 runtime,prompt-grade,9 维 rubric 自评待真实 LLM 链路实测" |
| brand-creative | alpha | "本模板按资深要求定义判断标准;13 sub-skill 中仅 6 有 pipeline(46%, 未达 KR-B1 最低线 50%),主线建设中" |

---

## 7. 后续(留给 S2-H3 / S2-H4)

- **S2-H3 Failure Mode Library**:基于本批 golden template 的"低阶失败信号"+ 一票否决项 + 各 skill 现有 `failure-modes` 资产,建立 failure detection 库
- **S2-H4 Self Review Gate**:基于本批 golden template 的「自评表 + 一票否决检查表」,建立 self review skill / governance step

本批不进入 H3/H4。

---

*报告结束。配套 5 个 golden template 见 `skills/{prd2proto,uxeval,ai-analytics,ip-design,brand-creative}/templates/golden-*.md`。*
