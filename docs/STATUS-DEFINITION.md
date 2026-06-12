# DesignOS Status Definition（状态定义口径）

> 本文件是 DesignOS 所有报告、README、status.matrix.yaml 的**状态口径 source of truth**。
> 任何关于"完成度"的表述，必须引用本文件定义的层级，禁止跨层级推导。

---

## 为什么需要本文件

历史报告曾出现"完成度口径混乱"问题：

- "方法论 100% 完成" 被误推导为 "终极目标达成"
- "prompt 已写" 被误推导为 "skill 可用"
- "runtime 有代码" 被误推导为 "真实验证通过"

**核心原则**：方法论完成 ≠ prompt 完成 ≠ runtime 完成 ≠ 真实验证完成 ≠ 企业可用。
每一层都是独立的、不可跨层推导的状态。

---

## 五层 Readiness 定义

### 1. methodology_ready（方法论就绪）

**定义**：该 skill 的设计方法论知识资产已完成（rubric / failure modes / senior checklist / 决策框架）。

**意味着**：知识底座更完整。

**不意味着**：
- ❌ prompt 已写
- ❌ LLM 能按此方法论工作
- ❌ 产物接近资深设计师
- ❌ 可以合并 main

**判定标准**：`knowledge/` 下有对应方法论文档，含决策框架而非仅流程清单。

---

### 2. prompt_ready（Prompt 就绪）

**定义**：该 skill 的 prompt 已完成，包含资深设计师推理模型（12 项必备内容），可以进入 LLM 测试。

**意味着**：可以进入 LLM 测试阶段。

**不意味着**：
- ❌ 真实效果已验证
- ❌ LLM 输出稳定
- ❌ schema 一定能通过

**判定标准**：prompt 文件标注 COMPLETE，含 Stage role / Senior reasoning model / Output schema / Decision rules / Junior mistakes / Quality self-check 等。

**子状态**：
- `prompt_ready: partial` — 部分 prompt 完成（如 17 个中完成 10 个）
- `prompt_ready: true` — 全部核心 prompt 完成

---

### 3. runtime_ready（运行时就绪）

**定义**：runtime 能真实执行该 skill 的完整链路，不静默 mock，每个 stage 输出可被 schema gate 校验。

**意味着**：能真实跑、不假装。

**不意味着**：
- ❌ 输出质量达到资深级
- ❌ 已通过真实 case 验证

**判定标准**：
- 默认走真实 LLM（mock 必须显式启用）
- 全 stage 自动加载 prompt + 调用 LLM + schema validate + 写入 reasoning_assets
- 失败显式报错，不静默兜底

**子状态**：
- `runtime_partial` — 部分 stage 可真实执行（如只验证过前 N 个）
- `runtime_ready: true` — 完整链路可真实执行

---

### 4. validated（已验证）

**定义**：至少通过一个真实 golden case（真实 PRD/输入），并有评测结果（run-report + rubric 评分）。

**意味着**：有真实证据证明 prompt/runtime 有效。

**不意味着**：
- ❌ 多场景稳定
- ❌ 企业可托付

**判定标准**：
- 至少 1 个真实输入端到端跑通
- 有 run-report 记录成功/失败
- 有 senior-review-rubric 评分
- 资深设计师可基于输出评审（而非重做）

---

### 5. enterprise_ready（企业就绪）

**定义**：通过多 case 验证，有质量门、追溯、人工复核边界、失败回归测试。

**意味着**：可托付中低阶设计师稳定使用。

**判定标准**：
- 多个 golden case 验证通过
- quality gates 能真实拦截错误
- traceability 真实连接上游
- 有 failure regression test
- 明确人工复核边界

---

## 状态推进顺序

```
methodology_ready
  ↓（写 prompt）
prompt_ready (partial → true)
  ↓（接 runtime）
runtime_ready (partial → true)
  ↓（跑真实 case）
validated
  ↓（多 case + 质量门 + 回归）
enterprise_ready
```

**禁止跳级推导**：不能因为 methodology_ready 就声称 validated。

---

## 当前各 skill 状态（2026-06-10）

| skill | methodology | prompt | runtime | validated | enterprise |
|-------|------------|--------|---------|-----------|-----------|
| prd2proto | ✅ | partial→true | partial | 🔄 验证中 | ❌ |
| uxeval | ✅ | partial | partial | ❌ | ❌ |
| ai-analytics | ✅ | partial | ❌ | ❌ | ❌ |
| ip-design | ✅ | partial | ❌ | ❌ | ❌ |
| brand-creative | ✅ | ❌ | ❌ | ❌ | ❌ |

详见 `skills/status.matrix.yaml`。

---

## 禁止的表述（not_allowed_claims）

任何文档**禁止**出现以下表述，除非有对应层级的真实证据：

- ❌ "终极目标达成"
- ❌ "所有 skills 已达到资深设计师级别"
- ❌ "100% 完成"（除非明确限定在 methodology 层）
- ❌ "production-ready" / "可用于生产" / "完整可用"
- ❌ 用"方法论 X/X 完成"推导"skill 可用"

**正确表述示例**：
- ✅ "DesignOS 已建立跨 skills 的资深设计师方法论底座"（methodology_ready）
- ✅ "prd2proto 已完成 prompts-v2 主要专业化升级"（prompt_ready）
- ✅ "runtime 已引入真实 LLM 执行能力，但尚未形成完整 17-stage 真实链路"（runtime_partial）
- ✅ "真实验证进行中"（validated 之前）

---

**版本**: v1.0（2026-06-10 Batch 0 事实收口）
**维护**: 所有状态变更必须同步更新本文件的"当前各 skill 状态"表 + status.matrix.yaml
