# S2-H4 — Self Review Gate

> **本报告性质**:总控审查层,把 S2-H1 rubric / S2-H1.1 OKR-KR / S2-H2 golden template / S2-H3 failure modes 串成**交付前自检闭环**。
> **关键边界**:S2-H4 是**引用层 / 审查层,不是新标准层**。不新增任何质量标准、KR、failure mode、通用 rubric。所有阈值/结构/失败模式均引用 H1~H3.1。
> **日期**:2026-06-12

---

## 1. 目标与边界

### 1.1 目标
让每个 skill 在交付前按统一结构完成 8 步自检,产出明确的 `delivery_decision`,杜绝"看起来完成但经不起资深评审"的产出流入交付。

### 1.2 边界(硬约束)
| 允许 | 禁止 |
|---|---|
| 引用 H1 rubric 阈值 | ❌ 新增质量标准 |
| 引用 H1.1 KR 编号 | ❌ 新增 KR |
| 引用 H2 golden template 结构 | ❌ 新增 golden 结构 |
| 引用 H3/H3.1 failure mode 的 id/severity/self_review_question | ❌ 新增 failure mode / 复制 FM 正文 |
| 引用各 skill constitution / PILOT-BOUNDARY / knowledge-manifest | ❌ 改 runtime/pipeline/factory/release |

---

## 2. 引用源清单

| 类别 | 文件 | 引用内容 |
|---|---|---|
| 资深 rubric | `docs/audits/S2-H1-SENIOR-OUTPUT-RUBRIC.md` | 最低交付线 / 目标线 / 一票否决项 |
| OKR/KR | `docs/audits/S2-H1-SENIOR-OUTPUT-RUBRIC.md` §6(OKR/KR) | 全局 KR1.1/1.2/3.1/3.2/3.3 + skill KR-P/U/A/I/B 1~5 |
| Golden template | `docs/audits/S2-H2-GOLDEN-OUTPUT-TEMPLATES.md` | golden 必填结构 |
| Failure mode 总表 | `docs/audits/S2-H3-FAILURE-MODE-LIBRARY.md` | 40 FM 映射 + delivery_decision 三态对齐 |
| skill failure modes | `skills/{prd2proto,uxeval,ai-analytics,ip-design,brand-creative}/eval/failure/failure-modes.md` | 8 FM × 5 的 id/severity/self_review_question |
| skill golden template | `skills/{...}/templates/golden-*.md` | 必填章节 |
| skill 约束 | `skills/{...}/constitution.md`、`skills/prd2proto/PILOT-BOUNDARY.md`、`skills/{...}/knowledge-manifest.yaml` | 硬约束 / 边界 / shared knowledge 锚定 |

---

## 3. Self Review Gate 统一执行顺序(8 步)

| Step | 名称 | 引用源 | 输出 |
|---|---|---|---|
| **1** | 确认适用 skill 与交付类型 | skill SKILL.md | skill id + output 类型 |
| **2** | 检查最低交付线 KR(全局) | H1.1 全局 KR1.1/1.2/3.x | 每条 KR status |
| **3** | 检查 skill-specific KR | H1.1 KR-{P/U/A/I/B}1~5 | 每条 KR status |
| **4** | 检查一票否决项 | H1 §2 各 skill 一票否决 | triggered? 任一 yes → block |
| **5** | 逐条跑 failure mode self_review_question | skill failure-modes.md(8 FM) | 每条 answer |
| **6** | 对照 golden template 必填结构 | skill golden-*.md | present? + gap |
| **7** | 检查 gap/assumption/confidence/traceability | artifact-base 字段 + H1.1 KR3.2/3.3 | 标注覆盖率 |
| **8** | 输出 delivery_decision | §4 规则 | 4 枚举之一 + 理由 + next_actions |

---

## 4. delivery_decision 规则

### 4.1 唯一枚举(只允许这 4 个)
```
pass
pass_with_minor_warnings
degrade_with_gaps
block
```

### 4.2 判定逻辑(优先级从高到低)

| 优先级 | 条件 | delivery_decision |
|---|---|---|
| 1(最高) | 命中任一 **blocker FM** 或任一**一票否决项 triggered=yes** | **block** |
| 2 | 未命中 blocker,但存在 **major FM** 命中 | **degrade_with_gaps** |
| 3 | 仅命中 **minor FM** | **pass_with_minor_warnings** |
| 4 | 未命中任何 FM,且 KR 最低线满足,golden 必填结构完整 | **pass** |

> 注:任何不确定(unknown)按"未排除风险"处理——blocker 类 unknown 视同需进一步核验,不得直接 pass。

---

## 5. 5 个 Skill 审查入口表

| skill | golden template path | failure mode path | key KR ids | constitution / boundary path | delivery_decision 字段位置 |
|---|---|---|---|---|---|
| prd2proto | `skills/prd2proto/templates/golden-prd2proto-output.md` | `skills/prd2proto/eval/failure/failure-modes.md` | KR-P1~P5 + KR1.1/1.2/3.1/3.3 | `skills/prd2proto/constitution.md` + `skills/prd2proto/PILOT-BOUNDARY.md` | self-review-gate.md §9 |
| uxeval | `skills/uxeval/templates/golden-evaluation-report.md` | `skills/uxeval/eval/failure/failure-modes.md` | KR-U1~U5 + KR1.1/1.2/3.1 | `skills/uxeval/constitution.md` | self-review-gate.md §9 |
| ai-analytics | `skills/ai-analytics/templates/golden-analysis-output.md` | `skills/ai-analytics/eval/failure/failure-modes.md` | KR-A1~A5 + KR1.1/1.2/3.2 | `skills/ai-analytics/constitution.md` | self-review-gate.md §9 |
| ip-design | `skills/ip-design/templates/golden-ip-design-output.md` | `skills/ip-design/eval/failure/failure-modes.md` | KR-I1~I5 + KR1.1/1.2/3.2 | `skills/ip-design/constitution.md` | self-review-gate.md §9 |
| brand-creative | `skills/brand-creative/templates/golden-brand-creative-output.md` | `skills/brand-creative/eval/failure/failure-modes.md` | KR-B1~B5 + KR1.1/1.2/3.2 | `knowledge/design/quality/brand-creative-failure-modes.md`(group skill 无 root constitution) | self-review-gate.md §9 |

---

## 6. 不可宣称(防过度声明)

Self review gate 的产出与文档**禁止**出现:
- ❌ "已达到资深设计师水平"
- ❌ "已通过真实业务验证" / "validated in production"
- ❌ "自动化全覆盖" / "fully automated" / "完全自动化" / "无人值守自动化"
- ❌ "可直接公网生产发布" / "生产就绪" / "production ready"

Self review gate 通过(`pass`)只意味着:**该产出满足本批定义的最低交付线 + 未命中 failure mode**,**不等于**达到资深水平或可生产。

---

## 7. 与 S2-H5 Input Quality Gate 的前置关系

| 维度 | S2-H4 Self Review Gate | S2-H5 Input Quality Gate |
|---|---|---|
| 检查对象 | **输出**是否合格 | **输入**是否足够支撑输出 |
| 时机 | 交付前(产出已生成) | 执行前(产出未生成) |
| 失败处置 | block/degrade/warn 输出 | 拒绝启动 / 要求补充输入 / fallback_safe |
| 引用 | H1~H3.1 | (H5 待建,预计引用 input-diagnosis + evidence-quality + data-completeness-rubric) |

**不可混淆**:H4 回答"产出对不对",H5 回答"输入够不够"。一个产出可以"输入足够(H5 pass)但输出不合格(H4 block)",反之亦然。两个 gate 独立判定。

---

## 8. 本批文件清单

| 文件 | 类型 |
|---|---|
| `docs/audits/S2-H4-SELF-REVIEW-GATE.md` | 总控报告(本文件) |
| `skills/prd2proto/templates/self-review-gate.md` | skill 自检模板 |
| `skills/uxeval/templates/self-review-gate.md` | skill 自检模板 |
| `skills/ai-analytics/templates/self-review-gate.md` | skill 自检模板 |
| `skills/ip-design/templates/self-review-gate.md` | skill 自检模板 |
| `skills/brand-creative/templates/self-review-gate.md` | skill 自检模板 |
| `scripts/validate_self_review_templates.py` | 只读校验脚本 |

**未碰**:runtime / pipeline / .factory/archetypes / release/npm/tag/workflow/version/install / `knowledge/manifest.yaml`。

---

## 9. 状态

本批完成后,DesignOS senior-output 体系五件套齐全:
- ✅ rubric(H1)→ ✅ OKR/KR(H1.1)→ ✅ golden template(H2)→ ✅ knowledge guardrails(H2.2)→ ✅ failure modes(H3/H3.1)→ ✅ **self review gate(本批 H4)**
- ⏭ 下一步:S2-H5 Input Quality Gate(检查输入是否足够支撑输出)
