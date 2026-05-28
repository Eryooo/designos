---
name: web-heuristic-eval-readonly
description: 基于 PRD、截图和真实 Web 环境做只读体验启发式评估。当用户说体验评估、启发式走查、可用性测试、Web 只读自动化、PRD+截图+真实环境评估时触发。支持先生成任务清单，再生成真实环境执行脚本，并在用户手动登录后接管已登录会话执行多空间评估。
---

# web-heuristic-eval-readonly

## 何时使用

当用户满足以下任一条件时使用：

- 需要基于 PRD 输出体验评估任务清单
- 需要基于 PRD + 截图输出可执行的启发式评估脚本
- 需要在真实 Web 环境中以只读方式进行自动化体验走查
- 需要在多个空间/租户/工作区中补证空状态、默认路径或主链路问题

## 不适用场景

- 设计还原度验收
- 需要真实提交/保存/执行训练/发布/注册的业务测试
- 纯功能正确性测试
- 没有 PRD 也没有截图，也没有可进入环境时

## 先做什么

1. 确认输入：
   - PRD 路径
   - 截图目录
   - 是否需要真实环境执行
2. 确认边界：
   - 只读模式
   - 可填但不提交
   - 可拖但不保存
3. 如需真实环境执行：
   - 要求用户只提供环境地址
   - 由用户手动登录
   - 接管已登录会话继续执行

## 主流程

### Phase 1：静态分析

输出：
- 体验导向任务清单
- PRD-截图冲突清单
- 第一轮问题底稿

规则：
- PRD 是主基准
- 截图是现实校准层
- 冲突显式标注，不擅自抹平

### Phase 2：执行脚本生成

把任务清单翻译为真实环境执行脚本，必须明确：

- 起始页面
- 点击路径
- 目标页面
- 观察点
- 截图点
- 问题记录字段

### Phase 3：真实环境执行

只读执行允许：

- 页面跳转
- 新页签切换
- iframe 切换
- 打开弹窗和详情
- 填写表单但不提交
- 切换下拉、tab、开关
- 拖节点但不保存
- 截图和记录问题

禁止：

- 保存
- 提交
- 执行训练
- 发布
- 注册
- 删除
- 导入导出
- 上传并确认

### Phase 4：问题沉淀

规则：

- 每个空间单独记录问题底稿
- 环境异常也要记录
- 没有证据的结论不得进入主问题清单

### Phase 5：业务汇总

输出：
- 全量问题汇总
- PDF

汇总必须先做系统性归并，再附完整问题台账。

## 需要读取的 references

- `references/workflow.md`
  - 何时生成任务清单、何时生成执行脚本、何时进入真实环境
- `references/runtime-boundaries.md`
  - 只读规则、登录协作规则、异常分类
- `references/evidence-model.md`
  - 截图命名、空间级问题清单、证据归档方式
- `references/failure-handling.md`
  - 新页签、iframe、错跳空间、空白页、遮罩层拦截
- `references/report-structure.md`
  - 业务汇总文档结构

## 需要的脚本能力

- `scripts/playwright_bridge.mjs`
  - page/frame 状态、点击、填表、拖拽、截图、文本读取
- `scripts/state_manager.mjs`
  - 运行状态文件维护
- `scripts/merge_issue_docs.mjs`
  - 合并空间级问题底稿
- `scripts/render_markdown_pdf.py`
  - 导出 PDF

## 输出要求

至少输出：

- `task_checklist.md`
- `execution_script.md`
- `space_issue_docs/*.md`
- `summary_full.md`
- `summary_full.pdf`

## 关键约束

1. 不把账号密码写入聊天或脚本
2. 不把环境异常伪装成无问题
3. 不把当前项目的空间名和 tenantId 写死进 skill
4. 不把任务清单和执行脚本混成一个文件
5. 不输出无证据的确定性问题
