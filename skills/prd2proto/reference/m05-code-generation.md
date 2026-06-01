# Reference: 代码生成（m05 checklist）

> Stage 05 `code-generation` 约束清单。代码宪法详见 `../constitution.md`，动机见 `textbook/code-constitution-rationale.md`。

## 项目骨架（必须存在）

```
prototype/
├── package.json (含 dev/build/preview scripts)
├── tsconfig.json (strict: true)
├── vite.config.ts / index.html / README.md
└── src/
    ├── main.tsx / App.tsx / router.tsx
    ├── styles/ (tokens.css + theme.ts)
    ├── components/ (业务组件 organism 级)
    ├── pages/ (每个 page_id 一个文件)
    ├── mock/ (types.ts + data.ts)
    ├── store/ (状态管理)
    └── layouts/Shell.tsx (全局 layout)
```

- [ ] 每个 stage 02 `page_id` 在 `pages/` 下有对应文件
- [ ] Shell.tsx 含完整导航（所有 page 可点击跳转）
- [ ] router.tsx 注册所有 page
- [ ] 禁止 `href="#"` 占位

## 4 条宪法在 stage 05 的落地

- [ ] **#1 无硬编码**：CSS/inline 引用 `var(--color-*)` 或 utility class；`theme.ts` 是唯一允许 hex 的文件，每值与 design-spec 一致；白名单 `0/100%/auto/transparent/currentColor` + 边框 `1px 2px` + 测试文件；pm 可放宽
- [ ] **#2 不自写基础组件**：Button/Input/Select/Checkbox/Radio/Switch/Modal/Drawer/Toast/Tooltip/DatePicker/Table/Pagination/Tabs/Menu/Tag/Badge 必须组件库导入；业务组件（RuleEditor 等）允许自写
- [ ] **#3 状态覆盖**：Button 必有 default/hover/active/focus/disabled/loading；Input 系列必有 default/hover/focus/disabled/error；Link/Tab 必有 default/hover/active/focus/disabled。pm 至少 hover+focus+disabled；designer-spec 必须 5 种；designer-dsl 全 7 种
- [ ] **#4 design-spec 优先**：spec 指定 > 组件库默认主题色 / 间距 / 圆角 / 选型

## 决定规则（不允许自由发挥）

### 框架选型
| 输入 | 决定 |
|---|---|
| 用户指定 | 用用户的 |
| "你看怎么合适" | React 18 + Vite + TypeScript |
| design-spec 指定组件库 | antd → React，element-plus → Vue |

### 组件库选型
| 输入 | 决定 |
|---|---|
| design-spec 指定 | 用 design-spec 的 |
| 用户指定 | 用用户的 |
| 未指定 + React | antd@5 |
| 未指定 + Vue | element-plus |

### 状态管理决策树
```
mode == pm              → useState
mode == designer-spec   → useSyncExternalStore + 单例
mode == designer-dsl    → 项目已有方案；没有则 zustand
```

### 路由
- React → react-router-dom v6 `createBrowserRouter`
- Vue → vue-router v4 `createRouter`

### 异步状态机模拟
- [ ] 所有 async 用 `setTimeout`
- [ ] 状态字段：`status: 'idle'|'loading'|'success'|'error'`
- [ ] 延迟随机 300-1500ms

## Mock 数据规模检查清单

- [ ] 列表：每场景 ≥1 + PRD P0 全覆盖
- [ ] 状态：所有声明状态各 ≥1 条
- [ ] enum：每值 ≥1 条
- [ ] 高风险/特殊分支：PRD 标注的 ≥1 条
- [ ] 单类型 5-15 条

## npm scripts 三件套（必须有）

```json
{"dev":"vite","build":"vite build","preview":"vite preview"}
```

## 代码质量底线

- [ ] TypeScript `strict: true`
- [ ] 0 个 `any`（用 `unknown` + type guard）
- [ ] 所有组件 export default + 命名导出
- [ ] 每个 page 在 router.tsx 注册
- [ ] 所有 link 指向真实路由

## 不要做的事

不写测试 / ESLint / Prettier / CI/CD / .env；不分多次询问用户"要不要加 X"。

教学材料：`textbook/code-constitution-rationale.md`。
