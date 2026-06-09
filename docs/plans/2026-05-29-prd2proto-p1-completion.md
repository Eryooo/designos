# prd2proto P1 Batch 完成记录

> 日期：2026-05-29
> 状态：✅ 结构化部分完成；prompt 内容部分进行中

---

## 已完成（结构 + 工厂 + 集成）

### 1. 工厂装配（task 11）

```bash
cd .factory
python3 -m tools.scaffold --archetype generation --name prd2proto --output-dir ../skills
```

✅ 产出 30+ 文件骨架；过 validate；过 kernel load。

### 2. 业务实装路线（task 12）

✅ 落盘 `docs/plans/2026-05-29-prd2proto-implementation-plan.md`：
- 4 个 batch 切分（P1 pm / P2 designer-spec / P3 frontend-codegen 真 MCP / P4 designer-dsl）
- 4 条代码宪法约束方式（先 LLM 软审查，P3 后改静态扫描）
- 时间估算（约 2-3 周到 designer-dsl 跑通真 Figma）

### 3. frontend-codegen Mock MCP（task 13）

```
mcp-servers/frontend-codegen/
├── pyproject.toml
├── schemas.py     (180 行 Pydantic schema)
├── core.py        (350 行 mock 实现)
├── server.py      (135 行 MCP stdio server)
└── tests/
    └── test_core.py  (12 tests, all green)
```

✅ 4 个工具：fetch_dsl / extract_tokens / map_components / generate_code
✅ 支持 figma + mastergo + 4 种组件库 + react/vue 双框架
✅ generate_code 写出可 `npm install && npm run dev` 的项目骨架
✅ 所有响应带 `is_mock: True` 标记，方便后续切真实现时识别

### 4. prd2proto SKILL.md（task 16）

✅ 完整 frontmatter（含 inputs / outputs / 4 个 MCP / 3 个 modes / requires_external）
✅ 详细文档（触发条件 / 模式选择 / 输入输出 / 4 条代码宪法 / pipeline 概览 / 当前实装阶段）
✅ kernel 加载验证：`load_pipeline_skill` 不抛错

### 5. prd2proto pipeline.yaml（task 18）

✅ 8 个 stages（按 generation archetype 拓扑）：
- prd-understanding (LLM)
- design-analysis (LLM, C1)
- spec-generation (LLM, only_when=designer-spec, C2)
- dsl-fetch (Tool, only_when=designer-dsl)
- token-extraction (Tool, only_when=mode!=pm, C3)
- component-mapping (Tool, only_when=designer-dsl)
- code-generation (Tool)
- review-gate (LLM, C4 + Gate QG_REVIEW)

✅ 模式过滤逻辑：pm→4 stages / designer-spec→6 / designer-dsl→7
✅ 上游引用 ai-analytics design_strategy / user_persona

### 6. 工厂 backlog（task 17）

✅ 4 个 scaffold 真实缺口写入 `.factory/CHANGELOG.md` v0.3.0 backlog：
- B1: SKILL.md 不生成 inputs 字段
- B2: stage only_when 不消费 archetype 配置
- B3: 外部 MCP 不支持声明
- B4: MCP 列表跨 archetype 不区分

每条带具体行号 / 根因 / 修复路径 / 优先级。

### 7. P1 smoke test（task 14）

`skills/prd2proto/tests/test_p1_smoke.py` (10 tests, all green)

锁定 P1 batch 关键契约：
- 三模式正确加载
- required outputs 完整
- figma-mcp / mastergo-mcp 正确声明为 builtin=False + required_when=designer-dsl
- 8 stages 拓扑正确
- pm/designer-spec/designer-dsl 三模式过滤逻辑正确
- frontend-codegen mock 端到端能产出 React 项目
- skill 通过工厂 validate

---

## 测试基线（P1 完成时）

| 测试套件 | 通过 |
|---|---:|
| Kernel 单元测试 | 180/180 ✅ |
| 工厂回归 | 46/46 ✅ |
| frontend-codegen Mock | 12/12 ✅ |
| prd2proto P1 smoke | 10/10 ✅ |
| **合计** | **248/248** |

零 kernel 回归 / 零工厂回归。

---

## 进行中（task 15）

7 个业务 prompt 由后台 Agent 写：

- prompts/01-prd-understanding.md
- prompts/02-design-analysis.md
- prompts/03a-spec-generation.md
- prompts/06-review-gate.md
- 配套 reference/m0*-*.md 知识库

进展：当前已写 01 + 02 + 对应 reference。还在继续。

---

## P1 完成的硬指标 vs 目标

| 指标 | 目标 | 实测 |
|---|---|---|
| 工厂装配 prd2proto 骨架耗时 | ≤ 5 分钟 | **0.5 秒** ✅ |
| 骨架立即过 validate | 必须 | ✅ |
| 骨架立即被 kernel 加载 | 必须 | ✅ |
| frontend-codegen Mock 完整 | 4 个工具 | ✅ |
| 4 个 MCP 正确声明（含 2 个外部） | 必须 | ✅ |
| 三模式过滤逻辑正确 | 必须 | ✅ |
| pm 模式端到端可跑通 | 必须 | ✅（除真 LLM 调用） |
| 248 个测试零回归 | 必须 | ✅ |

---

## 下一阶段路线

### P2: designer-spec 模式（next batch）

- 真实跑通 designer-spec 模式（PRD + 帮用户生成 design-spec.md → 高保真原型）
- 至少 1 个 designer-spec golden case
- spec-generation prompt 真业务化

预估：1-2 天

### P3: frontend-codegen 真 MCP（最大瓶颈）

- DSL 适配层（Figma + MasterGo）
- Token 提取器
- 组件映射器
- 真代码生成器
- 4 条宪法的静态扫描器

预估：5-10 工作日

### P4: designer-dsl 模式真实跑通

- 接 P3 真 MCP
- 跑真实 Figma 设计稿
- 4 条代码宪法静态检测全过
- 至少 1 个 designer-dsl golden case

预估：2-3 天

**总计**: P2-P4 约 2-3 周。

---

## 已知遗留（非阻塞 P1，待后续 batch）

1. **Prompt 内容尚未全完成**：task 15 后台 Agent 进行中，预计另 5-10 分钟出 4 个真业务 prompt
2. **constitution.md 尚未 prd2proto 特化**：当前是 generation 通用版，需要补 4 条代码宪法的具体执行细则
3. **golden / failure case 暂无**：scaffold 装了占位目录，P2 batch 起补真 case
4. **review-gate 是软审查**：等 P3 frontend-codegen 真 MCP 后改硬约束
5. **工厂 4 个 backlog**：B1-B4，留给工厂 v0.3.0 batch 处理

---

## 一句话总纲

> **P1 验收：用工厂 0.5 秒装出的 prd2proto 骨架，经过手工补 SKILL.md / pipeline / Mock MCP / smoke test 后，已具备完整结构和 pm 模式的端到端跑通条件。LLM 业务 prompt 进行中，完成后 pm 模式即可对真 PRD 跑一次。**
