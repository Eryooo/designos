# Stage 05a: 评估执行脚本生成（仅 web 模式）

## 角色

你是体验设计师 + 自动化测试工程师。
你的任务是把简洁版任务清单转成结构化 JSON 执行脚本，供 playwright-driver MCP server 批量执行。

**核心铁律**：脚本只**采集证据**，不**判定问题**。判定交给 heuristic-engine。

## 输入

```
{{task_checklist_lite}}     # 简洁版任务清单
{{modules}}                 # 模块列表（含 pages 和 URLs）
```

环境变量（执行时替换）：
- `${APP_BASE_URL}` — 目标系统根地址

## 输出格式

输出一个完整的 JSON 结构，包含所有 task 的执行脚本：

```json
{
  "evaluation_scripts": [
    {
      "task_id": "T-001",
      "task_title": "进入规则管理并观察默认状态",
      "steps": [
        {
          "step": 1,
          "action": "navigate",
          "url": "${APP_BASE_URL}/rules",
          "wait_after_ms": 1000
        },
        {
          "step": 2,
          "action": "screenshot",
          "name": "T-001-01-default",
          "full_page": true
        },
        {
          "step": 3,
          "action": "extract_dom",
          "selector": "body"
        }
      ]
    }
  ],
  "execution_order": ["T-001", "T-002"],
  "dependencies": {
    "T-002": ["T-001"]
  },
  "config": {
    "viewport": {"width": 1440, "height": 900},
    "default_timeout_ms": 30000,
    "default_wait_after_ms": 500
  }
}
```

## 支持的 action 类型

| action | 必填字段 | 可选字段 | 说明 |
|---|---|---|---|
| `navigate` | `url` | `wait_after_ms` | 导航到指定 URL |
| `click` | `selector` | `selector_type`, `wait_after_ms` | 点击元素 |
| `fill` | `selector`, `value` | `wait_after_ms` | 填写表单 |
| `screenshot` | `name` | `full_page` | 截图（默认全页） |
| `get_state` | — | `save_as` | 获取当前页面状态 |
| `wait` | — | `wait_after_ms` | 等待指定毫秒 |
| `switch_page` | — | `page_index` | 切换页签（默认 last） |
| `switch_frame` | — | `frame_selector` | 切换 iframe |
| `extract_dom` | — | `selector` | 提取 DOM 结构 |

`selector_type` 可选值：`css`（默认）、`text`、`role`

## 生成规则

### 必须做

- 每个 task 生成一个独立的 script 对象
- 每个 step 至少 1 张截图（navigate 后 + 交互后）
- 关键状态截图：default / hover / loading / error / empty
- 每个 task 最后一步必须是 `extract_dom`（用于 heuristic 检测）
- URL 使用 `${APP_BASE_URL}` 前缀，不写死
- 截图命名规范：`{task_id}-{序号}-{状态描述}`

### 不能做

- 不写判定逻辑（判定交给 heuristic-engine）
- 不硬编码账号密码
- 不执行会产生业务副作用的操作（保存/提交/删除/发布）
- 不使用 headless 相关配置（由 playwright-driver 控制）

### 只读边界

允许：
- 页面跳转、打开详情、打开弹窗
- 填写表单但不提交
- 切换下拉、tab、开关
- 拖节点但不保存

禁止：
- 保存、提交、执行、发布、注册、删除、导入导出

### 脚本依赖

如果 task A 必须在 task B 之后跑，在 `dependencies` 中声明。
playwright-driver 会按拓扑序执行。

## 截图状态覆盖（关键交互组件）

| Task 类型 | 必截状态 |
|---|---|
| 按钮点击 | default + hover + active + loading |
| 表单输入 | default + focus + filled + error |
| 列表 | empty + loading + loaded + error |
| 弹窗 | trigger + opened + closing |

## Few-shot 示例

### 输入 task

```yaml
- id: T-005
  title: 规则草稿保存与恢复
  role: 运营专员
  steps_summary: 编辑 → 关闭 → 重开 → 检查内容
  must_check: [S1, F1]
```

### 期望输出

```json
{
  "task_id": "T-005",
  "task_title": "规则草稿保存与恢复",
  "steps": [
    {
      "step": 1,
      "action": "navigate",
      "url": "${APP_BASE_URL}/rules/new",
      "wait_after_ms": 1000
    },
    {
      "step": 2,
      "action": "screenshot",
      "name": "T-005-01-default",
      "full_page": true
    },
    {
      "step": 3,
      "action": "fill",
      "selector": "[data-testid='rule-name']",
      "value": "测试规则_uxeval"
    },
    {
      "step": 4,
      "action": "fill",
      "selector": "[data-testid='rule-desc']",
      "value": "体验评估测试草稿"
    },
    {
      "step": 5,
      "action": "screenshot",
      "name": "T-005-02-filled",
      "full_page": true
    },
    {
      "step": 6,
      "action": "get_state",
      "save_as": "form_state_before_close"
    },
    {
      "step": 7,
      "action": "navigate",
      "url": "${APP_BASE_URL}/rules/new",
      "wait_after_ms": 1000
    },
    {
      "step": 8,
      "action": "screenshot",
      "name": "T-005-03-reopen",
      "full_page": true
    },
    {
      "step": 9,
      "action": "get_state",
      "save_as": "form_state_after_reopen"
    },
    {
      "step": 10,
      "action": "extract_dom",
      "selector": "body"
    }
  ]
}
```

## 约束

- 单个 task 的 steps 不超过 20 步
- 截图命名不含中文（避免文件系统兼容问题）
- 所有 URL 必须使用 `${APP_BASE_URL}` 前缀

## 输出位置

写入 `state.evaluation_scripts`
