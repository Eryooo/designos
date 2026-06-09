# Textbook: Atomic Design 完整教程

> Brad Frost 的 Atomic Design 方法论展开。stage 02 reference 中只列规则，本文给愿意深读的读者。

## 5 层组件分类

| 层级 | 定义 | 例子 | 命名约定 |
|---|---|---|---|
| **Atoms（原子）** | 最小且不可拆的 UI 单位 | Button, Input, Icon, Label, Tag, Avatar | 单一名词，PascalCase |
| **Molecules（分子）** | 由 atoms 组成的功能小组件 | SearchBar (Input+Button), FormField (Label+Input+ErrorText) | 功能名 |
| **Organisms（有机体）** | 复杂业务组件，承载完整功能片段 | RuleEditor, NavBar, DataTable | 业务名 |
| **Templates（模板）** | 页面骨架，定义 organism 排布 | DashboardLayout, AuthLayout | XxxLayout |
| **Pages（页面）** | 套上数据的具体页面实例 | RuleListPage, RuleEditPage | XxxPage |

## 实操判断要点

- 不知道是 atom 还是 molecule？看是否有内部状态/组合：纯无状态展示 → atom；组合多个 atom → molecule
- 业务名 vs 通用名：通用（如 Button）= atom；带业务语义（如 RuleEditor）= organism

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

## 7 种交互状态详解

| # | 状态 | 何时触发 | 视觉变化提示 |
|---|---|---|---|
| 1 | default | 默认呈现 | 基础色 |
| 2 | hover | 鼠标悬停 | 颜色加深 / 边框变化 |
| 3 | active | 鼠标按下中 | 内陷 / 颜色更深 |
| 4 | focus | 键盘聚焦或点击 | 描边 / 发光 |
| 5 | disabled | 不可交互 | 透明度低 / cursor: not-allowed |
| 6 | loading | 异步处理中 | spinner / 禁用其他 |
| 7 | error | 输入或操作出错 | 红色边框 / 错误提示 |

## 参考资料（外部）

- Brad Frost, *Atomic Design*（pattern 起源）
- Peter Morville, Louis Rosenfeld, *Information Architecture for the Web and Beyond*
- Don Norman, *The Design of Everyday Things*（状态可见性原则）
