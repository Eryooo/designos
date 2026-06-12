# UXEval 输入指南

> 跑 `/uxeval` 之前请准备这些输入。
> Kernel 在 preflight 阶段会校验，缺失会直接报错并提示。

---

## 必备输入

### 1. PRD 文档（必需）

放在 `inputs/prd.pdf`（或 `prd.docx` / `prd.md`）。

要求：
- 至少 5000 字（< 5000 字会触发 warning，可强制继续）
- 含「功能模块」「用户角色」「业务目标」三类内容（缺一项 warning）
- 不含真实账号 / 客户名 / 内部 URL（违反宪法 #2）

### 2. 评估范围 scope.md（必需）

放在 `inputs/scope.md`，模板见 `templates/scope.md`，包含：
- 评估目标（一句话）
- 重点关注的角色
- 重点关注的模块
- 不评估的部分（明确划分边界，避免跑偏）
- 业务背景

---

## 可选输入

### 3. 自定义启发式原则（可选）

放在 `inputs/principles.md`。
不提供则使用 Nielsen 10 原则 + 内置补充原则（数据可信性、视觉层级、错误恢复）。

### 4. 截图目录（仅 client 模式必需）

放在 `inputs/screens/`，约定：
- 推荐命名：`{模块}-{页面}-{状态}.png`，例如 `工作台-首页-默认.png`
- 单张图 < 5MB，批量总大小 < 200MB
- 关键流程必须有「初始 → 中间 → 结果」三连截图

如果截图很多，不想批量改文件名，优先补下面这些低摩擦输入：
- `inputs/screens/screens-description.md`
  - 用几段文字说明关键页面名称、关键按钮、关键状态
- `inputs/screens/screens-map.md` 或 `inputs/screens/screens-index.md`
  - 当系统自动起草的 mapping 仍有少数歧义项时，再用最少量映射说明“截图文件 -> 页面 / 状态”
  - 例如：

```md
- IMG_1024.png -> 工作台首页 / 加载态
- IMG_1025.png -> 工作台首页 / 空状态
- final-01.png -> 设置页 / 保存成功
```

系统会优先自动起草 screenshot -> page/state 映射；只有在 OCR、markdown 说明和自动起草仍不足以稳定匹配时，才建议你补最少量 mapping 或小范围补命名，不需要先大规模重命名整个截图集。

### 5. 历史问题清单（可选）

放在 `inputs/historical-issues.md`，用于让 Agent 避免重复指出已知问题。

---

## Web 模式额外要求

`.env.local` 必须包含：

```bash
APP_BASE_URL=https://app.example.com
APP_USERNAME=test_user@example.com
APP_PASSWORD=********
APP_LOGIN_TYPE=form        # form | sso | oauth
# 可选
APP_AUTH_STATE_PATH=auth_state.json   # 已有的登录态可复用
```

外部依赖检查：

```bash
playwright --version       # 必须 >= 1.40
which chromium             # playwright install chromium
```

如果 preflight 检测到 Playwright 未安装，会给出安装提示后退出。

---

## 输入校验

```bash
designos input check uxeval
```

会跑 7 项检查：
1. PRD 存在且可解析
2. scope.md 存在且至少含 3 段
3. (web 模式) URL 可达 / 登录态有效
4. (client 模式) 截图目录非空
5. 不含敏感信息（敏感词扫描）
6. principles.md 格式合法（如果有）
7. 磁盘空间足够（产物预估 50MB）

---

## 工作区结构

```
my-uxeval-project/
├── designos.project.yaml
├── .env.local
├── inputs/
│   ├── prd.pdf
│   ├── scope.md
│   ├── principles.md          # 可选
│   ├── historical-issues.md   # 可选
│   └── screens/                # 仅 client 模式
│       ├── 工作台-首页-默认.png
│       └── ...
└── runs/
    └── 001-uxeval/             # 跑完后产生
        ├── run.yaml
        ├── 01-旅程地图.md
        ├── 02-任务清单-完整版.md
        ├── 03-任务清单-简洁版.md
        ├── 04-问题报告.xlsx
        ├── 04-问题报告.html
        └── evidence/
            └── *.png
```
