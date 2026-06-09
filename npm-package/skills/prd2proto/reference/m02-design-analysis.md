# Reference: 设计分析（m02 checklist）

> Stage 02 `design-analysis` 的约束清单。教学材料见 `textbook/atomic-design.md`。

## 输出 schema 强约束

```json
{
  "information_architecture": "<markdown>",
  "component_spec": "<markdown>",
  "design_analysis_md": "<markdown>",
  "summary": {
    "atomic_breakdown": {"atoms": 12, "molecules": 8, "organisms": 4}
  }
}
```

## 信息架构 4 视图（缺一不可）

- [ ] **Sitemap**：树状或 mermaid，顶层节点是模块入口，URL 层级反映嵌套
- [ ] **Navigation**：选 1-2 种主要类型（顶部 / 侧边 / 底部 tab / 面包屑 / 步骤），列出每种触达哪些 page
- [ ] **Route Table**：markdown 表格，含 `path / 名称 / 类型 / 模块 / 需登录 / 备注`，下游 code-generation 直接消费
- [ ] **Critical Path**：仅 stage 01 标 `is_critical_path: true` 的 user_flows，每条画出页面跳转链 + 涉及 organism

## 组件分层规则（Atomic Design）

| 层级 | 命名约定 | 判断要点 |
|---|---|---|
| atoms | PascalCase 单一名词 | 无内部状态、不可拆 |
| molecules | 功能名 | 组合多个 atom |
| organisms | 业务名 | 业务语义 |
| templates | XxxLayout | 页面骨架，定义 organism 排布 |
| pages | XxxPage | 套数据的具体页面实例 |

**严格自下而上引用**：atoms ← molecules ← organisms ← templates ← pages。**禁止跨层反向引用**。

## 7 种状态强约束

每个交互组件的状态清单必须列全 7 种或显式标 ❌ + 理由：

```
default | hover | active | focus | disabled | loading | error
```

| 组件类型 | 必须全 7 种 |
|---|---|
| Button / Input / Select / Checkbox / Radio / Switch / Link / Tab | ✅ 必须 |
| 可点击 Card | ✅ 必须 |
| DatePicker / Slider 复合 | ✅ 全 7 种 + 子状态 |
| Table | 行级 hover/selected，不需要全 7 种 |
| Heading / Divider / Badge / Tag / Avatar | ❌ 不需要交互状态 |
| Modal / Toast | 需要 entering/leaving 动画态，不算 7 种交互态 |

## 组件复用维度

每个组件必须标一个：

- `cross-page`：≥3 个页面用 → 应入组件库或 atoms 层
- `cross-module-page`：同 module 多页面用 → molecules 层
- `page-only`：只 1 个页面用 → organisms 层，命名带页面前缀

## 输出格式约束（必须可机器解析）

下游 spec-generation 用正则抽组件名：

- [ ] 组件标题用 `### ComponentName (atomic_layer)` 格式
- [ ] 状态清单用 markdown checkbox：`- [x] hover` 或 `- [ ] error`
- [ ] 路由表用 markdown 表格
- [ ] `summary.atomic_breakdown` 必填三个数字

**数量校验**：organism > 10 → 过度拆分 warning；organism < 2 → 粒度过大 warning。

## 常见陷阱（不要踩）

| 陷阱 | 错误 | 正确 |
|---|---|---|
| 把样式当组件 | 建 `RedButton` | Button + variant="danger" |
| 粒度过大 | 一个 `RulePage` organism 含整页所有逻辑 | 拆成 `RuleListHeader` / `RuleTable` / `RuleEditor` |
| 粒度过小 | 把 `<span class="bold">` 建成 `BoldText` | 用文本样式 token |
| 跨层引用 | atoms import organisms | 严格自下而上 |
| 状态遗漏 | Button 只列 default + hover | 列全 7 种或显式标 ❌ + 理由 |

## 与下游 stage 的契约

| 产物 | 谁消费 | 怎么用 |
|---|---|---|
| `information_architecture.路由表` | code-generation | 直接生成 router config |
| `information_architecture.站点地图` | spec-generation / 用户 C1 | 看导航整体合理性 |
| `component_spec.层级` | code-generation | 决定文件目录结构 |
| `component_spec.状态清单` | review-gate | 校验代码覆盖声明状态 |
| `component_spec.复用维度` | code-generation | 决定 shared/ 还是 pages/X/ |
| `design_analysis_md` | spec-generation | 推 design-spec 设计原则 |

教学材料：`textbook/atomic-design.md`（5 层定义 + 信息架构常见模式 + 状态视觉变化详解）。
