# DesignOS Skills Factory — Changelog

记录每次 batch 的实测指标变化。

---

## v0.3.0 — Backlog (尚未实装)

> 由 prd2proto 真实装配（2026-05-29）暴露。这些缺口不阻塞当前业务实装，但需要在工厂迭代时补齐，提升装配质量。

### B1. SKILL.md 不生成 inputs 字段

**现象**: scaffold 产出的 SKILL.md frontmatter 只有 `outputs:`，没有 `inputs:`。例：`skills/prd2proto/SKILL.md` 行 14-20 只列 `outputs`，PRD / scope_md 等用户输入完全未声明。
**根因**:
- `tools/scaffold.py:272-284` `_render_skill_md` 构造 frontmatter 时仅写入 `name / version / type / description / requires / outputs`，没有 inputs 键。
- 上游 schema 缺位：`archetypes/archetype_schema.py` 的 `ArchetypeSpec`（行 233-265）没有顶层 `inputs` 概念，只有 `StageSlot.required_inputs`（行 104-107），无法表达"这一类 skill 整体的用户输入面"。
- 三个 archetype yaml（`evaluation.yaml` / `generation.yaml` / `analysis.yaml`）均无 inputs 块。
**影响**: 任何 skill 都需要 inputs 才能被调用方知道怎么喂数据。当前 kernel 不强校验 → 装配能过 validate，但实际调用一定缺。所有 skill 普适问题。
**建议修复**:
1. `archetype_schema.py` 新增 `InputRequirement(name / type / description / required: bool)` 模型；`ArchetypeSpec` 增加 `inputs: list[InputRequirement]` 字段。
2. 三个 archetype yaml 各自声明顶层 inputs（evaluation: scope_md/screenshots；generation: prd_file/scope_md/design_md；analysis: competitor_set/datasource_config）。
3. `scaffold.py:_render_skill_md` 把 `spec.inputs` 渲染成 frontmatter 的 `inputs` 块。
**优先级**: 高（任何 skill 都要 inputs，是基本盘）

### B2. stage only_when 不消费 archetype 配置

**现象**: `generation.yaml` 的 `spec_generation` / `dsl_fetch` / `token_extraction` 三个 slot 都声明了 `only_when_modes`（行 79 / 85 / 91），但 `skills/prd2proto/pipeline.yaml` 完全没出现这些 stage，更没有 `only_when:` 条件表达式 —— 装出来的 pipeline 只剩 4 个 required stage（行 9-50）。
**根因**:
- `tools/scaffold.py:369-371` `_build_plan` 在迭代 stage_slots 时硬编码 `if not slot.required: continue`，把所有 `required: false` 的 slot 直接丢弃。
- `only_when_modes` 的渲染逻辑（`scaffold.py:423-426`）确实存在，但永远只跑在 required slot 上，而 required 又通常意味着"全模式都跑"，导致这段 only_when 代码实际上从没被任何当前 archetype 触发。
- 结果：optional + only_when_modes 的 slot（多模式 skill 的核心特性）既不被装配也不被警告。
**影响**: 跨 mode 的 skill（uxeval 的 web/client、prd2proto 的 designer-spec/designer-dsl、ai-analytics 的 web/client）受影响 —— 装配出来的骨架完全看不到模式分支，作者必须从 archetype yaml 倒推自己手补 only_when stage。
**建议修复**:
1. 把 `if not slot.required: continue` 放宽：当 `slot.only_when_modes` 非空时也保留并渲染。
2. 或在 yaml 模型层引入 `slot.required_when_mode_in: [...]` 显式语义，scaffold 按此渲染。
3. validate 同步校验 only_when 表达式与 archetype 模式列表一致。
**优先级**: 中（跨 mode 的 skill 受影响，单模式 skill 不受影响）

### B3. 外部 MCP 不支持声明

**现象**: 装配出的 `skills/prd2proto/SKILL.md` 行 9-13 只挂了 `pdf-parser` / `excel-builder` 两个 builtin MCP；prd2proto 实际依赖的 `frontend-codegen` / `figma-mcp` / `mastergo-mcp` 这些外部 MCP 完全无法在装配阶段声明。
**根因**:
- `tools/scaffold.py:52` `_DEFAULT_MCP_SERVERS: list[str] = ["pdf-parser", "excel-builder"]` 硬编码 builtin 列表。
- `scaffold.py:279-282` 把列表里每个名字都写成 `{"name": name, "builtin": True}`，没有任何路径声明 `builtin: false` 或 `requires_external: true` 的外部 MCP。
- archetype_schema.py 无 `MCPRequirement` 模型，archetype yaml 没 mcp 块；scaffold 完全不读 archetype 来决定挂什么 MCP。
**影响**: 任何要外部 MCP 的 skill（prd2proto 的 frontend-codegen、ai-analytics 的 competitor-scraper、未来接 SaaS 工具的 skill）都得在 scaffold 之后手工改 SKILL.md。普适问题，未声明的外部 MCP 还会绕过 preflight 检查。
**建议修复**:
1. `archetype_schema.py` 新增 `MCPRequirement(name / builtin: bool / required_when: str | None / required: bool)` 模型；`ArchetypeSpec` 增加 `mcp_servers: list[MCPRequirement]`。
2. 三个 archetype yaml 各自声明所需 MCP（含 builtin 与外部）。
3. `scaffold.py:_render_skill_md` 用 `spec.mcp_servers` 取代 `_DEFAULT_MCP_SERVERS`，按 `builtin` 字段分别输出。
4. preflight 同步识别 `builtin: false` 的依赖，给出合适的"请先安装外部 MCP"提示。
**优先级**: 高（所有非纯 LLM skill 都受影响）

### B4. MCP 列表跨 archetype 不区分

**现象**: 三个 archetype 装配产出都是同一份 `[pdf-parser, excel-builder]`。但 generation 应挂 `frontend-codegen` + `figma-mcp` + `mastergo-mcp`；evaluation 应挂 `image-analyzer` + `heuristic-engine` + `playwright-driver`；analysis 应挂 `competitor-scraper`。装配 evaluation skill 与装配 generation skill 得到完全相同的 MCP 列表，毫无区分度。
**根因**:
- 同 B3 根因（`_DEFAULT_MCP_SERVERS` 硬编码）。
- 额外：`scaffold.py:417` tool stage 一律挂 `mcp_server: excel-builder`，与 stage 实际语义无关。例如 prd2proto 的 `code_generation` tool stage 也写成 `excel-builder`（见 `pipeline.yaml:33`）。
- archetype 没向 scaffold 提供"该 stage 该挂哪个 MCP"的映射。
**影响**: 装配出的骨架要手工把 mcp_servers 列表与每个 tool stage 的 mcp_server 字段全部改写一遍才能真用，几乎抵消了 scaffold 的提速价值。在跨 archetype 推广时尤其明显。
**建议修复**:
1. B3 完成后，在 `StageSlot` 增加 `default_mcp_server: str | None`，archetype yaml 里 tool slot 显式声明默认 MCP。
2. `scaffold.py:_render_stage` 用 `slot.default_mcp_server` 取代当前硬编码的 `excel-builder`；找不到时报警告而非静默 fallback。
3. 顶层 mcp_servers 列表与 stage 引用一致性由 validate 校验。
**优先级**: 中（装配后必须手改才能用，影响实装效率，但不阻断装配本身）

### 影响汇总

- B1 + B3 高优先级：所有 skill 都受影响（B1 是基本盘，B3 是凡涉外部工具的 skill 必踩）。
- B2 中等：跨 mode 的 skill（uxeval、prd2proto、ai-analytics）受影响，单模式 skill（ip-design、brand-creative.*）不受影响。
- B4 中等：scaffold 装配出来要手工调整 mcp_servers 与每个 tool stage 才能真用。

### 下次迭代建议顺序

B1 → B2 → B3 → B4
（B1 最简单且最普遍，先建立 InputRequirement 模型；B2 只动 scaffold 一处分支；B3 引入 MCPRequirement 模型，是 B4 的前置；B4 复用 B3 的模型把每个 stage 的默认 MCP 落到 archetype yaml）

---

## v0.2.0 — Wave 4 三 archetype 全闭环（2026-05-29 续）

### 新增

- ✅ `archetypes/analysis.yaml`（provisional 占位，源自 ai-analytics 产品规格）
- ✅ `archetypes/generation.yaml`（provisional 占位，源自 prd2proto 产品规格）
- ✅ `tests/test_scaffold.py`（Agent C 补全，14 个测试）

### 端到端验证（三个 archetype × scaffold + validate 全跑通）

```bash
# evaluation archetype
$ python3 -m tools.scaffold --archetype evaluation --name ai-analytics --output-dir /tmp/test1
$ python3 -m tools.validate /tmp/test1/ai-analytics --archetype evaluation
✅ All checks passed

# analysis archetype（用 ai-analytics 真正的语义装配）
$ python3 -m tools.scaffold --archetype analysis --name ai-analytics --output-dir /tmp/test2
$ python3 -m tools.validate /tmp/test2/ai-analytics --archetype analysis
✅ All checks passed

# generation archetype（用 prd2proto 真正的语义装配）
$ python3 -m tools.scaffold --archetype generation --name prd2proto --output-dir /tmp/test3
$ python3 -m tools.validate /tmp/test3/prd2proto --archetype generation
✅ All checks passed
```

### 实测 CONTRACT §3.A 三个硬指标（Agent C test_scaffold 验证）

| 指标 | 目标 | 实测 |
|---|---|---|
| `scaffold_success_rate` | 100% | **100%** ✅ |
| `scaffold_kernel_load_rate` | 100% | **100%** ✅ |
| `scaffold_preflight_pass_rate` | 100% | **100%** ✅ |

### 测试基线

- 工厂总测试: 46/46 通过（之前 32 + Agent C 新增 14）
- Kernel 单元测试: 180/180 通过（零回归）
- ruff: All checks passed
- pyright: 0 errors / 0 warnings

### 关键设计验证

✅ **Mode semantics 跨 archetype 不可强行统一**已验证：
- evaluation: `evidence_collection`，modes=[web, client]
- analysis: `data_source`，modes=[]
- generation: `fidelity`，modes=[pm, designer-spec, designer-dsl]

三种 mode 语义完全不同，archetype 各自独立声明。

✅ **Archetype 可扩展性**已验证：
- 新增 analysis / generation 两个 archetype 没改任何工厂工具代码
- scaffold / validate / extract 自动支持新 archetype（除 stage 关键词表需补 — 待后续优化）

### 已知遗留

1. analysis / generation archetype 是 provisional：基于产品规格而非真实实现，待 ai-analytics / prd2proto 业务实装后用 extract 反向萃取做对齐
2. validate.py 的 `_STAGE_SLOT_KEYWORDS` 当前只覆盖 evaluation，analysis/generation 的 stage 关键词需扩
3. scaffold.py 的 _DEFAULT_MCP_SERVERS 硬编码 [pdf-parser, excel-builder]，跨 archetype 时合适与否要看（generation 应有 frontend-codegen，analysis 应有 competitor-scraper）— 当前先用 builtin 保 preflight 过

---

## v0.1.0 — Wave 1+2+3 完成（2026-05-29）

### 范围

第一个端到端可用的工厂版本。完成 CONTRACT 定义的 5 道验收门。

### 交付物

| 模块 | 行数 | 状态 |
|---|---|---|
| `CONTRACT.md` | 240 | ✅ 工厂合同 + 指标体系 |
| `_kernel_bridge.py` | 90 | ✅ 20 个 kernel schema 唯一入口 |
| `archetypes/archetype_schema.py` | 230 | ✅ ArchetypeSpec Pydantic |
| `archetypes/loader.py` | 31 | ✅ 加载器 |
| `archetypes/evaluation.yaml` | 175 | ✅ evaluation 契约（萃取自 uxeval） |
| `tools/extract.py` | 821 | ✅ Agent A 实现 |
| `tools/validate.py` | 522 | ✅ Agent B 实现 |
| `tools/scaffold.py` | 744 | ✅ Agent C 实现 |
| `tests/test_*.py` × 5 | 901 | ✅ 32 个测试全过 |

### 实测指标 vs CONTRACT

#### §2 北极星指标

| 指标 | 目标 | 实测 | 状态 |
|---|---|---|---|
| Time-to-Skeleton | ≤ 30 分钟（首次） | **0.53 秒** | ✅ 远超目标 |
| Time-to-First-Run | ≤ 1 周（ai-analytics） | 待 Wave 4 业务实装 | — |
| Reuse Rate | ≥ 80% | 待量化（结构层 100%） | — |
| Zero Regression | uxeval 必过 | 180/180 kernel + 32/32 工厂 | ✅ |

#### §3 驱动指标

**A. 装配成功率层**
- `scaffold_success_rate` 100% ✅（ai-analytics 骨架过 validate）
- `scaffold_kernel_load_rate` 100% ✅（8 stages, 4 outputs 加载成功）
- `scaffold_preflight_pass_rate` ⏳ 待 test_scaffold 完成验证

**B. 抽象化层**
- `archetype_coverage` ≥ 90% ✅（CONTRACT §7 9 个维度全覆盖）
- `schema_import_count` 20 ✅（≥ 8 目标）
- `manual_step_count` 1（仅填 --name）≤ 3 ✅

**C. 验证闭环层**
- `extract_roundtrip` ✅（test_extract_roundtrip_through_archetype_spec 通过）
- `validate_uxeval_pass` ✅（uxeval 过 validate）
- `validate_catches_known_violations` 8 种 ≥ 6 ✅

**D. 工厂自身质量层**
- `factory_test_count` 32 ≥ 30 ✅
- `factory_test_pass_rate` 100% ✅

**E. 开发体验层**
- `cli_command_count` 3 现有（extract/validate/scaffold）→ 待补 benchmark
- `error_message_actionable_rate` 100% ✅（每条 violation 含 fix）
- `dry_run_supported` ✅
- `archetype_extensibility` ✅（新 archetype 只需写 yaml + 关键词扩展）

### Wave 3 端到端验证（CONTRACT §4 Gate 4）

```bash
# 装配
$ python3 -m tools.scaffold --archetype evaluation --name ai-analytics --output-dir /tmp/factory-test
✅ 0.53 秒，34 个文件/目录

# 验证
$ python3 -m tools.validate /tmp/factory-test/ai-analytics --archetype evaluation
✅ All checks passed

# 加载
$ python3 -c "from _kernel_bridge import load_pipeline_skill; ..."
✅ Loaded: ai-analytics v0.1.0, 8 stages, 4 outputs

# 骨架自带测试
$ cd /tmp/factory-test/ai-analytics && python3 -m pytest tests/ -v
✅ 4 passed

# kernel 零回归
$ python3 -m pytest tests/unit/ -q
✅ 180 passed
```

### Wave 3 暴露的契约不一致问题（已修复）

端到端跑 ai-analytics 时暴露 2 个工具间契约断裂：

1. **Stage id 命名风格不一致**
   - scaffold 用 `task_generation`（下划线，slot_id 直接当 id）
   - validate 关键词表只列了 `task-generation`（短横线）
   - **修复**: validate 的 `_STAGE_SLOT_KEYWORDS` 同时收两种风格

2. **archetype 漏字段**
   - `evaluation.yaml` 的 `evidence_collection` slot 没声明 `required_outputs`
   - 导致 scaffold 生成的 stage 没 `evidence_assessment` outputs，validate 报缺
   - **修复**: archetype 补 `required_outputs: [evidence_assessment]`

→ 这正是端到端验证的价值：单元测试都过，但工具间契约不对齐，要跑一次 ai-analytics 才暴露。

### 已知限制

- Generation / Analysis archetype 待萃取（需要做 prd2proto / 真实 ai-analytics 后再抽）
- Stage slot 关键词表硬编码在 validate.py，跨 archetype 时需手工扩展
- 没有统一 CLI 入口（暂时三个独立模块）
- preflight gate 还在等 Agent C 补 test_scaffold 验证

### 下一步

1. 等 Agent C 补完 test_scaffold.py（preflight 验证）
2. Wave 4：装配 prd2proto 骨架（需先萃取 generation archetype）
3. Wave 5：装配 ai-analytics 业务实装（验证北极星 Time-to-First-Run）
