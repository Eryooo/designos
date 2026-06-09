# Textbook: 4 条代码宪法的设计动机

> review-gate reference 只列检查清单，本文给愿意深读的读者讲为什么定这 4 条。

## 规则 1：不得硬编码颜色 / 字号 / 间距

**为什么**：硬编码会让团队改色板时遍历几百个文件，且无法统一暗色模式 / 多品牌主题。

行业最佳实践见 W3C Design Tokens Community Group 规范。

## 规则 2：不得自行编写基础组件

**为什么**：基础组件（Button、Input、Modal）业界已有成熟实现（无障碍、键盘导航、状态机等都很复杂），自己写不会比 Ant Design 好。

业务组件（RuleEditor、ApprovalFlow）则鼓励自写——这部分是产品差异化所在。

## 规则 3：不得跳过状态覆盖

**为什么**：用户反馈缺失 hover/focus 是 B 端产品最常见的"显得不专业"问题；缺失 loading/error 是数据系统最常见的体验崩塌点。

WCAG 2.1 明确要求 focus visibility，是 a11y 核心。

## 规则 4：不得忽略 Design.md 约束

**为什么**：设计师团队 design-spec.md 是"团队约定"，优先级最高；代码默认值不能覆盖 spec。

这条是 Google Labs design.md 工作流的核心原则。

## fidelity_score 评分规则

```
base = 100
critical: -20 each
major:    -8 each
minor:    -3 each

最低 = 0；最高 = 100
```

**模式期望分**：

- pm 模式：≥ 60（放宽，演示用）
- designer-spec 模式：≥ 80
- designer-dsl 模式：≥ 95（生产代码）

## 修复模板

### 模板 1：硬编码颜色

```diff
- background-color: #3B82F6;
+ background-color: var(--color-primary);
```

`auto_fixable: true`（机械替换）。

### 模板 2：自写基础 Button

```diff
- <button class="my-btn">Click</button>
+ <a-button type="primary">Click</a-button>
```

`auto_fixable: false`（需要人判断 type）。

### 模板 3：缺状态覆盖

```diff
.btn { background: var(--color-primary); }
+ .btn:hover { background: var(--color-primary-hover); }
+ .btn:focus-visible { outline: 2px solid var(--color-primary); }
+ .btn:disabled { opacity: 0.5; cursor: not-allowed; }
```

`auto_fixable: false`（CSS 值需要人决定）。

### 模板 4：design-spec 偏差

```diff
- .btn { border-radius: 8px; }
+ .btn { border-radius: var(--radius-md); /* 4px per spec */ }
```

`auto_fixable: true`（直接替换）。

## 参考资料（外部）

- ADR-003 §7.2「生产级代码最佳实践」
- W3C WCAG 2.1（focus visibility 是 a11y 必需）
- Ant Design Token System（token 命名参考）
- Brad Frost, *Atomic Design*（基础组件 vs 业务组件分层）
