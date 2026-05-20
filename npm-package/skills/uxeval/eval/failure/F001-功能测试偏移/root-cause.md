# 根因分析

## 根因 1：prompt 缺乏明确的「体验 vs 功能」判别口诀

最初的 task-generation prompt 只说「拆出体验任务」，但没有给出具体判别规则。
LLM 在面对详细 PRD 时倾向于按 PRD 字段拆任务，结果就成了功能测试。

## 根因 2：constitution.md 没有第 4 条

最初宪法只有 6 条，没有「不把功能存在与否当作主要体验问题」这条硬约束。
LLM 没有 fallback 检查，污染问题就直接进入报告。

## 根因 3：heuristic-detection 阶段没有原则映射强制

heuristic-engine 接受了所有 raw_issue（包括没有 principle_id 的），
本质上把「问题候选池」放得太宽。

## 根因 4：issue-attribution 没有强制每条 issue 必须有 ≥ 1 条 principle_ids

输出 schema 里 principle_ids 是 list，但允许空，导致功能 bug 也能成为 issue。

## 根因 5：缺乏前置 calibration

第一次跑时，没有用一个小样本（5 个 task）让设计师 calibrate 之后再放开做完整 30 个 task。
等 30 个 task 都生成完，发现偏了已经晚了。
