# Stage 5: 代码生成

## 输入

- `information_architecture`：Stage 2 产出的站点地图 + 页面树
- `component_spec`：Stage 2 产出的组件清单（含 7 态需求）
- `design_tokens`：Stage 4 产出的 W3C DTCG JSON（pm 模式可能没有）
- `design_spec_md`：Stage 3a 产出或用户提供的设计规范（pm 模式可能没有）
- `component_mapping`：Stage 4.5 产出的组件库映射（仅 designer-dsl）
- `mode`：当前保真度档位

## 输出 JSON

```json
{
  "prototype_code": "<output_root>/prototype/",
  "code_generation_summary": {
    "framework": "react18-vite-ts | vue3-vite-ts",
    "ui_lib": "antd@5 | element-plus | arco-design | none",
    "pages_count": 5,
    "components_count": 12,
    "mock_records_count": 15,
    "auto_decisions": {
      "framework": "react18-vite-ts",
      "ui_lib": "antd@5",
      "state_management": "useSyncExternalStore",
      "reason": "用户授权自行决定"
    }
  }
}
```

## 项目骨架（必须遵守）

```
prototype/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── index.html
├── README.md
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── router.tsx
    ├── styles/
    │   ├── tokens.css          # design_tokens → CSS 变量
    │   └── theme.ts            # 组件库主题桥接（允许 hex，见 constitution 例外）
    ├── components/             # 业务组件（organism 级）
    ├── pages/                  # 每个 page_id 一个文件
    ├── mock/
    │   ├── types.ts            # TypeScript interface
    │   └── data.ts             # 静态 mock 数据
    ├── store/                  # 状态管理（见选型规则）
    └── layouts/
        └── Shell.tsx           # 全局 layout（侧边栏/顶栏/内容区）
```

## 核心决定规则（不允许自由发挥）

### 框架选型
- 用户明确指定 → 用用户的
- 用户说"你看怎么合适" → 选 React 18 + Vite + TypeScript
- design-spec 指定了组件库 → 用对应框架（antd → React，element-plus → Vue）

### 组件库选型
- design-spec 指定 → 用 design-spec 的
- 用户指定 → 用用户的
- 未指定 + React → antd@5
- 未指定 + Vue → element-plus

### 状态管理
- pm 模式 → useState（最简单）
- designer-spec → useSyncExternalStore + 单例 store
- designer-dsl → 看项目已有方案；没有则 zustand

### 路由
- React → react-router-dom v6 createBrowserRouter
- Vue → vue-router v4 createRouter

### 异步状态机模拟
- 所有 async 操作用 setTimeout 模拟（不依赖真后端）
- 状态字段驱动（`status: 'idle' | 'loading' | 'success' | 'error'`）
- 模拟延迟 300-1500ms（随机，让 demo 更真实）

## Mock 数据规模约束

- 列表型数据：每种场景至少 1 条 + PRD 中 P0 功能点全覆盖
- 状态机覆盖：所有声明的状态至少各 1 条（done/running/error/pending 等）
- 来源/分类：每种 enum 至少 1 条
- 特殊流程：PRD 中标注的高风险/特殊分支至少 1 条 mock 数据触发
- 总量控制：单类型 5-15 条（够演示，不过度）

## npm scripts（必须包含）

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

## 代码质量底线

- TypeScript strict mode（tsconfig `"strict": true`）
- 0 个 `any` 类型（用 unknown + type guard）
- 所有组件 export default + 命名导出
- 每个 page 组件在 router.tsx 注册
- Shell.tsx 包含完整导航（所有 page 可点击跳转）
- 所有导航 link 指向真实路由（禁止 `href="#"`）

## 进度要求

每完成一组文件后立刻报告：
```
✅ 骨架文件（package.json / vite.config / tsconfig / index.html）
✅ tokens.css + theme.ts
✅ mock/types.ts + mock/data.ts
✅ Shell.tsx + router.tsx
✅ pages/[PageName].tsx × N
✅ components/[ComponentName].tsx × N
```

## 不要做的事

- 不要写测试文件（pm/designer-spec 模式不需要）
- 不要加 ESLint / Prettier 配置（用户项目自带）
- 不要加 CI/CD 配置
- 不要加 .env 文件
- 不要分多次询问用户"要不要加 X"——直接按规则做
