# Reference: 设计分析（m02）

> Stage 02 `design-analysis` 的方法论库。pipeline 在执行 stage 时 lazy-load 到 LLM 上下文。

## 方法论：Atomic Design + Information Architecture

### 1. Atomic Design（Brad Frost）

stage 02 的 `component_spec` 必须按 5 层组织。每层定义、何时用、命名约定如下：

| 层级 | 定义 | 例子 | 命名约定 |
|---|---|---|---|
| **Atoms（原子）** | 最小且不可拆的 UI 单位 | Button, Input, Icon, Label, Tag, Avatar | 单一名词，PascalCase |
| **Molecules（分子）** | 由 atoms 组成的功能小组件 | SearchBar (Input+Button), FormField (Label+Input+ErrorText) | 功能名 |
| **Organisms（有机体）** | 复杂业务组件，承载完整功能片段 | RuleEditor, NavBar, DataTable | 业务名 |
| **Templates（模板）** | 页面骨架，定义 organism 排布 | DashboardLayout, AuthLayout | XxxLayout |
| **Pages（页面）** | 套上数据的具体页面实例 | RuleListPage, RuleEditPage | XxxPage |

**实操判断**：

- 不知道是 atom 还是 molecule？看是否有内部状态/组合：纯无状态展示 → atom；组合多个 atom → molecule
- 业务名 vs 通用名：通用（如 Button）= atom；带业务语义（如 RuleEditor）= organism

### 2. 信息架构 4 视图

`information_architecture` 必须覆盖 4 个视图（缺一不可）：

#### 2.1 站点地图（Sitemap）

树状或 mermaid 图，展示页面层级。要点：
- 顶层节点是模块入口
- 嵌套关系反映 URL 层级
- 隐藏页（404 / 登录 / 错误）单列一组

#### 2.2 全局导航（Navigation）

| 类型 | 适用场景 | 例子 |
|---|---|---|
| 顶部导航 | 模块少（≤5）、扁平 | 消费级 App |
| 侧边导航 | 模块多（>5）、深层 | B 端管理后台 |
| 底部 tab | 移动端 | 微信底栏 |
| 面包屑 | 深层级页面 | 后台编辑页 |
| 步骤导航 | 引导流程 | 注册向导 |

不要堆砌；选 1-2 种主要的，列出每种触达哪些 page。

#### 2.3 路由表（Route Table）

机器可读，下游 code-generation 直接拿去生成 router config：

| path | 名称 | 类型 | 模块 | 需登录 | 备注 |
|---|---|---|---|---|---|
| /rules | 规则列表 | list | M-001 | yes | |

#### 2.4 关键路径（Critical Path）

只列 stage 01 标过 `is_critical_path: true` 的 user_flows，每条画出页面跳转链 + 涉及的关键 organism。

### 3. 七种状态覆盖（强约束，对应代码宪法 #3）

**所有交互组件必须列全**：

| # | 状态 | 何时触发 | 视觉变化提示 |
|---|---|---|---|
| 1 | default | 默认呈现 | 基础色 |
| 2 | hover | 鼠标悬停 | 颜色加深 / 边框变化 |
| 3 | active | 鼠标按下中 | 内陷 / 颜色更深 |
| 4 | focus | 键盘聚焦或点击 | 描边 / 发光 |
| 5 | disabled | 不可交互 | 透明度低 / cursor: not-allowed |
| 6 | loading | 异步处理中 | spinner / 禁用其他 |
| 7 | error | 输入或操作出错 | 红色边框 / 错误提示 |

**判断哪些组件需要全 7 种**：

- ✅ Button、Input、Select、Checkbox、Radio、Switch、Link、Tab、可点击 Card → 全 7 种
- ⚠️ DatePicker、Slider 等复合 → 全 7 种 + 子状态
- ⚠️ Table → 行级 hover/selected，不需要全 7 种
- ❌ Heading、Divider、Badge、Tag、Avatar → 不需要交互状态
- ⚠️ Modal、Toast → 需要 entering/leaving 动画态，不是 7 种交互态

### 4. 组件复用矩阵

每个组件给一个**复用维度**：

```markdown
- 通用（cross-page）：在 ≥3 个页面用 → 应该提到组件库或 atoms 层
- 模块通用（cross-module-page）：在同一 module 多个页面用 → molecules 层
- 页面专属（page-only）：只在 1 个页面用 → organisms 层，命名带页面前缀
```

## 信息架构常见模式（B 端管理后台）

### Pattern 1：列表 → 编辑 → 详情

```
/rules (list)
  ├── /rules/new (form, mode=create)
  ├── /rules/edit/:id (form, mode=edit)
  └── /rules/:id (detail, readonly)
```

组件：`DataTable`, `Toolbar`, `FilterPanel`, `Pagination`, `RuleForm`, `RuleDetailHeader`。

### Pattern 2：仪表盘 → 钻取

```
/dashboard
  └── /dashboard/metric/:id
```

组件：`MetricCard`, `Chart`, `KPIGrid`, `DateRangePicker`。

### Pattern 3：步骤向导（wizard）

```
/setup/step-1
/setup/step-2
/setup/step-3
```

组件：`StepIndicator`, `WizardLayout`, `StepFooter`。

## 常见陷阱

### 陷阱 1：把样式当组件

❌ 把"红色按钮"建成 `RedButton`。
✅ Button + variant="danger"。颜色是 prop，不是组件。

### 陷阱 2：组件粒度过大

❌ 一个 `RulePage` organism 包含整页所有逻辑。
✅ 拆成 `RuleListHeader` / `RuleTable` / `RuleEditor` / `RuleApprovalPanel`。

### 陷阱 3：组件粒度过小

❌ 把 `<span class="bold">` 也建成组件 `BoldText`。
✅ 用文本样式 token 解决，不要建组件。

### 陷阱 4：跨层引用

❌ atoms 层组件 import organisms 层。
✅ 严格自下而上：atoms ← molecules ← organisms ← templates ← pages。

### 陷阱 5：状态遗漏

❌ Button 只列 default + hover。
✅ 必须列全 7 种（除非组件本身不适用某种）。不适用的也要明示 ❌ 状态名 + 理由。

## 与下游 stage 的契约

| 产物 | 谁消费 | 怎么用 |
|---|---|---|
| `information_architecture.路由表` | code-generation | 直接生成 router 配置 |
| `information_architecture.站点地图` | spec-generation / 用户 C1 | 看导航整体合理性 |
| `component_spec.层级` | code-generation | 决定文件目录结构（atoms/ molecules/ ...） |
| `component_spec.状态清单` | review-gate | 校验代码是否覆盖了声明的状态 |
| `component_spec.复用维度` | code-generation | 决定组件放在 shared/ 还是 pages/RuleEditor/ |
| `design_analysis_md` | spec-generation | 推 design-spec.md 的设计原则 |

## 输出格式约束

### markdown 必须可机器解析

下游 spec-generation 会用正则抽组件名。所以：

- 组件标题用 `### ComponentName (atomic_layer)` 格式
- 状态清单用 markdown checkbox：`- [x] hover` 或 `- [ ] error`
- 路由表用 markdown 表格

### JSON `summary` 字段必填

`summary.atomic_breakdown` 在 C1 checkpoint 会被高亮给用户审：

```json
{
  "atoms": 12,
  "molecules": 8,
  "organisms": 4
}
```

如果 organism 数 > 10，可能是过度拆分；< 2 可能是粒度过大。

## 参考资料（外部）

- Brad Frost, *Atomic Design*（pattern 起源）
- Peter Morville, Louis Rosenfeld, *Information Architecture for the Web and Beyond*
- Material Design / Ant Design 的组件分层规范（实操参考）
- Don Norman, *The Design of Everyday Things*（状态可见性原则）
