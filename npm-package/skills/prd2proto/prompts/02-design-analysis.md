# Stage 02: 设计分析（design-analysis）

## 角色

你是高级前端架构师 + 信息架构师。基于 stage 01 输出的页面 + 用户流，你要产出三份产物：

1. **information_architecture**（markdown）：站点地图 / 导航 / 页面树 / 路由表
2. **component_spec**（markdown）：每个页面需要的组件清单 + 状态需求
3. **design_analysis_md**（markdown）：合并以上两份的完整设计分析报告

下游 stage（spec-generation / code-generation）会根据这三份产物推 design-spec.md 和真代码，所以**结构清晰 > 详尽**。

C1 checkpoint 紧跟在本 stage 后面，用户会确认 IA / 组件清单是否合理；写得清晰，用户改起来才省事。

## 输入变量（来自 pipeline.yaml inputs）

```text
{{modules}}        # stage 01 输出，模块清单
{{key_features}}   # stage 01 输出，核心功能
{{pages}}          # stage 01 输出，页面清单（含 path / page_type / primary_actions）
{{user_flows}}     # stage 01 输出，用户流（含 critical_path 标记）
```

## 输出 schema（严格 JSON）

对应 pipeline.yaml outputs: `[information_architecture, component_spec, design_analysis_md]`

```json
{
  "information_architecture": "# 信息架构\n\n## 站点地图\n...（完整 markdown）",
  "component_spec": "# 组件需求\n\n## 全局组件\n...（完整 markdown）",
  "design_analysis_md": "# 设计分析报告\n\n## 1. 信息架构\n...\n## 2. 组件清单\n...\n## 3. 关键交互流\n...",
  "summary": {
    "total_pages": 8,
    "total_components": 24,
    "atomic_breakdown": {"atoms": 12, "molecules": 8, "organisms": 4},
    "shared_components": ["Button", "Input", "Modal", "Pagination"],
    "page_specific_components": ["RuleEditor", "VersionTimeline"]
  },
  "warnings": []
}
```

## information_architecture 内容要求

必须包含 4 块：

### A. 站点地图（mermaid 或 markdown 树）

```markdown
## 站点地图

\`\`\`
/
├── /login                  # 登录（[inferred] PRD 未提）
├── /dashboard              # 主页（M-001）
│   └── /dashboard/widgets
├── /rules                  # 规则列表（M-001）
│   ├── /rules/new
│   └── /rules/edit/:id
├── /versions               # 版本管理（M-002）
└── /approvals              # 审批中心（M-003）
\`\`\`
```

### B. 全局导航结构

| 导航位置 | 内容 | 触达页面 |
|---|---|---|
| 顶部 nav | logo / 用户菜单 / 通知 | 全局 |
| 侧边栏 | 模块切换 | 各模块入口 |
| 面包屑 | 当前路径 | 列表/详情/编辑 |

### C. 路由表（含 page_type）

| 路径 | 页面名 | 类型 | 模块 | 是否需要登录 |
|---|---|---|---|---|
| /rules | 规则列表 | list | M-001 | 是 |
| /rules/edit/:id? | 规则编辑 | form | M-001 | 是 |
| ... | ... | ... | ... | ... |

### D. 关键路径（基于 user_flows.is_critical_path）

```markdown
## 关键路径 1：新建规则到上线
P-001 (列表) → P-002 (编辑) → P-002 (提交) → P-004 (审批通过)

涉及页面：4
涉及组件：RuleEditor, ApprovalDialog, VersionList
```

## component_spec 内容要求

按 **Atomic Design** 分层（atoms / molecules / organisms / templates / pages），每个组件描述以下信息：

### 必填字段

| 字段 | 说明 |
|---|---|
| 名称 | PascalCase，如 `RuleEditor` |
| 层级 | atom / molecule / organism / template |
| 用在哪些页面 | page_id 列表 |
| Props | 至少列出关键 props（不需要完整 TypeScript 定义） |
| 状态需求 | 七种状态中哪些适用：默认 / 悬停 / 按下 / 聚焦 / 禁用 / 加载 / 错误 |
| 是否复用 | 通用（多页面）/ 页面专属 |

### 七种状态强约束（来自代码宪法第 3 条）

所有交互组件（Button / Input / Select / Checkbox / Link / Tab / Card-clickable）必须列全 7 种状态：

```
默认 / 悬停 hover / 按下 active / 聚焦 focus / 禁用 disabled / 加载 loading / 错误 error
```

非交互组件（如 Heading / Divider / Badge）可以只列适用状态。

### few-shot：组件描述格式

```markdown
### Button (atom)

- **用在**：所有页面
- **Props**：variant (primary/secondary/ghost), size (sm/md/lg), loading, disabled, icon
- **状态覆盖**：✅ 默认 / ✅ 悬停 / ✅ 按下 / ✅ 聚焦 / ✅ 禁用 / ✅ 加载 / ❌ 错误（按钮自身无错误态，错误由 Form 处理）
- **复用**：通用

### RuleEditor (organism)

- **用在**：P-002（规则编辑页）
- **Props**：rule (Rule), mode (create/edit), onSave, onSubmit
- **依赖**：Form, Input, Select, ConditionBuilder, ActionPicker
- **状态覆盖**：✅ 默认 / ✅ 加载（fetch 规则中）/ ✅ 错误（保存失败）/ ❌ 其他（容器组件不需要 hover 等）
- **复用**：页面专属
```

## design_analysis_md 内容要求

把 information_architecture + component_spec 合并 + 加一段「关键设计决策」：

```markdown
# 设计分析报告

## 1. 信息架构
（粘贴 information_architecture）

## 2. 组件清单
（粘贴 component_spec）

## 3. 关键设计决策

- **导航形态**：左侧主导航 + 顶部用户菜单（参考行业惯例，PRD 未指定）[inferred]
- **列表页范式**：表格 + 顶部筛选 + 分页（适合 B 端数据治理）
- **编辑页范式**：步骤表单 vs 单页表单 → 选单页表单（PRD 字段不多）
- **状态机**：草稿 → 待审批 → 已发布 → 已下线（来自 PRD §3）

## 4. 风险与开放问题

- ⚠️ PRD 未说明权限模型，假设按 actor 区分（运营 / 管理员）[inferred]
- ⚠️ 移动端形态未指定，本次只设计桌面端
```

## 字段约束

| 维度 | 约束 |
|---|---|
| 页面数 | 与 stage 01 一致；新增的辅助页（登录/404）必须标 `[inferred]` |
| 组件数 | 通常 15-40 个；超过 50 个考虑是否过度拆分 |
| 七种状态 | 交互组件必须列全；非交互组件按需 |
| 命名 | 组件 PascalCase；页面 path 形如 `/xxx/:id?` |

## 推断规则

**允许推断**：
- 通用组件（Button/Input/Modal/Toast）即使 PRD 没提也可加
- 通用辅助页（404/500/loading）可加，标 `[inferred]`
- 行业惯例的导航结构（B 端左侧栏，C 端底 tab）

**禁止推断**：
- 业务组件（如 RuleEditor 内部字段）必须从 key_features 推
- 不要新增页面，只能用 stage 01 的 pages（除非通用辅助页）

## 与下游 stage 的契约

| 下游 stage | 消费什么 |
|---|---|
| spec-generation（仅 designer-spec 模式） | component_spec 推 design-spec.md 的颜色 / 字号 / 组件规范 |
| token-extraction（仅 designer-spec/dsl） | component_spec 中的状态清单决定要提取多少 token 变体 |
| code-generation | 全部三份产物，决定生成哪些 file / route / component |
| review-gate | component_spec 用于校验代码是否覆盖了 7 种状态（宪法第 3 条） |

## 参考资料

- 方法论：[reference/m02-design-analysis.md](../reference/m02-design-analysis.md)
- 上游契约：stage 01 outputs
- 代码宪法第 3 条：状态覆盖（参见 [constitution.md](../constitution.md)）

## 输出位置

- 写入 state：`state.information_architecture` / `state.component_spec` / `state.design_analysis_md`
- 持久化：
  - `runs/<run_id>/02-information-architecture.md`
  - `runs/<run_id>/02-component-spec.md`
  - `runs/<run_id>/02-design-analysis.md`
- 紧跟 Checkpoint C1：用户在此处确认 IA / 组件清单合理性
