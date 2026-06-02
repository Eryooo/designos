# UX 失败模式（UX Failure Modes）

> 通用资产 · `ux.ux-failure-modes` · status: pilot
> 从既有评估失败样例中反抽的体验评估失败模式库,用于前置 calibration 与质量门控。

## purpose

让评估系统不只是"会找问题",还知道自己什么时候会跑偏。本库记录常见失败模式、识别信号、预防办法与修复方向。

## applies_to

- 体验评估 prompt 设计。
- 评估结果质量审查。
- golden/failure eval 用例设计。

## decision_framework

每个失败模式按四段记录:
1. **现象**:输出看起来像问题,但本质跑偏。
2. **识别信号**:可在结果中自动或人工发现的症状。
3. **根因**:通常来自 prompt、schema、constitution、calibration 缺失。
4. **防线**:前置约束、schema 必填、负向 eval、人工校准。

## senior_heuristics

- 先用小样本 calibration(如 5 个任务)再放开全量,避免 30 个任务都生成后才发现偏。
- 没有 principle_id / evidence_refs 的 issue 默认不进主报告。
- "功能不存在"不是体验问题;体验问题必须落在用户完成任务过程中的阻碍。
- 失败样例比成功样例更能定义边界,每次真实跑偏都应沉淀为 failure mode。

## quality_rubric

| 分级 | 信号 |
|---|---|
| 优 | 每个失败模式有识别信号、根因、防线,能转成测试 |
| 中 | 有失败描述但防线不清 |
| 差 | 只记录事故复盘,不能防复发 |

## common_failure_modes

- **功能测试偏移**:LLM 按 PRD 字段拆任务,把功能测试当体验评估。
- **原则缺失**:raw issue 没有 principle_id 仍进入问题池。
- **证据缺失**:无 evidence_refs 的主观判断进入报告。
- **calibration 缺失**:未小样本校准即全量生成,返工成本高。
- **schema 过宽**:允许空原则/空证据,导致污染无法被结构拦截。

## source_assets

- `skills/uxeval/eval/failure/F001-功能测试偏移/root-cause.md`
- `skills/uxeval/eval/failure/F001-功能测试偏移/how-to-detect.md`
- `skills/uxeval/eval/failure/F001-功能测试偏移/what-happened.md`

## do_not_claim

- 不保证覆盖所有未来失败模式。
- 不替代真实 failure eval;它是设计测试的知识来源。
- 不把一次事故的项目细节搬进通用库,只保留可复用模式。
