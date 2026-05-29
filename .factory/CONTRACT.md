# DesignOS Skills Factory — Contract

> **这是工厂自身的合同，也是所有开发 Agent 的验收标准。**
> 所有指标必须达成，所有反模式必须避免，否则不算工厂搭好。

---

## 1. 工厂的存在意义

工厂的目标**不是**"再多一套抽象"，而是：

把 skill 开发从"读文档理解 → 手写所有契约 → 反复试错"
变成"按 archetype 装配 → 工厂保证骨架合规 → 只补业务逻辑"。

**衡量工厂是否成功的唯一标准**：从下一支 skill 开始，开发周期必须明显变短，且不能牺牲 uxeval 已建立的质量基线。

---

## 2. 北极星指标（Final Outcome）

### 2.1 Time-to-Skeleton（装配速度）

**定义**：从"决定做新 skill"到"装配出能过 validate + 能被 kernel 加载"的目录骨架的耗时（不含业务 prompt 编写）。

| 阶段 | 基线（uxeval） | 目标 |
|---|---|---|
| 工厂搭好后第 1 次 | — | ≤ 30 分钟 |
| 第 2 次（不同 archetype） | — | ≤ 10 分钟 |
| 终态 | — | ≤ 5 分钟 |

### 2.2 Time-to-First-Run（端到端业务实装）

**定义**：从骨架到"能跑通端到端、产出第一个 artifact"的时间。

| 顺位 | 目标 |
|---|---|
| 第 2 个 skill（ai-analytics） | ≤ 1 周 |
| 第 3 个 skill（prd2proto） | ≤ 3 天 |
| 第 4 个开始 | ≤ 1 天 |

### 2.3 Reuse Rate（复用率）

**定义**：新 skill 中**不需要新写**的部分占比（schema / 加载逻辑 / preflight / audit gate / output / pipeline 引擎 / 三级记忆 等）。

**目标**：≥ 80%。skill-specific 只能是：业务 prompt、reference 知识库、constitution 业务规则、benchmark 黄金样本。

### 2.4 Zero Regression（零回归）

**硬约束**：工厂迭代不能破坏 uxeval 基线。

- `pytest tests/` 必须全过（当前 249 个）
- `pytest mcp-servers/image-analyzer/tests/` 必须全过（当前 40 个）
- `ruff check .` 必须通过
- `pyright` 必须 0 错

---

## 3. 驱动指标（Process Metrics）

### A. 装配成功率层

- `scaffold_success_rate`：scaffold 产出的骨架直接过 validate 的比例 → **100%**
- `scaffold_kernel_load_rate`：scaffold 产出的骨架直接能被 `load_pipeline_skill` 加载的比例 → **100%**
- `scaffold_preflight_pass_rate`：scaffold 产出的骨架直接能过 `PreflightChecker.check` 的比例 → **100%**

### B. 抽象化层

- `archetype_coverage`：archetype 定义覆盖了 uxeval 的 stage 共性、checkpoint 共性、gate 共性 → **≥ 90%**
- `schema_import_count`：工厂直接 import 的 kernel schema 数量 → **≥ 8**（不重复定义 SkillConfig / StageConfig / CheckpointConfig / StageGateConfig / RetryConfig / MCPServerConfig / OutputType / SkillType）
- `manual_step_count`：装配新 skill 需要手工干预的次数 → **≤ 3**（仅：填 name、填 description、填业务 prompt 内容）

### C. 验证闭环层

- `extract_roundtrip`：`extract(uxeval) → archetype 定义 → validate(uxeval)` 必须通过 → **必过**
- `validate_uxeval_pass`：validate.py 跑现有 uxeval 必须通过 → **必过**
- `validate_catches_known_violations`：故意制造的违规骨架必须被拦截 → **≥ 6 种违规场景**
  - 缺 SKILL.md
  - 缺 pipeline.yaml
  - 缺 constitution.md
  - 缺 prompts/ 目录或文件不全
  - 缺 evidence-related stage（evaluation archetype）
  - 缺 audit gate（evaluation archetype）

### D. 工厂自身质量层

- `factory_test_count`：工厂自身 pytest 数量 → **≥ 30**
- `factory_test_pass_rate`：→ **100%**
- `factory_lint_pass`：→ ruff + pyright 必过
- `factory_independent_of_uxeval`：删除 skills/uxeval/ 后工厂代码本身仍能 import → **必过**

### E. 开发体验层

- `cli_command_count`：可执行命令数 → **≥ 4**（extract / validate / scaffold / benchmark）
- `error_message_actionable_rate`：错误消息带修复建议的比例 → **≥ 90%**
- `dry_run_supported`：scaffold 支持 --dry-run → **必有**
- `archetype_extensibility`：增加新 archetype 不需要改工厂核心代码 → **必有**

---

## 4. 验收门（Definition of Done）

工厂**同时满足**以下 5 道门才算搭好。任一门失败，整厂不算完成。

### Gate 1 — 萃取闭环

- ✅ `extract.py skills/uxeval` 产出 `evaluation.extracted.yaml`
- ✅ `validate.py skills/uxeval --archetype evaluation` 通过
- ✅ 故意删除 uxeval 关键文件（如 prompts/06-issue-attribution.md）后 validate 必须拦截，且报错带修复建议

### Gate 2 — 装配闭环

- ✅ `scaffold.py --archetype evaluation --name foo` 产出完整骨架
- ✅ 产出的骨架立即能被 `load_pipeline_skill(skill_dir)` 加载且不报错
- ✅ 产出的骨架立即能被 `PreflightChecker.check` 检查且不报错（在依赖齐全的环境）
- ✅ 产出的骨架立即能过 `validate.py`
- ✅ 支持 `--dry-run` 预览将创建的文件
- ✅ 支持 `--force` 覆盖已存在目录（默认拒绝）

### Gate 3 — 工厂自身回归

- ✅ `pytest .factory/tests/` 全过（≥ 30 个测试）
- ✅ `pytest tests/` 全过（uxeval 零回归）
- ✅ `pytest mcp-servers/` 全过
- ✅ `ruff check .factory` 通过
- ✅ `pyright .factory` 0 错

### Gate 4 — 端到端验证（用工厂装配 ai-analytics）

- ✅ 装配 ai-analytics 骨架，从 scaffold 命令执行到全部 gate 通过 ≤ 30 分钟
- ✅ 骨架过 validate
- ✅ 骨架能被 kernel `load_pipeline_skill` 加载
- ✅ 骨架的 pytest 测试（frontmatter / pipeline integration 占位测试）通过
- ✅ 骨架的目录结构与 evaluation archetype 定义一致

### Gate 5 — 文档与治理

- ✅ `.factory/README.md` 解释三大 archetype + 装配流程
- ✅ `.factory/CONTRACT.md`（本文件）落盘
- ✅ 每个 CLI 命令支持 `--help` 输出
- ✅ 错误消息带修复建议占比 ≥ 90%
- ✅ 工厂 CHANGELOG 记录每次 batch 的指标变化

---

## 5. Agent 边界与并行规则

### 5.1 Wave 划分

**Wave 1（串行，主控直接做）— 共享地基**

- `.factory/CONTRACT.md`（本文件）
- `.factory/README.md`
- `.factory/_kernel_bridge.py`（复用 kernel schemas 的桥层）
- `.factory/archetypes/archetype.schema.py`（用 Pydantic 定义"什么是一个 archetype"）
- `.factory/archetypes/evaluation.yaml`（手写最小可行版本，作为 Wave 2 的契约真源）
- `.factory/tests/test_kernel_bridge.py`（桥层回归）

**Wave 2（并行，3 个 Agent）— 三大工具**

| Agent | 模块 | 输入 | 自带闭环测试 |
|---|---|---|---|
| Agent A | `tools/extract.py` | CONTRACT + skills/uxeval | extract → 与手写 evaluation.yaml 对比 ≥ 90% 一致 |
| Agent B | `tools/validate.py` | CONTRACT + archetypes/evaluation.yaml + skills/uxeval | uxeval 通过 / 故障注入失败 / 错误消息可执行 |
| Agent C | `tools/scaffold.py` | CONTRACT + archetypes/evaluation.yaml | 装配出的骨架被 kernel 加载 / 过 validate / 过 preflight |

**Wave 3（串行）— 端到端验证**

- 用工厂装配 ai-analytics 骨架
- 跑 Gate 4 全部检查
- 落盘 changelog 记录指标实测值

### 5.2 Agent 自闭环规则（每个 Agent 必须满足）

每个 Wave 2 Agent 完成时必须返回：

1. ✅ 自己负责的代码（在自己的模块文件里，不动其他 Agent 的文件）
2. ✅ 自己负责的 pytest（在 `.factory/tests/test_<agent>.py`）
3. ✅ 跑过 `pytest .factory/tests/test_<agent>.py` 全部通过
4. ✅ 跑过 `ruff check .factory/tools/<module>.py` 通过
5. ✅ 跑过 `pyright .factory/tools/<module>.py` 0 错
6. ✅ 实测指标值（哪些驱动指标达成、未达成原因）
7. ✅ 不修改 `.factory/CONTRACT.md` / `.factory/_kernel_bridge.py` / `.factory/archetypes/`（地基只读）
8. ✅ 不修改 `skills/uxeval/`（uxeval 已冻结）
9. ✅ 不修改 `kernel/`（kernel 是真源）

### 5.3 Agent 并行冲突规避

- 同一时刻，每个 .factory/tools/ 下的文件只能由一个 Agent 写
- 公共地基（_kernel_bridge.py / archetypes/）由主控写，所有 Agent 只读
- 任意 Agent 发现需要改地基，必须停下来报告，由主控统一修改

---

## 6. 反模式（任何 Agent 都不允许）

- ❌ 重新定义 `SkillConfig` / `StageConfig` / `CheckpointConfig` / `OutputType` 等已存在于 kernel 的 schema（必须 import）
- ❌ 修改 `skills/uxeval/`（已冻结）
- ❌ 修改 `kernel/`（kernel 是真源）
- ❌ 装配产出"看起来对"但 kernel 加载不了的骨架（runtime truth 优先）
- ❌ 工厂代码不带测试就提交
- ❌ 工厂 import 任何 skill 内部模块（工厂只能 import kernel）
- ❌ 一个 Agent 同时写多个工具模块
- ❌ Agent 改地基（CONTRACT / kernel_bridge / archetypes）
- ❌ 错误消息只说"failed"，不给修复建议
- ❌ 跳过 ruff / pyright

---

## 7. Archetype 维度（必须萃取的共性）

evaluation archetype 至少要明确以下维度。Wave 2 Agent A（extract）必须能从 uxeval 萃取出每一项；Agent B（validate）必须能用每一项检查 skill。

| 维度 | 来源（uxeval 实证） | 工厂表达方式 |
|---|---|---|
| frontmatter 必填字段 | name / version / type / requires.kernel / outputs | archetype.required_frontmatter |
| outputs 类型约束 | issue_report / html_report / evidence_pack / delivery_audit_bundle | archetype.required_output_types |
| stage 阶段拓扑 | understanding → mapping → modeling → task-gen → evidence → attribution → audit → report | archetype.stage_topology |
| checkpoint 拓扑 | C1 (建模后) / C2 (任务后) / C3 (归因后) | archetype.required_checkpoints |
| audit gate 拓扑 | QG0 / QG1 / QG2 / QG3 | archetype.required_gates |
| 目录结构 | prompts/ reference/ templates/ eval/{golden,failure}/ tests/ | archetype.required_directories |
| evidence-related 字段 | inventory / coverage / confidence / trusted_mapping | archetype.evidence_contract |
| delivery-related 字段 | final_delivery_ready / fallback_safe / supplement_required / blocked | archetype.delivery_contract |
| 模式可选项 | web/client（uxeval 的 mode 是证据采集差异） | archetype.mode_semantics（标注语义类型） |

⚠️ **mode 语义不能跨 archetype 强行统一**：
- evaluation 的 mode = 证据采集方式
- generation 的 mode = 保真度档位（如 prd2proto）
- analysis 的 mode = 数据来源（如 ai-analytics）

archetype.yaml 必须显式声明 mode_semantics 类型，validate 时按各自语义校验。

---

## 8. 一句话总纲

> **工厂搭好的标志不是"代码写完"，而是"用工厂装配 ai-analytics 比手写 uxeval 快至少 10 倍，且零质量妥协"。**
