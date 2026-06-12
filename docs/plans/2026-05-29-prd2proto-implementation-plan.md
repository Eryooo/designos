# prd2proto 业务实装路线（A 路线 + Figma/MasterGo）

> 决策日期：2026-05-29
> 决策：先用工厂装骨架 + frontend-codegen Mock MCP 占位 → 端到端跑通 → 暴露真实需求 → 再实装真 MCP
> 用户已确认：支持 Figma 和 MasterGo 两个 DSL 工具

---

## 1. 当前状态

✅ 工厂装配 prd2proto 骨架完成（`skills/prd2proto/`）
✅ 4 stages, 3 modes, 2 outputs，过 validate + 过 kernel load
❌ 暴露 4 个 scaffold 真实缺口（见 §5）

---

## 2. 业务范围

prd2proto 的 3 个模式按"代码生产保真度"分级：

| 模式 | 用户 | 输入 | 输出 | 核心约束 |
|---|---|---|---|---|
| **pm** | PM | PRD | 低保真演示原型 | 形式跑通即可 |
| **designer-spec** | 设计师 | PRD + design-spec.md | 高保真原型 | 含 Token、状态覆盖 |
| **designer-dsl** | 设计师 | DSL（Figma/MasterGo）+ design-spec.md + 本地组件库 | 生产可用代码 | 4 条代码宪法硬约束 |

### 2.1 4 条代码宪法（来自 ADR-003）

1. ❌ 不得硬编码颜色 / 字号 / 间距 → 必须用 Token 变量
2. ❌ 不得自行编写基础组件 → 必须复用本地组件库
3. ❌ 不得跳过状态覆盖 → 默认/悬停/按下/聚焦/禁用/加载/错误 七种
4. ❌ 不得忽略 Design.md 约束（团队约定优先级最高）

**当前阶段**: 以 LLM 软审查实现（review_gate stage）；frontend-codegen MCP 实装后改为静态扫描硬约束。

---

## 3. 实装 batch 切分

### Batch P1: pm 模式端到端跑通（本批主目标）

只让 pm 模式能跑通：PRD → 低保真原型代码（一个能跑的 React/Vue 项目）。

**交付物**:
- ✅ frontend-codegen Mock MCP（占位，3 个工具返回固定示例）
- ✅ 改造 SKILL.md（补 inputs + 外部 MCP 引用）
- ✅ 改造 pipeline.yaml（补 7 stages + only_when 模式分支）
- ✅ 写 7 个业务 prompt（不是占位）
- ✅ pm 模式端到端 smoke test

**验收门**:
- pm 模式跑完一次，产出能 `npm install && npm run dev` 启动的 React 项目骨架
- review_gate 能给出 4 条宪法的软审查报告
- kernel 零回归、工厂零回归

**不做**:
- ❌ designer-spec / designer-dsl 模式真业务（用占位 stage，scaffold 加 only_when 跳过）
- ❌ 真 frontend-codegen MCP（DSL 解析 / Token 提取 / 组件映射）
- ❌ 4 条宪法的静态检测（先靠 LLM 自我审查）

---

### Batch P2: designer-spec 模式（下一批）

**前置**: P1 完成 + 至少 1 个真实 PRD 跑通

**新增**:
- spec-generation stage 业务化（PRD → design-spec.md）
- design-spec.md 模板 + reference 知识库
- C2 checkpoint 用户确认 spec
- pm + designer-spec 两个模式 golden case

**仍不做**:
- ❌ DSL 解析（要 frontend-codegen 真 MCP）

---

### Batch P3: frontend-codegen MCP 真实装（大工程，预估 1-2 周）

**目标**: 把 4 条代码宪法从软约束变成硬约束。

**模块**:

#### 3.1 DSL 适配层（Figma + MasterGo）

| 适配器 | 输入 | 输出 |
|---|---|---|
| `dsl/figma_adapter.py` | Figma 文件 ID + access token（or 图标本地导出 JSON） | 标准化 DSL（NodeTree） |
| `dsl/mastergo_adapter.py` | MasterGo 项目 ID | 标准化 DSL |
| `dsl/__init__.py` | 自动识别来源 | 调对应 adapter |

**外部 MCP 选项**: 用户从社区装 figma-mcp / mastergo-mcp，frontend-codegen 通过 SDK 或 stdio 调它们。CONTRACT 把它们标 `builtin=false, required_when='mode == "designer-dsl"'`。

#### 3.2 Token 提取器

| 工具 | 行为 |
|---|---|
| `extract_tokens(dsl, design_md)` | 从 DSL + design.md 综合提取 colors / typography / spacing / radius 等 Token |
| 输出 | `design-tokens.json`（W3C Design Tokens Format） |

#### 3.3 组件映射器

| 工具 | 行为 |
|---|---|
| `map_components(dsl, lib_ref)` | DSL node → 本地组件库组件名（AntDesign Vue / Element Plus 任一） |
| `lib_ref` 来源 | 用户在 SKILL config 里声明 `component_lib: antd-vue` 等 |
| 命中阈值 | 90%+ 节点能映射到组件库；剩下用兜底元素 |

#### 3.4 代码生成器

| 工具 | 行为 |
|---|---|
| `generate_code(node_tree, tokens, component_map)` | 输出 React/Vue 代码 + 7 种状态全覆盖 + 全 token 变量 |

#### 3.5 宪法检测器（static analyzer）

| 检测 | 实现 |
|---|---|
| 硬编码颜色检测 | AST 扫描所有 `#hex` / `rgb()` / `rgba()`，必须来自 token |
| 硬编码字号检测 | AST 扫描所有 `font-size` 字面量 |
| 硬编码间距检测 | AST 扫描 `padding` / `margin` 字面量 |
| 自定义基础组件检测 | 比对 import 列表，所有 `<Button>` / `<Input>` 等必须来自组件库 |
| 状态覆盖检测 | 每个交互组件必须有 `:hover` / `:active` / `:focus` / `:disabled` |
| Design.md 约束检测 | 解析 Design.md 提取规则 → 比对生成代码 |

#### 3.6 测试 / 集成

- 单元测试每个适配器
- 集成测试：sample DSL → 生成代码 → 跑宪法检测应该全过
- E2E 测试：真 Figma DSL → 真组件库 → 生成代码能 build

---

### Batch P4: designer-dsl 模式跑通

接 P3 真 MCP，把 designer-dsl 的 4 个新 stage 真实化：dsl-fetch / token-extraction / code-generation / review-gate（硬约束版）。

**验收门**:
- designer-dsl 模式跑完一次真实 Figma 设计稿
- 4 条代码宪法静态检测全过
- 生成的代码能 `npm run build` 通过 + 跑 lint
- 至少 1 个 designer-dsl golden case

---

## 4. 时间估算

| Batch | 预估 | 主要风险 |
|---|---|---|
| P1 (pm 模式跑通) | 半天-1天 | 无重大风险 |
| P2 (designer-spec 模式) | 1-2天 | spec 模板需要打磨几轮 |
| P3 (frontend-codegen 真 MCP) | **5-10 工作日** | DSL 适配器复杂；Figma SDK / MasterGo API 不稳；组件库映射需要规则库；最大风险点 |
| P4 (designer-dsl 模式) | 2-3 天 | 主要看 P3 质量；可能要回头改 P3 |

**总计**: 约 2-3 周到 designer-dsl 跑通真实 Figma 设计稿。

---

## 5. 工厂缺口（scaffold 需补，已记 backlog）

prd2proto 装配暴露的 scaffold 真实问题（不阻塞 prd2proto，留给后续工厂迭代）：

1. **SKILL.md 不生成 inputs 字段** — 当前 prd2proto SKILL.md 只有 outputs，没 inputs。kernel 不强校验所以装配能过，但实际跑会缺。
2. **stage only_when 不消费 archetype 配置** — `generation.yaml` 的 stage_slots 已经声明 `only_when_modes: [designer-dsl]`，但 scaffold.py 没读这个字段往 pipeline.yaml 里塞 `only_when:` 表达式。
3. **外部 MCP 不支持声明** — scaffold 的 `_DEFAULT_MCP_SERVERS = ["pdf-parser", "excel-builder"]` 硬编码 builtin。archetype 里没字段告诉 scaffold 要挂哪些 MCP（更别说外部 MCP 的 `requires_external` block）。
4. **MCP 列表跨 archetype 不区分** — generation 应该挂 frontend-codegen + figma-mcp + mastergo-mcp；analysis 应该挂 competitor-scraper；evaluation 应该挂 image-analyzer + heuristic-engine + playwright-driver。当前都是 pdf-parser + excel-builder。

→ 这些缺口的修复留给后续工厂 v0.3.0 batch。当前 prd2proto 业务实装直接手工补 SKILL.md / pipeline.yaml。

---

## 6. 一句话总纲

> **本批不解决 prd2proto 终极目标（生产代码），先让它在 pm 模式跑通端到端，把 designer-dsl 模式真实需求 (frontend-codegen MCP) 看清楚再投入大工程。**
