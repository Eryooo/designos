# Skill 封装方案

## 1. 推荐封装目标

推荐 Claude Code 最终实现的是：

### 核心 skill

`web-heuristic-eval-readonly`

它解决的是一个通用问题：

> 基于 PRD、截图和真实 Web 环境，以只读方式完成启发式评估，并输出任务清单、执行脚本、问题底稿和业务汇总。

### 项目资源包

当前 `data-design-review` 仓库本身保留为项目资源包，负责提供：

- PRD
- 截图
- 输出模板
- 问题字段规范
- 当前项目的任务清单实例

---

## 2. 为什么不建议做成单技能大一统

单技能大一统会把这些完全不同的东西耦合在一起：

- 通用启发式流程
- 当前业务的页面/空间
- Playwright 运行时实现
- PDF/Excel/PDF 导出细节
- 手动登录协作

后果是：

- 触发条件失真
- `SKILL.md` 过大
- Claude Code 改一点就影响全链路
- 很难迁移到别的项目

所以建议分成：

1. `SKILL.md`  
   只保留触发条件、主流程、边界、何时读哪些 references

2. `references/`
   - 评估原则
   - 执行阶段说明
   - 运行时异常策略
   - 输出结构规范

3. `scripts/`
   - 浏览器桥接
   - 状态写入
   - Markdown/PDF 导出
   - 结果归并

4. `assets/`
   - 问题模板
   - 示例输出

---

## 3. 推荐目录结构

```text
web-heuristic-eval-readonly/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── workflow.md
│   ├── runtime-boundaries.md
│   ├── evidence-model.md
│   ├── issue-schema.md
│   ├── report-structure.md
│   └── failure-handling.md
├── scripts/
│   ├── playwright_bridge.mjs
│   ├── merge_issue_docs.mjs
│   ├── render_markdown_pdf.py
│   └── state_manager.mjs
└── assets/
    ├── issue-template.md
    ├── summary-template.md
    └── workspace-config.example.yaml
```

---

## 4. 建议的状态机

skill 不要只靠“当前对话上下文”推进，应该落一个轻量状态机。

### 4.1 运行状态

```text
INIT
  -> INPUT_CONFIRMED
  -> STATIC_ANALYSIS_DONE
  -> EXECUTION_SCRIPT_READY
  -> RUNTIME_WAITING_LOGIN
  -> RUNTIME_ACTIVE
  -> SPACE_EVIDENCE_RECORDED
  -> SUMMARY_READY
  -> PDF_READY
```

### 4.2 异常状态

```text
BLOCKED_BY_LOGIN
BLOCKED_BY_ROUTE_MISMATCH
BLOCKED_BY_FRAME_TOPOLOGY
BLOCKED_BY_PAGE_BLANK
BLOCKED_BY_MISSING_EVIDENCE
```

### 4.3 状态文件建议

建议每次运行落一个：

`runs/current_run_state.json`

示例字段：

```json
{
  "project_name": "data-mining-v394",
  "mode": "web-readonly",
  "inputs": {
    "prd": "00_input/数据挖掘V3.9.4.pdf",
    "screens_dir": "00_input/界面截图"
  },
  "constraints": {
    "readonly": true,
    "allow_fill_without_submit": true,
    "allow_drag_without_save": true
  },
  "spaces": [
    {
      "id": "spaceA",
      "name": "数据挖掘V394BVT空间",
      "status": "completed"
    },
    {
      "id": "spaceB",
      "name": "ylgui2自动化51302",
      "status": "completed"
    },
    {
      "id": "spaceC",
      "name": "数据挖掘V393自测空间1",
      "status": "blocked_by_route_mismatch"
    }
  ],
  "artifacts": {
    "task_checklist": "outputs/数据挖掘V3.9.4_启发式评估任务清单_体验导向版.md",
    "execution_script": "outputs/数据挖掘V3.9.4_启发式评估执行脚本_真实环境版.md",
    "final_summary": "outputs/数据挖掘V3.9.4_启发式评估问题汇总_全量版.md"
  }
}
```

---

## 5. skill 应该如何拆阶段

### Phase 1：输入与边界确认

必须确认：

- PRD 路径
- 截图目录
- 是否 Web 模式
- 是否只读
- 是否允许填表不提交
- 是否允许拖节点不保存

### Phase 2：静态评估

产出：

- 任务清单
- PRD-截图冲突清单
- 第一轮问题底稿

### Phase 3：执行脚本化

产出：

- 真实环境执行脚本
- 多空间执行顺序
- 证据命名规范

### Phase 4：运行时执行

产出：

- 空间级问题清单
- 执行记录
- 截图资产

### Phase 5：汇总交付

产出：

- 全量问题汇总
- PDF

---

## 6. 推荐保留的硬规则

### 6.1 安全边界

skill 必须把这些做成硬规则，而不是建议：

- 禁止提交
- 禁止保存
- 禁止执行训练
- 禁止发布
- 禁止注册
- 禁止删除
- 禁止导入导出
- 禁止上传并确认

### 6.2 协作边界

- 登录必须由用户手动完成
- 账号密码不得进入聊天
- skill 只能接管已登录会话

### 6.3 证据边界

- 没有证据，不得输出确定性问题
- 页面没进入，不得伪装为“无问题”
- 环境异常必须输出为阻塞记录或异常问题

---

## 7. Claude Code 实现时建议复用的现成资产

### 7.1 可以直接复用

- [scripts/playwright_bridge.mjs](/Users/young/Documents/Codex/data-design-review/scripts/playwright_bridge.mjs)
- [scripts/render_markdown_pdf_reportlab.py](/Users/young/Documents/Codex/data-design-review/scripts/render_markdown_pdf_reportlab.py)
- [templates/问题清单字段规范.md](/Users/young/Documents/Codex/data-design-review/templates/问题清单字段规范.md)
- [docs/浏览器自动化启发式评估技术方案.md](/Users/young/Documents/Codex/data-design-review/docs/浏览器自动化启发式评估技术方案.md)

### 7.2 只适合参考，不要直接当 skill 逻辑

- 当前项目的空间名
- 当前项目的 URL
- 当前项目的截图命名
- 当前项目的业务术语

---

## 8. 关键优化建议

### 8.1 把“任务清单”和“执行脚本”分成两个命令

建议 skill 支持两个明确动作：

1. `plan`
   - 读 PRD + 截图
   - 产出任务清单和冲突清单

2. `run`
   - 基于执行脚本跑真实环境
   - 产出空间级问题底稿

这样不会把一次执行里所有职责搅在一起。

### 8.2 把“桥接调试”独立出来

建议再有一个低层命令：

3. `bridge-debug`
   - 查 page/frame 状态
   - 测 DOM 点击
   - 截图
   - 输出当前上下文

这样运行时异常不会污染主评估流程。

### 8.3 汇总阶段做归并，不做原样拼接

总表不应该只是把空间底稿相加。  
必须显式做：

- 系统性问题归并
- 优先级排序
- 面向业务方的建议方向

这一步应该是独立脚本或独立模板能力。
