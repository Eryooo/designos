# 严重等级口径（Severity Scale）

> 通用资产 · `ux.severity-scale` · status: draft
> 问题严重等级的通用分级口径。跨 skill 一致,每级有可区分的判定边界。
> 本文不绑定任何 issue 数据结构,也不规定上报渠道。

## 分级

- **critical（致命）**:阻断核心任务完成,或造成不可逆损失。用户无法绕过。
- **major（严重）**:显著增加完成核心任务的成本,存在可绕过的弯路但代价高。
- **minor（轻微）**:影响体验顺滑度,但不阻碍任务完成。
- **suggestion（建议）**:无明确损害,属优化空间。

## 判定边界

相邻两级的区分点:
- critical vs major:**能否绕过**。无法绕过 → critical。
- major vs minor:**是否阻碍任务**。增加成本但不阻碍 → minor。
- minor vs suggestion:**是否有可观察的体验损害**。无损害 → suggestion。

## 适用边界

本文只统一"等级含义";issue 的字段结构、严重等级如何映射到优先级或 gate,由消费方 skill 决定。

## 占位说明

本文为 K0 架构基线的 draft 占位,后续批次补全分级示例与边界用例。
