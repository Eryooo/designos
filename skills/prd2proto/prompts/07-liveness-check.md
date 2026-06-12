# Stage 7: liveness-check（启动验证）

## 目标

代码生成完不等于"用户能看见原型"。这一步把 `prototype_code/` 启动起来，让用户在浏览器里真的打开。

## 输入

- `prototype_code`：Stage 5 产出的项目目录路径
- `code_generation_summary.framework`：react18-vite-ts / vue3-vite-ts
- `code_generation_summary.ui_lib`：antd@5 / element-plus / arco-design

## 输出 JSON

```json
{
  "dev_url": "http://localhost:5173",
  "liveness_report": {
    "install_ok": true,
    "build_ok": true,
    "dev_started": true,
    "port": 5173,
    "errors": []
  }
}
```

## 执行步骤（LLM 引导版）

> ⚠️ TODO：本版 frontend-codegen Mock MCP 没有 `launch_preview` 工具。
> 这里 LLM 引导用户在自己的终端跑命令，回报结果即可。等 frontend-codegen 真 MCP 实装后，本 stage 可改 `type: tool`。

进入这个 stage 后，LLM 必须按以下顺序执行：

### 1. 进度提示（必须先发）

```
⏳ Stage 7: liveness-check — 启动 dev server，确认能看见原型
```

### 2. 探测包管理器

按顺序检查（用 Bash 工具）：
1. `pnpm --version` 存在 → 用 pnpm
2. 否则 `yarn --version` → 用 yarn
3. 否则 `npm --version` → 用 npm（默认）
4. 都没有 → 报错让用户装 Node.js 18+

### 3. 装依赖（后台跑，超时 180 秒）

```
⏳ npm install（预计 30-90 秒，后台跑，不阻塞）
```

完成后报：
```
✅ 依赖安装完成（N 个包）
```

### 4. 跑一次构建（验证 TypeScript / 模块解析）

```bash
cd <prototype_code> && npm run build
```

build 失败 → 把首条 error stack 给用户，问是不是继续修。
build 成功 → 报：
```
✅ build 通过（dist size: X MB）
```

### 5. 启动 dev server（后台）

用 Bash 工具的 `run_in_background: true` 跑：
```bash
cd <prototype_code> && npm run dev
```

然后等 5-10 秒，从输出抓 URL（一般是 `http://localhost:5173`）。

### 6. 报告 URL（最关键）

```
✅ Stage 7: liveness-check → 原型已起在 http://localhost:5173

打开这个地址就能看到原型。建议先看：
1. 首页 / 主入口（路由 /）
2. <PRD 里 P0 任务对应的页面>
3. <PRD 里关键流程的页面>

要 stop dev server，回复 "stop"。
```

## 失败处理

- npm install 失败 → 检查 node 版本（要求 ≥ 18）；检查 registry 是否被墙（建议 `npm config set registry https://registry.npmmirror.com`）
- build 失败 → 把 error 给用户，回 stage 5 修
- dev server 启不起来（端口被占）→ 让 vite 自己换端口（5173 → 5174 → ...）

## 不要做的事

- 不要 `npm install` + `npm run dev` 串成一个长命令（看不到中间进度）
- 不要静默等待，每一步都要发进度
- 不要假装跑通了：如果 build/dev 失败，必须诚实报错，不要伪造 URL
- 不要把 dev server 阻塞前台（必须 `run_in_background: true`）

## 退出条件

- `dev_url` 拿到 + 用户说看到了 → 完成
- 用户说"不用启了" → 跳过本 stage，liveness_report 标 skipped
