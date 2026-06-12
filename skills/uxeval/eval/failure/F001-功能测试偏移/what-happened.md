# 发生了什么

> 失败案例 F001：UXEval 跑成了功能测试

## 简短描述

第一次跑 UXEval 时，task-generation 阶段输出了 30 条任务，但其中 18 条是功能测试用例，
导致最终问题清单里 60% 是「按钮没响应」「跳转错误」这类与体验无关的功能 bug。

## 现象

### task-generation 阶段输出（坏样本）

```yaml
- id: T-XXX
  title: 保存按钮点击测试
  steps: ["点击保存按钮", "等待 3 秒"]
  success_criteria:
    - "跳转到列表页"
    - "提示「保存成功」"
  applicable_principles: []   # ← 空
```

### issue-attribution 输出（坏样本）

```yaml
- id: I-XXX
  title: 列表页排序按钮无响应
  description: "点击排序按钮，列表没有变化"
  severity: major
  user_impact: "用户无法排序"
  suggestion: "修复排序功能"
```

这些都是功能 bug，不是体验问题。
但 Agent 把它们一并塞进了报告，污染了产出。

## 触发条件

满足以下条件容易触发：
1. PRD 中包含详细功能描述（让 LLM 误以为「PRD 写了什么 = 要测试什么」）
2. 用户的 scope.md 没有明确划界 out_of_scope
3. heuristic-detection 阶段没有过滤 raw_issue 类型
4. issue-attribution 阶段没有运行 「功能 vs 体验」判别

## 影响范围

- 报告 noise 占比 60%+，资深设计师需手工剔除
- 中低阶设计师误以为功能测试就是体验评估，加深方法论误解
- 评估周期被拖长（多花 2 倍时间清洗 issues）
