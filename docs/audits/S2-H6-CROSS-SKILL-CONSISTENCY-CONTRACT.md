# S2-H6 — Cross-Skill Consistency Contract

> **本报告性质**:跨 skill 一致性契约总控层。**引用层,非新标准层**——不新增 KR / failure mode / rubric / shared knowledge 真源;不改 runtime / pipeline / factory / release。
> **核心命题**:单个 skill 合格 ≠ 链路合格。H4~H5.1 保证单 skill 质量,H6 保证多 skill 串联时不矛盾、不丢失信息。
> **日期**:2026-06-12

---

## 1. 为什么需要跨 skill 一致性契约

**单 skill 合格不等于链路合格**。链路级风险:

| 风险类型 | 示例 | 对最终产物的影响 |
|---|---|---|
| **上游策略被下游改写** | prd2proto 把 ai-analytics 定的"专业稳重"改成"年轻科技" | 整条链路策略断裂 |
| **用户画像不一致** | ai-analytics 定"IT 管理员",prd2proto 按"运营人员"做页面 | 任务建模全部偏移 |
| **gap/assumption 丢失** | 上游标"业务目标推断",下游当 verified fact 使用 | 置信度虚高,H4 无法追溯 |
| **推断被当成事实** | ai-analytics 的 [inferred] 进入 prd2proto 被去掉标注 | violation of Honesty FM |
| **evidence/traceability 断裂** | 下游引用上游 artifact_id 但 id 不存在 | traceability_map 无效 |
| **子技能输出冲突** | brand-creative 里 logo 偏科技冷峻,voice 偏温暖亲切 | VI 系统自相矛盾 |
| **多 skill 最终产物口径不一致** | ai-analytics 报告说"无竞品优势",prd2proto 原型按高端品牌做 | 用户收到矛盾产物 |

---

## 2. H6 与 H4 / H5 / H5.1 的关系

| Gate | 检查对象 | 时机 |
|---|---|---|
| **H5** Input Quality Gate | 单个 skill 输入是否够 | 执行前 |
| **H5.1** Progressive Checkpoints | 单个 skill 执行中是否健康 | 执行中 |
| **H4** Self Review Gate | 单个 skill 输出是否可交付 | 交付前 |
| **H6 Cross-Skill(本批)** | **多个 skill 之间输入输出是否一致** | **串联执行前 / 中 / 后均可** |

```
单 skill 路径:  [H5 输入] → [H5.1 过程] → [H4 输出]
跨 skill 路径:  上游 H4 pass → [H6 一致性检查] → 下游 H5 input
```

**H6 的时机**:上游 H4 通过后、下游 H5 输入前,做字段映射 + 一致性审查。

---

## 3. consistency_decision 枚举

### 3.1 唯一枚举(只允许这 4 个)
```
consistent
consistent_with_carried_gaps
needs_reconciliation
blocked_inconsistent
```

### 3.2 判定逻辑

| 优先级 | 条件 | consistency_decision |
|---|---|---|
| 1(最高) | 上游核心字段被下游**无依据改写** | **blocked_inconsistent** |
| 2 | 上下游关键字段**冲突**,需人工裁定 | **needs_reconciliation** |
| 3 | 上游 gap/assumption **被完整携带**且下游显式标注 | **consistent_with_carried_gaps** |
| 4 | 字段映射完整、无冲突、traceability 保留 | **consistent** |

---

## 4. 九个跨 skill 一致性维度

| 维度 | 检查项 |
|---|---|
| **artifact identity** | artifact_id / source_skill / source_stage / run_id 是否可追溯 |
| **semantic continuity** | 业务目标、用户、场景、策略关键词是否一致 |
| **evidence continuity** | 证据引用是否延续,evidence_refs 是否仍指向真实来源 |
| **gap continuity** | 上游 gaps 是否被下游完整携带 |
| **assumption continuity** | 上游 [inferred] 推断在下游是否仍标注 |
| **confidence continuity** | 置信度是否被保留或合理降级(不可上升) |
| **traceability continuity** | 关键结论是否能回溯到上游 artifact |
| **contradiction detection** | 上下游或同层是否出现前后冲突字段 |
| **degradation propagation** | 上游降级(degrade_with_gaps)是否传递到下游声明 |

---

## 5. 关键跨 skill 链路(6 条)

### 5.1 ai-analytics → prd2proto
**关键字段**:`design_strategy.(target_audience / business_goal / design_principles / differentiation_statement)` + `user_persona[].{role / goals / pain_points}`
- prd2proto 必须从 `upstream_refs` 注入这些字段
- **不允许**:prd2proto 在 design-objectives stage 定义一套新的业务目标/用户角色

### 5.2 ai-analytics → brand-creative
**关键字段**:`competitor_matrix` → `competitive-analysis` sub-skill;`design_strategy.target_audience` → `brand-strategy`
- brand-creative 的差异化分析必须引用 ai-analytics 的竞品结论
- **不允许**:brand-creative 重新定义目标人群(除非上游 confidence 过低,需显式说明)

### 5.3 brand-creative internal
**关键链路**:
- `competitive-analysis` → `brand-strategy`:差异化依据来源
- `brand-strategy` → `{logo-design, color-system, typography-system}`:关键词传导
- `{logo, color, typography}` → `visual-identity`:三件套 → VI 整合

### 5.4 ip-design internal
**关键链路**:
- `brand_brief / persona_profile / worldview` → `visual_spec / image_prompt_pack`:策略先于视觉
- **不允许**:visual_spec 中出现与 brand_brief 北极星矛盾的视觉调性

### 5.5 prd2proto internal
**关键链路**:
- `requirement_inventory` → `design_objectives` → `user_task_map` → `business_flow` → `information_architecture` → `page_flow` → `state_matrix` → `traceability_map` → `prototype_code`
- **核心不变量**:business_goal + target_audience 全链路不变

### 5.6 uxeval → ai-analytics / prd2proto(可选上游)
**关键字段**:evaluation report 的 issue 发现可作为 ai-analytics 的 user_research 来源
- 若 uxeval 跑在 ai-analytics 之后,评估问题可作为 pain_points 证据输入

---

## 6. 字段级映射原则

每条 mapping 含 7 个字段:

```yaml
mapping_id: MAP-XXX
upstream_artifact: <artifact 名>
upstream_field: <字段 JSON Path>
downstream_artifact: <artifact 名>
downstream_field: <字段 JSON Path>
mapping_type: exact | derived | optional | carry_forward
conflict_rule: <冲突时如何处理>
gap_rule: <上游字段缺失时下游如何处理>
confidence_rule: <置信度如何传递>
```

**mapping_type 语义**:
- `exact`:下游必须原样使用,不允许修改
- `derived`:下游基于上游派生,需显式说明派生逻辑
- `optional`:上游无此字段时下游可自行推断(须标 [inferred])
- `carry_forward`:gap/assumption 类,下游必须携带而非丢弃

---

## 7. 用户体验原则

跨 skill 不一致时,**禁止静默修正**,必须:

| 步骤 | 要求 |
|---|---|
| 1. 告知冲突位置 | 明确说明上游哪个字段 vs 下游哪个字段冲突 |
| 2. 给出建议裁定方案 | "建议以上游为准" / "建议追问用户" / "建议降级" |
| 3. 标注影响范围 | 冲突会影响哪些下游产物 |
| 4. 允许用户确认 | 用户确认继续 / 修正 / 降级(3 选 1) |
| 5. 记录决策 | 裁定结果记入 consistency review log,可被 H4 追溯 |

> ❌ 不允许:下游偷偷覆盖上游、把冲突埋进日志不告知。

---

## 8. 明确不可做

- ❌ 不把上游 assumption 当 verified fact(进入下游时必须保留 [inferred] 标注)
- ❌ 不静默丢弃上游 gap(下游 carry_forward_items 必须包含上游 gaps)
- ❌ 不下游重写上游策略后仍称"一致"
- ❌ 不跨 skill 编造 traceability(artifact_id 引用必须真实存在于上游 run 输出)
- ❌ 不把多 skill 拼接包装成已验证闭环
- ❌ 不用真实业务数据做示例(synthetic / sanitized only)

---

## 9. 本批文件清单

| 文件 | 类型 |
|---|---|
| `docs/audits/S2-H6-CROSS-SKILL-CONSISTENCY-CONTRACT.md` | 总控报告(本文件) |
| `templates/cross-skill-consistency-review.md` | 全局一致性评审模板 |
| `docs/contracts/cross-skill/ai-analytics-to-prd2proto.md` | 链路契约 |
| `docs/contracts/cross-skill/ai-analytics-to-brand-creative.md` | 链路契约 |
| `docs/contracts/cross-skill/brand-creative-internal.md` | 链路契约 |
| `docs/contracts/cross-skill/ip-design-internal.md` | 链路契约 |
| `docs/contracts/cross-skill/prd2proto-internal.md` | 链路契约 |
| `scripts/validate_cross_skill_consistency_contracts.py` | 只读校验脚本 |

**未碰**:runtime / pipeline / .factory/archetypes / release/npm/tag/workflow / version / install / `knowledge/manifest.yaml` / 禁止文件。

---

## 10. 与上游 gate 的衔接

```
H5 input gate          H5.1 checkpoints      H4 self review
─────────────         ────────────────       ──────────────
ready / ...      →    CP1~CP5           →    pass / block
gaps/assumptions ──────────────────────────► H4 §7 检查

                   H6 cross-skill contract
                   ─────────────────────
上游 H4 pass     →  field mapping audit  →  下游 H5 input
                    consistency_decision
                   ─────────────────────
                   consistent → 下游 H5 ready
                   needs_reconciliation → 追问
                   blocked_inconsistent → 不允许下游启动
```

---

## 11. 状态

本批完成后,DesignOS 质量保障体系八件套完整:
- ✅ rubric(H1)→ OKR/KR(H1.1)→ golden template(H2)→ knowledge guardrails(H2.2)→ failure modes(H3/H3.1)→ self review gate(H4)→ input quality gate(H5)→ progressive checkpoints(H5.1)→ **cross-skill consistency contract(本批 H6)**
- ⏭ 候选下一步:S2-H7 Offline Dry-Run Pack
